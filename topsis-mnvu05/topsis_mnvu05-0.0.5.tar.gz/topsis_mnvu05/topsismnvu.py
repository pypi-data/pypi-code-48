import numpy as np
import pandas as pd
import sys
import logging

if(len(sys.argv)<4):
    logging.error("Not enough arguments provided for the program to work!!")
    sys.exit()
    
    
weights=str(sys.argv[2])
weights=list(map(float,weights.split(",")))
impacts=str(sys.argv[3])
impacts=list(map(str,impacts.split(",")))

data=pd.read_csv(sys.argv[1])


s=sum(weights)
if(s!=1):
    for i in range(len(weights)):
        weights[i]/=s

cols=list(data.columns)

col_sum=list()
for col in cols:
    s=0
    for d in data[col]:
        s+=(d*d)
        s=pow(s,0.5)
    col_sum.append(s)
    
    
norm=np.array(col_sum)
decision_matrix=np.array(data)
n_decision_matrix=np.true_divide(decision_matrix,norm)
w_decision_matrix=np.multiply(n_decision_matrix,weights)

ideal_positive=np.amax(w_decision_matrix,axis=0)
ideal_negative=np.amin(w_decision_matrix,axis=0)
for i in range(len(impacts)):
    if(impacts[i]=='-'):
        temp=ideal_positive[i]
        ideal_positive[i]=ideal_negative[i]
        ideal_negative[i]=temp

dist_from_pos=list()
dist_from_neg=list()
for i in range(len(data[cols[0]])):
    s=0
    for j in range(len(cols)):
        s+=pow((w_decision_matrix[i][j]-ideal_positive[j]),2)
    dist_from_pos.append(float(pow(s,0.5)));

for i in range(len(data[cols[0]])):
    s=0
    for j in range(len(cols)):
        s+=pow((w_decision_matrix[i][j]-ideal_negative[j]),2)
    dist_from_neg.append(float(pow(s,0.5)));

    
performance_score=dict()
for i in range(len(data[cols[0]])):
    s=dist_from_neg[i]/(dist_from_pos[i]+dist_from_neg[i])
    performance_score[i+1]=s


a=list(performance_score.values())
b=sorted(list(performance_score.values()),reverse=True)


ranked_scores=dict()
for i in range(len(a)):
    ranked_scores[(b.index(a[i]))+1]=a[i]
    b[b.index(a[i])]=-b[b.index(a[i])]


row_number=list(i+1 for i in range(len(b)))
a=list(ranked_scores.values())
rank=list(ranked_scores.keys())

out={'Row_No':row_number, 'Performance_Score':a, 'Rank':rank}

output=pd.DataFrame(out)
print(output)
