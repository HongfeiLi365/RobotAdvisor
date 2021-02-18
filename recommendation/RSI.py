# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 09:20:16 2021

@author: lengh
"""
import numpy as np
import  loadTestData
class RSI:
    '''
    calculate the RSI: relative strength index
    RSI = 100 - (100/(1 + RS))
    RS = (Average of up closes in x days) / (Average of down closes in x days) 
    input is the stockData numpy array, each row is a stock and each column represents a daily change in pricing
    '''
    def __init__(self, stockData):
        self.stockData = stockData
        self.row, self.column = self.stockData.shape
        self.RS = np.zeros(self.row)
        self.RSI = np.zeros(self.row)
        self.calculateRS()
        self.calculateRSI()
        #print(self.RSI, row)
    def calculateRS(self):
        '''
        calculate RS
        '''
        for index in range(self.row):
            num = np.sum(self.stockData[index, :] > 0)
            dem = np.sum(self.stockData[index, :] < 0)
            try:
                self.RS[index] = num/dem
            except:
                self.RS[index] = num/dem
            #print(self.RS)
    
    def calculateRSI(self):
        '''
        calculate RSI
        '''
        for index in range(self.row):
            try:
                self.RSI[index] = 100 - 100/(1.0 + self.RS[index])
            except:
                print("Something is wrong with RSI calculation!")
        #print(self.RSI)
    
    def get(self):
        '''
        return an numpy array with RSI values, corresponding to the stocks in order
        '''
        return self.RSI
            
            
if __name__ == '__main__':
    ld = loadTestData.load()
    stockDict, stockList, stockData = ld.get()
    rsi = RSI(stockData)