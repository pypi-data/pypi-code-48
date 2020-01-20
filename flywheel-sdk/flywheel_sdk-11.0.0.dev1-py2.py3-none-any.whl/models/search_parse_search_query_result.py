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

from flywheel.models.search_parse_error import SearchParseError  # noqa: F401,E501

# NOTE: This file is auto generated by the swagger code generator program.
# Do not edit the class manually.


class SearchParseSearchQueryResult(object):

    swagger_types = {
        'valid': 'bool',
        'errors': 'list[SearchParseError]'
    }

    attribute_map = {
        'valid': 'valid',
        'errors': 'errors'
    }

    rattribute_map = {
        'valid': 'valid',
        'errors': 'errors'
    }

    def __init__(self, valid=None, errors=None):  # noqa: E501
        """SearchParseSearchQueryResult - a model defined in Swagger"""
        super(SearchParseSearchQueryResult, self).__init__()

        self._valid = None
        self._errors = None
        self.discriminator = None
        self.alt_discriminator = None

        self.valid = valid
        if errors is not None:
            self.errors = errors

    @property
    def valid(self):
        """Gets the valid of this SearchParseSearchQueryResult.

        Whether the structured query was valid or not

        :return: The valid of this SearchParseSearchQueryResult.
        :rtype: bool
        """
        return self._valid

    @valid.setter
    def valid(self, valid):
        """Sets the valid of this SearchParseSearchQueryResult.

        Whether the structured query was valid or not

        :param valid: The valid of this SearchParseSearchQueryResult.  # noqa: E501
        :type: bool
        """

        self._valid = valid

    @property
    def errors(self):
        """Gets the errors of this SearchParseSearchQueryResult.


        :return: The errors of this SearchParseSearchQueryResult.
        :rtype: list[SearchParseError]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this SearchParseSearchQueryResult.


        :param errors: The errors of this SearchParseSearchQueryResult.  # noqa: E501
        :type: list[SearchParseError]
        """

        self._errors = errors


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
        if not isinstance(other, SearchParseSearchQueryResult):
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
