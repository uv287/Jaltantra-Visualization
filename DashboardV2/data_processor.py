import base64
import io
import xlrd
import networkx as nx
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from logger_config import logger

class DataProcessor:

    def process_upload(self, contents, filename):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        buffer = io.BytesIO(decoded)

        # Read the Excel file
        workbook = xlrd.open_workbook(file_contents=buffer.getvalue())
        sheet = workbook.sheet_by_index(0)  # Select the first sheet

        data = []
        for row_idx in range(sheet.nrows):
            row = sheet.row_values(row_idx)
            data.append(row)
            
        logger.info(f"Processed file: {filename} with {len(data)} rows.")

        return data
    
    def process_source(self, df):
        source_ID = df.loc[df[0] == "Source Node ID", 3].values[0]
        source_Elevation = df.loc[df[0] == "Source Elevation", 3].values[0]
        minp = df.loc[df[0] == "Minimum Node Pressure", 3].values[0]
        logger.info("Source ID : " + str(source_ID))
        logger.info("Sourcec Elevation : "+str(source_Elevation))
        logger.info("Minimum Pressure :" + str(minp))
        return source_ID, source_Elevation, minp
    
    def general_data(self, df):
        # Get value from row where first column is "Network Name"
        network_name = df.loc[df.iloc[:, 0] == "Network Name", 3].values
        network_name = network_name[0] if len(network_name) > 0 else ""
            
        supply = df.loc[df.iloc[:, 0] == "Number of Supply Hours", 3].values
        supply = supply[0] if len(supply) > 0 else ""
        
        logger.info("Network name : " + network_name)
        logger.info("Supply Hour : " + str(supply))
        
        return  network_name, supply

    def validate_node_data(self, node_data, mainNodeData):
        # Validate node data against mainNodeData
        if (len(node_data["nodeID"])!=len(mainNodeData["nodeID"])):
            return False
        return True

    def process_node_data(self, df, minp):
        # 1. Find start index: where 'Node ID' appears in first column
        start_index = df[df[0] == "Node ID"].index[0] + 1

        # 2. Find end index: first row with empty first column after start
        empty_rows = df.loc[start_index:, 0].isna()
        if empty_rows.any():
            end_index = empty_rows.idxmax()  # first empty row
        else:
            end_index = df.shape[0]  # till the end

        # 3. Slice the relevant rows
        node_df = df.iloc[start_index:end_index].copy()

        # 4. Fill in Demand and MinPressure with defaults
        node_df[3] = node_df[3].replace(np.nan, 0)
        node_df[4] = node_df.apply(lambda row: row[4] if pd.notna(row[4]) else minp, axis=1)

        # 5. Build the dictionary
        node_data = {
            "nodeID": node_df[0].tolist(),
            "Elevation": node_df[2].tolist(),
            "Demand": node_df[3].tolist(),
            "MinPressure": node_df[4].tolist()
        }
        
        logger.info(str(node_data))

        return node_data

    def process_pipe_data(self, df):
        # 1. Find start index (row after 'Pipe ID')
        start_index = df[df[0] == "Pipe ID"].index[0] + 1
        # logger.info(start_index)

        # 2. Find end index (first empty first column after start_index)
        empty_rows = df.loc[start_index:, 0].isna() | (df.loc[start_index:, 0] == '')
        if empty_rows.any():
            end_index = empty_rows.idxmax()  # first empty or blank row index
        else:
            end_index = df.shape[0]

        # 3. Slice the relevant rows
        pipe_df = df.iloc[start_index:end_index].copy()

        # 4. Fix 'length' column: replace empty or NaN with '0'
        pipe_df[3] = pipe_df[3].replace(np.nan, 0)

        pipe_df[6] = pipe_df[6].apply(lambda x: 0 if pd.isna(x) else 1)

        # 6. Build dictionary
        pipe_data = {
            "pipeID": pipe_df[0].tolist(),
            "startNode": pipe_df[1].tolist(),
            "endNode": pipe_df[2].tolist(),
            "length": pipe_df[3].tolist(),
            "parallel": pipe_df[6].tolist()
        }
        
        logger.info(str(pipe_data))

        return pipe_data

    def process_commercial_pipe_data(self, df):
        # Find index where first column == "Diameter"
        start_idx = df.index[df.iloc[:, 0] == "Diameter"]
        if start_idx.empty:
            return {"diameters": [], "roughness": [], "cost": []}
        start_idx = start_idx[0] + 1  # Start from the row after "Diameter"
        
        # Slice the dataframe from start_idx to the end
        df_slice = df.iloc[start_idx:].copy()
        
        # Find the first empty or NaN row in the first column after start_idx
        empty_rows = df_slice[df_slice.iloc[:, 0].isna() | (df_slice.iloc[:, 0] == '')]
        
        if not empty_rows.empty:
            end_idx = empty_rows.index[0]
            df_slice = df.loc[start_idx:end_idx - 1]  # up to row before empty
        else:
            df_slice = df_slice  # no empty row, take all rows after start_idx
        
        # Now extract columns 0,1,2 as lists
        commercial_pipe_data = {
            "diameters": df_slice.iloc[:, 0].tolist(),
            "roughness": df_slice.iloc[:, 1].tolist(),
            "cost": df_slice.iloc[:, 2].tolist()
        }
        
        logger.info(str(commercial_pipe_data))
        return commercial_pipe_data
    
    def process_esr_cost_data(self, sheet):
        esr_cost_data = {
            "Minimum Capacity": [],
            "Maximum Capacity": [],
            "Base Cost": [],
            "Unit Cost": []
        }

        # Extract ESR cost data
        # Assuming the structure of ESR data is well defined
        # Implement the extraction logic here

        return esr_cost_data

    def process_manual_pump_data(self, sheet):
        manual_pump_data = {
            "pump_id": [],
            "power": [],
            "location": []
        }

        # Extract Manual Pump Data
        # Implement the extraction logic here based on the structure of the data

        return manual_pump_data

    def process_valve_data(self, sheet):
        valve_data = {
            "valve_id": [],
            "type": [],
            "location": []
        }

        return valve_data

    def create_network_graph(self, node_data, pipe_data):
        G = nx.Graph()  # For an undirected graph.

        # Add nodes to the graph
        for node in node_data["nodeID"]:
            G.add_node(node)

        # Add edges to the graph based on pipe data
        for start_node, end_node, length in zip(pipe_data["startNode"], pipe_data["endNode"], pipe_data["length"]):
            # print(type(length))
            G.add_edge(start_node, end_node, length=float(length))
            
        logger.info(f"Created network graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        return G
    
    def process_edges_hovertext(self, G, pos, pipe_data):
        """Process edge data for Plotly visualization, including midpoints for labeling."""

        # Extract pipe data from the dataframe into a dictionary with tuples as keys
        pipe_id_map = {}
        id_length_map={}
        id_par_map={}
        id_start_map={}
        id_end_map={}
        
        for idx in range(len(pipe_data['pipeID'])):
            start_node = pipe_data['startNode'][idx]
            end_node = pipe_data['endNode'][idx]
            pipe_id = pipe_data['pipeID'][idx]
            # Use both (start, end) and (end, start) to handle undirected edges
            pipe_id_map[(start_node, end_node)] = pipe_id
            pipe_id_map[(end_node, start_node)] = pipe_id
            id_length_map[pipe_id] = pipe_data['length'][idx]
            id_start_map[pipe_id] = start_node
            id_end_map[pipe_id] = end_node
            # print(pipe_data['parallel'][idx])
            # print(type(pipe_data['parallel'][idx]))
            if int(pipe_data['parallel'][idx]==1) :
                id_par_map[pipe_id]="Allowed"
            else :
                id_par_map[pipe_id]="Not Allowed"

        edge_x = []
        edge_y = []
        edge_text = []
        edge_label_x = []
        edge_label_y = []
        edge_label_text = []

        # Iterate through edges in the graph and match with pipe IDs
        for edge in G.edges():
            start_node, end_node = edge
            x0, y0 = pos[start_node]
            x1, y1 = pos[end_node]

            # Append coordinates for the edge line
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            # Generate a pipe ID label based on start and end node
            pipe_id = pipe_id_map.get((start_node, end_node), "Unknown Pipe ID")

            # Add text for hover on the edges
            edge_text.extend([
                f"Pipe ID: {pipe_id} <br> Start Node: {id_start_map[pipe_id]} <br> End Node: {id_end_map[pipe_id]} <br> length : {id_length_map[pipe_id]} <br> Parallel : {id_par_map[pipe_id]}",  # Text for the start point
            ])

            # Compute the midpoint for label positioning
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2

            # Append midpoint coordinates and text for the label
            edge_label_x.append(mid_x)
            edge_label_y.append(mid_y)
            edge_label_text.append(f"{pipe_id}")
            
        logger.info(f"Processed {len(edge_x)} edges for visualization.")
            
            # #create hover data
            # hover_text.append()

        return {
            'edge_x': edge_x,
            'edge_y': edge_y,
            'edge_text': edge_text,
            'edge_label_x': edge_label_x,
            'edge_label_y': edge_label_y,
            'edge_label_text': edge_label_text,
        }
        
    def process_nodes_for_plotting(self, G, pos, node_data):
        """Process node data for Plotly visualization."""
        
        id_Elevation_map={}
        id_Demand_map={}
        id_MinP_map={}
        
        for idx in range(len(node_data['Elevation'])):
            node_id=node_data['nodeID'][idx]
            node_elevation=node_data['Elevation'][idx]
            node_demand=node_data['Demand'][idx]
            node_minP=node_data['MinPressure'][idx]
            
            id_Elevation_map[node_id]=node_elevation
            id_Demand_map[node_id]=node_demand
            if node_minP=="":
                id_MinP_map[node_id]=node_minP

        # Prepare lists for storing node data
        node_x = []
        node_y = []
        node_text = []
        node_hovertext = []

        # Iterate over nodes to populate x, y, text, and hovertext lists
        for node in G.nodes():
            x, y = pos[node]  # Get the position of the node
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}")  # This will display the node identifier as text on the graph

            # Assuming node_data is a dictionary with node-specific info
            hover_text = (
                f"Node ID: {node}<br>"
                f"Elevation: {id_Elevation_map[node]}<br>"
                f"Demand: {id_Demand_map[node]}"
                # f"Minimum Pressure: {id_MinP_map[node]}"
            )
            node_hovertext.append(hover_text)
        logger.info(f"Processed {len(node_x)} nodes for visualization.")

        return node_x, node_y, node_text, node_hovertext
        
    def generate_layout(self, G):
        seed_value = 42  # Set a seed value for reproducibility
        pos = nx.spring_layout(G,k=3.0, iterations=500, seed=seed_value)
        logger.info(f"Generated layout for {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        return pos
    
    

