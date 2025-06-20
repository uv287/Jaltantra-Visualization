import math
import plotly.graph_objs as go
import pandas as pd
from logger_config import logger

class OutputDataProcessor :
    def safe_format(self, val):
        return f"{val:.{2}f}" if isinstance(val, (int, float)) else val
    
    def percentage_difference(self, diff, base):
        """
        Calculate the percentage difference
        """
        if base == 0:
            return 'N/A'
        else:
            return f"{(abs(diff)/ base) * 100:.2f}%"

    
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
    
    
    def process_nodes_1stfile_plotting(self, G, node_pos, node_demand_map, node_head_map, node_demand_2ndfile, node_head_2ndfile, node_demand_3rdfile, node_head_3rdfile, diffrent_2ndfile, diffrent_3rdfile):
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
            node_text.append(f"{node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in diffrent_2ndfile or node in diffrent_3rdfile:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"1st File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}<br>"
                    f"2nd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_2ndfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_2ndfile.get(node, 'N/A'))}<br>"
                    f"3rd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_3rdfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_3rdfile.get(node, 'N/A'))}<br>"
                )
            else:
                hover_text = f"Node ID: {node} <br> &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))} <br> &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}"

            node_hovertext.append(hover_text)
            node_colors.append(G.nodes[node]['color'])  # Use the assigned color from the graph attributes
            node_size.append(G.nodes[node]['size'])
            
        logger.info("1stfile output File node hover text, color and size is created")

        # Return all lists prepablue for plotting
        return node_x, node_y, node_text, node_hovertext, node_colors, node_size
    
    def process_nodes_2ndfile_plotting(self, G, node_pos, node_demand_map, node_head_map, node_demand_1stfile, node_head_1stfile, node_demand_3rdfile, node_head_3rdfile, diffrent_1stfile, diffrent_3rdfile):
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
            node_text.append(f"{node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in diffrent_1stfile or node in diffrent_3rdfile:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"2nd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}<br>"
                    f"1st File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_1stfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_1stfile.get(node, 'N/A'))}<br>"
                    f"3rd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_3rdfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_3rdfile.get(node, 'N/A'))}<br>"
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
        # Return all lists prepablue for plotting
        return node_x, node_y, node_text, node_hovertext, node_colors, node_size
    
    def process_nodes_3rdfile_plotting(self, G, node_pos, node_demand_map, node_head_map, node_demand_1stfile, node_head_1stfile, node_demand_2ndfile, node_head_2ndfile, diffrent_1stfile, diffrent_2ndfile):
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
            node_text.append(f"{node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in diffrent_1stfile or node in diffrent_2ndfile:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"3rd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_map.get(node, 'N/A'))}<br>"
                    f"1st File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_1stfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_1stfile.get(node, 'N/A'))}<br>"
                    f"2nd File: <br> &nbsp; &nbsp; &nbsp; &nbsp; Supply : {self.safe_format(node_demand_2ndfile.get(node, 'N/A'))}<br> &nbsp; &nbsp; &nbsp; &nbsp; Head : {self.safe_format(node_head_2ndfile.get(node, 'N/A'))}<br>"
                )
            else:
                hover_text = f"Node ID: {node} <br> &nbsp; Supply : {self.safe_format(node_demand_map.get(node, 'N/A'))} <br> &nbsp; Supply : {self.safe_format(node_head_map.get(node, 'N/A'))}"

            node_hovertext.append(hover_text)
            node_colors.append(G.nodes[node]['color'])  # Use the assigned color from the graph attributes
            node_size.append(G.nodes[node]['size'])
        
        logger.info("3rd File Output file node hover text, color and size is created")

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
            node_text.append(f"{node}")  # Node ID label

            # Generate detailed hover text for each node
            
            if node in node_head_map:
                hover_text = (
                    f"Node ID: {node}<br>"
                    f"Head: {round(node_head_map[node],2):,}<br>"
                    f"Elevation: {round(elevation_map[node],2):,}"
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
            edge_text.append(f"{key}")
        
        logger.info("Edge Data for the Node Graph are created")

        return edge_x, edge_y, edge_text, edge_hovertext
    
    
    
    def process_edges_for_diameter_graph_plotting_1stfile(self,G, node_pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_2ndfile, different_pipe_3rdfile, exist_pipe_status_2ndfile, exist_pipe_status_3rdfile):
        """Process edge data for Plotly visualization, including handling of parallel and multiple edges between the Nodes."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_length ={}
        edge_traces= []
        edge_colors= {}
        edge_text_color =[]
        
        # print("in latest fun : " + str(G.edges(keys=True)))
        logger.info("Exist Pipe 2ndfile : " + str(exist_pipe_status_2ndfile))
        logger.info("Exist Pipe 3rdfile : " + str(exist_pipe_status_3rdfile))

        # Iterate over all edges in the graph
        for u, v, full_key, data in G.edges(keys=True, data=True):
            
            length = data['length']
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # Offset for parallel edges to make them visually distinct
                # For simplicity, we're just offsetting by a small value, e.g., ±0.02
                #key is like 2_2+1 or 2_1+2 
                key = full_key.split('+')[0] #now key is like 2_2 or 2_1
                short_key = int(key.split('_')[0] )
                # print("key : " + key) 
                #this is cost=0 pipe
                if '_1' in key :
                    x0=x0+0.005
                    y0=y0+0.005
                    y1=y1+0.005
                    x1=x1+0.005
                    if not exist_pipe_status_2ndfile.get(short_key, True) and exist_pipe_status_3rdfile.get(short_key, True):
                            edge_color="#FF8500" #orange -> diffrent length and diameter from the 5 min file
                            edge_colors[full_key]="Dark Orange"
                            edge_text_color.append("blue")
                    elif not exist_pipe_status_3rdfile.get(short_key, True) and exist_pipe_status_2ndfile.get(short_key, True):
                        edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")
                    elif (not exist_pipe_status_2ndfile.get(short_key, True) and not exist_pipe_status_3rdfile.get(short_key, True)):
                        edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555" #grey -> same length and diameter in both the file
                        edge_colors[full_key]="Dark Grey"
                        edge_text_color.append("#939393")
                    edge_text.append(f'{key}')


                else :
                    total_length = total_length_pipe_map[int(float(key.split('_')[0]))]
                    # print("Total Length : " + str(total_length))
                    # print("Pipe Length : " + str(length))
                    #if parrallel pipe length is equal to the total length (distance between the 2 node= length of the pipe)
                    if(total_length == length) : 
                        x0=x0-0.005
                        y0=y0-0.005
                        y1=y1-0.005
                        x1=x1-0.005
                        if int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                            edge_color="#FF8500" 
                            #orange -> diffrent length and diameter from the 5 min file
                            edge_colors[full_key]="Dark Orange"
                            edge_text_color.append("blue")
                        elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                            edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                            edge_colors[full_key]="Dark Purple"
                            edge_text_color.append("red")
                        elif (int(key.split('_')[0]) in different_pipe_2ndfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                            edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                            edge_colors[full_key]="Dark Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#555555" #grey -> same length and diameter in both the file
                            edge_colors[full_key]="Dark Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                                                
                    #mixed edge length
                    else : 
                        #edge first time visible (key is like 2_2)
                        if int(float(key.split('_')[0])) not in edge_length:
                            edge_length[int(float(key.split('_')[0]))]=length
                            
                            distance_from_start = length / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                            
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l *  normalized_vector[1]
                            
                            x0=x0-0.005
                            y0=y0-0.005
                            y1=y1-0.005
                            x1=x1-0.005
                            if int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                edge_color="#E5C8AB"
                                edge_colors[full_key]="Light Orange"
                                edge_text_color.append("blue")
                            elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                edge_color="#D7C3E5"
                                edge_colors[full_key]="Light Purple"
                                edge_text_color.append("red")   
                            elif (int(key.split('_')[0]) in different_pipe_2ndfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                edge_color="#C8ACA1"
                                edge_colors[full_key]="Light Brown"
                                edge_text_color.append("red")
                            else:
                                edge_color="#aaaaaa"
                                edge_colors[full_key]="Light Grey" 
                                edge_text_color.append("#939393")
                            edge_text.append(f'{key}_2')
                            
                        else :
                            used_length = edge_length[int(float(key.split('_')[0]))]
                            edge_length[int(float(key.split('_')[0]))] = edge_length[int(float(key.split('_')[0]))]+length 
                            
                            distance_for_start = used_length /total_length
                            distance_from_start = (used_length+length) / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = (direction_vector[0] / l , direction_vector[1]/ l)
                            
                            xs=x0 + distance_for_start * normalized_vector[0]
                            ys=y0 + distance_for_start * normalized_vector[1]
                            
                            if((used_length+length)/total_length > 0.98) :
                                edge_x.extend([xs-0.005, x1-0.005, None])
                                edge_y.extend([ys-0.005, y1-0.005, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Dark Orange"
                                elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                    edge_color="#6A0DAD" 
                                    edge_colors[full_key]="Dark Purple"
                                elif (int(key.split('_')[0]) in different_pipe_2ndfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                    edge_color="#6D412F"
                                    edge_colors[full_key]="Dark Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="Dark Grey" 
                            else : 
                                x1=x0 + distance_from_start * normalized_vector[0]
                                y1=y0 + distance_from_start * normalized_vector[1]
                                edge_x.extend([xs, x1, None])
                                edge_y.extend([ys, y1, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Standard Orange"
                                elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                    edge_color="#6A0DAD"
                                    edge_colors[full_key]="Standard Purple"
                                elif (int(key.split('_')[0]) in different_pipe_2ndfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                    edge_color="#6D412f"
                                    edge_colors[full_key]="Standard Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="Standard Grey" 
                logger.info(f"{full_key} color is the {edge_colors[full_key]}")
            # Not parallel edge
            else:
                key = int(float(full_key.split('+')[0]))
                total_length = total_length_pipe_map.get(key)
                if(total_length == length) : 
                    if key in different_pipe_2ndfile and key not in different_pipe_3rdfile:
                        edge_color="#FF8500"
                        edge_colors[full_key]="Dark Orange"
                        edge_text_color.append("blue")
                    elif key in different_pipe_3rdfile and key not in different_pipe_2ndfile:
                        edge_color="#6A0DAD" 
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")
                    elif (key in different_pipe_2ndfile) and (key in different_pipe_3rdfile):
                        edge_color="#6D412F"
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555"
                        edge_colors[full_key]="Dark Grey" 
                        edge_text_color.append("#939393")
                    edge_text.append(f'{key}')
                    
                #mixed diameter edge
                else : 
                    #edge first time visible
                    
                    if key not in edge_length:
                        edge_length[key]=length

                        print(total_length)
                        distance_from_start = length / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        x1=x0 + distance_from_start *l * normalized_vector[0]
                        y1=y0 + distance_from_start *l * normalized_vector[1]
                        
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        if key in different_pipe_2ndfile and key not in different_pipe_3rdfile:
                            edge_color="#E5C8AB"
                            edge_colors[full_key]="Light Orange"
                            edge_text_color.append("blue")
                        elif key in different_pipe_3rdfile and key not in different_pipe_2ndfile:
                            edge_color="#D7C3E5"
                            edge_colors[full_key]="Light Purple"
                            edge_text_color.append("red")
                        elif (key in different_pipe_2ndfile) and (key in different_pipe_3rdfile):
                            edge_color="#C8ACA1"
                            edge_colors[full_key]="Light Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#aaaaaa"
                            edge_colors[full_key]="Light Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                    else :
                        used_length = edge_length[key]
                        edge_length[key] = edge_length[key]+length 
                        
                        distance_for_start = used_length /total_length
                        distance_from_start = edge_length[key] / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        xs=x0 + distance_for_start * l * normalized_vector[0]
                        ys=y0 + distance_for_start * l * normalized_vector[1]
                        
                        if((used_length+length)/total_length > 0.98) :
                            x0=xs
                            y0=ys
                            if key in different_pipe_2ndfile and key not in different_pipe_3rdfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Dark Orange"
                            elif key in different_pipe_3rdfile and key not in different_pipe_2ndfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Dark Purple"
                            elif (key in different_pipe_2ndfile) and (key in different_pipe_3rdfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Dark Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Dark Grey" 
                        else : 
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l * normalized_vector[1]
                            x0=xs
                            y0=ys
                            if key in different_pipe_2ndfile and key not in different_pipe_3rdfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Standard Orange"
                            elif key in different_pipe_3rdfile and key not in different_pipe_2ndfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Standard Purple"
                            elif (key in different_pipe_2ndfile) and (key in different_pipe_3rdfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Standard Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Standard Grey" 
                logger.info(f"{full_key} color is the {edge_colors[full_key]}")
        
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=3, color=edge_color)
            )
            edge_traces.append(edge_trace)
            
            logger.info("Edge traces, edge text and edge color for the pipe graph has been created sucessfully")

        return edge_traces, edge_text, edge_colors, edge_text_color
    
    def process_edges_for_diameter_graph_plotting_2ndfile(self,G, node_pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1stfile, different_pipe_3rdfile, exist_pipe_status_1stfile, exist_pipe_status_3rdfile):
        """Process edge data for Plotly visualization, including handling of parallel and multiple edges between the Nodes."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_length ={}
        edge_traces= []
        edge_colors= {}
        edge_text_color =[]
        
        logger.info("Different Pipe 1stfile : " + str(different_pipe_1stfile))
        logger.info("Different Pipe 3rdfile : " + str(different_pipe_3rdfile))
        logger.info("Exist Pipe 1stfile : " + str(exist_pipe_status_1stfile))
        logger.info("Exist Pipe 3rdfile : " + str(exist_pipe_status_3rdfile))

        # Iterate over all edges in the graph
        for u, v, full_key, data in G.edges(keys=True, data=True):
            
            length = data['length']
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                key = full_key.split('+')[0] #now key is like 2_2 or 2_1
                short_key = int(key.split('_')[0] )#now short_key is like 2
                # print("key" + key) 
                #this is cost=0 pipe
                if '_1' in key :
                    x0=x0+0.005
                    y0=y0+0.005
                    y1=y1+0.005
                    x1=x1+0.005
                    if (not exist_pipe_status_1stfile.get(short_key, True) and (exist_pipe_status_3rdfile.get(short_key, True))):
                            edge_color="#FF8500" #orange -> diffrent length and diameter from the 1st File file
                            edge_colors[full_key]="Dark Orange"
                            edge_text_color.append("blue")
                    elif not exist_pipe_status_3rdfile.get(short_key, True) and exist_pipe_status_1stfile.get(short_key, True):
                        edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")
                    elif (not exist_pipe_status_1stfile.get(short_key, True) and not exist_pipe_status_3rdfile.get(short_key, True)):
                        edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555" #grey -> same length and diameter in both the file
                        edge_colors[full_key]="Dark Grey"
                        edge_text_color.append("#939393")
                    edge_text.append(f'{key}')
                #if cost is not equal to zero and key contains the  '_2'
                else : 
                    total_length = total_length_pipe_map[int(float(key.split('_')[0]))]
                    print("Total Length : " + str(total_length))
                    print("Length : " + str(length))
                    #if parrallel pipe length is equal to the total length (distance between the 2 node= length of the pipe)
                    if(total_length == length) : 
                        print("Orange 2_2 Color Found for the key" + str(key))
                        x0=x0-0.005
                        y0=y0-0.005
                        y1=y1-0.005
                        x1=x1-0.005
                        if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                            edge_color="#FF8500" 
                            
                            #orange -> diffrent length and diameter from the 1st File file
                            edge_colors[full_key]="Dark Orange"
                            edge_text_color.append("blue")
                        elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                            edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                            edge_colors[full_key]="Dark Purple"
                            edge_text_color.append("red")
                        elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                            edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                            edge_colors[full_key]="Dark Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#555555" #grey -> same length and diameter in both the file
                            edge_colors[full_key]="Dark Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                                                
                    #mixed edge length
                    else : 
                        #edge first time visible (key is like 2_2)
                        if int(float(key.split('_')[0])) not in edge_length:
                            edge_length[int(float(key.split('_')[0]))]=length
                            
                            distance_from_start = length / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                            
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l *  normalized_vector[1]
                            
                            x0=x0-0.005
                            y0=y0-0.005
                            y1=y1-0.005
                            x1=x1-0.005
                            if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                edge_color="#E5C8AB"
                                edge_colors[full_key]="Light Orange"
                                edge_text_color.append("blue")
                            elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                edge_color="#D7C3E5"
                                edge_colors[full_key]="Light Purple"
                                edge_text_color.append("red")
                            elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                edge_color="#C8ACA1"
                                edge_colors[full_key]="Light Brown"
                                edge_text_color.append("red")
                            else:
                                edge_color="#aaaaaa"
                                edge_colors[full_key]="Light Grey"
                                edge_text_color.append("#939393")
                            edge_text.append(f'{key}_2')
                        else :
                            used_length = edge_length[int(float(key.split('_')[0]))]
                            edge_length[int(float(key.split('_')[0]))] = edge_length[int(float(key.split('_')[0]))]+length 
                            
                            distance_for_start = used_length /total_length
                            distance_from_start = (used_length+length) / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = (direction_vector[0] / l , direction_vector[1]/ l)
                            
                            xs=x0 + distance_for_start * normalized_vector[0]
                            ys=y0 + distance_for_start * normalized_vector[1]
                            
                            if((used_length+length)/total_length > 0.98) :
                                edge_x.extend([xs-0.005, x1-0.005, None])
                                edge_y.extend([ys-0.005, y1-0.005, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Dark Orange"
                                elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                    edge_color="#6A0DAD" 
                                    edge_colors[full_key]="Dark Purple"
                                elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                    edge_color="#6D412F"
                                    edge_colors[full_key]="Dark Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="Dark Grey" 
                            else : 
                                x1=x0 + distance_from_start * normalized_vector[0]
                                y1=y0 + distance_from_start * normalized_vector[1]
                                edge_x.extend([xs, x1, None])
                                edge_y.extend([ys, y1, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_3rdfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Stardard Orange"
                                elif int(key.split('_')[0]) in different_pipe_3rdfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                    edge_color="#6A0DAD" 
                                    edge_colors[full_key]="Standard Purple"
                                elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_3rdfile):
                                    edge_color="#6D412F"
                                    edge_colors[full_key]="Standard Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="standard Grey" 
            # Not parallel edge
            else:
                key = int(float(full_key.split('+')[0]))
                total_length = total_length_pipe_map.get(key)
                if(total_length == length) : 
                    # edge_x.extend([x0, x1, None])
                    # edge_y.extend([y0, y1, None])
                    if key in different_pipe_1stfile and key not in different_pipe_3rdfile:
                        edge_color="#FF8500"
                        edge_colors[full_key]="Dark Orange"
                        edge_text_color.append("blue")
                    elif key in different_pipe_3rdfile and key not in different_pipe_1stfile:
                        edge_color="#6A0DAD" 
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")
                    elif (key in different_pipe_1stfile) and (key in different_pipe_3rdfile):
                        edge_color="#6D412F"
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555"
                        edge_colors[full_key]="Dark Grey"
                        edge_text_color.append("#939393")

                    edge_text.append(f'{key}')
                #mixed diameter edge
                else : 
                    #edge first time visible
                    if key not in edge_length:
                        edge_length[key]=length
                        
                        distance_from_start = length / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        x1=x0 + distance_from_start *l * normalized_vector[0]
                        y1=y0 + distance_from_start *l * normalized_vector[1]
                        
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        if key in different_pipe_1stfile and key not in different_pipe_3rdfile:
                            edge_color="#E5C8AB"
                            edge_colors[full_key]="Light Orange"
                            edge_text_color.append("blue")
                        elif key in different_pipe_3rdfile and key not in different_pipe_1stfile:
                            edge_color="#D7C3E5"
                            edge_colors[full_key]="Light Purple"
                            edge_text_color.append("red")
                        elif (key in different_pipe_1stfile) and (key in different_pipe_3rdfile):
                            edge_color="#C8ACA1"
                            edge_colors[full_key]="Light Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#aaaaaa"
                            edge_colors[full_key]="Light Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                    else :
                        used_length = edge_length[key]
                        edge_length[key] = edge_length[key]+length 
                        
                        distance_for_start = used_length /total_length
                        distance_from_start = edge_length[key] / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        xs=x0 + distance_for_start * l * normalized_vector[0]
                        ys=y0 + distance_for_start * l * normalized_vector[1]
                        
                        if((used_length+length)/total_length > 0.98) :
                            x0=xs
                            y0=ys
                            if key in different_pipe_1stfile and key not in different_pipe_3rdfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Dark Orange"
                            elif key in different_pipe_3rdfile and key not in different_pipe_1stfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Dark Purple"
                            elif (key in different_pipe_1stfile) and (key in different_pipe_3rdfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Dark Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Dark Grey" 
                        else : 
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l * normalized_vector[1]
                            x0=xs
                            y0=ys
                            if key in different_pipe_1stfile and key not in different_pipe_3rdfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Standard Orange"
                            elif key in different_pipe_3rdfile and key not in different_pipe_1stfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Standard Purple"
                            elif (key in different_pipe_1stfile) and (key in different_pipe_3rdfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Standard Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Standard Grey" 
        
            logger.info(f"{full_key} color is the {edge_colors[full_key]}")
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=3, color=edge_color)
            )
            edge_traces.append(edge_trace)
        logger.info("Edge traces, edge text and edge color for the pipe graph has been created sucessfully for 2ndfile graph")

        return edge_traces, edge_text, edge_colors, edge_text_color
    
    def process_edges_for_diameter_graph_plotting_3rdfile(self,G, node_pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1stfile, different_pipe_2ndfile, exist_pipe_status_1stfile, exist_pipe_status_2ndfile):
        """Process edge data for Plotly visualization, including handling of parallel and multiple edges between the Nodes."""

        edge_x = []
        edge_y = []
        edge_text = []
        edge_length ={}
        edge_traces= []
        edge_colors= {}
        edge_text_color =[]
        
        # print("in latest fun : " + str(G.edges(keys=True)))

        # Iterate over all edges in the graph
        for u, v, full_key, data in G.edges(keys=True, data=True):
            
            length = data['length']
            # Get the positions of start and end nodes
            x0, y0 = node_pos[u]
            x1, y1 = node_pos[v]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # Offset for parallel edges to make them visually distinct
                # For simplicity, we're just offsetting by a small value, e.g., ±0.02
                #key is like 2_2+1 or 2_1+2 
                key = full_key.split('+')[0] #now key is like 2_2 or 2_1
                short_key = int(key.split('_')[0] )#now short_key is like 2
                # print("key" + key) 
                #this is cost=0 pipe
                if '_1' in key :
                    x0=x0+0.005
                    y0=y0+0.005
                    y1=y1+0.005
                    x1=x1+0.005
                    if not exist_pipe_status_1stfile.get(short_key, True) and exist_pipe_status_2ndfile.get(short_key, True):
                        edge_color="#FF8500" #orange -> diffrent length and diameter from the 5 min file
                        edge_colors[full_key]="Dark Orange"
                        edge_text_color.append("blue")
                    elif not exist_pipe_status_2ndfile.get(short_key, True) and exist_pipe_status_1stfile.get(short_key, True):
                        edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")   
                    elif (not exist_pipe_status_1stfile.get(short_key, True) and not exist_pipe_status_2ndfile.get(short_key, True)):
                        edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555" #grey -> same length and diameter in both the file
                        edge_colors[full_key]="Dark Grey"
                        edge_text_color.append("#939393")
                    edge_text.append(f'{key}')
                #if cost is not equal to zero and key contains the  '_2'
                else : 
                    total_length = total_length_pipe_map[int(float(key.split('_')[0]))]
                    
                    #if parrallel pipe length is equal to the total length (distance between the 2 node= length of the pipe)
                    if(total_length == length) : 
                        x0=x0-0.005
                        y0=y0-0.005
                        y1=y1-0.005
                        x1=x1-0.005
                        if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                            edge_color="#FF8500" 
                            #orange -> diffrent length and diameter from the 5 min file
                            edge_colors[full_key]="Dark Orange"
                            edge_text_color.append("blue")
                        elif int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                            edge_color="#6A0DAD" #purple -> diffrent length and diameter from the 1 hr file
                            edge_colors[full_key]="Dark Purple"
                            edge_text_color.append("red")
                        elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_2ndfile):
                            edge_color="#6D412F" #brown -> diffrent lengtha and diameter in both the file
                            edge_colors[full_key]="Dark Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#555555" #grey -> same length and diameter in both the file
                            edge_colors[full_key]="Dark Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                                                
                    #mixed edge length
                    else : 
                        #edge first time visible (key is like 2_2)
                        if int(float(key.split('_')[0])) not in edge_length:
                            edge_length[int(float(key.split('_')[0]))]=length
                            
                            distance_from_start = length / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                            
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l *  normalized_vector[1]
                            
                            x0=x0-0.005
                            y0=y0-0.005
                            y1=y1-0.005
                            x1=x1-0.005
                            if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                edge_color="#E5C8AB"
                                edge_colors[full_key]="Light Orange"
                                edge_text_color.append("blue")
                            elif int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                edge_color="#D7C3E5"
                                edge_colors[full_key]="Light Purple"
                                edge_text_color.append("red")
                            elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_2ndfile):
                                edge_color="#C8ACA1"
                                edge_colors[full_key]="Light Brown"
                                edge_text_color.append("red")
                            else:
                                edge_color="#aaaaaa"
                                edge_colors[full_key]="Light Grey"
                                edge_text_color.append("#939393")
                            edge_text.append(f'{key}_2')
                        else :
                            used_length = edge_length[int(float(key.split('_')[0]))]
                            edge_length[int(float(key.split('_')[0]))] = edge_length[int(float(key.split('_')[0]))]+length 
                            
                            distance_for_start = used_length /total_length
                            distance_from_start = (used_length+length) / total_length
                            
                            direction_vector = (x1 -x0, y1-y0)
                            
                            #claculate length of the direction vector
                            l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                            normalized_vector = (direction_vector[0] / l , direction_vector[1]/ l)
                            
                            xs=x0 + distance_for_start * normalized_vector[0]
                            ys=y0 + distance_for_start * normalized_vector[1]
                            
                            if((used_length+length)/total_length > 0.98) :
                                edge_x.extend([xs-0.005, x1-0.005, None])
                                edge_y.extend([ys-0.005, y1-0.005, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Dark Orange"
                                elif int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                    edge_color="#6A0DAD" 
                                    edge_colors[full_key]="Dark Purple"
                                elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_2ndfile):
                                    edge_color="#6D412F"
                                    edge_colors[full_key]="Dark Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="Dark Grey" 
                            else : 
                                x1=x0 + distance_from_start * normalized_vector[0]
                                y1=y0 + distance_from_start * normalized_vector[1]
                                edge_x.extend([xs, x1, None])
                                edge_y.extend([ys, y1, None])
                                x0=xs-0.005
                                y0=ys-0.005
                                y1=y1-0.005
                                x1=x1-0.005
                                if int(key.split('_')[0]) in different_pipe_1stfile and int(key.split('_')[0]) not in different_pipe_2ndfile:
                                    edge_color="#FF8500"
                                    edge_colors[full_key]="Standard Orange"
                                elif int(key.split('_')[0]) in different_pipe_2ndfile and int(key.split('_')[0]) not in different_pipe_1stfile:
                                    edge_color="#6A0DAD" 
                                    edge_colors[full_key]="Standard Purple"
                                elif (int(key.split('_')[0]) in different_pipe_1stfile) and (int(key.split('_')[0]) in different_pipe_2ndfile):
                                    edge_color="#6D412F"
                                    edge_colors[full_key]="Standard Brown"
                                else:
                                    edge_color="#555555"
                                    edge_colors[full_key]="Standard Grey" 
            # Not parallel edge
            else:
                key = int(float(full_key.split('+')[0]))
                total_length = total_length_pipe_map.get(key)
                if(total_length == length) : 
                    # edge_x.extend([x0, x1, None])
                    # edge_y.extend([y0, y1, None])
                    if key in different_pipe_1stfile and key not in different_pipe_2ndfile:
                        edge_color="#FF8500"
                        edge_colors[full_key]="Dark Orange"
                        edge_text_color.append("blue")
                    elif key in different_pipe_2ndfile and key not in different_pipe_1stfile:
                        edge_color="#6A0DAD" 
                        edge_colors[full_key]="Dark Purple"
                        edge_text_color.append("red")
                    elif (key in different_pipe_1stfile) and (key in different_pipe_2ndfile):
                        edge_color="#6D412F"
                        edge_colors[full_key]="Dark Brown"
                        edge_text_color.append("red")
                    else:
                        edge_color="#555555"
                        edge_colors[full_key]="Dark Grey"
                        edge_text_color.append("#939393") 
                    edge_text.append(f'{key}')
                #mixed diameter edge
                else : 
                    #edge first time visible
                    
                    if key not in edge_length:
                        edge_length[key]=length
                        
                        distance_from_start = length / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        x1=x0 + distance_from_start *l * normalized_vector[0]
                        y1=y0 + distance_from_start *l * normalized_vector[1]
                        
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        if key in different_pipe_1stfile and key not in different_pipe_2ndfile:
                            edge_color="#E5C8AB"
                            edge_colors[full_key]="Light Orange"
                            edge_text_color.append("blue")
                        elif key in different_pipe_2ndfile and key not in different_pipe_1stfile:
                            edge_color="#D7C3E5"
                            edge_colors[full_key]="Light Purple"
                            edge_text_color.append("red")
                        elif (key in different_pipe_1stfile) and (key in different_pipe_2ndfile):
                            edge_color="#C8ACA1"
                            edge_colors[full_key]="Light Brown"
                            edge_text_color.append("red")
                        else:
                            edge_color="#aaaaaa"
                            edge_colors[full_key]="Light Grey"
                            edge_text_color.append("#939393")
                        edge_text.append(f'{key}')
                    else :
                        used_length = edge_length[key]
                        edge_length[key] = edge_length[key]+length 
                        
                        distance_for_start = used_length /total_length
                        distance_from_start = edge_length[key] / total_length
                        
                        direction_vector = (x1 -x0, y1-y0)
                        
                        #claculate length of the direction vector
                        l = math.sqrt(direction_vector[0] ** 2 + direction_vector[1]**2)
                        normalized_vector = ( direction_vector[0] / l , direction_vector[1]/ l)
                        
                        xs=x0 + distance_for_start * l * normalized_vector[0]
                        ys=y0 + distance_for_start * l * normalized_vector[1]
                        
                        if((used_length+length)/total_length > 0.98) :
                            x0=xs
                            y0=ys
                            if key in different_pipe_1stfile and key not in different_pipe_2ndfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Dark Orange"
                            elif key in different_pipe_2ndfile and key not in different_pipe_1stfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Dark Purple"
                            elif (key in different_pipe_1stfile) and (key in different_pipe_2ndfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Dark Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Dark Grey" 
                        else : 
                            x1=x0 + distance_from_start * l * normalized_vector[0]
                            y1=y0 + distance_from_start * l * normalized_vector[1]
                            x0=xs
                            y0=ys
                            if key in different_pipe_1stfile and key not in different_pipe_2ndfile:
                                edge_color="#FF8500"
                                edge_colors[full_key]="Standard Orange"
                            elif key in different_pipe_2ndfile and key not in different_pipe_1stfile:
                                edge_color="#6A0DAD"
                                edge_colors[full_key]="Standard Purple"
                            elif (key in different_pipe_1stfile) and (key in different_pipe_2ndfile):
                                edge_color="#6D412F"
                                edge_colors[full_key]="Standard Brown"
                            else:
                                edge_color="#555555"
                                edge_colors[full_key]="Standard Grey" 
        
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=3, color=edge_color)
            )
            edge_traces.append(edge_trace)
            logger.info(f"{full_key} color is the {edge_colors[full_key]}")
        
        logger.info("Edge traces, edge text and edge color has been cretaed sucessfully for the 3rdfile pipe graph")

        return edge_traces, edge_text, edge_colors, edge_text_color
    
    
    
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
                    offset = 0.02  # First parallel edge offset
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
                    offset = -0.02  # Second parallel edge offset
                    
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
                                                          pipeData2ndfile, pipeData3rdfile, different_pipe_2ndfile, different_pipe_3rdfile, 
                                                          exist_pipe_status_2ndfile, exist_pipe_status_3rdfile,
                                                          id_to_cost_map_1stfile, id_to_cost_map_2ndfile, id_to_cost_map_3rdfile, 
                                                          sorted_difference_cost_pipeid_2ndfile,sorted_difference_cost_pipeid_3rdfile) :
        edge_hovertext_map = {}

        # Iterate over all edges in the graph
        for u, v, key, data in G.edges(keys=True, data=True):
            length = data['length']
            diameter = data.get('diameter', None)
            cost = data.get('cost', None)
            flow = data.get('flow', None)
            speed = data.get('speed', None)
            full_pipe_id = key.split('+')[0] # e.g. 1_2 or 2_1 from 1_2+1 or 2_1+2
            pipe_id = int(full_pipe_id.split('_')[0])  # Extract the pipe ID from the key
            hover_info = ""

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # if the edge is parallel, and cost is zero
                if '_1' in key:

                    if(exist_pipe_status_2ndfile.get(pipe_id, True) and exist_pipe_status_3rdfile.get(pipe_id, True)) :
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} <br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,}")

                    elif(not exist_pipe_status_2ndfile.get(pipe_id, True) and exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 1st File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m <br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):} m <br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br>"
                                    f"&nbsp; &nbsp; Total cost in 1st File : 0 <br>")

                        for i in range(len(pipeData2ndfile["pipeID"])) :
                            if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 2nd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,} m/s<br>"
                                                f"&nbsp; &nbsp; Total Cost in 2nd File : 0 <br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%)<br>")

                    elif(exist_pipe_status_2ndfile.get(pipe_id, True) and not exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 1st File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br>"
                                    f"&nbsp; &nbsp; Total cost in 1st File : 0 <br>")
                        
                        for i in range(len(pipeData3rdfile["pipeID"])) :
                            if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 3rd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,}m/s <br>"
                                                f"&nbsp; &nbsp; Total Cost in 3rd File : 0 <br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%)<br>")

                    if(not exist_pipe_status_2ndfile.get(pipe_id, True) and not exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 1st File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br>"
                                    f"&nbsp; &nbsp; Total Cost in 1st File : 0 <br>")

                        for i in range(len(pipeData2ndfile["pipeID"])) :
                            if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 2nd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; Total Cost in 2nd File : 0 <br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 <br>")

                        for i in range(len(pipeData3rdfile["pipeID"])) :
                            if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 3rd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,}  <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,} m<br>")
                        hover_info += ( f"&nbsp; &nbsp; Total Cost in 3rd File : 0 <br>"
                                        f"&nbsp; Cost Difference : 0(0%)<br>")

                    edge_hovertext_map[full_pipe_id]=hover_info
                # if the edge is parallel, and cost is not zero
                elif '_2' in key :
                    #if the edge is parallel and cost is not zero, and full_pipe_id is first time arrived means that parrallel pipe contains the many diffrent diameter pipes
                    if full_pipe_id not in edge_hovertext_map : 
                        #pipe_id is in the 
                        if pipe_id in different_pipe_2ndfile or pipe_id in different_pipe_3rdfile :
                            hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp;1st File: <br>"  
                                           f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,}<br> m/s<br>")
                        else :
                            hover_info += (f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                    else : 
                        hover_info = edge_hovertext_map[full_pipe_id] + (
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s <br> <br>")

            #edge is not parallel
            else:
                if full_pipe_id not in edge_hovertext_map : 
                    if pipe_id in different_pipe_2ndfile or pipe_id in different_pipe_3rdfile :
                        hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; 1st File: <br>"  
                                        f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                    else :
                        hover_info += (f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s <br> <br>")
                else : 
                    hover_info = edge_hovertext_map[full_pipe_id] + (
                                    f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
            edge_hovertext_map[full_pipe_id]=hover_info
        
        #for the total cost of the pipe in the 1st file
        for full_pipe_id in edge_hovertext_map :
            if "_1" not in full_pipe_id:
                pipe_id = int(full_pipe_id.split('_')[0])
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost in 1st File : {round(id_to_cost_map_1stfile.get(pipe_id, 0),2):,} <br>" )

        #prepare hover info for the diffrent edge
        for full_pipe_id in edge_hovertext_map :
            pipe_id = int(full_pipe_id.split('_')[0])
            #if the pipe_id is in the 5 min file and cost is zero to handle the parrallel pipes
            if(pipe_id in different_pipe_2ndfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 2nd File: <br>" )
                for i in range(len(pipeData2ndfile["pipeID"])) :
                    if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] != 0:
                        total_cost += pipeData2ndfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} m<br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} m<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} ltr/s<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,} m/s<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost in 2nd File : {round(total_cost,2):,} <br>" 
                                                     f"&nbsp; &nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id],id_to_cost_map_1stfile.get(pipe_id,0))})<br><br>")
                
            if(pipe_id in different_pipe_3rdfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 3rd File: <br>" )
                for i in range(len(pipeData3rdfile["pipeID"])) :
                    if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] != 0:
                        total_cost += pipeData3rdfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,} m/s<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost in 3rd File : {round(total_cost,2):,} <br>" )
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_3rdfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id],id_to_cost_map_1stfile.get(pipe_id, 0))})<br><br>")

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
            
            # print("Hover : " + pipe_id)
        print("Hovertext of Pipe 6 : " + str(hovertext[6]))
        
        logger.info("Edge Hovertext has been created sucessfully for 1stfile graph")
        
        return hovertext
    
    
    def process_edge_hovertext_for_diameter_graph_2ndfile(self, G, node_pos, unique_parallel_pipes, edge_colors,pipeData1stfile, 
                                                          pipeData3rdfile, different_pipe_1stfile, different_pipe_3rdfile, 
                                                          exist_pipe_status_1stfile, exist_pipe_status_3rdfile,
                                                          id_to_cost_map_1stfile, id_to_cost_map_3rdfile, id_to_cost_map_2ndfile, 
                                                          sorted_difference_cost_pipeid_1stfile, sorted_difference_cost_pipeid_3rdfile) :
        edge_hovertext_map = {}
        
        logger.info(f"Different Pipe 1stfile : {different_pipe_1stfile}")
        logger.info(f"Different Pipe 3rdfile : {different_pipe_3rdfile}")

        # Iterate over all edges in the graph
        for u, v, key, data in G.edges(keys=True, data=True):
            length = data['length']
            diameter = data.get('diameter', None)
            cost = data.get('cost', None)
            flow = data.get('flow', None)
            speed = data.get('speed', None)
            full_pipe_id = key.split('+')[0] # e.g. 1_2 or 2_1 from 1_2+1 or 2_1+2
            pipe_id = int(full_pipe_id.split('_')[0])  # Extract the pipe ID from the key
            hover_info = ""
        

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # if the edge is parallel, and cost is zero
                if '_1' in key:
                    
                    #if the static parrallel edge data is same in both the file
                    if(exist_pipe_status_1stfile.get(pipe_id, True) and exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 2nd File : 0 <br>")
                    
                    #if static parallel edge data is not same in the 1st File file
                    if(not exist_pipe_status_1stfile.get(pipe_id, True) and exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 2nd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 2nd File : 0 <br>")
                        
                        for i in range(len(pipeData1stfile["pipeID"])) :
                            if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 1st File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 1st File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%)<br>")

                    if(not exist_pipe_status_3rdfile.get(pipe_id, True) and exist_pipe_status_1stfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 2nd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br>"
                                    f"&nbsp; &nbsp; Total cost in 2nd File : 0 <br><br>")
                        
                        for i in range(len(pipeData3rdfile["pipeID"])) :
                            if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 3rd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,} m/s<br>"
                                                f"&nbsp; &nbsp; Total Cost in 3rd File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%) <br>")

                    if(not exist_pipe_status_1stfile.get(pipe_id, True) and not exist_pipe_status_3rdfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 2nd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 2nd File : 0 <br><br>")
                        
                        for i in range(len(pipeData1stfile["pipeID"])) :
                            if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 1st File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>")
                        hover_info += ( f"&nbsp; &nbsp; Total Cost in 1st File : 0 <br><br>")
                        hover_info += ( f"&nbsp; &nbsp; Cost Difference : 0 (0%)<br><br>")

                        for i in range(len(pipeData3rdfile["pipeID"])) :
                            if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 3rd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 3rd File : 0 <br><br>")
                        hover_info += ( f"&nbsp; &nbsp; Cost Difference : 0 (0%)<br>")
                    
                    edge_hovertext_map[full_pipe_id]=hover_info
                # if the edge is parallel, and cost is not zero
                elif '_2' in key :
                    #if the edge is parallel and cost is not zero, and full_pipe_id is first time arrived means that parrallel pipe contains the many diffrent diameter pipes
                    if full_pipe_id not in edge_hovertext_map : 
                        #pipe_id is in the 
                        if pipe_id in different_pipe_1stfile or pipe_id in different_pipe_3rdfile :
                            hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp; 2nd File: <br>"  
                                           f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                        else :
                            hover_info = (f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                    else : 
                        hover_info += edge_hovertext_map[full_pipe_id] + (
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")

            #edge is not parallel
            else:
                if full_pipe_id not in edge_hovertext_map : 
                    logger.info(f"Full Pipe ID : {full_pipe_id} not in edge_hovertext_map")
                    pipe_id = int(full_pipe_id.split('_')[0])
                    if pipe_id in different_pipe_1stfile or pipe_id in different_pipe_3rdfile :
                        hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; 2nd File: <br>"  
                                        f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                    else :
                        hover_info = (f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                else : 
                    hover_info = edge_hovertext_map[full_pipe_id] + (
                                    f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
            edge_hovertext_map[full_pipe_id]=hover_info
            
        for full_pipe_id in edge_hovertext_map :
            if "_1" not in full_pipe_id:
                pipe_id = int(full_pipe_id.split('_')[0])
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost in 2nd File : {round(id_to_cost_map_2ndfile.get(pipe_id, 0),2):,} <br><br>" )

        #prepare hover info for the diffrent edge
        for full_pipe_id in edge_hovertext_map :
            pipe_id = int(full_pipe_id.split('_')[0])
            #if the pipe_id is in the 5 min file and cost is zero to handle the parrallel pipes
            if(pipe_id in different_pipe_1stfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 1st File: <br>" )
                for i in range(len(pipeData1stfile["pipeID"])) :
                    if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] != 0:
                        total_cost += pipeData1stfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost : {round(total_cost,2):,} <br><br>"
                                                     f"&nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_1stfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id],id_to_cost_map_2ndfile.get(pipe_id, 0))})<br><br>")
            if(pipe_id in different_pipe_3rdfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 3rd File: <br>" )
                for i in range(len(pipeData3rdfile["pipeID"])) :
                    if pipeData3rdfile["pipeID"][i] == pipe_id and pipeData3rdfile["cost"][i] != 0:
                        total_cost += pipeData3rdfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData3rdfile['diameter'][i],2):,} m<br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData3rdfile['length'][i],2):,} m<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData3rdfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData3rdfile['flow'][i],2):,} ltr/s<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData3rdfile['speed'][i],2):,} m/s<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost : {round(total_cost,2):,} <br><br>"
                                                     f"&nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_3rdfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id],id_to_cost_map_1stfile.get(pipe_id, 0))})<br><br>" )

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
            
            # print("Hover : " + pipe_id)
        
        logger.info("Edge Hovertext has been created sucessfully for 2ndfile graph")
        
        return hovertext
    
    def process_edge_hovertext_for_diameter_graph_3rdfile(self, G, node_pos, unique_parallel_pipes, edge_colors,pipeData1stfile, 
                                                          pipeData2ndfile, different_pipe_1stfile, different_pipe_2ndfile, 
                                                          exist_pipe_status_1stfile, exist_pipe_status_2ndfile,
                                                          id_to_cost_map_1stfile, id_to_cost_map_2ndfile, id_to_cost_map_3rdfile,
                                                          sorted_difference_cost_pipeid_1stfile, sorted_difference_cost_pipeid_2ndfile) :
        edge_hovertext_map = {}

        # Iterate over all edges in the graph
        for u, v, key, data in G.edges(keys=True, data=True):
            length = data['length']
            diameter = data.get('diameter', None)
            cost = data.get('cost', None)
            flow = data.get('flow', None)
            speed = data.get('speed', None)
            full_pipe_id = key.split('+')[0] # e.g. 1_2 or 2_1 from 1_2+1 or 2_1+2
            pipe_id = int(full_pipe_id.split('_')[0])  # Extract the pipe ID from the key
            hover_info = ""

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                # if the edge is parallel, and cost is zero
                if '_1' in key:
                    #if the static parrallel edge data is same in both the file
                    if(exist_pipe_status_1stfile.get(pipe_id, True) and exist_pipe_status_2ndfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 3rd File : 0 <br>")
                    
                    #if static parallel edge data is not same in the 1st File file
                    if(not exist_pipe_status_1stfile.get(pipe_id, True) and exist_pipe_status_2ndfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 3rd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} ms/<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 3rd File : 0 <br> <br>")
                        
                        for i in range(len(pipeData1stfile["pipeID"])) :
                            if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 1st File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 1st File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%)<br><br>")

                    if(not exist_pipe_status_2ndfile.get(pipe_id, True) and exist_pipe_status_1stfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 3rd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 3rd File : 0 <br><br>")
                        
                        for i in range(len(pipeData2ndfile["pipeID"])) :
                            if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 2nd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 2nd File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%)<br><br>")

                    if(not exist_pipe_status_1stfile.get(pipe_id, True) and not exist_pipe_status_2ndfile.get(pipe_id, True)):
                        hover_info += ( f"Pipe ID : {full_pipe_id} <br>"
                                    f"Start Node : {u} <br>"
                                    f"End Node : {v} <br>"  
                                    f"&nbsp; &nbsp; 3rd File: <br>"
                                    f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br><br>"
                                    f"&nbsp; &nbsp; Total cost in 3rd File : 0 <br><br>")

                        for i in range(len(pipeData1stfile["pipeID"])) :
                            if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 1st File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 1st File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference : 0 (0%) <br>")

                        for i in range(len(pipeData2ndfile["pipeID"])) :
                            if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] == 0:
                                hover_info += ( f"&nbsp; &nbsp; 2nd File: <br>"    
                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} m<br>" 
                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} m<br>"
                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} ltr/s<br>"
                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,} m/s<br><br>"
                                                f"&nbsp; &nbsp; Total Cost in 2nd File : 0 <br><br>")
                        hover_info += ( f"&nbsp; Cost Difference: 0 (0%)<br>")

                    edge_hovertext_map[full_pipe_id]=hover_info
                # if the edge is parallel, and cost is not zero
                elif '_2' in key :
                    #if the edge is parallel and cost is not zero, and full_pipe_id is first time arrived means that parrallel pipe contains the many diffrent diameter pipes
                    if full_pipe_id not in edge_hovertext_map : 
                        #pipe_id is in the 
                        if pipe_id in different_pipe_1stfile or pipe_id in different_pipe_2ndfile :
                            hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp; 3rd File : <br>"  
                                           f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s <br> <br>")
                            #if pipe is same in both the file
                        else :
                            hover_info += (f"Pipe ID : {full_pipe_id} <br>"
                                           f"Start Node : {u} <br>"
                                           f"End Node : {v} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                           f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                           f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                           f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                    else : 
                        hover_info = edge_hovertext_map[full_pipe_id] + (
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s <br> <br>")

                #edge is not parallel
            else:
                #if edge encounter for the first time
                if full_pipe_id not in edge_hovertext_map : 
                    if pipe_id in different_pipe_1stfile or pipe_id in different_pipe_2ndfile :
                        hover_info = ( f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; 3rd File: <br>"  
                                        f"&nbsp; &nbsp; &nbsp; Color :{edge_colors[key]} <br>"    
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>" 
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s <br> <br>")
                    else :
                        hover_info = (f"Pipe ID : {full_pipe_id} <br>"
                                        f"Start Node : {u} <br>"
                                        f"End Node : {v} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                        f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                        f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                        f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,} m/s<br> <br>")
                else : 
                    hover_info = edge_hovertext_map[full_pipe_id] + (
                                    f"&nbsp; &nbsp; &nbsp; Color : {edge_colors[key]} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Diameter : {round(diameter,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Length : {round(length,2):,} m<br>"
                                    f"&nbsp; &nbsp; &nbsp; Cost : {round(cost,2):,} <br>"
                                    f"&nbsp; &nbsp; &nbsp; Flow : {round(flow,2):,} ltr/s<br>"
                                    f"&nbsp; &nbsp; &nbsp; Speed : {round(speed,2):,}m/s<br> ")
            edge_hovertext_map[full_pipe_id]=hover_info
        
        for full_pipe_id in edge_hovertext_map :
            if "_1" not in full_pipe_id:
                pipe_id = int(full_pipe_id.split('_')[0])
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost in 3rd File : {round(id_to_cost_map_3rdfile.get(pipe_id, 0),2):,} <br><br>" )


        #prepare hover info for the diffrent edge
        for full_pipe_id in edge_hovertext_map :
            pipe_id = int(full_pipe_id.split('_')[0])
            #if the pipe_id is in the 3rdfile file and cost is not zero to handle the parrallel pipes
            if(pipe_id in different_pipe_1stfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 1st File: <br>" )
                for i in range(len(pipeData1stfile["pipeID"])) :
                    if pipeData1stfile["pipeID"][i] == pipe_id and pipeData1stfile["cost"][i] != 0:
                        total_cost += pipeData1stfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData1stfile['diameter'][i],2):,} m<br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData1stfile['length'][i],2):,} m<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData1stfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData1stfile['flow'][i],2):,} ltr/s<br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData1stfile['speed'][i],2):,} m/s<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost : {round(total_cost,2):,} <br><br>"
                                                     f"&nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_1stfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id],id_to_cost_map_3rdfile.get(pipe_id, 0))})<br><br>")
            if(pipe_id in different_pipe_2ndfile and "_1" not in full_pipe_id):
                total_cost = 0
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; 2nd File: <br>" )
                for i in range(len(pipeData2ndfile["pipeID"])) :
                    if pipeData2ndfile["pipeID"][i] == pipe_id and pipeData2ndfile["cost"][i] != 0:
                        total_cost += pipeData2ndfile["cost"][i]
                        edge_hovertext_map[full_pipe_id] += (   
                                                                f"&nbsp; &nbsp; &nbsp; Diameter : {round(pipeData2ndfile['diameter'][i],2):,} <br>" 
                                                                f"&nbsp; &nbsp; &nbsp; Length : {round(pipeData2ndfile['length'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Cost : {round(pipeData2ndfile['cost'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Flow : {round(pipeData2ndfile['flow'][i],2):,} <br>"
                                                                f"&nbsp; &nbsp; &nbsp; Speed : {round(pipeData2ndfile['speed'][i],2):,}<br><br>")
                edge_hovertext_map[full_pipe_id] += ( f"&nbsp; &nbsp; Total Cost : {round(total_cost,2):,} <br><br>"
                                                     f"&nbsp; Cost Difference : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id],2):,} ({self.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id],id_to_cost_map_1stfile.get(pipe_id, 0))})<br><br>")
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
        
        logger.info("Edge Hovertext has been created sucessfully for 3rdfile graph")
        return hovertext
    
    
    def process_edge_hovertext_for_speed_graph(self, G, node_pos, unique_parallel_pipes, edge_colors) :
        edge_hovertext_map = {}

        # Iterate over all edges in the graph
        for u, v, key, data in G.edges(keys=True, data=True):
            diameter = data['diameter']
            speed = data.get('speed', None)
            pipe_id = key.split('+')[0]

            # Check if the edge is a parallel edge
            if (u, v) in unique_parallel_pipes or (v, u) in unique_parallel_pipes:
                if '_1' in key:
                    hover_info = f"Pipe ID : {pipe_id} <br>Start Node : {u} <br>End Node : {v} <br>  Color :{edge_colors[key]} <br>    Diameter : {diameter} <br>    Speed : {speed}"
                elif '_2' in key :
                    if pipe_id not in edge_hovertext_map : 
                        hover_info = f"Pipe ID : {pipe_id} <br>Start Node : {u} <br>End Node : {v} <br>  Color : {edge_colors[key]} <br>    Diameter : {diameter} <br>    Speed : {speed}"
                    else : 
                        hover_info = edge_hovertext_map[pipe_id] + f"<br>  Color : {edge_colors[key]} <br>    Diameter : {diameter} <br>    Speed : {speed}"
            else:
                if pipe_id not in edge_hovertext_map : 
                    hover_info = f"Pipe ID : {pipe_id} <br>Start Node : {u} <br>End Node : {v} <br>  Color : {edge_colors[key]} <br>    Diameter : {diameter} <br>    Speed : {speed}"
                else : 
                    hover_info = edge_hovertext_map[pipe_id] + f"<br>  Color : {edge_colors[key]} <br>    Diameter : {diameter} <br>    Speed : {speed}"

            edge_hovertext_map[pipe_id]=hover_info
        
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
            
            # print("Hover : " + pipe_id)
        
        return hovertext

    
        
    def process_main_network_pipedata(self,mainnode, mainpipe) : 
        total_length_map ={}
        elevation_map ={}
        for i in range(len(mainpipe["length"])):
            total_length_map[mainpipe["pipeID"][i]] = mainpipe["length"][i]
        
        for i in range(len(mainnode["Elevation"])):
            elevation_map[mainnode["nodeID"][i]] = mainnode["Elevation"][i]

        return total_length_map,elevation_map
    
            

    
    