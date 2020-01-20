# Copyright 2012 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import hashlib
import os
import re

import glance_store
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from oslo_utils import encodeutils
import six
from six.moves import http_client as http
import six.moves.urllib.parse as urlparse
import webob.exc

from glance.api import common
from glance.api import policy
from glance.common import exception
from glance.common import location_strategy
from glance.common import timeutils
from glance.common import utils
from glance.common import wsgi
import glance.db
import glance.gateway
from glance.i18n import _, _LW
import glance.notifier
import glance.schema

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.import_opt('disk_formats', 'glance.common.config', group='image_format')
CONF.import_opt('container_formats', 'glance.common.config',
                group='image_format')
CONF.import_opt('show_multiple_locations', 'glance.common.config')
CONF.import_opt('hashing_algorithm', 'glance.common.config')


class ImagesController(object):
    def __init__(self, db_api=None, policy_enforcer=None, notifier=None,
                 store_api=None):
        self.db_api = db_api or glance.db.get_api()
        self.policy = policy_enforcer or policy.Enforcer()
        self.notifier = notifier or glance.notifier.Notifier()
        self.store_api = store_api or glance_store
        self.gateway = glance.gateway.Gateway(self.db_api, self.store_api,
                                              self.notifier, self.policy)

    @utils.mutating
    def create(self, req, image, extra_properties, tags):
        image_factory = self.gateway.get_image_factory(req.context)
        image_repo = self.gateway.get_repo(req.context)
        try:
            image = image_factory.new_image(extra_properties=extra_properties,
                                            tags=tags, **image)
            image_repo.add(image)
        except (exception.DuplicateLocation,
                exception.Invalid) as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except (exception.ReservedProperty,
                exception.ReadonlyProperty) as e:
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.Forbidden as e:
            LOG.debug("User not permitted to create image")
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.LimitExceeded as e:
            LOG.warn(encodeutils.exception_to_unicode(e))
            raise webob.exc.HTTPRequestEntityTooLarge(
                explanation=e.msg, request=req, content_type='text/plain')
        except exception.Duplicate as e:
            raise webob.exc.HTTPConflict(explanation=e.msg)
        except exception.NotAuthenticated as e:
            raise webob.exc.HTTPUnauthorized(explanation=e.msg)
        except TypeError as e:
            LOG.debug(encodeutils.exception_to_unicode(e))
            raise webob.exc.HTTPBadRequest(explanation=e)

        return image

    @utils.mutating
    def import_image(self, req, image_id, body):
        image_repo = self.gateway.get_repo(req.context)
        task_factory = self.gateway.get_task_factory(req.context)
        executor_factory = self.gateway.get_task_executor_factory(req.context)
        task_repo = self.gateway.get_task_repo(req.context)
        import_method = body.get('method').get('name')
        uri = body.get('method').get('uri')

        try:
            image = image_repo.get(image_id)
            if image.status == 'active':
                msg = _("Image with status active cannot be target for import")
                raise exception.Conflict(msg)
            if image.status != 'queued' and import_method == 'web-download':
                msg = _("Image needs to be in 'queued' state to use "
                        "'web-download' method")
                raise exception.Conflict(msg)
            if (image.status != 'uploading' and
                    import_method == 'glance-direct'):
                msg = _("Image needs to be staged before 'glance-direct' "
                        "method can be used")
                raise exception.Conflict(msg)
            if not getattr(image, 'container_format', None):
                msg = _("'container_format' needs to be set before import")
                raise exception.Conflict(msg)
            if not getattr(image, 'disk_format', None):
                msg = _("'disk_format' needs to be set before import")
                raise exception.Conflict(msg)

            backend = None
            if CONF.enabled_backends:
                backend = req.headers.get('x-image-meta-store',
                                          CONF.glance_store.default_backend)
                try:
                    glance_store.get_store_from_store_identifier(backend)
                except glance_store.UnknownScheme:
                    msg = _("Store for scheme %s not found") % backend
                    LOG.warn(msg)
                    raise exception.Conflict(msg)
        except exception.Conflict as e:
            raise webob.exc.HTTPConflict(explanation=e.msg)
        except exception.NotFound as e:
            raise webob.exc.HTTPNotFound(explanation=e.msg)

        task_input = {'image_id': image_id,
                      'import_req': body,
                      'backend': backend}

        if (import_method == 'web-download' and
           not utils.validate_import_uri(uri)):
                LOG.debug("URI for web-download does not pass filtering: %s",
                          uri)
                msg = (_("URI for web-download does not pass filtering: %s") %
                       uri)
                raise webob.exc.HTTPBadRequest(explanation=msg)

        try:
            import_task = task_factory.new_task(task_type='api_image_import',
                                                owner=req.context.owner,
                                                task_input=task_input)
            task_repo.add(import_task)
            task_executor = executor_factory.new_task_executor(req.context)
            pool = common.get_thread_pool("tasks_eventlet_pool")
            pool.spawn_n(import_task.run, task_executor)
        except exception.Forbidden as e:
            LOG.debug("User not permitted to create image import task.")
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.Conflict as e:
            raise webob.exc.HTTPConflict(explanation=e.msg)
        except exception.InvalidImageStatusTransition as e:
            raise webob.exc.HTTPConflict(explanation=e.msg)
        except ValueError as e:
            LOG.debug("Cannot import data for image %(id)s: %(e)s",
                      {'id': image_id,
                       'e': encodeutils.exception_to_unicode(e)})
            raise webob.exc.HTTPBadRequest(
                explanation=encodeutils.exception_to_unicode(e))

        return image_id

    def index(self, req, marker=None, limit=None, sort_key=None,
              sort_dir=None, filters=None, member_status='accepted'):
        sort_key = ['created_at'] if not sort_key else sort_key

        sort_dir = ['desc'] if not sort_dir else sort_dir

        result = {}
        if filters is None:
            filters = {}
        filters['deleted'] = False

        os_hidden = filters.get('os_hidden', 'false').lower()
        if os_hidden not in ['true', 'false']:
            message = _("Invalid value '%s' for 'os_hidden' filter."
                        " Valid values are 'true' or 'false'.") % os_hidden
            raise webob.exc.HTTPBadRequest(explanation=message)
        # ensure the type of os_hidden is boolean
        filters['os_hidden'] = os_hidden == 'true'

        protected = filters.get('protected')
        if protected is not None:
            if protected not in ['true', 'false']:
                message = _("Invalid value '%s' for 'protected' filter."
                            " Valid values are 'true' or 'false'.") % protected
                raise webob.exc.HTTPBadRequest(explanation=message)
            # ensure the type of protected is boolean
            filters['protected'] = protected == 'true'

        if limit is None:
            limit = CONF.limit_param_default
        limit = min(CONF.api_limit_max, limit)

        image_repo = self.gateway.get_repo(req.context)
        try:
            images = image_repo.list(marker=marker, limit=limit,
                                     sort_key=sort_key,
                                     sort_dir=sort_dir,
                                     filters=filters,
                                     member_status=member_status)
            if len(images) != 0 and len(images) == limit:
                result['next_marker'] = images[-1].image_id
        except (exception.NotFound, exception.InvalidSortKey,
                exception.InvalidFilterRangeValue,
                exception.InvalidParameterValue,
                exception.InvalidFilterOperatorValue) as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except exception.Forbidden as e:
            LOG.debug("User not permitted to retrieve images index")
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.NotAuthenticated as e:
            raise webob.exc.HTTPUnauthorized(explanation=e.msg)
        result['images'] = images
        return result

    def show(self, req, image_id):
        image_repo = self.gateway.get_repo(req.context)
        try:
            return image_repo.get(image_id)
        except exception.Forbidden as e:
            LOG.debug("User not permitted to show image '%s'", image_id)
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.NotFound as e:
            raise webob.exc.HTTPNotFound(explanation=e.msg)
        except exception.NotAuthenticated as e:
            raise webob.exc.HTTPUnauthorized(explanation=e.msg)

    @utils.mutating
    def update(self, req, image_id, changes):
        image_repo = self.gateway.get_repo(req.context)
        try:
            image = image_repo.get(image_id)

            for change in changes:
                change_method_name = '_do_%s' % change['op']
                change_method = getattr(self, change_method_name)
                change_method(req, image, change)

            if changes:
                image_repo.save(image)
        except exception.NotFound as e:
            raise webob.exc.HTTPNotFound(explanation=e.msg)
        except (exception.Invalid, exception.BadStoreUri) as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except exception.Forbidden as e:
            LOG.debug("User not permitted to update image '%s'", image_id)
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except exception.StorageQuotaFull as e:
            msg = (_("Denying attempt to upload image because it exceeds the"
                     " quota: %s") % encodeutils.exception_to_unicode(e))
            LOG.warn(msg)
            raise webob.exc.HTTPRequestEntityTooLarge(
                explanation=msg, request=req, content_type='text/plain')
        except exception.LimitExceeded as e:
            LOG.exception(encodeutils.exception_to_unicode(e))
            raise webob.exc.HTTPRequestEntityTooLarge(
                explanation=e.msg, request=req, content_type='text/plain')
        except exception.NotAuthenticated as e:
            raise webob.exc.HTTPUnauthorized(explanation=e.msg)

        return image

    def _do_replace(self, req, image, change):
        path = change['path']
        path_root = path[0]
        value = change['value']
        if path_root == 'locations' and not value:
            msg = _("Cannot set locations to empty list.")
            raise webob.exc.HTTPForbidden(msg)
        elif path_root == 'locations' and value:
            self._do_replace_locations(image, value)
        elif path_root == 'owner' and req.context.is_admin == False:
            msg = _("Owner can't be updated by non admin.")
            raise webob.exc.HTTPForbidden(msg)
        else:
            if hasattr(image, path_root):
                setattr(image, path_root, value)
            elif path_root in image.extra_properties:
                image.extra_properties[path_root] = value
            else:
                msg = _("Property %s does not exist.")
                raise webob.exc.HTTPConflict(msg % path_root)

    def _do_add(self, req, image, change):
        path = change['path']
        path_root = path[0]
        value = change['value']
        json_schema_version = change.get('json_schema_version', 10)
        if path_root == 'locations':
            self._do_add_locations(image, path[1], value)
        else:
            if ((hasattr(image, path_root) or
                    path_root in image.extra_properties)
                    and json_schema_version == 4):
                msg = _("Property %s already present.")
                raise webob.exc.HTTPConflict(msg % path_root)
            if hasattr(image, path_root):
                setattr(image, path_root, value)
            else:
                image.extra_properties[path_root] = value

    def _do_remove(self, req, image, change):
        path = change['path']
        path_root = path[0]
        if path_root == 'locations':
            try:
                self._do_remove_locations(image, path[1])
            except exception.Forbidden as e:
                raise webob.exc.HTTPForbidden(e.msg)
        else:
            if hasattr(image, path_root):
                msg = _("Property %s may not be removed.")
                raise webob.exc.HTTPForbidden(msg % path_root)
            elif path_root in image.extra_properties:
                del image.extra_properties[path_root]
            else:
                msg = _("Property %s does not exist.")
                raise webob.exc.HTTPConflict(msg % path_root)

    @utils.mutating
    def delete(self, req, image_id):
        image_repo = self.gateway.get_repo(req.context)
        try:
            image = image_repo.get(image_id)
            file_path = str(
                CONF.node_staging_uri + '/' + image_id)[7:]
            if os.path.exists(file_path):
                try:
                    LOG.debug(
                        "After upload to the backend, deleting staged "
                        "image data from %(fn)s", {'fn': file_path})
                    os.unlink(file_path)
                except OSError as e:
                    LOG.error(
                        "After upload to backend, deletion of staged "
                        "image data from %(fn)s has failed because "
                        "[Errno %(en)d]", {'fn': file_path,
                                           'en': e.errno})
            else:
                LOG.warning(_(
                    "After upload to backend, deletion of staged "
                    "image data has failed because "
                    "it cannot be found at %(fn)s"), {'fn': file_path})

            image.delete()
            image_repo.remove(image)
        except (glance_store.Forbidden, exception.Forbidden) as e:
            LOG.debug("User not permitted to delete image '%s'", image_id)
            raise webob.exc.HTTPForbidden(explanation=e.msg)
        except (glance_store.NotFound, exception.NotFound) as e:
            msg = (_("Failed to find image %(image_id)s to delete") %
                   {'image_id': image_id})
            LOG.warn(msg)
            raise webob.exc.HTTPNotFound(explanation=msg)
        except glance_store.exceptions.InUseByStore as e:
            msg = (_("Image %(id)s could not be deleted "
                     "because it is in use: %(exc)s") %
                   {"id": image_id,
                    "exc": e.msg})
            LOG.warn(msg)
            raise webob.exc.HTTPConflict(explanation=msg)
        except glance_store.exceptions.HasSnapshot as e:
            raise webob.exc.HTTPConflict(explanation=e.msg)
        except exception.InvalidImageStatusTransition as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except exception.NotAuthenticated as e:
            raise webob.exc.HTTPUnauthorized(explanation=e.msg)

    def _validate_validation_data(self, image, locations):
        val_data = {}
        for loc in locations:
            if 'validation_data' not in loc:
                continue
            for k, v in loc['validation_data'].items():
                if val_data.get(k, v) != v:
                    msg = _("Conflicting values for %s") % k
                    raise webob.exc.HTTPConflict(explanation=msg)
                val_data[k] = v

        # NOTE(imacdonn): values may be provided for items which are
        # already set, so long as the values exactly match. In this
        # case, nothing actually needs to be updated, but we should
        # reject the request if there's an apparent attempt to supply
        # a different value.
        new_val_data = {}
        for k, v in val_data.items():
            current = getattr(image, k)
            if v == current:
                continue
            if current:
                msg = _("%s is already set with a different value") % k
                raise webob.exc.HTTPConflict(explanation=msg)
            new_val_data[k] = v

        if not new_val_data:
            return {}

        if image.status != 'queued':
            msg = _("New value(s) for %s may only be provided when image "
                    "status is 'queued'") % ', '.join(new_val_data.keys())
            raise webob.exc.HTTPConflict(explanation=msg)

        if 'checksum' in new_val_data:
            try:
                checksum_bytes = bytearray.fromhex(new_val_data['checksum'])
            except ValueError:
                msg = (_("checksum (%s) is not a valid hexadecimal value") %
                       new_val_data['checksum'])
                raise webob.exc.HTTPConflict(explanation=msg)
            if len(checksum_bytes) != 16:
                msg = (_("checksum (%s) is not the correct size for md5 "
                         "(should be 16 bytes)") %
                       new_val_data['checksum'])
                raise webob.exc.HTTPConflict(explanation=msg)

        hash_algo = new_val_data.get('os_hash_algo')
        if hash_algo != CONF['hashing_algorithm']:
            msg = (_("os_hash_algo must be %(want)s, not %(got)s") %
                   {'want': CONF['hashing_algorithm'], 'got': hash_algo})
            raise webob.exc.HTTPConflict(explanation=msg)

        try:
            hash_bytes = bytearray.fromhex(new_val_data['os_hash_value'])
        except ValueError:
            msg = (_("os_hash_value (%s) is not a valid hexadecimal value") %
                   new_val_data['os_hash_value'])
            raise webob.exc.HTTPConflict(explanation=msg)
        want_size = hashlib.new(hash_algo).digest_size
        if len(hash_bytes) != want_size:
            msg = (_("os_hash_value (%(value)s) is not the correct size for "
                     "%(algo)s (should be %(want)d bytes)") %
                   {'value': new_val_data['os_hash_value'],
                    'algo': hash_algo,
                    'want': want_size})
            raise webob.exc.HTTPConflict(explanation=msg)

        return new_val_data

    def _get_locations_op_pos(self, path_pos, max_pos, allow_max):
        if path_pos is None or max_pos is None:
            return None
        pos = max_pos if allow_max else max_pos - 1
        if path_pos.isdigit():
            pos = int(path_pos)
        elif path_pos != '-':
            return None
        if not (allow_max or 0 <= pos < max_pos):
            return None
        return pos

    def _do_replace_locations(self, image, value):
        if CONF.show_multiple_locations == False:
            msg = _("It's not allowed to update locations if locations are "
                    "invisible.")
            raise webob.exc.HTTPForbidden(explanation=msg)

        if image.status not in ('active', 'queued'):
            msg = _("It's not allowed to replace locations if image status is "
                    "%s.") % image.status
            raise webob.exc.HTTPConflict(explanation=msg)

        val_data = self._validate_validation_data(image, value)

        try:
            # NOTE(flwang): _locations_proxy's setattr method will check if
            # the update is acceptable.
            image.locations = value
            if image.status == 'queued':
                for k, v in val_data.items():
                    setattr(image, k, v)
                image.status = 'active'
        except (exception.BadStoreUri, exception.DuplicateLocation) as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except ValueError as ve:    # update image status failed.
            raise webob.exc.HTTPBadRequest(
                explanation=encodeutils.exception_to_unicode(ve))

    def _do_add_locations(self, image, path_pos, value):
        if CONF.show_multiple_locations == False:
            msg = _("It's not allowed to add locations if locations are "
                    "invisible.")
            raise webob.exc.HTTPForbidden(explanation=msg)

        if image.status not in ('active', 'queued'):
            msg = _("It's not allowed to add locations if image status is "
                    "%s.") % image.status
            raise webob.exc.HTTPConflict(explanation=msg)

        val_data = self._validate_validation_data(image, [value])

        pos = self._get_locations_op_pos(path_pos,
                                         len(image.locations), True)
        if pos is None:
            msg = _("Invalid position for adding a location.")
            raise webob.exc.HTTPBadRequest(explanation=msg)
        try:
            image.locations.insert(pos, value)
            if image.status == 'queued':
                for k, v in val_data.items():
                    setattr(image, k, v)
                image.status = 'active'
        except (exception.BadStoreUri, exception.DuplicateLocation) as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        except ValueError as e:    # update image status failed.
            raise webob.exc.HTTPBadRequest(
                explanation=encodeutils.exception_to_unicode(e))

    def _do_remove_locations(self, image, path_pos):
        if CONF.show_multiple_locations == False:
            msg = _("It's not allowed to remove locations if locations are "
                    "invisible.")
            raise webob.exc.HTTPForbidden(explanation=msg)

        if image.status not in ('active'):
            msg = _("It's not allowed to remove locations if image status is "
                    "%s.") % image.status
            raise webob.exc.HTTPConflict(explanation=msg)

        if len(image.locations) == 1:
            LOG.debug("User forbidden to remove last location of image %s",
                      image.image_id)
            msg = _("Cannot remove last location in the image.")
            raise exception.Forbidden(msg)
        pos = self._get_locations_op_pos(path_pos,
                                         len(image.locations), False)
        if pos is None:
            msg = _("Invalid position for removing a location.")
            raise webob.exc.HTTPBadRequest(explanation=msg)
        try:
            # NOTE(zhiyan): this actually deletes the location
            # from the backend store.
            image.locations.pop(pos)
        # TODO(jokke): Fix this, we should catch what store throws and
        # provide definitely something else than IternalServerError to user.
        except Exception as e:
            raise webob.exc.HTTPInternalServerError(
                explanation=encodeutils.exception_to_unicode(e))


