#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for google.apphosting.tools.devappserver2.api_server."""



import argparse
import cStringIO
import getpass
import itertools
import os
import pickle
import sys
import tempfile
import unittest
import urllib
import urllib2
import wsgiref.util

import google
import mock
import mox

from google.net.rpc.python.testing import rpc_test_harness

from google.appengine.api import apiproxy_stub
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_service_pb
from google.appengine.api import user_service_pb
from google.appengine.api.app_identity import app_identity_stub
from google.appengine.api.capabilities import capability_stub
from google.appengine.api.logservice import logservice_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.taskqueue import taskqueue_stub
from google.appengine.datastore import datastore_pb
from google.appengine.datastore import datastore_sqlite_stub
from google.appengine.datastore import datastore_stub_util
from google.appengine.datastore import datastore_v4_pb
from google.appengine.ext.remote_api import remote_api_pb
from google.appengine.runtime import apiproxy_errors
from google.appengine.tools.devappserver2 import api_server
from google.appengine.tools.devappserver2 import datastore_grpc_stub
from google.appengine.tools.devappserver2 import metrics
from google.appengine.tools.devappserver2 import shutdown
from google.appengine.tools.devappserver2 import stub_util
from google.appengine.tools.devappserver2 import wsgi_request_info
from google.appengine.tools.devappserver2 import wsgi_test_utils

APP_ID = 'test'
APPLICATION_ROOT = '/tmp'
TRUSTED = False
_, BLOBSTORE_PATH = tempfile.mkstemp(prefix='ae-blobstore')
_, DATASTORE_PATH = tempfile.mkstemp(prefix='ae-datastore')
DATASTORE_REQUIRE_INDEXES = False
IMAGES_HOST_PREFIX = 'localhost:8080'
LOGS_PATH = ':memory:'
MAIL_SMTP_HOST = 'localhost'
MAIL_SMTP_PORT = 80
MAIL_SMTP_USER = 'user'
MAIL_SMTP_PASSWORD = 'abc123'
MAIL_ENABLE_SENDMAIL = False
MAIL_SHOW_MAIL_BODY = True
TASKQUEUE_AUTO_RUN_TASKS = False
TASKQUEUE_DEFAULT_HTTP_SERVER = 'localhost:8080'
USER_LOGIN_URL = 'https://localhost/Login?continue=%s'
USER_LOGOUT_URL = 'https://localhost/Logout?continue=%s'

request_data = wsgi_request_info.WSGIRequestInfo(None)


class FakeURLFetchServiceStub(apiproxy_stub.APIProxyStub):
  def __init__(self):
    super(FakeURLFetchServiceStub, self).__init__('urlfetch')

  def _Dynamic_Fetch(self, request, unused_response):
    if request.url() == 'exception':
      raise IOError('the remote error')
    elif request.url() == 'application_error':
      raise apiproxy_errors.ApplicationError(23, 'details')


class FakeDatastoreV4ServiceStub(apiproxy_stub.APIProxyStub):
  def __init__(self):
    super(FakeDatastoreV4ServiceStub, self).__init__('datastore_v4')

  def _Dynamic_BeginTransaction(self, request, response):
    response.set_transaction('whatever')


