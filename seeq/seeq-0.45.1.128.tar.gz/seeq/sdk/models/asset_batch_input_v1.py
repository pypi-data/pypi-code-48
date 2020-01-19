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


class AssetBatchInputV1(object):
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
        'assets': 'list[AssetInputV1]',
        'host_id': 'str'
    }

    attribute_map = {
        'assets': 'assets',
        'host_id': 'hostId'
    }

    def __init__(self, assets=None, host_id=None):
        """
        AssetBatchInputV1 - a model defined in Swagger
        """

        self._assets = None
        self._host_id = None

        if assets is not None:
          self.assets = assets
        if host_id is not None:
          self.host_id = host_id

    @property
    def assets(self):
        """
        Gets the assets of this AssetBatchInputV1.
        A list of assets to create or update

        :return: The assets of this AssetBatchInputV1.
        :rtype: list[AssetInputV1]
        """
        return self._assets

    @assets.setter
    def assets(self, assets):
        """
        Sets the assets of this AssetBatchInputV1.
        A list of assets to create or update

        :param assets: The assets of this AssetBatchInputV1.
        :type: list[AssetInputV1]
        """
        if assets is None:
            raise ValueError("Invalid value for `assets`, must not be `None`")

        self._assets = assets

    @property
    def host_id(self):
        """
        Gets the host_id of this AssetBatchInputV1.
        This property is deprecated and will be removed in a future release and is currently ignored. Assign the hostId to each asset instead

        :return: The host_id of this AssetBatchInputV1.
        :rtype: str
        """
        return self._host_id

    @host_id.setter
    def host_id(self, host_id):
        """
        Sets the host_id of this AssetBatchInputV1.
        This property is deprecated and will be removed in a future release and is currently ignored. Assign the hostId to each asset instead

        :param host_id: The host_id of this AssetBatchInputV1.
        :type: str
        """

        self._host_id = host_id

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
        if not isinstance(other, AssetBatchInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
