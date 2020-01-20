'''import sys
filename=sys.argv[1]     
weight=sys.argv[2]
impact=sys.argv[3]'''

def topsis():
    import sys
    filename=sys.argv[1]     
    weight_input=sys.argv[2]
    impact_input=sys.argv[3]


    import pandas as pd
    dataset=pd.read_csv(filename)
    X=dataset.iloc[:,1:].values
    weight=weight_input.split(",")
    for i in range(len(weight)):
        weight[i]=int(weight[i])
    impact=impact_input.split(",")
    '''for item in impact:
        float(item)'''

    
    import numpy as np
    import math
    rows=len(X)
    columns=len(X[0])
    sos=[0]*columns
    #weight=0.25
    
    
    for j in range(columns):
        sum=0
        for i in range(rows):
            sum=sum+X[i][j]*X[i][j]
        sos[j]=math.sqrt(sum)
        
    
    for j in range(columns):
        for i in range(rows):
            X[i][j]=(X[i][j]/sos[j])*weight[j]
            
    ideal_best=[0]*columns
    ideal_worst=[0]*columns
    
    for j in range(columns):
        if impact[j]=='+':
            ideal_best[j]=max(X[j])
            ideal_worst[j]=min(X[j])
        else:
            ideal_best[j]=min(X[j])
            ideal_worst[j]=max(X[j])
        
    distance_best=[0]*rows
    distance_worst=[0]*rows
    
    for i in range(rows):
        sum=0
        for j in range(columns):
            sum=sum+(X[i][j]-ideal_best[j])**2
        distance_best[i]=math.sqrt(sum)
            
            
        
    for i in range(rows):
        sum=0
        for j in range(columns):
            sum=sum+(X[i][j]-ideal_worst[j])**2
        distance_worst[i]=math.sqrt(sum)    
    
    performance=[0]*rows  
    for i in range(rows):
        performance[i]=distance_worst[i]/(distance_worst[i]+distance_best[i])
      
    from scipy.stats import rankdata
    rankdata(performance)
    
    array=np.array(performance)    
    temp = array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array))
    
    indices = list(range(len(performance)))
    indices.sort(reverse= True,key=lambda x: performance[x])
    output = [0] * len(indices)
    for i, x in enumerate(indices):
        output[x] = i+1
    print(performance)
    print(output)
    
    
#topsis()
