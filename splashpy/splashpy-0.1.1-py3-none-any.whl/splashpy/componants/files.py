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

import base64
from pathlib import Path


class Files():
    """Various Function to Work with Files"""

    @staticmethod
    def getAssetsPath():
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        return base_path + "/assets"

    @staticmethod
    def getRawContents(path):
        if not Path(path).exists():
            return ""

        with open(path, 'rb') as file:
            return str(base64.b64encode(file.read()), "UTF-8")
