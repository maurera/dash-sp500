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

##### Start #########

# Get data
stockdata = getstockdata('data/sp500_6stocks.pkl')
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
                        options=[{"label":x,"value":x} for x in dfw.drop(columns=['SPY'])])],
          className="row", style={"display": "block", "width": "30%", "margin-left": "auto",
                                  "margin-right": "auto"}),
    # html.Div(className='row', children=[
    #     html.Div(id='tabs',style={"width": "30%"}),
    #     dcc.Graph(id='graph-timeseries',style={"width": "60%"})
    # ]),
    dcc.Graph(id='graph-timeseries'),
    #dcc.Slider(id='year-slider',min=2000,max=2010,value=2000,marks={str(2003): str(2003)},step=None),
    html.H3(children='Model estimation'),
    html.Div(id='regtable-div')
], style={"width": "80%","margin-left": "auto","margin-right": "auto"})


######################################
####### Tabs #########################
######################################
# @app.callback(Output('tabs', 'children'), [Input('selected-tickers', 'value')])
# def display_tabs(tickers):
#     alltabs = []
#     for t in tickers:
#         alltabs.append(
#             dcc.Tab(label=t, value=t)   #dcc.Tab(label='Tab {}'.format(i), value='tab-{}'.format(i))
#         )
#     return dcc.Tabs(alltabs)


######################################
####### Time series graph ############
######################################
@app.callback(
    Output('graph-timeseries', 'figure'),
    [Input('selected-tickers', 'value')]) # ,Input('year-slider', 'value')
def update_figure(selected): #,selected_year
    selected = ['SPY',*selected]
    traces = []
    for i in selected:
        print(i)
        traces.append(go.Scatter(
            x=dfw.index,
            y=dfw[i],
            text=i,
            mode='lines',
            name=i
        ))
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Normalized value'} #,
        )
    }



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
