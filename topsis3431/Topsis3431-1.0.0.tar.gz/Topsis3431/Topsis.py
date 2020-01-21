# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 23:02:23 2020

@author: Rakshit
"""
def Topsis(file,weights,impact):
        import pandas as pd
        file=file
        wt=weights
        ip=impact
        wt=list(map(float,wt))
        data=pd.read_csv(file)
        x=data.iloc[:,1:].values
        m=len(data)
        n=len(data.columns)
        temp=[]
        for j in range(1,n):
            a=data.iloc[:,j].values
            sum=0
            for i in range (0,m):
                sum=sum+a[i]**2
            temp.append(sum**0.5)
        for j in range(0,n-1):
            for i in range(m):
                x[i,j]/=temp[j]
        for j in range(0,n-1):
            for i in range(m):
                x[i,j]*=wt[j]
        wa=[]
        ba=[]
        for j in range(0,n-1):
            if ip[j]=="+":
                wa.append(min(x[:,j]))
                ba.append(max(x[:,j]))
            else:
                wa.append(max(x[:,j]))
                ba.append(min(x[:,j]))
        edb=[]
        edw=[]
        from scipy.spatial import distance
        for i in range(m):
            edb.append(distance.euclidean(x[i,:],ba))
            edw.append(distance.euclidean(x[i,:],wa))
        p=[]
        best=0
        for i in range(m):
            p.append(edw[i]/(edw[i]+edb[i]))
            if p[i]>best:
                best=p[i]
                bindex=i
        df=data.assign()
        df['Score']=p
        df['Rank']=df['Score'].rank(ascending=False)
        print(df)
        return df.iat[bindex,0]