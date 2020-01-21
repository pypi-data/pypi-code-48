# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:06:43 2020

@author: navee
"""

import pandas as pd
import numpy as np
import sys # To read arguments from command line

# Reading the dataset
x = pd.read_csv(sys.argv[1])
shape = x.shape
rows = shape[0]
cols = shape[1]

Attributes = x.iloc[:,0].values # Attribute names
matrix = x.iloc[:,1:cols].values 

weights_temp = sys.arg[2]  # Weights assigned to columns
weights = weights_temp.split(',')  # Converting string to array
for i in range(0,len(weights)):
    weights[i] = float(weights[i])
#print(weights)

level = sys.argv[3]  # State of the column
lvl = level.split(',')  # Converting string to array
#print(lvl)

# Vector normalisation formula
vector_nor = np.sqrt(np.sum(np.square(matrix), axis=0))

# Normalised Matrix
nor_matrix = matrix/vector_nor

# Weighted Normalised Matrix
weighted_matrix = nor_matrix*weights

aw = [] # Worst Alternative
ab = [] # Best Alternative

# Calculating the ideal best and worst for all columns
for i in range(0,cols-1):
    if lvl[i] == '+':
        aw.append(min(weighted_matrix[:,i]))
        ab.append(max(weighted_matrix[:,i]))
    else:
        aw.append(max(weighted_matrix[:,i]))
        ab.append(min(weighted_matrix[:,i]))

# Calculating the euclidean distance for each attribute
sPlus = np.sqrt(np.sum(np.square(weighted_matrix-ab),axis=1))
sMinus = np.sqrt(np.sum(np.square(weighted_matrix-aw),axis=1))              

# Calculating the performance of each Attribute
performance_score = []
performance_score = sMinus/(sMinus+sPlus)
result = np.max(performance_score) # The best performer

# Getting the index of the best performer
for i in range(0,len(performance_score)):
    if performance_score[i] == result:
        index=i
print("Object selected : ", Attributes[index])
print("Best Performance Score: ", result )
