from numpy import genfromtxt

def topsis(csv,w,ne):
    a = genfromtxt(csv, delimiter=',')
    su = []
    n,m = a.shape
    for i in range(m):
        s=0
        for j in range(n):
            s+=a[j][i]**2
        s=s**.5
        su.append(s)
    for i in range(m):
        for j in range(n):
            a[j][i]=(a[j][i]/su[i])*w[i]
    vb=[]
    vw=[]
    for i in range(m):
        if(ne[i]>0):
            vb.append(max(a[:,i]))
            vw.append(min(a[:,i]))
        else:
            vb.append(min(a[:,i]))
            vw.append(max(a[:,i]))
    sb=[]
    for i in range(n):
        sum1=0
        for j in range(m):
            sum1+=(vb[j]-a[i,j])**2
        sb.append(sum1**0.5)
    sw=[]
    for i in range(n):
        sum1=0
        for j in range(m):
            sum1+=(vw[j]-a[i,j])**2
        sw.append(sum1**0.5)
    p=[]
    for i in range(n):
        p.append(sw[i]/(sw[i]+sb[i]))
    k=[]
    for i in range(n):
        k.append(p[i])
    k.sort()
    rank = p
    for i in range(n):
        for j in range(n):
            if(k[i] is p[j]):
                rank[j]=m-i+1
    return rank