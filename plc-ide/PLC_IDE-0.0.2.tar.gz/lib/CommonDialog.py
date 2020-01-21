# -*- coding: utf-8 -*-
#!/usr/bin/env python
import wx
import os


def MessageBox(parent,msg,title,button=wx.OK | wx.ICON_INFORMATION):
                               # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION):
    dlg = wx.MessageDialog(parent,msg,
                            title,
                            button)
                               # wx.OK | wx.ICON_INFORMATION
                               # #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               # )
    val = dlg.ShowModal()
    dlg.Destroy()
    return val

def InputBox(parent=None,msg='',title=''):
        dlg = wx.TextEntryDialog(
                parent, msg,
                title, '')

        dlg.SetValue("")

        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()
        dlg.Destroy()


# filter is a list[list]
# exp:  [[dxf文件,dxf]]
def OpenFileDialog(parent,filter):

    tpath = os.getcwd()


    filters = ''

    for cmt,suffix in filter:
        filters += cmt + ' (*.' + suffix + ')|*.' + suffix
        filters += '|'

    filters = filters[:-1]
    dlg = wx.FileDialog(
        parent, message="Choose a file",
        defaultDir=os.getcwd(),
        defaultFile="",
        wildcard=filters,
        style=wx.FD_OPEN | wx.FD_MULTIPLE |
              wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
              wx.FD_PREVIEW
    )

    # Show the dialog and retrieve the user response. If it is the OK response,
    # process the data.
    if dlg.ShowModal() == wx.ID_OK:
        # This returns a Python list of files that were selected.
        paths = dlg.GetPaths()
        dlg.Destroy()
        os.chdir(tpath)
        return paths
        # self.log.WriteText('You selected %d files:' % len(paths))
        #
        # for path in paths:
        #     self.log.WriteText('           %s\n' % path)

    # Compare this with the debug above; did we change working dirs?
    # self.log.WriteText("CWD: %s\n" % os.getcwd())

    # Destroy the dialog. Don't do this until you are done with it!
    # BAD things can happen otherwise!
    dlg.Destroy()



#---------------------------------------------------------------------------

# This is how you pre-establish a file filter so that the dialog
# only shows the extension(s) you want it to.
wildcard = "Python source (*.py)|*.py|"     \
           "Compiled Python (*.pyc)|*.pyc|" \
           "SPAM files (*.spam)|*.spam|"    \
           "Egg file (*.egg)|*.egg|"        \
           "All files (*.*)|*.*"
