import pandas as pd
import csv
import numpy as np
from numpy import array
from numpy.linalg import norm

# dt=pd.read_csv("data.csv")
# dt.drop(dt.columns[[0]], axis = 1, inplace = True)
# print(dt)
# weight=[1,1,1,1]
# impact=['+','+','-','+']

def function(dt,weight,impact):
    
    #print(len(dt.columns))
    
    for i in range(len(dt.columns)):
        col=dt.iloc[:,i]
        l2=norm(col)
        c=dt.iloc[:,i]/l2
        dt.iloc[:,i]=c
    
    print(dt)
    
    
    
    weight=np.array(weight)
    for i in range(len(weight)):
        dt.iloc[:,i]=dt.iloc[:,i]*weight[i]
        
    print(dt)
    listmax=[]
    listmin=[]
    for i in range(len(weight)):
        if impact[i]=='+':
            listmax.append((dt.iloc[:,i]).max())
            listmin.append((dt.iloc[:,i]).min())
        else:
            listmax.append((dt.iloc[:,i]).min())
            listmin.append((dt.iloc[:,i]).max())
    listmax=np.array(listmax)
    listmin=np.array(listmin)
    
    Splus=[]
    Sminus=[]
    for i in range(len(dt)):
        Splus.append(np.linalg.norm(dt.iloc[i,:]-listmax))
        Sminus.append(np.linalg.norm(dt.iloc[i,:]-listmin))
    Splus=np.array(Splus)
    Sminus=np.array(Sminus)
    
    P=Sminus/(Splus+Sminus)
    
    return P

# V=function(dt,weight,impact)
# print(V)

