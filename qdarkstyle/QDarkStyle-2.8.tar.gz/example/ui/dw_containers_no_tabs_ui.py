# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dw_containers_no_tabs.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from qtpy import QtCore, QtGui, QtWidgets


class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(497, 566)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_45 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_45.setObjectName("gridLayout_45")
        self.label_126 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_126.setFont(font)
        self.label_126.setObjectName("label_126")
        self.gridLayout_45.addWidget(self.label_126, 0, 3, 2, 1)
        self.label_124 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_124.setFont(font)
        self.label_124.setObjectName("label_124")
        self.gridLayout_45.addWidget(self.label_124, 0, 2, 2, 1)
        self.label_133 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_133.setFont(font)
        self.label_133.setObjectName("label_133")
        self.gridLayout_45.addWidget(self.label_133, 8, 0, 1, 2)
        self.groupBoxDis_2 = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.groupBoxDis_2.setEnabled(False)
        self.groupBoxDis_2.setObjectName("groupBoxDis_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBoxDis_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_7 = QtWidgets.QLabel(self.groupBoxDis_2)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_4.addWidget(self.label_7)
        self.gridLayout_45.addWidget(self.groupBoxDis_2, 2, 3, 1, 1)
        self.stackedWidget_2 = QtWidgets.QStackedWidget(self.dockWidgetContents)
        self.stackedWidget_2.setObjectName("stackedWidget_2")
        self.page1_2 = QtWidgets.QWidget()
        self.page1_2.setObjectName("page1_2")
        self.gridLayout_35 = QtWidgets.QGridLayout(self.page1_2)
        self.gridLayout_35.setObjectName("gridLayout_35")
        self.label_57 = QtWidgets.QLabel(self.page1_2)
        self.label_57.setObjectName("label_57")
        self.gridLayout_35.addWidget(self.label_57, 0, 0, 1, 1)
        self.stackedWidget_2.addWidget(self.page1_2)
        self.page2_2 = QtWidgets.QWidget()
        self.page2_2.setObjectName("page2_2")
        self.gridLayout_36 = QtWidgets.QGridLayout(self.page2_2)
        self.gridLayout_36.setObjectName("gridLayout_36")
        self.label_58 = QtWidgets.QLabel(self.page2_2)
        self.label_58.setObjectName("label_58")
        self.gridLayout_36.addWidget(self.label_58, 0, 0, 1, 1)
        self.stackedWidget_2.addWidget(self.page2_2)
        self.gridLayout_45.addWidget(self.stackedWidget_2, 5, 2, 1, 1)
        self.stackedWidgetDis_2 = QtWidgets.QStackedWidget(self.dockWidgetContents)
        self.stackedWidgetDis_2.setEnabled(False)
        self.stackedWidgetDis_2.setObjectName("stackedWidgetDis_2")
        self.page1Dis_2 = QtWidgets.QWidget()
        self.page1Dis_2.setObjectName("page1Dis_2")
        self.gridLayout_37 = QtWidgets.QGridLayout(self.page1Dis_2)
        self.gridLayout_37.setObjectName("gridLayout_37")
        self.label_113 = QtWidgets.QLabel(self.page1Dis_2)
        self.label_113.setObjectName("label_113")
        self.gridLayout_37.addWidget(self.label_113, 0, 0, 1, 1)
        self.stackedWidgetDis_2.addWidget(self.page1Dis_2)
        self.page2Dis_2 = QtWidgets.QWidget()
        self.page2Dis_2.setObjectName("page2Dis_2")
        self.gridLayout_38 = QtWidgets.QGridLayout(self.page2Dis_2)
        self.gridLayout_38.setObjectName("gridLayout_38")
        self.label_114 = QtWidgets.QLabel(self.page2Dis_2)
        self.label_114.setObjectName("label_114")
        self.gridLayout_38.addWidget(self.label_114, 0, 0, 1, 1)
        self.stackedWidgetDis_2.addWidget(self.page2Dis_2)
        self.gridLayout_45.addWidget(self.stackedWidgetDis_2, 5, 3, 1, 1)
        self.label_131 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_131.setFont(font)
        self.label_131.setObjectName("label_131")
        self.gridLayout_45.addWidget(self.label_131, 6, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.dockWidgetContents)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_43 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_43.setObjectName("gridLayout_43")
        self.label_9 = QtWidgets.QLabel(self.frame_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout_43.addWidget(self.label_9, 0, 0, 1, 1)
        self.gridLayout_45.addWidget(self.frame_2, 6, 2, 1, 1)
        self.frameDis_2 = QtWidgets.QFrame(self.dockWidgetContents)
        self.frameDis_2.setEnabled(False)
        self.frameDis_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameDis_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameDis_2.setObjectName("frameDis_2")
        self.gridLayout_40 = QtWidgets.QGridLayout(self.frameDis_2)
        self.gridLayout_40.setObjectName("gridLayout_40")
        self.label_8 = QtWidgets.QLabel(self.frameDis_2)
        self.label_8.setObjectName("label_8")
        self.gridLayout_40.addWidget(self.label_8, 0, 0, 1, 1)
        self.gridLayout_45.addWidget(self.frameDis_2, 6, 3, 1, 1)
        self.label_132 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_132.setFont(font)
        self.label_132.setObjectName("label_132")
        self.gridLayout_45.addWidget(self.label_132, 7, 0, 1, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_7.addWidget(self.label_10, 0, 0, 1, 1)
        self.gridLayout_45.addWidget(self.groupBox_2, 2, 2, 1, 1)
        self.mdiAreaDis_2 = QtWidgets.QMdiArea(self.dockWidgetContents)
        self.mdiAreaDis_2.setEnabled(False)
        self.mdiAreaDis_2.setObjectName("mdiAreaDis_2")
        self.subwindow1Dis_2 = QtWidgets.QWidget()
        self.subwindow1Dis_2.setObjectName("subwindow1Dis_2")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.subwindow1Dis_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_111 = QtWidgets.QLabel(self.subwindow1Dis_2)
        self.label_111.setObjectName("label_111")
        self.verticalLayout_9.addWidget(self.label_111)
        self.subwindow2Dis_2 = QtWidgets.QWidget()
        self.subwindow2Dis_2.setObjectName("subwindow2Dis_2")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.subwindow2Dis_2)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_112 = QtWidgets.QLabel(self.subwindow2Dis_2)
        self.label_112.setObjectName("label_112")
        self.verticalLayout_10.addWidget(self.label_112)
        self.gridLayout_45.addWidget(self.mdiAreaDis_2, 8, 3, 1, 1)
        self.label_127 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_127.setFont(font)
        self.label_127.setObjectName("label_127")
        self.gridLayout_45.addWidget(self.label_127, 2, 0, 1, 2)
        self.widget_2 = QtWidgets.QWidget(self.dockWidgetContents)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_39 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_39.setObjectName("gridLayout_39")
        self.label_59 = QtWidgets.QLabel(self.widget_2)
        self.label_59.setObjectName("label_59")
        self.gridLayout_39.addWidget(self.label_59, 0, 0, 1, 1)
        self.gridLayout_45.addWidget(self.widget_2, 7, 2, 1, 1)
        self.widgetDis_2 = QtWidgets.QWidget(self.dockWidgetContents)
        self.widgetDis_2.setEnabled(False)
        self.widgetDis_2.setObjectName("widgetDis_2")
        self.gridLayout_44 = QtWidgets.QGridLayout(self.widgetDis_2)
        self.gridLayout_44.setObjectName("gridLayout_44")
        self.label_125 = QtWidgets.QLabel(self.widgetDis_2)
        self.label_125.setObjectName("label_125")
        self.gridLayout_44.addWidget(self.label_125, 0, 0, 1, 1)
        self.gridLayout_45.addWidget(self.widgetDis_2, 7, 3, 1, 1)
        self.mdiArea_2 = QtWidgets.QMdiArea(self.dockWidgetContents)
        self.mdiArea_2.setObjectName("mdiArea_2")
        self.subwindow1_2 = QtWidgets.QWidget()
        self.subwindow1_2.setObjectName("subwindow1_2")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.subwindow1_2)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_29 = QtWidgets.QLabel(self.subwindow1_2)
        self.label_29.setObjectName("label_29")
        self.verticalLayout_11.addWidget(self.label_29)
        self.subwindow2_2 = QtWidgets.QWidget()
        self.subwindow2_2.setObjectName("subwindow2_2")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.subwindow2_2)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_56 = QtWidgets.QLabel(self.subwindow2_2)
        self.label_56.setObjectName("label_56")
        self.verticalLayout_12.addWidget(self.label_56)
        self.gridLayout_45.addWidget(self.mdiArea_2, 8, 2, 1, 1)
        self.label_128 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_128.setFont(font)
        self.label_128.setObjectName("label_128")
        self.gridLayout_45.addWidget(self.label_128, 3, 0, 1, 2)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.dockWidgetContents)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 181, 246))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_70 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_70.setObjectName("label_70")
        self.verticalLayout_14.addWidget(self.label_70)
        self.label_71 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_71.setObjectName("label_71")
        self.verticalLayout_14.addWidget(self.label_71)
        self.label_75 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_75.setObjectName("label_75")
        self.verticalLayout_14.addWidget(self.label_75)
        self.label_76 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_76.setObjectName("label_76")
        self.verticalLayout_14.addWidget(self.label_76)
        self.label_77 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_77.setObjectName("label_77")
        self.verticalLayout_14.addWidget(self.label_77)
        self.label_78 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_78.setObjectName("label_78")
        self.verticalLayout_14.addWidget(self.label_78)
        self.label_79 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_79.setObjectName("label_79")
        self.verticalLayout_14.addWidget(self.label_79)
        self.label_80 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_80.setObjectName("label_80")
        self.verticalLayout_14.addWidget(self.label_80)
        self.label_81 = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label_81.setObjectName("label_81")
        self.verticalLayout_14.addWidget(self.label_81)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_45.addWidget(self.scrollArea_2, 3, 2, 1, 1)
        self.scrollAreaDis_2 = QtWidgets.QScrollArea(self.dockWidgetContents)
        self.scrollAreaDis_2.setEnabled(False)
        self.scrollAreaDis_2.setWidgetResizable(True)
        self.scrollAreaDis_2.setObjectName("scrollAreaDis_2")
        self.scrollAreaWidgetContentsDis_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContentsDis_2.setGeometry(QtCore.QRect(0, 0, 181, 246))
        self.scrollAreaWidgetContentsDis_2.setObjectName("scrollAreaWidgetContentsDis_2")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContentsDis_2)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_115 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_115.setObjectName("label_115")
        self.verticalLayout_13.addWidget(self.label_115)
        self.label_116 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_116.setObjectName("label_116")
        self.verticalLayout_13.addWidget(self.label_116)
        self.label_117 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_117.setObjectName("label_117")
        self.verticalLayout_13.addWidget(self.label_117)
        self.label_118 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_118.setObjectName("label_118")
        self.verticalLayout_13.addWidget(self.label_118)
        self.label_119 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_119.setObjectName("label_119")
        self.verticalLayout_13.addWidget(self.label_119)
        self.label_120 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_120.setObjectName("label_120")
        self.verticalLayout_13.addWidget(self.label_120)
        self.label_121 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_121.setObjectName("label_121")
        self.verticalLayout_13.addWidget(self.label_121)
        self.label_122 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_122.setObjectName("label_122")
        self.verticalLayout_13.addWidget(self.label_122)
        self.label_123 = QtWidgets.QLabel(self.scrollAreaWidgetContentsDis_2)
        self.label_123.setObjectName("label_123")
        self.verticalLayout_13.addWidget(self.label_123)
        self.scrollAreaDis_2.setWidget(self.scrollAreaWidgetContentsDis_2)
        self.gridLayout_45.addWidget(self.scrollAreaDis_2, 3, 3, 1, 1)
        self.label_129 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_129.setFont(font)
        self.label_129.setObjectName("label_129")
        self.gridLayout_45.addWidget(self.label_129, 4, 0, 1, 2)
        self.toolBox_2 = QtWidgets.QToolBox(self.dockWidgetContents)
        self.toolBox_2.setObjectName("toolBox_2")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 196, 73))
        self.page_3.setObjectName("page_3")
        self.gridLayout_41 = QtWidgets.QGridLayout(self.page_3)
        self.gridLayout_41.setObjectName("gridLayout_41")
        self.label_60 = QtWidgets.QLabel(self.page_3)
        self.label_60.setObjectName("label_60")
        self.gridLayout_41.addWidget(self.label_60, 2, 0, 1, 1)
        self.toolBox_2.addItem(self.page_3, "")
        self.page_8 = QtWidgets.QWidget()
        self.page_8.setGeometry(QtCore.QRect(0, 0, 163, 38))
        self.page_8.setObjectName("page_8")
        self.gridLayout_42 = QtWidgets.QGridLayout(self.page_8)
        self.gridLayout_42.setObjectName("gridLayout_42")
        self.label_61 = QtWidgets.QLabel(self.page_8)
        self.label_61.setObjectName("label_61")
        self.gridLayout_42.addWidget(self.label_61, 0, 0, 1, 1)
        self.toolBox_2.addItem(self.page_8, "")
        self.gridLayout_45.addWidget(self.toolBox_2, 4, 2, 1, 1)
        self.toolBoxDis_2 = QtWidgets.QToolBox(self.dockWidgetContents)
        self.toolBoxDis_2.setEnabled(False)
        self.toolBoxDis_2.setObjectName("toolBoxDis_2")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setGeometry(QtCore.QRect(0, 0, 196, 73))
        self.page_6.setObjectName("page_6")
        self.gridLayout_29 = QtWidgets.QGridLayout(self.page_6)
        self.gridLayout_29.setObjectName("gridLayout_29")
        self.label_109 = QtWidgets.QLabel(self.page_6)
        self.label_109.setObjectName("label_109")
        self.gridLayout_29.addWidget(self.label_109, 2, 0, 1, 1)
        self.toolBoxDis_2.addItem(self.page_6, "")
        self.page_7 = QtWidgets.QWidget()
        self.page_7.setGeometry(QtCore.QRect(0, 0, 163, 38))
        self.page_7.setObjectName("page_7")
        self.gridLayout_34 = QtWidgets.QGridLayout(self.page_7)
        self.gridLayout_34.setObjectName("gridLayout_34")
        self.label_110 = QtWidgets.QLabel(self.page_7)
        self.label_110.setObjectName("label_110")
        self.gridLayout_34.addWidget(self.label_110, 0, 0, 1, 1)
        self.toolBoxDis_2.addItem(self.page_7, "")
        self.gridLayout_45.addWidget(self.toolBoxDis_2, 4, 3, 1, 1)
        self.label_130 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_130.setFont(font)
        self.label_130.setObjectName("label_130")
        self.gridLayout_45.addWidget(self.label_130, 5, 0, 1, 2)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.stackedWidget_2.setCurrentIndex(1)
        self.stackedWidgetDis_2.setCurrentIndex(1)
        self.toolBox_2.setCurrentIndex(0)
        self.toolBoxDis_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Containers - No Tabs"))
        self.label_126.setText(_translate("DockWidget", "Disabled"))
        self.label_124.setText(_translate("DockWidget", "Enabled"))
        self.label_133.setText(_translate("DockWidget", "MDI Area"))
        self.groupBoxDis_2.setTitle(_translate("DockWidget", "GroupBox"))
        self.label_7.setText(_translate("DockWidget", "Inside GroupBox"))
        self.stackedWidget_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.stackedWidget_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.stackedWidget_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_57.setText(_translate("DockWidget", "Inside Stacked Page 1"))
        self.label_58.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_58.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_58.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_58.setText(_translate("DockWidget", "Inside Stacked Page 2"))
        self.stackedWidgetDis_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.stackedWidgetDis_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.stackedWidgetDis_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_113.setText(_translate("DockWidget", "Inside Stacked Page 1"))
        self.label_114.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_114.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_114.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_114.setText(_translate("DockWidget", "Inside Stacked Page 2"))
        self.label_131.setText(_translate("DockWidget", "Frame"))
        self.frame_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.frame_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.frame_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_9.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_9.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_9.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_9.setText(_translate("DockWidget", "Inside Frame"))
        self.frameDis_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.frameDis_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.frameDis_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_8.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_8.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_8.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_8.setText(_translate("DockWidget", "Inside Frame"))
        self.label_132.setText(_translate("DockWidget", "Widget"))
        self.groupBox_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.groupBox_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.groupBox_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.groupBox_2.setTitle(_translate("DockWidget", "GroupBox"))
        self.label_10.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_10.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_10.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_10.setText(_translate("DockWidget", "Inside GroupBox"))
        self.subwindow1Dis_2.setWindowTitle(_translate("DockWidget", "Subwindow"))
        self.label_111.setText(_translate("DockWidget", "Inside MDI Area 1"))
        self.subwindow2Dis_2.setWindowTitle(_translate("DockWidget", "Subwindow"))
        self.label_112.setText(_translate("DockWidget", "Inside MDI Area 2 "))
        self.label_127.setText(_translate("DockWidget", "GroupBox"))
        self.widget_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.widget_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.widget_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_59.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_59.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_59.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_59.setText(_translate("DockWidget", "Inside Widget"))
        self.widgetDis_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.widgetDis_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.widgetDis_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_125.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_125.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_125.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_125.setText(_translate("DockWidget", "Inside Widget"))
        self.subwindow1_2.setWindowTitle(_translate("DockWidget", "Subwindow"))
        self.label_29.setText(_translate("DockWidget", "Inside MDI Area 1"))
        self.subwindow2_2.setWindowTitle(_translate("DockWidget", "Subwindow"))
        self.label_56.setText(_translate("DockWidget", "Inside MDI Area 2 "))
        self.label_128.setText(_translate("DockWidget", "ScroolArea"))
        self.scrollArea_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.scrollArea_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.scrollArea_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_70.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_70.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_70.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_70.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_71.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_71.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_71.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_71.setText(_translate("DockWidget", "ScroolArea "))
        self.label_75.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_75.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_75.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_75.setText(_translate("DockWidget", "Inside ScroolArea "))
        self.label_76.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_76.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_76.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_76.setText(_translate("DockWidget", "ScroolArea"))
        self.label_77.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_77.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_77.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_77.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_78.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_78.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_78.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_78.setText(_translate("DockWidget", "ScroolArea"))
        self.label_79.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_79.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_79.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_79.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_80.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_80.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_80.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_80.setText(_translate("DockWidget", "ScroolArea"))
        self.label_81.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_81.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_81.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_81.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.scrollAreaDis_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.scrollAreaDis_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.scrollAreaDis_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_115.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_115.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_115.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_115.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_116.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_116.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_116.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_116.setText(_translate("DockWidget", "ScroolArea "))
        self.label_117.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_117.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_117.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_117.setText(_translate("DockWidget", "Inside ScroolArea "))
        self.label_118.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_118.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_118.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_118.setText(_translate("DockWidget", "ScroolArea"))
        self.label_119.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_119.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_119.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_119.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_120.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_120.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_120.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_120.setText(_translate("DockWidget", "ScroolArea"))
        self.label_121.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_121.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_121.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_121.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_122.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_122.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_122.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_122.setText(_translate("DockWidget", "ScroolArea"))
        self.label_123.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_123.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_123.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_123.setText(_translate("DockWidget", "Inside ScroolArea"))
        self.label_129.setText(_translate("DockWidget", "ToolBox"))
        self.toolBox_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.toolBox_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.toolBox_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_60.setText(_translate("DockWidget", "Inside ToolBox Page 1"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_3), _translate("DockWidget", "Page 1"))
        self.label_61.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_61.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_61.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_61.setText(_translate("DockWidget", "Inside ToolBox Page 2"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_8), _translate("DockWidget", "Page 2"))
        self.toolBoxDis_2.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.toolBoxDis_2.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.toolBoxDis_2.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_109.setText(_translate("DockWidget", "Inside ToolBox Page 1"))
        self.toolBoxDis_2.setItemText(self.toolBoxDis_2.indexOf(self.page_6), _translate("DockWidget", "Page 1"))
        self.label_110.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.label_110.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.label_110.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.label_110.setText(_translate("DockWidget", "Inside ToolBox Page 2"))
        self.toolBoxDis_2.setItemText(self.toolBoxDis_2.indexOf(self.page_7), _translate("DockWidget", "Page 2"))
        self.label_130.setText(_translate("DockWidget", "Stacked"))
