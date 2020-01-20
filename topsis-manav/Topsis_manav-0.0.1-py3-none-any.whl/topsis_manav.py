import sys
import numpy as np
import math as ma
import pandas as pd
def main():
    script=sys.argv[0]
    filename=sys.argv[1]
   # w=sys.argv[3]
    w=sys.argv[2]
    w=w.split(",") 
    w=[float(i) for i in w]
         
    c1=sys.argv[3]
    dataset=pd.read_csv(filename)
    x=dataset.iloc[:,1:]
    k=dataset.iloc[:,0]
    k=list(k)
    import math as m
    x=x.as_matrix()
    a=[0]*10000
    (r,c)=x.shape
    for i in range(0,r):
        for j in range(0,c):
            a[j]=a[j]+x[i][j]**2
    for i in range(0,c):
        a[i]=m.sqrt(a[i])
    for i in range(0,r):
        for j in range(0,c):
            x[i][j]=(x[i][j]/a[j])*w[j]
    c_be=[]
    c_wo=[]
    for i in range(0,c):
        if(c1[i]=='+'):
            c_be.append([max(s) for s in zip(*x)][i])
            c_wo.append([min(s) for s in zip(*x)][i])
        else:
            c_be.append([min(s) for s in zip(*x)][i])
            c_wo.append([max(s) for s in zip(*x)][i])
    m_be=[0]*10000
    m_wo=[0]*10000
    for i in range(0,r):
        for j in range(0,c):
            m_be[i]=m_be[i]+(x[i][j]-c_be[j])**2
            m_wo[i]=m_wo[i]+(x[i][j]-c_wo[j])**2
    for i in range(0,r):
        m_be[i]=m.sqrt(m_be[i])
        m_wo[i]=m.sqrt(m_wo[i])
    y=[]
    for i in range(0,r):
        y.append(m_be[i]+m_wo[i])
    p=[]
    for i in range(0,r):
        p.append(m_wo[i]/y[i])
    print(k," ")
    print(" has these performance scores")
    print(p)
main()# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

