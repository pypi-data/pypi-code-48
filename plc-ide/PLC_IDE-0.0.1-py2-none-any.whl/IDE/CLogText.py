# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import wx


logtext = None


def create_log(parent):
    global logtext
    logtext = wx.TextCtrl(parent, -1,
                     "",
                     size=(200, 100), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.TE_READONLY)
    logtext.SetInsertionPoint(0)

def LogText(txt):
    global logtext
    logtext.write(txt + '\n')

def write(txt):
    global logtext
    logtext.write(txt + '\n')