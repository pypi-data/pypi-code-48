#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gimbiseo import *
import sys

memory = ChineseMemory()
d = Dialogue()
with d.base:
    app = QApplication(sys.argv)
    dui=DialogueUI(d)
    dui.show()
    os.system("pause")
    sys.exit(app.exec_())