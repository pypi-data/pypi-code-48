# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['countries_plus',
 'countries_plus.management',
 'countries_plus.management.commands',
 'countries_plus.migrations']

package_data = \
{'': ['*'], 'countries_plus': ['fixtures/*']}

install_requires = \
['requests', 'six']

extras_require = \
{':python_version >= "2.7" and python_version < "3.0"': ['django<=1.11'],
 ':python_version >= "3.6" and python_version < "4.0"': ['django>=2']}

setup_kwargs = {
    'name': 'django-countries-plus',
    'version': '1.3.0',
    'description': 'A django model & fixture containing all data from the countries table of Geonames.org',
    'long_description': "=============================\nDjango Countries Plus\n=============================\n\n.. image:: https://badge.fury.io/py/django-countries-plus.svg\n    :target: https://badge.fury.io/py/django-countries-plus\n\n.. image:: https://travis-ci.org/cordery/django-countries-plus.svg\n    :target: https://travis-ci.org/cordery/django-countries-plus\n\n.. image:: https://codecov.io/github/cordery/django-countries-plus/coverage.svg\n    :target: https://codecov.io/github/cordery/django-countries-plus\n\n.. image:: https://requires.io/github/cordery/django-countries-plus/requirements.svg?branch=master\n    :target: https://requires.io/github/cordery/django-countries-plus/requirements/?branch=master\n\n.. image:: https://www.codacy.com/project/badge/c74f1b1041f44940b58e0e1587b10453?style=flat-square\n    :target: https://www.codacy.com/app/cordery/django-countries-plus\n\ndjango-countries-plus provides a model and fixture containing all top level country data from Geonames.org (http://download.geonames.org/export/dump/countryInfo.txt)\n\nThis package also provides a convenience middleware that will look up a country in the database using a defined meta header, ex:  the Cloudflare provided geoip META header HTTP_CF_IPCOUNTRY.  This country object will be\nattached to the request object at request.country.\n\n\n\nCountry Model\n-------------\n\nThe model provides the following fields (original geonames.org column name in parentheses).\n\n* iso (ISO)\n* iso3 (ISO3)\n* iso_numeric (ISO-Numeric)\n* fips (fips)\n* name (Country)\n* capital\n* area (Area(in sq km))\n* population (population)\n* continent (continent)\n* tld (tld)\n* currency_code (CurrencyCode)\n* currency_name (CurrencyName)\n* currency_symbol (Not part of the original table)\n* phone (Phone)\n* postal_code_format (Postal Code Format)\n* postal_code_regex (Postal Code Regex)\n* languages (Languages)\n* geonameid (geonameid)\n* neighbors (neighbours)\n* equivalent_fips_code (EquivalentFipsCode)\n\n\n\nInstallation\n------------\n\nStep 1: Install From PyPi\n\n``pip install django-countries-plus``\n\nStep 2: Add ``countries_plus`` to your settings INSTALLED_APPS\n\nStep 3: Run ``python manage.py migrate``\n\nStep 4: Load the Countries Data\n    a. Load the countries data into your database with the update_countries_plus management command.\n        ``python manage.py update_countries_plus``\n    b. (alternative) Load the provided fixture from the fixtures directory.\n        ``python manage.py loaddata PATH_TO_COUNTRIES_PLUS/countries_plus/countries_data.json.gz``\n\n\n\nUsage\n-----\n\n**Retrieve a Country**::\n\n    from countries_plus.models import Country\n    usa = Country.objects.get(iso3='USA')\n\n**Update the countries data with the latest geonames.org data**::\n\n    python manage.py update_countries_plus\n\nThis management command will download the latest geonames.org countries data and convert it into Country objects.  Existing Country objects will be updated if necessary.  No Country objects will be deleted, even if that country has ceased to exist.\n\n\nAdd the Request Country to each Request\n---------------------------------------\n\n1.  Add ``countries_plus.middleware.AddRequestCountryMiddleware`` to your MIDDLEWARE setting.\n\n2.  add the following two settings to your settings.py:\n\n    ``COUNTRIES_PLUS_COUNTRY_HEADER``   -   A string defining the name of the meta header that provides the country code.  Ex: 'HTTP_CF_COUNTRY' (from https://support.cloudflare.com/hc/en-us/articles/200168236-What-does-CloudFlare-IP-Geolocation-do-)\n\n    ``COUNTRIES_PLUS_DEFAULT_ISO``  -   A string containing an iso code for the country you want to use as a fallback in the case of a missing or malformed geoip header.  Ex:  'US' or 'DE' or 'BR'\n\n    Example::\n\n        COUNTRIES_PLUS_COUNTRY_HEADER = 'HTTP_CF_COUNTRY'\n        COUNTRIES_PLUS_DEFAULT_ISO = 'US'\n\n\nAdd the Request Country to the Request Context\n----------------------------------------------\n1. Enable the optional middleware as described above\n\n2. Add ``countries_plus.context_processors.add_request_country`` to your 'context_processors' option in the OPTIONS of a DjangoTemplates backend instead (Django 1.8)\n\n\n---------------------------------------\nRequirements\n---------------------------------------\nPython: 2.7 or 3.*\nDjango:  Tested against the latest versions of 1.11, 2, and 3.\n\n\nIntegrating with django-languages-plus\n--------------------------------------\nIf you also have django-languages-plus(https://pypi.python.org/pypi/django-languages-plus) installed then you can run the following command once to associate the two datasets and generate a list of culture codes (pt_BR for example)::\n\n        from languages_plus.utils import associate_countries_and_languages\n        associate_countries_and_languages()\n\n\nNotes on 1.0.1\n--------------\n* Two countries (Dominican Republic and Puerto Rico) have two phone number prefixes instead of 1.  These prefixes are now comma separated.\n* The Country model has had all fields with undefined lengths (ex: name) expanded to max_length=255.  Defined length fields (ex: Iso, Iso3) are unchanged.\n* The Country model will no validate on save and reject values of the wrong length.  The test suite has been expanded to test this.\n\nNotes on 1.0.0\n--------------\n* The data migration has been removed in favour of the new management command and manually loading the fixture.\n* The fixture is no longer named initial_data and so must be loaded manually, if desired.\n* In order to provide better compatibility with the way Django loads apps the Country model is no longer importable directly from countries_plus.\n* The get_country_by_request utility function has been moved into the Country model, and is available as Country.get_by_request(request)\n* Test coverage has been substantially improved.\n* If you have been running an earlier version you should run python manage.py update_countries_plus to update your data tables as they may contain incorrect data.\n\n\n\nRunning Tests\n-------------\n\nDoes the code actually work?\n\n::\n\n    $ poetry install\n    $ poetry run pytest\n\nOr for the full tox suite:\n\n::\n\n    $ poetry install\n    $ pip install tox\n    $ tox\n\n",
    'author': 'Andrew Cordery',
    'author_email': 'cordery@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cordery/django-countries-plus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
}


setup(**setup_kwargs)