def setup_stubs():
  """Setup the API stubs. This can only be done once."""
  stub_util.setup_test_stubs(
      request_data,
      app_id=APP_ID,
      application_root=APPLICATION_ROOT,
      trusted=TRUSTED,
      blobstore_path=BLOBSTORE_PATH,
      datastore_consistency=datastore_stub_util.TimeBasedHRConsistencyPolicy(),
      datastore_path=DATASTORE_PATH,
      datastore_require_indexes=DATASTORE_REQUIRE_INDEXES,
      images_host_prefix=IMAGES_HOST_PREFIX,
      logs_path=':memory:',
      mail_smtp_host=MAIL_SMTP_HOST,
      mail_smtp_port=MAIL_SMTP_PORT,
      mail_smtp_user=MAIL_SMTP_USER,
      mail_smtp_password=MAIL_SMTP_PASSWORD,
      mail_enable_sendmail=MAIL_ENABLE_SENDMAIL,
      mail_show_mail_body=MAIL_SHOW_MAIL_BODY,
      taskqueue_auto_run_tasks=TASKQUEUE_AUTO_RUN_TASKS,
      taskqueue_default_http_server=TASKQUEUE_DEFAULT_HTTP_SERVER,
      user_login_url=USER_LOGIN_URL,
      user_logout_url=USER_LOGOUT_URL)
  apiproxy_stub_map.apiproxy.ReplaceStub(
      'urlfetch', FakeURLFetchServiceStub())
  apiproxy_stub_map.apiproxy.ReplaceStub(
      'datastore_v4', FakeDatastoreV4ServiceStub())


class APIServerTestBase(wsgi_test_utils.WSGITestCase):
  """Tests for api_server.APIServer."""

  def setUp(self):
    setup_stubs()
    self.server = api_server.APIServer('localhost',
                                       0,
                                       APP_ID)

  def tearDown(self):
    stub_util.cleanup_stubs()

  def _assert_remote_call(
      self, expected_remote_response, stub_request, service, method):
    """Test a call across the remote API to the API server.

    Args:
      expected_remote_response: the remote response that is expected.
      stub_request: the request protobuf that the stub expects.
      service: the stub's service name.
      method: which service method to call.
    """
    request_environ = {'HTTP_HOST': 'machine:8080'}
    wsgiref.util.setup_testing_defaults(request_environ)

    with request_data.request(request_environ, None) as request_id:
      remote_request = remote_api_pb.Request()
      remote_request.set_service_name(service)
      remote_request.set_method(method)
      remote_request.set_request(stub_request.Encode())
      remote_request.set_request_id(request_id)
      remote_payload = remote_request.Encode()

      environ = {'CONTENT_LENGTH': len(remote_payload),
                 'REQUEST_METHOD': 'POST',
                 'wsgi.input': cStringIO.StringIO(remote_payload)}

      expected_headers = {'Content-Type': 'application/octet-stream'}
      self.assertResponse('200 OK',
                          expected_headers,
                          expected_remote_response.Encode(),
                          self.server,
                          environ)


