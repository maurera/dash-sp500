import pandas as pd

class getstockdata:
    def __init__(self, file):
        # self.val = val
        self.readFile(file)
    def readFile(self,file):
        # Read data from file
        df = pd.read_pickle(file)   # eg 'data/sp500_6stocks.pkl'
        start = min(df[df.Ticker == 'SPY']['Date'])

        # Reshape wide dataset of stock prices
        dfw = df.pivot(index='Date', columns='Ticker', values='Close')  # [['SPY',Tk]]
        dfw.index = pd.to_datetime(dfw.index)
        dfw = dfw[dfw.index >= start]
        #dfw.dropna(inplace=True) # this would drop MSFT if FB didn't exist
        for col in dfw.columns:
            dfw[col] = dfw[col] / dfw[col].dropna()[0] * 100
        self.dfw = dfw

        # Prepare return data
        dfr = df.copy()
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

# Save big pickle
# Bring in SPY
# df6 = pd.read_pickle('data/sp500_6stocks.pkl')
# df6 = df6[df6.Ticker=='SPY']
# # Big pickle
# path = 'C:/Users/andrew.maurer/PycharmProjects/StressTestingWarmup/Data/'
# df = pd.read_pickle(path+'sp500data_merged.pkl')[['Ticker','Date','Adj Close']]
# df.rename(columns={'Adj Close':'Close'},inplace=True)
# start = min(df['Date'])
# print(start)
# df=df.append(df6,ignore_index=True)
# df = df[df['Date']>=start]
# df.dropna(inplace=True)
# df.to_pickle('data/sp500_505stocks.pkl')
# print(df6[df6.Ticker=='SPY'].head())
