# coding: utf-8

"""
    Seeq REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 0.45.01
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class ExportItemV1(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'end': 'str',
        'id': 'str',
        'name': 'str',
        'start': 'str'
    }

    attribute_map = {
        'end': 'end',
        'id': 'id',
        'name': 'name',
        'start': 'start'
    }

    def __init__(self, end=None, id=None, name=None, start=None):
        """
        ExportItemV1 - a model defined in Swagger
        """

        self._end = None
        self._id = None
        self._name = None
        self._start = None

        if end is not None:
          self.end = end
        if id is not None:
          self.id = id
        if name is not None:
          self.name = name
        if start is not None:
          self.start = start

    @property
    def end(self):
        """
        Gets the end of this ExportItemV1.
        The ISO 8601 end time

        :return: The end of this ExportItemV1.
        :rtype: str
        """
        return self._end

    @end.setter
    def end(self, end):
        """
        Sets the end of this ExportItemV1.
        The ISO 8601 end time

        :param end: The end of this ExportItemV1.
        :type: str
        """
        if end is None:
            raise ValueError("Invalid value for `end`, must not be `None`")

        self._end = end

    @property
    def id(self):
        """
        Gets the id of this ExportItemV1.
        The unique id of a signal or condition

        :return: The id of this ExportItemV1.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this ExportItemV1.
        The unique id of a signal or condition

        :param id: The id of this ExportItemV1.
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")

        self._id = id

    @property
    def name(self):
        """
        Gets the name of this ExportItemV1.
        Human readable name. Null or whitespace names are not permitted.

        :return: The name of this ExportItemV1.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this ExportItemV1.
        Human readable name. Null or whitespace names are not permitted.

        :param name: The name of this ExportItemV1.
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")

        self._name = name

    @property
    def start(self):
        """
        Gets the start of this ExportItemV1.
        The ISO 8601 start time

        :return: The start of this ExportItemV1.
        :rtype: str
        """
        return self._start

    @start.setter
    def start(self, start):
        """
        Sets the start of this ExportItemV1.
        The ISO 8601 start time

        :param start: The start of this ExportItemV1.
        :type: str
        """
        if start is None:
            raise ValueError("Invalid value for `start`, must not be `None`")

        self._start = start

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, ExportItemV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
