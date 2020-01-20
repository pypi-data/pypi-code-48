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


class DspTrainedFeaturesResponse(object):
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
        'success': 'bool',
        'error': 'str',
        'total_sample_count': 'float',
        'data': 'list[DspTrainedFeaturesResponseAllOfData]'
    }

    attribute_map = {
        'success': 'success',
        'error': 'error',
        'total_sample_count': 'totalSampleCount',
        'data': 'data'
    }

    def __init__(self, success=None, error=None, total_sample_count=None, data=None, local_vars_configuration=None):  # noqa: E501
        """DspTrainedFeaturesResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._success = None
        self._error = None
        self._total_sample_count = None
        self._data = None
        self.discriminator = None

        self.success = success
        if error is not None:
            self.error = error
        self.total_sample_count = total_sample_count
        self.data = data

    @property
    def success(self):
        """Gets the success of this DspTrainedFeaturesResponse.  # noqa: E501

        Whether the operation succeeded  # noqa: E501

        :return: The success of this DspTrainedFeaturesResponse.  # noqa: E501
        :rtype: bool
        """
        return self._success

    @success.setter
    def success(self, success):
        """Sets the success of this DspTrainedFeaturesResponse.

        Whether the operation succeeded  # noqa: E501

        :param success: The success of this DspTrainedFeaturesResponse.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and success is None:  # noqa: E501
            raise ValueError("Invalid value for `success`, must not be `None`")  # noqa: E501

        self._success = success

    @property
    def error(self):
        """Gets the error of this DspTrainedFeaturesResponse.  # noqa: E501

        Optional error description (set if 'success' was false)  # noqa: E501

        :return: The error of this DspTrainedFeaturesResponse.  # noqa: E501
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this DspTrainedFeaturesResponse.

        Optional error description (set if 'success' was false)  # noqa: E501

        :param error: The error of this DspTrainedFeaturesResponse.  # noqa: E501
        :type: str
        """

        self._error = error

    @property
    def total_sample_count(self):
        """Gets the total_sample_count of this DspTrainedFeaturesResponse.  # noqa: E501

        Total number of windows in the data set  # noqa: E501

        :return: The total_sample_count of this DspTrainedFeaturesResponse.  # noqa: E501
        :rtype: float
        """
        return self._total_sample_count

    @total_sample_count.setter
    def total_sample_count(self, total_sample_count):
        """Sets the total_sample_count of this DspTrainedFeaturesResponse.

        Total number of windows in the data set  # noqa: E501

        :param total_sample_count: The total_sample_count of this DspTrainedFeaturesResponse.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and total_sample_count is None:  # noqa: E501
            raise ValueError("Invalid value for `total_sample_count`, must not be `None`")  # noqa: E501

        self._total_sample_count = total_sample_count

    @property
    def data(self):
        """Gets the data of this DspTrainedFeaturesResponse.  # noqa: E501


        :return: The data of this DspTrainedFeaturesResponse.  # noqa: E501
        :rtype: list[DspTrainedFeaturesResponseAllOfData]
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this DspTrainedFeaturesResponse.


        :param data: The data of this DspTrainedFeaturesResponse.  # noqa: E501
        :type: list[DspTrainedFeaturesResponseAllOfData]
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
        if not isinstance(other, DspTrainedFeaturesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DspTrainedFeaturesResponse):
            return True

        return self.to_dict() != other.to_dict()
