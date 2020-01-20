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


class DspSampleFeaturesResponseAllOf(object):
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
        'total_sample_count': 'float',
        'data': 'list[DspSampleFeaturesResponseAllOfData]'
    }

    attribute_map = {
        'total_sample_count': 'totalSampleCount',
        'data': 'data'
    }

    def __init__(self, total_sample_count=None, data=None, local_vars_configuration=None):  # noqa: E501
        """DspSampleFeaturesResponseAllOf - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._total_sample_count = None
        self._data = None
        self.discriminator = None

        self.total_sample_count = total_sample_count
        self.data = data

    @property
    def total_sample_count(self):
        """Gets the total_sample_count of this DspSampleFeaturesResponseAllOf.  # noqa: E501

        Total number of windows in the data set  # noqa: E501

        :return: The total_sample_count of this DspSampleFeaturesResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._total_sample_count

    @total_sample_count.setter
    def total_sample_count(self, total_sample_count):
        """Sets the total_sample_count of this DspSampleFeaturesResponseAllOf.

        Total number of windows in the data set  # noqa: E501

        :param total_sample_count: The total_sample_count of this DspSampleFeaturesResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and total_sample_count is None:  # noqa: E501
            raise ValueError("Invalid value for `total_sample_count`, must not be `None`")  # noqa: E501

        self._total_sample_count = total_sample_count

    @property
    def data(self):
        """Gets the data of this DspSampleFeaturesResponseAllOf.  # noqa: E501


        :return: The data of this DspSampleFeaturesResponseAllOf.  # noqa: E501
        :rtype: list[DspSampleFeaturesResponseAllOfData]
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this DspSampleFeaturesResponseAllOf.


        :param data: The data of this DspSampleFeaturesResponseAllOf.  # noqa: E501
        :type: list[DspSampleFeaturesResponseAllOfData]
        """
        if self.local_vars_configuration.client_side_validation and data is None:  # noqa: E501
            raise ValueError("Invalid value for `data`, must not be `None`")  # noqa: E501

        self._data = data

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
        if not isinstance(other, DspSampleFeaturesResponseAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DspSampleFeaturesResponseAllOf):
            return True

        return self.to_dict() != other.to_dict()
