# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import affinitic.privatefolder


class AffiniticPrivateFolderLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=affinitic.privatefolder)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "affinitic.privatefolder:default")
        import transaction

        transaction.commit()

    def tearDownZope(self, app):
        import transaction

        transaction.abort()


AFFINITIC_PRIVATEFOLDER_FIXTURE = AffiniticPrivateFolderLayer()


AFFINITIC_PRIVATEFOLDER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(AFFINITIC_PRIVATEFOLDER_FIXTURE,),
    name="AffiniticPrivateFolderLayer:IntegrationTesting",
)


AFFINITIC_PRIVATEFOLDER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(AFFINITIC_PRIVATEFOLDER_FIXTURE,),
    name="AffiniticPrivateFolderLayer:FunctionalTesting",
)


AFFINITIC_PRIVATEFOLDER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        AFFINITIC_PRIVATEFOLDER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="AffiniticPrivateFolderLayer:AcceptanceTesting",
)
