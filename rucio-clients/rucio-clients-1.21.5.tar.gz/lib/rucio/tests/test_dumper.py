# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#              http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Fernando Lopez, <felopez@cern.ch>, 2015
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2017
# - Dimitrios Christidis <dimitrios.christidis@cern.ch>, 2018
# - Hannes Hansen <hannes.jakob.hansen@cern.ch>, 2019
#
# PY3K COMPATIBLE

import json
import os
import tempfile

import bz2file
import mock
import requests

try:
    # PY2
    from StringIO import StringIO
except ImportError:
    # PY3
    from io import StringIO

from datetime import datetime

from nose.tools import eq_
from nose.tools import ok_
from nose.tools import raises

from rucio.common import config
from rucio.common import dumper
from rucio.tests.common import make_temp_file
from rucio.tests.common import mock_open
from rucio.tests.mocks import gfal2


DATE_SECONDS = "2015-03-10 14:00:35"
DATE_TENTHS = "2015-03-10T14:00:35.5"
DATE_MILLISECONDS = "2015-03-10T14:00:35.5"
AGISDATA = [{
    'arprotocols': {
        'read_wan': [
            {
                'endpoint': 'srm://example.com',
                'path': '/atlasdatadisk/rucio/'
            }
        ]
    },
    'name': 'SOMEENDPOINT',
}]


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data


@raises(dumper.HTTPDownloadFailed)
def test_http_download_failed_exception_with_no_semantic_errors():
    raise dumper.HTTPDownloadFailed('some message', 500)


@raises(SystemExit)
def test_error_ends_the_program():
    dumper.error('message', 2)


def test_cacert_config_returns_a_string():
    ok_(isinstance(dumper.cacert_config(config, '.'), str))


@mock.patch('rucio.common.config.config_get')
def test_cacert_config_returns_false_if_no_cert_configured(mock_get):
    mock_get.return_value = ''
    eq_(dumper.cacert_config(config, '.'), False)


def test_smart_open_for_text_file():
    tmp = make_temp_file('/tmp', 'abcdef')
    ok_(hasattr(dumper.smart_open(tmp), 'read'))  # check if object is file - python2/3 compatibility
    os.unlink(tmp)


def test_smart_open_for_bz2_file():
    fd, path = tempfile.mkstemp()
    comp = bz2file.BZ2Compressor()
    with os.fdopen(fd, 'wb') as f:
        f.write(comp.compress('abcdef'.encode()))
        f.write(comp.flush())
    ok_(not isinstance(dumper.smart_open(path), bz2file.BZ2File))
    os.unlink(path)


def test_temp_file_with_final_name_creates_a_tmp_file_and_then_removes_it():
    final_name = tempfile.mktemp()
    with dumper.temp_file('/tmp', final_name) as (_, tmp_path):
        tmp_path = os.path.join('/tmp', tmp_path)
        ok_(os.path.exists(tmp_path), tmp_path)
        ok_(not os.path.exists(final_name), tmp_path)

    ok_(os.path.exists(final_name), final_name)
    ok_(not os.path.exists(tmp_path), tmp_path)
    os.unlink(final_name)


def test_temp_file_with_final_name_creates_a_tmp_file_and_keeps_it():
    with dumper.temp_file('/tmp') as (_, tmp_path):
        tmp_path = os.path.join('/tmp', tmp_path)
        ok_(os.path.exists(tmp_path), tmp_path)

    ok_(os.path.exists(tmp_path), tmp_path)
    os.unlink(tmp_path)


def test_temp_file_cleanup_on_exception():
    try:
        with dumper.temp_file('/tmp') as (_, tmp_path):
            tmp_path = os.path.join('/tmp', tmp_path)
            raise Exception
    except:
        pass
    finally:
        ok_(not os.path.exists(tmp_path), tmp_path)


def test_temp_file_cleanup_on_exception_with_final_name():
    final_name = tempfile.mktemp()
    try:
        with dumper.temp_file('/tmp', final_name) as (_, tmp_path):
            tmp_path = os.path.join('/tmp', tmp_path)
            raise Exception
    except:
        pass
    finally:
        ok_(not os.path.exists(tmp_path), tmp_path)
        ok_(not os.path.exists(final_name), final_name)


def test_to_date_format():
    ok_(isinstance(dumper.to_datetime(DATE_SECONDS), datetime))
    ok_(isinstance(dumper.to_datetime(DATE_TENTHS), datetime))
    ok_(isinstance(dumper.to_datetime(DATE_MILLISECONDS), datetime))


@mock.patch('requests.get')
def test_agis_endpoints_data_parses_proper_json(mock_get):
    mock_get.return_value = MockResponse(AGISDATA, 200)
    eq_(dumper.agis_endpoints_data(cache=False), AGISDATA)


@mock.patch('rucio.common.dumper.agis_endpoints_data')
def test_ddmendpoint_url_builds_url_from_agis_records(mock_get):
    mock_get.return_value = AGISDATA
    eq_(dumper.ddmendpoint_url('SOMEENDPOINT'), 'srm://example.com/atlasdatadisk/')


@mock.patch('rucio.common.dumper.agis_endpoints_data')
@raises(StopIteration)
def test_ddmendpoint_url_fails_on_unexistent_entry(mock_get):
    mock_get.return_value = []
    dumper.ddmendpoint_url('SOMEENDPOINT')


@mock.patch('requests.get')
def test_http_download_to_file_without_session_uses_requests_get(mock_get):
    response = requests.Response()
    response.status_code = 200
    response.iter_content = lambda _: ['content']
    mock_get.return_value = response
    stringio = StringIO()

    dumper.http_download_to_file('http://example.com', stringio)

    stringio.seek(0)
    eq_(stringio.read(), 'content')


def test_http_download_to_file_with_session():
    response = requests.Response()
    response.status_code = 200
    response.iter_content = lambda _: ['content']

    stringio = StringIO()
    session = requests.Session()
    session.get = lambda _: response

    dumper.http_download_to_file('http://example.com', stringio, session)
    stringio.seek(0)
    eq_(stringio.read(), 'content')


@raises(dumper.HTTPDownloadFailed)
def test_http_download_to_file_throws_exception_on_error():
    response = requests.Response()
    response.status_code = 404
    response.iter_content = lambda _: ['content']

    stringio = StringIO()
    session = requests.Session()
    session.get = lambda _: response

    dumper.http_download_to_file('http://example.com', stringio, session)


@mock.patch('requests.get')
def test_http_download_creates_file_with_content(mock_get):
    response = requests.Response()
    response.status_code = 200
    response.iter_content = lambda _: ['abc']
    stringio = StringIO()
    mock_get.return_value = response

    with mock_open(dumper, stringio):
        dumper.http_download('http://example.com', 'filename')

    stringio.seek(0)
    eq_(stringio.read(), 'abc')


def test_gfal_download_to_file():
    gfal_file = StringIO()
    local_file = StringIO()
    gfal_file.write('content')
    gfal_file.seek(0)

    with gfal2.mocked_gfal2(dumper, files={'srm://example.com/file': gfal_file}):
        dumper.gfal_download_to_file('srm://example.com/file', local_file)

    local_file.seek(0)
    eq_(local_file.read(), 'content')


def test_gfal_download_creates_file_with_content():
    gfal_file = StringIO()
    local_file = StringIO()
    gfal_file.write('content')
    gfal_file.seek(0)

    with gfal2.mocked_gfal2(dumper, files={'srm://example.com/file': gfal_file}):
        with mock_open(dumper, local_file):
            dumper.gfal_download('srm://example.com/file', 'filename')

    local_file.seek(0)
    eq_(local_file.read(), 'content')
