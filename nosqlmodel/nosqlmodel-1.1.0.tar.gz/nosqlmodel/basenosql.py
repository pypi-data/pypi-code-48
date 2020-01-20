# -*- coding: utf-8 -*-
import json
import os
import uuid
import zipfile

from simplejsonobject import JsonObject

__author__ = 'ozgur'
__creation_date__ = '12.09.2019' '13:48'

from nosqlmodel.connectors.redisconnector import RedisConnector


class BaseNoSqlModel(JsonObject):
    """
    Nosql model with basic functionality\n
    """

    class Meta:
        connector = RedisConnector()
        indexkey = None

    def __init__(self):
        self.idkey = None

    def delete_table(self):
        """
        deletes table from db\n
        :return:
        """
        self.Meta.connector.delete_table()

    def create_table(self):
        """
        creates a new table, delete first if exists \n
        :return:
        """
        self.Meta.connector.create_table()

    @classmethod
    def flush(cls):
        """
        flushes al records\n
        :return: None
        """
        cls.Meta.connector.flush()

    @classmethod
    def dbsize(cls) -> int:
        """
        returns the itemcount in db\n
        :return: item count
        """
        return cls.Meta.connector.dbsize()

    @classmethod
    def get_keys(cls, pattern: str = "*") -> list:
        """
        return all idkeys in db\n
        :return:
        """
        return cls.Meta.connector.keys(pattern)

    def get_by_id(self, idkey: str) -> bool:
        """
        get item by id\n
        :return:
        """
        ret = self.Meta.connector.get(idkey)
        if ret:
            self.from_dict(ret)
            return True
        else:
            return False

    def get_or_create_by_id(self, idkey: str) -> bool:
        """
        get item by id\n
        :return:
        """
        ret = self.Meta.connector.get(idkey)
        if ret:
            self.from_dict(ret)
            return True
        else:
            self.__dict__[self.Meta.indexkey] = idkey
            return False

    @classmethod
    def get_multi(cls, keylist: list) -> list:
        """
        get value by key\n
        :param keylist: list of strings
        :return: [objectdict]
        """
        return cls.Meta.connector.get_multi(keylist)

    @classmethod
    def get_all_as_list(cls) -> list:
        """
        returns all db as list of item dicts\n
        :return:  [object_dict]
        """
        return cls.Meta.connector.get_all_as_list()

    @classmethod
    def get_all_as_dict(cls) -> dict:
        """
        returns all db as dict of item dicts\n
        :return:  {"id":object_dict,}
        """
        return cls.Meta.connector.get_all_as_dict()

    @classmethod
    def get_all_as_objectlist(cls) -> list:
        """
        returns all db as list of item objects\n
        :return:  [object]
        """
        retlist = []
        for itemdict in cls.get_all_as_list():
            retobj = cls()
            retobj.from_dict(itemdict)
            retlist.append(retobj)
        return retlist

    @classmethod
    def get_all_as_objectdict(cls) -> dict:
        """
        returns all db as dict of item objects\n
        :return:  {key:object}
        """
        retdict = {}
        for key, itemdict in cls.get_all_as_dict().items():
            retobj = cls()
            retobj.from_dict(itemdict)
            retdict[key] = retobj
        return retdict

    def save_to_cache(self, tags: list = None, compress=True) -> bool:
        """
        saves object\n

        :param tags: additional tags will added when saved
        :type compress: will save data compressed in db
        :return: success status
        """
        if not self.idkey:
            if self.Meta.indexkey:
                bnoid = self.__dict__.get(self.Meta.indexkey, None)
                self.idkey = bnoid if bnoid else str(uuid.uuid4())
            else:
                self.idkey = str(uuid.uuid4())
        else:
            pass
        if compress:
            sdict = self.to_dict_compressed()
        else:
            sdict = self.to_dict()

        retval = self.Meta.connector.upsert(self.idkey, sdict)

        if tags:
            tnew = [x for x in tags if x]
            self.add_tags_to_item(tnew)

        return retval

    def delete(self):
        """
        Deletes item from redis \n
        :return: None
        """
        if not self.idkey:
            raise KeyError("First you must save to remove it")
        self.Meta.connector.remove(self.idkey)

    @classmethod
    def get_tag_keys(cls, tag: str) -> list:
        """
        returns keys tagged bay given tag\n
        :return: list
        """
        return cls.Meta.connector.gettagkeys(tag)

    @classmethod
    def get_tags(cls) -> list:
        """
        returns tag list\n
        :return: list
        """
        return cls.Meta.connector.tags()

    @classmethod
    def get_by_tag(cls, tag: str) -> list:
        """
        returns obejct list tagged by given tag\n
        :return:[BaseNosqlModel]
        """
        retlist = []
        for itemdict in cls.Meta.connector.gettag(tag):
            retobj = cls()
            retobj.from_dict(itemdict)
            retlist.append(retobj)
        return retlist

    def add_tags_to_item(self, taglist: list):
        """
        adds tags to object\n
        :param taglist: list of tags
        :return:
        """
        if not self.idkey:
            raise KeyError("You must save before adding a tag")
        for tag in taglist:
            self.Meta.connector.addtag(tag, self.idkey)

    def remove_item_from_tag(self, tag: str):
        """
        removes item from tag\n
        :param tag:
        :return:
        """
        if not self.idkey:
            raise KeyError("You must save before removing from a tag")
        self.Meta.connector.removefromtag(tag, self.idkey)

    def from_dict(self, updatedict: dict):
        """
        populates data from dict
        Warning this will also overrides the id too!!        \n
        :param updatedict: dict which contains data
        :return: None
        """
        try:
            del updatedict["connector"]
        except (KeyError, TypeError):
            pass
        super().from_dict(updatedict.copy())

    def to_dict(self) -> dict:
        """
        populates data to dict \n
        :return: None
        """
        retval = super().to_dict()
        try:
            del retval["connector"]
        except (KeyError, TypeError):
            pass
        return retval

    @classmethod
    def export_to_json_text(cls, exportdict: dict = None, compress_data=False) -> str:
        """
         transforms exportdict or whole database into json \n
        :param compress_data: bool, data will be compressed or not
        :param exportdict: must be dictionary of same class objects or json serializable values
        :return: returns a json compliant text file
        """
        edict = {}
        if exportdict:
            for key, value in exportdict.items():
                try:
                    if isinstance(value, cls):
                        edict[key] = value.to_dict()
                    else:
                        edict[key] = value
                except AttributeError:
                    pass
        else:
            edict = cls.Meta.connector.get_all_as_dict()
        if compress_data:
            for key, subdict in edict.items():
                edict[key] = dict((i, d) for i, d in subdict.items() if d)

            retval = json.dumps(edict, ensure_ascii=False, indent=4)
        else:
            retval = json.dumps(edict, ensure_ascii=False)
        return retval

    @classmethod
    def export_to_json_file(cls, filepath: str, exportdict: dict = None, compress_data=False):
        """
         transforms exportdict or whole database into *.json file \n
        :param filepath: must end with .json
        :param exportdict: must be dictionary of same class objects
        :param compress_data: bool, data will be compressed or not
        :return:
        """
        if not filepath.endswith(".json"):
            raise FileNotFoundError("Wrong filename:" + filepath)
        with open(filepath, "w", encoding="UTF-8") as ofile:
            ofile.write(cls.export_to_json_text(exportdict, compress_data=compress_data))

    @classmethod
    def export_to_json_zip(cls, filepath: str, exportdict: dict = None, compress_data=False):
        """
         transforms exportdict or whole database into *.zip file \n
        :param filepath: must be end with .zip
        :param exportdict: must be dictionary of same class objects
        :param compress_data: bool, data will be compressed or not
        :return:
        """
        if not filepath.endswith(".zip"):
            raise FileNotFoundError("Wrong filename:" + filepath)
        else:
            tempfilepath = filepath.replace(".zip", ".json")
        cls.export_to_json_file(tempfilepath, exportdict, compress_data=compress_data)
        zipfile.ZipFile(filepath, mode='w').write(tempfilepath)
        os.remove(tempfilepath)

    @classmethod
    def import_from_json_text(cls, jsontext: str):
        """
        import and update db from exported json text \n
        :param jsontext: exported json text
        :return:
        """
        datadict = json.loads(jsontext, encoding="UTF-8")
        for key, value in datadict.items():
            instance = cls()
            instance.from_dict(value)
            instance.save_to_cache()

    @classmethod
    def import_from_json_file(cls, filepath: str):
        """
        import and update db from exported *.json file \n
        :param filepath: exported *.json file
        :return:
        """
        with open(filepath, "r", encoding="UTF-8") as ofile:
            content = ofile.read()
            cls.import_from_json_text(content)

    @classmethod
    def import_from_json_zip(cls, filepath: str):
        """
        import and update db from exported *.json file \n
        :param filepath: exported *.json file
        :return:
        """
        if not filepath.endswith(".zip"):
            raise FileNotFoundError("Wrong filename:" + filepath)
        else:
            tempfilepath = filepath.replace(".zip", ".json")

        with zipfile.ZipFile(filepath, 'r') as zipObj:
            zipObj.extractall("/")
        cls.import_from_json_file(tempfilepath)
        os.remove(tempfilepath)
