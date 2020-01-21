import pytest

from click.testing import CliRunner
from koconf.cli import _show, _refresh, _remind, entry_command
from koconf.db import DataBaseManager
from koconf.task import BashManager, CronManager


@pytest.fixture(scope='session')
def runner():
    yield CliRunner()


def test_show_with_no_option(mocker, runner):
    mock = mocker.patch.object(DataBaseManager, 'show')

    runner.invoke(_show)

    mock.assert_called_once()


@pytest.mark.parametrize(
    'method, option',
    [
        ('show_by_applicable', '--applicable'),
    ],
)
def test_show_with_flag(mocker, runner, method, option):
    mock = mocker.patch.object(DataBaseManager, method)

    runner.invoke(_show, [option])

    mock.assert_called_once()


@pytest.mark.parametrize(
    'method, option',
    [
        ('show_by_id', '--id'),
        ('show_by_id', '-i'),
        ('show_by_title', '--title'),
        ('show_by_title', '-t'),
        ('show_by_city', '--city'),
        ('show_by_city', '-c'),
        ('show_by_tag', '--tag'),
        ('show_by_tag', '-g'),
    ],
)
def test_show_with_single_param(mocker, runner, method, option):
    param = 'NOT_USED_STRING'

    mock = mocker.patch.object(DataBaseManager, method)

    runner.invoke(_show, [option, param])

    mock.assert_called_once_with(param)


@pytest.mark.parametrize(
    'method, option',
    [
        ('show_by_applies', '--apply'),
        ('show_by_applies', '-a'),
        ('show_by_events', '--event'),
        ('show_by_events', '-e'),
    ],
)
def test_show_with_multiple_param(mocker, runner, method, option):
    params = ('NOT_USED', 'MULTIPLE_STRING')

    mock = mocker.patch.object(DataBaseManager, method)

    args = []
    for param in params:
        args.append(option)
        args.append(param)
    runner.invoke(_show, args)

    mock.assert_called_once_with(params)


def test_refresh(mocker, runner):
    method_orders = ['refresh', 'expire']

    mock, call = mocker.Mock(), mocker.call
    for method in method_orders:
        mock.attach_mock(mocker.patch.object(DataBaseManager, method), method)

    runner.invoke(_refresh)

    assert mock.mock_calls == [call.refresh(), call.expire()]


@pytest.mark.parametrize(
    'option',
    [
        ('--only-expired'),
        ('-e'),
    ],
)
def test_refresh_only_expired(mocker, runner, option):
    method_orders = ['expire']

    mock, call = mocker.Mock(), mocker.call
    for method in method_orders:
        mock.attach_mock(mocker.patch.object(DataBaseManager, method), method)

    runner.invoke(_refresh, [option])

    assert mock.mock_calls == [call.expire()]


@pytest.mark.parametrize(
    'option',
    [
        ('--with-clean'),
        ('-c'),
    ],
)
def test_refresh_with_clean(mocker, runner, option):
    method_orders = ['clean', 'refresh', 'expire']

    mock, call = mocker.Mock(), mocker.call
    for method in method_orders:
        mock.attach_mock(mocker.patch.object(DataBaseManager, method), method)

    runner.invoke(_refresh, [option])

    assert mock.mock_calls == [call.clean(), call.refresh(), call.expire()]


@pytest.mark.parametrize(
    'method, option',
    [
        ('set_reboot_task', '--set-auto'),
        ('set_reboot_task', '-s'),
        ('unset_reboot_task', '--unset-auto'),
        ('unset_reboot_task', '-u'),
    ],
)
def test_refresh_task(mocker, runner, method, option):
    sub_command = 'refresh'

    mock = mocker.patch.object(CronManager, method)
    runner.invoke(_refresh, [option])
    mock.assert_called_once_with(command='%s %s' % (entry_command, sub_command))


def test_remind(mocker, runner):
    mock = mocker.patch.object(DataBaseManager, 'remind')
    runner.invoke(_remind)
    mock.assert_called_once()

@pytest.mark.parametrize(
    'method, option',
    [
        ('add_remind', '--add'),
        ('add_remind', '-a'),
        ('remove_remind', '--remove'),
        ('remove_remind', '-r'),
    ],
)
def test_remind_modification(mocker, runner, method, option):
    param = 'NOT_ID_FORMAT'

    mock = mocker.patch.object(DataBaseManager, method)
    runner.invoke(_remind, [option, param])
    mock.assert_called_once_with(param)


@pytest.mark.parametrize(
    'method, option',
    [
        ('set_terminal_task', '--set-background'),
        ('set_terminal_task', '-s'),
        ('unset_terminal_task', '--unset-background'),
        ('unset_terminal_task', '-u'),
    ],
)
def test_remind_task(mocker, runner, method, option):
    sub_command = 'remind'

    mock = mocker.patch.object(BashManager, method)
    runner.invoke(_remind, [option])
    mock.assert_called_once_with(command='%s %s' % (entry_command, sub_command))
