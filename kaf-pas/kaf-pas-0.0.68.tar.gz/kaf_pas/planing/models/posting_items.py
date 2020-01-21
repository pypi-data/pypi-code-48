import logging

from django.conf import settings
from django.db import transaction
from django.forms import model_to_dict

from isc_common import delAttr
from isc_common.http.DSRequest import DSRequest
from isc_common.number import DelProps
from kaf_pas.planing.models.operations import Operations, OperationsManager, OperationsQuerySet
from kaf_pas.planing.models.operations_view import Operations_view

logger = logging.getLogger(__name__)


class Posting_itemsQuerySet(OperationsQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Posting_itemsManager(OperationsManager):
    def createFromRequest(self, request, removed=None):
        from kaf_pas.planing.models.operation_locations import Operation_locations
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.accounting.models.tmp_buffer import Tmp_buffer

        request = DSRequest(request=request)
        data = request.get_data()
        user_id = request.user_id
        items = data.get('items')
        if isinstance(items, list):
            delAttr(data, 'items')
            _data = data.copy()
            delAttr(_data, 'dataSource')
            delAttr(_data, 'operationType')
            delAttr(_data, 'textMatchStyle')
            delAttr(_data, 'form')
            _data.setdefault('opertype', settings.OPERS_TYPES_STACK.POSTING_TASK)

            with transaction.atomic():
                parent = Operations.objects.create(**_data)
                Operation_refs.objects.create(child=parent)

                for item in items:
                    child = dict()
                    child.setdefault('lastmodified', parent.lastmodified)
                    child.setdefault('opertype', settings.OPERS_TYPES_STACK.POSTING_DETAIL_TASK)
                    child = Operations.objects.create(**child)

                    Operation_refs.objects.create(parent=parent, child=child)

                    if item.get('location_id'):
                        Operation_locations.objects.create(operation=child, location_id=item.get('location_id'))

                    if item.get('item_id'):
                        Operation_item.objects.create(operation=child, item_id=item.get('item_id'))

                    if item.get('value'):
                        Operation_value.objects.create(operation=child, value=item.get('value'), edizm_id=item.get('edizm_id'))


                Tmp_buffer.objects.filter(user_id=user_id).delete()

                parent = model_to_dict(parent)
                return DelProps(parent)
        else:
            return {}

    def get_queryset(self):
        return Posting_itemsQuerySet(self.model, using=self._db)


class Posting_items(Operations_view):
    objects = Posting_itemsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        proxy = True
        verbose_name = 'Оприходования'
