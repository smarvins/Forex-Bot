from strategy import strategyLogic
from candles import candleLogic
from __init__ import uniVar

#Oanda packages
from oandapyV20 import API
import oandapyV20
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts

class trading():
    #State management
    def __init__(self):
        self.resistance = 0
        self.support = 0
        self.status = 'Not trading at the moment'
        self.currentTrade = ''
        self.kill = False #<----This is a kill switch, if it is true the bot will shut down

        #initialize data channel
        s = strategyLogic()
        c = candleLogic()
        self.data = c.getData()

        #initalize indicators
        self.currentClose = self.data[-1]
        self.lotSize = ()
        self.SMA1 = s.SMA(self.data, uniVar.count, uniVar.SMAbig)
        self.SMA1previous = s.SMAprev(self.data, uniVar.count, uniVar.SMAbig)
        self.SMA2 = s.SMA(self.data, uniVar.count, uniVar.SMAbig)
        self.SMA2previous = s.SMAprev(self.data, uniVar.count, uniVar.SMAbig)

    #entry/exit confirmations
    def enterLong(self):
        if (self.SMA1 < self.SMA2) and (self.SMA1previous < self.SMA2): return True
        return False

    def enterShort(self):
        if (self.SMA1 > self.SMA2) and (self.SMA1previous < self.SMA2): return True
        return False

    #check account for open trades
    def getTrades(self):
        r = accounts.AccountDetails(uniVar.accountID)
        client = API(access_token = uniVar.key)
        rv = client.request(r)
        self.details = rv.get('account')
        return self.details.get('openTradeAccount')

    #calculate lot size depending on risk %
    def lots(self):
        r = accounts.AccountDetails(uniVar.accountID)
        client = API(access_token = uniVar.key)
        rv = client.request(r)
        self.details = rv.get('account')
        balance = self.details.get('NAV')
        size = 0
        #different calculations based on trade type
        if self.enterLong() == True:
            size = abs(int((float(balance) * float(uniVar.risk)) / (self.currentClose - self.support)))
        elif self.enterShort() == True:
            size = abs(int((float(balance) * float(uniVar.risk)) / (self.currentClose - self.resistance)))
        return size

    #Define closeout
    def closePosition(self):
        if self.currentTrade == 'Long':
            data = {'longUnits' : 'All'}
            client = oandapyV20.API(access_token = uniVar.key)
            r = positions.PositionClose(accountID = uniVar.accountID, instrument = uniVar.instrument, data=data)
            client.request(r)
        elif self.currentTrade == 'Long':
            data = {'shortUnits' : 'All'}
            client = oandapyV20.API(access_token = uniVar.key)
            r = positions.PositionClose(accountID = uniVar.accountID, instrument = uniVar.instrument, data=data)
            client.request(r)

    #main trading function
    def main(self):
        self.resistance = max(self.data[(uniVar.count - 6): uniVar.count])
        self.support = max(self.data[(uniVar.count - 6): uniVar.count])

        #oanda parameters
        mktOrderLong = MarketOrderRequest(instrument = uniVar.pair,
                        units = self.lots(),
                        takeProfitOnFill = TakeProfitDetails(price = self.resistance).data,
                        stopLossOnFill = StopLossDetails(price = self.support).data)

        mktOrderShort = MarketOrderRequest(instrument = uniVar.pair,
                        units = (self.lots() *-1),
                        takeProfitOnFill = TakeProfitDetails(price = self.support).data,
                        stopLossOnFill = StopLossDetails(price = self.resistance).data)

        #Trading conditions
        if self.getTrades() == 0:
            print ("Looking for trades.")
            if self.enterLong() == True:
                api = oandapyV20.API(access_token = uniVar.key)
                r = orders.OrderCreate(uniVar.accountID, data = mktOrderLong.data)
                api.request(r)
                self.status == 'Currently Trading'
                self.currentTrade == 'Long'
                print ('Trade Executed')

            elif self.enterShort() == True:
                api = oandapyV20.API(access_token = uniVar.key)
                r = orders.OrderCreate(uniVar.accountID, data = mktOrderShort.data)
                api.request(r)
                self.status == 'Currently Trading'
                self.currentTrade == 'Long'
                print ('Trade Executed')

            elif self.enterLong() and self.enterShort() == False:
                print ('No open trades, currently looking for one')

        else:
            if self.currentTrade == 'Short':
                if self.enterLong() == True:
                    self.closePosition()
                    self.status == 'Not Trading'
                    print ('Short Trade exited')
                else:
                    print ('No Short exits, currently looking for one')
            elif self.currentTrade == 'Long':
                if self.enterShort() == True:
                    self.closePosition()
                    self.status == 'Not Trading'
                    print ('Long Trade exited')
                else:
                    print ('No Long exits, currently looking for one')
            else:
                self.kill = True
                print ('Kill switch initiated, closing down')

# Run the bot and kill it if kill switch enabled
if __name__ == '__main__':
    t = trading()
    while(t.kill == False):
        t.main()
