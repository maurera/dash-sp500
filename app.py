# -*- coding: utf-8 -*-
"""
Created on Jul 10 2019

@author: Andrew Maurer
"""

import os
import pathlib as pl
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
from myfunctions import sp500_estimate
from myfunctions import dash_regtable
from getstockdata import getstockdata
from myfunctions import yearfrac_to_date

##### Start #########

# Get data
stockdata = getstockdata('data/sp500_6stocks.pkl')
#stockdata = getstockdata('data/sp500_505stocks.pkl')
dfw=stockdata.dfw
dfr=stockdata.dfr

# Start application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

######################################
####### App layout ###################
######################################
app.layout = html.Div([
    html.Div([dcc.Dropdown(id="selected-tickers", multi=True, value=["PEP"],
                        options=[{"label":x,"value":x} for x in dfw.drop(columns=['SPY'])]),
              #html.Button('Load full SP500', id='button'),
              #html.Div(id='button-response')
              ],
          className="row", style={"display": "block", "justify-content": "center", "margin-left": "auto",
                                  "margin-right": "auto", "width": "30%"}),
    html.Div(className='row', children=[
        html.Div([html.Div(id='mytabs'),
        dcc.Graph(id='tabs-content',config={'displayModeBar': False})],style={"width": "30%"}),
        dcc.Tabs(id="tabs",value="tab-1",children=[]),
        html.Div([
            dcc.Graph(id='graph-timeseries'),
            dcc.RangeSlider(id='date-slider',min=1993,max=2020,step=0.1,allowCross=False,value=[1993, 2020],
                            marks={x:str(x) for x in range(1993,2020,5)})
        ],style={"width": "60%"})
    ], style={"display":"flex","flex-wrap":"wrap"}),
    # dcc.Graph(id='graph-timeseries'),
    #dcc.Slider(id='year-slider',min=2000,max=2010,value=2000,marks={str(2003): str(2003)},step=None),
    html.H3(children='Model estimation'),
    html.Div(id='graph-range'),
    html.Div(id='regtable-div')
], style={"width": "80%","margin-left": "auto","margin-right": "auto"})

######################################
####### Tabs #########################
######################################
@app.callback(Output('mytabs', 'children'), [Input('selected-tickers', 'value')])
def display_tabs(tickers):
    alltabs = [dcc.Tab(label=t, value=t) for t in tickers]
    #return alltabs
    return dcc.Tabs(id="tabs", children=alltabs, value=tickers[0])

@app.callback(Output('tabs-content', 'figure'),
              [Input('tabs', 'value'),Input('date-slider', 'value')])
def render_content(tab,daterange):
    if tab=='tab-1': return None
    # restrict data for plotting
    start, end = yearfrac_to_date(daterange[0]), yearfrac_to_date(daterange[1])
    dfr_wide = dfr.pivot(index='Date', columns='Ticker', values='Return')[['SPY', tab]]
    dfr_wide.dropna(inplace=True)
    dfr_wide.index = pd.to_datetime(dfr_wide.index)
    dfrsub = dfr_wide[(dfr_wide.index > start) & (dfr_wide.index < end)]
    X = pd.DataFrame(dfrsub['SPY'].dropna()).sort_values(by='SPY',axis=0)
    X.insert(0, 'Intercept', 1)
    yhat = sp500_estimate(dfr, tab).predict(X)
    p1 = go.Scatter(x=dfrsub['SPY'], y=dfrsub[tab], text=tab, mode='markers')
    p2 = go.Scatter(x=X['SPY'], y=yhat, text=tab, mode='lines')
    return {
        "data": [p1,p2],
        "layout": go.Layout(showlegend=False,
            margin=go.layout.Margin(l=50,r=30,b=50,t=50,pad=4))
    }

######################################
####### Time series graph ############
######################################
@app.callback(
    Output('graph-timeseries', 'figure'),
    [Input('selected-tickers', 'value'),Input('date-slider', 'value')])
def update_figure(selected,daterange): #,selected_year
    selected = ['SPY',*selected]
    start,end=yearfrac_to_date(daterange[0]),yearfrac_to_date(daterange[1])
    dfsub=dfw[(dfw.index>start) & (dfw.index<end)]
    traces = [go.Scatter(x=dfsub.index,y=dfsub[i],text=i,mode='lines',name=i) for i in selected]
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Normalized value'}
        )
    }

@app.callback(
    Output('graph-range', 'children'),
    [Input('graph-timeseries', 'relayoutData')])
def get_figure_range(relayout_data):
    if relayout_data==None: return None
    range = [relayout_data.get('xaxis.range[0]'),relayout_data.get('xaxis.range[1]')]
    if range[0]==None: return None
    return range


######################################
####### Model estimation table #######
######################################
@app.callback(
    Output(component_id='regtable-div', component_property='children'),
    [Input('selected-tickers', 'value')]
)
def update_output_div(tickers):
    tickers = ['SPY',*tickers]
    Tk = tickers[-1]
    if len(tickers)==1:
        return ''
    model1 = sp500_estimate(dfr, Tk)
    allmodels = [sp500_estimate(dfr, x) for x in tickers[1:]]
    return html.Div(className='row', children=[
        dash_regtable([m]) for m in allmodels
    ])

if __name__ == "__main__":
    app.run_server(debug=True)

# Can't do this - can't modify global variable inside callback
# @app.callback(
#     dash.dependencies.Output('button-response', 'children'),
#     [dash.dependencies.Input('button', 'n_clicks')])
# def update_output(n_clicks):
#     if n_clicks==None:
#         return ''
#     A = stockdata
#     A = getstockdata('data/sp500_505stocks.pkl')
#     return 'Loaded'
