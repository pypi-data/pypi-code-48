def topsis(file, weights, impacts):
    import pandas as pd
    import sys
    datafile=file
    if(len(weights)!=len(impacts)):
        print("Number of elements in weights and impacts should be same")
        sys.exit(0)
    wt=weights
    imp=impacts
    data=pd.read_csv(datafile)
    x=data.iloc[:,1:].values
    n=len(data.columns)
    m=len(data)
    temp=[]
    for i in range(0,n-1):
        s=0
        for j in range(0,m):
            s=s+pow(x[j][i],2)
        temp.append(pow(s,0.5))
    for i in range(0,n-1):
        for j in range(0,m):
            x[j][i]/=temp[i]
    sum=0
    wt= [int(i) for i in wt]
    for i in range(0,n-1):
        sum=sum+wt[i]
    for i in range(0,n-1):
        wt[i]/=sum
    for i in range(0,n-1):
        for j in range(0,m):
            x[j][i]*=wt[i]
    best=[]
    wors=[]
    for i in range(0,n-1):
        ma=x[0][i]
        mi=x[0][i]
        for j in range(0,m-1):
            if ma<x[j+1][i]:
                ma=x[j+1][i]
            if mi>x[j+1][i]:
                mi=x[j+1][i]
        if imp[i]=='+':
            best.append(ma)
            wors.append(mi)
        else:
            best.append(mi)
            wors.append(ma)
    smax=[]
    smin=[]
    for i in range(0,m):
        ss=0
        ss1=0
        for j in range(0,n-1):
            ss=ss+pow(x[i][j]-best[j],2)
            ss1=ss1+pow(x[i][j]-wors[j],2)
        smax.append(pow(ss,0.5))
        smin.append(pow(ss1,0.5))
    p=[]
    for i in range(0,m):
        p.append(smin[i]/(smax[i]+smin[i]))
    data['Performance']=p
    data['Rank']=data['Performance'].rank(ascending=False)
    print(data)
    y=data.iloc[:,[0,-1]].values
    for i in range(0,m):
        if(y[i][1]==float(1)):
            print("The best model is",y[i][0] )