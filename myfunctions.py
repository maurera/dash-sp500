import pandas as pd
import numpy as np
import statsmodels.api as sm
import dash_html_components as html

def sp500_estimate(df,Tk):
    # Reshape data
    dfw = df.pivot(index='Date', columns='Ticker', values='Close')[['SPY',Tk]]
    dfr = df.pivot(index='Date', columns='Ticker', values='Return')[['SPY',Tk]] # Reshape long to wide
    dfr.index = pd.to_datetime(dfr.index)
    dfr = dfr.dropna()
    X = pd.DataFrame(dfr['SPY'].dropna())
    Y = dfr[[Tk]].dropna()
    Y = pd.Series(dfr[Tk].dropna())
    X.insert(0, 'Intercept', 1)

    # Different models
    model1 = sm.OLS(Y, X)
    results1 = model1.fit()

    # Trailing x-day return
    dflagreturn = pd.concat([dfw[Tk].pct_change(1).shift(),dfw[Tk].pct_change(5).shift(),dfw[Tk].pct_change(21).shift()],axis=1)
    dflagreturn.columns = ['Self_Trail1','Self_Trail5','Self_Trail21']
    dflagreturn.index = pd.to_datetime(dflagreturn.index)

    # Concatenate X variables
    X = pd.concat([X,dflagreturn],axis=1).dropna()

    # Intersect X and Y
    intersect = Y.index.intersection(X.index)
    Y = Y[intersect]
    X = X.loc[intersect]

    # Model 1 - Intercept/SPY
    vars = ['Intercept','SPY']
    model1 = sm.OLS(Y, X[vars])
    results1 = model1.fit()
    return results1

# Run model eg
# print(([sp500_estimate(df,Tk).summary()]))

def dash_regtable(modellist):
    N = len(modellist)
    betas = pd.concat([r.params for r in modellist], axis=1, sort=False)
    pvalues = pd.concat([r.pvalues for r in modellist], axis=1, sort=False)
    se = pd.concat([r.bse for r in modellist], axis=1, sort=False)
    params = betas.index

    # Header
    S = []
    # Column titles
    row = [modellist[0].model.endog_names]+['('+str(i+1)+')' for i in range(N)]
    S = S+[html.Tr([html.Th(x) for x in row])]

    # Variables
    for p in params:
        row = [p]
        for i,pval in zip(betas.loc[p],pvalues.loc[p]):
            stars = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.1 else ''))
            row = row+['' if np.isnan(i) else '{0:.5f}'.format(i)+stars]
        S = S + [html.Tr([html.Td(x) for x in row])]
        row = [' ']+[('' if np.isnan(x) else '({0:.5f}'.format(x)+')') for x in se.loc[p]]
        S = S + [html.Tr([html.Td(x) for x in row])]

    # Statistics
    stat_labels = ['Observation','Parameters','R-squared','Adj. R-squared']
    stat_formats = ['{:.0f}','{:.0f}','{0:.5f}','{0:.5f}']
    d = {}
    for i,m in enumerate(modellist):
        for j,s in enumerate([m.nobs,m.df_model+1,m.rsquared,m.rsquared_adj]):
          d[i,j] = s
    for (j,lab),fmt in zip(enumerate(stat_labels),stat_formats):
        row = [lab]+[fmt.format(d[i,j]) for i,m in enumerate(modellist)]
        S = S + [html.Tr([html.Td(x) for x in row])]

    return html.Table(S, className='three columns')