class RequestDeserializer(wsgi.JSONRequestDeserializer):

    _disallowed_properties = ('direct_url', 'self', 'file', 'schema')
    _readonly_properties = ('created_at', 'updated_at', 'status', 'checksum',
                            'size', 'virtual_size', 'direct_url', 'self',
                            'file', 'schema', 'id', 'os_hash_algo',
                            'os_hash_value')
    _reserved_properties = ('location', 'deleted', 'deleted_at')
    _base_properties = ('checksum', 'created_at', 'container_format',
                        'disk_format', 'id', 'min_disk', 'min_ram', 'name',
                        'size', 'virtual_size', 'status', 'tags', 'owner',
                        'updated_at', 'visibility', 'protected', 'os_hidden')
    _available_sort_keys = ('name', 'status', 'container_format',
                            'disk_format', 'size', 'id', 'created_at',
                            'updated_at')

    _default_sort_key = 'created_at'

    _default_sort_dir = 'desc'

    _path_depth_limits = {'locations': {'add': 2, 'remove': 2, 'replace': 1}}

    _supported_operations = ('add', 'remove', 'replace')

    def __init__(self, schema=None):
        super(RequestDeserializer, self).__init__()
        self.schema = schema or get_schema()

    def _get_request_body(self, request):
        output = super(RequestDeserializer, self).default(request)
        if 'body' not in output:
            msg = _('Body expected in request.')
            raise webob.exc.HTTPBadRequest(explanation=msg)
        return output['body']

    @classmethod
    def _check_allowed(cls, image):
        for key in cls._disallowed_properties:
            if key in image:
                msg = _("Attribute '%s' is read-only.") % key
                raise webob.exc.HTTPForbidden(
                    explanation=six.text_type(msg))

    def create(self, request):
        body = self._get_request_body(request)
        self._check_allowed(body)
        try:
            self.schema.validate(body)
        except exception.InvalidObject as e:
            raise webob.exc.HTTPBadRequest(explanation=e.msg)
        image = {}
        properties = body
        tags = properties.pop('tags', [])
        for key in self._base_properties:
            try:
                # NOTE(flwang): Instead of changing the _check_unexpected
                # of ImageFactory. It would be better to do the mapping
                # at here.
                if key == 'id':
                    image['image_id'] = properties.pop(key)
                else:
                    image[key] = properties.pop(key)
            except KeyError:
                pass

        # NOTE(abhishekk): Check if custom property key name is less than 255
        # characters. Reference LP #1737952
        for key in properties:
            if len(key) > 255:
                msg = (_("Custom property should not be greater than 255 "
                         "characters."))
                raise webob.exc.HTTPBadRequest(explanation=msg)

        return dict(image=image, extra_properties=properties, tags=tags)

    def _get_change_operation_d10(self, raw_change):
        op = raw_change.get('op')
        if op is None:
            msg = (_('Unable to find `op` in JSON Schema change. '
                     'It must be one of the following: %(available)s.') %
                   {'available': ', '.join(self._supported_operations)})
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if op not in self._supported_operations:
            msg = (_('Invalid operation: `%(op)s`. '
                     'It must be one of the following: %(available)s.') %
                   {'op': op,
                    'available': ', '.join(self._supported_operations)})
            raise webob.exc.HTTPBadRequest(explanation=msg)
        return op

    def _get_change_operation_d4(self, raw_change):
        op = None
        for key in self._supported_operations:
            if key in raw_change:
                if op is not None:
                    msg = _('Operation objects must contain only one member'
                            ' named "add", "remove", or "replace".')
                    raise webob.exc.HTTPBadRequest(explanation=msg)
                op = key
        if op is None:
            msg = _('Operation objects must contain exactly one member'
                    ' named "add", "remove", or "replace".')
            raise webob.exc.HTTPBadRequest(explanation=msg)
        return op

    def _get_change_path_d10(self, raw_change):
        try:
            return raw_change['path']
        except KeyError:
            msg = _("Unable to find '%s' in JSON Schema change") % 'path'
            raise webob.exc.HTTPBadRequest(explanation=msg)

    def _get_change_path_d4(self, raw_change, op):
        return raw_change[op]

    def _decode_json_pointer(self, pointer):
        """Parse a json pointer.

        Json Pointers are defined in
        http://tools.ietf.org/html/draft-pbryan-zyp-json-pointer .
        The pointers use '/' for separation between object attributes, such
        that '/A/B' would evaluate to C in {"A": {"B": "C"}}. A '/' character
        in an attribute name is encoded as "~1" and a '~' character is encoded
        as "~0".
        """
        self._validate_json_pointer(pointer)
        ret = []
        for part in pointer.lstrip('/').split('/'):
            ret.append(part.replace('~1', '/').replace('~0', '~').strip())
        return ret

    def _validate_json_pointer(self, pointer):
        """Validate a json pointer.

        We only accept a limited form of json pointers.
        """
        if not pointer.startswith('/'):
            msg = _('Pointer `%s` does not start with "/".') % pointer
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if re.search('/\s*?/', pointer[1:]):
            msg = _('Pointer `%s` contains adjacent "/".') % pointer
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if len(pointer) > 1 and pointer.endswith('/'):
            msg = _('Pointer `%s` end with "/".') % pointer
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if pointer[1:].strip() == '/':
            msg = _('Pointer `%s` does not contains valid token.') % pointer
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if re.search('~[^01]', pointer) or pointer.endswith('~'):
            msg = _('Pointer `%s` contains "~" not part of'
                    ' a recognized escape sequence.') % pointer
            raise webob.exc.HTTPBadRequest(explanation=msg)

    def _get_change_value(self, raw_change, op):
        if 'value' not in raw_change:
            msg = _('Operation "%s" requires a member named "value".')
            raise webob.exc.HTTPBadRequest(explanation=msg % op)
        return raw_change['value']

    def _validate_change(self, change):
        path_root = change['path'][0]
        if path_root in self._readonly_properties:
            msg = _("Attribute '%s' is read-only.") % path_root
            raise webob.exc.HTTPForbidden(explanation=six.text_type(msg))
        if path_root in self._reserved_properties:
            msg = _("Attribute '%s' is reserved.") % path_root
            raise webob.exc.HTTPForbidden(explanation=six.text_type(msg))

        if change['op'] == 'remove':
            return

        partial_image = None
        if len(change['path']) == 1:
            partial_image = {path_root: change['value']}
        elif ((path_root in get_base_properties().keys()) and
              (get_base_properties()[path_root].get('type', '') == 'array')):
            # NOTE(zhiyan): client can use the PATCH API to add an element
            # directly to an existing property
            # Such as: 1. using '/locations/N' path to add a location
            #             to the image's 'locations' list at position N.
            #             (implemented)
            #          2. using '/tags/-' path to append a tag to the
            #             image's 'tags' list at the end. (Not implemented)
            partial_image = {path_root: [change['value']]}

        if partial_image:
            try:
                self.schema.validate(partial_image)
            except exception.InvalidObject as e:
                raise webob.exc.HTTPBadRequest(explanation=e.msg)

    def _validate_path(self, op, path):
        path_root = path[0]
        limits = self._path_depth_limits.get(path_root, {})
        if len(path) != limits.get(op, 1):
            msg = _("Invalid JSON pointer for this resource: "
                    "'/%s'") % '/'.join(path)
            raise webob.exc.HTTPBadRequest(explanation=six.text_type(msg))

    def _parse_json_schema_change(self, raw_change, draft_version):
        if draft_version == 10:
            op = self._get_change_operation_d10(raw_change)
            path = self._get_change_path_d10(raw_change)
        elif draft_version == 4:
            op = self._get_change_operation_d4(raw_change)
            path = self._get_change_path_d4(raw_change, op)
        else:
            msg = _('Unrecognized JSON Schema draft version')
            raise webob.exc.HTTPBadRequest(explanation=msg)

        path_list = self._decode_json_pointer(path)
        return op, path_list

    def update(self, request):
        changes = []
        content_types = {
            'application/openstack-images-v2.0-json-patch': 4,
            'application/openstack-images-v2.1-json-patch': 10,
        }
        if request.content_type not in content_types:
            headers = {'Accept-Patch':
                       ', '.join(sorted(content_types.keys()))}
            raise webob.exc.HTTPUnsupportedMediaType(headers=headers)

        json_schema_version = content_types[request.content_type]

        body = self._get_request_body(request)

        if not isinstance(body, list):
            msg = _('Request body must be a JSON array of operation objects.')
            raise webob.exc.HTTPBadRequest(explanation=msg)

        for raw_change in body:
            if not isinstance(raw_change, dict):
                msg = _('Operations must be JSON objects.')
                raise webob.exc.HTTPBadRequest(explanation=msg)

            (op, path) = self._parse_json_schema_change(raw_change,
                                                        json_schema_version)

            # NOTE(zhiyan): the 'path' is a list.
            self._validate_path(op, path)
            change = {'op': op, 'path': path,
                      'json_schema_version': json_schema_version}

            if not op == 'remove':
                change['value'] = self._get_change_value(raw_change, op)

            self._validate_change(change)

            changes.append(change)

        return {'changes': changes}

    def _validate_limit(self, limit):
        try:
            limit = int(limit)
        except ValueError:
            msg = _("limit param must be an integer")
            raise webob.exc.HTTPBadRequest(explanation=msg)

        if limit < 0:
            msg = _("limit param must be positive")
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return limit

    def _validate_sort_key(self, sort_key):
        if sort_key not in self._available_sort_keys:
            msg = _('Invalid sort key: %(sort_key)s. '
                    'It must be one of the following: %(available)s.') % (
                {'sort_key': sort_key,
                 'available': ', '.join(self._available_sort_keys)})
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return sort_key

    def _validate_sort_dir(self, sort_dir):
        if sort_dir not in ['asc', 'desc']:
            msg = _('Invalid sort direction: %s') % sort_dir
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return sort_dir

    def _validate_member_status(self, member_status):
        if member_status not in ['pending', 'accepted', 'rejected', 'all']:
            msg = _('Invalid status: %s') % member_status
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return member_status

    def _get_filters(self, filters):
        visibility = filters.get('visibility')
        if visibility:
            if visibility not in ['community', 'public', 'private', 'shared',
                                  'all']:
                msg = _('Invalid visibility value: %s') % visibility
                raise webob.exc.HTTPBadRequest(explanation=msg)
        changes_since = filters.get('changes-since')
        if changes_since:
            msg = _('The "changes-since" filter is no longer available on v2.')
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return filters

    def _get_sorting_params(self, params):
        """
        Process sorting params.
        Currently glance supports two sorting syntax: classic and new one,
        that is uniform for all OpenStack projects.
        Classic syntax: sort_key=name&sort_dir=asc&sort_key=size&sort_dir=desc
        New syntax: sort=name:asc,size:desc
        """
        sort_keys = []
        sort_dirs = []

        if 'sort' in params:
            # use new sorting syntax here
            if 'sort_key' in params or 'sort_dir' in params:
                msg = _('Old and new sorting syntax cannot be combined')
                raise webob.exc.HTTPBadRequest(explanation=msg)
            for sort_param in params.pop('sort').strip().split(','):
                key, _sep, dir = sort_param.partition(':')
                if not dir:
                    dir = self._default_sort_dir
                sort_keys.append(self._validate_sort_key(key.strip()))
                sort_dirs.append(self._validate_sort_dir(dir.strip()))
        else:
            # continue with classic syntax
            # NOTE(mfedosin): we have 3 options here:
            # 1. sort_dir wasn't passed: we use default one - 'desc'.
            # 2. Only one sort_dir was passed: use it for every sort_key
            # in the list.
            # 3. Multiple sort_dirs were passed: consistently apply each one to
            # the corresponding sort_key.
            # If number of sort_dirs and sort_keys doesn't match then raise an
            # exception.
            while 'sort_key' in params:
                sort_keys.append(self._validate_sort_key(
                    params.pop('sort_key').strip()))

            while 'sort_dir' in params:
                sort_dirs.append(self._validate_sort_dir(
                    params.pop('sort_dir').strip()))

            if sort_dirs:
                dir_len = len(sort_dirs)
                key_len = len(sort_keys)

                if dir_len > 1 and dir_len != key_len:
                    msg = _('Number of sort dirs does not match the number '
                            'of sort keys')
                    raise webob.exc.HTTPBadRequest(explanation=msg)

        if not sort_keys:
            sort_keys = [self._default_sort_key]

        if not sort_dirs:
            sort_dirs = [self._default_sort_dir]

        return sort_keys, sort_dirs

    def index(self, request):
        params = request.params.copy()
        limit = params.pop('limit', None)
        marker = params.pop('marker', None)
        member_status = params.pop('member_status', 'accepted')

        # NOTE (flwang) To avoid using comma or any predefined chars to split
        # multiple tags, now we allow user specify multiple 'tag' parameters
        # in URL, such as v2/images?tag=x86&tag=64bit.
        tags = []
        while 'tag' in params:
            tags.append(params.pop('tag').strip())

        query_params = {
            'filters': self._get_filters(params),
            'member_status': self._validate_member_status(member_status),
        }

        if marker is not None:
            query_params['marker'] = marker

        if limit is not None:
            query_params['limit'] = self._validate_limit(limit)

        if tags:
            query_params['filters']['tags'] = tags

        # NOTE(mfedosin): param is still called sort_key and sort_dir,
        # instead of sort_keys and sort_dirs respectively.
        # It's done because in v1 it's still a single value.

        query_params['sort_key'], query_params['sort_dir'] = (
            self._get_sorting_params(params))

        return query_params

    def _validate_import_body(self, body):
        # TODO(rosmaita): do schema validation of body instead
        # of this ad-hoc stuff
        try:
            method = body['method']
        except KeyError:
            msg = _("Import request requires a 'method' field.")
            raise webob.exc.HTTPBadRequest(explanation=msg)
        try:
            method_name = method['name']
        except KeyError:
            msg = _("Import request requires a 'name' field.")
            raise webob.exc.HTTPBadRequest(explanation=msg)
        if method_name not in CONF.enabled_import_methods:
            msg = _("Unknown import method name '%s'.") % method_name
            raise webob.exc.HTTPBadRequest(explanation=msg)

    def import_image(self, request):
        body = self._get_request_body(request)
        self._validate_import_body(body)
        return {'body': body}


