# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:54:10 2020

@author: Agraj Gupta
"""

import numpy as np
from scipy.stats import rankdata
from tabulate import tabulate

def main():
    import sys
    import pandas as pd
    filename=sys.argv[1]
    data=pd.read_csv(filename).values
    dMatrix=data[:,1:]
    wt=[int(i) for i in sys.argv[2].split(',')]
    impacts=sys.argv[3].split(',')
    #print(data);
    #print(dMatrix);
    topsis(dMatrix,wt,impacts);

def topsis(dMatrix,wt,impacts):
    m,n =dMatrix.shape
    if len(wt) != n :
        return print("error as the length of weights is not equal to attributes")
    if len(impacts) != n :
        return print("error as length of impacts is not equal to attributes")
    if not all(i > 0 for i in wt) :
        return print("enter positive weights")
    if not all(i=="+"or i=="-" for i in impacts) :
        return print("impacts should be a char vector of '+' and '-' signs")

    w_normalised=np.zeros([m+2,n+4])
    sum_w=sum(wt)

    for i in range(n):
        for j in range(m):
            deno=np.sqrt(sum(dMatrix[:,i]**2))
            fact=(dMatrix[j,i]/deno)
            w_normalised[j,i]=fact*wt[i]/sum_w


    for i in range(n):
        if impacts[i]=='+':
            w_normalised[m,i]=max(w_normalised[:m,i])
            w_normalised[m+1,i]=min(w_normalised[:m,i])
        else:
            w_normalised[m,i]=min(w_normalised[:m,i])
            w_normalised[m+1,i]=max(w_normalised[:m,i])


    for i in range(m):
        w_normalised[i,n]=np.sqrt(sum((w_normalised[m,:n] - w_normalised[i,:n])**2))
        w_normalised[i,n+1]=np.sqrt(sum((w_normalised[m+1,:n] - w_normalised[i,:n])**2))
        w_normalised[i,n+2]=w_normalised[i,n+1]/(w_normalised[i,n]+w_normalised[i,n+1])


    w_normalised[:m,n+3]=len(w_normalised[:m,n+2])-rankdata(w_normalised[:m,n+2]).astype(int)+1
    print(tabulate({"Model":np.arange(1,m+1),"Performance":w_normalised[:m,n+2],"Rank":w_normalised[:m,n+3]},headers="keys"))
if __name__=="__main__":
    main()
