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


class ProjectInfoResponseAllOf(object):
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
        'project': 'Project',
        'collaborators': 'list[User]',
        'downloads': 'list[Download]',
        'development_keys': 'DevelopmentKeys',
        'impulse': 'ProjectInfoResponseAllOfImpulse',
        'devices': 'list[Device]',
        'data_summary': 'ProjectDataSummary',
        'data_axis_summary': 'dict(str, float)',
        'suggested_sampling_interval': 'float',
        'compute_time': 'ProjectInfoResponseAllOfComputeTime'
    }

    attribute_map = {
        'project': 'project',
        'collaborators': 'collaborators',
        'downloads': 'downloads',
        'development_keys': 'developmentKeys',
        'impulse': 'impulse',
        'devices': 'devices',
        'data_summary': 'dataSummary',
        'data_axis_summary': 'dataAxisSummary',
        'suggested_sampling_interval': 'suggestedSamplingInterval',
        'compute_time': 'computeTime'
    }

    def __init__(self, project=None, collaborators=None, downloads=None, development_keys=None, impulse=None, devices=None, data_summary=None, data_axis_summary=None, suggested_sampling_interval=None, compute_time=None, local_vars_configuration=None):  # noqa: E501
        """ProjectInfoResponseAllOf - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._project = None
        self._collaborators = None
        self._downloads = None
        self._development_keys = None
        self._impulse = None
        self._devices = None
        self._data_summary = None
        self._data_axis_summary = None
        self._suggested_sampling_interval = None
        self._compute_time = None
        self.discriminator = None

        self.project = project
        self.collaborators = collaborators
        self.downloads = downloads
        self.development_keys = development_keys
        self.impulse = impulse
        self.devices = devices
        self.data_summary = data_summary
        self.data_axis_summary = data_axis_summary
        self.suggested_sampling_interval = suggested_sampling_interval
        self.compute_time = compute_time

    @property
    def project(self):
        """Gets the project of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The project of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: Project
        """
        return self._project

    @project.setter
    def project(self, project):
        """Sets the project of this ProjectInfoResponseAllOf.


        :param project: The project of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: Project
        """
        if self.local_vars_configuration.client_side_validation and project is None:  # noqa: E501
            raise ValueError("Invalid value for `project`, must not be `None`")  # noqa: E501

        self._project = project

    @property
    def collaborators(self):
        """Gets the collaborators of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The collaborators of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: list[User]
        """
        return self._collaborators

    @collaborators.setter
    def collaborators(self, collaborators):
        """Sets the collaborators of this ProjectInfoResponseAllOf.


        :param collaborators: The collaborators of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: list[User]
        """
        if self.local_vars_configuration.client_side_validation and collaborators is None:  # noqa: E501
            raise ValueError("Invalid value for `collaborators`, must not be `None`")  # noqa: E501

        self._collaborators = collaborators

    @property
    def downloads(self):
        """Gets the downloads of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The downloads of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: list[Download]
        """
        return self._downloads

    @downloads.setter
    def downloads(self, downloads):
        """Sets the downloads of this ProjectInfoResponseAllOf.


        :param downloads: The downloads of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: list[Download]
        """
        if self.local_vars_configuration.client_side_validation and downloads is None:  # noqa: E501
            raise ValueError("Invalid value for `downloads`, must not be `None`")  # noqa: E501

        self._downloads = downloads

    @property
    def development_keys(self):
        """Gets the development_keys of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The development_keys of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: DevelopmentKeys
        """
        return self._development_keys

    @development_keys.setter
    def development_keys(self, development_keys):
        """Sets the development_keys of this ProjectInfoResponseAllOf.


        :param development_keys: The development_keys of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: DevelopmentKeys
        """
        if self.local_vars_configuration.client_side_validation and development_keys is None:  # noqa: E501
            raise ValueError("Invalid value for `development_keys`, must not be `None`")  # noqa: E501

        self._development_keys = development_keys

    @property
    def impulse(self):
        """Gets the impulse of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The impulse of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: ProjectInfoResponseAllOfImpulse
        """
        return self._impulse

    @impulse.setter
    def impulse(self, impulse):
        """Sets the impulse of this ProjectInfoResponseAllOf.


        :param impulse: The impulse of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: ProjectInfoResponseAllOfImpulse
        """
        if self.local_vars_configuration.client_side_validation and impulse is None:  # noqa: E501
            raise ValueError("Invalid value for `impulse`, must not be `None`")  # noqa: E501

        self._impulse = impulse

    @property
    def devices(self):
        """Gets the devices of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The devices of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: list[Device]
        """
        return self._devices

    @devices.setter
    def devices(self, devices):
        """Sets the devices of this ProjectInfoResponseAllOf.


        :param devices: The devices of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: list[Device]
        """
        if self.local_vars_configuration.client_side_validation and devices is None:  # noqa: E501
            raise ValueError("Invalid value for `devices`, must not be `None`")  # noqa: E501

        self._devices = devices

    @property
    def data_summary(self):
        """Gets the data_summary of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The data_summary of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: ProjectDataSummary
        """
        return self._data_summary

    @data_summary.setter
    def data_summary(self, data_summary):
        """Sets the data_summary of this ProjectInfoResponseAllOf.


        :param data_summary: The data_summary of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: ProjectDataSummary
        """
        if self.local_vars_configuration.client_side_validation and data_summary is None:  # noqa: E501
            raise ValueError("Invalid value for `data_summary`, must not be `None`")  # noqa: E501

        self._data_summary = data_summary

    @property
    def data_axis_summary(self):
        """Gets the data_axis_summary of this ProjectInfoResponseAllOf.  # noqa: E501

        Summary of the amount of data (in ms.) per sensor axis  # noqa: E501

        :return: The data_axis_summary of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: dict(str, float)
        """
        return self._data_axis_summary

    @data_axis_summary.setter
    def data_axis_summary(self, data_axis_summary):
        """Sets the data_axis_summary of this ProjectInfoResponseAllOf.

        Summary of the amount of data (in ms.) per sensor axis  # noqa: E501

        :param data_axis_summary: The data_axis_summary of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: dict(str, float)
        """
        if self.local_vars_configuration.client_side_validation and data_axis_summary is None:  # noqa: E501
            raise ValueError("Invalid value for `data_axis_summary`, must not be `None`")  # noqa: E501

        self._data_axis_summary = data_axis_summary

    @property
    def suggested_sampling_interval(self):
        """Gets the suggested_sampling_interval of this ProjectInfoResponseAllOf.  # noqa: E501

        The suggested interval for new sampling data. This is based on the existing data in your training set.  # noqa: E501

        :return: The suggested_sampling_interval of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: float
        """
        return self._suggested_sampling_interval

    @suggested_sampling_interval.setter
    def suggested_sampling_interval(self, suggested_sampling_interval):
        """Sets the suggested_sampling_interval of this ProjectInfoResponseAllOf.

        The suggested interval for new sampling data. This is based on the existing data in your training set.  # noqa: E501

        :param suggested_sampling_interval: The suggested_sampling_interval of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: float
        """
        if self.local_vars_configuration.client_side_validation and suggested_sampling_interval is None:  # noqa: E501
            raise ValueError("Invalid value for `suggested_sampling_interval`, must not be `None`")  # noqa: E501

        self._suggested_sampling_interval = suggested_sampling_interval

    @property
    def compute_time(self):
        """Gets the compute_time of this ProjectInfoResponseAllOf.  # noqa: E501


        :return: The compute_time of this ProjectInfoResponseAllOf.  # noqa: E501
        :rtype: ProjectInfoResponseAllOfComputeTime
        """
        return self._compute_time

    @compute_time.setter
    def compute_time(self, compute_time):
        """Sets the compute_time of this ProjectInfoResponseAllOf.


        :param compute_time: The compute_time of this ProjectInfoResponseAllOf.  # noqa: E501
        :type: ProjectInfoResponseAllOfComputeTime
        """
        if self.local_vars_configuration.client_side_validation and compute_time is None:  # noqa: E501
            raise ValueError("Invalid value for `compute_time`, must not be `None`")  # noqa: E501

        self._compute_time = compute_time

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
        if not isinstance(other, ProjectInfoResponseAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectInfoResponseAllOf):
            return True

        return self.to_dict() != other.to_dict()
