# -*- coding: utf-8 -*-
"""TODO: doc module"""


import logging
from unittest import TestCase
from unittest import skipIf
from qatestlink.core.testlink_manager import TLManager
from qatestlink.core.utils import settings


SETTINGS = settings()
API_DEV_KEY = SETTINGS['dev_key']
SKIP = SETTINGS['tests']['skip']['connection']
SKIP_MESSAGE = SETTINGS['tests']['skip_message']


class TestConnection(object):
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
    def test_connok_bysettings(self):
        """TODO: doc method"""
        self.tc.assertTrue(
            self.testlink_manager.api_login())

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_connok_byparam(self):
        """TODO: doc method"""
        self.tc.assertTrue(
            self.testlink_manager.api_login(
                dev_key=API_DEV_KEY))

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_connok_notdevkey(self):
        """TODO: doc method"""
        self.tc.assertTrue(
            self.testlink_manager.api_login(
                dev_key=None))

    @skipIf(SKIP, SKIP_MESSAGE)
    def test_raises_connemptydevkey(self):
        """TODO: doc method"""
        self.tc.assertRaises(
            Exception,
            self.testlink_manager.api_login, dev_key=' ')
