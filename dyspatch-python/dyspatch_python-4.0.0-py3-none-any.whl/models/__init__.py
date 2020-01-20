# coding: utf-8

# flake8: noqa
"""
    Dyspatch API

    # Introduction  The Dyspatch API is based on the REST paradigm, and features resource based URLs with standard HTTP response codes to indicate errors. We use standard HTTP authentication and request verbs, and all responses are JSON formatted. See our [Implementation Guide](https://docs.dyspatch.io/development/implementing_dyspatch/) for more details on how to implement Dyspatch.  ## API Client Libraries Dyspatch provides API Clients for popular languages and web frameworks.  - [Java](https://github.com/getdyspatch/dyspatch-java) - [Javascript](https://github.com/getdyspatch/dyspatch-javascript) - [Python](https://github.com/getdyspatch/dyspatch-python) - [C#](https://github.com/getdyspatch/dyspatch-dotnet) - [Go](https://github.com/getdyspatch/dyspatch-golang) - [Ruby](https://github.com/getdyspatch/dyspatch-ruby)    # noqa: E501

    The version of the OpenAPI document: 2019.10
    Contact: support@dyspatch.io
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

# import models into model package
from dyspatch_client.models.api_error import APIError
from dyspatch_client.models.compiled_read import CompiledRead
from dyspatch_client.models.cursor import Cursor
from dyspatch_client.models.draft_meta_read import DraftMetaRead
from dyspatch_client.models.draft_read import DraftRead
from dyspatch_client.models.drafts_read import DraftsRead
from dyspatch_client.models.inline_object import InlineObject
from dyspatch_client.models.localization_key_read import LocalizationKeyRead
from dyspatch_client.models.localization_meta_read import LocalizationMetaRead
from dyspatch_client.models.localization_read import LocalizationRead
from dyspatch_client.models.template_meta_read import TemplateMetaRead
from dyspatch_client.models.template_read import TemplateRead
from dyspatch_client.models.templates_read import TemplatesRead
