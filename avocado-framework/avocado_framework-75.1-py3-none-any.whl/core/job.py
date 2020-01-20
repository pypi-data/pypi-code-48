# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2013-2015
# Authors: Lucas Meneghel Rodrigues <lmr@redhat.com>
#          Ruda Moura <rmoura@redhat.com>

"""
Job module - describes a sequence of automated test operations.
"""

import argparse
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import traceback

from . import data_dir
from . import dispatcher
from . import exceptions
from . import exit_codes
from . import job_id
from . import jobdata
from . import loader
from . import nrunner
from . import output
from . import resolver
from . import result
from . import tags
from . import test
from . import varianter
from . import version
from ..utils import astring
from ..utils import data_structures
from ..utils import path
from ..utils import process
from ..utils import stacktrace
from .output import LOG_JOB
from .output import LOG_UI
from .output import STD_OUTPUT
from .settings import settings
from .tags import filter_test_tags_runnable


_NEW_ISSUE_LINK = 'https://github.com/avocado-framework/avocado/issues/new'


def resolutions_to_tasks(resolutions, config):
    """
    Transforms resolver resolutions into tasks

    A resolver resolution
    (:class:`avocado.core.resolver.ReferenceResolution`) contains
    information about the resolution process (if it was successful
    or not) and in case of successful resolutions a list of
    resolutions.  It's expected that the resolution are
    :class:`avocado.core.nrunner.Runnable`.

    This method transforms those runnables into Tasks
    (:class:`avocado.core.nrunner.Task`), which will include an
    unique sequential identification and a status reporting URI.
    It also performs tag based filtering on the runnables for
    possibly excluding some of the Runnables.

    :param resolutions: possible multiple resolutions for multiple
                        references
    :type resolutions: list of :class:`avocado.core.resolver.ReferenceResolution`
    :param config: job configuration
    :type config: dict
    :returns: the resolutions converted to tasks
    :rtype: list of :class:`avocado.core.nrunner.Task`
    """

    tasks = []
    index = 0
    resolutions = [res for res in resolutions if
                   res.result == resolver.ReferenceResolutionResult.SUCCESS]
    no_digits = len(str(len(resolutions)))
    for resolution in resolutions:
        name = resolution.reference
        for runnable in resolution.resolutions:
            filter_by_tags = config.get('filter_by_tags')
            if filter_by_tags:
                if not filter_test_tags_runnable(
                        runnable,
                        filter_by_tags,
                        config.get('filter_by_tags_include_empty'),
                        config.get('filter_by_tags_include_empty_key')):
                    continue
            if runnable.uri:
                name = runnable.uri
            identifier = str(test.TestID(index + 1, name, None, no_digits))
            tasks.append(nrunner.Task(identifier, runnable,
                                      [config.get('status_server')]))
            index += 1
    return tasks


