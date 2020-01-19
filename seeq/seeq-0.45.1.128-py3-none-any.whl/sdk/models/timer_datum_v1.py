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


class TimerDatumV1(object):
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
        'args': 'list[str]',
        'duration': 'str',
        'monitor': 'str'
    }

    attribute_map = {
        'args': 'args',
        'duration': 'duration',
        'monitor': 'monitor'
    }

    def __init__(self, args=None, duration=None, monitor=None):
        """
        TimerDatumV1 - a model defined in Swagger
        """

        self._args = None
        self._duration = None
        self._monitor = None

        if args is not None:
          self.args = args
        if duration is not None:
          self.duration = duration
        if monitor is not None:
          self.monitor = monitor

    @property
    def args(self):
        """
        Gets the args of this TimerDatumV1.
        List of arguments to include in the monitor path

        :return: The args of this TimerDatumV1.
        :rtype: list[str]
        """
        return self._args

    @args.setter
    def args(self, args):
        """
        Sets the args of this TimerDatumV1.
        List of arguments to include in the monitor path

        :param args: The args of this TimerDatumV1.
        :type: list[str]
        """

        self._args = args

    @property
    def duration(self):
        """
        Gets the duration of this TimerDatumV1.
        The duration between each screenshot. Example: 5min

        :return: The duration of this TimerDatumV1.
        :rtype: str
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """
        Sets the duration of this TimerDatumV1.
        The duration between each screenshot. Example: 5min

        :param duration: The duration of this TimerDatumV1.
        :type: str
        """
        if duration is None:
            raise ValueError("Invalid value for `duration`, must not be `None`")

        self._duration = duration

    @property
    def monitor(self):
        """
        Gets the monitor of this TimerDatumV1.
        Name of the monitor item this data should apply to.

        :return: The monitor of this TimerDatumV1.
        :rtype: str
        """
        return self._monitor

    @monitor.setter
    def monitor(self, monitor):
        """
        Sets the monitor of this TimerDatumV1.
        Name of the monitor item this data should apply to.

        :param monitor: The monitor of this TimerDatumV1.
        :type: str
        """
        if monitor is None:
            raise ValueError("Invalid value for `monitor`, must not be `None`")

        self._monitor = monitor

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
        if not isinstance(other, TimerDatumV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
