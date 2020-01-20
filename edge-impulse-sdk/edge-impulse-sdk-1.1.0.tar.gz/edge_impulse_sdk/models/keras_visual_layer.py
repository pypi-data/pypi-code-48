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


class KerasVisualLayer(object):
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
        'type': 'str',
        'neurons': 'float',
        'kernel_size': 'float',
        'columns': 'float'
    }

    attribute_map = {
        'type': 'type',
        'neurons': 'neurons',
        'kernel_size': 'kernelSize',
        'columns': 'columns'
    }

    def __init__(self, type=None, neurons=None, kernel_size=None, columns=None, local_vars_configuration=None):  # noqa: E501
        """KerasVisualLayer - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._neurons = None
        self._kernel_size = None
        self._columns = None
        self.discriminator = None

        self.type = type
        if neurons is not None:
            self.neurons = neurons
        if kernel_size is not None:
            self.kernel_size = kernel_size
        if columns is not None:
            self.columns = columns

    @property
    def type(self):
        """Gets the type of this KerasVisualLayer.  # noqa: E501


        :return: The type of this KerasVisualLayer.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this KerasVisualLayer.


        :param type: The type of this KerasVisualLayer.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["dense", "conv1d", "reshape", "flatten"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def neurons(self):
        """Gets the neurons of this KerasVisualLayer.  # noqa: E501

        Number of neurons in this layer (only for dense, conv1d)  # noqa: E501

        :return: The neurons of this KerasVisualLayer.  # noqa: E501
        :rtype: float
        """
        return self._neurons

    @neurons.setter
    def neurons(self, neurons):
        """Sets the neurons of this KerasVisualLayer.

        Number of neurons in this layer (only for dense, conv1d)  # noqa: E501

        :param neurons: The neurons of this KerasVisualLayer.  # noqa: E501
        :type: float
        """

        self._neurons = neurons

    @property
    def kernel_size(self):
        """Gets the kernel_size of this KerasVisualLayer.  # noqa: E501

        Kernel size for the convolutional and pooling layer (only for conv1d)  # noqa: E501

        :return: The kernel_size of this KerasVisualLayer.  # noqa: E501
        :rtype: float
        """
        return self._kernel_size

    @kernel_size.setter
    def kernel_size(self, kernel_size):
        """Sets the kernel_size of this KerasVisualLayer.

        Kernel size for the convolutional and pooling layer (only for conv1d)  # noqa: E501

        :param kernel_size: The kernel_size of this KerasVisualLayer.  # noqa: E501
        :type: float
        """

        self._kernel_size = kernel_size

    @property
    def columns(self):
        """Gets the columns of this KerasVisualLayer.  # noqa: E501

        Number of columns for the reshape operation (only for reshape)  # noqa: E501

        :return: The columns of this KerasVisualLayer.  # noqa: E501
        :rtype: float
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """Sets the columns of this KerasVisualLayer.

        Number of columns for the reshape operation (only for reshape)  # noqa: E501

        :param columns: The columns of this KerasVisualLayer.  # noqa: E501
        :type: float
        """

        self._columns = columns

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
        if not isinstance(other, KerasVisualLayer):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, KerasVisualLayer):
            return True

        return self.to_dict() != other.to_dict()
