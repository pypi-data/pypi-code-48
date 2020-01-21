import pytest

from koconf.task import BashManager, CronManager

command = ': THIS IS NOP COMMAND'


class TestCronManager():
    @classmethod
    def setup_class(cls):
        cls.__state = cls.check_task()

    @classmethod
    def teardown_class(cls):
        if cls.__state:
            cls.set_task()
        else:
            cls.unset_task()

    @staticmethod
    def set_task():
        with CronManager() as cron:
            cron.set_reboot_task(command)

    @staticmethod
    def unset_task():
        with CronManager() as cron:
            cron.unset_reboot_task(command)

    @staticmethod
    def check_task():
        with CronManager() as cron:
            return cron.check_reboot_task(command)

    @pytest.mark.parametrize(
        'methods, expect',
        [
            (['set_task', 'set_task'], True),
            (['unset_task', 'set_task'], True),
            (['set_task', 'unset_task'], False),
            (['unset_task', 'unset_task'], False),
        ],
    )
    def test_cron(self, methods, expect):
        for method in methods:
            getattr(self, method)()

        assert self.check_task() == expect


class TestBashManager():
    @classmethod
    def setup_class(cls):
        cls.__state = cls.check_task()

    @classmethod
    def teardown_class(cls):
        if cls.__state:
            cls.set_task()
        else:
            cls.unset_task()

    @staticmethod
    def set_task():
        with BashManager() as bash:
            bash.set_terminal_task(command)

    @staticmethod
    def unset_task():
        with BashManager() as bash:
            bash.unset_terminal_task(command)

    @staticmethod
    def check_task():
        with BashManager() as bash:
            return bash.check_terminal_task(command)

    @pytest.mark.parametrize(
        'methods, expected',
        [
            (['set_task', 'set_task'], True),
            (['unset_task', 'set_task'], True),
            (['set_task', 'unset_task'], False),
            (['unset_task', 'unset_task'], False),
        ],
    )
    def test_bash(self, methods, expected):
        for method in methods:
            getattr(self, method)()

        assert self.check_task() == expected
