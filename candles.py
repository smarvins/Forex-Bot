import requests as r
import numpy as np
from __init__ import uniVar

from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments

#The class under the name apiCalls will hold the resoponsibility for handling the variables for the API calls.

class apiCalls():
    client = API(access_token=uniVar.key)
    o = instruments.InstrumentsCandles(instrument=uniVar.pair,
        params=uniVar.params)

class candleLogic:
    def OHLC(self, data):
        #call imported apiCalls class
        apiCalls.client.request(apiCalls.o)
        candles = apiCalls.o.response.get('candles')
        candleData = candles[data].get('mid')

        #OHLC vars to return in an array
        o = candleData.get('o')
        h = candleData.get('h')
        l = candleData.get('l')
        c = candleData.get('c')
        return float(o), float(h), float(l), float(c)

    #Define clean function routes for returning proper data
    def open(self, data):
        return self.OHLC(data)[0]

    #This is the functions that'll call the ohlc data based on the candle.
    def High(self, data):
        return self.OHLC(data)[1]

    def Low(self, data):
        return self.OHLC(data)[2]

    def Close(self, data):
        return self.OHLC(data)[3]

    #The getData function below will return data in a clean array so that it can be manipulated in the strategy.py file
    def getData(self):
        numList = []
        for x in range(0, uniVar.count):
            numList.append(self.Close(x))
        return numList
