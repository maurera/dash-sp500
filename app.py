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
from myfunctions import getgrid
from getstockdata import getstockdata
from myfunctions import yearfrac_to_date
from model_nn import sp500_estimate_nn

##### Start #########

# Get data
stockdata = getstockdata('data/sp500_6stocks.pkl')  #stockdata = getstockdata('data/sp500_505stocks.pkl')
dfw=stockdata.dfw
dfr=stockdata.dfr
#dfwL=stockdata.dfwL

# Start application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

######################################
####### App layout ###################
######################################
app.layout = html.Div([
    html.Div([dcc.Dropdown(id="selected-tickers", multi=True, value=["PEP"], #style={"width": "50%"},
                        options=[{"label":x,"value":x} for x in dfw.drop(columns=['SPY'])]),
              html.Button('Save to pdf', id='button_pdf'),
              html.Div(id='button-pdf-content', style={'display':'none'})
              ],
          className="row", style={"display": "flex", "justify-content": "center", "margin-left": "auto",
                                  "margin-right": "auto"}),
    html.Div(className='row', children=[
        html.Div([html.Div(id='mytabs'),
        dcc.Graph(id='tabs-content',config={'displayModeBar': False}),
            html.Div(children=[html.Button('Train neural network (epochs)', id='button_nn'),
            dcc.Input(id='input-box', type='number', value=100, style={'width':'25%'})], style={"display":"flex","margin": "auto"}),
            ],style={"width": "30%"}),
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
], style={"width": "90%","margin-left": "auto","margin-right": "auto"})

@app.callback(Output('button-pdf-content', 'children'),
              [Input('button_pdf', 'n_clicks')])
def download_pdf(n_clicks):
    if n_clicks != None:
        print('yes')
    return html.H3(children=''),

######################################
####### Tabs #########################
######################################
@app.callback(Output('mytabs', 'children'), [Input('selected-tickers', 'value')])
def display_tabs(tickers):
    alltabs = [dcc.Tab(label=t, value=t) for t in tickers]
    #return alltabs
    return dcc.Tabs(id="tabs", children=alltabs, value=tickers[0])

@app.callback(Output('tabs-content', 'figure'),
              [Input('tabs', 'value'),Input('date-slider', 'value'), Input('button_nn', 'n_clicks')], [State('input-box', 'value')])
def render_content(tab,daterange,n_clicks,epochs):
    if tab=='tab-1': return None
    # restrict data for plotting
    start, end = yearfrac_to_date(daterange[0]), yearfrac_to_date(daterange[1])
    dfrsub = dfr[(dfr.index > start) & (dfr.index < end)]
    X = stockdata.X
    Xgrid = getgrid(X)
    yhat1 = sp500_estimate(stockdata, tab).predict(Xgrid[['Intercept','SPY']])
    yhat2 = sp500_estimate(stockdata, tab, ['SPY Squared']).predict(Xgrid)
    p1 = go.Scatter(x=dfrsub['SPY'], y=dfrsub[tab], text=tab, name='Returns', mode='markers')
    p2 = go.Scatter(x=Xgrid['SPY'], y=yhat1, text=tab, name='Linear', mode='lines')
    p3 = go.Scatter(x=Xgrid['SPY'], y=yhat2, text=tab, name='Quadratic', mode='lines')
    graphdata = [p1,p2,p3]
    if dash.callback_context.triggered:
        button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        #if n_clicks == 1:
        if button_id=='button_nn':
            yhat3 = sp500_estimate_nn(stockdata, tab, epochs).predict(Xgrid['SPY'])
            yhat3 = pd.Series(yhat3[:,0])
            p4 = go.Scatter(x=Xgrid['SPY'], y=yhat3, text=tab, name='NN', mode='lines')
            graphdata=[p1,p2,p3,p4]
    return {
        "data": graphdata,
        "layout": go.Layout(showlegend=True, legend=go.layout.Legend(orientation='h',yanchor='top',y=1.2), #,x=.1
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
    #model1 = sp500_estimate(dfr, Tk)
    #allmodels = [sp500_estimate(stockdata, x,['SPY Squared']) for x in tickers[1:]]
    allmodels = []
    for x in tickers[1:]:
        allmodels.append([sp500_estimate(stockdata, x, set) for set in [[],['SPY Squared']]])

    return html.Div(className='row', children=[
        dash_regtable(m) for m in allmodels
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
