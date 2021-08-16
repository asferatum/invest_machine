from numpy import bitwise_and
import pandas as pd
import sys, os

fileIn = 'tmp.csv'
fileOut = 'out.csv'
# res = os.system(sys.argv[1]) sys.argv[2]
print(sys.argv[1:])

if len(sys.argv) > 1: # is not None:
    fileIn = str(sys.argv[1])

dfIn = pd.read_csv(fileIn, sep = ',', low_memory=False)
dfOut = pd.DataFrame({'id':[], 'time(utc timestamp)':[], 'amount(usd)':[], 'price':[], 'side':[]})

numEntryes = dfIn.last_valid_index()
# print(str(fileIn) + ": " + str(numEntryes))
# print(dfIn.iloc[0]['asks[0].amount'])

dfIn = dfIn.to_numpy()

# print(dfIn[0])
# exit()

class Bids:
    amount = 0
    price = 0
    def __init__(self, price, amount):
        self.amount = amount
        self.price = price

    def __repr__(self):        
        return '[' + str(self.amount) + ':' + str(self.price) + ']'

class Asks:
    amount = 0
    price = 0
    def __init__(self, price, amount):
        self.amount = amount
        self.price = price

    def __repr__(self):        
        return '[' + str(self.amount) + ':' + str(self.price) + ']'

class Dom:
    bids = []
    asks = []

    def __init__(self, asks, bids):
        self.bids = []
        self.asks = []
        for i in range(int(len(asks)/2)):
            self.asks.append(Asks(asks[i], asks[i+10]))
            # print(asks[i], ' ', asks[i+10])             
        for i in range(int(len(bids)/2)):
            self.bids.append(Bids(bids[i], bids[i+10]))
    
    def __repr__(self):        
        return '[' + str(self.bids) + ',\n' + str(self.asks) + ']'


# timestamp          2021-04-02 09:00:00.400
# exchange                           deribit
# symbol                         BTC-16APR21
# timestamp.1               1617354000424000
# local_timestamp           1617354000430645
# asks[0].price                      60892.5
# asks[1].price                      60893.0
# asks[2].price                      60897.0
# asks[3].price                      60897.5
# asks[4].price                      60904.0
# asks[5].price                      60913.5
# asks[6].price                      60918.5
# asks[7].price                      60938.5
# asks[8].price                      60942.0
# asks[9].price                      60948.5
# asks[0].amount                      2000.0
# asks[1].amount                     13700.0
# asks[2].amount                      4180.0
# asks[3].amount                      6000.0
# asks[4].amount                    193180.0
# asks[5].amount                    100000.0
# asks[6].amount                      2540.0
# asks[7].amount                      8000.0
# asks[8].amount                      1810.0
# asks[9].amount                    289770.0
# bids[0].price                      60828.0
# bids[1].price                      60806.5
# bids[2].price                      60785.0
# bids[3].price                      60780.5
# bids[4].price                      60780.0
# bids[5].price                      60761.0
# bids[6].price                      60738.5
# bids[7].price                      60732.0
# bids[8].price                      60725.0
# bids[9].price                      60705.5
# bids[0].amount                    213250.0
# bids[1].amount                      2820.0
# bids[2].amount                      1810.0
# bids[3].amount                      2690.0
# bids[4].amount                    319870.0
# bids[5].amount                      5270.0
# bids[6].amount                      2290.0
# bids[7].amount                    379100.0
# bids[8].amount                    100000.0
# bids[9].amount                      1830.0

def buyFromDOM(dom, volume=1000, depth=10, step=0, time=0):
    sum, buyVol, slippage = 0, 0, 0
    if dom.asks[step].amount >= volume:
        sum = volume * dom.asks[step].price
        buyVol= volume
        
        dfOut.loc[len(dfOut)] = [int(len(dfOut)), time, buyVol, round(dom.asks[step].price*1.0002, 4), 'asks']
    else:
        sum = dom.asks[step].amount * dom.asks[step].price
        buyVol= dom.asks[step].amount
        dfOut.loc[len(dfOut)] = [int(len(dfOut)), time, buyVol, round(dom.asks[step].price*1.0002, 4), 'asks']
        if step < depth-1:
            sm, b, sl = buyFromDOM(dom, volume=volume-dom.asks[step].amount, step=step+1, time=time)
            sum += sm
            buyVol += b

    if step == 0:
        slippage = sum/buyVol - dom.asks[step].price 
        return sum, buyVol, slippage
    else:
        return sum, buyVol, slippage


# for i in range(10):
#     print(dfIn["timestamp.1"][i+1]-dfIn["timestamp.1"][i])
# print(df["local_timestamp"][:10])

# dfOut = pd.DataFrame({'id':[], 'time(utc timestamp)':[], 'amount(usd)':[], 'price':[], 'side':[]})

# dfOut.set_index('id',  inplace=True)
# data = [{'id':'East','time(utc timestamp)':'Shop Rite','amount(usd)':'Fruits','price':'December','side': 1265}]
# dfOut.append(data,ignore_index=True,sort=False)
# dfOut.loc[len(dfOut)] = [1,2,3,4,5]
# dfOut.loc[len(dfOut.index)]=list(data[0].values())

volumeBuy = 10000
timePrev = 0
ctrRawOut = 0

buyVol = 0
avgPrice = 0
slippage = 0
# for i in range(30): #range(numEntryes):
for i in range(numEntryes):

    if dfIn[i][3] - timePrev > 1e6:
        ctrRawOut+=1
        timeNow = dfIn[i][3]
        # dom = dfIn.iloc[0]
        dom = None
        dom = Dom(dfIn[i][5:25], dfIn[i][25:])
        # print(dom)
        totVal = 0
        for i in range(len(dom.asks)):
            totVal += dom.asks[i].amount
        # print('totVal: ', totVal)
        sm, bv, slpge = buyFromDOM(dom, volume=volumeBuy, depth=10, time=timeNow)
        # print("sum:", sum, "buyVol:", buyVol, "slpge", slpge)
        
        buyVol += bv
        avgPrice += sm*1.0002/bv
        slippage += slpge
        
        # dfOut.loc[len(dfOut)] = [int(len(dfOut)), timeNow, buyVol, sum/buyVol, 'asks']
        # if dfIn['asks[0].amount'][i] < volumeBuy:
        #     dfOut.loc[len(dfOut)] = [int(len(dfOut)), timeNow, dfIn['asks[0].amount'][i], dfIn['asks[0].price'][i], 'asks']

        timePrev = timeNow
slippage /= ctrRawOut
avgPrice /= ctrRawOut
print("buyVol: ", round(buyVol, 4))
print("avgPrice: ", round(avgPrice, 4))
print("slippage: ", round(slippage, 4))
dfOut.astype({'id': 'int', 'time(utc timestamp)': 'int'}).dtypes
dfOut.set_index('id',  inplace=True)
print(dfOut)
dfOut.to_csv(fileOut, sep=',')