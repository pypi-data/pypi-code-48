# Copyright 2015-2018 CERN for the benefit of the ATLAS collaboration.
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
# - Vincent Garonne <vgaronne@gmail.com>, 2015
# - Cedric Serfon <cedric.serfon@cern.ch>, 2015
# - Mario Lassnig <mario.lassnig@cern.ch>, 2018
# - Hannes Hansen <hannes.jakob.hansen@cern.ch>, 2018-2019
# - Andrew Lister, <andrew.lister@stfc.ac.uk>, 2019
#
# PY3K COMPATIBLE

from nose.tools import assert_equal, assert_true

from rucio.core.did import attach_dids, add_did, add_dids
from rucio.core.replica import list_datasets_per_rse, update_collection_replica, get_cleaned_updated_collection_replicas, delete_replicas, add_replicas
from rucio.core.rse import add_rse, del_rse, add_protocol, get_rse_id
from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.ruleclient import RuleClient
from rucio.common.types import InternalAccount, InternalScope
from rucio.common.utils import generate_uuid
from rucio.db.sqla import session, models, constants
from rucio.tests.common import rse_name_generator


class TestDatasetReplicaClient:

    def test_list_dataset_replicas(self):
        """ REPLICA (CLIENT): List dataset replicas."""
        replica_client = ReplicaClient()
        rule_client = RuleClient()
        did_client = DIDClient()
        scope = 'mock'
        dataset = 'dataset_' + str(generate_uuid())

        did_client.add_dataset(scope=scope, name=dataset)
        rule_client.add_replication_rule(dids=[{'scope': scope, 'name': dataset}],
                                         account='root', copies=1, rse_expression='MOCK',
                                         grouping='DATASET')
        replicas = [r for r in replica_client.list_dataset_replicas(scope=scope, name=dataset)]
        assert_equal(len(replicas), 1)

    def test_list_datasets_per_rse(self):
        """ REPLICA (CLIENT): List datasets in RSE."""
        rule_client = RuleClient()
        did_client = DIDClient()
        scope = 'mock'
        dataset = 'dataset_' + str(generate_uuid())

        did_client.add_dataset(scope=scope, name=dataset)
        rule_client.add_replication_rule(dids=[{'scope': scope, 'name': dataset}],
                                         account='root', copies=1, rse_expression='MOCK',
                                         grouping='DATASET')
        replicas = [r for r in list_datasets_per_rse(rse_id=get_rse_id(rse='MOCK'), filters={'scope': InternalScope('mock'), 'name': 'data*'})]
        assert(replicas != [])

    def test_list_dataset_replicas_archive(self):
        """ REPLICA (CLIENT): List dataset replicas with archives. """

        replica_client = ReplicaClient()
        did_client = DIDClient()
        rule_client = RuleClient()

        scope = 'mock'

        rse = 'APERTURE_%s' % rse_name_generator()
        rse_id = add_rse(rse)
        add_protocol(rse_id=rse_id, parameter={'scheme': 'root',
                                               'hostname': 'root.aperture.com',
                                               'port': 1409,
                                               'prefix': '//test/chamber/',
                                               'impl': 'rucio.rse.protocols.xrootd.Default',
                                               'domains': {
                                                   'lan': {'read': 1, 'write': 1, 'delete': 1},
                                                   'wan': {'read': 1, 'write': 1, 'delete': 1}}})

        rse2 = 'BLACKMESA_%s' % rse_name_generator()
        rse2_id = add_rse(rse2)
        add_protocol(rse_id=rse2_id, parameter={'scheme': 'root',
                                                'hostname': 'root.blackmesa.com',
                                                'port': 1409,
                                                'prefix': '//underground/facility',
                                                'impl': 'rucio.rse.protocols.xrootd.Default',
                                                'domains': {
                                                    'lan': {'read': 1, 'write': 1, 'delete': 1},
                                                    'wan': {'read': 1, 'write': 1, 'delete': 1}}})

        # register archive
        archive = {'scope': scope, 'name': 'another.%s.zip' % generate_uuid(),
                   'type': 'FILE', 'bytes': 2596, 'adler32': 'deedbeaf'}
        replica_client.add_replicas(rse=rse, files=[archive])
        replica_client.add_replicas(rse=rse2, files=[archive])

        archived_files = [{'scope': scope, 'name': 'zippedfile-%i-%s' % (i, str(generate_uuid())), 'type': 'FILE',
                           'bytes': 4322, 'adler32': 'deaddead'} for i in range(2)]
        replica_client.add_replicas(rse=rse2, files=archived_files)
        did_client.add_files_to_archive(scope=scope, name=archive['name'], files=archived_files)

        dataset_name = 'find_me.' + str(generate_uuid())
        did_client.add_dataset(scope=scope, name=dataset_name)
        did_client.attach_dids(scope=scope, name=dataset_name, dids=archived_files)
        rule_client.add_replication_rule(dids=[{'scope': scope, 'name': dataset_name}],
                                         account='root', copies=1, rse_expression=rse,
                                         grouping='DATASET')

        res = [r for r in replica_client.list_dataset_replicas(scope=scope,
                                                               name=dataset_name)]
        assert_equal(len(res), 1)
        assert_equal(res[0]['state'], 'UNAVAILABLE')

        res = [r for r in replica_client.list_dataset_replicas(scope=scope,
                                                               name=dataset_name,
                                                               deep=True)]

        assert_equal(len(res), 3)
        assert_equal(res[0]['state'], 'AVAILABLE')
        assert_equal(res[1]['state'], 'AVAILABLE')
        assert_equal(res[2]['state'], 'AVAILABLE')

        del_rse(rse_id)


