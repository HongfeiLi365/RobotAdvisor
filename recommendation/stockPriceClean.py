
import numpy as np
class stockPriceClean:
    '''
    This function tries to clean up the grepped data into an array.
    return the relative changes of the stock price from day to day.
    '''
    def __init__(self, pandaData):
        '''
        input is following the 
        '''
        self.data = pandaData.to_numpy()
        self.clean()
    def clean(self):
        '''
        this method returns the processed value of the stock data.
        It can return the relative change
        '''
        self.open = self.data[:,0]
        self.close = self.data[:,3]
        self.change = (self.close - self.open) / self.open * 100 # get the relative change for each day
    def get(self):
        '''
        return the processed value, a numpy array
        '''
        return self.change

if __name__ == '__main__':
    print("It will be called in loadTestData.py")