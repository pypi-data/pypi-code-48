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

from cloudmersive_convert_api_client.models.pdf_form_field import PdfFormField  # noqa: F401,E501


class PdfFormFields(object):
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
        'successful': 'bool',
        'form_fields': 'list[PdfFormField]'
    }

    attribute_map = {
        'successful': 'Successful',
        'form_fields': 'FormFields'
    }

    def __init__(self, successful=None, form_fields=None):  # noqa: E501
        """PdfFormFields - a model defined in Swagger"""  # noqa: E501

        self._successful = None
        self._form_fields = None
        self.discriminator = None

        if successful is not None:
            self.successful = successful
        if form_fields is not None:
            self.form_fields = form_fields

    @property
    def successful(self):
        """Gets the successful of this PdfFormFields.  # noqa: E501

        True if the operation was successful, false otherwise  # noqa: E501

        :return: The successful of this PdfFormFields.  # noqa: E501
        :rtype: bool
        """
        return self._successful

    @successful.setter
    def successful(self, successful):
        """Sets the successful of this PdfFormFields.

        True if the operation was successful, false otherwise  # noqa: E501

        :param successful: The successful of this PdfFormFields.  # noqa: E501
        :type: bool
        """

        self._successful = successful

    @property
    def form_fields(self):
        """Gets the form_fields of this PdfFormFields.  # noqa: E501

        Fields and field values found in the form  # noqa: E501

        :return: The form_fields of this PdfFormFields.  # noqa: E501
        :rtype: list[PdfFormField]
        """
        return self._form_fields

    @form_fields.setter
    def form_fields(self, form_fields):
        """Sets the form_fields of this PdfFormFields.

        Fields and field values found in the form  # noqa: E501

        :param form_fields: The form_fields of this PdfFormFields.  # noqa: E501
        :type: list[PdfFormField]
        """

        self._form_fields = form_fields

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
        if issubclass(PdfFormFields, dict):
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
        if not isinstance(other, PdfFormFields):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
