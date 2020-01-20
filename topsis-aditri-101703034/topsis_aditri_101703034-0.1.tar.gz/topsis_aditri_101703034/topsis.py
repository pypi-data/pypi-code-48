# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 17:00:32 2020

@author: DELL
"""

import numpy as np
import sys
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from scipy.stats import rankdata
from tabulate import tabulate   
# if not installed already enter command ->pip install tabulate 


def main():
    # Checking proper inputs on command prompt
    if len(sys.argv)!=4:
        print("Incorrect parameters.Input format:python <programName> <dataset> <weights array> <impacts array>")
        exit(1)
    else:
        # Importing dataset
        data = pd.read_csv(sys.argv[1]).values
        # Dropping the first column which is serves as the index in the sample dataset
        data1 = data[:,1:]
        # Initialising the weights array
        w = [int(i) for i in sys.argv[2].split(',')]
        # Initialising the impact array
        imp = sys.argv[3].split(',')
        # y is the last column which contains categorical values in string format in the sample dataset
        y=data1[:,-1]
        # Encoding the categorical values and adding it back to the dataset
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)               
        data1[:,-1]=y                 
        
       
        topsis(data1 , w , imp)
        
        
def topsis(data1,w,imp):
    
    r = data1.shape[0]
    c = data1.shape[1]
    
    if len(w) != c or len(imp) != c or not all(i > 0 for i in w) or not all(i=="+"or i=="-" for i in imp):
        return print("Please check the input arguments.")

    data = np.zeros([r+2,c+4])
    s=sum(w)
    
    for i in range(c):
        for j in range(r):
            data[j,i] = (data1[j,i]/np.sqrt(sum(data1[:,i]**2)))*w[i]/s
    
    for i in range(c):
        data[r,i] = max(data[:r,i])
        data[r+1,i] = min(data[:r,i])
        if i[i] == "-":
            data[r,i] , data[r+1,i] = data[r+1,i] , data[r,i]
    
    for i in range(r):
        data[i,c] = np.sqrt(sum((data[r,:c] - data[i,:c])**2))
        data[i,c+1] = np.sqrt(sum((data[r+1,:c] - data[i,:c])**2))
        data[i,c+2] = data[i,c+1]/(data[i,c] + data[i,c+1])
        
    data[:r,c+3] = len(data[:r,c+2]) - rankdata(data[:r,c+2]).astype(int) + 1
    print(tabulate({"Model": np.arange(1,r+1), "Performance Score": data[:5,c+2], "Rank": data[:5,c+3]}, headers="keys"))
    

if __name__ == "__main__":
    main()
