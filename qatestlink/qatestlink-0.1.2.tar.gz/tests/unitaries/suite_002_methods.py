# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""TODO: doc module"""


import logging
from unittest import TestCase
from unittest import skipIf
from qatestlink.core.exceptions.response_exception import ResponseException
from qatestlink.core.models.tl_models import (
    TBuild, TCase, TPlan, TPlatform, TProject, TSuite
)
from qatestlink.core.models.tl_reports import (
    RTCase, RTPlanTotals
)
from qatestlink.core.testlink_manager import TLManager
from qatestlink.core.utils import settings


SETTINGS = settings()
API_DEV_KEY = SETTINGS['dev_key']
SKIP = SETTINGS['tests']['skip']['methods']
SKIP_MESSAGE = SETTINGS['tests']['skip_message']
DATA = SETTINGS['tests']['data']


class TestMethods(object):
    """TODO: doc class"""

    @classmethod
    def setup_class(cls):
        """TODO: doc method"""
        cls.testlink_manager = TLManager()
        cls.tc = TestCase()

    def setup_method(self):
        """TODO: doc method"""
        self.tc.assertIsInstance(
            self.testlink_manager, TLManager)
        self.tc.assertIsInstance(
            self.testlink_manager.log, logging.Logger)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tprojects(self):
        """TODO: doc method"""
        tprojects = self.testlink_manager.api_tprojects(
            dev_key=API_DEV_KEY)
        self.tc.assertIsInstance(tprojects, list)
        self.tc.assertGreater(len(tprojects), 0)
        for tproject in tprojects:
            self.testlink_manager.log.debug(repr(tproject))
            self.tc.assertIsInstance(tproject, TProject)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tproject(self):
        """TODO: doc method"""
        tproject = self.testlink_manager.api_tproject(DATA['tproject_name'])
        self.tc.assertIsInstance(tproject, TProject)
        self.tc.assertEqual(tproject.name, DATA['tproject_name'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tproject_tplans(self):
        """TODO: doc method"""
        tplans = self.testlink_manager.api_tproject_tplans(DATA['tproject_id'])
        self.tc.assertIsInstance(tplans, list)
        self.tc.assertGreater(len(tplans), 0)
        for tplan in tplans:
            self.testlink_manager.log.debug(repr(tplan))
            self.tc.assertIsInstance(tplan, TPlan)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tproject_tsuites_first_level(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tproject_tsuites_first_level(
            DATA['tproject_id'])
        self.tc.assertIsInstance(tsuites, list)
        self.tc.assertGreater(len(tsuites), 0)
        for tsuite in tsuites:
            self.testlink_manager.log.debug(repr(tsuite))
            self.tc.assertIsInstance(tsuite, TSuite)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tplan(self):
        """TODO: doc method"""
        tplan = self.testlink_manager.api_tplan(
            DATA['tproject_name'], DATA['tplan_name'])
        self.tc.assertIsInstance(tplan, TPlan)
        self.tc.assertEqual(tplan.name, DATA['tplan_name'])
        self.tc.assertEqual(tplan.tproject_id, DATA['tproject_id'])

    @skipIf(True, SKIP_MESSAGE)
    def test_method_tplan_platforms(self):
        """TODO: doc method"""
        platforms = self.testlink_manager.api_tplan_platforms(
            DATA['tplan_id_platforms'])
        self.tc.assertIsInstance(platforms, list)
        self.tc.assertGreater(len(platforms), 0)
        for platform in platforms:
            self.testlink_manager.log.debug(repr(platform))
            self.tc.assertIsInstance(platform, TPlatform)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tplan_builds(self):
        """TODO: doc method"""
        builds = self.testlink_manager.api_tplan_builds(DATA['tplan_id'])
        self.tc.assertIsInstance(builds, list)
        self.tc.assertGreater(len(builds), 0)
        for build in builds:
            self.testlink_manager.log.debug(repr(build))
            self.tc.assertIsInstance(build, TBuild)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tplan_tsuites(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tplan_tsuites(DATA['tplan_id'])
        self.tc.assertIsInstance(tsuites, list)
        self.tc.assertGreater(len(tsuites), 0)
        for tsuite in tsuites:
            self.testlink_manager.log.debug(repr(tsuite))
            self.tc.assertIsInstance(tsuite, TSuite)

    @skipIf(True, SKIP_MESSAGE)
    def test_method_tplan_tcases(self):
        """TODO: doc method"""
        tcases = self.testlink_manager.api_tplan_tcases(DATA['tplan_id'])
        self.tc.assertIsInstance(tcases, list)
        self.tc.assertGreater(len(tcases), 0)
        for tcase in tcases:
            self.testlink_manager.log.debug(repr(tcase))
            self.tc.assertIsInstance(tcase, TCase)
            if tcase.id == DATA['tcase_id']:
                self.tc.assertEqual(
                    tcase.full_external_id,
                    DATA['tcase_full_external_id']
                )

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tplan_tbuild_latest(self):
        """TODO: doc method"""
        build = self.testlink_manager.api_tplan_build_latest(
            DATA['tplan_id'])
        self.tc.assertIsInstance(build, TBuild)
        self.tc.assertEqual(build.id, DATA['build_id_two'])
        self.tc.assertEqual(build.name, DATA['build_name_two'])

    @skipIf(True, "https://github.com/netzulo/qatestlink/issues/55")
    def test_method_tplan_totals(self):
        """TODO: doc method"""
        totals = self.testlink_manager.api_tplan_totals(
            DATA['tplan_id'])
        self.tc.assertIsInstance(totals, RTPlanTotals)
        self.tc.assertIsInstance(totals.by_tester, list)
        self.tc.assertIsInstance(totals.by_tester[0]['user_id'], int)
        self.tc.assertIsInstance(totals.by_tester[0]['report_types'], list)
        for by_tester_report_type in totals.by_tester[0]['report_types']:
            self.tc.assertIsInstance(by_tester_report_type['platform_id'], int)
            self.tc.assertIsInstance(by_tester_report_type['qty'], int)
            self.tc.assertIsInstance(by_tester_report_type['report_type'], str)
            self.tc.assertIn(
                by_tester_report_type['report_type'],
                ['p', 'n', 'b', 'f']
            )

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tsuite(self):
        """TODO: doc method"""
        tsuite = self.testlink_manager.api_tsuite(
            DATA['tsuite_id'])
        self.tc.assertIsInstance(tsuite, TSuite)
        self.tc.assertEqual(tsuite.name, DATA['tsuite_name'])

    @skipIf(True, SKIP_MESSAGE)
    def test_method_tsuite_tsuites(self):
        """TODO: doc method"""
        tsuites = self.testlink_manager.api_tsuite_tsuites(
            DATA['tsuite_id'])
        self.tc.assertIsInstance(tsuites, list)
        for tsuite in tsuites:
            self.tc.assertIsInstance(tsuite, TSuite)

    @skipIf(True, SKIP_MESSAGE)
    def test_method_tcase_byid(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase(
            tcase_id=DATA['tcase_id'])
        self.tc.assertIsInstance(tcase, TCase)
        self.tc.assertEqual(tcase.id, DATA['tcase_id'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tcase_byexternalid(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase(
            external_id=DATA['tcase_full_external_id'])
        self.tc.assertIsInstance(tcase, TCase)
        self.tc.assertEqual(
            tcase.external_id, DATA['tcase_full_external_id'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tcase_byname(self):
        """TODO: doc method"""
        tcase = self.testlink_manager.api_tcase_by_name(
            DATA['tcase_name'])
        self.tc.assertIsInstance(tcase, TCase)
        self.tc.assertEqual(
            tcase.name, DATA['tcase_name'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_tcase_report(self):
        """TODO: doc method"""
        report = self.testlink_manager.api_tcase_report(
            external_id=DATA['tc_report']['external_id'],
            tplan_id=DATA['tc_report']['tplan_id'],
            build_id=DATA['tc_report']['build_id'],
            platform_id=DATA['tc_report']['platform_id'],
            status=DATA['tc_report']['status']['blocked']
        )
        self.tc.assertIsInstance(report, RTCase)
        self.tc.assertTrue(report.status)
        self.tc.assertEqual(
            report.message, DATA['tc_report']['message'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_user_exist(self):
        """TODO: doc method"""
        is_user = self.testlink_manager.api_user_exist(
            DATA['user_name'])
        self.tc.assertTrue(is_user)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_about(self):
        """TODO: doc method"""
        about = self.testlink_manager.api_about()
        self.tc.assertIsInstance(about, str)
        self.tc.assertEqual(about, DATA['about'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_say_hello(self):
        """TODO: doc method"""
        say_hello = self.testlink_manager.api_say_hello()
        self.tc.assertIsInstance(say_hello, str)
        self.tc.assertEqual(say_hello, DATA['say_hello'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_ping(self):
        """TODO: doc method"""
        ping = self.testlink_manager.api_ping()
        self.tc.assertIsInstance(ping, str)
        self.tc.assertEqual(ping, DATA['ping'])

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_method_repeat(self):
        """TODO: doc method"""
        repeat = self.testlink_manager.api_repeat(DATA['repeat'])
        self.tc.assertIsInstance(repeat, str)
        self.tc.assertEqual(
            repeat, "You said: {}".format(DATA['repeat']))

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_notname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tproject)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_emptyname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tproject,
            '')

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_tplans_notid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tproject_tplans)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_tplans_notfoundid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tproject_tplans,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_tsuites_first_level_notid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tproject_tsuites_first_level)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tproject_tsuites_first_level_notfoundid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tproject_tsuites_first_level,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_notname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tplan)

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_raises_tplan_emptytprojectname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            '',
            DATA['tplan_name'])

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_raises_tplan_emptytplanname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            DATA['tproject_name'],
            '')

    @skipIf(True, 'Test SKIPPED, waiting for issue https://github.com/viglesiasce/testlink/issues/7') # noqa
    def test_raises_tplan_emptytnames(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tplan,
            '', '')

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_platforms_notname(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tplan_platforms)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_platforms_notfoundid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tplan_platforms,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_builds_notid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tplan_builds)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_builds_notfoundid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_tplan_builds,
            -1)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_tsuites_notid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception, self.testlink_manager.api_tplan_tsuites)

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_tplan_tsuites_notfoundid(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            ResponseException,
            self.testlink_manager.api_tplan_tsuites,
            -1)
