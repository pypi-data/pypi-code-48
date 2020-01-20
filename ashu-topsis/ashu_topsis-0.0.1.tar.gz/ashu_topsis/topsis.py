# Made by Ashutosh Gupta(101703118)
import numpy as np
import pandas as pd
class topsis:
    def topsis(filename,weights,impacts):
        data=pd.read_csv(filename)
        x=pd.DataFrame(data.iloc[:,1:])
        y=pd.DataFrame(data.iloc[:,0])
        y=np.array(y)
        x=np.array(x)
    #weights=[0.25,0.25,0.25,0.25]
    #impacts=['+','+','-','+']
        a=[]
        xy=x.shape[1]
        for i in range(0,xy):
            sum=0
            for j in range(0,len(x)):
                sum=sum+(x[j][i]*x[j][i])
            a.append(sum**0.5)

        for i in range(0,len(x)):
            for j in range(0,xy):
                x[i][j]=(x[i][j]/a[j])*weights[j]
        ma=[]
        mi=[]
        for i in range(0,xy):
            m1=0
            m2=1000000
            for j in range(0,len(x)):
                if(x[j][i]>m1):
                    m1=x[j][i]
                if(x[j][i]<m2):
                    m2=x[j][i]
            if(impacts[i]=='+'):
                ma.append(m1)
                mi.append(m2)
            else:
                ma.append(m2)
                mi.append(m1)
        splus=[]
        sminus=[]
        for i in range(0,len(x)):
            sum2=0
            sum1=0
            for j in range(0,xy):
                sum2+=((x[i][j]-ma[j])**2)
                sum1+=((x[i][j]-mi[j])**2)
            splus.append(sum2**0.5)
            sminus.append(sum1**0.5)
        perf=[]

        for i in range(0,len(splus)):
            per=sminus[i]/(sminus[i]+splus[i])
            perf.append(per)
        r1=sorted(perf,reverse=True)
        rank=[(r1.index(v)+1) for v in perf]
        print("Model    Rank")
        g=-1;
        for i in range(0,len(rank)):
            print(y[i]," ",rank[i])
            if(rank[i]==1):
                g=i
        print(y[g],"is the best solution.")
        
#weights=[0.25,0.25,0.25,0.25]       
#impacts=['+','+','-','+']        
#filename="data.csv"
     