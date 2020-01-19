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


class WorkbookInputV1(object):
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
        'branch_from': 'str',
        'data': 'str',
        'description': 'str',
        'folder_id': 'str',
        'name': 'str',
        'owner_id': 'str'
    }

    attribute_map = {
        'branch_from': 'branchFrom',
        'data': 'data',
        'description': 'description',
        'folder_id': 'folderId',
        'name': 'name',
        'owner_id': 'ownerId'
    }

    def __init__(self, branch_from=None, data=None, description=None, folder_id=None, name=None, owner_id=None):
        """
        WorkbookInputV1 - a model defined in Swagger
        """

        self._branch_from = None
        self._data = None
        self._description = None
        self._folder_id = None
        self._name = None
        self._owner_id = None

        if branch_from is not None:
          self.branch_from = branch_from
        if data is not None:
          self.data = data
        if description is not None:
          self.description = description
        if folder_id is not None:
          self.folder_id = folder_id
        if name is not None:
          self.name = name
        if owner_id is not None:
          self.owner_id = owner_id

    @property
    def branch_from(self):
        """
        Gets the branch_from of this WorkbookInputV1.
        Create a new workbook by duplicating the contents and history of the workbook with the specified ID. When null, no branching will occur; resulting workbook will be empty.

        :return: The branch_from of this WorkbookInputV1.
        :rtype: str
        """
        return self._branch_from

    @branch_from.setter
    def branch_from(self, branch_from):
        """
        Sets the branch_from of this WorkbookInputV1.
        Create a new workbook by duplicating the contents and history of the workbook with the specified ID. When null, no branching will occur; resulting workbook will be empty.

        :param branch_from: The branch_from of this WorkbookInputV1.
        :type: str
        """

        self._branch_from = branch_from

    @property
    def data(self):
        """
        Gets the data of this WorkbookInputV1.
        JSON-encoded state for this Workbook

        :return: The data of this WorkbookInputV1.
        :rtype: str
        """
        return self._data

    @data.setter
    def data(self, data):
        """
        Sets the data of this WorkbookInputV1.
        JSON-encoded state for this Workbook

        :param data: The data of this WorkbookInputV1.
        :type: str
        """
        if data is None:
            raise ValueError("Invalid value for `data`, must not be `None`")

        self._data = data

    @property
    def description(self):
        """
        Gets the description of this WorkbookInputV1.
        Clarifying information or other plain language description of this asset. An input of just whitespace is equivalent to a null input.

        :return: The description of this WorkbookInputV1.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this WorkbookInputV1.
        Clarifying information or other plain language description of this asset. An input of just whitespace is equivalent to a null input.

        :param description: The description of this WorkbookInputV1.
        :type: str
        """

        self._description = description

    @property
    def folder_id(self):
        """
        Gets the folder_id of this WorkbookInputV1.
        The id of the folder to place the new workbook into. If null, the workbook will be created at the root level.

        :return: The folder_id of this WorkbookInputV1.
        :rtype: str
        """
        return self._folder_id

    @folder_id.setter
    def folder_id(self, folder_id):
        """
        Sets the folder_id of this WorkbookInputV1.
        The id of the folder to place the new workbook into. If null, the workbook will be created at the root level.

        :param folder_id: The folder_id of this WorkbookInputV1.
        :type: str
        """

        self._folder_id = folder_id

    @property
    def name(self):
        """
        Gets the name of this WorkbookInputV1.
        Human readable name. Null or whitespace names are not permitted.

        :return: The name of this WorkbookInputV1.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this WorkbookInputV1.
        Human readable name. Null or whitespace names are not permitted.

        :param name: The name of this WorkbookInputV1.
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")

        self._name = name

    @property
    def owner_id(self):
        """
        Gets the owner_id of this WorkbookInputV1.
        The ID of the User that owns this workbook. If omitted when creating a new Workbook, the authenticated user is used by default. Only administrators can set this value.

        :return: The owner_id of this WorkbookInputV1.
        :rtype: str
        """
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        """
        Sets the owner_id of this WorkbookInputV1.
        The ID of the User that owns this workbook. If omitted when creating a new Workbook, the authenticated user is used by default. Only administrators can set this value.

        :param owner_id: The owner_id of this WorkbookInputV1.
        :type: str
        """

        self._owner_id = owner_id

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
        if not isinstance(other, WorkbookInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
