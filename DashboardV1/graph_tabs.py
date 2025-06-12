# graph_tabs.py
from dash import dcc, html
import dash_bootstrap_components as dbc

graph_tab_contents = {
    'main-graph': dcc.Graph(id='graph-1', style={'height': '100vh'}),
    
    '1min': html.Div([
        dcc.Tabs(
            id='inner-tab-1min',
            value='demand',
            children=[
                dcc.Tab(label='Demand Graph', value='demand', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-2', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Head Graph', value='head', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-head-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-head-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-3', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Length & Diameter Graph', value='length', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-length-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-length-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-4', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Cost Graph', value='cost', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-cost-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-cost-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-5', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Flow Graph', value='flow', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-flow-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-flow-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-6', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Speed Graph', value='speed', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1min-speed-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1min-speed-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-7', style={'height': '70vh'})
                ], className='mt-3')),
            ],
            className='mt-3'
        )
    ]),

    #repete same for the 5 min and 1 hour tabs
    '5min': html.Div([
        dcc.Tabs(
            id='inner-tab-5min',
            value='demand',
            children=[
                dcc.Tab(label='Demand Graph', value='demand', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-8', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Head Graph', value='head', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-head-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-head-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-9', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Length & Diameter Graph', value='length', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-length-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-length-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-10', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Cost Graph', value='cost', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-cost-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-cost-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-11', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Flow Graph', value='flow', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-flow-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-flow-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-12', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Speed Graph', value='speed', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("1 hr", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='5min-speed-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='5min-speed-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-13', style={'height': '70vh'})
                ], className='mt-3')),
                
            ],
            className='mt-3'
        )
    ]),
    '1hr': html.Div([
        dcc.Tabs(
            id='inner-tab-1hr',
            value='demand',
            children=[
                dcc.Tab(label='Demand Graph', value='demand', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-14', style={'height': '70vh'})
                ], className='mt-3')),
                
                dcc.Tab(label='Head Graph', value='head', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-head-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-head-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-15', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Length & Diameter Graph', value='length', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-16', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Cost Graph', value='cost', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-17', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Flow Graph', value='flow', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-flow-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-flow-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-18', style={'height': '70vh'})
                ], className='mt-3')),

                dcc.Tab(label='Speed Graph', value='speed', children=html.Div([
                    dbc.Row([
                        dbc.Col(html.Div("1 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                        dbc.Col(html.Div("5 min", className='p-3 mb-3',
                                         style={'backgroundColor': 'white', 'textAlign': 'center'}), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(html.Div(id='1hr-demand-1', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                        dbc.Col(html.Div(id='1hr-demand-2', className='p-3 mb-3',
                                         style={'backgroundColor': 'white'}), width=6),
                    ]),
                    dcc.Graph(id='graph-19', style={'height': '70vh'})
                ], className='mt-3')),

            ],
            className='mt-3'
        )
    ])
}
