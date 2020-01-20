# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

__author__ = 'ozgur'
__creation_date__ = '9.09.2019' '14:12'


class BaseNosqlConnector(ABC):
    """Base Nosql connector Class"""
    def __init__(self):
        self.tagprefix = "tag:"

    @abstractmethod
    def delete_table(self):
        """
        deletes table from db\n
        :return:
        """

    @abstractmethod
    def create_table(self):
        """
        creates a new table, delete first if exists \n
        :return:
        """
    @abstractmethod
    def dbsize(self) -> int:
        """
        returns the itemcount in db\n
        :return: item count
        """

    @abstractmethod
    def keys(self, pattern='*') -> list:
        """
        returns keys list in db \n
        :param pattern: str urlpathregex
        :return: the keys in db
        """

    @abstractmethod
    def get(self, key: str) -> str or dict or list:
        """
        get value by key\n
        :param key: str
        :return: str or dict or list
        """

    @abstractmethod
    def get_multi(self, keylist: list) -> list:
        """
        get value by key\n
        :param keylist: list of strings
        :return: [objectdict]
        """

    @abstractmethod
    def get_all_as_dict(self) -> dict:
        """
        get all values in store \n
        :return: dict
        """

    @abstractmethod
    def get_all_as_list(self) -> list:
        """
        get all values in store \n
        :return: list
        """

    @abstractmethod
    def upsert(self, key: str, value: str or list or dict) -> bool:
        """
        adds a value to store\n
        :param key: key
        :param value: value to insert
        :return: bool
        """

    @abstractmethod
    def remove(self, key: str) -> bool:
        """
        removes the key from store\n
        :param key: str or list or tuple
        :return:
        """

    @abstractmethod
    def remove_keys(self, keys: list) -> bool:
        """
        removes the key from store\n
        :param keys:
        :return:
        """

    @abstractmethod
    def flush(self):
        """
        Flushes current store\n
        :return: None
        """

    @abstractmethod
    def tags(self) -> list:
        """
        returns tag list \n
        :return:
        """

    @abstractmethod
    def gettagkeys(self, tag: str) -> list:
        """
        get all keys of given tag \n
        :param tag:
        :return:
        """

    @abstractmethod
    def gettag(self, tag: str) -> list:
        """
        get all dict items in given tag \n
        :param tag:
        :return: list of dictionaries
        """

    @abstractmethod
    def addtag(self, tag: str, key: str):
        """
        Adds tags to keys \n
        :param tag: list
        :param key: list
        :return: None
        """

    @abstractmethod
    def removefromtag(self, tag: str, key: str or list):
        """
        Remove items from lists \n
        :param tag: str
        :param key: str or list
        :return: None
        """
