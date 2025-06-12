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
    
    
    #read data from the 1st file and update the graphs
    @app.callback(
    [
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
        Output('node-data-upload3', 'data'),
        Output('pipe-data-upload3', 'data'),
        Output('graph-2', 'figure'), Output('graph-4', 'figure'),
        Output('graph-8', 'figure'), Output('graph-10', 'figure'),
        Output('graph-14', 'figure'), Output('graph-16', 'figure'),
        Output('total-network-length','children'),
        Output('total-cost1','children'),
        Output('total-cost2','children'),
        Output('total-cost3','children'),
        Output('1min-demand-1', 'children'), Output('1min-demand-2', 'children'),
        Output('1min-length-1', 'children'), Output('1min-length-2', 'children'),
        Output('5min-demand-1', 'children'), Output('5min-demand-2', 'children'),
        Output('5min-length-1', 'children'), Output('5min-length-2', 'children'),
        Output('1hr-demand-1', 'children'), Output('1hr-demand-2', 'children'),
        Output('1hr-length-1', 'children'), Output('1hr-length-2', 'children')
    ],
    [
        Input('upload-input1', 'contents'),
        Input('upload-Output1', 'contents'),
        Input('upload-Output2', 'contents'),
        Input('upload-Output3', 'contents'),
        Input('graph-1', 'figure'),
    ],
    [
        State('node-data-store', 'data'),
        State('pipe-data-store', 'data'),
        State('commercial-pipe-data-store', 'data'),
        State('node-data-upload1', 'data'),
        State('pipe-data-upload1', 'data'),
        State('node-data-upload2', 'data'),
        State('pipe-data-upload2', 'data'),
        State('node-data-upload3', 'data'),
        State('pipe-data-upload3', 'data'),
        State('upload-input1', 'filename'),
        State('upload-Output1', 'filename'),
    ]
    )
    def update_data(content ,content1, content2, content3, mainfig, mainNodeData, mainPipeData, commercial_pipe_data, nodeData1min, pipeData1min, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr, inputfilename, filename):
        if (content is None) and (content1 is None) and (content2 is None) and (content3 is None):
            return (
                    None,None,None, None, None, None, None, go.Figure(), f"Network Name: ", f"Supply Hours: ", f"Active Nodes: ",
                    None, None, None, None, None, None,
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                    "Total Network Length: ", "Total Cost 1 min: ", "Total Cost 5 min: ", "Total Cost 1 hr: ",
                    "", "",
                    "", "",
                    "", "",
                    "", "",
                    "", "",
                    "", ""
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
            
            logger.info("Input File Network created successfully.")
            input_data = df.to_dict('records')

            return (input_data, node_data, pipe_data, commercial_pipe_data, esr_cost_data, manual_pump_data, valve_data, fig , f"Network Name: {network_name}", f"Supply Hours: {supply_hours}", f"Active Nodes: {len(node_data['Demand'])}",
                    None, None, None, None, None, None,
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                    go.Figure(), go.Figure(),
                    "Total Network Length: ", "Total Cost 1 min: ", "Total Cost 5 min: ", "Total Cost 1 hr: ",
                    "", "",
                    "", "",
                    "", "",
                    "", "",
                    "", "",
                    "", ""
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
            
            logger.info("Output1 data reading started...")
            node_data_1min = output1_data_processor.process_node_data(df)
            pipe_data_1min = output1_data_processor.process_pipe_data(df)
            sourceID, sourceElevation, sourceHead = output1_data_processor.process_source(df)
            
            total_length, total_cost = output1_data_processor.get_length_and_cost(df)
            
            node_data_1min['nodeID'].insert(0,sourceID)
            node_data_1min['Elevation'].insert(0,sourceElevation)
            node_data_1min['Demand'].insert(0,-1)
            node_data_1min['Head'].insert(0,sourceHead)
            node_data_1min["Pressure"].insert(0,-1)
            node_data_1min["MinPressure"].insert(0,-1)
            logger.info("Output1 data reading completed successfully.")
            logger.info(f"Node data: {node_data_1min}")
            logger.info(f"Pipe data: {pipe_data_1min}")
            
            unique_parallel_pipes = output1_data_processor.get_unique_parallel_pipes(pipe_data_1min)
            
            logger.info(f"Unique parallel pipes: {unique_parallel_pipes}")
            
            #new class for the figure generator
            figGen = FigureGenerator()
            
            pos = figGen.extract_node_positions(mainfig)
            logger.info("Node positions extracted successfully.")
            
            G = figGen.create_graph_with_parallel_edges(pos, pipe_data_1min, unique_parallel_pipes)
            
            nodeFig_1min, nodeFig_5min, nodeFig_1hr, par_1mintab_demand_1, par_1mintab_demand_2, par_5mintab_demand_1, par_1hrtab_demand_1 = figGen.create_node_1min_graph(pos,node_data_1min, pipe_data_1min, unique_parallel_pipes, mainNodeData, mainPipeData, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr, G, start)
            
            logger.info("Node output 1 figures created successfully.")
            
            G, no_of_pipes = figGen.create_graph_with_parallel_and_mutliple_edges(pos, pipe_data_1min, unique_parallel_pipes)
            
            
            pipeFig_1min, pipeFig_5min, pipeFig_1hr, par_1mintab_pipe_1, par_1mintab_pipe_2, par_5mintab_pipe_1, par_1hrtab_pipe_1= figGen.create_pipe_1min_graph(pos,node_data_1min, pipe_data_1min, unique_parallel_pipes, no_of_pipes, mainNodeData,  mainPipeData, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr, G, start)
            
            logger.info("Pipe output 1 figures created successfully.")  
            logger.info(f"Total network length: {total_length}, Total cost: {total_cost}")
            return (
                    no_update,no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                    node_data_1min, pipe_data_1min, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr,
                    nodeFig_1min, pipeFig_1min,
                    nodeFig_5min, pipeFig_5min,
                    nodeFig_1hr, pipeFig_1hr,
                    f"Total Network Length: {total_length}", f"Total Cost 1 min: {total_cost}", no_update, no_update,
                    DangerouslySetInnerHTML(par_1mintab_demand_1),DangerouslySetInnerHTML(par_1mintab_demand_2),
                    DangerouslySetInnerHTML(par_1mintab_pipe_1),DangerouslySetInnerHTML(par_1mintab_pipe_2),
                    DangerouslySetInnerHTML(par_5mintab_demand_1),no_update,
                    DangerouslySetInnerHTML(par_5mintab_pipe_1),no_update,
                    DangerouslySetInnerHTML(par_1hrtab_demand_1),no_update, 
                    DangerouslySetInnerHTML(par_1hrtab_pipe_1),no_update,  
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
            
            logger.info("Output2 data reading started...")
            node_data_5min = output1_data_processor.process_node_data(df)
            pipe_data_5min = output1_data_processor.process_pipe_data(df)
            sourceID, sourceElevation, sourceHead = output1_data_processor.process_source(df)
            
            total_length, total_cost = output1_data_processor.get_length_and_cost(df)
            
            node_data_5min['nodeID'].insert(0,sourceID)
            node_data_5min['Elevation'].insert(0,sourceElevation)
            node_data_5min['Demand'].insert(0,-1)
            node_data_5min['Head'].insert(0,sourceHead)
            node_data_5min["Pressure"].insert(0,-1)
            node_data_5min["MinPressure"].insert(0,-1)
            logger.info("Output2 data reading completed successfully.")
            logger.info(f"Node data: {node_data_5min}")
            logger.info(f"Pipe data: {pipe_data_5min}")
            
            unique_parallel_pipes = output1_data_processor.get_unique_parallel_pipes(pipe_data_5min)
            logger.info(f"Unique parallel pipes: {unique_parallel_pipes}")
            
            #new class for the figure generator
            figGen = FigureGenerator()
            
            pos = figGen.extract_node_positions(mainfig)
            logger.info("Node positions extracted successfully.")
            
            G = figGen.create_graph_with_parallel_edges(pos, pipe_data_5min, unique_parallel_pipes)
            
            nodeFig_5min, nodeFig_1min, nodeFig_1hr, par_5mintab_node_1, par_5mintab_node_2, par_1mintab_node_1, par_1hrtab_node_2 = figGen.create_node_5min_graph(pos,node_data_5min, pipe_data_5min, unique_parallel_pipes, mainNodeData, mainPipeData, nodeData1min, pipeData1min, nodeData1hr, pipeData1hr, G, start)
            
            logger.info("Node output 5min figures created successfully.")
            
            G, no_of_pipes = figGen.create_graph_with_parallel_and_mutliple_edges(pos, pipe_data_5min, unique_parallel_pipes)
            
            pipeFig_5min, pipeFig_1min, pipeFig_1hr, par_5mintab_pipe_1, par_5mintab_pipe_2, par_1mintab_pipe_1, par_1hrtab_pipe_2 = figGen.create_pipe_5min_graph(pos,node_data_5min, pipe_data_5min, unique_parallel_pipes, no_of_pipes, mainNodeData,  mainPipeData, nodeData1min, pipeData1min, nodeData1hr, pipeData1hr, G, start)
            
            logger.info("Pipe output 5min figures created successfully.")
            logger.info(f"Total network length: {total_length}, Total cost: {total_cost}")
            ############# 5 min data processing completed ##################
            
            return (
                no_update,no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                nodeData1min, pipeData1min, node_data_5min, pipe_data_5min, nodeData1hr, pipeData1hr, 
                    nodeFig_1min, pipeFig_1min,
                    nodeFig_5min, pipeFig_5min,
                    nodeFig_1hr, pipeFig_1hr,
                    f"Total Network Length: {total_length}", no_update, f"Total Cost 5 min: {total_cost}", no_update,
                    DangerouslySetInnerHTML(par_1mintab_node_1),no_update,
                    DangerouslySetInnerHTML(par_1mintab_pipe_1),no_update,
                    DangerouslySetInnerHTML(par_5mintab_node_1),DangerouslySetInnerHTML(par_5mintab_node_2), 
                    DangerouslySetInnerHTML(par_5mintab_pipe_1),DangerouslySetInnerHTML(par_5mintab_pipe_2), 
                    no_update,DangerouslySetInnerHTML(par_1hrtab_node_2), 
                    no_update,DangerouslySetInnerHTML(par_1hrtab_pipe_2)
                    # no_update, total_cost, no_update,
                    # no_update, total_length, no_update
                    )
        
        if ctx.triggered_id == 'upload-Output3':
            
            logger.info(f"Processing Output3 data from {filename}...")
            contents = content3
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            buffer = io.BytesIO(decoded)
            # workbook = xlrd.open_workbook(file_contents=buffer.getvalue())
            # sheet= workbook.sheet_by_index(0)
            df = pd.read_excel(buffer,header=None)
            
            node_data_1hr = output1_data_processor.process_node_data(df)
            pipe_data_1hr = output1_data_processor.process_pipe_data(df)
            sourceID, sourceElevation, sourceHead = output1_data_processor.process_source(df)
            
            total_length, total_cost = output1_data_processor.get_length_and_cost(df)
            
            node_data_1hr['nodeID'].insert(0,sourceID)
            node_data_1hr['Elevation'].insert(0,sourceElevation)
            node_data_1hr['Demand'].insert(0,-1)
            node_data_1hr['Head'].insert(0,sourceHead)
            node_data_1hr["Pressure"].insert(0,-1)
            node_data_1hr["MinPressure"].insert(0,-1)
            
            logger.info("Output3 data reading completed successfully.")
            logger.info(f"Node data: {node_data_1hr}")
            logger.info(f"Pipe data: {pipe_data_1hr}")
            
            unique_parallel_pipes = output1_data_processor.get_unique_parallel_pipes(pipe_data_1hr)
            
            logger.info(f"Unique parallel pipes: {unique_parallel_pipes}")
            
            #new class for the figure generator
            figGen = FigureGenerator()
            
            pos = figGen.extract_node_positions(mainfig)
            
            G = figGen.create_graph_with_parallel_edges(pos, pipe_data_1hr, unique_parallel_pipes)
            
            nodeFig_1hr, nodeFig_1min, nodeFig_5min, par_1hrtab_node_1, par_1hrtab_node_2, par_1mintab_node_2, par_5mintab_node_2 = figGen.create_node_1hr_graph(pos,node_data_1hr, pipe_data_1hr, unique_parallel_pipes, mainNodeData, mainPipeData, nodeData1min, pipeData1min, nodeData5min, pipeData5min, G, start)
            
            logger.info("Node output 1hr figures created successfully.")
                     
            G, no_of_pipes = figGen.create_graph_with_parallel_and_mutliple_edges(pos, pipe_data_1hr, unique_parallel_pipes)
            
            pipeFig_1hr, pipeFig_1min, pipeFig_5min, par_1hrtab_pipe_1, par_1hrtab_pipe_2, par_1mintab_pipe_2, par_5mintab_pipe_2 = figGen.create_pipe_1hr_graph(pos,node_data_1hr, pipe_data_1hr, unique_parallel_pipes, no_of_pipes, mainNodeData,  mainPipeData, nodeData1min, pipeData1min, nodeData5min, pipeData5min, G, start)
            
            logger.info("Pipe output 1hr figures created successfully.")
            
            return (
                    no_update,no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                    nodeData1min, pipeData1min, nodeData5min, pipeData5min, node_data_1hr, pipe_data_1hr, 
                    nodeFig_1min, pipeFig_1min,
                    nodeFig_5min, pipeFig_5min,
                    nodeFig_1hr, pipeFig_1hr,
                    f"Total Network Length: {total_length}", no_update, no_update,f"Total Cost 1 hr: {total_cost}",
                    no_update,DangerouslySetInnerHTML(par_1mintab_node_2), 
                    no_update,DangerouslySetInnerHTML(par_1mintab_pipe_2),
                    no_update,DangerouslySetInnerHTML(par_5mintab_node_2), 
                    no_update,DangerouslySetInnerHTML(par_5mintab_pipe_2), 
                    DangerouslySetInnerHTML(par_1hrtab_node_1),DangerouslySetInnerHTML(par_1hrtab_node_2), 
                    DangerouslySetInnerHTML(par_1hrtab_pipe_1),DangerouslySetInnerHTML(par_1hrtab_pipe_2), 
                    # no_update, no_update, total_cost,
                    # no_update, no_update, total_length
                    )
        
    #If the tab is clicked then change the total cost and diffrence between them
    # @app.callback(
    #         [Output('total-cost', 'children'), Output('total-diff1', 'children'), Output('total-diff2', 'children')],
    #         Input('tab-1hr', 'value'),
    #         Input('tab-1min', 'value'),
    #         Input('tab-5min', 'value'),
    #         State('Cost-file1', 'data'),
    #         State('Cost-file2', 'data'),
    #         State('Cost-file3', 'data')
    #     )
    # def update_total_cost_and_diff(tab_1hr, tab_1min, tab_5min, total_cost_1min, total_cost_5min, total_cost_1hr):
    #     triggered_id = ctx.triggered_id
        
    #     if triggered_id == '1hr':
    #         total_cost = total_cost_1hr
    #         diff1 = total_cost_1hr - total_cost_1min
    #         diff2 = total_cost_1hr - total_cost_5min
    #         return (
    #             f"Total Cost: {total_cost}",
    #             f"Difference with 1hr: {diff1}",
    #             f"Difference with 5min: {diff2}"
    #         )
    #     elif triggered_id == '1min':
    #         total_cost = total_cost_1min
    #         diff1 = total_cost_1min - total_cost_1hr
    #         diff2 = total_cost_1min - total_cost_5min
    #         return (
    #             f"Total Cost: {total_cost}",
    #             f"Difference with 5min: {diff2}",
    #             f"Difference with 1hr: {diff1}"
    #         )
    #     elif triggered_id == '5min':
    #         total_cost = total_cost_5min
    #         diff1 = total_cost_5min - total_cost_1hr
    #         diff2 = total_cost_5min - total_cost_1min
    #         return (
    #             f"Total Cost: {total_cost}",
    #             f"Difference with 1min: {diff2}",
    #             f"Difference with 1hr: {diff1}"
    #         )
    #     else:
    #         # If no tab is selected, return default values
    #         return "Total Cost: 0", "", ""
