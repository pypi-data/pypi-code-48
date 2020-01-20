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


class DSPMetadataIncludedSamples(object):
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
        'id': 'float',
        'window_count': 'float'
    }

    attribute_map = {
        'id': 'id',
        'window_count': 'windowCount'
    }

    def __init__(self, id=None, window_count=None, local_vars_configuration=None):  # noqa: E501
        """DSPMetadataIncludedSamples - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._window_count = None
        self.discriminator = None

        self.id = id
        self.window_count = window_count

    @property
    def id(self):
        """Gets the id of this DSPMetadataIncludedSamples.  # noqa: E501


        :return: The id of this DSPMetadataIncludedSamples.  # noqa: E501
        :rtype: float
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DSPMetadataIncludedSamples.


        :param id: The id of this DSPMetadataIncludedSamples.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def window_count(self):
        """Gets the window_count of this DSPMetadataIncludedSamples.  # noqa: E501


        :return: The window_count of this DSPMetadataIncludedSamples.  # noqa: E501
        :rtype: float
        """
        return self._window_count

    @window_count.setter
    def window_count(self, window_count):
        """Sets the window_count of this DSPMetadataIncludedSamples.


        :param window_count: The window_count of this DSPMetadataIncludedSamples.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and window_count is None:  # noqa: E501
            raise ValueError("Invalid value for `window_count`, must not be `None`")  # noqa: E501

        self._window_count = window_count

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
        if not isinstance(other, DSPMetadataIncludedSamples):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DSPMetadataIncludedSamples):
            return True

        return self.to_dict() != other.to_dict()
