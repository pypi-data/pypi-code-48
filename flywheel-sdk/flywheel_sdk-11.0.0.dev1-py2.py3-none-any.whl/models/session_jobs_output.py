# coding: utf-8

"""
    Flywheel

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 11.0.0-dev.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


## NOTE: This file is auto generated by the swagger code generator program.
## Do not edit the file manually.

import pprint
import re  # noqa: F401

import six

from flywheel.models.job import Job  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.


class SessionJobsOutput(object):

    swagger_types = {
        'jobs': 'list[Job]',
        'containers': 'dict(str, object)'
    }

    attribute_map = {
        'jobs': 'jobs',
        'containers': 'containers'
    }

    rattribute_map = {
        'jobs': 'jobs',
        'containers': 'containers'
    }

    def __init__(self, jobs=None, containers=None):  # noqa: E501
        """SessionJobsOutput - a model defined in Swagger"""
        super(SessionJobsOutput, self).__init__()

        self._jobs = None
        self._containers = None
        self.discriminator = None
        self.alt_discriminator = None

        if jobs is not None:
            self.jobs = jobs
        if containers is not None:
            self.containers = containers

    @property
    def jobs(self):
        """Gets the jobs of this SessionJobsOutput.


        :return: The jobs of this SessionJobsOutput.
        :rtype: list[Job]
        """
        return self._jobs

    @jobs.setter
    def jobs(self, jobs):
        """Sets the jobs of this SessionJobsOutput.


        :param jobs: The jobs of this SessionJobsOutput.  # noqa: E501
        :type: list[Job]
        """

        self._jobs = jobs

    @property
    def containers(self):
        """Gets the containers of this SessionJobsOutput.


        :return: The containers of this SessionJobsOutput.
        :rtype: dict(str, object)
        """
        return self._containers

    @containers.setter
    def containers(self, containers):
        """Sets the containers of this SessionJobsOutput.


        :param containers: The containers of this SessionJobsOutput.  # noqa: E501
        :type: dict(str, object)
        """

        self._containers = containers


    @staticmethod
    def positional_to_model(value):
        """Converts a positional argument to a model value"""
        return value

    def return_value(self):
        """Unwraps return value from model"""
        return self

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if not isinstance(other, SessionJobsOutput):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

    # Container emulation
    def __getitem__(self, key):
        """Returns the value of key"""
        key = self._map_key(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Sets the value of key"""
        key = self._map_key(key)
        setattr(self, key, value)

    def __contains__(self, key):
        """Checks if the given value is a key in this object"""
        key = self._map_key(key, raise_on_error=False)
        return key is not None

    def keys(self):
        """Returns the list of json properties in the object"""
        return self.__class__.rattribute_map.keys()

    def values(self):
        """Returns the list of values in the object"""
        for key in self.__class__.attribute_map.keys():
            yield getattr(self, key)

    def items(self):
        """Returns the list of json property to value mapping"""
        for key, prop in self.__class__.rattribute_map.items():
            yield key, getattr(self, prop)

    def get(self, key, default=None):
        """Get the value of the provided json property, or default"""
        key = self._map_key(key, raise_on_error=False)
        if key:
            return getattr(self, key, default)
        return default

    def _map_key(self, key, raise_on_error=True):
        result = self.__class__.rattribute_map.get(key)
        if result is None:
            if raise_on_error:
                raise AttributeError('Invalid attribute name: {}'.format(key))
            return None
        return '_' + result
