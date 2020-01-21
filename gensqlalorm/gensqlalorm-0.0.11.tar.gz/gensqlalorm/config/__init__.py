#! -*- coding:utf8 -*-

import yaml

import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

from gensqlalorm.utils import (
    gen_file_abspath
)


class GenConfig(object):
    def __init__(self, gen_project_list, ignore_shard, root_path):
        self.gen_list = gen_project_list
        self.ignore_shard = ignore_shard
        self.root_path = root_path

    def __str__(self):
        return "gen_list:%s, ignore_shard:%s, root_path:%s" % (self.gen_list, self.ignore_shard, self.root_path)


class DBConfig(object):
    def __init__(self, host, user, pawd, port, name):
        self.host_name = host
        self.user_name = user
        self.pass_word = pawd
        self.port = port
        self.name = name

    def __str__(self):
        return "host:%s, port:%s, user:%s, pass:%s, name:%s" % (self.host_name, self.port, self.user_name, self.pass_word, self.name)


db_config = None
gen_config = None

db_config_file_path = None
gen_config_file_path = None


def set_db_config(config):
    global db_config
    db_config = config


def set_gen_config(config):
    global gen_config
    gen_config = config


def set_db_config_path(config_path):
    global db_config_file_path
    db_config_file_path = config_path


def set_gen_config_path(config_path):
    global gen_config_file_path
    gen_config_file_path = config_path


def set_db_config_path(config_path):
    global db_config_file_path
    db_config_file_path = config_path


def get_gen_config():
    global gen_config
    if gen_config is not None:
        return gen_config

    global gen_config_file_path
    if gen_config_file_path is None:
        raise Exception("gen config path is None")

    r_file = open(gen_config_file_path, "r")
    resource = yaml.load(r_file, Loader=yaml.FullLoader)

    return GenConfig(resource.get("genProjectNames"),
                     resource.get("ignoreShard"),
                     resource.get("rootPath"))


def get_db_config():
    """
    {
        "TestDB_1":{
            "host": xxxx,
            "user": xxxx,
            "pass": xxxx,
            "port": xxxx
        }
    }
    """
    global db_config
    if db_config is not None:
        return db_config

    global db_config_file_path
    if db_config_file_path is None:
        raise Exception("db config is none")

    r_file = open(db_config_file_path, "r")
    resource = yaml.load(r_file, Loader=yaml.FullLoader)
    result = {}
    for db_name, db_config in resource.items():
        config = DBConfig(
            str(db_config.get("hostName")),
            str(db_config.get("userName")),
            str(db_config.get("passWord")),
            int(db_config.get("dbPort")),
            str(db_config.get("dbName"))
        )
        result[db_name] = config

    return result


if __name__ == "__main__":
    print get_db_config()
