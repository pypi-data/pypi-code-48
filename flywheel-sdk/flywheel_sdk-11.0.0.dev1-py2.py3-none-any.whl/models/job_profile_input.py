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

from flywheel.models.job_executor_info import JobExecutorInfo  # noqa: F401,E501
from flywheel.models.job_version_info import JobVersionInfo  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.


class JobProfileInput(object):

    swagger_types = {
        'preparation_time_ms': 'int',
        'elapsed_time_ms': 'int',
        'upload_time_ms': 'int',
        'versions': 'JobVersionInfo',
        'executor': 'JobExecutorInfo'
    }

    attribute_map = {
        'preparation_time_ms': 'preparation_time_ms',
        'elapsed_time_ms': 'elapsed_time_ms',
        'upload_time_ms': 'upload_time_ms',
        'versions': 'versions',
        'executor': 'executor'
    }

    rattribute_map = {
        'preparation_time_ms': 'preparation_time_ms',
        'elapsed_time_ms': 'elapsed_time_ms',
        'upload_time_ms': 'upload_time_ms',
        'versions': 'versions',
        'executor': 'executor'
    }

    def __init__(self, preparation_time_ms=None, elapsed_time_ms=None, upload_time_ms=None, versions=None, executor=None):  # noqa: E501
        """JobProfileInput - a model defined in Swagger"""
        super(JobProfileInput, self).__init__()

        self._preparation_time_ms = None
        self._elapsed_time_ms = None
        self._upload_time_ms = None
        self._versions = None
        self._executor = None
        self.discriminator = None
        self.alt_discriminator = None

        if preparation_time_ms is not None:
            self.preparation_time_ms = preparation_time_ms
        if elapsed_time_ms is not None:
            self.elapsed_time_ms = elapsed_time_ms
        if upload_time_ms is not None:
            self.upload_time_ms = upload_time_ms
        if versions is not None:
            self.versions = versions
        if executor is not None:
            self.executor = executor

    @property
    def preparation_time_ms(self):
        """Gets the preparation_time_ms of this JobProfileInput.

        The length of time taken to download gear container and inputs, in milliseconds

        :return: The preparation_time_ms of this JobProfileInput.
        :rtype: int
        """
        return self._preparation_time_ms

    @preparation_time_ms.setter
    def preparation_time_ms(self, preparation_time_ms):
        """Sets the preparation_time_ms of this JobProfileInput.

        The length of time taken to download gear container and inputs, in milliseconds

        :param preparation_time_ms: The preparation_time_ms of this JobProfileInput.  # noqa: E501
        :type: int
        """

        self._preparation_time_ms = preparation_time_ms

    @property
    def elapsed_time_ms(self):
        """Gets the elapsed_time_ms of this JobProfileInput.

        The runtime of the job, in milliseconds

        :return: The elapsed_time_ms of this JobProfileInput.
        :rtype: int
        """
        return self._elapsed_time_ms

    @elapsed_time_ms.setter
    def elapsed_time_ms(self, elapsed_time_ms):
        """Sets the elapsed_time_ms of this JobProfileInput.

        The runtime of the job, in milliseconds

        :param elapsed_time_ms: The elapsed_time_ms of this JobProfileInput.  # noqa: E501
        :type: int
        """

        self._elapsed_time_ms = elapsed_time_ms

    @property
    def upload_time_ms(self):
        """Gets the upload_time_ms of this JobProfileInput.

        The length of time taken to upload the job's outputs, in milliseconds

        :return: The upload_time_ms of this JobProfileInput.
        :rtype: int
        """
        return self._upload_time_ms

    @upload_time_ms.setter
    def upload_time_ms(self, upload_time_ms):
        """Sets the upload_time_ms of this JobProfileInput.

        The length of time taken to upload the job's outputs, in milliseconds

        :param upload_time_ms: The upload_time_ms of this JobProfileInput.  # noqa: E501
        :type: int
        """

        self._upload_time_ms = upload_time_ms

    @property
    def versions(self):
        """Gets the versions of this JobProfileInput.


        :return: The versions of this JobProfileInput.
        :rtype: JobVersionInfo
        """
        return self._versions

    @versions.setter
    def versions(self, versions):
        """Sets the versions of this JobProfileInput.


        :param versions: The versions of this JobProfileInput.  # noqa: E501
        :type: JobVersionInfo
        """

        self._versions = versions

    @property
    def executor(self):
        """Gets the executor of this JobProfileInput.


        :return: The executor of this JobProfileInput.
        :rtype: JobExecutorInfo
        """
        return self._executor

    @executor.setter
    def executor(self, executor):
        """Sets the executor of this JobProfileInput.


        :param executor: The executor of this JobProfileInput.  # noqa: E501
        :type: JobExecutorInfo
        """

        self._executor = executor


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
        if not isinstance(other, JobProfileInput):
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
