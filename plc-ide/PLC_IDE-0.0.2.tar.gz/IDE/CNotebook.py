# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from CCodeEditor import Panel_Code
from CCodeEditor_FC import Panel_Code_FC
from CCodeEditor_PRG import Panel_Code_PRG
from CDeclar_Menber import Panel_Declare
from CDeclar_Menber_FB import Panel_Declare_FB
from CDeclar_Menber_Hardware import Panel_Declare_HW
from CDeclar_Enum import Panel_Enum
from CDeclar_Task import Panel_Task
from CDeclar_Axis import Panel_Axis
from CLogText import LogText
###########################################################################
## Class Panel_Notebook
###########################################################################

class Panel_Notebook(wx.Panel):

    def __init__(self, parent,hanndel):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300),
                          style=wx.TAB_TRAVERSAL)

        self.parent = hanndel
        self.opened = []
        bz = wx.BoxSizer(wx.VERTICAL)

        self.m_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        bz.Add(self.m_notebook, 1, wx.EXPAND | wx.ALL, 0)



        self.SetSizer(bz)
        self.Layout()

        # Connect Events
        self.m_notebook.Bind(wx.EVT_LEFT_DCLICK, self.ClosePage)

    def __del__(self):
        pass


    def OpenPage(self,d,data):

        _idname = '$'.join(d)

        k = d[0]
        f = d[1]

        m = ''
        if len(d) > 2:
            m = d[2]

        if len(d) == 2 and k == 'class':
            _idname += '$Declare'



        _res = (_idname) in self.opened
        if _res == True :
            _index = self.opened.index((_idname))
            self.m_notebook.ChangeSelection(_index)
            return

        _panel = None
        if k == 'struct':
            _panel = Panel_Declare(self.m_notebook,self)
            pass
        elif k == 'enum':
            _panel = Panel_Enum(self.m_notebook, self)
            pass
        elif k == 'gvl':
            _panel = Panel_Declare(self.m_notebook, self)
            pass
        elif k == 'class':
            if len(d) > 2:
                _panel = Panel_Code_FC(self.m_notebook, self)
            elif len(d) == 2:
                _panel = Panel_Declare_FB(self.m_notebook, self)

            pass
        elif k == 'function':
            _panel = Panel_Code_FC(self.m_notebook, self)
            pass
        elif k == 'program':
            _panel = Panel_Code_PRG(self.m_notebook, self)
            pass
        elif k == 'main':
            _panel = Panel_Code(self.m_notebook, self)
        elif k == 'task':
            _panel = Panel_Task(self.m_notebook,self)
        elif k == 'motion':
            _panel = Panel_Axis(self.m_notebook,self)
        elif k == 'hardware':
            _panel = Panel_Declare_HW(self.m_notebook,self)


        if len(d) == 2:
            if k == 'class':
                self.m_notebook.AddPage(_panel, '%s[%s][%s]' % ('Declare', f, k), True)
                _panel.renderdata(data['Declare'])
            else:
                self.m_notebook.AddPage(_panel, '%s[%s]' % (f, k),True)
                _panel.renderdata(data)
        elif len(d) == 3:
            self.m_notebook.AddPage(_panel, '%s[%s][%s]' % (m,f, k), True)
            _panel.renderdata(data)



        self.opened.append(_idname)

        pass

    def SavePage(self,data):
        v = self.m_notebook.GetSelection()
        l = self.opened[v].split('$')

        self.parent.SavePage(l,data)


        pass

    def ClosePage(self,event):
        self.opened.pop(self.m_notebook.GetSelection())
        self.m_notebook.DeletePage(self.m_notebook.GetSelection())
        event.Skip()
        pass

    def CloseAll(self):
        # self.m_notebook.DeleteAllPages()
        for i in xrange(len(self.opened)):
            self.m_notebook.DeletePage(0)
        self.opened = []
        pass



    def PageHasEdited(self):
        # v = self.m_notebook.GetSelection()
        #
        # txt = self.m_notebook.GetLabelText()
        # self.m_notebook.SetLabelText(txt + "  *")
        pass