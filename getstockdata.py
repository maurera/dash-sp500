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
