# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 19:41:35 2020

@author: HP
"""

from topsis import topsis
import pandas as pd
import numpy as np
# df=np.genfromtxt(r'testdata.csv',delimiter=',')
df = pd.read_csv('testdata_singers.csv')
# modelnames=df[:,0].values
data=df.iloc[0:,1:].values
print("Data",data)
#print(type(data))
w=[.20,.20,.20,.20,.20]
i=['+','+','+','+','+']
top=topsis()
ranks = top.topsi(data,w,i)
print("Rank Column:",ranks)
