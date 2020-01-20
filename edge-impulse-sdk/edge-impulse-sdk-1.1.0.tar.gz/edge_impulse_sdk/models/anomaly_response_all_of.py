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


class AnomalyResponseAllOf(object):
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
        'dependencies': 'DependencyData',
        'name': 'str',
        'axes': 'list[AnomalyResponseAllOfAxes]',
        'trained': 'bool',
        'cluster_count': 'float',
        'selected_axes': 'list[float]',
        'minimum_confidence_rating': 'float'
    }

    attribute_map = {
        'dependencies': 'dependencies',
        'name': 'name',
        'axes': 'axes',
        'trained': 'trained',
        'cluster_count': 'clusterCount',
        'selected_axes': 'selectedAxes',
        'minimum_confidence_rating': 'minimumConfidenceRating'
    }

    def __init__(self, dependencies=None, name=None, axes=None, trained=None, cluster_count=None, selected_axes=None, minimum_confidence_rating=None, local_vars_configuration=None):  # noqa: E501
        """AnomalyResponseAllOf - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._dependencies = None
        self._name = None
        self._axes = None
        self._trained = None
        self._cluster_count = None
        self._selected_axes = None
        self._minimum_confidence_rating = None
        self.discriminator = None

        self.dependencies = dependencies
        self.name = name
        self.axes = axes
        self.trained = trained
        self.cluster_count = cluster_count
        self.selected_axes = selected_axes
        self.minimum_confidence_rating = minimum_confidence_rating

    @property
    def dependencies(self):
        """Gets the dependencies of this AnomalyResponseAllOf.  # noqa: E501


        :return: The dependencies of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: DependencyData
        """
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        """Sets the dependencies of this AnomalyResponseAllOf.


        :param dependencies: The dependencies of this AnomalyResponseAllOf.  # noqa: E501
        :type: DependencyData
        """
        if self.local_vars_configuration.client_side_validation and dependencies is None:  # noqa: E501
            raise ValueError("Invalid value for `dependencies`, must not be `None`")  # noqa: E501

        self._dependencies = dependencies

    @property
    def name(self):
        """Gets the name of this AnomalyResponseAllOf.  # noqa: E501


        :return: The name of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AnomalyResponseAllOf.


        :param name: The name of this AnomalyResponseAllOf.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def axes(self):
        """Gets the axes of this AnomalyResponseAllOf.  # noqa: E501

        Selectable axes for the anomaly detection block  # noqa: E501

        :return: The axes of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: list[AnomalyResponseAllOfAxes]
        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        """Sets the axes of this AnomalyResponseAllOf.

        Selectable axes for the anomaly detection block  # noqa: E501

        :param axes: The axes of this AnomalyResponseAllOf.  # noqa: E501
        :type: list[AnomalyResponseAllOfAxes]
        """
        if self.local_vars_configuration.client_side_validation and axes is None:  # noqa: E501
            raise ValueError("Invalid value for `axes`, must not be `None`")  # noqa: E501

        self._axes = axes

    @property
    def trained(self):
        """Gets the trained of this AnomalyResponseAllOf.  # noqa: E501

        Whether the block is trained  # noqa: E501

        :return: The trained of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: bool
        """
        return self._trained

    @trained.setter
    def trained(self, trained):
        """Sets the trained of this AnomalyResponseAllOf.

        Whether the block is trained  # noqa: E501

        :param trained: The trained of this AnomalyResponseAllOf.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and trained is None:  # noqa: E501
            raise ValueError("Invalid value for `trained`, must not be `None`")  # noqa: E501

        self._trained = trained

    @property
    def cluster_count(self):
        """Gets the cluster_count of this AnomalyResponseAllOf.  # noqa: E501

        Number of clusters (in config)  # noqa: E501

        :return: The cluster_count of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._cluster_count

    @cluster_count.setter
    def cluster_count(self, cluster_count):
        """Sets the cluster_count of this AnomalyResponseAllOf.

        Number of clusters (in config)  # noqa: E501

        :param cluster_count: The cluster_count of this AnomalyResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and cluster_count is None:  # noqa: E501
            raise ValueError("Invalid value for `cluster_count`, must not be `None`")  # noqa: E501

        self._cluster_count = cluster_count

    @property
    def selected_axes(self):
        """Gets the selected_axes of this AnomalyResponseAllOf.  # noqa: E501

        Selected clusters (in config)  # noqa: E501

        :return: The selected_axes of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: list[float]
        """
        return self._selected_axes

    @selected_axes.setter
    def selected_axes(self, selected_axes):
        """Sets the selected_axes of this AnomalyResponseAllOf.

        Selected clusters (in config)  # noqa: E501

        :param selected_axes: The selected_axes of this AnomalyResponseAllOf.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and selected_axes is None:  # noqa: E501
            raise ValueError("Invalid value for `selected_axes`, must not be `None`")  # noqa: E501

        self._selected_axes = selected_axes

    @property
    def minimum_confidence_rating(self):
        """Gets the minimum_confidence_rating of this AnomalyResponseAllOf.  # noqa: E501

        Minimum confidence rating for this block, scores above this number will be flagged as anomaly.  # noqa: E501

        :return: The minimum_confidence_rating of this AnomalyResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._minimum_confidence_rating

    @minimum_confidence_rating.setter
    def minimum_confidence_rating(self, minimum_confidence_rating):
        """Sets the minimum_confidence_rating of this AnomalyResponseAllOf.

        Minimum confidence rating for this block, scores above this number will be flagged as anomaly.  # noqa: E501

        :param minimum_confidence_rating: The minimum_confidence_rating of this AnomalyResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and minimum_confidence_rating is None:  # noqa: E501
            raise ValueError("Invalid value for `minimum_confidence_rating`, must not be `None`")  # noqa: E501

        self._minimum_confidence_rating = minimum_confidence_rating

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
        if not isinstance(other, AnomalyResponseAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AnomalyResponseAllOf):
            return True

        return self.to_dict() != other.to_dict()
