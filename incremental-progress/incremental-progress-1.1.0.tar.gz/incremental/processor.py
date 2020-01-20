import logging
import os
import subprocess
import time
from configparser import ConfigParser

from watchgod import watch

from incremental.handler import ProgressFileHandler as pfh

LOGGER = logging.getLogger("default")


class ProgressWatcher:
    """
    ProgressWatcher:
    - start will begin watching for changes in the files specified in
      configurations
    - execute_test_runner provides the ability to run tests without having to
      change a file.
    """

    def __init__(self, config_file="./config.ini"):
        LOGGER.debug("Loading watches")
        config = ConfigParser()
        # Load the configuration file
        self.config = config.read(config_file)

        # TODO: I hate this so much....
        self.monitored_files = config.get("PROGRESS", "monitored_files")
        self.monitored_path = config.get("PROGRESS", "monitored_path")
        self.pytest_to_markdown = config.getboolean(
            "PROGRESS", "pytest_to_markdown")
        self.storage_path = config.get("PROGRESS", "storage_path")
        self.test_runner = config.get("PROGRESS", "test_runner")
        self.monitored_extensions = config.get(
            "PROGRESS", "monitored_extensions")

    def _mointor(self, changes):
        """
        For each modified file
        - check to see if it is a MONITORED_FILES
        - If monitored, copy current version
        - If monitored, run TEST_RUNNER
        """
        LOGGER.debug(changes)

        for _event, file_path in changes:
            event_time = time.strftime("%a_%d-%b-%Y_%H:%M:%S")
            file_copy_path = f"{self.storage_path}/{event_time}"

            if pfh.should_operate(
                file_path, self.monitored_files, self.monitored_extensions
            ):
                pfh.copy_source(file_path, file_copy_path)
                self.execute_test_runner(file_copy_path)

    def execute_test_runner(self, file_copy_path):
        """
        Execute tests
        If using pytest markdown converter, run with additional options
        If not using pytest md, write results to file
        """

        runner_command = self.test_runner

        if self.pytest_to_markdown:
            LOGGER.debug("Running with pytest-md")
            runner_command += f" --md {file_copy_path}.md"
            LOGGER.debug(runner_command)
            subprocess.check_call(runner_command.split(" "))

        else:

            runner_result = subprocess.Popen(
                self.test_runner.split(" "),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, stderr = runner_result.communicate()
            LOGGER.debug(stdout)
            LOGGER.error(stderr)

            with open(f"{file_copy_path}.test", "w+") as test_result:
                test_result.write(str(stdout))
                test_result.write(str(stderr))

    def start(self):
        """
        Starts watcher with current configuration options
        - Creates storage_path if it does not exist
        - Starts watching for file changes in configured path
        """

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        for changes in watch(self.monitored_path):
            self._mointor(changes)