class TestAPIServer(APIServerTestBase):

  def test_user_api_call(self):
    logout_response = user_service_pb.CreateLogoutURLResponse()
    logout_response.set_logout_url(
        USER_LOGOUT_URL % urllib.quote('http://machine:8080/crazy_logout'))

    expected_remote_response = remote_api_pb.Response()
    expected_remote_response.set_response(logout_response.Encode())

    logout_request = user_service_pb.CreateLogoutURLRequest()
    logout_request.set_destination_url('/crazy_logout')

    self._assert_remote_call(
        expected_remote_response, logout_request, 'user', 'CreateLogoutURL')

  def test_datastore_v4_api_call(self):
    begin_transaction_response = datastore_v4_pb.BeginTransactionResponse()
    begin_transaction_response.set_transaction('whatever')

    expected_remote_response = remote_api_pb.Response()
    expected_remote_response.set_response(
        begin_transaction_response.Encode())

    begin_transaction_request = datastore_v4_pb.BeginTransactionRequest()

    self._assert_remote_call(
        expected_remote_response, begin_transaction_request,
        'datastore_v4', 'BeginTransaction')

  def test_datastore_v4_api_calls_handled(self):
    # We are only using RpcTestHarness as a clean way to get the list of
    # service methods.
    harness = rpc_test_harness.RpcTestHarness(
        datastore_v4_pb.DatastoreV4Service)
    deprecated = ['Get', 'Write']
    methods = set([k for k in harness.__dict__.keys()
                   if k not in deprecated and not k.startswith('_')])
    self.assertEqual(methods, set(stub_util.DATASTORE_V4_METHODS.keys()))

  def test_GET(self):
    environ = {'REQUEST_METHOD': 'GET',
               'QUERY_STRING': 'rtok=23'}
    self.assertResponse('200 OK',
                        {'Content-Type': 'text/plain'},
                        "{app_id: test, rtok: '23'}\n",
                        self.server,
                        environ)

  def test_unsupported_method(self):
    environ = {'REQUEST_METHOD': 'HEAD',
               'QUERY_STRING': 'rtok=23'}
    self.assertResponse('405 Method Not Allowed',
                        {},
                        '',
                        self.server,
                        environ)

  def test_exception(self):
    urlfetch_request = urlfetch_service_pb.URLFetchRequest()
    urlfetch_request.set_url('exception')
    urlfetch_request.set_method(urlfetch_service_pb.URLFetchRequest.GET)

    expected_remote_response = remote_api_pb.Response()
    expected_remote_response.set_exception(pickle.dumps(
        RuntimeError(repr(IOError('the remote error')))))

    self._assert_remote_call(
        expected_remote_response, urlfetch_request, 'urlfetch', 'Fetch')

  def test_application_error(self):
    urlfetch_request = urlfetch_service_pb.URLFetchRequest()
    urlfetch_request.set_url('application_error')
    urlfetch_request.set_method(urlfetch_service_pb.URLFetchRequest.GET)

    expected_remote_response = remote_api_pb.Response()
    expected_remote_response.mutable_application_error().set_code(23)
    expected_remote_response.mutable_application_error().set_detail('details')
    expected_remote_response.set_exception(pickle.dumps(
        apiproxy_errors.ApplicationError(23, 'details')))

    self._assert_remote_call(
        expected_remote_response, urlfetch_request, 'urlfetch', 'Fetch')


class TestAPIServerWithEmulator(APIServerTestBase):
  """Test ApiServer working with cloud datastore emulator."""

  def setUp(self):
    super(TestAPIServerWithEmulator, self).setUp()
    apiproxy_stub_map.apiproxy.ReplaceStub(
        'datastore_v3', datastore_grpc_stub.DatastoreGrpcStub(''))

  def test_datastore_emulator_request_too_large(self):
    fake_put_request = datastore_pb.PutRequest()
    fake_put_request.Encode = lambda: 'x' * (apiproxy_stub.MAX_REQUEST_SIZE + 1)

    expected_remote_response = remote_api_pb.Response()
    expected_remote_response.set_exception(pickle.dumps(
        apiproxy_errors.RequestTooLargeError(
            apiproxy_stub.REQ_SIZE_EXCEEDS_LIMIT_MSG_TEMPLATE % (
                'datastore_v3', 'Put'))))
    self._assert_remote_call(expected_remote_response, fake_put_request,
                             'datastore_v3', 'Put')


class TestApiServerMain(unittest.TestCase):

  @mock.patch.object(api_server, 'create_api_server')
  @mock.patch.object(shutdown, 'wait_until_shutdown')
  @mock.patch.object(metrics._MetricsLogger, 'Start')
  @mock.patch.object(metrics._MetricsLogger, 'Stop')
  @mock.patch.object(argparse.ArgumentParser, 'parse_args',
                     return_value=argparse.Namespace(
                         google_analytics_client_id='myid',
                         google_analytics_user_agent='myagent',
                         support_datastore_emulator=True,
                         storage_path='/tmp',
                         app_id='',
                         dev_appserver_log_level='info',
                         config_paths=None,
                         java_app_base_url=None))
  def testMetrics(self,
                  unused_mock_parse,
                  mock_stop,
                  mock_start,
                  mock_wait_until_shutdown,
                  mock_create_api_server):
    """Tests metrics logging flow is triggered by api_server main()."""
    api_server.main()
    mock_create_api_server.assert_called_once()
    mock_wait_until_shutdown.assert_called_once()
    mock_start.assert_called_once_with(
        'myid', user_agent='myagent', support_datastore_emulator=True,
        category=metrics.API_SERVER_CATEGORY)
    mock_stop.assert_called_once()


