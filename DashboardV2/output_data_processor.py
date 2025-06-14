import math
import plotly.graph_objs as go
import pandas as pd
from logger_config import logger
import matplotlib.colors as mcolors

class OutputDataProcessor :
    def safe_format(self, val):
        return f"{val:.{3}f}" if isinstance(val, (int, float)) else val
    
    def percentage_difference(self, diff, base):
        """
        Calculate the percentage difference
        """
        if base == 0:
            return 'N/A'
        else:
            return f"{(abs(diff)/ base) * 100:.2f}%"
    
    def value_to_color(self, value, min_val, max_val):
        if min_val >= 0:
            norm = mcolors.PowerNorm(gamma=0.5, vmin=min_val, vmax=max_val)  # gamma < 1 = better spread
            cmap = mcolors.LinearSegmentedColormap.from_list("red_scale", ["white", "darkred"])
            return mcolors.to_hex(cmap(norm(value)))

        elif max_val <= 0:
            norm = mcolors.PowerNorm(gamma=0.5, vmin=min_val, vmax=max_val)
            cmap = mcolors.LinearSegmentedColormap.from_list("green_scale", ["green", "white"])
            return mcolors.to_hex(cmap(norm(value)))

        else:
            mid = 0
            if value <= 0:
                norm = mcolors.PowerNorm(gamma=0.5, vmin=min_val, vmax=mid)
                cmap = mcolors.LinearSegmentedColormap.from_list("green_to_white", ["green", "white"])
            else:
                norm = mcolors.PowerNorm(gamma=0.5, vmin=mid, vmax=max_val)
                cmap = mcolors.LinearSegmentedColormap.from_list("white_to_red", ["white", "red"])
            return mcolors.to_hex(cmap(norm(value)))

    
    def process_source(self, df):
        source_ID = df.loc[df[0] == "Source Node ID", 3].values[0]
        source_Elevation = df.loc[df[0] == "Source Elevation", 3].values[0]
        source_Head = df.loc[df[0] == "Source Head", 3].values[0]
        
        logger.info("Source ID : "+str(source_ID))
        logger.info("Source Elevation : "+str(source_Elevation))
        logger.info("Source Head : "+str(source_Head))
        
        return source_ID,source_Elevation, source_Head
    
    def get_length_and_cost(self, df):
        total_len = df.loc[df[0] == "Total Length of Network", 3].values[0]
        total_cost = df.loc[df[0] == "Total Pipe Cost", 3].values[0]
        
        logger.info("Total length of Network : "+str(total_len))
        logger.info("Total Cost : "+str(total_cost))
        
        return total_len, total_cost
    
    def process_node_data(self, df):
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
        
        # 4. Create dictionary
        node_data = {
            "nodeID": node_df[0].tolist(),
            "Demand": node_df[2].tolist(),
            "Elevation": node_df[3].tolist(),
            "Head": node_df[4].tolist(),
            "Pressure": node_df[5].tolist(),
            "MinPressure": node_df[6].tolist()
        }
        
        logger.info("Node Data sucessfully created.")
        
        return node_data
    
    def process_pipe_data(self, df):
        # 1. Find start index: where 'Node ID' appears in first column
        start_index = df[df[0] == "Pipe ID"].index[0] + 1

        # 2. Find end index: first row with empty first column after start
        empty_rows = df.loc[start_index:].isna().all(axis=1)
        if empty_rows.any():
            end_index = empty_rows.idxmax()  # first empty row
        else:
            end_index = df.shape[0]  # till the end

        # 3. Slice the relevant rows
        pipe_df = df.iloc[start_index:end_index].copy()
        
        # 4. Forward-fill pipeID, startNode, endNode for merged rows
        pipe_df[[0, 1, 2]] = pipe_df[[0, 1, 2]].ffill().infer_objects(copy=False)
        
        # print(pipe_df)
        # 5. Mark "Parallel" pipes (column 14) and assign binary flags
        pipe_df['parallel'] = (pipe_df[14] == "Parallel").astype(int)

        # For every consecutive pair where 'Parallel' is 1, mark both rows as 1
        parallel_indices = pipe_df.index[pipe_df['parallel'] == 1].tolist()
        for idx in parallel_indices:
            if idx > 0:
                pipe_df.at[idx - 1, 'parallel'] = 1  # mark previous one too

        # 6. Build the final dictionary
        pipe_data = {
            "pipeID": pipe_df[0].tolist(),
            "startNode": pipe_df[1].tolist(),
            "endNode": pipe_df[2].tolist(),
            "length": pipe_df[3].tolist(),
            "flow": pipe_df[4].tolist(),
            "speed": pipe_df[5].tolist(),
            "diameter": pipe_df[6].tolist(),
            "roughness": pipe_df[7].tolist(),
            "headloss": pipe_df[8].tolist(),
            "cost": pipe_df[10].tolist(),
            "parallel": pipe_df['parallel'].tolist()
        }
        
        
        logger.info("Pipe Data created successfully")
        
        # print(pipe_data)

        return pipe_data
    
    def get_unique_parallel_pipes(self,pipe_data):
        """
        Function to get unique parallel pipes from the given pipe_data dictionary.

        Parameters:
        pipe_data (dict): A dictionary containing pipe information, with keys:
                        "pipeID", "startNode", "endNode", and "parallel".

        Returns:
        list of tuples: A list of unique (startNode, endNode) tuples
                        for pipes marked as parallel (parallel = 1).
        """
        # Set to store unique (pipeID, startNode, endNode) tuples
        unique_parallel_pipes = set()

        # Iterate through the pipe_data to find parallel pipes
        for i in range(len(pipe_data["pipeID"])):
            if int(pipe_data["parallel"][i]) == 1:
                # Get pipeID, startNode, and endNode
                start_node = pipe_data["startNode"][i]
                end_node = pipe_data["endNode"][i]

                # Create a tuple for the unique combination of pipeID, startNode, endNode without sorting nodes
                pipe_tuple = (start_node, end_node)

                # Add the tuple to the set (set automatically handles uniqueness)
                unique_parallel_pipes.add(pipe_tuple)
        
        logger.info(f"Parrallel pipes : {str(unique_parallel_pipes)}")

        # Convert the set to a list to return
        return list(unique_parallel_pipes)
    
    
    def process_nodes_1stfile_plotting(self, G, node_pos, node_demand_map, node_head_map, node_demand_2ndfile, node_head_2ndfile, diffrent_2ndfile):
        """Process nodes for plotting by extracting x, y, text, hovertext, and colors."""
        node_x = []
        node_y = []
        node_text = []
        node_hovertext = []
        node_colors = []   
        node_size = []

        # Iterate over nodes to populate x, y, text, hovertext, and colors
        for node in G.nodes():
            if(node in node_pos) :
                x= node_pos[node][0]
                y= node_pos[node][1]# Get the position of the node from the provided node_pos dictionary
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in diffrent_2ndfile:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"1st File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Demand : {self.safe_format(node_demand_map.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}<br>"
                    f"2nd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Demand : {self.safe_format(node_demand_2ndfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_2ndfile.get(node, 'N/A'))}<br>"
                )
            else:
                hover_text = f"Node ID: {node} <br> &nbsp; Demand : {self.safe_format(node_demand_map.get(node, 'N/A'))} <br> &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}"

            node_hovertext.append(hover_text)
            node_colors.append(G.nodes[node]['color'])  # Use the assigned color from the graph attributes
            node_size.append(G.nodes[node]['size'])
            
        logger.info("1stfile output File node hover text, color and size is created")

        # Return all lists prepared for plotting
        return node_x, node_y, node_text, node_hovertext, node_colors, node_size
    
    def process_nodes_2ndfile_plotting(self, G, node_pos, node_demand_map, node_head_map, node_demand_1stfile, node_head_1stfile , diffrent_1stfile):
        """Process nodes for plotting by extracting x, y, text, hovertext, and colors."""
        node_x = []
        node_y = []
        node_text = []
        node_hovertext = []
        node_colors = []   
        node_size = []  

        # Iterate over nodes to populate x, y, text, hovertext, and colors
        for node in G.nodes():
            if(node in node_pos) :
                x= node_pos[node][0]
                y= node_pos[node][1]# Get the position of the node from the provided node_pos dictionary
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in diffrent_1stfile:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"2nd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}<br>"
                    f"1st File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_1stfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_1stfile.get(node, 'N/A'))}<br>"
                )
            else:
                hover_text = (f"Node ID: {node} <br> "
                            f"&nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))} <br>"
                            f"&nbsp; Supply : {self.safe_format(node_head_map.get(node, 'N/A'))}"
                )   
            node_hovertext.append(hover_text)
            node_colors.append(G.nodes[node]['color'])  # Use the assigned color from the graph attributes
            node_size.append(G.nodes[node]['size'])

        logger.info("2ndfile output file node hover text, color and size is created.")
        # Return all lists prepared for plotting
        return node_x, node_y, node_text, node_hovertext, node_colors, node_size
    
    
    def process_nodes_for_diameter_graph_plotting(self, G, node_pos, elevation_map, node_head_map) : 
        node_x = []
        node_y = []
        node_text = []
        node_hovertext = []
        
        # Iterate over nodes to populate x, y, text, hovertext, and colors
        for node in G.nodes():
            if(node in node_pos) :
                x= node_pos[node][0]
                y= node_pos[node][1]# Get the position of the node from the provided node_pos dictionary
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in node_head_map:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"Head: {round(node_head_map[node],3)}<br>"
                    f"Elevation: {round(elevation_map[node],3)}"
                )
            else:
                hover_text = f"Node ID: {node}<br>Demand data unavailable"
            
            node_hovertext.append(hover_text)

        # Return all lists prepared for plotting

        logger.info("Node Data for the pipegraph is generated")
        
        return node_x, node_y, node_text, node_hovertext
    
    
    
    def process_edges_for_plotting(self, G, node_pos, pipe_data, unique_parallel_pipes):
        """Process edge data for Plotly visualization, including handling of parallel edges."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_hovertext = []
        # print("Edges : " , end= " ")
        
        # print(G.edges(keys=True))

        # Iterate over all edges in the graph
        for u, v, key in G.edges(keys=True):
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # Offset for parallel edges to make them visually distinct
                # For simplicity, we're just offsetting by a small value, e.g., ±0.02
                offset = 0.005 if key.endswith('_1') else -0.005
                edge_x.extend([x0 + offset, x1 + offset, None])
                edge_y.extend([y0 + offset, y1 + offset, None])
            else:
                # Regular edges
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            # Add text and hover information for each edge
            # pipe_id = pipe_data['pipeID'][int(key.split('_')[0])] if '_' in key else key
            hover_info = f"Pipe ID: {key} <br> Start Node: {u} <br> End Node : {v}"
            edge_hovertext.append(hover_info)
            edge_text.append(f"{key}.0")
        
        logger.info("Edge Data for the Node Graph are created")

        return edge_x, edge_y, edge_text, edge_hovertext
    
    
    
    def process_edges_for_diameter_graph_plotting_1stfile(self,G, node_pos, pipe_data, total_length_pipe_map, 
                                                          unique_parallel_pipes, different_pipe_2ndfile, min_diff, max_diff,
                                                          sorted_difference_cost_pipeid_2ndfile):
        """Process edge data for Plotly visualization, including handling of parallel and multiple edges between the Nodes."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_length ={}
        edge_traces= []
        edge_colors= {}
        
        logger.info(f"Different pipe from second file : {different_pipe_2ndfile}")

        # Iterate over all edges in the graph
        for u, v, full_key in G.edges(keys=True):
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # Offset for parallel edges to make them visually distinct
                # For simplicity, we're just offsetting by a small value, e.g., ±0.02
                #key is like 2_2 or 2_1 
                #this is cost=0 pipe
                if '_1' in full_key:
                    x0=x0+0.005
                    y0=y0+0.005
                    y1=y1+0.005
                    x1=x1+0.005
                    edge_color="#666666" #grey -> same length and diameter in both the file
                    edge_colors[full_key]="Grey"
                    edge_text.append(f'{full_key}')
                else : 
                    x0=x0-0.005
                    y0=y0-0.005
                    y1=y1-0.005
                    x1=x1-0.005
                    if int(full_key.split('_')[0]) in different_pipe_2ndfile:
                        edge_color=self.value_to_color(sorted_difference_cost_pipeid_2ndfile[int(full_key.split('_')[0])], min_diff, max_diff) 
                        #orange -> diffrent length and diameter from the 5 min file
                        edge_colors[full_key]="Dark Orange"
                    else:
                        edge_color="#666666" #grey -> same length and diameter and cost in both the file
                        edge_colors[full_key]="Grey"
                    edge_text.append(f'{full_key}')
                logger.info(f"{full_key} color is the {edge_colors[full_key]}")
            # Not parallel edge
            else:
                if int(full_key.split('_')[0]) in different_pipe_2ndfile:
                    edge_color=self.value_to_color(sorted_difference_cost_pipeid_2ndfile[int(full_key.split('_')[0])], min_diff, max_diff) 
                    edge_colors[full_key]="Dark Orange"
                else:
                    edge_color="#666666"
                    edge_colors[full_key]="Dark Grey" 
                edge_text.append(f'{full_key}.0')

            logger.info(f"{full_key} color is the {edge_colors[full_key]}")
        
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=3, color=edge_color)
            )
            edge_traces.append(edge_trace)
            
        logger.info("Edge traces, edge text and edge color for the pipe graph has been created sucessfully")

        return edge_traces, edge_text, edge_colors
    
    def process_edges_for_diameter_graph_plotting_2ndfile(self,G, node_pos, pipe_data, total_length_pipe_map, 
                                                          unique_parallel_pipes, different_pipe_1stfile, min_diff, max_diff,
                                                          sorted_difference_cost_pipeid_1stfile):
        """Process edge data for Plotly visualization, including handling of parallel and multiple edges between the Nodes."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_length ={}
        edge_traces= []
        edge_colors= {}
        
        logger.info("Different Pipe 1stfile : " + str(different_pipe_1stfile))

        # Iterate over all edges in the graph
        for u, v, full_key in G.edges(keys=True):
            
            # length = data['length']
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # print("key" + key)
                #this is for cost=0 pipe
                if '_1' in full_key:
                    x0=x0+0.005
                    y0=y0+0.005
                    y1=y1+0.005
                    x1=x1+0.005

                    edge_color="#666666" 
                    edge_colors[full_key]="Grey"
                    edge_text.append(f'{full_key}')
                #if cost is not equal to zero and key contains the  '_2'
                else : 
                    x0=x0-0.005
                    y0=y0-0.005
                    y1=y1-0.005
                    x1=x1-0.005
                    if int(full_key.split('_')[0]) in different_pipe_1stfile:
                        edge_color=self.value_to_color(sorted_difference_cost_pipeid_1stfile[int(full_key.split('_')[0])], min_diff, max_diff)
                        edge_colors[full_key]="Dark Orange"
                    else:
                        edge_color="#666666" #grey -> same length and diameter in both the file
                        edge_colors[full_key]="Dark Grey"
                    edge_text.append(f'{full_key}')

            # Not parallel edge
            else:
                key = int(float(full_key.split('+')[0]))
                if key in different_pipe_1stfile:
                    edge_color=self.value_to_color(sorted_difference_cost_pipeid_1stfile[int(full_key.split('_')[0])], min_diff, max_diff)
                    edge_colors[full_key]="Dark Orange"
                else:
                    edge_color="#666666"
                    edge_colors[full_key]="Dark Grey"
                edge_text.append(f'{full_key}.0')

            logger.info(f"{full_key} color is the {edge_colors[full_key]}")
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=3, color=edge_color)
            )
            edge_traces.append(edge_trace)
        logger.info("Edge traces, edge text and edge color for the pipe graph has been created sucessfully for 2ndfile graph")

        return edge_traces, edge_text, edge_colors
    
    def process_edge_label_positions_for_graph_plotting(self, G, pos, unique_parallel_pipes) :
        edge_label_x = []
        edge_label_y = []
        
        visited_edge = []

        # Iterate through all edges in the graph
        for u, v, key in G.edges(keys=True):
            # Get the positions of start and end nodes
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            pipe_id = key.split('+')[0]
            dx, dy = x1 - x0, y1 - y0
            length = (dx**2 + dy**2) ** 0.5

            # Check if the edge is a parallel edge and adjust label position accordingly
            if ((u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes)  :
                # Offset for parallel edges to make them visually distinct
                if '_1' in key:
                    offset = - 0.02  # First parallel edge offset
                     # Compute perpendicular offset directions
                    offset_x = -dy / length * offset
                    offset_y = dx / length * offset

                    # Compute the midpoint for label positioning with an offset
                    mid_x = (x0 + x1) / 2 + offset_x
                    mid_y = (y0 + y1) / 2 + offset_y
                    
                    # Append midpoint coordinates for label positioning
                    edge_label_x.append(mid_x)
                    edge_label_y.append(mid_y)
                elif '_2' in key  and pipe_id not in visited_edge:
                    visited_edge.append(pipe_id)
                    offset = 0.02  # Second parallel edge offset
                    
                     # Compute perpendicular offset directions
                    offset_x = -dy / length * offset
                    offset_y = dx / length * offset

                    # Compute the midpoint for label positioning with an offset
                    mid_x = (x0 + x1) / 2 + offset_x
                    mid_y = (y0 + y1) / 2 + offset_y
                    
                    # Append midpoint coordinates for label positioning
                    edge_label_x.append(mid_x)
                    edge_label_y.append(mid_y)
            else:
                # Compute the midpoint for label positioning without offset
                if(pipe_id not in visited_edge) :
                    visited_edge.append(pipe_id)
                    mid_x = (x0 + x1) / 2
                    mid_y = (y0 + y1) / 2
                    
                    # Append midpoint coordinates for label positioning
                    edge_label_x.append(mid_x)
                    edge_label_y.append(mid_y)
            
            # print("Visited_edges" + str(visited_edge))

        logger.info("Label position for the pipe has been created sucessfully")
        return edge_label_x, edge_label_y
    
    
    def process_edge_label_positions(self, G, node_pos, unique_parallel_pipes):
        """Process edge label positions for Plotly visualization, including handling of parallel edges."""

        edge_label_x = []
        edge_label_y = []

        # Iterate through all edges in the graph
        for u, v, key in G.edges(keys=True):
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge and adjust label position accordingly
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # Offset for parallel edges to make them visually distinct
                if key.endswith('_1'):
                    offset = 0.02  # First parallel edge offset
                elif key.endswith('_2'):
                    offset = -0.02  # Second parallel edge offset
                else:
                    offset = 0.0  # Default for non-parallel edges

                # Calculate the offset direction (perpendicular to the edge)
                dx, dy = x1 - x0, y1 - y0
                length = (dx**2 + dy**2) ** 0.5
                # Compute perpendicular offset directions
                offset_x = -dy / length * offset
                offset_y = dx / length * offset

                # Compute the midpoint for label positioning with an offset
                mid_x = (x0 + x1) / 2 + offset_x
                mid_y = (y0 + y1) / 2 + offset_y
            else:
                # Compute the midpoint for label positioning without offset
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2

            # Append midpoint coordinates for label positioning
            edge_label_x.append(mid_x)
            edge_label_y.append(mid_y)

        return edge_label_x, edge_label_y
    
    def process_edge_hovertext_for_diameter_graph_1stfile(self, G, node_pos, unique_parallel_pipes, edge_colors,
                                                          pipe_data, pipeData2ndfile, different_pipe_2ndfile, 
                                                          id_to_cost_map_1stfile, id_to_cost_map_2ndfile,
                                                          sorted_difference_cost_pipeid_2ndfile) :
        edge_hovertext_map = {}
        # Iterate over all edges in the graph
        for u, v, key in G.edges(keys=True):
            pipe_id = int(key.split('_')[0])  # Extract the pipe ID from the key
            hover_info =( f"Pipe ID : {key} <br>"
                            f"Start Node : {u} <br>"
                            f"End Node : {v} <br>")

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # if the edge is parallel, and cost is zero
                
                if '_1' in key:
                    for i in range(len(pipe_data["pipeID"])):
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        
                        if cost==0:
                            hover_info += (
                                        # f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>" 
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")

                    hover_info += (f"&nbsp; &nbsp; Total Cost : 0<br>")
                    
                elif '_2' in key : 
                    
                    #if pipe id is diffrent
                    if pipe_id in different_pipe_2ndfile:
                        hover_info += (f"1st File : <br>")
                        
                    for i in range(len(pipe_data["pipeID"])):
                        if pipe_data["pipeID"][i] == pipe_id:
                            diameter = pipe_data["diameter"][i]
                            length = pipe_data["length"][i]
                            cost = pipe_data["cost"][i]

                            if cost!=0:
                                hover_info += (
                                            f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                    
                    hover_info+=(f"&nbsp; &nbsp; Total Cost : {id_to_cost_map_1stfile[pipe_id]}<br><br>")
                    
                    if pipe_id in different_pipe_2ndfile:
                        hover_info+=(f"2nd File :<br>")
                        
                        for i in range(len(pipeData2ndfile["pipeID"])):
                            if pipeData2ndfile["pipeID"][i] == pipe_id:
                                diameter = pipeData2ndfile["diameter"][i]
                                length = pipeData2ndfile["length"][i]
                                cost = pipeData2ndfile["cost"][i]

                                if cost!=0:
                                    hover_info += (
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                        hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_2ndfile[pipe_id],3)}<br> <br>"
                                    f"&nbsp; Difference : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id],3)} ({self.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})")

            #edge is not parallel
            else:
                if pipe_id in different_pipe_2ndfile:
                    hover_info += (f"1st File : <br>")
                    
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]

                        if cost!=0:
                            hover_info += (
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                
                hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_1stfile[pipe_id],3)} <br><br>")
                
                if pipe_id in different_pipe_2ndfile:
                    hover_info+=(f"2nd File :<br>")
                    
                    for i in range(len(pipeData2ndfile["pipeID"])):
                        if pipeData2ndfile["pipeID"][i] == pipe_id:
                            diameter = pipeData2ndfile["diameter"][i]
                            length = pipeData2ndfile["length"][i]
                            cost = pipeData2ndfile["cost"][i]

                            if cost!=0:
                                hover_info += (
                                            f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                    hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_2ndfile[pipe_id],3)}<br> <br>"
                                f"&nbsp; Difference : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id],3)} ({self.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})")

            edge_hovertext_map[key]=hover_info
        hovertext=[]
        #for the list
        visited_edge = []

        # Iterate through all edges in the graph
        for u, v, key in G.edges(keys=True):
            pipe_id = key.split('+')[0]

            if ((u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes)  :
                if '_1' in key:
                    hovertext.append(edge_hovertext_map[pipe_id])
                elif '_2' in key  and pipe_id not in visited_edge:
                    visited_edge.append(pipe_id)
                    hovertext.append(edge_hovertext_map[pipe_id])
            else:
                if(pipe_id not in visited_edge) :
                    visited_edge.append(pipe_id)
                    hovertext.append(edge_hovertext_map[pipe_id])
        
        logger.info("Edge Hovertext has been created sucessfully for 1stfile graph")
        
        return hovertext
    
    
    def process_edge_hovertext_for_diameter_graph_2ndfile(self, G, node_pos, unique_parallel_pipes, edge_colors, pipe_data, pipeData1stfile, 
                                                          different_pipe_1stfile, 
                                                          id_to_cost_map_1stfile, id_to_cost_map_2ndfile, 
                                                          sorted_difference_cost_pipeid_1stfile) :
        edge_hovertext_map = {}

        # Iterate over all edges in the graph
        for u, v, key in G.edges(keys=True):
            
            pipe_id = int(key.split('_')[0])  # Extract the pipe ID from the key
            hover_info =( f"Pipe ID : {key} <br>"
                            f"Start Node : {u} <br>"
                            f"End Node : {v} <br>")

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # if the edge is parallel, and cost is zero
                
                if '_1' in key:
                    for i in range(len(pipe_data["pipeID"])):
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        
                        if cost==0:
                            hover_info += (
                                        f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>" 
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")

                    hover_info += (f"&nbsp; &nbsp; Total Cost : 0<br>")
                    
                    # edge_hovertext_map[full_pipe_id]=hover_info
                # if the edge is parallel, and cost is not zero
                elif '_2' in key :
                    #if the edge is parallel and cost is not zero,
                    if pipe_id in different_pipe_1stfile:
                        hover_info += (f"2nd File : <br>")
                        
                    for i in range(len(pipe_data["pipeID"])):
                        if pipe_data["pipeID"][i] == pipe_id:
                            diameter = pipe_data["diameter"][i]
                            length = pipe_data["length"][i]
                            cost = pipe_data["cost"][i]

                            if cost!=0:
                                hover_info += (
                                            f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")

                    hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_2ndfile[pipe_id],3)}<br><br>")

                    if pipe_id in different_pipe_1stfile:
                        hover_info+=(f"1st File :<br>")
                        
                        for i in range(len(pipeData1stfile["pipeID"])):
                            if pipeData1stfile["pipeID"][i] == pipe_id:
                                diameter = pipeData1stfile["diameter"][i]
                                length = pipeData1stfile["length"][i]
                                cost = pipeData1stfile["cost"][i]

                                if cost!=0:
                                    hover_info += (
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                        hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_1stfile[pipe_id],3)}<br> <br>"
                                    f"&nbsp; Difference : {round(sorted_difference_cost_pipeid_1stfile[pipe_id],3)} ({self.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})")

            #edge is not parallel
            else:
                if pipe_id in different_pipe_1stfile:
                    hover_info += (f"2nd File : <br>")
                    
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]

                        if cost!=0:
                            hover_info += (
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                
                hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_2ndfile[pipe_id],3)}<br><br>")
                
                if pipe_id in different_pipe_1stfile:
                    hover_info+=(f"1st File :<br>")

                    for i in range(len(pipeData1stfile["pipeID"])):
                        if pipeData1stfile["pipeID"][i] == pipe_id:
                            diameter = pipeData1stfile["diameter"][i]
                            length = pipeData1stfile["length"][i]
                            cost = pipeData1stfile["cost"][i]

                            if cost!=0:
                                hover_info += (
                                            f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Length : {round(length,3)} <br>"
                                            f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,3)} <br><br>")
                    hover_info+=(f"&nbsp; &nbsp; Total Cost : {round(id_to_cost_map_1stfile[pipe_id],3)}<br> <br>"
                                    f"&nbsp; Difference : {round(sorted_difference_cost_pipeid_1stfile[pipe_id],3)} ({self.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})")

            edge_hovertext_map[key]=hover_info

        hovertext=[]
        #for the list
        visited_edge = []

        # Iterate through all edges in the graph
        for u, v, key in G.edges(keys=True):
            pipe_id = key.split('+')[0]

            if ((u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes)  :
                if '_1' in key:
                    hovertext.append(edge_hovertext_map[pipe_id])
                elif '_2' in key  and pipe_id not in visited_edge:
                    visited_edge.append(pipe_id)
                    hovertext.append(edge_hovertext_map[pipe_id])
            else:
                if(pipe_id not in visited_edge) :
                    visited_edge.append(pipe_id)
                    hovertext.append(edge_hovertext_map[pipe_id])
        
        logger.info("Edge Hovertext has been created sucessfully for 2ndfile graph")
        
        return hovertext
    
        
    def process_main_network_pipedata(self,mainnode, mainpipe) : 
        total_length_map ={}
        elevation_map ={}
        for i in range(len(mainpipe["length"])):
            total_length_map[mainpipe["pipeID"][i]] = mainpipe["length"][i]
        
        for i in range(len(mainnode["Elevation"])):
            elevation_map[mainnode["nodeID"][i]] = mainnode["Elevation"][i]

        return total_length_map,elevation_map
    
            

    
    