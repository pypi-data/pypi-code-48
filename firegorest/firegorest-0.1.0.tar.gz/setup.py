# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['firegorest']

package_data = \
{'': ['*']}

install_requires = \
['importlib_metadata>=1.4.0,<2.0.0', 'iso8601>=0.1.12,<0.2.0']

setup_kwargs = {
    'name': 'firegorest',
    'version': '0.1.0',
    'description': 'Some utilties to work with Google Firestore API.',
    'long_description': "==========\nFireGoRest\n==========\n\n\nSome utilties to work with Google Firestore API.\n\nFirst utility is ``firegorest.tidy_doc``, to make a neat data dictionary from the `event`_ passed by Google Cloud runtime to your cloud function.\n\nInstall\n-------\n\n    pip install firegorest\n\n\nExample\n-------\n\n.. code-block:: python\n\n    from logbook import Logger\n    from firegorest import tidy_doc\n    from firegorest.types import GCFContext\n\n    logger = Logger(__name__)\n\n\n    def act_on_customer_change(event: dict, context: GCFContext):\n        try:\n            logger.info('Old Value: {}', tidy_doc(event['oldValue']['fields']))\n        except KeyError:\n            pass\n        try:\n            logger.info('New Value: {}', tidy_doc(event['value']['fields']))\n        except KeyError:\n            pass\n        resource = context.resource\n        logger.debug('Resource: {}', resource)\n        return True\n\n\n\n.. _event: https://cloud.google.com/functions/docs/calling/cloud-firestore#event_structure\n",
    'author': 'Nguyễn Hồng Quân',
    'author_email': 'ng.hong.quan@gmail.com',
    'maintainer': 'Nguyễn Hồng Quân',
    'maintainer_email': 'ng.hong.quan@gmail.com',
    'url': 'https://github.com/sunshine-tech/FireGoRest.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
