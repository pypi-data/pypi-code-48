# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opset']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'munch>=2.3,<3.0',
 'pytz>=2018.9',
 'pyyaml>=3.13,<6',
 'structlog>=19.1,<20.0']

setup_kwargs = {
    'name': 'opset',
    'version': '1.2.0',
    'description': 'A library for simplifying the configuration of Python applications at all stages of deployment.',
    'long_description': '# Opset\n\n[![Coverage Status](https://coveralls.io/repos/github/ElementAI/opset/badge.svg)](https://coveralls.io/github/ElementAI/opset)\n\nA library for simplifying the configuration of Python applications at all stages of deployment.\n\nOpset is a config manager that let you manage your configuration via yaml file or environment variables.\nThe general principle of Opset is that you want to hold your secrets and manage your configurations via\nconfiguration files when doing local development and via environment variables when your app is deployed. It is however\npossible to also handle local development through environment variables if the developer see fit.\n\nWith Opset you define everything that can be tweaked with your application in one specific\nfile (`default.yml`). This way the developers and integrators working with your code will know exactly what setting they\ncan change on your code base. You can then overwrite the default config with a local config stored in a file called\n`local.yml`, this file is aimed to be used for local development by your developers and let them easily manage a\nconfiguration file that fits their development need. Finally, you can also have environment variables that have a\nmatching name to your config that will overwrite your config, letting you use your config in a deployed environment\nwithout having your secret written down in a config file. Opset aims to reconcile the ease of use of a\nconfig file with the added security of environment variables.\n\nThis library is available on PyPI under the name Opset. You can install with pip by running `pip install opset`.\n\n# Table of Contents\n\n1. [Lexicon](#lexicon)\n1. [Architecture Overview](#architecture-overview)\n    1. [Loading the config for unit tests](#loading-the-config-for-unit-tests)\n    1. [Safeguards](#safeguards)\n        1. [Settings not declared in default.yml are not loaded](#settings-not-declared-in-defaultyml-are-not-loaded)\n        1. [Forcing all default settings to have values](#forcing-all-default-settings-to-have-values)\n1. [Usage Guide](#usage-guide)\n    1. [Making the difference between null and empty](#making-the-difference-between-null-and-empty)\n1. [Example of Usage](#example-of-usage)\n    1. [Opset + Environment Variables](#Opset--environment-variables)\n    1. [Naming your config sections](#naming-your-config-sections)\n    1. [Controlling your entry points](#controlling-your-entry-points)\n1. [Example Configuration file](#example-configuration-file)\n    1. [default.yml](#defaultyml)\n    1. [local.yml](#localyml)\n    1. [unit_test.yml](#unit_testyml)\n    1. [Example Logging Configuration values](#example-logging-configuration-values)\n    1. [Log Processors](#log-processors)\n1. [Support for unit tests](#support-for-unit-tests)\n    1. [setup_unit_test_config](#setup_unit_test_config)\n        1. [Usage example of setup_unit_test_config](#usage-example-of-setup_unit_test_config)\n    1. [mock_config](#mock_config)\n        1. [Usage example of mock_config](#usage-example-of-mock_config)\n1. [Contributing and getting set up for local development](#contributing-and-getting-set-up-for-local-development)\n\n## Lexicon\n\n| Term | Definition |\n|--- | --- |\n| config |\tA configuration file (format: YAML). |\n| section\t| A section within a configuration file, a section tend to group different settings together under a logical block. For example a section named redis would encompass all settings related specifically to redis. Section name should not contain underscore. |\n| setting\t| A key within a section in a configuration file. A value is associated with a key and querying the config for a setting within a section will return the value associated with it. |\n\n![Lexicon](https://github.com/ElementAI/opset/raw/master/doc/lexicon.png)\n\n## Architecture Overview\n\nThere are three possible config files\n\n| Config Name | Purpose |\n| --- | --- |\n| default.yml | This is the base config, `default.yml` needs to have the declaration of all sections and settings. |\n| local.yml | This is a local config that overwrites the default config, this file is not committed to the repository and is meant to be used in a local development environment. |\n| unit_test.yml | This is a local config that overwrites the default config during unit tests, this file is not committed to the repository and is meant to be used in a local development environment. When the config is initialized for unit tests, if a `unit_test.yml` file is present it will be loaded, otherwise the environment variables will be loaded on top of the default config. |\n\nThe content of the default config is loaded first, and if any settings are redefined in `local.yml`, the values from\n`default.yml` are overwritten by `local.yml`.\n\nEnvironment variables will apply after the `local.yml` overwrite of the config settings if they have a matching name. To\ndo so, the environment variable must be named in the following way:\n\n> {APP_NAME_ALL_CAPS_UNDERSCORE}_{SECTION}_{SETTING}\n\nSo for the application my-small-project if we wanted to overwrite the setting port from the section app, your\nenvironment variable would need to be named like this:\n\n> MY_SMALL_PROJECT_APP_PORT\n\n![Order](https://github.com/ElementAI/opset/raw/master/doc/setup_config_overwrite_order.png)\n\n### Loading the config for unit tests\n\nOpset provides a specific function to load the config when performing unit testing that provides the\ndeveloper with some additional tool to better handle the reality of unit testing. When initializing the config for\nunit tests, the content of the default config is loaded first, and if the `unit_test.yml` file is present and have\nvalues, the values from `default.yml` are overwritten by `unit_test.yml`. Then the values from the environment variables\napply and if you need some config values to be specific to your unit tests you have the option to pass config values\nwhen loading the unit tests that will overwrite all other sources.\n\n![Order](https://github.com/ElementAI/opset/raw/master/doc/setup_config_unit_test_overwrite_order.png)\n\n### Safeguards\n\nThere are two safeguards in the code to try to prevent developer mistakes.\n\n#### Settings not declared in `default.yml` are not loaded\n\nYour `default.yml` is what defines what can be tweaked in your application, it is made to be the one place to look at if\nyou are wondering what can be changed in the configuration of your application.\n\nWhen loading the configuration a warning will be raised if a setting is detected from the local config, environment\nvariables or unit tests values that is not present in `default.yml`. This means that if your `local.yml`\nconfig looks like this:\n\n```\napp:\n  host: 127.0.0.1\n  port: 7777\n  ham_level: 7\n  api_key: 332d5c3e-a7a3-41db-aa5c-c0dfbac8f3d2\n```\n\nAnd your default config looks like this:\n\n```\napp:\n  host: 127.0.0.1\n  port: 7777\n  debug: False\n  api_key: null\n```\n\nA warning will be issued when the config is loaded because the setting `ham_level` from the section `app` is not known to\nthe default config. The setting and value of `ham_level` will not be loaded in the config and will not be usable in the\napplication if it\'s not present in `default.yml`. As per the example above, you are not forced to set a value for\nsettings in the default config (see api_key), but the setting needs to be there.\n\n#### Forcing all default settings to have values\n\nThere is a special flag called `critical_settings` that is passed to the function `setup_config` from the module.\nThis flag is set to `True` by default and will make Opset raises an error if there is no\nvalue defined for a setting in `default.yml` after having applied all possible configuration files and environment\nvariables.\n\n## Usage Guide\n\nYou interact with the library through the function `opset.setup_config` to set up the config and with the\nsingleton object `opset.config` to read config values. Optionally Opset can also manage your\napplication logging via the function `opset.load_logging_config` or the argument `setup_logging` from the\nfunction `opset.setup_config`. The `opset.config` object is a singleton which means that no matter where\nit is accessed in the code and the loading order, as long as it has been initiated with `opset.setup_config` it\nwill hold the same configuration values in all of your application.\n\nThe library expects that your project will contain [yaml](https://yaml.org/) files named `default.yml` and\n(optionally) `local.yml` and `unit_test.yml`. You will be able to point to the location of those config files when\ninvoking `opset.setup_config` as the second positional argument. The file `default.yml` should be committed and follow your\nproject and should not contain any secrets. The files `local.yml` and `unit_test.yml` should be added to your\n`.gitignore` to avoid having them committed by accident as those files can contain secrets.\n\nThe `opset.setup_config` function will handle everything from reading the yaml file containing your project\'s config values,\nto loading them into your environment being mindful not to overwrite ENV variables already present. It needs to be\npassed the name of your application along with the python style path (eg. `module.submodule`) to where the\n`default.yml`, `local.yml` or `unit_test.yml` files are located in the project.\n\nTo initialize the configuration, use the function `opset.setup_config` and that\'s it. After that you can import\nthe variable `opset.config` from the module to use the config. You can safely import the config variable before\ninitializing it because access to the config object attributes is dynamic. It is important to note that the config is\nbuilt to be read-only, it gets populated when `opset.setup_config` and from then on you just read the values from\nthe config as needed in your implementation.\n\nThe function setup_config takes the following arguments:\n\n| Parameter | Description | Default value | Example\n| --- | --- | --- | --- |\n| `app_name` | The name of the application, usually the name of the repo. Ex: myproject-example. This will be used for finding the prefix to the environment variables. The name of the app will be uppercased and dashes will be replaced by underscores. | | `myproject-example` |\n| `config_path` | A python path to where the configuration files are. Relative to the application. Ex: `tasks.config` would mean that the config files are located in the directory config of the directory tasks from the root of the repo. | | `tasks.config` |\n| `critical_settings` | A boolean to specify how null settings in `default.yml` should be handled. If set to `True`, the function will raise an exception when a key in `default.yml` is not defined in `local.yml` or in an environment variable. | `True` | `True` |\n| `setup_logging` | Whether the logging config should be loaded immediately after the config has been loaded. Default to `True`. | `True` | `True` |\n\n### Making the difference between null and empty\n\nThe configuration is stored in yaml and follows the yaml standard. As such, it makes a distinction between null keys\nand empty keys. \n\n```\napp:\n  # this setting\'s value is declared but not defined\n  # it will be set to None when accessed unless it is overwritten in local.yml or in an environment variable\n  api_key: null\n  # this setting\'s value is set to an empty string\n  log_prefix: \n```\n\n### Naming your config sections\n\nDue to certain limitations when loading environment variables, your config sections should not contain underscores to\navoid issues when loading environment variables.\n\n### Controlling your entry points\n\nThe config object is initiated once you call the function `opset.setup_config`, before that, trying to get read\na value from the config will throw an exception. It is very important to have a good idea of what the entry points\nare in your application and to call `opset.setup_config` as early as possible in your application to avoid issues.\n\nTo avoid duplicating calls to `opset.setup_config` we recommend you add the call to `opset.setup_config`\nin a function that is called whenever you need to start your application, you can then safely call this function\nwhenever you create a new entry points in your application.\n\nBe mindful about reading values from the config object at module level. If you need to import modules before you can\ncall `opset.setup_config` and one of those modules has a module-level call to read the config, Opset\nwill raise an error when importing because the code will be read at import time and the config will not have been\ninitiated.\n\nFor a more concrete example, avoid doing something like this:\n\n```python\nfrom opset import config\n\nFULL_DB_URI = f"{config.db.scheme}{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}"\n```\n\nAnd do something like this instead:\n\n```python\nfrom opset import config\n\ndef get_full_db_uri():\n    return f"{config.db.scheme}{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}"\n```\n\nLast thing, remember that it is safe to import the config object before the config has been initiated. The config\nobject is a singleton and will be populated after `opset.setup_config` has been called, even if it was imported\nfirst.\n\n## Example Of Usage\n\nHere is a little example of how to use the opset features in a simple Flask app.\n\n```python\nfrom flask import Flask, jsonify\nfrom opset import config, setup_config\n\n\nsetup_config("myproject-example", "myproject-example.config")\n \napp = Flask(config.app.name)\n\n@app.route("/")\ndef hello():\n    return jsonify({"Hello and welcome to": config.app.welcome_message})\n```\n\nThis example will leverage the config values stored under the `myproject-example/config` folder, with the following content:\n\n```yaml\napp:\n  welcome_message: Hi lads\n```\n\n### Opset + Environment Variables\n\nOne of the features of Opset is how it handles the interaction between the config values in your projects\' yaml\nfiles and the values that might already be set in your environment. Values already in your environment have higher\npriority and will overwrite any values in your config files. In order to compare against the environment variables,\nOpset builds the names for config values using `<APP_NAME>_<SECTION_NAME>_<SETTING_NAME>` as a template.\nThis means that if your environment contains the value `MYPROJECT_EXAMPLE_DATABASE_HOST`, and your application is named\n`myproject-example` it will overwrite the value of the database host from the following config file:\n\n```yaml\ndatabase:\n  host: 89.22.102.02\n```\n\nThe conversion to python types from the yaml config file is handled by pyyaml but for environment variables\nOpset do its own conversion depending on the value:\n\n- `true`, `t`, `yes`, `y` (case-insensitive) will be converted to a `True` `bool`\n- `false`, `f`, `no`, `n` (case-insensitive) will be converted to a `False` `bool`\n- Any number-only string will be converted to an `int` if they have no decimals and `float` if they do\n- A JSON-valid array will be converted to a `list`\n- A JSON-valid object will be converted to a `dict`\n- Any other value will remain a `str`\n\nNOTE: Be sure to respect JSON conventions when defining arrays and objects, use lower-case booleans, double quotes, etc.\n\n## Example Configuration file\n\n### default.yml\n\nDeclare in the `default.yml` file all the settings that the app will require. For each of the keys,\nyou can define a default value. If there is no sensible defaults for a setting, leave it blank (which\nis equivalent to setting it to _null_).\n\nAs a rule of thumb, a default value should be equally good and safe for local, staging or prod environments.\nFor example, setting `app.debug` above to `True` would be an error as it may cause prod to run with debug\nmessages enabled if prod is not overriding it. The opposite is also true. A default value pointing to a production\nsystem can easily wipe or overload it during testing if tests do not overwrite the defaults properly. When in doubt,\nprefer a null value.\n\nAlso, secrets should NEVER be added to this file.\n\n### local.yml\n\nThis file is typically defined by developers for their own development and local usage of the app. This file\nmay contain secrets and as such it must be added to the `.gitignore` file.\n\n### unit_test.yml\n\nThis file is used to handle configuration values when running unit tests locally by developers. The content of this\nfile is only used when initiating the config through `opset.setup_unit_test_config` and is discussed in more\ndetails in the section of the documentation dedicated to unit testing. This file may contain secrets and as such it\nmust be added to the `.gitignore` file.\n\n### Example Logging Configuration values\n\nOpset also provides functionality for configuring the logging handlers for your project, this uses\n`structlog` in the background. This is provided through the aforementioned `load_logging_config` function. If you\nchoose to use this functionality, you will need to add some more values to your configuration files, and you can find\nan example of such values here:\n\n```yaml\nlogging:\n  date_format: "iso"  # strftime-valid date format, e.g.: "%Y-%M-%d", or "iso" to use the standard ISO format\n  use_utc: True  # Use UTC timezone if true, or local otherwise\n  min_level: DEBUG  # Minimum level to display log for\n  colors: False  # Use colors for log display, defaults to False\n  disable_processors: False  # Disables log processors (additional info at the end of the log record)\n  logger_overrides:  # overwrite min log level of third party loggers\n    googleapiclient: ERROR\n```\n\n### Log Processors\n\nSince we are using `structlog` you can use the Processor feature to add additional info to your log records, this\ncan be useful to add a request ID, or the hostname of the machine to all your log records without having to pass\nanything to your logging calls.\n\nTo use this simply define any processors you want by inheriting from the `BaseProcessor` class of `opset`\nand pass an instance to the `load_logging_config` call:\n\n```python\nimport logging\n\nfrom flask import Flask\nfrom opset import BaseProcessor, load_logging_config, setup_config\n\nfrom my_app.request_context import get_request_id\n\n\nclass RequestContextProcessor(BaseProcessor):\n    def __call__(self, logger, name, event_dict):\n        event_dict["request_id"] = get_request_id()\n        return event_dict\n\n\nsetup_config("my_app", "my_app.config", setup_logging=False)  # Defer the logging setup\nload_logging_config(custom_processors=[RequestContextProcessor()])  # Pass your custom processors\n\napp = Flask(__name__)\n\n@app.route("/")\ndef root():\n    logging.info("This will include the request ID!")\n    return "OK"\n```\n\nA processor receives the logger object, the logger name and most importantly the `event_dict` which contains all the\ninfo of the log record. So simply add to the `event_dict` in your processor and return it.\n\nIn local development processors can add some unnecessary noise to the log output, so they can be disabled by setting\n`logging.disable_processors` to `True` in your `local.yml`.\n\nBy default, Opset enables the built-in `HostNameProcessor`, which adds the machine hostname to log records.\nIt can be disabled by passing `use_hostname_processor=False` in the `load_logging_config` call.\n\n## Support for unit tests\n\nOpset support unit testing to make sure you can handle the special cases that may come up in your\napplication configuration during unit testing.\n\n### setup_unit_test_config\n\nThe function `opset.setup_unit_test_config` is made to replace `opset.setup_config` when running unit\ntests. Remember to control your entry points and call this function as early as possible when running the unit tests.\nIf you are using pytest it is recommended to add it to a\n[conftest.py](https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins) module set at the root of\nyour unit tests package.\n\n`opset.setup_unit_test_config` works in the same way as `opset.setup_config` but will load the yaml\nconfig file `unit_test.yml` if present instead of `local.yml`. It also accepts an additional parameter called\n`config_values` that is a dictionary representation of a config file that will have the highest priority when doing\noverwrites.\n\n| Parameter | Description | Default value | Example\n| --- | --- | --- | --- |\n| `app_name` | The name of the application, usually the name of the repo. Ex: myproject-example. This will be used for finding the prefix to the environment variables. The name of the app will be uppercased and dashes will be replaced by underscores. | | `myproject-example` |\n| `config_path` | A python path to where the configuration files are. Relative to the application. Ex: `tasks.config` would mean that the config files are located in the directory config of the directory tasks from the root of the repo. | | `tasks.config` |\n| `config_values` | A dictionary mimicking the structure of the config files, to be applied as an overwrite on top of default + unit_test config (if available) and env variables. | | `{"app": {"debug": False}}` |\n\n#### Usage example of setup_unit_test_config\n\nIn `default.yml`:\n\n```yaml\ndb:\n    user: \n    password:\n    name: staging\n```\n\nIn `unit_test.yml`:\n\n```yaml\ndb:\n    user: serge\n    password: mystrongpassword\n```\n\nIn the `conftest.py` module a the root of your unit tests package:\n\n```python\nfrom opset import config, setup_unit_test_config\n\nsetup_unit_test_config("myproject-example", "myproject-example.config", config_values={"db": {"name": "test"}})\n```\n\nAfter running `opset.setup_unit_test_config` the config will hold the following values:\n\n```\n>>> config.db.user\n\'serge\'\n\n>>> config.db.password\n\'mystrongpassword\'\n\n>>> config.db.name\n\'test\' \n```\n\n### mock_config\n\nThe function `opset.mock_config` is a context manager that lets you overwrite config values from the config\nobject for the time of a unit tests. If your unit test requires for the time of a test to have your config hold a\nspecial temporary value, `opset.mock_config` is there for you. It takes the parameter `config_values` which\nis identical to what `opset.setup_unit_test_config` uses.\n\nYour config object will be duplicated for the duration of your context manager and overwritten by the values you send\nto the parameter `config_values`. Once you exit the context manager the copy of the config disappears and your\napplication resumes with the config object being in the same state as it was before entering the context manager.\n\n#### Usage example of mock_config\n\nIn your module to be tested:\n\n```python\nfrom opset import config\n\ndef is_admin(user_name: str) -> bool:\n    return user_name in config.app.admin_list\n```\n\nIn your `default.yml`:\n```yaml\napp:\n    admin_list: \n```\n\nIn your `unit_test.yml`:\n```yaml\napp:\n    admin_list:\n      - "jotaro kujo"\n```\n\nIn your unit test module:\n```python\nfrom opset import mock_config\n\nfrom my_package.my_module import is_admin\n\n\ndef test_is_admin():\n    # Test true\n    assert is_admin("jotaro kujo")\n    \n    # Test false\n    with mock_config(config_values={"app": {"admin_list": []}}):\n        assert not is_admin("jotaro kujo")\n```\n\n\n## Contributing and getting set up for local development\n\nTo set yourself up for development on Opset, make sure you are using\n[poetry](https://poetry.eustace.io/docs/) and simply run the following commands from the root directory:\n\n```bash\nmake bootstrap\nmake install\n```\n',
    'author': 'Element AI Inc.',
    'author_email': 'hello@elementai.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ElementAI/opset',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
