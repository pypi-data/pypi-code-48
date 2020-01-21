import koconf.common as common
import pytest

from datetime import datetime as dt


def test_now(mocker):
    year, month, day, hour, minute = 2020, 1, 1, 11, 50

    mock = mocker.patch('koconf.common.dt')
    mock.now.return_value = dt(year, month, day, hour, minute)

    assert common.now() == '%02d-%02d-%02d %02d:%02d' % (year, month, day, hour, minute)


@pytest.mark.parametrize(
    'before, after, diff',
    [
        ('2020-01-01 11:50', '2020-01-01 12:30', '40 minutes'),
        ('2020-01-01 11:50', '2020-01-01 13:40', '1 hour and 50 minutes'),
        ('2020-01-01 11:50', '2020-01-02 12:50', '1 day and 1 hour'),
        ('2020-01-01 11:50', '2020-01-11 12:55', '1 week, 3 days and 1 hour'),
    ],
)
def test_difftime(before, after, diff):
    assert common.difftime(before, after) == diff


def test_request(mocker):
    response = mocker.Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [
        {'NOT USED': 'JSON OBJECT'},
    ]

    mock = mocker.patch('koconf.common.requests')
    mock.get.return_value = response

    assert common.request() == response.json()
