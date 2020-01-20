# Copyright 2014-2019 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Tomas Javor Javurek <tomas.javurek@cern.ch>, 2019
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019

import os

from exceptions import NotImplementedError
from xml.dom import minidom

from rucio.common import exception
from rucio.common.utils import run_cmd_process
from rucio.rse.protocols import protocol


class Default(protocol.RSEProtocol):
    """ Implementing access to RSEs using the local filesystem."""

    def __init__(self, protocol_attr, rse_settings):
        """ Initializes the object with information about the referred RSE.

            :param props Properties derived from the RSE Repository
        """
        super(Default, self).__init__(protocol_attr, rse_settings)
        self.attributes.pop('determinism_type', None)
        self.files = []

    def lfns2pfns(self, lfns):
        """ Create fake storm:// path. Will be resolved at the get() stage later. """
        pfns = {}

        hostname = self.attributes['hostname']
        if '://' in hostname:
            hostname = hostname.split("://")[1]

        prefix = self.attributes['prefix']
        if not prefix.startswith('/'):
            prefix = ''.join(['/', prefix])
        if not prefix.endswith('/'):
            prefix = ''.join([prefix, '/'])

        lfns = [lfns] if isinstance(lfns, dict) else lfns
        for lfn in lfns:
            path = lfn['path'] if 'path' in lfn and lfn['path'] else self._get_path(scope=lfn['scope'].external,
                                                                                    name=lfn['name'])
            pfns['%s:%s' % (lfn['scope'], lfn['name'])] = ''.join(['storm://', hostname, ':', str(self.attributes['port']), prefix, path])

        return pfns

    def path2pfn(self, path):
        """
            Retruns a fully qualified PFN for the file referred by path.

            :param path: The path to the file.

            :returns: Fully qualified PFN.

        """
        return ''.join([self.rse['scheme'], '://%s' % self.rse['hostname'], path])

    def exists(self, pfn):
        """ Checks if the requested file is known by the referred RSE.

            :param pfn Physical file name

            :returns: True if the file exists, False if it doesn't

            :raise  ServiceUnavailable
        """
        raise NotImplementedError

    def connect(self):
        """ Establishes the actual connection to the referred RSE.

            :param credentials Provide all necessary information to establish a connection
                to the referred storage system. Some is loaded from the repository inside the
                RSE class and some must be provided specific for the SFTP protocol like
                username, password, private_key, private_key_pass, port.
                For details about possible additional parameters and details about their usage
                see the pysftp.Connection() documentation.
                NOTE: the host parametrer is overwritten with the value provided by the repository

            :raise RSEAccessDenied
        """
        pass

    def close(self):
        """ Closes the connection to RSE."""
        pass

    def get(self, pfn, dest, transfer_timeout=None):
        """ Provides access to files stored inside connected the RSE.

            :param pfn Physical file name of requested file
            :param dest Name and path of the files when stored at the client
            :param transfer_timeout Transfer timeout (in seconds)

            :raises DestinationNotAccessible, ServiceUnavailable, SourceNotFound
         """

        # storm prefix needs to be replaced by davs in order to get etag
        pfn = 'davs' + pfn[5:]

        # retrieve the TURL from the webdav etag, TODO: make it configurable
        cmd = 'davix-http --capath /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/etc/grid-security-emi/certificates --cert $X509_USER_PROXY -X PROPFIND %s' % pfn
        try:
            rcode, output = run_cmd_process(cmd, timeout=10)
        except Exception as e:
            raise exception.ServiceUnavailable('Could not retrieve STORM WebDAV ETag: %s' % str(e))
        p_output = minidom.parseString(output)

        # we need to strip off the quotation marks and the <timestamp> from the etag
        # but since we can have multiple underscores, we have to rely on the uniqueness
        # of the full LFN to make the split
        target = p_output.getElementsByTagName('d:getetag')[0].childNodes[0].nodeValue.replace('"', '')
        target_ending = '_' + target.split('_')[-1]
        target = target.split(target_ending)[0]

        # make the symlink
        try:
            os.symlink(target, dest)
        except Exception as e:
            exception.ServiceUnavailable('Could not create symlink: %s for target %s' % (str(e), str(target)))

    def put(self, source, target, source_dir=None, transfer_timeout=None):
        """ Allows to store files inside the referred RSE.

            :param source Physical file name
            :param target Name of the file on the storage system e.g. with prefixed scope
            :param source_dir Path where the to be transferred files are stored in the local file system
            :param transfer_timeout Transfer timeout (in seconds)

            :raises DestinationNotAccessible, ServiceUnavailable, SourceNotFound
            """
        raise NotImplementedError

    def delete(self, pfn):
        """ Deletes a file from the connected RSE.

            :param pfn Physical file name

            :raises ServiceUnavailable, SourceNotFound
        """
        raise NotImplementedError

    def rename(self, pfn, new_pfn):
        """ Allows to rename a file stored inside the connected RSE.

            :param pfn      Current physical file name
            :param new_pfn  New physical file name

            :raises DestinationNotAccessible, ServiceUnavailable, SourceNotFound
        """
        raise NotImplementedError
