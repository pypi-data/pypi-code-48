#!/usr/bin/python
# -*- coding: utf-8 -*-


###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid as gridlib
import wx.dataview
import copy
# ---------------------------------------------------------------------------


class TableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        gridlib.Grid.__init__(self, parent, -1)

        self.table = DataTable(log)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.table, True)

        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)

        self.SetColSize(0, 200)
        self.SetColSize(1, 100)
        self.SetColSize(2, 300)
        self.SetColSize(3, 100)

        self.selRow = 0
        self.selCol = 0
        self.log = log

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()
        # self.selRow = evt.GetRow()
        # self.selCol = evt.GetCol()
        # self.log('Global Grid sel:(%d,%d)' % (self.selRow,self.selCol))
        evt.Skip()

    def OnLeftClick(self, evt):
        self.selRow = evt.GetRow()
        self.selCol = evt.GetCol()
        # self.log('Global Grid sel:(%d,%d)' % (self.selRow, self.selCol))
        evt.Skip()

    def SetChoice(self, col, lt):
        self.table.SetChoice(col, lt)

    def DelRow(self):
        self.table.DeleteRows(self.selRow, 1)
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        return self.selRow

    def DelAll(self):
        self.table.DeleteAll()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

    def AddRow(self):
        self.table.AppendRows(1)
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

    def AddRows(self, numRows):
        self.table.AppendRows(numRows)
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

    def InsertRow(self, pos):
        self.table.InsertRows(pos, 1)
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

    def Refresh(self):
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)

    def Render(self, data):
        self.DelAll()
        self.AddRows(len(data))
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                self.table.SetValue(i, j, data[i][j])

        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)
        self.Update()
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(False)



# ---------------------------------------------------------------------------

class DataTable(gridlib.GridTableBase):
    def __init__(self, log):
        gridlib.GridTableBase.__init__(self)

        self.log = log

        self.colLabels = ['Name', 'Datatype', 'Comment', 'Init Value']

        self.dataTypes = [gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING
                          ]
        self.data = [
            # ['','','','']

        ]

        self.itemdata = []


        self.defaultdata = ['', '', '', '']

    # --------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colLabels)

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def GetItemValue(self,row,col):
        try:
            return self.itemdata[row][col]
        except IndexError:
            return None

    def SetValue(self, row, col, value):

        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row

                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,  # The table
                                               gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                                               1  # how many
                                               )

                self.GetView().ProcessTableMessage(msg)

        innerSetValue(row, col, value)


    def SetItemValue(self,row,col,value):
        def innerSetItemValue(row, col, value):
            try:
                self.itemdata[row][col] = value
            except IndexError:
                # add a new row

                self.data.append([''] * self.GetNumberCols())
                innerSetItemValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,  # The table
                                               gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                                               1  # how many
                                               )

                self.GetView().ProcessTableMessage(msg)

        innerSetItemValue(row, col, value)

    def SetChoice(self, col, lt):
        self.dataTypes[col] = gridlib.GRID_VALUE_CHOICE + ':' + ','.join(lt)

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

    def DeleteRows(self, pos=0, numRows=1):
        if pos > len(self.data) and pos < 0:
            return

        for i in range(0, numRows):
            del self.data[pos + i]
            del self.itemdata[pos + i]

        msg = gridlib.GridTableMessage(self,  # The table
                                       gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,  # what we did to it
                                       pos,  # how many
                                       numRows
                                       )

        self.GetView().ProcessTableMessage(msg)

    def DeleteAll(self):
        nn = self.GetNumberRows()
        msg = gridlib.GridTableMessage(self,  # The table
                                       gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,  # what we did to it
                                       0,  # how many
                                       self.GetNumberRows()
                                       )

        self.GetView().ProcessTableMessage(msg)
        self.data = []
        self.itemdata = []

    def AppendRows(self, numRows=1):
        for i in range(0, numRows):
            dd = copy.deepcopy(self.defaultdata)
            self.data.append(dd)
            dd2 = [None]*len(self.defaultdata)
            self.itemdata.append(dd2)


        msg = gridlib.GridTableMessage(self,  # The table
                                       gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                                       numRows  # how many
                                       )
        self.GetView().ProcessTableMessage(msg)

    def InsertRows(self, pos, numRows=1):
        for i in range(0, numRows):
            dd = copy.deepcopy(self.defaultdata)
            self.data.insert(pos, dd)
            dd2 = [None] * len(self.defaultdata)
            self.itemdata.append(dd2)

        msg = gridlib.GridTableMessage(self,  # The table
                                       gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED,  # what we did to it
                                       pos,
                                       numRows  # how many
                                       )
        self.GetView().ProcessTableMessage(msg)


