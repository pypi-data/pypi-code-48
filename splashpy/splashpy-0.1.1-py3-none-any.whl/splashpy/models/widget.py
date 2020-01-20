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

from splashpy.models.widgets.interfaces import WidgetInterface


class BaseWidget(WidgetInterface):

    # ====================================================================#
    # Constants Definition
    # ====================================================================#

    __SIZE_XS__ = "col-sm-6 col-md-4 col-lg-3"
    __SIZE_SM__ = "col-sm-6 col-md-6 col-lg-4"
    __SIZE_DEFAULT__ = "col-sm-12 col-md-6 col-lg-6"
    __SIZE_M__ = "col-sm-12 col-md-6 col-lg-6"
    __SIZE_L__ = "col-sm-12 col-md-6 col-lg-8"
    __SIZE_XL__ = "col-sm-12 col-md-12 col-lg-12"

    # ====================================================================#
    # Widget Definition
    # ====================================================================#

    name = "Widget"
    desc = "Widget"
    icon = "fas fa-info"
    fields = {}
    blocks = {}
    options = {}
    parameters = {}
    out = {}
    disabled = False

    # ====================================================================#
    # COMMON CLASS INFORMATION
    # ====================================================================#

    def getType( self ):
        """Get Widget Type"""
        return self.__class__.__name__

    def getName( self ):
        """Get Widget Type Name"""
        return self.name

    def getDescription( self ):
        """Get Widget Type Description"""
        return self.desc

    def getIcon( self ):
        """Get Widget Type FontAwesome 5 Icon"""
        return self.icon

    def getOptions( self ):
        """Get Widget Default Options"""
        return self.options

    def getParameters(self):
        """Get Widget Default Parameters"""
        return self.parameters

    def description( self ):
        """Get Ws Widget Description"""
        # Build & Return Widget Description Array
        return {
            # ====================================================================#
            # General Widget definition
            # ====================================================================#
            # Widget Type Name
            "type": self.getType(),
            # Widget Display Name
            "name": self.getName(),
            # Widget Description
            "description": self.getDescription(),
            # Widget Icon Class (Font Awesome 5. ie "fas fa-user")
            "icon": self.getIcon(),
            # Is This Widget Enabled or Not?
            "disabled": self.isDisabled()
        }

    def isDisabled( self ):
        """Check if Object is Disabled"""
        return self.disabled

    # ====================================================================#
    # COMMON CLASS SETTERS
    # ====================================================================#
