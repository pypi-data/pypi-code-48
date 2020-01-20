# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from pulpcore.client.pulp_ansible.configuration import Configuration


class ContentSummary(object):
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
        'added': 'dict(str, dict(str, str))',
        'removed': 'dict(str, dict(str, str))',
        'present': 'dict(str, dict(str, str))'
    }

    attribute_map = {
        'added': 'added',
        'removed': 'removed',
        'present': 'present'
    }

    def __init__(self, added=None, removed=None, present=None, local_vars_configuration=None):  # noqa: E501
        """ContentSummary - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._added = None
        self._removed = None
        self._present = None
        self.discriminator = None

        self.added = added
        self.removed = removed
        self.present = present

    @property
    def added(self):
        """Gets the added of this ContentSummary.  # noqa: E501


        :return: The added of this ContentSummary.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._added

    @added.setter
    def added(self, added):
        """Sets the added of this ContentSummary.


        :param added: The added of this ContentSummary.  # noqa: E501
        :type: dict(str, dict(str, str))
        """
        if self.local_vars_configuration.client_side_validation and added is None:  # noqa: E501
            raise ValueError("Invalid value for `added`, must not be `None`")  # noqa: E501

        self._added = added

    @property
    def removed(self):
        """Gets the removed of this ContentSummary.  # noqa: E501


        :return: The removed of this ContentSummary.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._removed

    @removed.setter
    def removed(self, removed):
        """Sets the removed of this ContentSummary.


        :param removed: The removed of this ContentSummary.  # noqa: E501
        :type: dict(str, dict(str, str))
        """
        if self.local_vars_configuration.client_side_validation and removed is None:  # noqa: E501
            raise ValueError("Invalid value for `removed`, must not be `None`")  # noqa: E501

        self._removed = removed

    @property
    def present(self):
        """Gets the present of this ContentSummary.  # noqa: E501


        :return: The present of this ContentSummary.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._present

    @present.setter
    def present(self, present):
        """Sets the present of this ContentSummary.


        :param present: The present of this ContentSummary.  # noqa: E501
        :type: dict(str, dict(str, str))
        """
        if self.local_vars_configuration.client_side_validation and present is None:  # noqa: E501
            raise ValueError("Invalid value for `present`, must not be `None`")  # noqa: E501

        self._present = present

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
        if not isinstance(other, ContentSummary):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ContentSummary):
            return True

        return self.to_dict() != other.to_dict()
