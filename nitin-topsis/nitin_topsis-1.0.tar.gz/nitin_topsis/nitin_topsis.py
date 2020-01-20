# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 16:50:18 2020

@author: Dell
"""

import numpy as np
class topsis:
    
    performancescore=None
    bestchoice=None
#    
    
    def __init__(self,dataset,weights,beneficialvalue):
        self.dataset=np.array(dataset,dtype=np.float).T
        assert len(self.dataset.shape)==2,"Data Matrix should be 2 dimensional"
        (self.n,self.m)=self.dataset.shape 
        
        self.weights=np.array(weights,dtype=np.float)
        assert len(self.weights.shape)==1,"Weight matrix should be 1 dimensional"
        assert self.weights.size==self.n,"Weights vector should be of length {}".format(self.n)
        
        self.weights=self.weights/sum(self.weights)
        
        self.beneficialvalue=np.array(beneficialvalue,dtype=np.int8)
        assert len(self.beneficialvalue.shape)==1,"Beneficial and Non Beneficial Value should be 1 dimensional"
        assert self.beneficialvalue.size==self.n,"Beneficial values vector should be of length{}".format(self.n)
        
        
        vpositive=np.zeros(self.n)
        vnegative=np.zeros(self.n)
    
    def __repr__(self):
        print('\n')
        if self.bestchoice==None:
            self.calculate()
            print("Alternate rank is \n {}".format(self.performancescore))
        return 'Best value\n[{}]:{}\n'.format(self.bestchoice,self.dataset[:,self.bestchoice])
    
    def normalizedataset(self):
        self.nd=self.dataset/np.array(np.linalg.norm(self.dataset,axis=1)[:,np.newaxis])
        return 
    
    def weightednormalisedmatrix(self):
        self.weightedresult=(self.weights*self.nd.T).T
        return
    
    def vvalues(self):
        self.vpositive=np.max(self.weightedresult,axis=1)*self.beneficialvalue + np.min(self.weightedresult,axis=1)*(1-self.beneficialvalue)
        self.vnegative=np.max(self.weightedresult,axis=1)*(1-self.beneficialvalue) + np.min(self.weightedresult,axis=1)*self.beneficialvalue
        return
    
    def eucliddist(self):
        self.spositive=np.linalg.norm(self.weightedresult-self.vpositive[:,np.newaxis],axis=0)
        self.snegative=np.linalg.norm(self.weightedresult-self.vnegative[:,np.newaxis],axis=0)
        return
    
    def performancerank(self):
        self.performancescore=self.snegative/(self.snegative+self.spositive)
        self.bestchoice=self.performancescore.argsort()[-1]
        return
    
    def calculate(self):
        self.normalizedataset()
        self.weightednormalisedmatrix()
        self.vvalues()
        self.eucliddist()
        self.performancerank()
        return 
        
        
        
        
        
    