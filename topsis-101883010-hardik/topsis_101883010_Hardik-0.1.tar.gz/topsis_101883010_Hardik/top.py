import numpy as np
import math


def topsis(name,we,im):
    data = np.genfromtxt(name,delimiter=',')
    da = np.array(data,dtype = float)
    
    impact=list(im.split(","))
    
    li = list(we.split(",")) 
    w= []
    for item in li:
        w.append(float(item))
    

    s = da.shape
    
    c = s[1]
    r = s[0]
    
    pl = []
    minu = []
    
    spl = []
    sminu = []
    
    for i in range(c):
        s1 = 0
        for j in range(r):
            s1 += da[j][i]**2
        s1 = math.sqrt(s1)
        
        maxx = 0
        minn =1 
        for j in range(r):
            da[j][i] = (da[j][i]/s1)*w[i]
            if da[j][i] > maxx:
                maxx = da[j][i]
            if da[j][i] < minn:
                minn = da[j][i]
  
        pl.append(maxx)
        minu.append(minn)

    for i in range(c):
        if impact[i] == '-':
            pl[i],minu[i] = minu[i],pl[i]

    for i in range(r):
        p = 0
        q = 0
        for j in range(c):
            p += (da[i][j] - pl[j])**2
            q += (da[i][j] - minu[j])**2
        spl.append(math.sqrt(p))
        sminu.append(math.sqrt(q))

        
        
    hh = []
    
    for i in range(len(spl)):
        hh.append(sminu[i]/(sminu[i]+spl[i]))
        
    nn = np.array(hh)
    
    def rankify_improved(A): 
        R = [0 for i in range(len(A))] 
        T = [(A[i], i) for i in range(len(A))] 
        T.sort(key=lambda x: x[0]) 
        (rank, n, i) = (1, 1, 0) 
  
        while i < len(A): 
            j = i 
  
    
            while j < len(A) - 1 and T[j][0] == T[j + 1][0]: 
                j += 1
            n = j - i + 1
      
            for j in range(n): 
                idx = T[i+j][1] 
                R[idx] =(rank + (n - 1) * 0.5)
      
            rank += n 
            i += n 
      
        return R

    a=rankify_improved(hh)
    h=len(a)
    ranks=[]
    for xx in a:
        ranks.append(int((h-xx)+1))
        
    
    return ranks,nn

