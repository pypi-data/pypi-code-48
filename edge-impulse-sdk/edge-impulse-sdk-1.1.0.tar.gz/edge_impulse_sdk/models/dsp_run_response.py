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


class DspRunResponse(object):
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
        'features': 'list[float]',
        'graphs': 'list[DspRunGraph]',
        'labels': 'list[str]'
    }

    attribute_map = {
        'success': 'success',
        'error': 'error',
        'features': 'features',
        'graphs': 'graphs',
        'labels': 'labels'
    }

    def __init__(self, success=None, error=None, features=None, graphs=None, labels=None, local_vars_configuration=None):  # noqa: E501
        """DspRunResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._success = None
        self._error = None
        self._features = None
        self._graphs = None
        self._labels = None
        self.discriminator = None

        self.success = success
        if error is not None:
            self.error = error
        self.features = features
        self.graphs = graphs
        self.labels = labels

    @property
    def success(self):
        """Gets the success of this DspRunResponse.  # noqa: E501

        Whether the operation succeeded  # noqa: E501

        :return: The success of this DspRunResponse.  # noqa: E501
        :rtype: bool
        """
        return self._success

    @success.setter
    def success(self, success):
        """Sets the success of this DspRunResponse.

        Whether the operation succeeded  # noqa: E501

        :param success: The success of this DspRunResponse.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and success is None:  # noqa: E501
            raise ValueError("Invalid value for `success`, must not be `None`")  # noqa: E501

        self._success = success

    @property
    def error(self):
        """Gets the error of this DspRunResponse.  # noqa: E501

        Optional error description (set if 'success' was false)  # noqa: E501

        :return: The error of this DspRunResponse.  # noqa: E501
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this DspRunResponse.

        Optional error description (set if 'success' was false)  # noqa: E501

        :param error: The error of this DspRunResponse.  # noqa: E501
        :type: str
        """

        self._error = error

    @property
    def features(self):
        """Gets the features of this DspRunResponse.  # noqa: E501

        Array of processed features. Laid out according to the names in 'labels'  # noqa: E501

        :return: The features of this DspRunResponse.  # noqa: E501
        :rtype: list[float]
        """
        return self._features

    @features.setter
    def features(self, features):
        """Sets the features of this DspRunResponse.

        Array of processed features. Laid out according to the names in 'labels'  # noqa: E501

        :param features: The features of this DspRunResponse.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and features is None:  # noqa: E501
            raise ValueError("Invalid value for `features`, must not be `None`")  # noqa: E501

        self._features = features

    @property
    def graphs(self):
        """Gets the graphs of this DspRunResponse.  # noqa: E501

        Graphs to plot to give an insight in how the DSP process ran  # noqa: E501

        :return: The graphs of this DspRunResponse.  # noqa: E501
        :rtype: list[DspRunGraph]
        """
        return self._graphs

    @graphs.setter
    def graphs(self, graphs):
        """Sets the graphs of this DspRunResponse.

        Graphs to plot to give an insight in how the DSP process ran  # noqa: E501

        :param graphs: The graphs of this DspRunResponse.  # noqa: E501
        :type: list[DspRunGraph]
        """
        if self.local_vars_configuration.client_side_validation and graphs is None:  # noqa: E501
            raise ValueError("Invalid value for `graphs`, must not be `None`")  # noqa: E501

        self._graphs = graphs

    @property
    def labels(self):
        """Gets the labels of this DspRunResponse.  # noqa: E501

        Labels of the feature axes  # noqa: E501

        :return: The labels of this DspRunResponse.  # noqa: E501
        :rtype: list[str]
        """
        return self._labels

    @labels.setter
    def labels(self, labels):
        """Sets the labels of this DspRunResponse.

        Labels of the feature axes  # noqa: E501

        :param labels: The labels of this DspRunResponse.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and labels is None:  # noqa: E501
            raise ValueError("Invalid value for `labels`, must not be `None`")  # noqa: E501

        self._labels = labels

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
        if not isinstance(other, DspRunResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DspRunResponse):
            return True

        return self.to_dict() != other.to_dict()
