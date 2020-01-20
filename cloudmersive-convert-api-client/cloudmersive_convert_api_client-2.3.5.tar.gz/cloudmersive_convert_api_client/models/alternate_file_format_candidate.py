# coding: utf-8

"""
    convertapi

    Convert API lets you effortlessly convert file formats and types.  # noqa: E501

    OpenAPI spec version: v1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class AlternateFileFormatCandidate(object):
    """NOTE: This class is auto generated by the swagger code generator program.

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
        'probability': 'float',
        'detected_file_extension': 'str',
        'detected_mime_type': 'str'
    }

    attribute_map = {
        'probability': 'Probability',
        'detected_file_extension': 'DetectedFileExtension',
        'detected_mime_type': 'DetectedMimeType'
    }

    def __init__(self, probability=None, detected_file_extension=None, detected_mime_type=None):  # noqa: E501
        """AlternateFileFormatCandidate - a model defined in Swagger"""  # noqa: E501

        self._probability = None
        self._detected_file_extension = None
        self._detected_mime_type = None
        self.discriminator = None

        if probability is not None:
            self.probability = probability
        if detected_file_extension is not None:
            self.detected_file_extension = detected_file_extension
        if detected_mime_type is not None:
            self.detected_mime_type = detected_mime_type

    @property
    def probability(self):
        """Gets the probability of this AlternateFileFormatCandidate.  # noqa: E501

        Probability that this extension is the right one; possible values are between 0.0 (lowest confidence) and 1.0 (highest confidence)  # noqa: E501

        :return: The probability of this AlternateFileFormatCandidate.  # noqa: E501
        :rtype: float
        """
        return self._probability

    @probability.setter
    def probability(self, probability):
        """Sets the probability of this AlternateFileFormatCandidate.

        Probability that this extension is the right one; possible values are between 0.0 (lowest confidence) and 1.0 (highest confidence)  # noqa: E501

        :param probability: The probability of this AlternateFileFormatCandidate.  # noqa: E501
        :type: float
        """

        self._probability = probability

    @property
    def detected_file_extension(self):
        """Gets the detected_file_extension of this AlternateFileFormatCandidate.  # noqa: E501

        Detected file extension of the file format, with a leading period  # noqa: E501

        :return: The detected_file_extension of this AlternateFileFormatCandidate.  # noqa: E501
        :rtype: str
        """
        return self._detected_file_extension

    @detected_file_extension.setter
    def detected_file_extension(self, detected_file_extension):
        """Sets the detected_file_extension of this AlternateFileFormatCandidate.

        Detected file extension of the file format, with a leading period  # noqa: E501

        :param detected_file_extension: The detected_file_extension of this AlternateFileFormatCandidate.  # noqa: E501
        :type: str
        """

        self._detected_file_extension = detected_file_extension

    @property
    def detected_mime_type(self):
        """Gets the detected_mime_type of this AlternateFileFormatCandidate.  # noqa: E501

        MIME type of this file extension  # noqa: E501

        :return: The detected_mime_type of this AlternateFileFormatCandidate.  # noqa: E501
        :rtype: str
        """
        return self._detected_mime_type

    @detected_mime_type.setter
    def detected_mime_type(self, detected_mime_type):
        """Sets the detected_mime_type of this AlternateFileFormatCandidate.

        MIME type of this file extension  # noqa: E501

        :param detected_mime_type: The detected_mime_type of this AlternateFileFormatCandidate.  # noqa: E501
        :type: str
        """

        self._detected_mime_type = detected_mime_type

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
        if issubclass(AlternateFileFormatCandidate, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AlternateFileFormatCandidate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
