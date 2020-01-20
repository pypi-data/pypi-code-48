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

from flywheel.models.common_classification import CommonClassification  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.

from .mixins import FileMixin

class SearchFileResponse(FileMixin):

    swagger_types = {
        'classification': 'CommonClassification',
        'created': 'datetime',
        'type': 'str',
        'name': 'str',
        'size': 'int'
    }

    attribute_map = {
        'classification': 'classification',
        'created': 'created',
        'type': 'type',
        'name': 'name',
        'size': 'size'
    }

    rattribute_map = {
        'classification': 'classification',
        'created': 'created',
        'type': 'type',
        'name': 'name',
        'size': 'size'
    }

    def __init__(self, classification=None, created=None, type=None, name=None, size=None):  # noqa: E501
        """SearchFileResponse - a model defined in Swagger"""
        super(SearchFileResponse, self).__init__()

        self._classification = None
        self._created = None
        self._type = None
        self._name = None
        self._size = None
        self.discriminator = None
        self.alt_discriminator = None

        if classification is not None:
            self.classification = classification
        if created is not None:
            self.created = created
        if type is not None:
            self.type = type
        if name is not None:
            self.name = name
        if size is not None:
            self.size = size

    @property
    def classification(self):
        """Gets the classification of this SearchFileResponse.


        :return: The classification of this SearchFileResponse.
        :rtype: CommonClassification
        """
        return self._classification

    @classification.setter
    def classification(self, classification):
        """Sets the classification of this SearchFileResponse.


        :param classification: The classification of this SearchFileResponse.  # noqa: E501
        :type: CommonClassification
        """

        self._classification = classification

    @property
    def created(self):
        """Gets the created of this SearchFileResponse.

        Creation time (automatically set)

        :return: The created of this SearchFileResponse.
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this SearchFileResponse.

        Creation time (automatically set)

        :param created: The created of this SearchFileResponse.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def type(self):
        """Gets the type of this SearchFileResponse.

        A descriptive file type (e.g. dicom, image, document, ...)

        :return: The type of this SearchFileResponse.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this SearchFileResponse.

        A descriptive file type (e.g. dicom, image, document, ...)

        :param type: The type of this SearchFileResponse.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def name(self):
        """Gets the name of this SearchFileResponse.

        The name of the file on disk

        :return: The name of this SearchFileResponse.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SearchFileResponse.

        The name of the file on disk

        :param name: The name of this SearchFileResponse.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def size(self):
        """Gets the size of this SearchFileResponse.

        Size of the file, in bytes

        :return: The size of this SearchFileResponse.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this SearchFileResponse.

        Size of the file, in bytes

        :param size: The size of this SearchFileResponse.  # noqa: E501
        :type: int
        """

        self._size = size


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
        if not isinstance(other, SearchFileResponse):
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
