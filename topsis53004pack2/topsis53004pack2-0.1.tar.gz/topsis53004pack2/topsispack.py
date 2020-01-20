# -*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import math

def topsis(n,w,p):
    fileName = n #sys.argv[1]
    try:
        dataSet =  pd.read_csv(fileName)
    except FileNotFoundError:
        print(fileName,"doesn't exist")
    
    weight = []
    str1 = []
    a = w #sys.argv[2]
    a = a + (",")
    for c in a:
        if(c != ","):
            str1.append(c)
        else:
            weight.append(float((''.join(str1)))) 
            str1.clear()
        
    weight = np.array(weight)
    print("The weights are:-",weight,"\n")
    
    pref = []
    for c in p: #sys.argv[3]
        if(c == "-"):
            pref.append("-")
        elif(c == "+"):
            pref.append("+")
    print("The preferences are", pref,"\n")
    
    
    featMatrix = dataSet.iloc[:,1:np.size(weight)+1]
    featMatrix = np.array(featMatrix, dtype = float)
    
    print("Feature Matrix :-\n")
    print(featMatrix,"\n")
    
    #Vector Normailsation
    rows = np.size(featMatrix,axis = 0)
    cols = np.size(featMatrix,axis = 1)
    
    rootSq = []
    for i in range(0,cols):
        c = 0.0
        for j in range(0,rows):
            c = c + float(featMatrix[j,i]**2) #[rows,cols]
        rootSq.append(math.sqrt(c))
    
    rootSq = np.array(rootSq)
    
    
    for i in range(0,cols):
        for j in range(0,rows):
            featMatrix[j,i]/=rootSq[i] 
        
    
    
    #Multiplication of weights with the cells
    for i in range(0,cols):
        for j in range(0,rows):
            featMatrix[j,i]*=weight[i] 
    
    #Finding best ideal and best worst
    idealBest = [] 
    idealWorst = [] 
    for i in range(0,cols):
        c = pref[i]
        if(c == "+"):
            idealBest.append(np.amax(featMatrix[:,i]))
            idealWorst.append(np.amin(featMatrix[:,i]))
        elif(c == "-"):
            idealBest.append(np.amin(featMatrix[:,i]))
            idealWorst.append(np.amax(featMatrix[:,i]))
            
    idealBest = np.array(idealBest)
    idealWorst = np.array(idealWorst)
    
    #Finding Euclidean Distances from ideal best and worst
    s_plus = []
    s_minus = []
    
    for i in range(0,rows):
        cb = 0
        cw = 0
        for j in range (0,cols):
            cb += (featMatrix[i,j]-idealBest[j])**2
            cw += (featMatrix[i,j]-idealWorst[j])**2
        s_plus.append(math.sqrt(cb))
        s_minus.append(math.sqrt(cw))
    
    s_plus = np.array(s_plus)
    s_minus = np.array(s_minus)
    
    
    #Finding perfromance scores
    perfScore = []
    for i in range (0,rows):
        perfScore.append((s_minus[i])/(s_plus[i]+s_minus[i]))
        
    print("The performance scores are",perfScore,"\n")
    
    #Picking the desired alternative
    options = dataSet.iloc[:,0].values
    print("\n\n..Choice/Item number",options[perfScore.index(max(perfScore))],"is the best option..") 

if __name__ == "__main__":
    topsis(sys.argv[1],sys.argv[2],sys.argv[3])
    