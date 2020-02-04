# Here is the universal variable called uniVar that we'll need for the strategy and the api

class uniVar():
    SMAbig = 50
    SMAsmall = 25
    count = 55
    key = 'your API key from Oanda'
    accountID = 'your oanda acc.'
    pair='EUR_USD'
    params = {
        "count" : count,
        "granularity" : "H4"
    }
