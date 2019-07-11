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

table_header_style = {
    "backgroundColor": "rgb(2,21,70)",
    "color": "white",
    "textAlign": "center",
}

##### Start #########
# First time series
Tk = 'BAC'
df = pd.read_pickle('data/sp500_6stocks.pkl')
dfw = df.pivot(index='Date', columns='Ticker', values='Close') #[['SPY',Tk]]
dfw.index = pd.to_datetime(dfw.index)
dfw.dropna(inplace=True)
for col in dfw.columns:
    dfw[col]=dfw[col]/dfw[col].dropna()[0]*100

# Prepare data for modeling
dfc = df.copy()
start = min(dfc[dfc.Ticker=='SPY']['Date'])
dfc["Return"] = dfc.groupby("Ticker")["Close"].pct_change(1)
dfc = dfc[dfc['Date']>=start]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([dcc.Dropdown(id="selected-value", multi=True, value=["SPY"],
                        options=[{"label":x,"value":x} for x in dfw])],
          className="row", style={"display": "block", "width": "30%", "margin-left": "auto",
                                  "margin-right": "auto"}),
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='year-slider',
        min=2000,
        max=2010,
        value=2000,
        marks={str(2003): str(2003)},
        step=None
    ),
    html.Div(id='regtable-div')
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('selected-value', 'value'),Input('year-slider', 'value')])
def update_figure(selected,selected_year):
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
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            # legend={'x': 0, 'y': 1},
            # hovermode='closest'
        )
    }

@app.callback(
    Output(component_id='regtable-div', component_property='children'),
    [Input('selected-value', 'value')]
)
def update_output_div(tickers):
    Tk = tickers[-1]
    if len(tickers)==1:
        return ''
    model1 = sp500_estimate(dfc, Tk) 
    allmodels = [sp500_estimate(dfc, x) for x in tickers[1:]]
    return html.Div(className='row', children=[
        dash_regtable([m]) for m in allmodels
    ])

if __name__ == "__main__":
    app.run_server(debug=True)
