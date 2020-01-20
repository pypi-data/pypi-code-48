# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 21:43:37 2020

@author: acer
"""

import numpy as np
import sys
import csv
import argparse
def step1(dec_matrix):
    sqrtSum=np.sqrt(np.sum(np.square(dec_matrix),axis=0))
    dec_matrix=dec_matrix/sqrtSum
    return (dec_matrix)

def step2(dec_matrix,weights):
    return dec_matrix*weights

def step3a(dec_matrix,impact):
    col=len(dec_matrix[0])
    row=len(dec_matrix)
    minValues=np.min(dec_matrix, axis=0) 
    maxValues=np.max(dec_matrix, axis=0)
    
    idealSol=np.zeros((1,col))
    for i in range(0,col):
        if(impact[i]==1):
            idealSol[0][i]=maxValues[i]
        else:
            idealSol[0][i]=minValues[i]
    return idealSol
        
def step3b(dec_matrix,impact):
    col=len(dec_matrix[0])
    row=len(dec_matrix)
    minValues=np.min(dec_matrix, axis=0) 
    maxValues=np.max(dec_matrix, axis=0)
    
    negIdealSol=np.zeros((1,col))
    for i in range(0,col):
        if(impact[i]==1):
            negIdealSol[0][i]=minValues[i]
        else:
            negIdealSol[0][i]=maxValues[i]
    return negIdealSol 
    
def step4a(idealSol,dec_matrix):
    return np.sqrt(np.sum(np.square(dec_matrix-idealSol),axis=1))

def step4b(negIdealSol,dec_matrix):
    return np.sqrt(np.sum(np.square(dec_matrix-negIdealSol),axis=1))

def step5(idealSol,negIdealSol):
    return (negIdealSol)/(idealSol+negIdealSol)

def topsisCalc(dec_matrix,weights,impacts):
    dec_matrix=step1(dec_matrix)
    dec_matrix=step2(dec_matrix,weights)
    idealSol=step3a(dec_matrix,impacts)
    negIdealSol=step3b(dec_matrix,impacts)
    eucIdeal=step4a(idealSol,dec_matrix)
    eucNonIdeal=step4b(negIdealSol,dec_matrix)
    relClos=step5(eucIdeal,eucNonIdeal)
    print("BEST DESICION: ",max(relClos),"\n")
    print("WORST DESICION: ",min(relClos),"\n")
    
def main(args):
    filename = args['InputDataFile'] 
    try:
        f = open(filename, 'r')
    except IOError:
       print ("There was an error reading", filename)
       sys.exit()
   
    file = csv.reader(f)
    data = list(file)
    data=np.array(data)
    data=np.array(data[1:,1:],dtype=float)
    
    
    x=data
    n=np.size(x,1)
    m=np.size(x,0)
    
    try:
        weights = np.array(args['Weights'][0].split(','),dtype=float)
  
    except ValueError:
        print ("Incorrect value(s) in Weight vector")
        sys.exit()
    
    if(len(weights) != n):
        print("Incorrect input size for Weights vector")
        sys.exit(0)
    
    
    try:
        impacts = args['Impacts'][0].split(',')
    
    except ValueError:
        print ("Incorrect value(s) in Impacts vector")
        sys.exit()
    
    if(len(impacts) != n):
        print("Incorrect input size for Impacts vector")
        sys.exit(0)    
    
    topsisCalc(x,weights,impacts)

    
# driver code    
if __name__ == "__main__":
  
    # parse command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument("InputDataFile", help="Enter the name of CSV file with .csv extention",type=str)
    parser.add_argument("Weights", nargs=1, help="Enter the weight vector comma separated" ,type=str)
    parser.add_argument("Impacts", nargs=1, help="Enter the impact vector comma separated",type=str)
    args = parser.parse_args()
    

    main(vars(args))
    
    
    


    
'''m=[[7,9,9,8],[8,7,8,7],[9,6,8,9],[6,7,8,6]]
w=[0.1,.4,.3,.2]
i=[1,1,1,0]
topsisCalc(m,w,i)
m=step1(m)
print(m)
w=[0.1,.4,.3,.2]
m=step2(m,w)
print(m)
i=[1,1,1,0]
ideal=step3a(m,i)
neg=step3b(m,i)
print(ideal)
print(neg)

anspos=step4a(ideal,m)
print(anspos)
ansneg=step4b(neg,m)
print(ansneg)

relClos=step5(anspos,ansneg)
print(relClos)'''