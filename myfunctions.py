import pandas as pd
import numpy as np
import statsmodels.api as sm
import dash_html_components as html
from datetime import timedelta
from datetime import datetime as dt
def yearfrac_to_date(y):
    return dt(int(y),1,1)+timedelta(days=(y%1)*365)

style_tr_underline = {
    "border-bottom": "2px solid #c6d5e3",
    "color": " darken(#c6d5e3, 25%)"
}
style_tr_noborder = {
    "border-bottom": "none",
}

# def modelwrap(X,Y,xvars):
#     # Intersect X and Y
#     intersect = Y.index.intersection(X.index)
#     Y = Y[intersect]
#     X = X.loc[intersect]

def getgrid(X,n=50):
    grid = pd.DataFrame(columns=X.columns)
    grid['SPY'] = [min(X['SPY'])+ x*(max(X['SPY'])-min(X['SPY']))/n for x in range(n)] # numpy use: np.linspace(min(X['SPY']), max(X['SPY']), 50)
    grid['Intercept'] = 1
    if 'SPY Squared' in X.columns:
        grid['SPY Squared'] = grid['SPY']**2
    return grid


def sp500_estimate(stockdata,Tk,addvars=[]):

    # Y data must be a pd Series
    Y = pd.Series(stockdata.dfr[Tk].dropna())

    # Trailing x-day return
    # dflagreturn = pd.concat([dfw[Tk].pct_change(1).shift(),dfw[Tk].pct_change(5).shift(),dfw[Tk].pct_change(21).shift()],axis=1)
    # dflagreturn.columns = ['Self_Trail1','Self_Trail5','Self_Trail21']
    # dflagreturn.index = pd.to_datetime(dflagreturn.index)

    X = stockdata.X

    # Concatenate X variables
    #X = pd.concat([X,Xsq,dflagreturn],axis=1).dropna()
    #X = pd.concat([X, dflagreturn], axis=1).dropna()

    # Intersect X and Y
    intersect = Y.index.intersection(X.index)
    Y = Y[intersect]
    X = X.loc[intersect]

    # Model 1 - Intercept/SPY
    vars = ['Intercept','SPY']+addvars
    model1 = sm.OLS(Y, X[vars])
    results1 = model1.fit()

    # # Model 2 - X-squared
    # vars = ['Intercept', 'SPY', 'SPYSquared']
    # model2 = sm.OLS(Y, X[vars])
    # results2 = model2.fit()

    #return [results1,results1]
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
    S = S+[html.Tr([html.Th(x) for x in row],style=style_tr_underline)]

    # Variables
    for n,p in enumerate(params):
        row = [p]
        for i,pval in zip(betas.loc[p],pvalues.loc[p]):
            stars = '***' if pval < 0.01 else ('**' if pval < 0.05 else ('*' if pval < 0.1 else ''))
            row = row+['' if np.isnan(i) else '{0:.5f}'.format(i)+stars]
        S = S + [html.Tr([html.Td(x) for x in row])]
        row = [' ']+[('' if np.isnan(x) else '({0:.5f}'.format(x)+')') for x in se.loc[p]]
        rowstyle = {} if n<len(params)-1 else style_tr_underline # underline last standard error row
        S = S + [html.Tr([html.Td(x) for x in row],style=rowstyle)]

    # Statistics
    stat_labels = ['Observation','Parameters','R-squared','Adj. R-squared']
    stat_formats = ['{:.0f}','{:.0f}','{0:.5f}','{0:.5f}']
    d = {}
    for i,m in enumerate(modellist):
        for j,s in enumerate([m.nobs,m.df_model+1,m.rsquared,m.rsquared_adj]):
          d[i,j] = s
    for (j,lab),fmt in zip(enumerate(stat_labels),stat_formats):
        row = [lab]+[fmt.format(d[i,j]) for i,m in enumerate(modellist)]
        rowstyle = {} if j < len(stat_labels) - 1 else style_tr_underline  # underline last standard error row
        S = S + [html.Tr([html.Td(x) for x in row],style=rowstyle)]

    return html.Table(S, className='three columns')