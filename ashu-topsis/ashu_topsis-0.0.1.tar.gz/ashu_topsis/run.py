# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 21:00:30 2020

@author: ashu
"""
# Made by Ashutosh Gupta(101703118)
import numpy as np
import pandas as pd
import sys
import topsis as tp
argList=sys.argv
file=argList[1]
we=argList[2]
we=list(we.split(","))
we = [float(i) for i in we]
cv=sum(we)
weights=[i/cv for i in we]
imp=argList[3]
impacts=list(imp.split(","))
#print(we)
#print(imp)
tp.topsis(file,weights,impacts)  