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

from splashpy import const
from splashpy.routers.base import BaseRouter
from splashpy.core.framework import Framework


class WidgetsRouter(BaseRouter):

    def execute(self, task):

        response = self.empty_response(task)

        # READING OF SERVER WIDGETS LIST
        if task['name'] == const.__SPL_F_WIDGET_LIST__:
            response['data'] = Framework.getWidgets()
            response['result'] = True

        # READING OF SERVER WIDGETS DEFINITION
        if task['name'] == const.__SPL_F_WIDGET_DEFINITION__:
            Framework.log().error("Widget Router - NOT Implemented Yet... ")
            response['data'] = {}
            response['result'] = True

        # READING OF SERVER WIDGETS CONTENTS
        if task['name'] == const.__SPL_F_WIDGET_GET__:
            Framework.log().error("Widget Router - NOT Implemented Yet... ")
            response['data'] = {}
            response['result'] = True

        return response
