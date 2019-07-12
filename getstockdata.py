import pandas as pd

class getstockdata:
    def __init__(self, file):
        # self.val = val
        self.readFile(file)
    def readFile(self,file):
        # Read data from file
        df = pd.read_pickle(file)   # eg 'data/sp500_6stocks.pkl'

        # Reshape wide dataset of stock prices
        dfw = df.pivot(index='Date', columns='Ticker', values='Close')  # [['SPY',Tk]]
        dfw.index = pd.to_datetime(dfw.index)
        dfw.dropna(inplace=True)
        for col in dfw.columns:
            dfw[col] = dfw[col] / dfw[col].dropna()[0] * 100
        self.dfw = dfw

        # Prepare return data
        dfr = df.copy()
        start = min(dfr[dfr.Ticker == 'SPY']['Date'])
        dfr["Return"] = dfr.groupby("Ticker")["Close"].pct_change(1)
        dfr = dfr[dfr['Date'] >= start]
        self.dfr = dfr


# #########################
# # Generate pickle files #
# import pandas as pd
# import numpy as np
#
# # Load Treasury data
# dfCMT = pd.concat([pd.read_csv('data/FREDT'+str(x)+'Y.csv',parse_dates=True).set_index('DATE') for x in [1,2,5,10]],axis=1,sort=False)
# dfCMT.replace('.',np.nan,inplace=True)
# dfCMT.dropna(inplace=True)
# dfCMT = dfCMT.apply(pd.to_numeric)
# dfCMTlagged= pd.concat([dfCMT, dfCMT.shift(1), dfCMT.shift(5), dfCMT.shift(21)], axis=1)
# # Now fix column names
# dfCMTlagged.columns = [*dfCMT.columns,*['DGS'+str(x)+'L'+str(i) for i in [1,5,21] for x in [1,2,5,10]]]
# dfCMTlagged.index = pd.to_datetime(dfCMTlagged.index)
# print(dfCMTlagged.head())