class Job:

    """
    A Job is a set of operations performed on a test machine.

    Most of the time, we are interested in simply running tests,
    along with setup operations and event recording.
    """

    LOG_MAP = {'info': logging.INFO,
               'debug': logging.DEBUG,
               'warning': logging.WARNING,
               'error': logging.ERROR,
               'critical': logging.CRITICAL}

    def __init__(self, config=None):
        """
        Creates an instance of Job class.

        :param config: the job configuration, usually set by command
                       line options and argument parsing
        :type config: dict
        """
        self.config = config or {}
        self.log = LOG_UI
        self.loglevel = self.LOG_MAP.get(settings.get_value('job.output',
                                                            'loglevel',
                                                            default='debug'),
                                         logging.DEBUG)
        self.__logging_handlers = {}
        self.standalone = self.config.get('standalone', False)
        if self.config.get('dry_run', False):  # Modify args for dry-run
            unique_id = self.config.get('unique_job_id', None)
            if unique_id is None:
                self.config['unique_job_id'] = '0' * 40
            self.config['sysinfo'] = False

        unique_id = self.config.get('unique_job_id', None)
        if unique_id is None:
            unique_id = job_id.create_unique_job_id()
        self.unique_id = unique_id
        #: The log directory for this job, also known as the job results
        #: directory.  If it's set to None, it means that the job results
        #: directory has not yet been created.
        self.logdir = None
        self.logfile = None
        self.tmpdir = None
        self.__keep_tmpdir = True
        self.status = "RUNNING"
        self.result = None
        self.interrupted_reason = None
        self.sysinfo = None
        self.timeout = self.config.get('job_timeout', 0)
        #: The time at which the job has started or `-1` if it has not been
        #: started by means of the `run()` method.
        self.time_start = -1
        #: The time at which the job has finished or `-1` if it has not been
        #: started by means of the `run()` method.
        self.time_end = -1
        #: The total amount of time the job took from start to finish,
        #: or `-1` if it has not been started by means of the `run()` method
        self.time_elapsed = -1
        self.funcatexit = data_structures.CallbackRegister("JobExit %s"
                                                           % self.unique_id,
                                                           LOG_JOB)
        self._stdout_stderr = None
        self.replay_sourcejob = self.config.get('replay_sourcejob', None)
        self.exitcode = exit_codes.AVOCADO_ALL_OK
        #: The list of discovered/resolved tests that will be attempted to
        #: be run by this job.  If set to None, it means that test resolution
        #: has not been attempted.  If set to an empty list, it means that no
        #: test was found during resolution.
        self.test_suite = None
        self.test_runner = None

        #: Placeholder for test parameters (related to --test-parameters command
        #: line option).  They're kept in the job because they will be prepared
        #: only once, since they are read only and will be shared across all
        #: tests of a job.
        self.test_parameters = None
        if "test_parameters" in self.config:
            self.test_parameters = {}
            for parameter_name, parameter_value in self.config.get('test_parameters'):
                self.test_parameters[parameter_name] = parameter_value

        # The result events dispatcher is shared with the test runner.
        # Because of our goal to support using the phases of a job
        # freely, let's get the result events dispatcher ready early.
        # A future optimization may load it on demand.
        self.result_events_dispatcher = dispatcher.ResultEventsDispatcher(self.config)
        output.log_plugin_failures(self.result_events_dispatcher.load_failures)

    def __enter__(self):
        self.setup()
        if not output.STD_OUTPUT.configured:
            output.reconfigure(self.config)
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.cleanup()

    def setup(self):
        """
        Setup the temporary job handlers (dirs, global setting, ...)
        """
        assert self.tmpdir is None, "Job.setup() already called"
        if self.config.get("dry_run", False):  # Create the dry-run dirs
            if self.config.get("base_logdir", None) is None:
                self.config['base_logdir'] = tempfile.mkdtemp(prefix="avocado-dry-run-")
        self._setup_job_results()
        self.result = result.Result(self.unique_id, self.logfile)
        self.__start_job_logging()
        self._setup_job_category()
        # Use "logdir" in case "keep_tmp" is enabled
        if self.config.get("keep_tmp", None) == "on":
            base_tmpdir = self.logdir
        else:
            base_tmpdir = data_dir.get_tmp_dir()
            self.__keep_tmpdir = False
        self.tmpdir = tempfile.mkdtemp(prefix="avocado_job_",
                                       dir=base_tmpdir)

    def _setup_job_results(self):
        """
        Prepares a job result directory, also known as logdir, for this job
        """
        base_logdir = self.config.get('base_logdir', None)
        if self.standalone:
            if base_logdir is not None:
                base_logdir = os.path.abspath(base_logdir)
                self.logdir = data_dir.create_job_logs_dir(base_dir=base_logdir,
                                                           unique_id=self.unique_id)
            else:
                self.logdir = tempfile.mkdtemp(prefix='avocado_' + __name__)
        else:
            if base_logdir is None:
                self.logdir = data_dir.create_job_logs_dir(unique_id=self.unique_id)
            else:
                base_logdir = os.path.abspath(base_logdir)
                self.logdir = data_dir.create_job_logs_dir(base_dir=base_logdir,
                                                           unique_id=self.unique_id)
        if not (self.standalone or self.config.get("dry_run", False)):
            self._update_latest_link()
        self.logfile = os.path.join(self.logdir, "job.log")
        idfile = os.path.join(self.logdir, "id")
        with open(idfile, 'w') as id_file_obj:
            id_file_obj.write("%s\n" % self.unique_id)
            id_file_obj.flush()
            os.fsync(id_file_obj)

    def _setup_job_category(self):
        """
        This has to be called after self.logdir has been defined

        It attempts to create a directory one level up from the job results,
        with the given category name.  Then, a symbolic link is created to
        this job results directory.

        This should allow a user to look at a single directory for all
        jobs of a given category.
        """
        category = self.config.get('job_category', None)
        if category is None:
            return

        if category != astring.string_to_safe_path(category):
            msg = ("Unable to set category in job results: name is not "
                   "filesystem safe: %s" % category)
            LOG_UI.warning(msg)
            LOG_JOB.warning(msg)
            return

        # we could also get "base_logdir" from args, but I believe this is
        # the best choice because it reduces the dependency surface (depends
        # only on self.logdir)
        category_path = os.path.join(os.path.dirname(self.logdir),
                                     category)
        try:
            os.mkdir(category_path)
        except FileExistsError:
            pass

        try:
            os.symlink(os.path.relpath(self.logdir, category_path),
                       os.path.join(category_path, os.path.basename(self.logdir)))
        except NotImplementedError:
            msg = "Unable to link this job to category %s" % category
            LOG_UI.warning(msg)
            LOG_JOB.warning(msg)
        except OSError:
            msg = "Permission denied to link this job to category %s" % category
            LOG_UI.warning(msg)
            LOG_JOB.warning(msg)

    def __start_job_logging(self):
        # Enable test logger
        fmt = ('%(asctime)s %(module)-16.16s L%(lineno)-.4d %('
               'levelname)-5.5s| %(message)s')
        test_handler = output.add_log_handler(LOG_JOB,
                                              logging.FileHandler,
                                              self.logfile, self.loglevel, fmt)
        root_logger = logging.getLogger()
        root_logger.addHandler(test_handler)
        root_logger.setLevel(self.loglevel)
        self.__logging_handlers[test_handler] = [LOG_JOB.name, ""]
        # Add --store-logging-streams
        fmt = '%(asctime)s %(levelname)-5.5s| %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt='%H:%M:%S')
        for name in self.config.get("store_logging_stream", []):
            name = re.split(r'(?<!\\):', name, maxsplit=1)
            if len(name) == 1:
                name = name[0]
                level = logging.INFO
            else:
                level = (int(name[1]) if name[1].isdigit()
                         else logging.getLevelName(name[1].upper()))
                name = name[0]
            try:
                logname = "log" if name == "" else name
                logfile = os.path.join(self.logdir, logname + "." +
                                       logging.getLevelName(level))
                handler = output.add_log_handler(name, logging.FileHandler,
                                                 logfile, level, formatter)
            except ValueError as details:
                self.log.error("Failed to set log for --store-logging-stream "
                               "%s:%s: %s.", name, level, details)
            else:
                self.__logging_handlers[handler] = [name]
        # Enable console loggers
        enabled_logs = self.config.get("show", [])
        if ('test' in enabled_logs and
                'early' not in enabled_logs):
            self._stdout_stderr = sys.stdout, sys.stderr
            # Enable std{out,err} but redirect booth to stderr
            sys.stdout = STD_OUTPUT.stdout
            sys.stderr = STD_OUTPUT.stdout
            test_handler = output.add_log_handler(LOG_JOB,
                                                  logging.StreamHandler,
                                                  STD_OUTPUT.stdout,
                                                  logging.DEBUG,
                                                  fmt="%(message)s")
            root_logger.addHandler(test_handler)
            self.__logging_handlers[test_handler] = [LOG_JOB.name, ""]

    def __stop_job_logging(self):
        if self._stdout_stderr:
            sys.stdout, sys.stderr = self._stdout_stderr
        for handler, loggers in self.__logging_handlers.items():
            for logger in loggers:
                logging.getLogger(logger).removeHandler(handler)

    def _update_latest_link(self):
        """
        Update the latest job result symbolic link [avocado-logs-dir]/latest.
        """
        def soft_abort(msg):
            """ Only log the problem """
            LOG_JOB.warning("Unable to update the latest link: {}", msg)
        basedir = os.path.dirname(self.logdir)
        basename = os.path.basename(self.logdir)
        proc_latest = os.path.join(basedir, "latest.%s" % os.getpid())
        latest = os.path.join(basedir, "latest")
        if os.path.exists(latest) and not os.path.islink(latest):
            soft_abort('"%s" already exists and is not a symlink' % latest)
            return

        if os.path.exists(proc_latest):
            try:
                os.unlink(proc_latest)
            except OSError as details:
                soft_abort("Unable to remove %s: %s" % (proc_latest, details))
                return

        try:
            os.symlink(basename, proc_latest)
            os.rename(proc_latest, latest)
        except OSError as details:
            soft_abort("Unable to create create latest symlink: %s" % details)
            return
        finally:
            if os.path.exists(proc_latest):
                os.unlink(proc_latest)

    def _make_test_suite_loader(self, references):
        """
        Prepares a test suite to be used for running tests

        :param references: List of tests references to be resolved and
                           transformed into test factories
        :type references: list of str
        :returns: a test suite (a list of test factories)
        """
        loader.loader.load_plugins(self.config)
        try:
            force = self.config.get('ignore_missing_references', 'off')
            suite = loader.loader.discover(references, force=force)
            if self.config.get('filter_by_tags', False):
                suite = tags.filter_test_tags(
                    suite,
                    self.config.get('filter_by_tags'),
                    self.config.get('filter_by_tags_include_empty'),
                    self.config.get('filter_by_tags_include_empty_key'))
        except loader.LoaderUnhandledReferenceError as details:
            raise exceptions.OptionValidationError(details)
        except KeyboardInterrupt:
            raise exceptions.JobError('Command interrupted by user...')

        if not self.config.get("dry_run", False):
            return suite
        for i in range(len(suite)):
            suite[i] = [test.DryRunTest, suite[i][1]]
        return suite

    def _make_test_suite_resolver(self, references):
        resolutions = resolver.resolve(references)
        return resolutions_to_tasks(resolutions, self.config)

    def _log_job_id(self):
        LOG_JOB.info('Job ID: %s', self.unique_id)
        if self.replay_sourcejob is not None:
            LOG_JOB.info('Replay of Job ID: %s', self.replay_sourcejob)
        LOG_JOB.info('')

    @staticmethod
    def _log_cmdline():
        cmdline = " ".join(sys.argv)
        LOG_JOB.info("Command line: %s", cmdline)
        LOG_JOB.info('')

    @staticmethod
    def _get_avocado_git_version():
        # if running from git sources, there will be a ".git" directory
        # 3 levels up
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        git_dir = os.path.join(base_dir, '.git')
        if not os.path.isdir(git_dir):
            return
        if not os.path.exists(os.path.join(base_dir, 'python-avocado.spec')):
            return

        try:
            git = path.find_command('git')
        except path.CmdNotFoundError:
            return

        olddir = os.getcwd()
        try:
            os.chdir(os.path.abspath(base_dir))
            cmd = "%s show --summary --pretty='%%H'" % git
            res = process.run(cmd, ignore_status=True, verbose=False)
            if res.exit_status == 0:
                top_commit = res.stdout_text.splitlines()[0][:8]
                return " (GIT commit %s)" % top_commit
        finally:
            os.chdir(olddir)

    def _log_avocado_version(self):
        version_log = version.VERSION
        git_version = self._get_avocado_git_version()
        if git_version is not None:
            version_log += git_version
        LOG_JOB.info('Avocado version: %s', version_log)
        LOG_JOB.info('')

    @staticmethod
    def _log_avocado_config():
        LOG_JOB.info('Config files read (in order):')
        for cfg_path in settings.config_paths:
            LOG_JOB.info(cfg_path)
        LOG_JOB.info('')

        LOG_JOB.info('Avocado config:')
        header = ('Section.Key', 'Value')
        config_matrix = []
        for section in settings.config.sections():
            for value in settings.config.items(section):
                config_key = ".".join((section, value[0]))
                config_matrix.append([config_key, value[1]])

        for line in astring.iter_tabular_output(config_matrix, header):
            LOG_JOB.info(line)
        LOG_JOB.info('')

    def _log_avocado_datadir(self):
        LOG_JOB.info('Avocado Data Directories:')
        LOG_JOB.info('')
        LOG_JOB.info('base     %s', data_dir.get_base_dir())
        LOG_JOB.info('tests    %s', data_dir.get_test_dir())
        LOG_JOB.info('data     %s', data_dir.get_data_dir())
        LOG_JOB.info('logs     %s', self.logdir)
        LOG_JOB.info('')

    @staticmethod
    def _log_variants(variants):
        lines = variants.to_str(summary=1, variants=1, use_utf8=False)
        for line in lines.splitlines():
            LOG_JOB.info(line)

    def _log_tmp_dir(self):
        LOG_JOB.info('Temporary dir: %s', self.tmpdir)
        LOG_JOB.info('')

    def _log_job_debug_info(self, variants):
        """
        Log relevant debug information to the job log.
        """
        self._log_cmdline()
        self._log_avocado_version()
        self._log_avocado_config()
        self._log_avocado_datadir()
        self._log_variants(variants)
        self._log_tmp_dir()
        self._log_job_id()

    def create_test_suite(self):
        """
        Creates the test suite for this Job

        This is a public Job API as part of the documented Job phases
        """
        refs = self.config.get('references', [])
        runner_name = self.config.get('test_runner', 'runner')
        try:
            if runner_name == 'nrunner':
                self.test_suite = self._make_test_suite_resolver(refs)
            else:
                self.test_suite = self._make_test_suite_loader(refs)
            self.result.tests_total = len(self.test_suite)
        except loader.LoaderError as details:
            stacktrace.log_exc_info(sys.exc_info(), LOG_UI.getChild("debug"))
            raise exceptions.OptionValidationError(details)

        if not self.test_suite:
            if refs:
                e_msg = ("No tests found for given test references, try "
                         "'avocado list -V %s' for details") % " ".join(refs)
            else:
                e_msg = ("No test references provided nor any other arguments "
                         "resolved into tests. Please double check the "
                         "executed command.")
            raise exceptions.OptionValidationError(e_msg)

    def pre_tests(self):
        """
        Run the pre tests execution hooks

        By default this runs the plugins that implement the
        :class:`avocado.core.plugin_interfaces.JobPreTests` interface.
        """
        self.result_events_dispatcher.map_method('pre_tests', self)

    def run_tests(self):
        """
        The actual test execution phase
        """
        variant = self.config.get("avocado_variants", None)
        if variant is None:
            variant = varianter.Varianter()
        if not variant.is_parsed():   # Varianter not yet parsed, apply args
            try:
                variant.parse(self.config)
            except (IOError, ValueError) as details:
                raise exceptions.OptionValidationError("Unable to parse "
                                                       "variant: %s" % details)

        runner_name = self.config.get('test_runner', 'runner')
        try:
            runner_extension = dispatcher.RunnerDispatcher()[runner_name]
        except KeyError:
            return
        self.test_runner = runner_extension.obj

        self._log_job_debug_info(variant)
        jobdata.record(self.config, self.logdir, variant,
                       self.config.get('references'), sys.argv)
        replay_map = self.config.get('replay_map', None)
        execution_order = self.config.get('execution_order', None)
        summary = self.test_runner.run_suite(self,
                                             self.result,
                                             self.test_suite,
                                             variant,
                                             self.timeout,
                                             replay_map,
                                             execution_order)
        # If it's all good so far, set job status to 'PASS'
        if self.status == 'RUNNING':
            self.status = 'PASS'
        LOG_JOB.info('Test results available in %s', self.logdir)

        if summary is None:
            self.exitcode |= exit_codes.AVOCADO_JOB_FAIL
            return self.exitcode

        if 'INTERRUPTED' in summary:
            self.exitcode |= exit_codes.AVOCADO_JOB_INTERRUPTED
        if 'FAIL' in summary:
            self.exitcode |= exit_codes.AVOCADO_TESTS_FAIL

        return self.exitcode

    def post_tests(self):
        """
        Run the post tests execution hooks

        By default this runs the plugins that implement the
        :class:`avocado.core.plugin_interfaces.JobPostTests` interface.
        """
        self.result_events_dispatcher.map_method('post_tests', self)

    def run(self):
        """
        Runs all job phases, returning the test execution results.

        This method is supposed to be the simplified interface for
        jobs, that is, they run all phases of a job.

        :return: Integer with overall job status. See
                 :mod:`avocado.core.exit_codes` for more information.
        """
        assert self.tmpdir is not None, "Job.setup() not called"
        if self.time_start == -1:
            self.time_start = time.time()
        try:
            self.create_test_suite()
            self.pre_tests()
            return self.run_tests()
        except exceptions.JobBaseException as details:
            self.status = details.status
            fail_class = details.__class__.__name__
            self.log.error('\nAvocado job failed: %s: %s', fail_class, details)
            self.exitcode |= exit_codes.AVOCADO_JOB_FAIL
            return self.exitcode
        except exceptions.OptionValidationError as details:
            self.log.error('\n%s', str(details))
            self.exitcode |= exit_codes.AVOCADO_JOB_FAIL
            return self.exitcode

        except Exception as details:  # pylint: disable=W0703
            self.status = "ERROR"
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_info = traceback.format_exception(exc_type, exc_value,
                                                 exc_traceback.tb_next)
            fail_class = details.__class__.__name__
            self.log.error('\nAvocado crashed: %s: %s', fail_class, details)
            for line in tb_info:
                self.log.debug(line)
            self.log.error("Please include the traceback info and command line"
                           " used on your bug report")
            self.log.error('Report bugs visiting %s', _NEW_ISSUE_LINK)
            self.exitcode |= exit_codes.AVOCADO_FAIL
            return self.exitcode
        finally:
            self.post_tests()
            if self.time_end == -1:
                self.time_end = time.time()
                self.time_elapsed = self.time_end - self.time_start

    def cleanup(self):
        """
        Cleanup the temporary job handlers (dirs, global setting, ...)
        """
        self.__stop_job_logging()
        if not self.__keep_tmpdir and os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
        cleanup_conditionals = (
            self.config.get("dry_run", False),
            not self.config.get("dry_run_no_cleanup", False)
        )
        if all(cleanup_conditionals):
            # Also clean up temp base directory created because of the dry-run
            base_logdir = self.config.get("base_logdir", None)
            if base_logdir is not None:
                try:
                    FileNotFoundError
                except NameError:
                    FileNotFoundError = OSError   # pylint: disable=W0622
                try:
                    shutil.rmtree(base_logdir)
                except FileNotFoundError:
                    pass


