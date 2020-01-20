# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 23:28:28 2020

@author: Arpit Singla
"""

import math
import pandas as pd
import sys

def topsis(arglist):
    dataset=pd.read_csv(arglist[0])
    dataset=dataset.iloc[:,1:]
    
    for col in dataset:
        x_denom=math.sqrt(sum(x*x for x in dataset[col]))
        dataset[col]=dataset[col]/x_denom
        
    weights=list(map(int,arglist[1].split(',')))
    weights=[float(x)/sum(weights) for x in weights]
    temp=0
    
    for col in dataset:
        dataset[col]=dataset[col]*weights[temp]
        temp=temp+1
        
    impacts=list(arglist[2].split(','))
    vpos=[]
    vneg=[]
    temp=0
    
    for col in dataset:
        if impacts[temp]=="+":
            vpos.append(max(dataset[col]))
            vneg.append(min(dataset[col]))
        else:
            vpos.append(min(dataset[col]))
            vneg.append(max(dataset[col]))
        temp=temp+1
        
    pscore=dict()
    for row in dataset.itertuples(index=False):
        temp=0
        eucdisp=0
        eucdisn=0
        for x in row:
            eucdisp=eucdisp+(x-vpos[temp])*(x-vpos[temp])
            eucdisn=eucdisn+(x-vneg[temp])*(x-vneg[temp])
            temp=temp+1
        eucdisp=math.sqrt(eucdisp)
        eucdisn=math.sqrt(eucdisn)
        pscore[row]=(eucdisn/(eucdisp+eucdisn))
        
    a=list(pscore.values())
    b=sorted(list(pscore.values()),reverse=True)
    
    ranked_scores=dict()
    for i in range(len(a)):
        ranked_scores[(b.index(a[i]))+1]=a[i]
        b[b.index(a[i])]=-b[b.index(a[i])]

    row_number=list(i+1 for i in range(len(b)))
    a=list(ranked_scores.values())
    rank=list(ranked_scores.keys())

    out={'Row_No':row_number, 'Performance_Score':a, 'Rank':rank}

    output=pd.DataFrame(out)
    print(output)
    
if __name__ == "__main__":
    sysarglist = sys.argv
    sysarglist.pop(0) 
    topsis(sysarglist)
    
    
    