# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:15:37 2020

@author: Anurag Agarwal
"""

import topsis_avani_code as tp
import pandas as pd
import numpy as np
dataset= tp.topsis("IDOLS.csv")

weights=[1,2,1,1,1]
impacts=["+","+","-","+","+"]
result =tp.topsis.evaluate(dataset,weights,impacts)
x = result
seq = sorted(x)
index = [seq.index(v)+1 for v in x]

print(index)