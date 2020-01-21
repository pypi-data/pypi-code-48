# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 00:05:05 2020

@author: Tarit
"""

import pandas as pd

def calbest(ds,weights,pn):
    #find root of sum of squares of each column
    rsum=[0]
    n=len(ds.columns)
    for i in range(1,n):
        temp=0
        for j in ds.iloc[:,i]:
            temp=temp+pow(j,2)
        rsum.append(pow(temp,0.5))
        
    #divide each element by the above value for each column
    for i in range(1,n):
        counter=0
        for j in ds.iloc[:,i]:
            ds.iloc[counter,i]=ds.iloc[counter,i]/rsum[i]
            counter=counter+1
    m=counter

    #calculate weight for each column
    temp=0
    counter=0
    for num in weights:
        temp=temp+int(num)
    for num in weights:
        weights[counter]=int(weights[counter])/temp
        counter=counter+1

    #multiply each value by respective weights
    for i in range(1,n):
        counter=0
        for j in ds.iloc[:,i]:
            ds.iloc[counter,i]=ds.iloc[counter,i]*weights[i-1]
            counter=counter+1

    #calculate ideal best and ideal worst values
    vbest=[0]
    vworst=[0]
    for i in range(1,n):
        if pn[i-1]=='+':
            vbest.append(ds.iloc[:,i].max())
            vworst.append(ds.iloc[:,i].min())
        else:
            vbest.append(ds.iloc[:,i].min())
            vworst.append(ds.iloc[:,i].max())

    #find euclidean distances from best and worst values   
    sbest=[]
    sworst=[]
    for i in range(0,m):
        tb=0
        tw=0
        for j in range(1,n):
            tb=tb+pow(ds.iloc[i,j]-vbest[j],2)
            tw=tw+pow(ds.iloc[i,j]-vworst[j],2)
        sbest.append(pow(tb,0.5))
        sworst.append(pow(tw,0.5))

    #find performance score
    best=0
    bindex=0
    p=[]
    for i in range(0,m):
        p.append(sworst[i]/(sworst[i]+sbest[i]))
        if p[i]>best:
            bindex=i
            best=p[i]
    return bindex