class ResponseSerializer(wsgi.JSONResponseSerializer):
    def __init__(self, schema=None):
        super(ResponseSerializer, self).__init__()
        self.schema = schema or get_schema()

    def _get_image_href(self, image, subcollection=''):
        base_href = '/v2/images/%s' % image.image_id
        if subcollection:
            base_href = '%s/%s' % (base_href, subcollection)
        return base_href

    def _format_image(self, image):

        def _get_image_locations(image):
            try:
                return list(image.locations)
            except exception.Forbidden:
                return []

        try:
            image_view = dict(image.extra_properties)
            attributes = ['name', 'disk_format', 'container_format',
                          'visibility', 'size', 'virtual_size', 'status',
                          'checksum', 'protected', 'min_ram', 'min_disk',
                          'owner', 'os_hidden', 'os_hash_algo',
                          'os_hash_value']
            for key in attributes:
                image_view[key] = getattr(image, key)
            image_view['id'] = image.image_id
            image_view['created_at'] = timeutils.isotime(image.created_at)
            image_view['updated_at'] = timeutils.isotime(image.updated_at)

            if CONF.show_multiple_locations:
                locations = _get_image_locations(image)
                if locations:
                    image_view['locations'] = []
                    for loc in locations:
                        tmp = dict(loc)
                        tmp.pop('id', None)
                        tmp.pop('status', None)
                        image_view['locations'].append(tmp)
                else:
                    # NOTE (flwang): We will still show "locations": [] if
                    # image.locations is None to indicate it's allowed to show
                    # locations but it's just non-existent.
                    image_view['locations'] = []
                    LOG.debug("The 'locations' list of image %s is empty",
                              image.image_id)

            if CONF.show_image_direct_url:
                locations = _get_image_locations(image)
                if locations:
                    # Choose best location configured strategy
                    l = location_strategy.choose_best_location(locations)
                    image_view['direct_url'] = l['url']
                else:
                    LOG.debug("The 'locations' list of image %s is empty, "
                              "not including 'direct_url' in response",
                              image.image_id)

            image_view['tags'] = list(image.tags)
            image_view['self'] = self._get_image_href(image)
            image_view['file'] = self._get_image_href(image, 'file')
            image_view['schema'] = '/v2/schemas/image'
            image_view = self.schema.filter(image_view)  # domain

            # add store information to image
            if CONF.enabled_backends:
                locations = _get_image_locations(image)
                if locations:
                    stores = []
                    for loc in locations:
                        backend = loc['metadata'].get('backend')
                        if backend:
                            stores.append(backend)

                    if stores:
                        image_view['stores'] = ",".join(stores)

            return image_view
        except exception.Forbidden as e:
            raise webob.exc.HTTPForbidden(explanation=e.msg)

    def create(self, response, image):
        response.status_int = http.CREATED
        self.show(response, image)
        response.location = self._get_image_href(image)
        # according to RFC7230, headers should not have empty fields
        # see http://httpwg.org/specs/rfc7230.html#field.components
        if CONF.enabled_import_methods:
            import_methods = ("OpenStack-image-import-methods",
                              ','.join(CONF.enabled_import_methods))
            response.headerlist.append(import_methods)

        if CONF.enabled_backends:
            enabled_backends = ("OpenStack-image-store-ids",
                                ','.join(CONF.enabled_backends.keys()))
            response.headerlist.append(enabled_backends)

    def show(self, response, image):
        image_view = self._format_image(image)
        body = json.dumps(image_view, ensure_ascii=False)
        response.unicode_body = six.text_type(body)
        response.content_type = 'application/json'

    def update(self, response, image):
        image_view = self._format_image(image)
        body = json.dumps(image_view, ensure_ascii=False)
        response.unicode_body = six.text_type(body)
        response.content_type = 'application/json'

    def index(self, response, result):
        params = dict(response.request.params)
        params.pop('marker', None)
        query = urlparse.urlencode(params)
        body = {
            'images': [self._format_image(i) for i in result['images']],
            'first': '/v2/images',
            'schema': '/v2/schemas/images',
        }
        if query:
            body['first'] = '%s?%s' % (body['first'], query)
        if 'next_marker' in result:
            params['marker'] = result['next_marker']
            next_query = urlparse.urlencode(params)
            body['next'] = '/v2/images?%s' % next_query
        response.unicode_body = six.text_type(json.dumps(body,
                                                         ensure_ascii=False))
        response.content_type = 'application/json'

    def delete(self, response, result):
        response.status_int = http.NO_CONTENT

    def import_image(self, response, result):
        response.status_int = http.ACCEPTED


