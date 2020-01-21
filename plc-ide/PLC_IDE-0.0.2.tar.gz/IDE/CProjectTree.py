# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc


###########################################################################
## Class Panel_Tree
###########################################################################

class Panel_Tree(wx.Panel):

    def __init__(self, parent,hanndel):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(200, 600),
                          style=wx.TAB_TRAVERSAL)

        self.parent = hanndel

        bz = wx.BoxSizer(wx.VERTICAL)

        self.m_tree = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)
        bz.Add(self.m_tree, 1, wx.ALL | wx.EXPAND, 0)


        self.root = self.m_tree.AddRoot('Project')
        self.m_tree.SetItemData(self.root,None)

        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.m_tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.m_tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.m_tree)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.m_tree)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self.m_tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.m_tree)

        self.m_tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.m_tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.m_tree.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)


        self.SetSizer(bz)
        self.Layout()

    def __del__(self):
        pass


    def DeleteAll(self):
        self.m_tree.Delete(self.root)
        self.root = self.m_tree.AddRoot('Project')

    def Render(self,dc):
        self.data = {}

        lt = [
            'hardware',
            'motion',
            'struct',
            'enum',
            'function',
            'class',
            'program',
            'gvl',
            'task'
        ]


        for n in lt:
            k = n
            itemlv1 = self.m_tree.AppendItem(self.root,k)
            self.m_tree.SetItemData(itemlv1,[k])
            self.data[k] = itemlv1
            for f in dc[k].keys():
                itemlv2 = self.m_tree.AppendItem(itemlv1,f)
                self.m_tree.SetItemData(itemlv2,[k,f])
                if k == 'class':
                    for m in dc[k][f].keys():
                        if m != 'init' and m != 'Declare':
                            itemlv3 = self.m_tree.AppendItem(itemlv2,m)
                            self.m_tree.SetItemData(itemlv3,[k,f,m])


    def AppendItem(self,k,f):
        itemlv2 = self.m_tree.AppendItem(self.data[k],f)
        self.m_tree.SetItemData(itemlv2,[k,f])


    def OnRightDown(self, event):
        pt = event.GetPosition()
        item, flags = self.m_tree.HitTest(pt)
        if item:

            d = self.m_tree.GetItemData(item)
            print d
            if d != None and len(d) >= 1:

                if len(d) == 1:
                    if d[0] in ['gvl','motion','hardware']:
                        pass
                    else:
                        self.parent.TreeOnRightDown(d)
                elif len(d) >= 2:
                    if d[0] == 'class':
                        self.parent.TreeClassOnRrightDown(d)
                self.SelectionItem = d
            pass


    def OnRightUp(self, event):
        event.Skip()
        # pt = event.GetPosition();
        # item, flags = self.tree.HitTest(pt)
        # if item:
        #     self.log.WriteText("OnRightUp: %s (manually starting label edit)\n"
        #                        % self.tree.GetItemText(item))
        #     self.tree.EditLabel(item)

    def OnBeginEdit(self, event):
        event.Skip()
        # self.log.WriteText("OnBeginEdit\n")
        # # show how to prevent edit...
        # item = event.GetItem()
        # if item and self.tree.GetItemText(item) == "The Root Item":
        #     wx.Bell()
        #     self.log.WriteText("You can't edit this one...\n")
        #
        #     # Lets just see what's visible of its children
        #     cookie = 0
        #     root = event.GetItem()
        #     (child, cookie) = self.tree.GetFirstChild(root)
        #
        #     while child.IsOk():
        #         self.log.WriteText("Child [%s] visible = %d" %
        #                            (self.tree.GetItemText(child),
        #                             self.tree.IsVisible(child)))
        #         (child, cookie) = self.tree.GetNextChild(root, cookie)
        #
        #     event.Veto()

    def OnEndEdit(self, event):
        event.Skip()
        # self.log.WriteText("OnEndEdit: %s %s\n" %
        #                    (event.IsEditCancelled(), event.GetLabel()))
        # # show how to reject edit, we'll not allow any digits
        # for x in event.GetLabel():
        #     if x in string.digits:
        #         self.log.WriteText("You can't enter digits...\n")
        #         event.Veto()
        #         return

    def OnLeftDClick(self, event):
        pt = event.GetPosition()
        item, flags = self.m_tree.HitTest(pt)
        if item:
            d = self.m_tree.GetItemData(item)
            if d != None and len(d) >= 2:

                self.parent.openfilepage(d)


                self.SelectionItem = d
            pass
            # self.log.WriteText("OnLeftDClick: %s\n" % self.tree.GetItemText(item))
            # parent = self.tree.GetItemParent(item)
            # if parent.IsOk():
            #     self.tree.SortChildren(parent)
        event.Skip()

    def OnSize(self, event):
        w, h = self.GetClientSize()
        self.m_tree.SetSize(0, 0, w, h)

    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            pass
            # self.log.WriteText("OnItemExpanded: %s\n" % self.tree.GetItemText(item))

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            pass
            # self.log.WriteText("OnItemCollapsed: %s\n" % self.tree.GetItemText(item))

    def OnSelChanged(self, event):
        item = event.GetItem()
        if item:
            d = self.m_tree.GetItemData(item)
            if d != None:
                self.SelectionItem = d
        event.Skip()

    def OnActivate(self, event):
        # if self.item:
        #     self.log.WriteText("OnActivate: %s\n" % self.tree.GetItemText(self.item))
        event.Skip()