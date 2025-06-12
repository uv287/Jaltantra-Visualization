import networkx as nx
import plotly.graph_objs as go
from output_data_processor import OutputDataProcessor
from collections import defaultdict
from logger_config import logger

class FigureGenerator:
    
    def extract_node_positions(self,fig):
        """
        Extracts node positions from a given Plotly figure.

        Parameters:
        fig (plotly.graph_objs.Figure): The Plotly figure object containing graph traces.

        Returns:
        List: A List of node positions, where values are tuples representing the (x, y) coordinates of each node.
        """
        node_positions = {}
        fig = go.Figure(fig)

        # Iterate over the traces in fig to extract node positions
        for trace in fig.data:
            # Assuming nodes have markers and labels, and their mode is 'markers+text' or 'markers'
            if 'markers' in trace.mode:
                node_texts = trace['text']
                for i in range(len(node_texts)):
                    node_positions[float(node_texts[i].split(": ")[1])] = (trace['x'][i], trace['y'][i])
        
        logger.info(f"Extracted node positions: {node_positions}")

        return node_positions
    
    
    #create mutiligraph toa llow multiple edges between the nodes
    def create_graph_with_parallel_edges(self, node_positions, pipe_data , unique_parallel_pipes):
    # Create a MultiGraph to allow multiple edges between nodes
        G = nx.MultiGraph()
        
        logger.info(f"Creating graph with node positions: {node_positions} and pipe data: {pipe_data}")

        # Add nodes to the graph with positions
        for node, position in node_positions.items():

            G.add_node(node, pos=position)
            
        visitedEdges=[]
        
        # Add edges from pipe_data
        for i in range(len(pipe_data["pipeID"])):
            pipe_id = pipe_data["pipeID"][i]
            start_node = pipe_data["startNode"][i]
            end_node = pipe_data["endNode"][i]
            
            pipe_tuple=(start_node,end_node)
            
            if pipe_id not in visitedEdges:
                
                visitedEdges.append(pipe_id)
                # Add edge (add multiple if it's parallel)
                if pipe_tuple in unique_parallel_pipes:
                    # Add two parallel edges (represented with unique keys)
                    G.add_edge(start_node, end_node, key=f'{pipe_id}_1')
                    G.add_edge(start_node, end_node, key=f'{pipe_id}_2')
                else:
                    # Add a single edge
                    G.add_edge(start_node, end_node, key=f'{pipe_id}')
        
        logger.info(f"Created graph with edges: {G.edges()}")
        return G
    
    def create_graph_with_parallel_and_mutliple_edges(self, node_positions, pipe_data , unique_parallel_pipes):
    # Create a MultiGraph to allow multiple edges between nodes
        G = nx.MultiGraph()
        edge_count={}
        # Add nodes to the graph with positions
        for node, position in node_positions.items():
            G.add_node(node, pos=position)
            
        no_of_pipes={}
        
        # print(pipe_data)
        
        # Add edges from pipe_data
        logger.info("Adding edges to the graph with parallel and multiple edges with relavant data")
        for i in range(len(pipe_data["pipeID"])):
            pipe_id = pipe_data["pipeID"][i]
            start_node = pipe_data["startNode"][i]
            end_node = pipe_data["endNode"][i]
            cost = pipe_data["cost"][i]
            length =pipe_data["length"][i]
            diameter = pipe_data["diameter"][i]
            flow = pipe_data["flow"][i]
            speed =pipe_data["speed"][i]
            
            pipe_tuple=(start_node,end_node)
            # Add edge (add multiple if it's parallel)
            if pipe_tuple in unique_parallel_pipes:
                # Add two parallel edges (represented with unique keys)
                if cost == 0 :
                    G.add_edge(start_node, end_node, key=f'{pipe_id}_1+1', length = length, diameter= diameter, cost=cost, flow=flow, speed=speed)
                    no_of_pipes[pipe_id]=1
                else :
                    if pipe_id not in no_of_pipes:
                        no_of_pipes[pipe_id]=1
                    else:
                        no_of_pipes[pipe_id]=no_of_pipes[pipe_id]+1
                    G.add_edge(start_node, end_node, key=f'{pipe_id}_2+{no_of_pipes[pipe_id]}', length = length, diameter = diameter, cost=cost, flow=flow, speed=speed)
                    # print(diameter)
            else:
                # Add a single edge
                if pipe_id not in no_of_pipes:
                    no_of_pipes[pipe_id]=1
                    G.add_edge(start_node, end_node, key=f'{pipe_id}+1', length = length, diameter =diameter, cost=cost, flow=flow, speed=speed)
                    # print(diameter)
                else:
                    no_of_pipes[pipe_id]=no_of_pipes[pipe_id]+1
                    G.add_edge(start_node, end_node, key=f'{pipe_id}+{no_of_pipes[pipe_id]}', length = length, diameter= diameter, cost=cost, flow=flow, speed=speed)
                    # print(diameter)
            
            # print(f"[{start_node} , {end_node}] ,", end= "")
        # print("")
        # print("multipipe edges " + str(G.edges()))
        logger.info(f"No of pipes added to the graph: {no_of_pipes}")
        logger.info("Multiple same pipe id edges added successfully")
        return G, no_of_pipes
    
    def create_node_1min_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr, G, start) :
        node_demand_map = {}    
        node_demand_1hr={}
        node_demand_5min={}
        data_processor = OutputDataProcessor()
        diffrent_5min = []
        diffrent_1hr = []
        demand_difference_5min = {}
        demand_difference_1hr = {}
        sorted_demand_difference_5min = {}
        sorted_demand_difference_1hr = {}
        para_1mintab_5min= ""
        para_1mintab_1hr= ""
        para_5mintab_1min=""
        para_1hrtab_1min=""
        node_head_map = {}    
        node_head_1hr={}
        node_head_5min={}
        head_difference_5min = {}
        head_difference_1hr = {}
        sorted_head_difference_5min = {}
        sorted_head_difference_1hr = {}
        
        # Create the map for 1minnode_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
        
        logger.info(f"1min Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = 'blue'
            G.nodes[node]['size'] = 30  # Default size for all nodes
        
        
        if nodeData5min is not None:
            # Create the map for 5minNodeData
            
            for i in range(len(nodeData5min["nodeID"])):
                node_id = nodeData5min["nodeID"][i]
                demand = nodeData5min["Demand"][i]
                head = nodeData5min["Head"][i]
                node_demand_5min[node_id] = demand
                node_head_5min[node_id] = head
            
            logger.info("5 minutes Result File Head Map : "+ str(node_head_5min))
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_5min[node])) or (float(node_head_map[node]) != float(node_head_5min[node])):
                    diffrent_5min.append(node)
                    demand_difference_5min[node]=(float(node_demand_map[node]) - float(node_demand_5min[node]))
                    head_difference_5min[node]=(float(node_head_map[node]) - float(node_head_5min[node]))
            
            logger.info("Diffrent Node ID in 5min output file compare to the 1min output file : "+ str(diffrent_5min))
            
            #reverse sort the list with the node
            sorted_head_difference_5min = dict(sorted(head_difference_5min.items(), key=lambda item: item[1], reverse=True))
            
            #traverse the sorted list and create the list 
            for node in sorted_head_difference_5min:
                para_1mintab_5min +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp; <b>Difference : {round(sorted_head_difference_5min[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node]- node_demand_5min[node],3)}</b><br><br><br>"
                                    )
            
            logger.info("Paragraph for 1min tab with 5min data is stored")
            #sort the list with the node
            sorted_head_difference_5min = dict(sorted(head_difference_5min.items(), key=lambda item: item[1], reverse=False))
            
            for node in sorted_head_difference_5min:                        
                para_5mintab_1min +=(f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_5min[node]-node_head_map[node],3)}</b><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_5min[node]-node_demand_map[node],3)}</b><br><br><br>")

            logger.info("Paragraph for 5min tab with 1min data is stored")
            
            for node in G.nodes():
                if node in diffrent_5min:
                    G.nodes[node]['color'] = 'red'  # diffrent demand or head then 5min -> Red
                    G.nodes[node]['size'] = 45
                
        # Create the map for 1hrNodeData
        if nodeData1hr is not None:
            for i in range(len(nodeData1hr["nodeID"])):
                node_id = nodeData1hr["nodeID"][i]
                demand = nodeData1hr["Demand"][i]
                head = nodeData1hr["Head"][i]
                node_demand_1hr[node_id] = demand
                node_head_1hr[node_id] = head
            
            logger.info("1 hour Result File Head Map : "+ str(node_head_1hr))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1hr[node])) or (float(node_head_map[node]) != float(node_head_1hr[node])):
                    diffrent_1hr.append(node)
                    demand_difference_1hr[node]=(float(node_demand_map[node]) - float(node_demand_1hr[node]))
                    head_difference_1hr[node]=(float(node_head_map[node]) - float(node_head_1hr[node]))
            
            logger.info("Diffrent Node ID in 1hr output file compare to the 1min output file : "+ str(diffrent_1hr))
                    
            #sort the list with the node 
            sorted_head_difference_1hr = dict(sorted(demand_difference_1hr.items(), key=lambda item: item[1], reverse=True))
            for node in sorted_demand_difference_1hr:
                para_1mintab_1hr += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1hr[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1hr : {round(node_demand_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_demand_difference_1hr[node],3)}</b><br><br><br>"
                                    )
            
            logger.info("Paragraph for 1min tab with 1hr data is stored")
            
            sorted_head_difference_1hr = dict(sorted(demand_difference_1hr.items(), key=lambda item: item[1], reverse=False))
                
            for node in sorted_head_difference_1hr:
                para_1hrtab_1min += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_1hr[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 1hr : {round(node_demand_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 1min : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_1hr[node]-node_demand_map[node],3)}</b><br><br><br>")
            
            logger.info("Paragraph for 1hr tab with 1min data is stored")
            
            for node in G.nodes():
                if node in diffrent_1hr :
                    G.nodes[node]['color'] = 'green'    # diffrent demand or head then 1hr -> Green
                    G.nodes[node]['size'] = 45

        # if the node is in the both the list
        if nodeData5min is not None and nodeData1hr is not None:
            for node in G.nodes():
                if node in diffrent_5min and node in diffrent_1hr:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 45
                
        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_1min_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_5min, node_head_5min, node_demand_1hr, node_head_1hr, diffrent_5min, diffrent_1hr)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=node_size,
                color=node_colors,  # Colors assigned individually for each node
                line=dict(width=2, color='black')
            )
        )
        
        logger.info("Node trace created for 1min graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='#bbb')
        )
        
        logger.info("Edge trace created for 1min graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions(G, node_pos, unique_parallel_pipes)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 1min graph")
        
        nodeFig_1min = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Nodes Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        nodeFig_5min = go.Figure()
        nodeFig_1hr = go.Figure()
        
        if (nodeData5min is not None) and (start == 0):
            # print("Hello World")
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData5min)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData5min, parrallel_pipes)
            logger.info("Creating 5min graph with 1min data")
            nodeFig_5min, _, _, _, _, _, _ = self.create_node_5min_graph(node_pos, nodeData5min, pipeData5min, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData1hr, pipeData1hr, G1, start+1)

        if (nodeData1hr is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1hr)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData1hr, parrallel_pipes)
            logger.info("Creating 1hr graph with 1min data")
            nodeFig_1hr, _, _, _, _, _, _ = self.create_node_1hr_graph(node_pos, nodeData1hr, pipeData1hr, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData5min, pipeData5min, G2, start+1)
        
        return nodeFig_1min, nodeFig_5min, nodeFig_1hr, para_1mintab_5min, para_1mintab_1hr, para_5mintab_1min, para_1hrtab_1min
    
    
    #node graph for the 5 min tab
    def create_node_5min_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, nodeData1hr, pipeData1hr, G, start) :
        node_demand_map = {}    
        node_demand_1hr={}
        node_demand_1min={}
        data_processor = OutputDataProcessor()
        diffrent_1min = [] #for nodes with different demand or head in 1min
        diffrent_1hr = [] #for nodes with different demand or head in 1hr
        demand_difference_1min = {} #difference in demand in 1min
        demand_difference_1hr = {} #difference in demand in 1hr
        sorted_demand_difference_1min = {} #sorted difference in demand in 1min
        sorted_demand_difference_1hr = {} #sorted difference in demand in 1hr
        para_5mintab_1min= "" #Paragraph for 5min tab with 1min data
        para_5mintab_1hr= ""  #Paragraph for 5min tab with 1hr data
        para_1mintab_5min=""  #Paragraph for 1min tab with 5min data
        para_1hrtab_5min=""   #Paragraph for 1hr tab with 5min data
        node_head_map = {}    #5min node to head map
        node_head_1hr={}      #1hr node to head map
        node_head_1min={}    #1min node to head map
        head_difference_1min = {} #difference in head in 1min
        head_difference_1hr = {}  #difference in head in 1hr
        sorted_head_difference_1min = {} #sorted difference in head in 1min
        sorted_head_difference_1hr = {} #sorted difference in head in 1hr
        
        # Create the map for 5min node_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
            
        logger.info(f"5min Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = 'blue'
            G.nodes[node]['size'] = 30  # Default size for all nodes
        
        # print("hello from 5 min")
        if nodeData1min is not None:
            # Create the map for 5minNodeData
            for i in range(len(nodeData1min["nodeID"])):
                node_id = nodeData1min["nodeID"][i]
                demand = nodeData1min["Demand"][i]
                head = nodeData1min["Head"][i]
                node_demand_1min[node_id] = demand
                node_head_1min[node_id] = head
            
            logger.info("1 minute Result File Head Map : "+ str(node_head_1min))
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1min[node])) or (float(node_head_map[node]) != float(node_head_1min[node])):
                    diffrent_1min.append(node)
                    demand_difference_1min[node]=(float(node_demand_map[node]) - float(node_demand_1min[node]))
                    head_difference_1min[node]=(float(node_head_map[node]) - float(node_head_1min[node]))
                
            
            logger.info("Diffrent Node ID in 1min output file compare to the 5min output file : "+ str(diffrent_1min))
            
            #reverse sort the list
            sorted_head_difference_1min = dict(sorted(head_difference_1min.items(), key=lambda item: item[1], reverse=True))
            
            #traverse the sorted list and create the list 
            for node in sorted_head_difference_1min:
                para_5mintab_1min +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1min[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node] - node_demand_1min[node],3)}</b><br><br><br>"
                                    )
            
            logger.info("Paragraph for 5min tab with 1min data is stored")
            #sort the list with the node
            sorted_head_difference_1min = dict(sorted(head_difference_1min.items(), key=lambda item: item[1], reverse=False))
            
            for node in sorted_head_difference_1min:                        
                para_1mintab_5min +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_1min[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_1min[node]-node_demand_map[node],3)}</b><br><br><br>")

            logger.info("Paragraph for 1min tab with 5min data is stored")
            
            for node in G.nodes():
                if node in diffrent_1min:
                    G.nodes[node]['color'] = 'red'  # diffrent demand or head then 1min -> Red
                    G.nodes[node]['size'] = 45
                
        # Create the map for 1hrNodeData
        if nodeData1hr is not None:
            for i in range(len(nodeData1hr["nodeID"])):
                node_id = nodeData1hr["nodeID"][i]
                demand = nodeData1hr["Demand"][i]
                head = nodeData1hr["Head"][i]
                node_demand_1hr[node_id] = demand
                node_head_1hr[node_id] = head
            
            logger.info("1 hour Result File Head Map : "+ str(node_head_1hr))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1hr[node])) or (float(node_head_map[node]) != float(node_head_1hr[node])):
                    diffrent_1hr.append(node)
                    demand_difference_1hr[node]=(float(node_demand_map[node]) - float(node_demand_1hr[node]))
                    head_difference_1hr[node]=(float(node_head_map[node]) - float(node_head_1hr[node]))
            
            logger.info("Diffrent Node ID in 1hr output file compare to the 5min output file : "+ str(diffrent_1hr))
                    
            #sort the list with the node 
            sorted_head_difference_1hr = dict(sorted(demand_difference_1hr.items(), key=lambda item: item[1], reverse=True))
            for node in sorted_demand_difference_1hr:
                para_5mintab_1hr += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1hr[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1hr : {round(node_demand_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_demand_difference_1hr[node],3)}</b><br><br><br>"
                                    )
            
            logger.info("Paragraph for 5min tab with 1hr data is stored")
            
            sorted_head_difference_1hr = dict(sorted(demand_difference_1hr.items(), key=lambda item: item[1], reverse=False))
                
            for node in sorted_head_difference_1hr:
                para_1hrtab_5min += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_head_1hr[node]-node_head_map[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 1hr : {round(node_demand_1hr[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 5min : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_1hr[node]-node_demand_map[node],3)}</b><br><br><br>")

            for node in G.nodes():
                if node in diffrent_1hr :
                    G.nodes[node]['color'] = 'yellow'    # diffrent demand or head then 1hr -> yellow
                    G.nodes[node]['size'] = 45

        # if the node is in the both the list
        if nodeData1min is not None and nodeData1hr is not None:
            for node in G.nodes():
                if node in diffrent_1min and node in diffrent_1hr:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 45
                
        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_5min_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_1min, node_head_1min, node_demand_1hr, node_head_1hr, diffrent_1min, diffrent_1hr)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=node_size,
                color=node_colors,  # Colors assigned individually for each node
                line=dict(width=2, color='black')
            )
        )
        
        logger.info("Node trace created for 5min graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='#bbb')
        )
        
        logger.info("Edge trace created for 5min graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions(G, node_pos, unique_parallel_pipes)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 5min graph")
        
        nodeFig_5min = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Nodes Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        logger.info("Node figure created for 5min graph")
        
        nodeFig_1min = go.Figure()
        nodeFig_1hr = go.Figure()
        
        #start is to remove the recusrsion
        if (nodeData1min is not None) and (start == 0) :
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1min)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData1min, parrallel_pipes)
            logger.info("Creating 1min graph with 5min data")
            nodeFig_1min, _, _, _, _, _, _ = self.create_node_1min_graph(node_pos, nodeData1min, pipeData1min, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData1hr, pipeData1hr, G1, start+1)

        if (nodeData1hr is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1hr)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData1hr, parrallel_pipes)
            logger.info("Creating 1hr graph with 5min data")
            nodeFig_1hr, _, _, _, _, _, _ = self.create_node_1hr_graph(node_pos, nodeData1hr, pipeData1hr, parrallel_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, node_data, pipe_data, G2, start+1)

        return nodeFig_5min, nodeFig_1min, nodeFig_1hr, para_5mintab_1min, para_5mintab_1hr, para_1mintab_5min, para_1hrtab_5min
    
    #Node graph for the 1hr tab
    def create_node_1hr_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, nodeData5min, pipeData5min, G, start) :
        node_demand_map = {}    
        node_demand_5min={}
        node_demand_1min={}
        data_processor = OutputDataProcessor()
        diffrent_1min = [] #for nodes with different demand or head in 1min
        diffrent_5min = [] #for nodes with different demand or head in 5min
        demand_difference_1min = {} #difference in demand in 1min
        demand_difference_5min = {} #difference in demand in 1hr
        sorted_demand_difference_1min = {} #sorted difference in demand in 1min
        sorted_demand_difference_5min = {} #sorted difference in demand in 5min
        para_1hrtab_1min= "" #Paragraph for 1hr tab with 1min data
        para_1hrtab_5min= ""  #Paragraph for 1hr tab with 5min data
        para_1mintab_1hr=""  #Paragraph for 1min tab with 1hr data
        para_5mintab_1hr=""   #Paragraph for 5min tab with 1hr data
        node_head_map = {}    #5min node to head map
        node_head_5min={}      #1hr node to head map
        node_head_1min={}    #1min node to head map
        head_difference_1min = {} #difference in head in 1min
        head_difference_5min = {}  #difference in head in 1hr
        sorted_head_difference_1min = {} #sorted difference in head in 1min
        sorted_head_difference_5min = {} #sorted difference in head in 1hr
        
        # Create the map for 1hr node_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
            
        logger.info(f"1hr Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = 'blue'
            G.nodes[node]['size'] = 30  # Default size for all nodes
        
        
        if nodeData1min is not None:
            # Create the map for 5minNodeData
            for i in range(len(nodeData1min["nodeID"])):
                node_id = nodeData1min["nodeID"][i]
                demand = nodeData1min["Demand"][i]
                head = nodeData1min["Head"][i]
                node_demand_1min[node_id] = demand
                node_head_1min[node_id] = head
            
            logger.info("1 minute Result File Head Map : "+ str(node_head_1min))   
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1min[node])) or (float(node_head_map[node]) != float(node_head_1min[node])):
                    diffrent_1min.append(node)
                    demand_difference_1min[node]=(float(node_demand_map[node]) - float(node_demand_1min[node]))
                    head_difference_1min[node]=(float(node_head_map[node]) - float(node_head_1min[node]))
            
            logger.info("Diffrent Node ID in 1min output file compare to the 1hr output file : "+ str(diffrent_1min))
            
            #reverse sort the list
            sorted_head_difference_1min = dict(sorted(head_difference_1min.items(), key=lambda item: item[1], reverse=True))
            
            #traverse the sorted list and create the list 
            for node in sorted_head_difference_1min:
                para_1hrtab_1min +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1min[node],3)}</b><br><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1hr : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node]- node_demand_1min[node],3)}</b><br><br><br>"
                                    )
            
            logger.info("Paragraph for 1hr tab with 1min data is stored")
            #sort the list with the node
            sorted_head_difference_1min = dict(sorted(head_difference_1min.items(), key=lambda item: item[1], reverse=False))
            
            for node in sorted_head_difference_1min:                        
                para_1mintab_1hr +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1min : {round(node_head_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_1min[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1min : {round(node_demand_1min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1hr : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_1min[node]-node_demand_map[node],3)}</b><br><br><br>")
            
            logger.info("Paragraph for 1min tab with 1hr data is stored")
            
            for node in G.nodes():
                if node in diffrent_1min:
                    G.nodes[node]['color'] = 'green'  # diffrent demand or head then 1min -> Green
                    G.nodes[node]['size'] = 45
                
        # Create the map for 1hrNodeData
        if nodeData5min is not None:
            for i in range(len(nodeData5min["nodeID"])):
                node_id = nodeData5min["nodeID"][i]
                demand = nodeData5min["Demand"][i]
                head = nodeData5min["Head"][i]
                node_demand_5min[node_id] = demand
                node_head_5min[node_id] = head
            
            logger.info("5 minute Result File Head Map : "+ str(node_head_5min))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_5min[node])) or (float(node_head_map[node]) != float(node_head_5min[node])):
                    diffrent_5min.append(node)
                    demand_difference_5min[node]=(float(node_demand_map[node]) - float(node_demand_5min[node]))
                    head_difference_5min[node]=(float(node_head_map[node]) - float(node_head_5min[node]))
            
            logger.info("Diffrent Node ID in 5min output file compare to the 1hr output file : "+ str(diffrent_5min))
                    
            #sort the list with the node 
            sorted_head_difference_5min = dict(sorted(head_difference_5min.items(), key=lambda item: item[1], reverse=True))
            for node in sorted_head_difference_5min:
                para_1hrtab_5min += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(sorted_head_difference_5min[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1hr : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 5min : {round(node_demand_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_demand_map[node]-node_demand_5min[node],3)}<br><br><br>"
                                    )
            
            logger.info("Paragraph for 1hr tab with 5min data is stored")
            
            sorted_head_difference_5min = dict(sorted(demand_difference_5min.items(), key=lambda item: item[1], reverse=False))
                
            for node in sorted_head_difference_5min:
                para_5mintab_1hr += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 5min : {round(node_head_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1hr : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_head_5min[node]-node_head_map[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 5min : {round(node_demand_5min[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 1hr : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_5min[node]-node_demand_map[node],3)}</b><br><br><br>")
            
            logger.info("Paragraph for 5min tab with 1hr data is stored")
            
            for node in G.nodes():
                if node in diffrent_5min :
                    G.nodes[node]['color'] = 'yellow'    # diffrent demand or head then 1hr -> yellow
                    G.nodes[node]['size'] = 45

        # if the node is in the both the list
        if nodeData1min is not None and nodeData5min is not None:
            for node in G.nodes():
                if node in diffrent_1min and node in diffrent_5min:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 45
                
        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_1hr_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_1min, node_head_1min, node_demand_5min, node_head_5min, diffrent_1min, diffrent_5min)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=node_size,
                color=node_colors,  # Colors assigned individually for each node
                line=dict(width=2, color='black')
            )
        )
        
        logger.info("Node trace created for 1hr graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='#bbb')
        )
        
        logger.info("Edge trace created for 1hr graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions(G, node_pos, unique_parallel_pipes)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 1hr graph")
        
        nodeFig_1hr = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Nodes Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        logger.info("Node figure created for 1hr graph")
        nodeFig_1min = go.Figure()
        nodeFig_5min = go.Figure()
        
        
        if (nodeData1min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1min)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData1min, parrallel_pipes)
            logger.info("Creating 1min graph with 1hr data")
            nodeFig_1min, _, _, _, _, _, _ = self.create_node_1min_graph(node_pos, nodeData1min, pipeData1min, parrallel_pipes, mainNodeData, mainpipe, nodeData5min, pipeData5min, node_data, pipe_data, G1, start+1)
        
        if (nodeData5min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData5min)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData5min, parrallel_pipes)
            logger.info("Creating 5min graph with 1hr data")
            nodeFig_5min, _, _, _, _, _, _ = self.create_node_5min_graph(node_pos, nodeData5min, pipeData5min, parrallel_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, node_data, pipe_data, G2, start+1)

        return nodeFig_1hr, nodeFig_1min, nodeFig_5min, para_1hrtab_1min, para_1hrtab_5min, para_1mintab_1hr, para_5mintab_1hr
    
    
    def create_pipe_1min_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData5min, pipeData5min, nodeData1hr, pipeData1hr, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_1mintab_5min = ""  # Paragraph for 1min tab with 5min data
        par_1mintab_1hr = ""  # Paragraph for 1min tab with 1hr data
        par_5mintab_1min = ""  # Paragraph for 5min tab with 1min data
        par_1hrtab_1min = ""  # Paragraph for 1hr tab with 1min data
        id_to_cost_map_1min = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"1min Graph Head Map : " + str(node_head_map))
        
        node_x, node_y, node_text, node_hovertext = data_processor.process_nodes_for_diameter_graph_plotting(G, pos, elevation_map, node_head_map)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=30,
                color="blue", 
                line=dict(width=2, color='black')
            )
        )
        logger.info("Node trace created for 1min graph")
        
        
        different_pipe_5min = []
        different_pipe_1hr = []
        pipeid_length_map_1min ={}
        pipeid_cost_map_1min={}
        pipeid_flow_map_1min ={}
        pipeif_speed_map_1min={}
        difference_cost_pipeid_5min ={}
        difference_cost_pipeid_1hr ={}
        id_to_cost_map_1hr = defaultdict(float)  # Map to store pipeID to cost for 1hr data
        id_to_cost_map_5min = defaultdict(float)  # Map to store pipeID to cost for 5min data
        exist_pipe_status_5min = {} #parallel pipe flow and speed is same or not
        exist_pipe_status_1hr = {}
        flow_parallel = {}#for the static pipe which cost is zero 
        speed_parallel= {} #for the static pipe which cost is zero
        unique_pipeid_1min= []
        
        for i in range(len(pipe_data["pipeID"])):
            pipe_id = pipe_data["pipeID"][i]
            start_node = pipe_data["startNode"][i]
            end_node = pipe_data["endNode"][i]
            diameter = pipe_data["diameter"][i]
            length = pipe_data["length"][i]
            cost = pipe_data["cost"][i]
            flow = pipe_data["flow"][i]
            speed = pipe_data["speed"][i]
            parallel = pipe_data["parallel"][i]
            
            if cost ==0:
                flow_parallel[pipe_id]=flow
                speed_parallel[pipe_id]=speed
            
            if pipe_id not in unique_pipeid_1min:
                unique_pipeid_1min.append(pipe_id)
            
            pipeid_length_map_1min[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_1min[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_1min[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_1min[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_1min[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("1 minute Result File Pipe ID to Cost Map : " + str(id_to_cost_map_1min))
        
        if pipeData5min is not None:
            unique_id=unique_pipeid_1min.copy()  # Create a copy of unique_pipeid_1min to track unique pipe IDs
            for i in range(len(pipeData5min["pipeID"])):
                pipe_id = pipeData5min["pipeID"][i]
                diameter = pipeData5min["diameter"][i]
                length = pipeData5min["length"][i]
                parallel = pipeData5min["parallel"][i]
                cost = pipeData5min["cost"][i]
                flow = pipeData5min["flow"][i]
                speed = pipeData5min["speed"][i]
                
                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_5min[pipe_id] = False
                    
                if cost!=0 :
                    id_to_cost_map_5min[pipe_id] += cost  # Aggregate cost for each pipeID in 5min data
                    
                    # Find the pipe id which are diffrent from 5min to 1min
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1min:
                        different_pipe_5min.append(pipe_id)
                    elif length != pipeid_length_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_5min.append(pipe_id)
                    elif cost != pipeid_cost_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_5min.append(pipe_id)
                    elif flow != pipeid_flow_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_5min.append(pipe_id) 
                    elif speed != pipeif_speed_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_5min.append(pipe_id)
                    else:   
                        None
                    
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_5min.append(pipe_id)  # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if(pipe_id ==2):
                    print(f"No of pipe ID in 2 is : {no_of_pipes[pipe_id]}")
                
                if pipe_id not in unique_pipeid_1min:
                    different_pipe_5min.append(pipe_id)
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
            
            if(len(unique_id) > 0):
                different_pipe_5min+=unique_id    
                
            different_pipe_5min= list(dict.fromkeys(different_pipe_5min))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 5min output file compare to the 1min output file : "+ str(different_pipe_5min))
            
            #find the diffrance cost between one minute and five minute
            for pipe_id in different_pipe_5min:
                if pipe_id in id_to_cost_map_1min and pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_5min[pipe_id] = id_to_cost_map_1min[pipe_id] - id_to_cost_map_5min[pipe_id]
                elif pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_5min[pipe_id] = -id_to_cost_map_5min[pipe_id]
                elif pipe_id in id_to_cost_map_1min:
                    difference_cost_pipeid_5min[pipe_id] = id_to_cost_map_1min[pipe_id]
                else:
                    difference_cost_pipeid_5min[pipe_id] = 0
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_5min = dict(sorted(difference_cost_pipeid_5min.items(), key=lambda item: item[1], reverse=True))
            
            for pipe_id in sorted_difference_cost_pipeid_5min:
                par_1mintab_5min += (f"Pipe ID : <b>{pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1mintab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")

                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                
                for i in range(len(pipeData5min["pipeID"])):
                    if pipeData5min["pipeID"][i] == pipe_id:
                        diameter = pipeData5min["diameter"][i]
                        length = pipeData5min["length"][i]
                        cost = pipeData5min["cost"][i]
                        flow = pipeData5min["flow"][i]
                        speed = pipeData5min["speed"][i]
                        par_1mintab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")
                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_5min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1min tab with 5min data is stored")
                
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_5min = dict(sorted(difference_cost_pipeid_5min.items(), key=lambda item: item[1], reverse=False))
            
            for pipe_id in sorted_difference_cost_pipeid_5min:
                par_5mintab_1min += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                for i in range(len(pipeData5min["pipeID"])):
                    if pipeData5min["pipeID"][i] == pipe_id:
                        diameter = pipeData5min["diameter"][i]
                        length = pipeData5min["length"][i]
                        cost = pipeData5min["cost"][i]
                        flow = pipeData5min["flow"][i]
                        speed = pipeData5min["speed"][i]
                        par_5mintab_1min += ( 
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")
                
                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_5mintab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br>")
                
                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")
                par_5mintab_1min += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_5min[pipe_id], 3)}</b><br><br><br>")
            
            logger.info("Paragraph for 5min tab with 1min data is stored")    
            
        if pipeData1hr is not None:
            unique_id = unique_pipeid_1min.copy()  # Create a copy of unique_pipeid_1min to track unique pipe IDs
            for i in range(len(pipeData1hr["pipeID"])):
                pipe_id = pipeData1hr["pipeID"][i]
                diameter = pipeData1hr["diameter"][i]
                length = pipeData1hr["length"][i]
                parallel = pipeData1hr["parallel"][i]
                cost = pipeData1hr["cost"][i]
                flow = pipeData1hr["flow"][i]
                speed = pipeData1hr["speed"][i]
                
                id_to_cost_map_1hr[pipe_id] += cost  # Aggregate cost for each pipeID in 1hr data

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1hr[pipe_id] = False

                    # Find the pipe id which are diffrent from 1min to 1hr
                if cost!=0 :
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1min:
                        different_pipe_1hr.append(pipe_id)
                    elif length != pipeid_length_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_1hr.append(pipe_id)
                    elif cost != pipeid_cost_map_1min[(pipe_id, diameter, parallel)]:
                        different_pipe_1hr.append(pipe_id)
                    elif flow != pipeid_flow_map_1min[(pipe_id, diameter, parallel)] and cost != 0:
                        different_pipe_1hr.append(pipe_id) 
                    elif speed != pipeif_speed_map_1min[(pipe_id, diameter, parallel)] and cost != 0:
                        different_pipe_1hr.append(pipe_id)
                    else:   
                        None
                
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_1hr.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if pipe_id not in unique_pipeid_1min:
                    different_pipe_1hr.append(pipe_id)
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
                    
            if(len(unique_id) > 0):
                different_pipe_1hr+=unique_id

            different_pipe_1hr = list(dict.fromkeys(different_pipe_1hr))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 1hr output file compare to the 1min output file : "+ str(different_pipe_1hr))

            
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_1hr:
                if pipe_id in id_to_cost_map_1min and pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1hr[pipe_id] = id_to_cost_map_1min[pipe_id] - id_to_cost_map_1hr[pipe_id]
                elif pipe_id in id_to_cost_map_1min:
                    difference_cost_pipeid_1hr[pipe_id] = id_to_cost_map_1min[pipe_id]
                elif pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1hr[pipe_id] = -id_to_cost_map_1hr[pipe_id]
                else:
                    difference_cost_pipeid_1hr[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1hr = dict(sorted(difference_cost_pipeid_1hr.items(), key=lambda item: item[1], reverse=True))
            
            #prepare the paragraph for 1min tab with 1hr data
            for pipe_id in sorted_difference_cost_pipeid_1hr:
                par_1mintab_1hr += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")

                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                
                for i in range(len(pipeData1hr["pipeID"])):
                    if pipeData1hr["pipeID"][i] == pipe_id:
                        diameter = pipeData1hr["diameter"][i]
                        length = pipeData1hr["length"][i]
                        cost = pipeData1hr["cost"][i]
                        flow = pipeData1hr["flow"][i]
                        speed = pipeData1hr["speed"][i]
                        par_1mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")
                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_1hr[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1min tab with 1hr data is stored")

            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1hr = dict(sorted(difference_cost_pipeid_1hr.items(), key=lambda item: item[1], reverse=False))
            
            for pipe_id in sorted_difference_cost_pipeid_1hr:
                par_1hrtab_1min += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                for i in range(len(pipeData1hr["pipeID"])):
                    if pipeData1hr["pipeID"][i] == pipe_id:
                        diameter = pipeData1hr["diameter"][i]
                        length = pipeData1hr["length"][i]
                        cost = pipeData1hr["cost"][i]
                        flow = pipeData1hr["flow"][i]
                        speed = pipeData1hr["speed"][i]
                        par_1hrtab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")

                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1hrtab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")
                par_1hrtab_1min += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1hr[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1hr tab with 1min data is stored")
        
        edge_trace ,edge_text, edge_colors= data_processor.process_edges_for_diameter_graph_plotting_1min(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_5min, different_pipe_1hr, exist_pipe_status_5min, exist_pipe_status_1hr)
        
        logger.info("Edge trace created for 1min pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_1min(G, pos, unique_parallel_pipes, edge_colors, pipeData5min, pipeData1hr, different_pipe_5min, different_pipe_1hr, exist_pipe_status_5min, exist_pipe_status_1hr)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 1min pipe data graph")
        
        pipeFig_1min = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Pipe in Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        logger.info("Pipe figure created for 1min graph")
        
        pipeFig_5min = go.Figure()
        pipeFig_1hr = go.Figure()
        
        if (pipeData5min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData5min)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData5min, parrallel_pipes)
            logger.info("Creating 5min graph with 1hr data")
            pipeFig_5min, _, _, _, _, _, _ = self.create_pipe_5min_graph(pos, nodeData5min, pipeData5min, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData1hr, pipeData1hr, G1, start+1)
            
        
        if (pipeData1hr is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1hr)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1hr, parrallel_pipes)
            logger.info("Creating 1hr graph with 1min data")
            pipeFig_1hr, _, _, _, _, _, _ = self.create_pipe_1hr_graph(pos, nodeData1hr, pipeData1hr, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData5min, pipeData5min, G2, start+1)
        
        return pipeFig_1min, pipeFig_5min, pipeFig_1hr, par_1mintab_5min, par_1mintab_1hr, par_5mintab_1min, par_1hrtab_1min
    

    def create_pipe_5min_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, nodeData1hr, pipeData1hr, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_5mintab_1min = ""  # Paragraph for 5min tab with 1min data
        par_5mintab_1hr = ""  # Paragraph for 5min tab with 1hr data
        par_1mintab_5min = ""  # Paragraph for 5min tab with 5min data
        par_1hrtab_5min = ""  # Paragraph for 1hr tab with 5min data
        id_to_cost_map_5min = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"5min Graph Head Map : " + str(node_head_map))
        
        node_x, node_y, node_text, node_hovertext = data_processor.process_nodes_for_diameter_graph_plotting(G, pos, elevation_map, node_head_map)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=30,
                color="blue", 
                line=dict(width=2, color='black')
            )
        )
        
        logger.info("Node trace created for 5min graph")
        
        
        different_pipe_1min = []
        different_pipe_1hr = []
        pipeid_length_map_5min ={}
        pipeid_cost_map_5min={}
        pipeid_flow_map_5min ={}
        pipeif_speed_map_5min={}
        difference_cost_pipeid_1min ={}
        difference_cost_pipeid_1hr ={}
        exist_pipe_status_1min = {} #static parallel pipe flow and speed is same or not
        exist_pipe_status_1hr = {} #static parallel pipe flow and speed is same or not
        flow_parallel = {} #for the static pipe which cost is zero 
        speed_parallel= {}  #for the static pipe which cost is zero
        unique_pipeid_5min= []
        
        for i in range(len(pipe_data["pipeID"])):
            pipe_id = pipe_data["pipeID"][i]
            start_node = pipe_data["startNode"][i]
            end_node = pipe_data["endNode"][i]
            diameter = pipe_data["diameter"][i]
            length = pipe_data["length"][i]
            cost = pipe_data["cost"][i]
            flow = pipe_data["flow"][i]
            speed = pipe_data["speed"][i]
            parallel = pipe_data["parallel"][i]
            
            if pipe_id not in unique_pipeid_5min:
                unique_pipeid_5min.append(pipe_id)
            
            print("Unique Pipe ID in 5min data: ", unique_pipeid_5min)
            
            if cost==0:
                flow_parallel[pipe_id]=flow
                speed_parallel[pipe_id]=speed
            
            pipeid_length_map_5min[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_5min[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_5min[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_5min[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_5min[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("5 minute Result File Pipe ID to Cost Map : " + str(id_to_cost_map_5min))
        
        if pipeData1min is not None:
            unique_id = unique_pipeid_5min.copy()
            id_to_cost_map_1min = defaultdict(float)  # Map to store pipeID to cost for 1min data
            for i in range(len(pipeData1min["pipeID"])):
                pipe_id = pipeData1min["pipeID"][i]
                diameter = pipeData1min["diameter"][i]
                length = pipeData1min["length"][i]
                parallel = pipeData1min["parallel"][i]
                cost = pipeData1min["cost"][i]
                flow = pipeData1min["flow"][i]
                speed = pipeData1min["speed"][i]
                
                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1min[pipe_id] = False
                elif cost ==0 and (flow_parallel[pipe_id] == flow and speed_parallel[pipe_id] == speed):
                    exist_pipe_status_1min[pipe_id] = True
                    
                id_to_cost_map_1min[pipe_id] += cost  # Aggregate cost for each pipeID in 5min data
                
                # Find the pipe id which are diffrent from 5min to 1min
                if cost!=0 :
                    if(pipe_id == 2):
                        print("Pipe ID 2 found in 1min data")
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_5min:
                        print("Pipe ID not found in 1min data: ", pipe_id)
                        different_pipe_1min.append(pipe_id)
                    elif length != pipeid_length_map_5min[(pipe_id, diameter, parallel)]:
                        print("Pipe length not match 1min data: ", pipe_id)
                        different_pipe_1min.append(pipe_id)
                    elif cost != pipeid_cost_map_5min[(pipe_id, diameter, parallel)]:
                        print("Pipe cost not match 1min data: ", pipe_id)
                        different_pipe_1min.append(pipe_id)
                    elif flow != pipeid_flow_map_5min[(pipe_id, diameter, parallel)]:
                        print("Pipe flow not match 1min data: ", pipe_id)
                        different_pipe_1min.append(pipe_id) 
                    elif speed != pipeif_speed_map_5min[(pipe_id, diameter, parallel)]:
                        print("Pipe speed not match 1min data: ", pipe_id)
                        different_pipe_1min.append(pipe_id)
                    else:   
                        None
                
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    print("Pipe cost is zero and parallel is not parallel: ", pipe_id)
                    different_pipe_1min.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if(pipe_id not in unique_pipeid_5min):
                    print("Unique Pipe ID :", unique_pipeid_5min)
                    print("Pipe ID not found in 5min data: ", pipe_id)
                    different_pipe_1min.append(pipe_id)
                
                if pipe_id in unique_id:
                    # print("Removing Pipe ID from unique_id: ", pipe_id)
                    unique_id.remove(pipe_id)

            print("Unique Pipe ID in 5min data: ", unique_id)
            if len(unique_id) > 0:
                different_pipe_1min += unique_id

            different_pipe_1min= list(dict.fromkeys(different_pipe_1min))  # Remove duplicates
            logger.info("Pipe ID which are diffrent in 1min output file compare to the 5min output file : "+ str(different_pipe_1min))
            
            #find the diffrance cost between one minute and five minute
            for pipe_id in different_pipe_1min:
                if pipe_id in id_to_cost_map_1min and pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_1min[pipe_id] = id_to_cost_map_5min[pipe_id] - id_to_cost_map_1min[pipe_id]
                elif pipe_id in id_to_cost_map_1min:
                    difference_cost_pipeid_1min[pipe_id] = -id_to_cost_map_1min[pipe_id]
                elif pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_1min[pipe_id] = id_to_cost_map_5min[pipe_id]
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1min = dict(sorted(difference_cost_pipeid_1min.items(), key=lambda item: item[1], reverse=True))
            
            for pipe_id in sorted_difference_cost_pipeid_1min:
                par_5mintab_1min += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_5mintab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")

                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                
                for i in range(len(pipeData1min["pipeID"])):
                    if pipeData1min["pipeID"][i] == pipe_id:
                        diameter = pipeData1min["diameter"][i]
                        length = pipeData1min["length"][i]
                        cost = pipeData1min["cost"][i]
                        flow = pipeData1min["flow"][i]
                        speed = pipeData1min["speed"][i]
                        par_5mintab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")
                par_5mintab_1min += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_1min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 5min tab with 1min data is stored")
                
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1min = dict(sorted(difference_cost_pipeid_1min.items(), key=lambda item: item[1], reverse=False))
            
            for pipe_id in sorted_difference_cost_pipeid_1min:
                par_1mintab_5min += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                for i in range(len(pipeData1min["pipeID"])):
                    if pipeData1min["pipeID"][i] == pipe_id:
                        diameter = pipeData1min["diameter"][i]
                        length = pipeData1min["length"][i]
                        cost = pipeData1min["cost"][i]
                        flow = pipeData1min["flow"][i]
                        speed = pipeData1min["speed"][i]
                        par_1mintab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")

                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1mintab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1mintab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")
                par_1mintab_5min += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1min[pipe_id], 3)}</b><br><br><br>")

        logger.info("Paragraph for 1min tab with 5min data is stored")

        if pipeData1hr is not None:
            unique_id = unique_pipeid_5min.copy()
            id_to_cost_map_1hr = defaultdict(float)  # Map to store pipeID to cost for 1hr data
            for i in range(len(pipeData1hr["pipeID"])):
                pipe_id = pipeData1hr["pipeID"][i]
                diameter = pipeData1hr["diameter"][i]
                length = pipeData1hr["length"][i]
                parallel = pipeData1hr["parallel"][i]
                cost = pipeData1hr["cost"][i]
                flow = pipeData1hr["flow"][i]
                speed = pipeData1hr["speed"][i]
                
                id_to_cost_map_1hr[pipe_id] += cost  # Aggregate cost for each pipeID in 1hr data

                if cost ==0  and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1hr[pipe_id] = False
                else:
                    exist_pipe_status_1hr[pipe_id] = True
                
                if pipe_id not in unique_pipeid_5min:
                    different_pipe_1hr.append(pipe_id)

                # Find the pipe id which are diffrent from 1min to 1hr
                if cost!=0 :
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_5min:
                        different_pipe_1hr.append(pipe_id)
                    elif length != pipeid_length_map_5min[(pipe_id, diameter, parallel)]:
                        different_pipe_1hr.append(pipe_id)
                    elif cost != pipeid_cost_map_5min[(pipe_id, diameter, parallel)]:
                        different_pipe_1hr.append(pipe_id)
                    elif flow != pipeid_flow_map_5min[(pipe_id, diameter, parallel)] and cost != 0:
                        different_pipe_1hr.append(pipe_id) 
                    elif speed != pipeif_speed_map_5min[(pipe_id, diameter, parallel)] and cost != 0:
                        different_pipe_1hr.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_1hr.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)


            if(len(unique_id) > 0) :
                different_pipe_1hr+=unique_id
            
            
            different_pipe_1hr = list(dict.fromkeys(different_pipe_1hr))  # Remove duplicates   
            
            logger.info("Pipe ID which are diffrent in 1hr output file compare to the 5min output file : "+ str(different_pipe_1hr)) 
            
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_1hr:
                if pipe_id in id_to_cost_map_5min and pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1hr[pipe_id] = id_to_cost_map_5min[pipe_id] - id_to_cost_map_1hr[pipe_id]
                elif pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_1hr[pipe_id] = id_to_cost_map_5min[pipe_id]
                elif pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1hr[pipe_id] = -id_to_cost_map_1hr[pipe_id]
                else:
                    difference_cost_pipeid_1hr[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1hr = dict(sorted(difference_cost_pipeid_1hr.items(), key=lambda item: item[1], reverse=True))
            
            #prepare the paragraph for 5min tab with 1hr data
            for pipe_id in sorted_difference_cost_pipeid_1hr:
                par_5mintab_1hr += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_5mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")

                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                
                for i in range(len(pipeData1hr["pipeID"])):
                    if pipeData1hr["pipeID"][i] == pipe_id:
                        diameter = pipeData1hr["diameter"][i]
                        length = pipeData1hr["length"][i]
                        cost = pipeData1hr["cost"][i]
                        flow = pipeData1hr["flow"][i]
                        speed = pipeData1hr["speed"][i]
                        par_5mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; <b>1hr Data :<b> <br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")
                par_5mintab_1hr += (f"&nbsp; &nbsp; <b>Difference in cost : {round(sorted_difference_cost_pipeid_1hr[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 5min tab with 1hr data is stored")
            
            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1hr = dict(sorted(difference_cost_pipeid_1hr.items(), key=lambda item: item[1], reverse=False))
            #prepare the paragraph for 1hr tab with 5min data
            for pipe_id in sorted_difference_cost_pipeid_1hr:
                par_1hrtab_5min += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                for i in range(len(pipeData1hr["pipeID"])):
                    if pipeData1hr["pipeID"][i] == pipe_id:
                        diameter = pipeData1hr["diameter"][i]
                        length = pipeData1hr["length"][i]
                        cost = pipeData1hr["cost"][i]
                        flow = pipeData1hr["flow"][i]
                        speed = pipeData1hr["speed"][i]
                        par_1hrtab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1hrtab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br><br>")

                par_1hrtab_5min += ( f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):

                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1hrtab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1hrtab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")
                par_1hrtab_5min += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1hr[pipe_id], 3)}</b><br><br><br>")
            logger.info("Paragraph for 1hr tab with 5min data is stored")
                        
        edge_trace ,edge_text, edge_colors= data_processor.process_edges_for_diameter_graph_plotting_5min(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1min, different_pipe_1hr, exist_pipe_status_1min, exist_pipe_status_1hr)
        
        logger.info("Edge trace created for 5min pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_5min(G, pos, unique_parallel_pipes, edge_colors, pipeData1min, pipeData1hr, different_pipe_1min, different_pipe_1hr, exist_pipe_status_1min, exist_pipe_status_1hr)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 5min pipe data graph")
        
        pipeFig_5min = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Pipe in Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        logger.info("Pipe figure created for 5min graph")   
        
        pipeFig_1min = go.Figure()
        pipeFig_1hr = go.Figure()
        
        if (pipeData1min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1min)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1min, parrallel_pipes)
            logger.info("Creating 1min graph with 5min data")
            logger.info("Parallel Pipes : " + str(parrallel_pipes))
            print("Number of Pipes in 1min data: ", no_of_pipe)
            pipeFig_1min, _, _, _, _, _, _ = self.create_pipe_1min_graph(pos, nodeData1min, pipeData1min, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData1hr, pipeData1hr, G1, start+1)
            
        
        if (pipeData1hr is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1hr)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1hr, parrallel_pipes)
            logger.info("Creating 1hr graph with 5min data")
            pipeFig_1hr, _, _, _, _, _, _ = self.create_pipe_1hr_graph(pos, nodeData1hr, pipeData1hr, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData1min, pipeData1min, node_data, pipe_data, G2, start+1)

        return pipeFig_5min, pipeFig_1min, pipeFig_1hr, par_5mintab_1min, par_5mintab_1hr, par_1mintab_5min, par_1hrtab_5min
    
    
    
    def create_pipe_1hr_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData1min, pipeData1min, nodeData5min, pipeData5min, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_1hrtab_1min = ""  # Paragraph for 1hr tab with 1min data
        par_1hrtab_5min = ""  # Paragraph for 1hr tab with 5min data
        par_1mintab_1hr = ""  # Paragraph for 1min tab with 1hr data
        par_5mintab_1hr = ""  # Paragraph for 5min tab with 1hr data
        id_to_cost_map_1hr = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"1hr Graph Head Map : " + str(node_head_map))
        
        node_x, node_y, node_text, node_hovertext = data_processor.process_nodes_for_diameter_graph_plotting(G, pos, elevation_map, node_head_map)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            hovertext=node_hovertext,
            mode='markers+text',
            hoverinfo='text',
            textposition='top center',
            marker=dict(
                size=30,
                color="blue", 
                line=dict(width=2, color='black')
            )
        )
        
        logger.info("Node trace created for 1hr graph")
        
        
        different_pipe_1min = []
        different_pipe_5min = []
        pipeid_length_map_1hr ={}
        pipeid_cost_map_1hr={}
        pipeid_flow_map_1hr ={}
        pipeif_speed_map_1hr={}
        difference_cost_pipeid_1min ={}
        difference_cost_pipeid_5min ={}
        unique_pipeid_1hr= []
        exist_pipe_status_1min = {} #static parallel pipe flow and speed is same or not
        exist_pipe_status_5min = {}
        flow_parallel = {} #for the static pipe which cost is zero 
        speed_parallel= {}  #for the static pipe which cost is zero
        
        for i in range(len(pipe_data["pipeID"])):
            pipe_id = pipe_data["pipeID"][i]
            start_node = pipe_data["startNode"][i]
            end_node = pipe_data["endNode"][i]
            diameter = pipe_data["diameter"][i]
            length = pipe_data["length"][i]
            cost = pipe_data["cost"][i]
            flow = pipe_data["flow"][i]
            speed = pipe_data["speed"][i]
            parallel = pipe_data["parallel"][i]
            
            if pipe_id not in unique_pipeid_1hr:
                unique_pipeid_1hr.append(pipe_id)
            
            if cost ==0:
                flow_parallel[pipe_id]=flow
                speed_parallel[pipe_id]=speed

            pipeid_length_map_1hr[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_1hr[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_1hr[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_1hr[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_1hr[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("1 hour Result File Pipe ID to Cost Map : " + str(id_to_cost_map_1hr))
                
        if pipeData1min is not None:
            unique_id = unique_pipeid_1hr.copy()
            id_to_cost_map_1min = defaultdict(float)  # Map to store pipeID to cost for 1min data
            for i in range(len(pipeData1min["pipeID"])):
                pipe_id = pipeData1min["pipeID"][i]
                diameter = pipeData1min["diameter"][i]
                length = pipeData1min["length"][i]
                parallel = pipeData1min["parallel"][i]
                cost = pipeData1min["cost"][i]
                flow = pipeData1min["flow"][i]
                speed = pipeData1min["speed"][i]

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1min[pipe_id] = False

                id_to_cost_map_1min[pipe_id] += cost  # Aggregate cost for each pipeID in 5min data
                
                # Find the pipe id which are diffrent from 1hr to 1min
                if cost!=0 :
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1hr:
                        different_pipe_1min.append(pipe_id)
                    elif length != pipeid_length_map_1hr[(pipe_id, diameter, parallel)]:
                        different_pipe_1min.append(pipe_id)
                    elif cost != pipeid_cost_map_1hr[(pipe_id, diameter, parallel)]:
                        different_pipe_1min.append(pipe_id)
                    elif flow != pipeid_flow_map_1hr[(pipe_id, diameter, parallel)]:
                        different_pipe_1min.append(pipe_id) 
                    elif speed != pipeif_speed_map_1hr[(pipe_id,diameter, parallel)]:
                        different_pipe_1min.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_1min.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
                
                if pipe_id not in unique_pipeid_1hr:
                    different_pipe_1min.append(pipe_id)

            if len(unique_id) > 0:
                different_pipe_1min+=unique_id
                
            different_pipe_1min= list(dict.fromkeys(different_pipe_1min))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 1min output file compare to the 1hr output file : "+ str(different_pipe_1min))
            #find the diffrance cost between one minute and one hour
            for pipe_id in different_pipe_1min:
                if pipe_id in id_to_cost_map_1min and pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1min[pipe_id] = id_to_cost_map_1hr[pipe_id] - id_to_cost_map_1min[pipe_id]
                elif pipe_id in id_to_cost_map_1min:
                    difference_cost_pipeid_1min[pipe_id]= - id_to_cost_map_1min[pipe_id]
                elif pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_1min[pipe_id] = id_to_cost_map_1hr[pipe_id]
                else:
                    difference_cost_pipeid_1min[pipe_id] = 0
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1min = dict(sorted(difference_cost_pipeid_1min.items(), key=lambda item: item[1], reverse=True))
            
            for pipe_id in sorted_difference_cost_pipeid_1min:
                par_1hrtab_1min += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1hrtab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")

                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                
                for i in range(len(pipeData1min["pipeID"])):
                    if pipeData1min["pipeID"][i] == pipe_id:
                        diameter = pipeData1min["diameter"][i]
                        length = pipeData1min["length"][i]
                        cost = pipeData1min["cost"][i]
                        flow = pipeData1min["flow"][i]
                        speed = pipeData1min["speed"][i]
                        par_1hrtab_1min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")
                par_1hrtab_1min += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_1min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1hr tab with 1min data is stored")
            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1min = dict(sorted(difference_cost_pipeid_1min.items(), key=lambda item: item[1], reverse=False))
            
            for pipe_id in sorted_difference_cost_pipeid_1min:
                par_1mintab_1hr += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1min Data :</b> <br>")
                for i in range(len(pipeData1min["pipeID"])):
                    if pipeData1min["pipeID"][i] == pipe_id:
                        diameter = pipeData1min["diameter"][i]
                        length = pipeData1min["length"][i]
                        cost = pipeData1min["cost"][i]
                        flow = pipeData1min["flow"][i]
                        speed = pipeData1min["speed"][i]
                        par_1mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 1min : {round(id_to_cost_map_1min[pipe_id], 3)}<br><br>")
                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")
                par_1mintab_1hr += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1min tab with 1hr data is stored")

        if pipeData5min is not None:
            unique_id = unique_pipeid_1hr.copy()
            id_to_cost_map_5min = defaultdict(float)  # Map to store pipeID to cost for 5min data
            for i in range(len(pipeData5min["pipeID"])):
                pipe_id = pipeData5min["pipeID"][i]
                diameter = pipeData5min["diameter"][i]
                length = pipeData5min["length"][i]
                parallel = pipeData5min["parallel"][i]
                cost = pipeData5min["cost"][i]
                flow = pipeData5min["flow"][i]
                speed = pipeData5min["speed"][i]
                
                id_to_cost_map_5min[pipe_id] += cost  # Aggregate cost for each pipeID in 5min data

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_5min[pipe_id] = False

                if pipe_id not in unique_pipeid_1hr:
                    # print(1)
                    different_pipe_5min.append(pipe_id)
                
                # Find the pipe id which are diffrent from 5min to 1hr
                if cost!=0 :
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1hr:
                        # print(2)
                        different_pipe_5min.append(pipe_id)
                    elif length != pipeid_length_map_1hr[(pipe_id, diameter, parallel)]:
                        # print(3)
                        different_pipe_5min.append(pipe_id)
                    elif cost != pipeid_cost_map_1hr[(pipe_id, diameter, parallel)]:
                        # print(4)
                        different_pipe_5min.append(pipe_id)
                    elif flow != pipeid_flow_map_1hr[(pipe_id, diameter, parallel)] and cost != 0:
                        # print(5)
                        different_pipe_5min.append(pipe_id) 
                    elif speed != pipeif_speed_map_1hr[(pipe_id, diameter, parallel)] and cost != 0:
                        # print(6)
                        different_pipe_5min.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_5min.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)

            if(len(unique_id) > 0):
                print(8)
                different_pipe_5min+=unique_id
                    
            different_pipe_5min = list(dict.fromkeys(different_pipe_5min))  # Remove duplicates    
            
            logger.info("Pipe ID which are diffrent in 5min output file compare to the 1hr output file : "+ str(different_pipe_5min))
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_5min:
                if pipe_id in id_to_cost_map_5min and pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_5min[pipe_id] = id_to_cost_map_1hr[pipe_id] - id_to_cost_map_5min[pipe_id]
                elif pipe_id in id_to_cost_map_5min:
                    difference_cost_pipeid_5min[pipe_id] = -id_to_cost_map_5min[pipe_id]
                elif pipe_id in id_to_cost_map_1hr:
                    difference_cost_pipeid_5min[pipe_id] = id_to_cost_map_1hr[pipe_id]
                else:
                    difference_cost_pipeid_5min[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_5min = dict(sorted(difference_cost_pipeid_5min.items(), key=lambda item: item[1], reverse=True))
            
            #prepare the paragraph for 5min tab with 1hr data
            for pipe_id in sorted_difference_cost_pipeid_5min:
                par_1hrtab_5min += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1hrtab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_1hrtab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")

                par_1hrtab_5min += (f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                
                for i in range(len(pipeData5min["pipeID"])) :
                    if pipeData5min["pipeID"][i] == pipe_id:
                        diameter = pipeData5min["diameter"][i]
                        length = pipeData5min["length"][i]
                        cost = pipeData5min["cost"][i]
                        flow = pipeData5min["flow"][i]
                        speed = pipeData5min["speed"][i]
                        par_1hrtab_5min += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_1hrtab_5min += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")
                par_1hrtab_5min += (f"&nbsp; &nbsp; <b>Difference in cost : {round(sorted_difference_cost_pipeid_5min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 5min tab with 1hr data is stored")
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_5min = dict(sorted(difference_cost_pipeid_5min.items(), key=lambda item: item[1], reverse=False))
            #prepare the paragraph for 1hr tab with 5min data
            for pipe_id in sorted_difference_cost_pipeid_5min:
                par_5mintab_1hr += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>5min Data :</b> <br>")
                for i in range(len(pipeData5min["pipeID"])):
                    if pipeData5min["pipeID"][i] == pipe_id:
                        diameter = pipeData5min["diameter"][i]
                        length = pipeData5min["length"][i]
                        cost = pipeData5min["cost"][i]
                        flow = pipeData5min["flow"][i]
                        speed = pipeData5min["speed"][i]
                        par_5mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")

                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 1hr : {round(id_to_cost_map_5min[pipe_id], 3)}<br><br>")

                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp; <b>1hr Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_5mintab_1hr += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 3)} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 3)}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 3)}<br><br>")
                par_5mintab_1hr += (f"&nbsp; &nbsp; &nbsp;Total cost of 5min : {round(id_to_cost_map_1hr[pipe_id], 3)}<br><br>")
                par_5mintab_1hr += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_5min[pipe_id], 3)}</b><br><br><br>")

            logger.info("Paragraph for 1hr tab with 5min data is stored")
        edge_trace ,edge_text, edge_colors= data_processor.process_edges_for_diameter_graph_plotting_1hr(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1min, different_pipe_5min, exist_pipe_status_1min, exist_pipe_status_5min)
        
        logger.info("Edge trace created for 1hr pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_1hr(G, pos, unique_parallel_pipes, edge_colors, pipeData1min, pipeData5min, different_pipe_1min, different_pipe_5min, exist_pipe_status_1min, exist_pipe_status_5min)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=15,
                color='red'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 1hr pipe data graph")
        
        pipeFig_1hr = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
                        layout=go.Layout(
                            title='Pipe in Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            dragmode='pan'
                        ))
        
        logger.info("Pipe figure created for 1hr graph")
        
        pipeFig_1min = go.Figure()
        pipeFig_5min = go.Figure()
        
        if (pipeData1min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1min)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1min, parrallel_pipes)
            logger.info("Creating 1min graph with 1hr data")
            pipeFig_1min, _, _, _, _, _, _ = self.create_pipe_1min_graph(pos, nodeData1min, pipeData1min, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData5min, pipeData5min, node_data, pipe_data, G1, start+1)


        if (pipeData5min is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData5min)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData5min, parrallel_pipes)
            logger.info("Creating 5min graph with 1hr data")
            pipeFig_5min, _, _, _, _, _, _ = self.create_pipe_5min_graph(pos, nodeData5min, pipeData5min, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData1min, pipeData1min, node_data, pipe_data, G2, start+1)

        return pipeFig_1hr, pipeFig_1min, pipeFig_5min, par_1hrtab_1min, par_1hrtab_5min, par_1mintab_1hr, par_5mintab_1hr
    
    
    

    
    
    