class TestProgram:

    """
    Convenience class to make avocado test modules executable.
    """

    def __init__(self):
        # Avoid fork loop/bomb when running a test via avocado.main() that
        # calls avocado.main() itself
        if os.environ.get('AVOCADO_STANDALONE_IN_MAIN', False):
            sys.stderr.write('AVOCADO_STANDALONE_IN_MAIN environment variable '
                             'found. This means that this code is being '
                             'called recursively. Exiting to avoid an infinite'
                             ' fork loop.\n')
            sys.exit(exit_codes.AVOCADO_FAIL)
        os.environ['AVOCADO_STANDALONE_IN_MAIN'] = 'True'

        self.prog_name = os.path.basename(sys.argv[0])
        output.add_log_handler("", output.ProgressStreamHandler,
                               fmt="%(message)s")
        self.parse_args(sys.argv[1:])
        self.config['references'] = [sys.argv[0]]
        self.run_tests()

    def parse_args(self, argv):
        self.parser = argparse.ArgumentParser(prog=self.prog_name)
        self.parser.add_argument('-r', '--remove-test-results',
                                 action='store_true', help="remove all test "
                                 "results files after test execution")
        self.parser.add_argument('-d', '--test-results-dir', dest='base_logdir',
                                 default=None, metavar='TEST_RESULTS_DIR',
                                 help="use an alternative test results "
                                 "directory")
        self.config = vars(self.parser.parse_args(argv))

    def run_tests(self):
        self.config['standalone'] = True
        self.config['show'] = ["test"]
        output.reconfigure(self.config)
        with Job(self.config) as self.job:
            exit_status = self.job.run()
            if self.config.get('remove_test_results') is True:
                shutil.rmtree(self.job.logdir)
        sys.exit(exit_status)

    def __del__(self):
        data_dir.clean_tmp_files()


main = TestProgram
