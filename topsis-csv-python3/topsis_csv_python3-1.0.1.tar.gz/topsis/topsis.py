import sys
import pandas as pd
import math

class topsis:
	def read_file(self):
		try:
			return pd.read_csv(self.filename)
		except IOError:
			raise Exception("Check filename!!")

	def inDigit(self,x):
		try:
			return float(x)
		except ValueError:
			raise Exception("Weights: Enter numeric values!!")

	def isCategorical(x):
		try:
			float(x)
			return False
		except ValueError:
			return True

	def calc(self):
		i=0
		self.weights = self.weights.split(",")
		self.impacts = self.impacts.split(",")
		dataset = self.read_file()
		for p in range(len(self.weights)):
			self.weights[p] = self.inDigit(self.weights[p])
		s = sum(self.weights)
		self.weights[:] = [x/s for x in self.weights]
		if(dataset.iloc[0][0]):
			data = pd.DataFrame(dataset.iloc[:,1:])
		else:
			data = dataset
		if(len(self.weights)<len(data.columns)):
			raise Exception("weights are less in number!!")
		if(len(self.impacts)<len(data.columns)):
			raise Exception("Impacts are less in number!!")
		best = []
		worst = []
		for column in data.columns:
			sq = data[column].pow(2).sum()
			sq = math.sqrt(sq)
			data[column] = data[column]*self.weights[i]/sq
			if(self.impacts[i]=='+'):
				best.append(data[column].max())
				worst.append(data[column].min())
			elif(self.impacts[i]=='-'):
				best.append(data[column].min())
				worst.append(data[column].max())
			else:
				raise Exception("Impacts: Invalid input")
			i+=1
		plus=0
		plus_worst=0
		sum_all=[]
		column = len(data.columns)
		row = len(data)
		for x in range(row):
			for y in range(column):
				plus+=(data.iloc[x][y]-best[y])**2
				plus_worst+=(data.iloc[x][y]-worst[y])**2
			plus_worst = math.sqrt(plus_worst)
			plus = math.sqrt(plus) + plus_worst
			sum_all.append(plus_worst/plus)
		sum_all = pd.DataFrame(sum_all)
		sum_all = sum_all.rank(method='first',ascending=False)
		sum_all.columns = ['Rank']
		dataset.insert(column+1,"Rank",sum_all,allow_duplicates=False)
		print(dataset)
		dataset .to_csv(r'ordered.csv')


	def __init__ (self,filename,weights,impacts):
		self.filename = filename
		self.weights = weights
		self.impacts = impacts
		self.calc()

def main(filename,weights,impacts):
	t = topsis(filename,weights,impacts)

if __name__ == '__main__':
	filename = sys.argv[1]
	weights = sys.argv[2]
	impacts = sys.argv[3]
	main(filename,weights,impacts)