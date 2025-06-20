from dash import dcc, html
import dash_bootstrap_components as dbc

class Layout:
    def __init__(self):
        pass

    def create_layout(self):
        data_stores = html.Div([
            dcc.Store(id='node-data-store'),
            dcc.Store(id='pipe-data-store'),
            dcc.Store(id='commercial-pipe-data-store'),
            dcc.Store(id='esr-cost-data-store'),
            dcc.Store(id='manual-pump-data-store'),
            dcc.Store(id='valve-data-store'),
            dcc.Store(id='input-data'),
            dcc.Store(id='node-data-upload1'),
            dcc.Store(id='pipe-data-upload1'),
            dcc.Store(id='node-data-upload2'),
            dcc.Store(id='pipe-data-upload2'),
            dcc.Store(id='tc1'),
            dcc.Store(id='tc2'),
            dcc.Store(id='Cost-file1'),
            dcc.Store(id='Length-file1'),
            dcc.Store(id='Cost-file2'),
            dcc.Store(id='Length-file2')
        ])
        
        # Left Sidebar 
        sidebar = html.Div([
            html.H2("Jaltantra Water Network Visualization", className='text-white font-weight-bold mb-4'),
            dbc.Nav([
                dbc.NavLink("Overview", active='exact', className='text-white mb-2'),
                dbc.NavLink("Upload Data", active='exact', className='text-white mb-2'),
                dbc.NavLink("Statistics", active='exact', className='text-white mb-2'),
            ], vertical=True, pills=True)
        ], className='p-3', style={
            'height': '100vh',
            'overflowY': 'auto',
            'backgroundColor': '#343A40',
            'color': '#FFFFFF',
            'width': '100%',
        })

        # Modal for enlarged graph
        modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Enlarged Graph")),
                dbc.ModalBody(
                    dcc.Graph(id='enlarged-graph', style={'height': '80vh'})
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ml-auto")
                ),
            ],
            id="graph-modal",
            size="xl",
            is_open=False,
        )

        # Left panel with inputs and overview
        left_panel = html.Div([
            dbc.Alert(
                    id="file-alert",
                    children="You uploaded the wrong file!",
                    color="danger",
                    dismissable=True,
                    is_open=False,  #intiallty hidden
                    className="mt-2"
                ),
            html.H4("Upload Data and Water Network Overview", className='font-weight-bold mb-4'),
            html.Div(
                dcc.Upload(
                    id='upload-input1',
                    children=html.Button(
                        "Upload Input File",
                        className='button'
                    ),
                    multiple=False
                ),
                className='mb-3'
            ),
            html.Div(
                dcc.Upload(
                    id='upload-Output1',
                    children=html.Button(
                        "Upload 1st Output File",
                        className='button'
                    ),
                    multiple=False
                ),
                className='mb-3'
            ),
            html.Div(
                dcc.Upload(
                    id='upload-Output2',
                    children=html.Button(
                        "Upload 2nd Output File",
                        className='button'
                    ),
                    multiple=False
                ),
                className='mb-3'
            ),
            html.Div([
                html.H4("Water Network Overview", className='font-weight-bold mt-4'),
                html.P(id='network-name', children="Network Name: "),
                html.P(id='supply-hours', children="Supply Hours: "),
                html.P(id='active-nodes', children="Active Nodes: "),
                html.P(id='links', children="Links: "),
                html.P(id='source', children="Source Node ID: "),
                html.P(id='total-cost1', children="Total Cost of 1st Output File: "),
                html.P(id='total-cost2', children="Total Cost of 2nd Output File: "),
                html.P(id='diff-cost', children="Difference in Cost : ")
            ], className='card mt-4'),
            # html.H4("Do you want to change the Input?", className='text-primary mt-4 mb-4 font-weight-bold'),
            # dbc.Label("Select an option", className='text-primary font-weight-bold'),
            # dcc.Dropdown(
            #     id='Changes',
            #     options=[
            #         {'label': 'Node', 'value': '1'},
            #         {'label': 'Pipe', 'value': '2'},
            #         {'label': 'Commercial', 'value': '3'}
            #     ],
            #     placeholder='Select an option',
            #     className='dropdown mb-3'
            # ),
            # dcc.Dropdown(
            #     id='dropdown-2',
            #     options=[],
            #     placeholder='Select another option',
            #     className='dropdown mb-3'
            # ),
            # dcc.Dropdown(
            #     id='dropdown-3',
            #     options=[],
            #     placeholder='Select another option',
            #     className='dropdown mb-3'
            # ),
            # dbc.Label("Enter a value", className='text-primary font-weight-bold'),
            # dbc.Input(
            #     id='text-input',
            #     type='text',
            #     placeholder='Enter a value',
            #     className='input mb-3'
            # ),
            # dbc.Button(
            #     'Submit',
            #     id='submit-button',
            #     color="dark",
            #     className='button mt-3 mb-4'
            # ),
            # html.A('Download Updated File', id='download-link', download="updated_data.xlsx", href="", target="_blank", style={'display': 'none'}),
            
        ], style={
            'height': '100%',
            'overflowY': 'auto',
            'padding': '20px',
            'backgroundColor': '#F0F2F5',
            'borderRadius': '10px',
            'boxShadow': '0px 0px 10px rgba(0, 0, 0, 0.1)',
        })

        # Main content area
        main_content = html.Div(
        [
            dbc.Container([
                dbc.Row([
                    dbc.Col(left_panel, md=4, style={'paddingRight': '15px'}),
                    dbc.Col(html.Div([
                        html.H4("Current Statistics", className='font-weight-bold mb-4'),
                        dcc.Tabs(id='main-tab', value='main-graph', children=[
                            dcc.Tab(label='Main Graph', value='main-graph', children=[
                                dcc.Graph(id='graph-1', config={'modeBarButtonsToRemove': ['select2d', 'lasso2d']}, style={'height': '100vh'})]),
                            dcc.Tab(label='1st File', value='1stfile', id="tab-1stfile", children=[
                                html.Div([
                                        dcc.Tabs(
                                            id='inner-tab-1stfile',
                                            value='demand',
                                            children=[
                                                dcc.Tab(label='Node Graph', value='demand', children=html.Div([
                                                    dbc.Row([
                                                        dbc.Col(html.Div(id='1stfile-demand-1', className='p-3 mb-3 ps-5',
                                                                        style={'backgroundColor': 'white', 'height':'300px', 'overflowY': 'auto', 'paddingLeft': '80px'})),
                                                    ]),
                                                    dcc.Graph(id='graph-2', config={'modeBarButtonsToRemove': ['select2d', 'lasso2d']}, style={'height': '90vh'})
                                                ], className='mt-3')),

                                                dcc.Tab(label='Pipes', value='length', children=html.Div([
                                                    dbc.Row([
                                                        dbc.Col(html.Div(id='1stfile-length-1', className='p-3 mb-3 ps-5',
                                                                        style={'backgroundColor': 'white', 'height':'300px',  'overflowY': 'auto', 'paddingLeft': '80px'})),]),
                                                    dcc.Graph(id='graph-4', config={'modeBarButtonsToRemove': ['select2d', 'lasso2d']}, style={'height': '90vh'})
                                                ], className='mt-3')),
                                            ],
                                            className='mt-3'
                                        )
                                    ]),
                                ]), 
                            dcc.Tab(label='2nd file', value='2ndfile', id="tab-2ndfile", children=[
                                    html.Div([
                                        dcc.Tabs(
                                            id='inner-tab-2ndfile',
                                            value='demand',
                                            children=[
                                                dcc.Tab(label='Nodes', value='demand', children=html.Div([
                                                    dbc.Row([
                                                        dbc.Col(html.Div(id='2ndfile-demand-1', className='p-3 mb-3 ps-5',
                                                                        style={'backgroundColor': 'white', 'height':'300px',  'overflowY': 'auto', 'paddingLeft': '80px'})),
                                                    ]),
                                                    dcc.Graph(id='graph-8', config={'modeBarButtonsToRemove': ['select2d', 'lasso2d']}, style={'height': '90vh'})
                                                ], className='mt-3')),

                                                dcc.Tab(label='Pipes', value='length', children=html.Div([
                                                    dbc.Row([
                                                        dbc.Col(html.Div(id='2ndfile-length-1', className='p-3 mb-3 ps-5',
                                                                        style={'backgroundColor': 'white', 'height':'300px',  'overflowY': 'auto', 'paddingLeft': '80px'})),
                                                    ]),
                                                    dcc.Graph(id='graph-10', config={'modeBarButtonsToRemove': ['select2d', 'lasso2d']}, style={'height': '90vh'})
                                                ], className='mt-3')),
                                                
                                            ],
                                            className='mt-3'
                                        )
                                    ]),
                                ]),
                        ], className='mb-3'),
                        # html.Div(id='graph-tabs-content')  # Placeholder for dynamic content
                    ]), md=8),
                ]),
                modal
            ], fluid=True)
        ],
        style={'padding': '10px'})

        # Main layout
        return html.Div(
            [
                data_stores,
                dbc.Row([
                    dbc.Col(sidebar, width=2, style={'padding': '0'}),
                    dbc.Col(main_content, width=10, style={
                        'height': '100vh',
                        'overflowY': 'auto'
                    })
                ], className='g-0')  # Remove gutter spacing for closer alignment
            ],
            id="main-container"
        )