def get_base_properties():
    return {
        'id': {
            'type': 'string',
            'description': _('An identifier for the image'),
            'pattern': ('^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}'
                        '-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$'),
        },
        'name': {
            'type': ['null', 'string'],
            'description': _('Descriptive name for the image'),
            'maxLength': 255,
        },
        'status': {
            'type': 'string',
            'readOnly': True,
            'description': _('Status of the image'),
            'enum': ['queued', 'saving', 'active', 'killed',
                     'deleted', 'uploading', 'importing',
                     'pending_delete', 'deactivated'],
        },
        'visibility': {
            'type': 'string',
            'description': _('Scope of image accessibility'),
            'enum': ['community', 'public', 'private', 'shared'],
        },
        'protected': {
            'type': 'boolean',
            'description': _('If true, image will not be deletable.'),
        },
        'os_hidden': {
            'type': 'boolean',
            'description': _('If true, image will not appear in default '
                             'image list response.'),
        },
        'checksum': {
            'type': ['null', 'string'],
            'readOnly': True,
            'description': _('md5 hash of image contents.'),
            'maxLength': 32,
        },
        'os_hash_algo': {
            'type': ['null', 'string'],
            'readOnly': True,
            'description': _('Algorithm to calculate the os_hash_value'),
            'maxLength': 64,
        },
        'os_hash_value': {
            'type': ['null', 'string'],
            'readOnly': True,
            'description': _('Hexdigest of the image contents using the '
                             'algorithm specified by the os_hash_algo'),
            'maxLength': 128,
        },
        'owner': {
            'type': ['null', 'string'],
            'description': _('Owner of the image'),
            'maxLength': 255,
        },
        'size': {
            'type': ['null', 'integer'],
            'readOnly': True,
            'description': _('Size of image file in bytes'),
        },
        'virtual_size': {
            'type': ['null', 'integer'],
            'readOnly': True,
            'description': _('Virtual size of image in bytes'),
        },
        'container_format': {
            'type': ['null', 'string'],
            'description': _('Format of the container'),
            'enum': [None] + CONF.image_format.container_formats,
        },
        'disk_format': {
            'type': ['null', 'string'],
            'description': _('Format of the disk'),
            'enum': [None] + CONF.image_format.disk_formats,
        },
        'created_at': {
            'type': 'string',
            'readOnly': True,
            'description': _('Date and time of image registration'
                             ),
            # TODO(bcwaldon): our jsonschema library doesn't seem to like the
            # format attribute, figure out why!
            # 'format': 'date-time',
        },
        'updated_at': {
            'type': 'string',
            'readOnly': True,
            'description': _('Date and time of the last image modification'
                             ),
            # 'format': 'date-time',
        },
        'tags': {
            'type': 'array',
            'description': _('List of strings related to the image'),
            'items': {
                'type': 'string',
                'maxLength': 255,
            },
        },
        'direct_url': {
            'type': 'string',
            'readOnly': True,
            'description': _('URL to access the image file kept in external '
                             'store'),
        },
        'min_ram': {
            'type': 'integer',
            'description': _('Amount of ram (in MB) required to boot image.'),
        },
        'min_disk': {
            'type': 'integer',
            'description': _('Amount of disk space (in GB) required to boot '
                             'image.'),
        },
        'self': {
            'type': 'string',
            'readOnly': True,
            'description': _('An image self url'),
        },
        'file': {
            'type': 'string',
            'readOnly': True,
            'description': _('An image file url'),
        },
        'backend': {
            'type': 'string',
            'readOnly': True,
            'description': _('Backend store to upload image to'),
        },
        'schema': {
            'type': 'string',
            'readOnly': True,
            'description': _('An image schema url'),
        },
        'locations': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'maxLength': 255,
                    },
                    'metadata': {
                        'type': 'object',
                    },
                    'validation_data': {
                        'description': _(
                            'Values to be used to populate the corresponding '
                            'image properties. If the image status is not '
                            '\'queued\', values must exactly match those '
                            'already contained in the image properties.'
                        ),
                        'type': 'object',
                        'writeOnly': True,
                        'additionalProperties': False,
                        'properties': {
                            'checksum': {
                                'type': 'string',
                                'minLength': 32,
                                'maxLength': 32,
                            },
                            'os_hash_algo': {
                                'type': 'string',
                                'maxLength': 64,
                            },
                            'os_hash_value': {
                                'type': 'string',
                                'maxLength': 128,
                            },
                        },
                        'required': [
                            'os_hash_algo',
                            'os_hash_value',
                        ],
                    },
                },
                'required': ['url', 'metadata'],
            },
            'description': _('A set of URLs to access the image file kept in '
                             'external store'),
        },
    }


