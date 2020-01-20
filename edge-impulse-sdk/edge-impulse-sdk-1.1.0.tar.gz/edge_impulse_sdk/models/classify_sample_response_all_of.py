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


class ClassifySampleResponseAllOf(object):
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
        'classifications': 'list[ClassifySampleResponseAllOfClassifications]',
        'sample': 'RawSampleData',
        'window_size_ms': 'float',
        'window_increase_ms': 'float',
        'already_in_database': 'bool'
    }

    attribute_map = {
        'classifications': 'classifications',
        'sample': 'sample',
        'window_size_ms': 'windowSizeMs',
        'window_increase_ms': 'windowIncreaseMs',
        'already_in_database': 'alreadyInDatabase'
    }

    def __init__(self, classifications=None, sample=None, window_size_ms=None, window_increase_ms=None, already_in_database=None, local_vars_configuration=None):  # noqa: E501
        """ClassifySampleResponseAllOf - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._classifications = None
        self._sample = None
        self._window_size_ms = None
        self._window_increase_ms = None
        self._already_in_database = None
        self.discriminator = None

        self.classifications = classifications
        self.sample = sample
        self.window_size_ms = window_size_ms
        self.window_increase_ms = window_increase_ms
        self.already_in_database = already_in_database

    @property
    def classifications(self):
        """Gets the classifications of this ClassifySampleResponseAllOf.  # noqa: E501


        :return: The classifications of this ClassifySampleResponseAllOf.  # noqa: E501
        :rtype: list[ClassifySampleResponseAllOfClassifications]
        """
        return self._classifications

    @classifications.setter
    def classifications(self, classifications):
        """Sets the classifications of this ClassifySampleResponseAllOf.


        :param classifications: The classifications of this ClassifySampleResponseAllOf.  # noqa: E501
        :type: list[ClassifySampleResponseAllOfClassifications]
        """
        if self.local_vars_configuration.client_side_validation and classifications is None:  # noqa: E501
            raise ValueError("Invalid value for `classifications`, must not be `None`")  # noqa: E501

        self._classifications = classifications

    @property
    def sample(self):
        """Gets the sample of this ClassifySampleResponseAllOf.  # noqa: E501


        :return: The sample of this ClassifySampleResponseAllOf.  # noqa: E501
        :rtype: RawSampleData
        """
        return self._sample

    @sample.setter
    def sample(self, sample):
        """Sets the sample of this ClassifySampleResponseAllOf.


        :param sample: The sample of this ClassifySampleResponseAllOf.  # noqa: E501
        :type: RawSampleData
        """
        if self.local_vars_configuration.client_side_validation and sample is None:  # noqa: E501
            raise ValueError("Invalid value for `sample`, must not be `None`")  # noqa: E501

        self._sample = sample

    @property
    def window_size_ms(self):
        """Gets the window_size_ms of this ClassifySampleResponseAllOf.  # noqa: E501

        Size of the sliding window (as set by the impulse) in milliseconds.  # noqa: E501

        :return: The window_size_ms of this ClassifySampleResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._window_size_ms

    @window_size_ms.setter
    def window_size_ms(self, window_size_ms):
        """Sets the window_size_ms of this ClassifySampleResponseAllOf.

        Size of the sliding window (as set by the impulse) in milliseconds.  # noqa: E501

        :param window_size_ms: The window_size_ms of this ClassifySampleResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and window_size_ms is None:  # noqa: E501
            raise ValueError("Invalid value for `window_size_ms`, must not be `None`")  # noqa: E501

        self._window_size_ms = window_size_ms

    @property
    def window_increase_ms(self):
        """Gets the window_increase_ms of this ClassifySampleResponseAllOf.  # noqa: E501

        Number of milliseconds that the sliding window increased with (as set by the impulse)  # noqa: E501

        :return: The window_increase_ms of this ClassifySampleResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._window_increase_ms

    @window_increase_ms.setter
    def window_increase_ms(self, window_increase_ms):
        """Sets the window_increase_ms of this ClassifySampleResponseAllOf.

        Number of milliseconds that the sliding window increased with (as set by the impulse)  # noqa: E501

        :param window_increase_ms: The window_increase_ms of this ClassifySampleResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and window_increase_ms is None:  # noqa: E501
            raise ValueError("Invalid value for `window_increase_ms`, must not be `None`")  # noqa: E501

        self._window_increase_ms = window_increase_ms

    @property
    def already_in_database(self):
        """Gets the already_in_database of this ClassifySampleResponseAllOf.  # noqa: E501

        Whether this sample is already in the training database  # noqa: E501

        :return: The already_in_database of this ClassifySampleResponseAllOf.  # noqa: E501
        :rtype: bool
        """
        return self._already_in_database

    @already_in_database.setter
    def already_in_database(self, already_in_database):
        """Sets the already_in_database of this ClassifySampleResponseAllOf.

        Whether this sample is already in the training database  # noqa: E501

        :param already_in_database: The already_in_database of this ClassifySampleResponseAllOf.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and already_in_database is None:  # noqa: E501
            raise ValueError("Invalid value for `already_in_database`, must not be `None`")  # noqa: E501

        self._already_in_database = already_in_database

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
        if not isinstance(other, ClassifySampleResponseAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ClassifySampleResponseAllOf):
            return True

        return self.to_dict() != other.to_dict()
