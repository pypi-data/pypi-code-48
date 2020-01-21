# -*- coding: utf-8 -*-
# Adapted copy of PloneHotfix20160830/tests/test_102_in_portal.py
from Products.PloneHotfix20200121.tests import BaseTest


class TestAttackVector(BaseTest):
    def test_regression(self):
        self.assertTrue(self.portal.portal_url.isURLInPortal("foobar"))

    def test_script_tag_url_not_in_portal(self):
        self.assertFalse(
            self.portal.portal_url.isURLInPortal('<sCript>alert("hi");</script>')
        )
        self.assertFalse(
            self.portal.portal_url.isURLInPortal(
                "%3CsCript%3Ealert(%22hi%22)%3B%3C%2Fscript%3E"
            )
        )

    def test_inline_url_not_in_portal(self):
        self.assertFalse(self.portal.portal_url.isURLInPortal("jaVascript%3Aalert(3)"))
        self.assertFalse(self.portal.portal_url.isURLInPortal("jaVascript:alert(3)"))

    def test_double_back_slash(self):
        self.assertFalse(self.portal.portal_url.isURLInPortal("\\\\www.google.com"))
