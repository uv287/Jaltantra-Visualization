from dash import Input, Output, State, callback, ctx , no_update
import dash
import pandas as pd
from data_processor import DataProcessor
import plotly.graph_objects as go
import base64
import xlrd  # type: ignore
import io
from data_processor import DataProcessor
from new_inputfile import NewInputFile
from output_data_processor import OutputDataProcessor
from figure_generator import FigureGenerator
from dash import dcc, html
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
from graph_tabs import graph_tab_contents # Import the graph_tab_contents from the graph_tabs.py file
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from logger_config import logger  # Import the logger from the logger_config.py file

def register_callbacks(app):
    
    #update the dropdown function
    @app.callback(
        Output('dropdown-2', 'options'),
        Output('dropdown-3', 'options'),
        Input('Changes', 'value'),
        State('node-data-store', 'data'),
        State('pipe-data-store', 'data')
    )
    def update_dropdown_options(selected_value, node_data, pipe_data):
        options_dropdown_2 = []
        options_dropdown_3 = []

        if selected_value is None:
            return options_dropdown_2, options_dropdown_3  # No options if nothing is selected

        # Define options based on the first dropdown selection
        if selected_value == '1':  # Node selected
            options_dropdown_2 = [{'label': f'Node {node_id}', 'value': str(node_id)} for node_id in node_data.get("nodeID", [])]
            options_dropdown_3 = [{'label': 'Elevation', 'value': 'Elevation'},
                                  {'label': 'Demand', 'value': 'Demand'},]
        elif selected_value == '2':  # Pipe selected
            options_dropdown_2 = [{'label': f'Pipe {pipe_id}', 'value': str(pipe_id)} for pipe_id in pipe_data.get("pipeID", [])]
            options_dropdown_3 = [{'label': 'Parallel', 'value': 'parallel'},]
        elif selected_value == '3':  # Commercial selected
            options_dropdown_2 = [{'label': 'Add', 'value': 'E'},
                                  {'label': 'Remove', 'value': 'F'}]
            options_dropdown_3 = []  # Clear dropdown-3 options if 'Commercial' is selected

        return options_dropdown_2, options_dropdown_3
    #   {'label': 'Minimum Pressure', 'value': 'Minimum Pressure'},] 
    
    
    @app.callback(
        [Output('download-link', 'href'), Output('download-link', 'style')],
        Input('Changes', 'value'),
        Input('dropdown-2', 'value'),
        Input('dropdown-3', 'value'),
        Input('text-input','value'),
        Input('submit-button','n_clicks'),
        State('input-data', 'data')
    )
    def new_file(option1,option2,option3,textvalue,n_clicks, data):
        if(n_clicks and n_clicks>0) :
            if option1 and option2 and option3 and textvalue is not None:
                
                new_inputfile=NewInputFile()
                
                #for the Node
                if option1=='1' :  
                    #if elevation is changed
                    if option3=='Elevation' :
                        data = new_inputfile.change_elevation(data, option2, textvalue)
                    
                    #if Demand is changed
                    elif option3=='Demand' :   
                        data = new_inputfile.change_demand(data, option2,textvalue)
                          
                #for the pipe
                if option1=='2' :    
                    data = new_inputfile.change_pipe_parallel(data, option2, textvalue)
                      
                #for the commercial pipe
                if option1=='3' : 
                    if option2=='E':   
                        data= new_inputfile.add_commercial_pipe(data, textvalue)
                        
                    if option2=='F':
                        data = new_inputfile.remove_commercial_pipe(data, textvalue)
                
                df = pd.DataFrame(data)

                # Save the DataFrame to an Excel file in memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                output.seek(0)

                # Encode the Excel file in Base64
                excel_data = output.getvalue()
                encoded_excel = base64.b64encode(excel_data).decode()

                # Create the href for download
                href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.df;base64,{encoded_excel}"

                # Make the download link visible and update its href
                return href, {'display': 'block'}

            # If the button hasn't been clicked, keep the link hidden
            return "", {'display': 'none'}

        return "",{'display': 'none'}
    
    
    #read data from the file and update the graphs
    @app.callback(
    [
        Output("file-alert", "is_open"),
        Output("file-alert", "children"),
        Output('input-data','data'),
        Output('node-data-store', 'data'),
        Output('pipe-data-store', 'data'),
        Output('commercial-pipe-data-store', 'data'),
        Output('esr-cost-data-store', 'data'),
        Output('manual-pump-data-store', 'data'),
        Output('valve-data-store', 'data'),
        Output('graph-1', 'figure'),
        Output('network-name', 'children'),
        Output('supply-hours', 'children'),
        Output('active-nodes', 'children'),
        Output('node-data-upload1', 'data'),
        Output('pipe-data-upload1', 'data'),
        Output('node-data-upload2', 'data'),
        Output('pipe-data-upload2', 'data'),
        Output('graph-2', 'figure'), Output('graph-4', 'figure'),
        Output('graph-8', 'figure'), Output('graph-10', 'figure'),
        Output('total-cost1','children'),
        Output('total-cost2','children'),
        Output('diff-cost', 'children'),
        Output('tc1', 'data'),
        Output('tc2', 'data'),
        Output('1stfile-demand-1', 'children'), 
        Output('1stfile-length-1', 'children'), 
        Output('2ndfile-demand-1', 'children'), 
        Output('2ndfile-length-1', 'children')
    ],
    [
        Input('upload-input1', 'contents'),
        Input('upload-Output1', 'contents'),
        Input('upload-Output2', 'contents'),
        Input('graph-1', 'figure')
    ],
    [
        State('node-data-store', 'data'),
        State('pipe-data-store', 'data'),
        State('commercial-pipe-data-store', 'data'),
        State('node-data-upload1', 'data'),
        State('pipe-data-upload1', 'data'),
        State('node-data-upload2', 'data'),
        State('pipe-data-upload2', 'data'),
        State('tc1', 'data'),
        State('tc2', 'data'),
        State('upload-input1', 'filename'),
        State('upload-Output1', 'filename')
    ]
    )
    def update_data(content ,content1, content2, mainfig, mainNodeData, mainPipeData, commercial_pipe_data, nodeData1stfile, pipeData1stfile, nodeData2ndfile, pipeData2ndfile, cost1, cost2, inputfilename, filename):
        if (content is None) and (content1 is None) and (content2 is None):
            return (
                    False, no_update, None,None,None, None, None, None, None, go.Figure(), f"Network Name: ", f"Supply Hours: ", f"Active Nodes: ",
                    None, None, None, None,
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                     "Total Cost 1st File: ", "Total Cost 2nd File: ", "Difference in Cost: ",
                     0,0,
                    "", 
                    "",
                    "",
                    ""
                    )

        triggered_id = ctx.triggered_id
        output1_data_processor=OutputDataProcessor()
        start =0 # to remove the recursion used in figure_genreator graph
        
        if triggered_id == 'upload-input1':
            data_processor = DataProcessor()

            # Process the uploaded file
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)
            # workbook = xlrd.open_workbook(file_contents=buffer.getvalue())
            # df = workbook.sheet_by_index(0)
            df = pd.read_excel(buffer,header=None)
            logger.info(f"File {inputfilename} uploaded and read successfully.") 
            
            logger.info(f"Processing data from {inputfilename}...")
            source_node, source_elevation, minp = data_processor.process_source(df)
            node_data = data_processor.process_node_data(df, minp)
            pipe_data = data_processor.process_pipe_data(df)
            commercial_pipe_data = data_processor.process_commercial_pipe_data(df)
            esr_cost_data = data_processor.process_esr_cost_data(df)
            manual_pump_data = data_processor.process_manual_pump_data(df)
            valve_data = data_processor.process_valve_data(df)
            
            network_name, supply_hours =  data_processor.general_data(df)
            
            node_data['nodeID'].insert(0,source_node)
            node_data['Elevation'].insert(0,source_elevation)
            node_data['Demand'].insert(0,-1)
            node_data['MinPressure'].insert(0,-1)
        
            
            logger.info(f"Node data and pipe data processed successfully from {inputfilename}.")
            logger.info(f"Input Node data: {node_data}")
            logger.info(f"Input Pipe data: {pipe_data}")
            G = data_processor.create_network_graph(node_data, pipe_data)
            pos = data_processor.generate_layout(G)

            # Create plotly traces for edges
            edge_data = data_processor.process_edges_hovertext(G, pos, pipe_data)

            # Create plotly trace for edges
            edge_trace = go.Scatter(
                x=edge_data['edge_x'],
                y=edge_data['edge_y'],
                hoverinfo='none',  # This means no hover information will be displayed
                mode='lines',  # This mode will plot lines and also display text labels
                # text=edge_data['edge_label_text'],  # Text to be displayed as labels on the plot
                line=dict(width=3, color='#bbb')  # Line attributes
            )
            
            logger.info("Edge trace created successfully.")

            # Create plotly trace for edge labels
            edge_label_trace = go.Scatter(
                x=edge_data['edge_label_x'],
                y=edge_data['edge_label_y'],
                text=edge_data['edge_label_text'],  # Text to be displayed as labels
                hovertext=edge_data['edge_text'],  # Hover information to be displayed when hovering over the labels
                mode='text',
                hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
                textposition='middle center',
                textfont=dict(
                    size=15,
                    color='red'  # You can change the color as needed
                )
            )
            
            logger.info("Edge label trace created successfully.")

            # Create plotly traces for nodes
            node_x, node_y, node_text, node_hovertext = data_processor.process_nodes_for_plotting(G, pos, node_data)

            # Create node trace
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                text=node_text,
                hovertext=node_hovertext,  # Use hovertext to provide detailed node information
                mode='markers+text',  # Show markers and labels
                hoverinfo='text',  # Display hovertext when hovering
                textposition='top center',
                marker=dict(
                    size=20,
                    color='blue',
                    line=dict(width=2, color='black')
                )
            )
            
            logger.info("Node trace created successfully.")

            # Create the figure
            fig = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                            layout=go.Layout(
                                title='Water Network',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                dragmode='pan'
                            ))
            # fig.update_layout(
            #     paper_bgcolor='white',   # Outside the plot area
            #     plot_bgcolor='#bbbbbb'     # Inside the plot area (where graph is drawn)
            # )
            
            logger.info("Input File Network created successfully.")
            input_data = df.to_dict('records')

            return (False, no_update, input_data, node_data, pipe_data, commercial_pipe_data, esr_cost_data, manual_pump_data, valve_data, fig , f"Network Name: {network_name}", f"Supply Hours: {supply_hours}", f"Active Nodes: {len(node_data['Demand'])}",
                    None, None, None, None,
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                    "Total Cost 1st File: ", "Total Cost 2nd File: ", "Difference in Cost: ",
                    0,0,
                    "",
                    "",
                    "",
                    ""
                    )
        if triggered_id == 'upload-Output1':
            logger.info(f"Processing Output1 data from {filename}...")
            contents = content1
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)
            # workbook = xlrd.open_workbook(file_contents=buffer.getvalue())
            # sheet= workbook.sheet_by_index(0)
            df = pd.read_excel(buffer,header=None)
            
            data_processor = DataProcessor()
            
            logger.info("Output1 data reading started...")
            node_data_1stfile = output1_data_processor.process_node_data(df)
            pipe_data_1stfile = output1_data_processor.process_pipe_data(df)
            sourceID, sourceElevation, sourceHead = output1_data_processor.process_source(df)
            
            total_length, total_cost = output1_data_processor.get_length_and_cost(df)
            
            diff_cost = ""
            
            if content2 is not None:
                diff_cost += f"Difference in Cost : {round(total_cost - cost2, 1):,}"
            else:
                diff_cost += f"Difference in Cost : "
                
            node_data_1stfile['nodeID'].insert(0,sourceID)
            node_data_1stfile['Elevation'].insert(0,sourceElevation)
            node_data_1stfile['Demand'].insert(0,-1)
            node_data_1stfile['Head'].insert(0,sourceHead)
            node_data_1stfile["Pressure"].insert(0,-1)
            node_data_1stfile["MinPressure"].insert(0,-1)
            logger.info("Output1 data reading completed successfully.")
            
            valid = data_processor.validate_node_data(node_data_1stfile, mainNodeData)
            
            if not valid:
                logger.error("Node data validation failed. Please check the input file.")
                return (True, "Data validation failed. Please check the Output file.",
                        no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                        no_update, no_update, no_update, no_update,
                        no_update, no_update,
                        no_update, no_update,
                        no_update, no_update, no_update,
                        no_update, no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update
                        )
            
            logger.info(f"Node data: {node_data_1stfile}")
            logger.info(f"Pipe data: {pipe_data_1stfile}")
            
            unique_parallel_pipes = output1_data_processor.get_unique_parallel_pipes(pipe_data_1stfile)
            
            logger.info(f"Unique parallel pipes: {unique_parallel_pipes}")
            
            #new class for the figure generator
            figGen = FigureGenerator()
            
            pos = figGen.extract_node_positions(mainfig)
            logger.info("Node positions extracted successfully.")
            
            G, no_of_pipes= figGen.create_graph_with_parallel_edges(pos, pipe_data_1stfile, unique_parallel_pipes)
            
            nodeFig_1stfile, nodeFig_2ndfile, par_1stfiletab_demand_1, par_2ndfiletab_demand_1 = figGen.create_node_1stfile_graph(pos,node_data_1stfile, pipe_data_1stfile, unique_parallel_pipes, mainNodeData, mainPipeData, nodeData2ndfile, pipeData2ndfile, G, start)
            
            # G, no_of_pipes = figGen.create_graph_with_parallel_and_mutliple_edges(pos, pipe_data_1stfile, unique_parallel_pipes)
            # G = figGen.create_graph_with_parallel_edges(pos, pipe_data_1stfile, unique_parallel_pipes)

            pipeFig_1stfile, pipeFig_2ndfile, par_1stfiletab_pipe_1, par_2ndfiletab_pipe_1 = figGen.create_pipe_1stfile_graph(pos,node_data_1stfile, pipe_data_1stfile, unique_parallel_pipes, no_of_pipes, mainNodeData,  mainPipeData, nodeData2ndfile, pipeData2ndfile, G, start)

            logger.info("Pipe output 1 figures created successfully.")
            logger.info(f"Total network length: {total_length}, Total cost: {round(total_cost,3)}")
            return (
                    False, no_update, no_update,no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                    node_data_1stfile, pipe_data_1stfile, nodeData2ndfile, pipeData2ndfile,
                    nodeFig_1stfile, pipeFig_1stfile,
                    nodeFig_2ndfile, pipeFig_2ndfile,
                    f"Total Cost of 1st File: {round(total_cost,3):,}", no_update, diff_cost,
                    total_cost, no_update,
                    DangerouslySetInnerHTML(par_1stfiletab_demand_1),
                    DangerouslySetInnerHTML(par_1stfiletab_pipe_1),
                    DangerouslySetInnerHTML(par_2ndfiletab_demand_1),
                    DangerouslySetInnerHTML(par_2ndfiletab_pipe_1)
                    )
        
        if triggered_id == 'upload-Output2':
            logger.info(f"Processing Output2 data from {filename}...")
            contents = content2
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)
            # workbook = xlrd.open_workbook(file_contents=buffer.getvalue())
            # sheet= workbook.sheet_by_index(0)
            df = pd.read_excel(buffer,header=None)
            
            data_processor = DataProcessor()
            
            logger.info("Output2 data reading started...")
            node_data_2ndfile = output1_data_processor.process_node_data(df)
            pipe_data_2ndfile = output1_data_processor.process_pipe_data(df)
            sourceID, sourceElevation, sourceHead = output1_data_processor.process_source(df)
            
            total_length, total_cost = output1_data_processor.get_length_and_cost(df)
            
            node_data_2ndfile['nodeID'].insert(0,sourceID)
            node_data_2ndfile['Elevation'].insert(0,sourceElevation)
            node_data_2ndfile['Demand'].insert(0,-1)
            node_data_2ndfile['Head'].insert(0,sourceHead)
            node_data_2ndfile["Pressure"].insert(0,-1)
            node_data_2ndfile["MinPressure"].insert(0,-1)
            logger.info("Output2 data reading completed successfully.")
            valid = data_processor.validate_node_data(node_data_2ndfile, mainNodeData)
            
            if not valid:
                logger.error("Node data validation failed. Please check the input file.")
                return (True, "Data validation failed. Please check the Output file.",
                        no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                        no_update, no_update, no_update, no_update,
                        no_update, no_update,
                        no_update, no_update,
                        no_update, no_update, no_update,
                        no_update, no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update)
            logger.info(f"Node data: {node_data_2ndfile}")
            logger.info(f"Pipe data: {pipe_data_2ndfile}")
            
            if content1 is not None:
                diff_cost = f"Difference in Cost : {round(cost1 - total_cost, 1):,} ({output1_data_processor.percentage_difference((cost1-total_cost), cost1)})"
            else:
                diff_cost = f"Difference in Cost : "
            
            unique_parallel_pipes = output1_data_processor.get_unique_parallel_pipes(pipe_data_2ndfile)
            logger.info(f"Unique parallel pipes: {unique_parallel_pipes}")
            
            #new class for the figure generator
            figGen = FigureGenerator()
            
            pos = figGen.extract_node_positions(mainfig)
            logger.info("Node positions extracted successfully.")
            
            G , no_of_pipes= figGen.create_graph_with_parallel_edges(pos, pipe_data_2ndfile, unique_parallel_pipes)
            
            nodeFig_2ndfile, nodeFig_1stfile, par_2ndfiletab_node_1, par_1stfiletab_node_1 = figGen.create_node_2ndfile_graph(pos,node_data_2ndfile, pipe_data_2ndfile, unique_parallel_pipes, mainNodeData, mainPipeData, nodeData1stfile, pipeData1stfile, G, start)
            
            logger.info("Node output 2ndfile figures created successfully.")
            
            # G, no_of_pipes = figGen.create_graph_with_parallel_and_mutliple_edges(pos, pipe_data_2ndfile, unique_parallel_pipes)
            
            pipeFig_2ndfile, pipeFig_1stfile, par_2ndfiletab_pipe_1, par_1stfiletab_pipe_1 = figGen.create_pipe_2ndfile_graph(pos,node_data_2ndfile, pipe_data_2ndfile, unique_parallel_pipes, no_of_pipes, mainNodeData,  mainPipeData, nodeData1stfile, pipeData1stfile, G, start)
            
            logger.info("Pipe output 2ndfile figures created successfully.")
            logger.info(f"Total network length: {total_length}, Total cost: {round(total_cost,3)}")
            ############# 2nd File data processing completed ##############

            return (
                False, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                nodeData1stfile, pipeData1stfile, node_data_2ndfile, pipe_data_2ndfile, 
                    nodeFig_1stfile, pipeFig_1stfile,
                    nodeFig_2ndfile, pipeFig_2ndfile,
                    no_update, f"Total Cost of 2nd File: {round(total_cost,3):,}", diff_cost,
                    no_update, total_cost,
                    DangerouslySetInnerHTML(par_1stfiletab_node_1),
                    DangerouslySetInnerHTML(par_1stfiletab_pipe_1),
                    DangerouslySetInnerHTML(par_2ndfiletab_node_1), 
                    DangerouslySetInnerHTML(par_2ndfiletab_pipe_1) 
                    )
        
        