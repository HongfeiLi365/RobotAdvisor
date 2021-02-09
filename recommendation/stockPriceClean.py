'''
This function tries to clean up the grepped data into an array.
return the relative changes of the stock price from day to day.
'''
import numpy as np
class stockPriceClean:
    def __init__(self, pandaData):
        self.data = pandaData.to_numpy()
        self.clean()
    def clean(self):
        self.open = self.data[:,0]
        self.close = self.data[:,3]
        self.change = (self.close - self.open) / self.open * 100 # get the relative change for each day
    def get(self):
        return self.change
