# coding: utf-8

"""
    Dyspatch API

    # Introduction  The Dyspatch API is based on the REST paradigm, and features resource based URLs with standard HTTP response codes to indicate errors. We use standard HTTP authentication and request verbs, and all responses are JSON formatted. See our [Implementation Guide](https://docs.dyspatch.io/development/implementing_dyspatch/) for more details on how to implement Dyspatch.  ## API Client Libraries Dyspatch provides API Clients for popular languages and web frameworks.  - [Java](https://github.com/getdyspatch/dyspatch-java) - [Javascript](https://github.com/getdyspatch/dyspatch-javascript) - [Python](https://github.com/getdyspatch/dyspatch-python) - [C#](https://github.com/getdyspatch/dyspatch-dotnet) - [Go](https://github.com/getdyspatch/dyspatch-golang) - [Ruby](https://github.com/getdyspatch/dyspatch-ruby)    # noqa: E501

    The version of the OpenAPI document: 2019.10
    Contact: support@dyspatch.io
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from dyspatch_client.configuration import Configuration


class LocalizationKeyRead(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'key': 'str',
        'comment': 'str'
    }

    attribute_map = {
        'key': 'key',
        'comment': 'comment'
    }

    def __init__(self, key=None, comment=None, local_vars_configuration=None):  # noqa: E501
        """LocalizationKeyRead - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._key = None
        self._comment = None
        self.discriminator = None

        if key is not None:
            self.key = key
        if comment is not None:
            self.comment = comment

    @property
    def key(self):
        """Gets the key of this LocalizationKeyRead.  # noqa: E501


        :return: The key of this LocalizationKeyRead.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this LocalizationKeyRead.


        :param key: The key of this LocalizationKeyRead.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def comment(self):
        """Gets the comment of this LocalizationKeyRead.  # noqa: E501


        :return: The comment of this LocalizationKeyRead.  # noqa: E501
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment):
        """Sets the comment of this LocalizationKeyRead.


        :param comment: The comment of this LocalizationKeyRead.  # noqa: E501
        :type: str
        """

        self._comment = comment

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, LocalizationKeyRead):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, LocalizationKeyRead):
            return True

        return self.to_dict() != other.to_dict()