class GetStoragePathTest(unittest.TestCase):
  """Tests for api_server.get_storage_path."""

  def setUp(self):
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(api_server, '_generate_storage_paths')

  def tearDown(self):
    self.mox.UnsetStubs()

  def test_no_path_given_directory_does_not_exist(self):
    path = tempfile.mkdtemp()
    os.rmdir(path)
    api_server._generate_storage_paths('example.com_myapp').AndReturn([path])

    self.mox.ReplayAll()
    self.assertEqual(
        path, api_server.get_storage_path(None, 'dev~example.com:myapp'))
    self.mox.VerifyAll()
    self.assertTrue(os.path.isdir(path))

  def test_no_path_given_directory_exists(self):
    path1 = tempfile.mkdtemp()
    os.chmod(path1, 0777)
    path2 = tempfile.mkdtemp()  # Made with mode 0700.

    api_server._generate_storage_paths('example.com_myapp').AndReturn(
        [path1, path2])

    self.mox.ReplayAll()
    if sys.platform == 'win32':
      expected_path = path1
    else:
      expected_path = path2
    self.assertEqual(
        expected_path,
        api_server.get_storage_path(None, 'dev~example.com:myapp'))
    self.mox.VerifyAll()

  def test_path_given_does_not_exist(self):
    path = tempfile.mkdtemp()
    os.rmdir(path)

    self.assertEqual(
        path, api_server.get_storage_path(path, 'dev~example.com:myapp'))
    self.assertTrue(os.path.isdir(path))

  def test_path_given_not_directory(self):
    _, path = tempfile.mkstemp()

    self.assertRaises(
        IOError, api_server.get_storage_path, path, 'dev~example.com:myapp')

  def test_path_given_exists(self):
    path = tempfile.mkdtemp()

    self.assertEqual(
        path, api_server.get_storage_path(path, 'dev~example.com:myapp'))