def _get_base_links():
    return [
        {'rel': 'self', 'href': '{self}'},
        {'rel': 'enclosure', 'href': '{file}'},
        {'rel': 'describedby', 'href': '{schema}'},
    ]


def get_schema(custom_properties=None):
    properties = get_base_properties()
    links = _get_base_links()
    if CONF.allow_additional_image_properties:
        schema = glance.schema.PermissiveSchema('image', properties, links)
    else:
        schema = glance.schema.Schema('image', properties)

    if custom_properties:
        for property_value in custom_properties.values():
            property_value['is_base'] = False
        schema.merge_properties(custom_properties)
    return schema


def get_collection_schema(custom_properties=None):
    image_schema = get_schema(custom_properties)
    return glance.schema.CollectionSchema('images', image_schema)


def load_custom_properties():
    """Find the schema properties files and load them into a dict."""
    filename = 'schema-image.json'
    match = CONF.find_file(filename)
    if match:
        with open(match, 'r') as schema_file:
            schema_data = schema_file.read()
        return json.loads(schema_data)
    else:
        msg = (_LW('Could not find schema properties file %s. Continuing '
                   'without custom properties') % filename)
        LOG.warn(msg)
        return {}


def create_resource(custom_properties=None):
    """Images resource factory method"""
    schema = get_schema(custom_properties)
    deserializer = RequestDeserializer(schema)
    serializer = ResponseSerializer(schema)
    controller = ImagesController()
    return wsgi.Resource(controller, deserializer, serializer)
