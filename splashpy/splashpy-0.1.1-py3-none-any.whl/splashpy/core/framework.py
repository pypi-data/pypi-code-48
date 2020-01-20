# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from splashpy.componants.config import Config
from splashpy.componants.logger import Logger
from splashpy.models.object import BaseObject
from splashpy.models.widget import BaseWidget
from splashpy.models.client import ClientInfo
from splashpy.models.server import ServerInfo

class Framework:
    """Base Class for Splash Client & Server"""

    __config = None     # Framework general Configuration
    __logger = None     # Splash Logger
    __client = None     # Client module info/description
    __server = None     # Server technical details
    __objects = {}      # Shared Objects Classes
    __widgets = {}      # Shared Widgets Classes

    def __init__(self, identifier, key, objects=None, widgets=None, info=False, server=False, config=False):
        """Init of Splash Mini Framework"""

        # ====================================================================#
        # Init Splash Client Configuration
        Framework.__config = Config(identifier, key)
        # Init Logger
        Framework.__logger = Logger()
        # ====================================================================#
        # Init Client Information
        if isinstance(info, ClientInfo):
            Framework.__client = info
        else:
            Framework.__client = ClientInfo(info)
        # ====================================================================#
        # Init Server Information
        if isinstance(server, ServerInfo):
            Framework.__server = server
        else:
            Framework.__server = ServerInfo(server)
        # ====================================================================#
        # Init Client Available Objects
        if isinstance(objects, list):
            for ws_object in objects:
                Framework.addObject(ws_object)
        # ====================================================================#
        # Init Client Available Widgets
        if isinstance(widgets, list):
            for ws_widget in widgets:
                Framework.addWidget(ws_widget)

    @staticmethod
    def config():
        """Safe Access to Local Configuration"""
        return Framework.__config

    @staticmethod
    def log():
        """Safe Access to Splash Logger"""
        return Framework.__logger

    # ====================================================================#
    # Client Module Management
    # ====================================================================#

    @staticmethod
    def getClientInfo():
        """Safe Access to Client Module Information"""
        return Framework.__client

    @staticmethod
    def setClientInfo(info):
        """Safe Access to Client Module Information"""
        if isinstance(info, ClientInfo):
            Framework.__client = info

    # ====================================================================#
    # Server Details Management
    # ====================================================================#

    @staticmethod
    def getServerDetails():
        """Safe Access to Server Details"""
        return Framework.__server

    @staticmethod
    def setServerDetails(info):
        """Safe Access to Server Details"""
        if isinstance(info, ServerInfo):
            Framework.__server = info

    # ====================================================================#
    # Objects Management
    # ====================================================================#

    @staticmethod
    def addObject(ws_object):
        """Safe Add Objects to Framework"""
        if isinstance(ws_object, BaseObject):
            Framework.__objects[ws_object.getType()] = ws_object

    @staticmethod
    def getObjects():
        """Get List of Available Objects Types"""
        return list(Framework.__objects.keys())

    @staticmethod
    def getObject(object_type):
        """Safe Get Object Class"""
        if object_type not in Framework.__objects:
            return False
        return Framework.__objects[object_type]

    # ====================================================================#
    # Widgets Management
    # ====================================================================#

    @staticmethod
    def addWidget(ws_widget):
        """Safe Add Widget to Framework"""
        if isinstance(ws_widget, BaseWidget):
            Framework.__widgets[ws_widget.getType()] = ws_widget

    @staticmethod
    def getWidgets():
        """Get List of Available Widget Types"""
        return list(Framework.__widgets.keys())

    @staticmethod
    def getWidget(widget_type):
        """Safe Get Widget Class"""
        if widget_type not in Framework.__widget:
            return False
        return Framework.__widgets[widget_type]


