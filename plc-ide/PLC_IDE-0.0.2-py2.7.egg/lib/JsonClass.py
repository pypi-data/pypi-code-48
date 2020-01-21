#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import codecs
import os

class CJSON:
    data = {}

    def __int__(self):
        self.__doc__ = "v1.0"

    def loadstr(self,txt):  #load json string
        return json.loads(txt)

    def loadstr2(self,txt):  #load json string
        self.data = json.loads(txt)

    def loadfile(self,filepath):        #load json file
        try:
            fso = open(filepath, "r")
            txt = fso.read()
            if txt[:3] == codecs.BOM_UTF8:
                txt = txt[3:]
            jsonstring = txt
            data = json.loads(jsonstring)
        except UnicodeDecodeError,EOFError:
            data = json.loads(txt)
            print EOFError.message
            return {}
        except IOError:
            print u"Error: 没有找到文件或读取文件失败"
            return {}
        else:
            if fso:
                fso.close()
                return data

    def outputjson(self,data):                   #output json string
        t = json.dumps(data, sort_keys=False)
        return json.dumps(json.loads(t), ensure_ascii=False,indent=4)


    def outputjson_min(self,data):
        t = json.dumps(data, sort_keys=False)
        return json.dumps(json.loads(t), ensure_ascii=False)

    def outputjson_max(self,data):
        t = json.dumps(data, sort_keys=False)
        return json.dumps(json.loads(t), ensure_ascii=False, indent=4)

    def loadfile2(self,filepath):        #load json file
        try:
            fso = open(filepath, "r")
            txt = fso.read()
            if txt[:3] == codecs.BOM_UTF8:
                txt = txt[3:]

            jsonstring = txt.decode("gb2312")
            self.data = json.loads(jsonstring)
        finally:
            if fso:
                fso.close()

    def outputjson2(self):                   #output json string
        return json.dumps(self.data,sort_keys=False)

    def writefile(self,data,filepath):           #write json file
        txt = self.outputjson(data)
        # txt = txt.encode('gb2312')
        # # txt = txt.decode('utf-8').encode('gbk')
        # txt = txt.decode('raw_unicode_escape')
        try:
            fso = codecs.open(filepath, "w+", "utf-8")
            fso.write(txt)
        except IOError:
            print "Error: 没有找到文件或读取文件失败"
        finally:
            if fso:
                fso.close()



    def compress(self,s):
        pass


#tt1 = '{"a":333333,\r\n"b":2, "c"                :  33, "d" : 4,"e" : 5 }'
##
##  tt2 = '{"a" : 11,"b" : 21, "c" : 31, "d" : 41,"e" : 51}'
#aa = CJSON()
##  a2 = CJSON()
#d = aa.loadstr(tt1)
#print aa.outputjson(d)
#print aa.outputjson_min(d)
#print aa.outputjson_max(d)
#ss = aa.outputjson_max(d)
#kk = 1
#
#  path1 = "d:\pytest.json"
#  aa.loadstr(tt1)
#  aa.loadfile(path1)
#  a2.loadstr(tt2)
#
#  print a2.output()
#  a2.outputfile("d:\pytest2.json")
#
#
#  print "over"