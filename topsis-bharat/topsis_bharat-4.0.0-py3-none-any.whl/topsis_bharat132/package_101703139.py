import pandas as pd
import math
import sys



def file(filename):
    try:
        return pd.read_csv(filename)
    except IOError:
        raise Exception("Datafile doesn't exist\n")
        
def digit(i):
    try:
        return float(i)
    except ValueError:
        raise Exception("Enter numeric Data\n")
        
def main():
    filename = sys.argv[1]
    weight = sys.argv[2]
    impact = sys.argv[3]
    dataset = file(filename)
    
    x = pd.DataFrame(dataset.iloc[:,1:].values)
    '''weight = input("enter weight")'''
    
    weight_int = weight.split(",")
    
    for i in range(0,len(weight_int)):
        weight_int[i] = digit(weight_int[i])
    if(len(weight)<len(x.columns)):
        raise Exception("Number of weights are less than number of columns \n")
    weight_int = [float(i) for i in weight_int]
    total=0
    for i in range(0,len(weight_int)):
        total = total + weight_int[i]
        
    'total = sum(weight_int)'
    weight_int = [float(i/total) for i in weight_int]
    
    '''impact = input("enter impact")'''
    impact = impact.split(",")
    if(len(impact)<len(x.columns)):
        raise Exception("Number of impact parameter is less than number of columns\n")
 
    
    v_plus=[]
    v_minus=[]
    
    for column in x.columns:
        square = x[column].pow(2).sum()
        square = math.sqrt(square)
        x[column]=x[column]*weight_int[column]/square
        if(impact[column] == '+'):
            v_plus.append(x[column].max())
            v_minus.append(x[column].min())
        elif(impact[column] == '-'):
            v_plus.append(x[column].min())
            v_minus.append(x[column].max())
    
    row_length = len(x)
    
    p=[]
    
    for i in range(row_length):
        a_plus = 0
        a_minus = 0
        for j in x.columns:
            a_plus =a_plus+ (x.iloc[i,j]-v_plus[j])**2
            a_minus = a_minus+ (x.iloc[i,j]-v_minus[j])**2
        a_plus = math.sqrt(a_plus)
        a_minus = math.sqrt(a_minus)
        a_plus = a_plus+a_minus
        p.append(a_minus/(a_plus))
    
    d = pd.DataFrame(p)
    d = d.rank(method = 'first', ascending = False)
    
    p = pd.DataFrame(p)
    p.columns = ['Performance']
    print(p)
    #print("Rank of items is \n")
    d.columns = ['Rank']
    print(d)
    #m = d.min()
    index = 0
    min_element = d.iloc[0,0]
    for i in range(1,len(d)):
        if(d.iloc[i,0]<min_element):
            index = i
            min_element = d.iloc[i,0]
            
    print("Best choice is item %d"% (index+1))
    
