import sys
import math
import numpy as np
import pandas as pd


def topsis_fun(file,wght,impact):
    try:
        mat=pd.read_csv(file)
    except FileNotFoundError:
        raise Exception("File does not exist")
    
    #print(mat)
    
    row_count=mat.shape[0]
    col_count=mat.shape[1]
    if(len(wght)<col_count-1 and len(impact)<col_count-1):
        raise Exception("less number of weights and impacts assigned")
    if(len(wght)>col_count-1 and len(impact)>col_count-1):
        raise Exception("more number of weights and impacts assigned")
    if(len(wght)<col_count-1):
        raise Exception("less number of weights assigned")
    if(len(wght)>col_count-1):
        raise Exception("more number of weights assigned")

    if(len(impact)<col_count-1):
        raise Exception("less number of impacts assigned")
    if(len(impact)>col_count-1):
        raise Exception("more number of impacts assigned")



    sa=np.zeros(shape=(row_count, col_count))
    mat.astype('float32')
    #normalising
    x=[]
    for i in range(1,col_count):
        s=0
        for j in range(row_count):
            s=s+float(mat.iloc[j][i]**2)
        s=float(math.sqrt(s))
        x.append(s)
    
    for i in range(1,col_count):
        for j in range(row_count):
            if(float(x[i-1])==0.0):
                raise Exception("Division by zero not possible.")
            a=mat.iloc[j,i]/float(x[i-1])
            mat.iloc[j,i]=a
    
    for i in range(1,col_count):
        for j in range(row_count):
            a=mat.iloc[j,i]*wght[i-1]
            mat.iloc[j,i]=a
    
    #calculating ideal best and worst
    best=[]
    worst=[]
    
    for i in range(1,col_count):
        if impact[i-1]=='+':
            best.append(mat.iloc[:,i].max())
            worst.append(mat.iloc[:,i].min())
        else:
            worst.append(mat.iloc[:,i].max())
            best.append(mat.iloc[:,i].min())
    
    #euclidean distance
    
    total=[]
    performance=[]
    for i in range(row_count):
        sum_pos=sum((mat.iloc[i,1:]-best[:])**2)
        sum_neg=sum((mat.iloc[i,1:]-worst[:])**2)
           
        sum_pos=math.sqrt(sum_pos)
        sum_neg=math.sqrt(sum_neg)
        sums=sum_pos + sum_neg
        perf=sum_neg/sums
        performance.append(perf)
       
    rank1=max(performance)
    ind=performance.index(rank1)
    
    return rank1,mat.iloc[ind,0]
    

if(len(sys.argv)<4):
    raise Exception("Less inputs given")

if(len(sys.argv)>4):
    raise Exception("More inputs given")

filename=sys.argv[1]
weights=sys.argv[2]
impact=sys.argv[3]

w = list(weights.split(","))
w1=[float(i) for i in w]
im=list(impact.split(","))


for i in im:
    if(i=='+' or i=='-'):
        pass
    else:
        raise Exception("Invalid impact input")


ans,ind1=topsis_fun(filename, w1, im)

print(" The most favourable is: ",ind1," with performance value according to TOPSIS: ", ans)