# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 11:37:01 2021

@author: lengh
"""

import pandas as pd
import pickle

class sectorInfo:
    '''
    create a dictionary where you can check the sector of each stock
    '''
    def __init__(self):
        try:
            self.dict = pickle.load(open("sectorDict.p", "rb"))
        except:
            self.table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            self.dict = {}
            self.populateDict()
            pickle.dump(self.dict, open("sectorDict.p", "wb"))
            
    def populateDict(self):
        '''
        populate the dictionary with stock abbreviation as key and section name as value
        '''
        listOfStocks = list(self.table[0][0])
        listOfSectors = list(self.table[0][3])
        for index in range(len(listOfStocks)):
            self.dict[listOfStocks[index]] = listOfSectors[index]
    
    def check(self, stock):
        '''
        return the sector name of a given stock
        '''
        try:
            return self.dict[stock]
        except:
            print("Stock not found in the sector list!")
            return None
    
    def get(self):
        '''
        return the dictionary
        '''
        return self.dict
    

if __name__ == '__main__':
    si = sectorInfo()
    print('AMD is in ' + si.check('AMD') + ' sector.')
