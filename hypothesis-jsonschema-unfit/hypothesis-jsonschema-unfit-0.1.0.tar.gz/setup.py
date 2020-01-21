# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['hypothesis_jsonschema_unfit']

package_data = \
{'': ['*']}

install_requires = \
['hypothesis_jsonschema>=0.9.13,<1.0']

setup_kwargs = {
    'name': 'hypothesis-jsonschema-unfit',
    'version': '0.1.0',
    'description': '',
    'long_description': 'hypothesis-jsonschema-invalid\n=============================\n\nAn experimental project for the generation of JSON data that does NOT match the given JSON schema.\n\n.. code:: python\n\n    from hypothesis import given\n    from hypothesis_jsonschema_unfit import not_from_schema\n\n    SCHEMA = {\n        "items": {\n            "type": "object",\n            "required": ["key1", "key2"],\n            "properties": {"key1": {"type": "string"}, "key2": {"type": "integer"}},\n        },\n        "type": "array",\n        "minItems": 4,\n    }\n\n    @given(not_from_schema(SCHEMA))\n    def test(instance):\n        ...\n',
    'author': 'Dmitry Dygalo',
    'author_email': 'dadygalo@kiwi.com',
    'url': 'https://github.com/kiwicom/hypothesis-jsonschema-unfit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
