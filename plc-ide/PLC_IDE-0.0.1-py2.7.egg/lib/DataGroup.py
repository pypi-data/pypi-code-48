#!/usr/bin/python
# -*- coding: UTF-8 -*-
from lib.JsonClass import CJSON
import copy


class CDataGroup:
    def __init__(self,filepath):
        self.version = "v1.0"
        objJSON = CJSON()
        self.temp = objJSON.loadfile(filepath)

    #items:
    ##[
    ##    {
    ##        'name':'',
    ##        'description':'',
    ##        'varType':''
    ##    }
    ##]
    def add_group(self,name,comment,items):
        dc = {}
        dc['description'] = comment
        dc['name'] = name
        dc['version'] = 1
        dc['enable'] = False
        dc['items'] = self.add_items(items)
        self.temp['hisDataGroups'].append(dc)


    def add_items(self,items):
        lt = []
        for item in items:
            dc = {}
            dc['DataItems'] = {}
            dc['description'] = item['description']
            dc['name'] = item['name']
            dc['varType'] = item['varType'] ##TODO 需要对数据类型进行翻译
            dc['version'] = 1
            dc['fixed'] = True
            dc['varData'] = ''
            lt.append(dc)

        return lt

    def output(self):
        objJSON = CJSON()
        return objJSON.outputjson(self.temp)