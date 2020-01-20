import numpy as np
import pandas as pd
import math

class topsis:
    
    def __init__(self,filename):
        data = pd.read_csv(filename)
        self.d = data.iloc[:,1:].values 
        self.d = self.d.astype("float64")
        self.features=len(self .d[0])
        self.samples=len(self.d)

    def evaluate(self,weights,impacts):
        x=self.d
        count_row=self.samples
        count_col=self.features
        if (weights==None):
            weights=[1]*weights
        if (impacts==None):
            impacts=["+"]*impacts
        
        for i in range(0,count_col):
            k = math.sqrt(sum(x[:,i]*x[:,i]))
            for j in range(0,count_row):
                x[j,i]=x[j,i]/k
       
                
        
        for i in range(count_col):
            for j in range(count_row):
                x[j,i]=x[j,i]*float(weights[i])
                
        #Calculation of ideals
        ideal_best=[]
        ideal_worst=[]
        
        maximum_val = np.amax(x, axis=0)
        minimum_val = np.amin(x, axis=0)
        for i in range(count_col):
            if impacts[i] == '+':
                ideal_best.append(maximum_val[i])
                ideal_worst.append(minimum_val[i])
            elif impacts[i] == '-':
                ideal_best.append(minimum_val[i])
                ideal_worst.append(maximum_val[i])
                
        
        
        a=[]
        b=[]
        for i in range(0,count_row):
            temp1 = math.sqrt(sum((x[i]-ideal_worst)*(x[i]-ideal_worst)))
            a.append(temp1)
            temp2 = math.sqrt(sum((x[i]-ideal_best)*(x[i]-ideal_best)))
            b.append(temp2)
    
        
            
        #Calculating Perforance or P's
        p=[]
        
        for i in  range(count_row):
            temp=a[i]/(a[i]+b[i])
            p.append(temp)
            
        #Assigning Ranks and choosing the best
        return p