class TestDatasetReplicaUpdate:
    def setUp(self):
        self.scope = InternalScope('mock')
        self.rse = 'MOCK4'
        self.rse2 = 'MOCK3'
        self.account = InternalAccount('root')
        self.rse_id = get_rse_id(self.rse)
        self.rse2_id = get_rse_id(self.rse2)
        self.db_session = session.get_session()

    def tearDown(self):
        self.db_session.commit()  # pylint: disable=no-member

    def test_clean_and_get_collection_replica_updates(self):
        """ REPLICA (CORE): Get cleaned update requests for collection replicas. """
        dataset_name_with_collection_replica = 'dataset_with_rse%s' % generate_uuid()
        dataset_name_without_collection_replica = 'dataset_without_rse%s' % generate_uuid()
        add_dids(dids=[{'name': dataset_name_without_collection_replica, 'scope': self.scope, 'type': constants.DIDType.DATASET},
                       {'name': dataset_name_with_collection_replica, 'scope': self.scope, 'type': constants.DIDType.DATASET}], account=self.account, session=self.db_session)
        self.db_session.query(models.UpdatedCollectionReplica).delete()  # pylint: disable=no-member
        self.db_session.commit()  # pylint: disable=no-member

        # setup test data - 4 without corresponding replica, 4 duplicates and 2 correct
        models.CollectionReplica(rse_id=self.rse_id, scope=self.scope, bytes=10, state=constants.ReplicaState.AVAILABLE, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name_without_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name_without_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name_without_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name_without_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name_with_collection_replica, did_type=constants.DIDType.DATASET).save(session=self.db_session)

        cleaned_collection_replica_updates = get_cleaned_updated_collection_replicas(total_workers=0, worker_number=0, session=self.db_session)
        assert_equal(len(cleaned_collection_replica_updates), 2)
        for update_request in cleaned_collection_replica_updates:
            update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(id=update_request['id']).one()  # pylint: disable=no-member
            assert_equal(update_request.scope, self.scope)
            assert_true(update_request.name in (dataset_name_with_collection_replica, dataset_name_without_collection_replica))

    def test_update_collection_replica(self):
        """ REPLICA (CORE): Update collection replicas from update requests. """
        file_size = 2
        files = [{'name': 'file_%s' % generate_uuid(), 'scope': self.scope, 'bytes': file_size} for i in range(0, 2)]
        dataset_name = 'dataset_test_%s' % generate_uuid()
        add_replicas(rse_id=self.rse_id, files=files, account=self.account, session=self.db_session)
        add_did(scope=self.scope, name=dataset_name, type=constants.DIDType.DATASET, account=self.account, session=self.db_session)
        attach_dids(scope=self.scope, name=dataset_name, dids=files, account=self.account, session=self.db_session)
        models.CollectionReplica(rse_id=self.rse_id, scope=self.scope, state=constants.ReplicaState.AVAILABLE, name=dataset_name, did_type=constants.DIDType.DATASET, bytes=len(files) * file_size, length=len(files)).save(session=self.db_session)

        # Update request with rse id
        # First update -> dataset replica should be available
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(rse_id=self.rse_id, scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(id=update_request.id).first()  # pylint: disable=no-member
        assert_equal(update_request, None)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')

        # Delete one file replica -> dataset replica should be unavailable
        delete_replicas(rse_id=self.rse_id, files=[files[0]], session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(rse_id=self.rse_id, scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'UNAVAILABLE')

        # Add one file replica -> dataset replica should be available again
        add_replicas(rse_id=self.rse_id, files=[files[0]], account=self.account, session=self.db_session)
        attach_dids(scope=self.scope, name=dataset_name, dids=[files[0]], account=self.account, session=self.db_session)
        models.UpdatedCollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(rse_id=self.rse_id, scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')

        # Delete all file replicas -> dataset replica should be deleted
        delete_replicas(rse_id=self.rse_id, files=files, session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(rse_id=self.rse_id, scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name).all()  # pylint: disable=no-member
        assert_equal(len(dataset_replica), 0)

        # Update request without rse_id - using two replicas per file -> total 4 replicas
        add_replicas(rse_id=self.rse_id, files=files, account=self.account, session=self.db_session)
        add_replicas(rse_id=self.rse2_id, files=files, account=self.account, session=self.db_session)
        attach_dids(scope=self.scope, name=dataset_name, dids=files, account=self.account, session=self.db_session)
        models.CollectionReplica(rse_id=self.rse_id, scope=self.scope, name=dataset_name, state=constants.ReplicaState.UNAVAILABLE, did_type=constants.DIDType.DATASET, bytes=len(files) * file_size, length=len(files)).save(session=self.db_session)
        models.CollectionReplica(rse_id=self.rse2_id, scope=self.scope, name=dataset_name, state=constants.ReplicaState.UNAVAILABLE, did_type=constants.DIDType.DATASET, bytes=len(files) * file_size, length=len(files)).save(session=self.db_session)

        # First update -> replicas should be available
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter_by(scope=self.scope, name=dataset_name).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        for dataset_replica in self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name).all():  # pylint: disable=no-member
            assert_equal(dataset_replica['bytes'], len(files) * file_size)
            assert_equal(dataset_replica['length'], len(files))
            assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
            assert_equal(dataset_replica['available_replicas_cnt'], len(files))
            assert_equal(str(dataset_replica['state']), 'AVAILABLE')

        # Delete first replica on first RSE -> replica on first RSE should be unavailable, replica on second RSE should be still available
        delete_replicas(rse_id=self.rse_id, files=[files[0]], session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        # delete_replica creates also update object but with rse_id -> extra filter for rse_id is NULL
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter(models.UpdatedCollectionReplica.scope == self.scope, models.UpdatedCollectionReplica.name == dataset_name,  # pylint: disable=no-member
                                                                                       models.UpdatedCollectionReplica.rse_id.is_(None)).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'UNAVAILABLE')
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse2_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')

        # Set the state of the first replica on the second RSE to UNAVAILABLE -> both replicass should be unavailable
        file_replica = self.db_session.query(models.RSEFileAssociation).filter_by(rse_id=self.rse2_id, scope=self.scope, name=files[0]['name']).one()  # pylint: disable=no-member
        file_replica.state = constants.ReplicaState.UNAVAILABLE
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter(models.UpdatedCollectionReplica.scope == self.scope, models.UpdatedCollectionReplica.name == dataset_name,  # pylint: disable=no-member
                                                                                       models.UpdatedCollectionReplica.rse_id.is_(None)).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'UNAVAILABLE')
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse2_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'UNAVAILABLE')

        # Delete first replica on second RSE -> file is not longer part of dataset -> both replicas should be available
        delete_replicas(rse_id=self.rse2_id, files=[files[0]], session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter(models.UpdatedCollectionReplica.scope == self.scope, models.UpdatedCollectionReplica.name == dataset_name,  # pylint: disable=no-member
                                                                                       models.UpdatedCollectionReplica.rse_id.is_(None)).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['length'], len(files) - 1)
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse2_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['length'], len(files) - 1)
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')

        # Add first replica to the first RSE -> first replicas should be available
        add_replicas(rse_id=self.rse_id, files=[files[0]], account=self.account, session=self.db_session)
        attach_dids(scope=self.scope, name=dataset_name, dids=[files[0]], account=self.account, session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter(models.UpdatedCollectionReplica.scope == self.scope, models.UpdatedCollectionReplica.name == dataset_name,  # pylint: disable=no-member
                                                                                       models.UpdatedCollectionReplica.rse_id.is_(None)).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse2_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], (len(files) - 1) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files) - 1)
        assert_equal(str(dataset_replica['state']), 'UNAVAILABLE')

        # Add first replica to the second RSE -> both replicas should be available again
        add_replicas(rse_id=self.rse2_id, files=[files[0]], account=self.account, session=self.db_session)
        models.UpdatedCollectionReplica(scope=self.scope, name=dataset_name, did_type=constants.DIDType.DATASET).save(session=self.db_session)
        update_request = self.db_session.query(models.UpdatedCollectionReplica).filter(models.UpdatedCollectionReplica.scope == self.scope, models.UpdatedCollectionReplica.name == dataset_name,  # pylint: disable=no-member
                                                                                       models.UpdatedCollectionReplica.rse_id.is_(None)).one()  # pylint: disable=no-member
        update_collection_replica(update_request=update_request.to_dict(), session=self.db_session)
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')
        dataset_replica = self.db_session.query(models.CollectionReplica).filter_by(scope=self.scope, name=dataset_name, rse_id=self.rse2_id).one()  # pylint: disable=no-member
        assert_equal(dataset_replica['bytes'], len(files) * file_size)
        assert_equal(dataset_replica['length'], len(files))
        assert_equal(dataset_replica['available_bytes'], len(files) * file_size)
        assert_equal(dataset_replica['available_replicas_cnt'], len(files))
        assert_equal(str(dataset_replica['state']), 'AVAILABLE')
