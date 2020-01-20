import argparse as ag 
import pandas as pd
import numpy as np

parser=ag.ArgumentParser(description='TOPSIS Implementation')

parser.add_argument('file_name',nargs=1,help="Enter file name with .csv extension")
parser.add_argument('weights',nargs=4,type=float,help="Enter weights separated by spaces for each of 4 columns")
parser.add_argument('impacts',nargs=1,help="Enter impacts preceding and succeeding with any character <without spaces> for each of 4 columns\n Example a-+++b where a and b are any characters")
args=parser.parse_args()
lst=[]

df=pd.read_csv(args.file_name[0])
# df=df.iloc[0:5]
# print(df)
for i in range(df.shape[1]):
	lst.append(np.sqrt(np.sum(df.iloc[:,i]**2)))
	df.iloc[:,i]=df.iloc[:,i]/lst[i]

weights=args.weights
for i in range(df.shape[1]):
	df.iloc[:,i]=df.iloc[:,i]*weights[i]

normalized_best=[]
normalized_worst=[]
impacts=args.impacts[0]
impacts=impacts[1:-1]
# print(impacts)

for i in range(df.shape[1]):
	if impacts[i]=='+':
		normalized_best.append(df.iloc[:,i].max())
		normalized_worst.append(df.iloc[:,i].min())
	elif impacts[i]=='-':
		normalized_best.append(df.iloc[:,i].min())
		normalized_worst.append(df.iloc[:,i].max())
	else:
		print("Enter valid impacts. Either + or - without spaces.\n Example: ++-+")

# print(normalized_best)
# print(normalized_worst)

lst_pos=pd.Series()
lst_neg=pd.Series()
lst_pos=np.square(df.iloc[:,0]-normalized_best[0])
lst_neg=np.square(df.iloc[:,0]-normalized_worst[0])
for i in range(1,4):
	lst_pos=lst_pos+np.square(df.iloc[:,i]-normalized_best[i])
	lst_neg=lst_neg+np.square(df.iloc[:,i]-normalized_worst[i])

lst_pos=np.sqrt(lst_pos)
lst_neg=np.sqrt(lst_neg)

df.insert(df.shape[1],"S+",lst_pos)
df.insert(df.shape[1],"S-",lst_neg)
df.insert(df.shape[1],"Performance_Score",df['S-']/(df['S+']+df['S-']))
df['Rank']=df['Performance_Score'].rank(ascending=False)
print(df)


