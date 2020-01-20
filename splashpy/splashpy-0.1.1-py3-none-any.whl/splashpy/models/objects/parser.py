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

from datetime import datetime
from splashpy.core.framework import Framework
from splashpy import const


class SimpleFields():

    def __getSimpleValue( self, index, field_id, target=None ):
        """Read Simple Raw Field Value"""
        try:
            if target is None:
                value = getattr(self.object, field_id)
            else:
                value = getattr(target, field_id)
            self._in.__delitem__(index)
        except Exception as exception:
            Framework.log().error(exception.message)
            return None

        return value

    def __setSimpleValue( self, field_id, field_data, target=None ):
        """Write Simple Raw Field Value"""
        try:
            if target is None:
                setattr(self.object, field_id, field_data)
            else:
                setattr(target, field_id, field_data)
            self._in.__delitem__(field_id)
        except Exception as exception:
            return Framework.log().error(exception.message)

    def getSimple( self, index, field_id, target=None):
        """Read Simple Raw Field"""
        self._out[field_id] = self.__getSimpleValue(index, field_id, target)

    def setSimple( self, field_id, field_data, target=None ):
        """Read Simple Raw Field"""
        self.__setSimpleValue(field_id, field_data, target)

    def getSimpleStr( self, index, field_id, target=None ):
        """Read Simple String Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if value is None:
            value = ""
        self._out[field_id] = str(value)

    def setSimpleBool( self, field_id, field_data, target=None ):
        """Write Simple Bool Field"""
        if not isinstance(field_data, bool) and field_data == "0":
            field_data = False
        self.__setSimpleValue(field_id, bool(field_data), target)

    def getSimpleDate( self, index, field_id, target=None ):
        """Read Simple Date Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if value is None:
            self._out[field_id] = ""
        else:
            self._out[field_id] = value.strftime(const.__SPL_T_DATECAST__)

    def setSimpleDate( self, field_id, field_data, target=None ):
        """Write Simple Date Field"""
        try:
            field_date = datetime.strptime(field_data, const.__SPL_T_DATECAST__)
        except Exception as exception:
            return Framework.log().error(exception.message)

        self.__setSimpleValue(field_id, field_date, target)

    def getSimpleDateTime( self, index, field_id, target=None ):
        """Read Simple DateTime Field"""
        value = self.__getSimpleValue(index, field_id, target)
        if value is None:
            self._out[field_id] = ""
        else:
            self._out[field_id] = value.strftime(const.__SPL_T_DATETIMECAST__)

    def setSimpleDateTime( self, field_id, field_data, target=None ):
        """Write Simple DateTime Field"""
        try:
            field_date = datetime.strptime(field_data, const.__SPL_T_DATETIMECAST__)
        except ValueError:
            return Framework.log().error("Invalid DateTime: " + field_data)
        except Exception as exception:
            return Framework.log().error(exception.message)

        self.__setSimpleValue(field_id, field_date, target)
