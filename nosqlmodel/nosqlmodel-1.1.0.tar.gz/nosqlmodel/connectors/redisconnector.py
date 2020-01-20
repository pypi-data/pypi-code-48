# -*- coding: utf-8 -*-
"""
Basic redis connector
"""
import json

import redis

from nosqlmodel.connectors.baseconnector import BaseNosqlConnector

__author__ = 'ozgur'
__creation_date__ = '9.09.2019' '10:07'

RHOST = "localhost"
RPORT = "6379"


class RedisConnector(BaseNosqlConnector):
    """Redis connector for models. Can also be used as standalone lib too"""

    def __init__(self, dbnum: int = 0):
        self.redisdbnum = dbnum
        self.conn = redis.StrictRedis(host=RHOST, port=RPORT, charset="utf-8",
                                      decode_responses=True, db=self.redisdbnum)
        super().__init__()

    def delete_table(self):
        self.flush()

    def create_table(self):
        pass

    def dbsize(self) -> int:
        return len(self.keys())

    def keys(self, pattern='*') -> list:
        return list(
            set(self.conn.keys(pattern=pattern)) - set(self.conn.keys(self.tagprefix + "*")))

    def get(self, key: str) -> str or dict or list:
        key = str(key)
        retval = self.conn.get(key)

        if retval:
            # noinspection PyBroadException
            try:
                retval = json.loads(retval, encoding="UTF-8")
            except Exception:  # pylint: disable=broad-except
                retval = str(retval)
        else:
            pass

        return retval

    def get_multi(self, keylist: list) -> list:
        retlist = self.conn.mget(keylist)

        for i, rstr in enumerate(retlist):
            # noinspection PyBroadException
            try:
                retlist[i] = json.loads(rstr, encoding="UTF-8")
            except Exception:  # pylint: disable=broad-except
                retlist[i] = str(rstr)
        return retlist

    def get_all_as_dict(self) -> dict:
        keys = self.keys()
        retdct = {}
        for key in keys:
            retdct[key] = self.get(key)

        return retdct

    def get_all_as_list(self) -> list:
        keys = self.keys()
        retlist = []
        for key in keys:
            retlist.append(self.get(key))

        return retlist

    def upsert(self, key: str, value: str or list or dict) -> bool:
        key = str(key)
        if isinstance(value, (list, (dict, set, tuple))):
            value = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, object) and hasattr(value, "__dict__"):
            value = json.dumps(value.__dict__, ensure_ascii=False)
        else:
            value = str(value)
        return bool(self.conn.set(key, value))

    def remove(self, key: str) -> bool:
        key = str(key)
        ret = str(self.conn.delete(key))
        return {"1": True}.get(ret, False)

    def remove_keys(self, keys: list) -> bool:
        ret = str(self.conn.delete(keys))
        return {"1": True}.get(ret, False)

    def flush(self):
        self.conn.flushdb()

    def tags(self) -> list:
        taglist = self.conn.keys(self.tagprefix + "*")
        retlist = []
        for tag in taglist:
            retlist.append(tag.replace(self.tagprefix, ""))
        return retlist

    def gettagkeys(self, tag: str) -> list:
        memberids = self.conn.smembers(self.tagprefix + tag)
        return list(memberids)

    def gettag(self, tag: str) -> list:
        memberids = self.gettagkeys(tag)
        retlist = []
        for memberid in list(memberids):
            retlist.append(self.get(memberid))

        return retlist

    def addtag(self, tag: str, key: str):
        if not (tag and key):
            raise TypeError
        self.conn.sadd(self.tagprefix + tag, key)

    def removefromtag(self, tag: str, key: str or list):
        tag = str(tag)
        # ! dont touch it. srem doesnt accept list !!!!!
        if isinstance(key, (list, tuple, set)):
            for k in key:
                self.conn.srem(self.tagprefix + tag, k)
        else:
            self.conn.srem(self.tagprefix + tag, key)