class GenerateStoragePathsTest(unittest.TestCase):
  """Tests for api_server._generate_storage_paths."""

  def setUp(self):
    self.mox = mox.Mox()
    self.mox.StubOutWithMock(getpass, 'getuser')
    self.mox.StubOutWithMock(tempfile, 'gettempdir')

  def tearDown(self):
    self.mox.UnsetStubs()

  @unittest.skipUnless(sys.platform.startswith('win'), 'Windows only')
  def test_windows(self):
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual(
        [os.path.join('/tmp', 'appengine.myapp'),
         os.path.join('/tmp', 'appengine.myapp.1'),
         os.path.join('/tmp', 'appengine.myapp.2')],
        list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()

  @unittest.skipIf(sys.platform.startswith('win'), 'not on Windows')
  def test_working_getuser(self):
    getpass.getuser().AndReturn('johndoe')
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual(
        [os.path.join('/tmp', 'appengine.myapp.johndoe'),
         os.path.join('/tmp', 'appengine.myapp.johndoe.1'),
         os.path.join('/tmp', 'appengine.myapp.johndoe.2')],
        list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()

  @unittest.skipIf(sys.platform.startswith('win'), 'not on Windows')
  def test_broken_getuser(self):
    getpass.getuser().AndRaise(Exception())
    tempfile.gettempdir().AndReturn('/tmp')

    self.mox.ReplayAll()
    self.assertEqual(
        [os.path.join('/tmp', 'appengine.myapp'),
         os.path.join('/tmp', 'appengine.myapp.1'),
         os.path.join('/tmp', 'appengine.myapp.2')],
        list(itertools.islice(api_server._generate_storage_paths('myapp'), 3)))
    self.mox.VerifyAll()


class ClearApiServer(unittest.TestCase):
  """Tests for api_server._handle_CLEAR."""

  def setUp(self):
    self.server = api_server.APIServer('localhost', 0, '')

    self.app_identity_stub = mock.create_autospec(
        app_identity_stub.AppIdentityServiceStub)
    self.capability_stub = mock.create_autospec(
        capability_stub.CapabilityServiceStub)
    self.datastore_v3_stub = mock.create_autospec(
        datastore_sqlite_stub.DatastoreSqliteStub)
    self.logservice_stub = mock.create_autospec(logservice_stub.LogServiceStub)
    self.mail_stub = mock.create_autospec(mail_stub.MailServiceStub)
    self.memcache_stub = mock.create_autospec(memcache_stub.MemcacheServiceStub)
    self.taskqueue_stub = mock.create_autospec(
        taskqueue_stub.TaskQueueServiceStub)
    self.clearable_stubs = set([
        self.app_identity_stub, self.capability_stub, self.datastore_v3_stub,
        self.logservice_stub, self.mail_stub, self.memcache_stub,
        self.taskqueue_stub
    ])

    apiproxy_stub_map.apiproxy.ReplaceStub('app_identity_service',
                                           self.app_identity_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('capability_service',
                                           self.capability_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub(
        'datastore_v3', self.datastore_v3_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('logservice', self.logservice_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('mail', self.mail_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('memcache', self.memcache_stub)
    apiproxy_stub_map.apiproxy.ReplaceStub('taskqueue', self.taskqueue_stub)

  def test_clear_all(self):
    """Tests that all stubs are cleared."""
    environ = {'QUERY_STRING': ''}
    self.server._handle_CLEAR(environ, lambda *args: None)
    for stub in self.clearable_stubs:
      getattr(stub, 'Clear').assert_called_once()

  def test_clear_datastore_only(self):
    """Tests that only datastore stub is cleared."""
    environ = {'QUERY_STRING': 'stub=datastore_v3'}
    self.server._handle_CLEAR(environ, lambda *args: None)
    self.datastore_v3_stub.Clear.assert_called_once()
    for stub in self.clearable_stubs - set([self.datastore_v3_stub]):
      getattr(stub, 'Clear').assert_not_called()

  def test_clear_datastore_and_memcache(self):
    """Tests that both datastore and memcache stubs are cleared."""
    environ = {'QUERY_STRING': 'stub=datastore_v3&stub=memcache'}
    self.server._handle_CLEAR(environ, lambda *args: None)
    cleared_stubs = set([self.datastore_v3_stub, self.memcache_stub])
    for stub in cleared_stubs:
      getattr(stub, 'Clear').assert_called_once()
    for stub in self.clearable_stubs - cleared_stubs:
      getattr(stub, 'Clear').assert_not_called()


class LocalJavaAppDispatcherTest(unittest.TestCase):
  """Tests for request_info._LocalJavaAppDispatcher."""

  def setUp(self):
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testAddRequest(self):
    java_app_base_url = 'http://localhost:8080'
    relative_url = '/_ah/queue'
    body = 'body'
    headers = [('X-Header', 'x-header-value')]

    self.mox.StubOutWithMock(urllib2, 'urlopen')
    self.mox.StubOutClassWithMocks(urllib2, 'Request')

    urllib2_mock_request = urllib2.Request(
        url=java_app_base_url + relative_url, data=body, headers=dict(headers))

    urllib2_mock_response = self.mox.CreateMock(urllib2.addinfourl)
    urllib2_mock_response.getcode().AndReturn(200)

    urllib2.urlopen(urllib2_mock_request).AndReturn(urllib2_mock_response)

    dispatcher = api_server._LocalJavaAppDispatcher(
        java_app_base_url=java_app_base_url)

    self.mox.ReplayAll()
    dispatcher.add_request(
        method='POST',
        relative_url=relative_url,
        headers=headers,
        body=body,
        source_ip='127.0.0.1')
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()
