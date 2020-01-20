# coding: utf-8

"""
    Edge Impulse API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from edge_impulse_sdk.configuration import Configuration


class DevelopmentKeys(object):
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
        'api_key': 'str',
        'hmac_key': 'str'
    }

    attribute_map = {
        'api_key': 'apiKey',
        'hmac_key': 'hmacKey'
    }

    def __init__(self, api_key=None, hmac_key=None, local_vars_configuration=None):  # noqa: E501
        """DevelopmentKeys - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._api_key = None
        self._hmac_key = None
        self.discriminator = None

        if api_key is not None:
            self.api_key = api_key
        if hmac_key is not None:
            self.hmac_key = hmac_key

    @property
    def api_key(self):
        """Gets the api_key of this DevelopmentKeys.  # noqa: E501

        API Key  # noqa: E501

        :return: The api_key of this DevelopmentKeys.  # noqa: E501
        :rtype: str
        """
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        """Sets the api_key of this DevelopmentKeys.

        API Key  # noqa: E501

        :param api_key: The api_key of this DevelopmentKeys.  # noqa: E501
        :type: str
        """

        self._api_key = api_key

    @property
    def hmac_key(self):
        """Gets the hmac_key of this DevelopmentKeys.  # noqa: E501

        HMAC Key  # noqa: E501

        :return: The hmac_key of this DevelopmentKeys.  # noqa: E501
        :rtype: str
        """
        return self._hmac_key

    @hmac_key.setter
    def hmac_key(self, hmac_key):
        """Sets the hmac_key of this DevelopmentKeys.

        HMAC Key  # noqa: E501

        :param hmac_key: The hmac_key of this DevelopmentKeys.  # noqa: E501
        :type: str
        """

        self._hmac_key = hmac_key

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
        if not isinstance(other, DevelopmentKeys):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DevelopmentKeys):
            return True

        return self.to_dict() != other.to_dict()
