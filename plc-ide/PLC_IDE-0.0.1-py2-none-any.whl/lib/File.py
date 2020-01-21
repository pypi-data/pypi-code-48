#!/usr/bin/python
# -*- coding: UTF-8 -*-
import codecs
import os

class FSO():

    def __int__(self):
        self.verison = "v1.0"

    def createfile(self,file,txt):
        try:
            fso = codecs.open(file, "w+","utf-8-sig")
            fso.write(txt)
            if fso:
                fso.close()
        except IOError:
            print u"Error: 没有找到文件或读取文件失败"
        else:
            if fso:
                fso.close()

    def readfile(self, file):
        try:
            file = os.path.abspath(file)
            fso = open(file, "r")
            txt = fso.read()
            if txt[:3] == codecs.BOM_UTF8:
                txt = txt[3:]
            return txt
        except IOError:
            print u"Error: 没有找到文件或读取文件失败"
            return ''
        else:
            if fso:
                fso.close()