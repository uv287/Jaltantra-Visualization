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
                    
        logger.info(f"No of pipes added to the graph: {no_of_pipes}")
        logger.info("Multiple same pipe id edges added successfully")
        return G, no_of_pipes
    
    def create_node_1stfile_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData2ndfile, pipeData2ndfile, nodeData3rdfile, pipeData3rdfile, G, start) :
        node_demand_map = {}    
        node_demand_3rdfile={}
        node_demand_2ndfile={}
        data_processor = OutputDataProcessor()
        diffrent_2ndfile = []
        diffrent_3rdfile = []
        demand_difference_2ndfile = {}
        demand_difference_3rdfile = {}
        sorted_demand_difference_2ndfile = {}
        sorted_demand_difference_3rdfile = {}
        para_1stfiletab_2ndfile= ""
        para_1stfiletab_3rdfile= ""
        para_2ndfiletab_1stfile=""
        para_3rdfiletab_1stfile=""
        node_head_map = {}    
        node_head_3rdfile={}
        node_head_2ndfile={}
        head_difference_2ndfile = {}
        head_difference_3rdfile = {}
        sorted_head_difference_2ndfile = {}
        sorted_head_difference_3rdfile = {}
        
        # Create the map for 1stfilenode_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
        
        logger.info(f"1stfile Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = "#AABFF5"
            G.nodes[node]['size'] = 10  # Default size for all nodes
        
        
        if nodeData2ndfile is not None:
            # Create the map for 2ndfileNodeData
            
            for i in range(len(nodeData2ndfile["nodeID"])):
                node_id = nodeData2ndfile["nodeID"][i]
                demand = nodeData2ndfile["Demand"][i]
                head = nodeData2ndfile["Head"][i]
                node_demand_2ndfile[node_id] = demand
                node_head_2ndfile[node_id] = head
            
            logger.info("5 minutes Result File Head Map : "+ str(node_head_2ndfile))
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_2ndfile[node])) or (float(node_head_map[node]) != float(node_head_2ndfile[node])):
                    diffrent_2ndfile.append(node)
                    demand_difference_2ndfile[node]=(float(node_demand_map[node]) - float(node_demand_2ndfile[node]))
                    head_difference_2ndfile[node]=(float(node_head_map[node]) - float(node_head_2ndfile[node]))
            
            logger.info("Diffrent Node ID in 2ndfile output file compare to the 1stfile output file : "+ str(diffrent_2ndfile))
            
            #reverse sort the list with the node
            sorted_head_difference_2ndfile = dict(sorted(head_difference_2ndfile.items(), key=lambda item: item[1], reverse=True))

            para_1stfiletab_2ndfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_2ndfile)}<br>"
            para_1stfiletab_2ndfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_2ndfile.keys())}<br><br>"
            para_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            #traverse the sorted list and create the list
            for node in sorted_head_difference_2ndfile:
                para_1stfiletab_2ndfile +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp; <b>Difference : {round(sorted_head_difference_2ndfile[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Supply : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node]- node_demand_2ndfile[node],3)}</b><br><br>"
                                    )
                para_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 1stfile tab with 2ndfile data is stored")
            #sort the list with the node
            sorted_head_difference_2ndfile = dict(sorted(head_difference_2ndfile.items(), key=lambda item: item[1], reverse=False))
            
            para_2ndfiletab_1stfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_2ndfile)}<br>"
            para_2ndfiletab_1stfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_2ndfile.keys())}<br><br>"
            para_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            for node in sorted_head_difference_2ndfile:                        
                para_2ndfiletab_1stfile +=(f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_2ndfile[node]-node_head_map[node],3)}</b><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_2ndfile[node]-node_demand_map[node],3)}</b><br><br>")
                para_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"

            logger.info("Paragraph for 2ndfile tab with 1stfile data is stored")
            
            for node in G.nodes():
                if node in diffrent_2ndfile:
                    G.nodes[node]['color'] = 'red'  # diffrent demand or head then 2ndfile -> Red
                    G.nodes[node]['size'] = 10
                
        # Create the map for 3rdfileNodeData
        if nodeData3rdfile is not None:
            for i in range(len(nodeData3rdfile["nodeID"])):
                node_id = nodeData3rdfile["nodeID"][i]
                demand = nodeData3rdfile["Demand"][i]
                head = nodeData3rdfile["Head"][i]
                node_demand_3rdfile[node_id] = demand
                node_head_3rdfile[node_id] = head
            
            logger.info("1 hour Result File Head Map : "+ str(node_head_3rdfile))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_3rdfile[node])) or (float(node_head_map[node]) != float(node_head_3rdfile[node])):
                    diffrent_3rdfile.append(node)
                    demand_difference_3rdfile[node]=(float(node_demand_map[node]) - float(node_demand_3rdfile[node]))
                    head_difference_3rdfile[node]=(float(node_head_map[node]) - float(node_head_3rdfile[node]))
            
            logger.info("Diffrent Node ID in 3rdfile output file compare to the 1stfile output file : "+ str(diffrent_3rdfile))
                    
            #sort the list with the node 
            sorted_head_difference_3rdfile = dict(sorted(demand_difference_3rdfile.items(), key=lambda item: item[1], reverse=True))
            
            para_1stfiletab_3rdfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_3rdfile)}<br>"
            para_1stfiletab_3rdfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_3rdfile.keys())}<br><br>"
            para_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            for node in sorted_demand_difference_3rdfile:
                para_1stfiletab_3rdfile += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_3rdfile[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 3rdfile : {round(node_demand_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_demand_difference_3rdfile[node],3)}</b><br><br>"
                                    )
                para_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 1stfile tab with 3rdfile data is stored")
            
            sorted_head_difference_3rdfile = dict(sorted(demand_difference_3rdfile.items(), key=lambda item: item[1], reverse=False))
            
            para_3rdfiletab_1stfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_3rdfile)}<br>"
            para_3rdfiletab_1stfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_3rdfile.keys())}<br><br>"
            para_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
                
            for node in sorted_head_difference_3rdfile:
                para_3rdfiletab_1stfile += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_3rdfile[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 3rdfile : {round(node_demand_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 1stfile : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_3rdfile[node]-node_demand_map[node],3)}</b><br><br><br>")
                para_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 3rdfile tab with 1stfile data is stored")
            
            for node in G.nodes():
                if node in diffrent_3rdfile :
                    G.nodes[node]['color'] = 'green'    # diffrent demand or head then 3rdfile -> Green
                    G.nodes[node]['size'] = 10

        # if the node is in the both the list
        if nodeData2ndfile is not None and nodeData3rdfile is not None:
            for node in G.nodes():
                if node in diffrent_2ndfile and node in diffrent_3rdfile:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 10
                
        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_1stfile_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_2ndfile, node_head_2ndfile, node_demand_3rdfile, node_head_3rdfile, diffrent_2ndfile, diffrent_3rdfile)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            textfont=dict(
                size=15,
                color='#222222'
            ),
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
        
        logger.info("Node trace created for 1stfile graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='#bbbbbb')
        )
        
        logger.info("Edge trace created for 1stfile graph")
        
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
                color='#939393'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 1stfile graph")
        
        nodeFig_1stfile = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
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
        
        nodeFig_1stfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        nodeFig_2ndfile = go.Figure()
        nodeFig_3rdfile = go.Figure()
        
        if (nodeData2ndfile is not None) and (start == 0):
            # print("Hello World")
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData2ndfile)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData2ndfile, parrallel_pipes)
            logger.info("Creating 2ndfile graph with 1stfile data")
            nodeFig_2ndfile, _, _, _, _, _, _ = self.create_node_2ndfile_graph(node_pos, nodeData2ndfile, pipeData2ndfile, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData3rdfile, pipeData3rdfile, G1, start+1)

        if (nodeData3rdfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData3rdfile)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData3rdfile, parrallel_pipes)
            logger.info("Creating 3rdfile graph with 1stfile data")
            nodeFig_3rdfile, _, _, _, _, _, _ = self.create_node_3rdfile_graph(node_pos, nodeData3rdfile, pipeData3rdfile, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData2ndfile, pipeData2ndfile, G2, start+1)
        
        return nodeFig_1stfile, nodeFig_2ndfile, nodeFig_3rdfile, para_1stfiletab_2ndfile, para_1stfiletab_3rdfile, para_2ndfiletab_1stfile, para_3rdfiletab_1stfile
    
    
    #node graph for the 5 min tab
    def create_node_2ndfile_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, nodeData3rdfile, pipeData3rdfile, G, start) :
        node_demand_map = {}    
        node_demand_3rdfile={}
        node_demand_1stfile={}
        data_processor = OutputDataProcessor()
        diffrent_1stfile = [] #for nodes with different demand or head in 1stfile
        diffrent_3rdfile = [] #for nodes with different demand or head in 3rdfile
        demand_difference_1stfile = {} #difference in demand in 1stfile
        demand_difference_3rdfile = {} #difference in demand in 3rdfile
        sorted_demand_difference_1stfile = {} #sorted difference in demand in 1stfile
        sorted_demand_difference_3rdfile = {} #sorted difference in demand in 3rdfile
        para_2ndfiletab_1stfile= "" #Paragraph for 2ndfile tab with 1stfile data
        para_2ndfiletab_3rdfile= ""  #Paragraph for 2ndfile tab with 3rdfile data
        para_1stfiletab_2ndfile=""  #Paragraph for 1stfile tab with 2ndfile data
        para_3rdfiletab_2ndfile=""   #Paragraph for 3rdfile tab with 2ndfile data
        node_head_map = {}    #2ndfile node to head map
        node_head_3rdfile={}      #3rdfile node to head map
        node_head_1stfile={}    #1stfile node to head map
        head_difference_1stfile = {} #difference in head in 1stfile
        head_difference_3rdfile = {}  #difference in head in 3rdfile
        sorted_head_difference_1stfile = {} #sorted difference in head in 1stfile
        sorted_head_difference_3rdfile = {} #sorted difference in head in 3rdfile
        
        # Create the map for 2ndfile node_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
            
        logger.info(f"2ndfile Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = "#AABFF5"
            G.nodes[node]['size'] = 10  # Default size for all nodes
        
        # print("hello from 5 min")
        if nodeData1stfile is not None:
            # Create the map for 2ndfileNodeData
            for i in range(len(nodeData1stfile["nodeID"])):
                node_id = nodeData1stfile["nodeID"][i]
                demand = nodeData1stfile["Demand"][i]
                head = nodeData1stfile["Head"][i]
                node_demand_1stfile[node_id] = demand
                node_head_1stfile[node_id] = head
            
            logger.info("1 minute Result File Head Map : "+ str(node_head_1stfile))
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1stfile[node])) or (float(node_head_map[node]) != float(node_head_1stfile[node])):
                    diffrent_1stfile.append(node)
                    demand_difference_1stfile[node]=(float(node_demand_map[node]) - float(node_demand_1stfile[node]))
                    head_difference_1stfile[node]=(float(node_head_map[node]) - float(node_head_1stfile[node]))
                
            
            logger.info("Diffrent Node ID in 1stfile output file compare to the 2ndfile output file : "+ str(diffrent_1stfile))
            
            #reverse sort the list
            sorted_head_difference_1stfile = dict(sorted(head_difference_1stfile.items(), key=lambda item: item[1], reverse=True))
            
            para_2ndfiletab_1stfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_1stfile)}<br>"
            para_2ndfiletab_1stfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_1stfile.keys())}<br><br>"
            para_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            #traverse the sorted list and create the list 
            for node in sorted_head_difference_1stfile:
                para_2ndfiletab_1stfile +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1stfile[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node] - node_demand_1stfile[node],3)}</b><br><br><br>"
                                    )
                para_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 2ndfile tab with 1stfile data is stored")
            #sort the list with the node
            sorted_head_difference_1stfile = dict(sorted(head_difference_1stfile.items(), key=lambda item: item[1], reverse=False))
            
            para_1stfiletab_2ndfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_1stfile)}<br>"
            para_1stfiletab_2ndfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_1stfile.keys())}<br><br>"
            para_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            for node in sorted_head_difference_1stfile:                        
                para_1stfiletab_2ndfile +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_1stfile[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_1stfile[node]-node_demand_map[node],3)}</b><br><br><br>")
                para_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            logger.info("Paragraph for 1stfile tab with 2ndfile data is stored")
            
            for node in G.nodes():
                if node in diffrent_1stfile:
                    G.nodes[node]['color'] = 'red'  # diffrent demand or head then 1stfile -> Red
                    G.nodes[node]['size'] = 10
                
        # Create the map for 3rdfileNodeData
        if nodeData3rdfile is not None:
            for i in range(len(nodeData3rdfile["nodeID"])):
                node_id = nodeData3rdfile["nodeID"][i]
                demand = nodeData3rdfile["Demand"][i]
                head = nodeData3rdfile["Head"][i]
                node_demand_3rdfile[node_id] = demand
                node_head_3rdfile[node_id] = head
            
            logger.info("1 hour Result File Head Map : "+ str(node_head_3rdfile))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_3rdfile[node])) or (float(node_head_map[node]) != float(node_head_3rdfile[node])):
                    diffrent_3rdfile.append(node)
                    demand_difference_3rdfile[node]=(float(node_demand_map[node]) - float(node_demand_3rdfile[node]))
                    head_difference_3rdfile[node]=(float(node_head_map[node]) - float(node_head_3rdfile[node]))
            
            logger.info("Diffrent Node ID in 3rdfile output file compare to the 2ndfile output file : "+ str(diffrent_3rdfile))
                    
            #sort the list with the node 
            sorted_head_difference_3rdfile = dict(sorted(head_difference_3rdfile.items(), key=lambda item: item[1], reverse=True))
            
            para_2ndfiletab_3rdfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_3rdfile)}<br>"
            para_2ndfiletab_3rdfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_3rdfile.keys())}<br><br>"
            para_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
            for node in sorted_demand_difference_3rdfile:
                para_2ndfiletab_3rdfile += (f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_3rdfile[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 3rdfile : {round(node_demand_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_demand_difference_3rdfile[node],3)}</b><br><br><br>"
                                    )
                para_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 2ndfile tab with 3rdfile data is stored")

            sorted_head_difference_3rdfile = dict(sorted(head_difference_3rdfile.items(), key=lambda item: item[1], reverse=False))

            para_3rdfiletab_2ndfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_3rdfile)}<br>"
            para_3rdfiletab_2ndfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_3rdfile.keys())}<br><br>"
            para_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            for node in sorted_head_difference_3rdfile:
                para_3rdfiletab_2ndfile += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_head_3rdfile[node]-node_head_map[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 3rdfile : {round(node_demand_3rdfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 2ndfile : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_3rdfile[node]-node_demand_map[node],3)}</b><br><br><br>")
                para_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"

            for node in G.nodes():
                if node in diffrent_3rdfile :
                    G.nodes[node]['color'] = 'yellow'    # diffrent demand or head then 3rdfile -> yellow
                    G.nodes[node]['size'] = 10

        # if the node is in the both the list
        if nodeData1stfile is not None and nodeData3rdfile is not None:
            for node in G.nodes():
                if node in diffrent_1stfile and node in diffrent_3rdfile:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 10
                
        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_2ndfile_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_1stfile, node_head_1stfile, node_demand_3rdfile, node_head_3rdfile, diffrent_1stfile, diffrent_3rdfile)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            textfont=dict(
                size=15,
                color='#222222'
            ),
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
        
        logger.info("Node trace created for 2ndfile graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color="#bbbbbb" )
        )
        
        logger.info("Edge trace created for 2ndfile graph")
        
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
                color='#939393'  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 2ndfile graph")
        
        nodeFig_2ndfile = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
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
        
        nodeFig_2ndfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        logger.info("Node figure created for 2ndfile graph")
        
        nodeFig_1stfile = go.Figure()
        nodeFig_3rdfile = go.Figure()
        
        #start is to remove the recusrsion
        if (nodeData1stfile is not None) and (start == 0) :
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1stfile)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData1stfile, parrallel_pipes)
            logger.info("Creating 1stfile graph with 2ndfile data")
            nodeFig_1stfile, _, _, _, _, _, _ = self.create_node_1stfile_graph(node_pos, nodeData1stfile, pipeData1stfile, parrallel_pipes, mainNodeData, mainpipe, node_data, pipe_data, nodeData3rdfile, pipeData3rdfile, G1, start+1)

        if (nodeData3rdfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData3rdfile)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData3rdfile, parrallel_pipes)
            logger.info("Creating 3rdfile graph with 2ndfile data")
            nodeFig_3rdfile, _, _, _, _, _, _ = self.create_node_3rdfile_graph(node_pos, nodeData3rdfile, pipeData3rdfile, parrallel_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, node_data, pipe_data, G2, start+1)

        return nodeFig_2ndfile, nodeFig_1stfile, nodeFig_3rdfile, para_2ndfiletab_1stfile, para_2ndfiletab_3rdfile, para_1stfiletab_2ndfile, para_3rdfiletab_2ndfile
    
    #Node graph for the 3rdfile tab
    def create_node_3rdfile_graph(self, node_pos, node_data, pipe_data, unique_parallel_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, nodeData2ndfile, pipeData2ndfile, G, start) :
        node_demand_map = {}    
        node_demand_2ndfile={}
        node_demand_1stfile={}
        data_processor = OutputDataProcessor()
        diffrent_1stfile = [] #for nodes with different demand or head in 1stfile
        diffrent_2ndfile = [] #for nodes with different demand or head in 2ndfile
        demand_difference_1stfile = {} #difference in demand in 1stfile
        demand_difference_2ndfile = {} #difference in demand in 3rdfile
        sorted_demand_difference_1stfile = {} #sorted difference in demand in 1stfile
        sorted_demand_difference_2ndfile = {} #sorted difference in demand in 2ndfile
        para_3rdfiletab_1stfile= "" #Paragraph for 3rdfile tab with 1stfile data
        para_3rdfiletab_2ndfile= ""  #Paragraph for 3rdfile tab with 2ndfile data
        para_1stfiletab_3rdfile=""  #Paragraph for 1stfile tab with 3rdfile data
        para_2ndfiletab_3rdfile=""   #Paragraph for 2ndfile tab with 3rdfile data
        node_head_map = {}    #2ndfile node to head map
        node_head_2ndfile={}      #3rdfile node to head map
        node_head_1stfile={}    #1stfile node to head map
        head_difference_1stfile = {} #difference in head in 1stfile
        head_difference_2ndfile = {}  #difference in head in 3rdfile
        sorted_head_difference_1stfile = {} #sorted difference in head in 1stfile
        sorted_head_difference_2ndfile = {} #sorted difference in head in 3rdfile
        
        # Create the map for 3rdfile node_data
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            demand = node_data["Demand"][i]
            head = node_data["Head"][i]
            node_demand_map[node_id] = demand
            node_head_map[node_id] = head
            
        logger.info(f"3rdfile Graph Head Map : " + str(node_head_map))
        
        for node in G.nodes():
            G.nodes[node]['color'] = "#AABFF5"
            G.nodes[node]['size'] = 10  # Default size for all nodes
        
        
        if nodeData1stfile is not None:
            # Create the map for 2ndfileNodeData
            for i in range(len(nodeData1stfile["nodeID"])):
                node_id = nodeData1stfile["nodeID"][i]
                demand = nodeData1stfile["Demand"][i]
                head = nodeData1stfile["Head"][i]
                node_demand_1stfile[node_id] = demand
                node_head_1stfile[node_id] = head
            
            logger.info("1 minute Result File Head Map : "+ str(node_head_1stfile))   
                
            #Lists to store the nodes with different demands and heads
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_1stfile[node])) or (float(node_head_map[node]) != float(node_head_1stfile[node])):
                    diffrent_1stfile.append(node)
                    demand_difference_1stfile[node]=(float(node_demand_map[node]) - float(node_demand_1stfile[node]))
                    head_difference_1stfile[node]=(float(node_head_map[node]) - float(node_head_1stfile[node]))
            
            logger.info("Diffrent Node ID in 1stfile output file compare to the 3rdfile output file : "+ str(diffrent_1stfile))
            
            #reverse sort the list
            sorted_head_difference_1stfile = dict(sorted(head_difference_1stfile.items(), key=lambda item: item[1], reverse=True))
            
            para_3rdfiletab_1stfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_1stfile)}<br>"
            para_3rdfiletab_1stfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_1stfile.keys())}<br><br>"
            para_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            #traverse the sorted list and create the list 
            for node in sorted_head_difference_1stfile:
                para_3rdfiletab_1stfile +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(sorted_head_difference_1stfile[node],3)}</b><br><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 3rdfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_demand_map[node]- node_demand_1stfile[node],3)}</b><br><br>"
                                    )
                para_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 3rdfile tab with 1stfile data is stored")
            #sort the list with the node
            sorted_head_difference_1stfile = dict(sorted(head_difference_1stfile.items(), key=lambda item: item[1], reverse=False))
            
            para_1stfiletab_3rdfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_1stfile)}<br>"
            para_1stfiletab_3rdfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_1stfile.keys())}<br><br>"
            para_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            for node in sorted_head_difference_1stfile:                        
                para_1stfiletab_3rdfile +=(f"<b>Node : {node}</b><br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 1stfile : {round(node_head_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;<b>Difference : {round(node_head_1stfile[node]-node_head_map[node],3)}</b><br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 1stfile : {round(node_demand_1stfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 3rdfile : {round(node_demand_map[node],3)}<br>"
                                        f"&nbsp;&nbsp;<b>Difference : {round(node_demand_1stfile[node]-node_demand_map[node],3)}</b><br><br><br>")
                para_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 1stfile tab with 3rdfile data is stored")
            
            for node in G.nodes():
                if node in diffrent_1stfile:
                    G.nodes[node]['color'] = 'green'  # diffrent demand or head then 1stfile -> Green
                    G.nodes[node]['size'] = 10
                
        # Create the map for 3rdfileNodeData
        if nodeData2ndfile is not None:
            for i in range(len(nodeData2ndfile["nodeID"])):
                node_id = nodeData2ndfile["nodeID"][i]
                demand = nodeData2ndfile["Demand"][i]
                head = nodeData2ndfile["Head"][i]
                node_demand_2ndfile[node_id] = demand
                node_head_2ndfile[node_id] = head
            
            logger.info("5 minute Result File Head Map : "+ str(node_head_2ndfile))
            
            #Lists to store the nodes with different demands
            for node in node_demand_map:
                if (float(node_demand_map[node]) != float(node_demand_2ndfile[node])) or (float(node_head_map[node]) != float(node_head_2ndfile[node])):
                    diffrent_2ndfile.append(node)
                    demand_difference_2ndfile[node]=(float(node_demand_map[node]) - float(node_demand_2ndfile[node]))
                    head_difference_2ndfile[node]=(float(node_head_map[node]) - float(node_head_2ndfile[node]))
            
            logger.info("Diffrent Node ID in 2ndfile output file compare to the 3rdfile output file : "+ str(diffrent_2ndfile))
                    
            #sort the list with the node 
            sorted_head_difference_2ndfile = dict(sorted(head_difference_2ndfile.items(), key=lambda item: item[1], reverse=True))
            
            para_3rdfiletab_2ndfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_2ndfile)}<br>"
            para_3rdfiletab_2ndfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_2ndfile.keys())}<br><br>"
            para_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            for node in sorted_head_difference_2ndfile:
                para_3rdfiletab_2ndfile += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(sorted_head_difference_2ndfile[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Supply in 3rdfile : {round(node_demand_map[node],3)}<br>" 
                                            f"&nbsp;&nbsp;&nbsp;Supply in 2ndfile : {round(node_demand_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_demand_map[node]-node_demand_2ndfile[node],3)}<br><br><br>"
                                    )
                para_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 3rdfile tab with 2ndfile data is stored")
            
            sorted_head_difference_2ndfile = dict(sorted(head_difference_2ndfile.items(), key=lambda item: item[1], reverse=False))
            
            para_2ndfiletab_3rdfile += f"Total Nodes with Head or Supply Difference : {len(sorted_head_difference_2ndfile)}<br>"
            para_2ndfiletab_3rdfile += f"Nodes ID : {', '.join(str(k) for k in sorted_head_difference_2ndfile.keys())}<br><br>"
            para_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
                
            for node in sorted_head_difference_2ndfile:
                para_2ndfiletab_3rdfile += (f"Node : {node}<br>"
                                        f"&nbsp; &nbsp; Head : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 2ndfile : {round(node_head_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Head in 3rdfile : {round(node_head_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Difference : {round(node_head_2ndfile[node]-node_head_map[node],3)}<br><br>"
                                        f"&nbsp; &nbsp; Demand : <br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 2ndfile : {round(node_demand_2ndfile[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;Demand in 3rdfile : {round(node_demand_map[node],3)}<br>"
                                            f"&nbsp;&nbsp;&nbsp;<b>Difference : {round(node_demand_2ndfile[node]-node_demand_map[node],3)}</b><br><br><br>")
                para_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"

            logger.info("Paragraph for 2ndfile tab with 3rdfile data is stored")
            
            for node in G.nodes():
                if node in diffrent_2ndfile :
                    G.nodes[node]['color'] = 'yellow'    # diffrent demand or head then 3rdfile -> yellow
                    G.nodes[node]['size'] = 10

        # if the node is in the both the list
        if nodeData1stfile is not None and nodeData2ndfile is not None:
            for node in G.nodes():
                if node in diffrent_1stfile and node in diffrent_2ndfile:
                    G.nodes[node]['color'] = 'brown'  # diffrent supply or head in both -> Brown
                    G.nodes[node]['size'] = 10

        node_x, node_y, node_text, node_hovertext, node_colors, node_size = data_processor.process_nodes_3rdfile_plotting(G, node_pos, node_demand_map, node_head_map, node_demand_1stfile, node_head_1stfile, node_demand_2ndfile, node_head_2ndfile, diffrent_1stfile, diffrent_2ndfile)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            textfont=dict(
                size=15,
                color='#222222'
            ),
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
        
        logger.info("Node trace created for 3rdfile graph")
        
        edge_x, edge_y, edge_text, edge_hovertext = data_processor.process_edges_for_plotting(G, node_pos, pipe_data, unique_parallel_pipes)
        
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='#bbbbbb')
        )
        
        logger.info("Edge trace created for 3rdfile graph")
        
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
                color="#939393"  # You can change the color as needed
            )
        )
        
        logger.info("Edge label trace created for 3rdfile graph")
        
        nodeFig_3rdfile = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
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
        
        nodeFig_3rdfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        logger.info("Node figure created for 3rdfile graph")
        nodeFig_1stfile = go.Figure()
        nodeFig_2ndfile = go.Figure()
        
        
        if (nodeData1stfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1stfile)
            G1 = self.create_graph_with_parallel_edges(node_pos, pipeData1stfile, parrallel_pipes)
            logger.info("Creating 1stfile graph with 3rdfile data")
            nodeFig_1stfile, _, _, _, _, _, _ = self.create_node_1stfile_graph(node_pos, nodeData1stfile, pipeData1stfile, parrallel_pipes, mainNodeData, mainpipe, nodeData2ndfile, pipeData2ndfile, node_data, pipe_data, G1, start+1)
        
        if (nodeData2ndfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData2ndfile)
            G2 = self.create_graph_with_parallel_edges(node_pos, pipeData2ndfile, parrallel_pipes)
            logger.info("Creating 2ndfile graph with 3rdfile data")
            nodeFig_2ndfile, _, _, _, _, _, _ = self.create_node_2ndfile_graph(node_pos, nodeData2ndfile, pipeData2ndfile, parrallel_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, node_data, pipe_data, G2, start+1)

        return nodeFig_3rdfile, nodeFig_1stfile, nodeFig_2ndfile, para_3rdfiletab_1stfile, para_3rdfiletab_2ndfile, para_1stfiletab_3rdfile, para_2ndfiletab_3rdfile
    
    
    def create_pipe_1stfile_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData2ndfile, pipeData2ndfile, nodeData3rdfile, pipeData3rdfile, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_1stfiletab_2ndfile = ""  # Paragraph for 1stfile tab with 2ndfile data
        par_1stfiletab_3rdfile = ""  # Paragraph for 1stfile tab with 3rdfile data
        par_2ndfiletab_1stfile = ""  # Paragraph for 2ndfile tab with 1stfile data
        par_3rdfiletab_1stfile = ""  # Paragraph for 3rdfile tab with 1stfile data
        id_to_cost_map_1stfile = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"1stfile Graph Head Map : " + str(node_head_map))
        
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
                size=10,
                color="#AABFF5",  # Color for all nodes
                line=dict(width=1, color='black')
            )
        )
        logger.info("Node trace created for 1stfile graph")
        
        
        different_pipe_2ndfile = []
        different_pipe_3rdfile = []
        pipeid_length_map_1stfile ={}
        pipeid_cost_map_1stfile={}
        pipeid_flow_map_1stfile ={}
        pipeif_speed_map_1stfile={}
        difference_cost_pipeid_2ndfile ={}
        difference_cost_pipeid_3rdfile ={}
        id_to_cost_map_3rdfile = defaultdict(float)  # Map to store pipeID to cost for 3rdfile data
        id_to_cost_map_2ndfile = defaultdict(float)  # Map to store pipeID to cost for 2ndfile data
        exist_pipe_status_2ndfile = {} #parallel pipe flow and speed is same or not
        exist_pipe_status_3rdfile = {}
        flow_parallel = {}#for the static pipe which cost is zero 
        speed_parallel= {} #for the static pipe which cost is zero
        unique_pipeid_1stfile= []
        sorted_difference_cost_pipeid_2ndfile = {}
        sorted_difference_cost_pipeid_3rdfile = {}
        
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
            
            if pipe_id not in unique_pipeid_1stfile:
                unique_pipeid_1stfile.append(pipe_id)
            
            pipeid_length_map_1stfile[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_1stfile[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_1stfile[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_1stfile[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_1stfile[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("1 minute Result File Pipe ID to Cost Map : " + str(id_to_cost_map_1stfile))
        
        if pipeData2ndfile is not None:
            unique_id=unique_pipeid_1stfile.copy()  # Create a copy of unique_pipeid_1stfile to track unique pipe IDs
            for i in range(len(pipeData2ndfile["pipeID"])):
                pipe_id = pipeData2ndfile["pipeID"][i]
                diameter = pipeData2ndfile["diameter"][i]
                length = pipeData2ndfile["length"][i]
                parallel = pipeData2ndfile["parallel"][i]
                cost = pipeData2ndfile["cost"][i]
                flow = pipeData2ndfile["flow"][i]
                speed = pipeData2ndfile["speed"][i]
                
                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_2ndfile[pipe_id] = False
                    
                if cost!=0 :
                    id_to_cost_map_2ndfile[pipe_id] += cost  # Aggregate cost for each pipeID in 2ndfile data
                    
                    
                    
                    # Find the pipe id which are diffrent from 2ndfile to 1stfile
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1stfile:
                        different_pipe_2ndfile.append(pipe_id)
                    elif length != pipeid_length_map_1stfile[(pipe_id, diameter, parallel)]:
                        different_pipe_2ndfile.append(pipe_id)
                    elif cost != pipeid_cost_map_1stfile[(pipe_id, diameter, parallel)]:
                        different_pipe_2ndfile.append(pipe_id)
                    elif flow != pipeid_flow_map_1stfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_1stfile[(pipe_id, diameter, parallel)])
                        if flowdiff > 0.01:
                            different_pipe_2ndfile.append(pipe_id) 
                    elif speed != pipeif_speed_map_1stfile[(pipe_id, diameter, parallel)]:
                        speeddiff = abs(speed - pipeif_speed_map_1stfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            different_pipe_2ndfile.append(pipe_id)
                    else:   
                        None
                    
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_2ndfile.append(pipe_id)  # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if(pipe_id ==2):
                    print(f"No of pipe ID in 2 is : {no_of_pipes[pipe_id]}")
                
                if pipe_id not in unique_pipeid_1stfile:
                    different_pipe_2ndfile.append(pipe_id)
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
            
            if(len(unique_id) > 0):
                different_pipe_2ndfile+=unique_id    
                
            different_pipe_2ndfile= list(dict.fromkeys(different_pipe_2ndfile))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 2ndfile output file compare to the 1stfile output file : "+ str(different_pipe_2ndfile))
            
            #find the diffrance cost between one minute and five minute
            for pipe_id in different_pipe_2ndfile:
                if pipe_id in id_to_cost_map_1stfile and pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = id_to_cost_map_1stfile[pipe_id] - id_to_cost_map_2ndfile[pipe_id]
                elif pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = -id_to_cost_map_2ndfile[pipe_id]
                elif pipe_id in id_to_cost_map_1stfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = id_to_cost_map_1stfile[pipe_id]
                else:
                    difference_cost_pipeid_2ndfile[pipe_id] = 0
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_2ndfile = dict(sorted(difference_cost_pipeid_2ndfile.items(), key=lambda item: item[1], reverse=True))
            
            par_1stfiletab_2ndfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_2ndfile)}<br>"
            par_1stfiletab_2ndfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_2ndfile.keys())}<br><br>"
            par_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            for pipe_id in sorted_difference_cost_pipeid_2ndfile:
                par_1stfiletab_2ndfile += (f"Pipe ID : <b>{pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1stfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")

                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                
                for i in range(len(pipeData2ndfile["pipeID"])):
                    if pipeData2ndfile["pipeID"][i] == pipe_id:
                        diameter = pipeData2ndfile["diameter"][i]
                        length = pipeData2ndfile["length"][i]
                        cost = pipeData2ndfile["cost"][i]
                        flow = pipeData2ndfile["flow"][i]
                        speed = pipeData2ndfile["speed"][i]
                        par_1stfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")
                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})</b><br><br><br>")
                par_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 1stfile tab with 2ndfile data is stored")
                
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_2ndfile = dict(sorted(difference_cost_pipeid_2ndfile.items(), key=lambda item: item[1], reverse=False))
            
            par_2ndfiletab_1stfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_2ndfile)}<br>"
            par_2ndfiletab_1stfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_2ndfile.keys())}<br><br>"
            par_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            for pipe_id in sorted_difference_cost_pipeid_2ndfile:
                par_2ndfiletab_1stfile += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                for i in range(len(pipeData2ndfile["pipeID"])):
                    if pipeData2ndfile["pipeID"][i] == pipe_id:
                        diameter = pipeData2ndfile["diameter"][i]
                        length = pipeData2ndfile["length"][i]
                        cost = pipeData2ndfile["cost"][i]
                        flow = pipeData2ndfile["flow"][i]
                        speed = pipeData2ndfile["speed"][i]
                        par_2ndfiletab_1stfile += ( 
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,} (<br><br>")
                
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_2ndfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br>")
                
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_2ndfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})</b><br><br><br>")
                par_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 2ndfile tab with 1stfile data is stored")

        if pipeData3rdfile is not None:
            unique_id = unique_pipeid_1stfile.copy()  # Create a copy of unique_pipeid_1stfile to track unique pipe IDs
            for i in range(len(pipeData3rdfile["pipeID"])):
                pipe_id = pipeData3rdfile["pipeID"][i]
                diameter = pipeData3rdfile["diameter"][i]
                length = pipeData3rdfile["length"][i]
                parallel = pipeData3rdfile["parallel"][i]
                cost = pipeData3rdfile["cost"][i]
                flow = pipeData3rdfile["flow"][i]
                speed = pipeData3rdfile["speed"][i]
                
                id_to_cost_map_3rdfile[pipe_id] += cost  # Aggregate cost for each pipeID in 3rdfile data

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_3rdfile[pipe_id] = False

                    # Find the pipe id which are diffrent from 1stfile to 3rdfile
                if cost!=0 :
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_1stfile:
                        different_pipe_3rdfile.append(pipe_id)
                    elif length != pipeid_length_map_1stfile[(pipe_id, diameter, parallel)]:
                        different_pipe_3rdfile.append(pipe_id)
                    elif cost != pipeid_cost_map_1stfile[(pipe_id, diameter, parallel)]:
                        different_pipe_3rdfile.append(pipe_id)
                    elif flow != pipeid_flow_map_1stfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_1stfile[(pipe_id, diameter, parallel)])
                        if flowdiff > 0.01:
                            different_pipe_3rdfile.append(pipe_id) 
                    elif speed != pipeif_speed_map_1stfile[(pipe_id, diameter, parallel)]:
                        speeddiff = abs(speed - pipeif_speed_map_1stfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            different_pipe_3rdfile.append(pipe_id)
                    else:   
                        None
                
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_3rdfile.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if pipe_id not in unique_pipeid_1stfile:
                    different_pipe_3rdfile.append(pipe_id)
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
                    
            if(len(unique_id) > 0):
                different_pipe_3rdfile+=unique_id

            different_pipe_3rdfile = list(dict.fromkeys(different_pipe_3rdfile))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 3rdfile output file compare to the 1stfile output file : "+ str(different_pipe_3rdfile))

            
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_3rdfile:
                if pipe_id in id_to_cost_map_1stfile and pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = id_to_cost_map_1stfile[pipe_id] - id_to_cost_map_3rdfile[pipe_id]
                elif pipe_id in id_to_cost_map_1stfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = id_to_cost_map_1stfile[pipe_id]
                elif pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = -id_to_cost_map_3rdfile[pipe_id]
                else:
                    difference_cost_pipeid_3rdfile[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_3rdfile = dict(sorted(difference_cost_pipeid_3rdfile.items(), key=lambda item: item[1], reverse=True))
            
            par_1stfiletab_3rdfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_3rdfile)}<br>"
            par_1stfiletab_3rdfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_3rdfile.keys())}<br><br>"
            par_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            #prepare the paragraph for 1stfile tab with 3rdfile data
            for pipe_id in sorted_difference_cost_pipeid_3rdfile:
                par_1stfiletab_3rdfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1stfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")

                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                
                for i in range(len(pipeData3rdfile["pipeID"])):
                    if pipeData3rdfile["pipeID"][i] == pipe_id:
                        diameter = pipeData3rdfile["diameter"][i]
                        length = pipeData3rdfile["length"][i]
                        cost = pipeData3rdfile["cost"][i]
                        flow = pipeData3rdfile["flow"][i]
                        speed = pipeData3rdfile["speed"][i]
                        par_1stfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")
                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_3rdfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})</b><br><br><br>")
                par_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 1stfile tab with 3rdfile data is stored")

            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_3rdfile = dict(sorted(difference_cost_pipeid_3rdfile.items(), key=lambda item: item[1], reverse=False))
            
            
            par_3rdfiletab_1stfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_3rdfile)}<br>"
            par_3rdfiletab_1stfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_3rdfile.keys())}<br><br>"
            par_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
            for pipe_id in sorted_difference_cost_pipeid_3rdfile:
                par_3rdfiletab_1stfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                for i in range(len(pipeData3rdfile["pipeID"])):
                    if pipeData3rdfile["pipeID"][i] == pipe_id:
                        diameter = pipeData3rdfile["diameter"][i]
                        length = pipeData3rdfile["length"][i]
                        cost = pipeData3rdfile["cost"][i]
                        flow = pipeData3rdfile["flow"][i]
                        speed = pipeData3rdfile["speed"][i]
                        par_3rdfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")

                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_3rdfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")
                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_3rdfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id], id_to_cost_map_3rdfile[pipe_id])})</b><br><br>")
                par_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 3rdfile tab with 1stfile data is stored")
        
        edge_trace ,edge_text, edge_colors, edge_text_color= data_processor.process_edges_for_diameter_graph_plotting_1stfile(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_2ndfile, different_pipe_3rdfile, exist_pipe_status_2ndfile, exist_pipe_status_3rdfile)
        
        logger.info("Edge trace created for 1stfile pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_1stfile(G, pos, unique_parallel_pipes, edge_colors, pipeData2ndfile, pipeData3rdfile, different_pipe_2ndfile, different_pipe_3rdfile, exist_pipe_status_2ndfile, exist_pipe_status_3rdfile, id_to_cost_map_1stfile, id_to_cost_map_2ndfile, id_to_cost_map_3rdfile, sorted_difference_cost_pipeid_2ndfile,sorted_difference_cost_pipeid_3rdfile)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=17.5,
                color=edge_text_color,  # You can change the color as needed
                family='Arial Black'
            )
        )
        
        logger.info("Edge label trace created for 1stfile pipe data graph")
        
        pipeFig_1stfile = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
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
        
        pipeFig_1stfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        logger.info("Pipe figure created for 1stfile graph")
        
        pipeFig_2ndfile = go.Figure()
        pipeFig_3rdfile = go.Figure()
        
        if (pipeData2ndfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData2ndfile)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData2ndfile, parrallel_pipes)
            logger.info("Creating 2ndfile graph with 3rdfile data")
            pipeFig_2ndfile, _, _, _, _, _, _ = self.create_pipe_2ndfile_graph(pos, nodeData2ndfile, pipeData2ndfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData3rdfile, pipeData3rdfile, G1, start+1)
            
        
        if (pipeData3rdfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData3rdfile)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData3rdfile, parrallel_pipes)
            logger.info("Creating 3rdfile graph with 1stfile data")
            pipeFig_3rdfile, _, _, _, _, _, _ = self.create_pipe_3rdfile_graph(pos, nodeData3rdfile, pipeData3rdfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData2ndfile, pipeData2ndfile, G2, start+1)
        
        return pipeFig_1stfile, pipeFig_2ndfile, pipeFig_3rdfile, par_1stfiletab_2ndfile, par_1stfiletab_3rdfile, par_2ndfiletab_1stfile, par_3rdfiletab_1stfile
    

    def create_pipe_2ndfile_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, nodeData3rdfile, pipeData3rdfile, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_2ndfiletab_1stfile = ""  # Paragraph for 2ndfile tab with 1stfile data
        par_2ndfiletab_3rdfile = ""  # Paragraph for 2ndfile tab with 3rdfile data
        par_1stfiletab_2ndfile = ""  # Paragraph for 2ndfile tab with 2ndfile data
        par_3rdfiletab_2ndfile = ""  # Paragraph for 3rdfile tab with 2ndfile data
        id_to_cost_map_2ndfile = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"2ndfile Graph Head Map : " + str(node_head_map))
        
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
                size=10,
                color="#AABFF5", 
                line=dict(width=1, color='black')
            )
        )
        
        logger.info("Node trace created for 2ndfile graph")
        
        
        different_pipe_1stfile = []
        different_pipe_3rdfile = []
        pipeid_length_map_2ndfile ={}
        pipeid_cost_map_2ndfile={}
        pipeid_flow_map_2ndfile ={}
        pipeif_speed_map_2ndfile={}
        difference_cost_pipeid_1stfile ={}
        difference_cost_pipeid_3rdfile ={}
        exist_pipe_status_1stfile = {} #static parallel pipe flow and speed is same or not
        exist_pipe_status_3rdfile = {} #static parallel pipe flow and speed is same or not
        flow_parallel = {} #for the static pipe which cost is zero 
        speed_parallel= {}  #for the static pipe which cost is zero
        unique_pipeid_2ndfile= []
        sorted_difference_cost_pipeid_1stfile = {}
        sorted_difference_cost_pipeid_3rdfile = {}
        id_to_cost_map_3rdfile = defaultdict(float)  # Map to store pipeID to cost for 3rdfile data
        id_to_cost_map_1stfile = defaultdict(float)  # Map to store pipeID to cost for 1stfile data
        
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
            
            if pipe_id not in unique_pipeid_2ndfile:
                unique_pipeid_2ndfile.append(pipe_id)
            
            print("Unique Pipe ID in 2ndfile data: ", unique_pipeid_2ndfile)
            
            if cost==0:
                flow_parallel[pipe_id]=flow
                speed_parallel[pipe_id]=speed
            
            pipeid_length_map_2ndfile[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_2ndfile[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_2ndfile[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_2ndfile[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_2ndfile[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("5 minute Result File Pipe ID to Cost Map : " + str(id_to_cost_map_2ndfile))
        
        if pipeData1stfile is not None:
            unique_id = unique_pipeid_2ndfile.copy()
            for i in range(len(pipeData1stfile["pipeID"])):
                pipe_id = pipeData1stfile["pipeID"][i]
                diameter = pipeData1stfile["diameter"][i]
                length = pipeData1stfile["length"][i]
                parallel = pipeData1stfile["parallel"][i]
                cost = pipeData1stfile["cost"][i]
                flow = pipeData1stfile["flow"][i]
                speed = pipeData1stfile["speed"][i]
                
                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1stfile[pipe_id] = False
                elif cost ==0 and (flow_parallel[pipe_id] == flow and speed_parallel[pipe_id] == speed):
                    exist_pipe_status_1stfile[pipe_id] = True
                    
                id_to_cost_map_1stfile[pipe_id] += cost  # Aggregate cost for each pipeID in 2ndfile data
                
                # Find the pipe id which are diffrent from 2ndfile to 1stfile
                if cost!=0 :
                    
                    # speeddiff = abs(speed - pipeif_speed_map_2ndfile[(pipe_id, diameter, parallel)])
                    if(pipe_id == 2):
                        print("Pipe ID 2 found in 1stfile data")
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_2ndfile:
                        print("Pipe ID not found in 1stfile data: ", pipe_id)
                        different_pipe_1stfile.append(pipe_id)
                    elif length != pipeid_length_map_2ndfile[(pipe_id, diameter, parallel)]:
                        print("Pipe length not match 1stfile data: ", pipe_id)
                        different_pipe_1stfile.append(pipe_id)
                    elif cost != pipeid_cost_map_2ndfile[(pipe_id, diameter, parallel)]:
                        print("Pipe cost not match 1stfile data: ", pipe_id)
                        different_pipe_1stfile.append(pipe_id)
                    elif flow != pipeid_flow_map_2ndfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_2ndfile[(pipe_id, diameter, parallel)])
                        if flowdiff > 0.01:
                            print("Pipe flow not match 1stfile data: ", pipe_id)
                            different_pipe_1stfile.append(pipe_id) 
                    elif speed != pipeif_speed_map_2ndfile[(pipe_id, diameter, parallel)]:
                        speeddiff = abs(speed - pipeif_speed_map_2ndfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            print("Pipe speed not match 1stfile data: ", pipe_id)
                            different_pipe_1stfile.append(pipe_id)
                    else:   
                        None
                
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    print("Pipe cost is zero and parallel is not parallel: ", pipe_id)
                    different_pipe_1stfile.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if(pipe_id not in unique_pipeid_2ndfile):
                    print("Unique Pipe ID :", unique_pipeid_2ndfile)
                    print("Pipe ID not found in 2ndfile data: ", pipe_id)
                    different_pipe_1stfile.append(pipe_id)
                
                if pipe_id in unique_id:
                    # print("Removing Pipe ID from unique_id: ", pipe_id)
                    unique_id.remove(pipe_id)

            print("Unique Pipe ID in 2ndfile data: ", unique_id)
            if len(unique_id) > 0:
                different_pipe_1stfile += unique_id

            different_pipe_1stfile= list(dict.fromkeys(different_pipe_1stfile))  # Remove duplicates
            logger.info("Pipe ID which are diffrent in 1stfile output file compare to the 2ndfile output file : "+ str(different_pipe_1stfile))
            
            #find the diffrance cost between one minute and five minute
            for pipe_id in different_pipe_1stfile:
                if pipe_id in id_to_cost_map_1stfile and pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_1stfile[pipe_id] = id_to_cost_map_2ndfile[pipe_id] - id_to_cost_map_1stfile[pipe_id]
                elif pipe_id in id_to_cost_map_1stfile:
                    difference_cost_pipeid_1stfile[pipe_id] = -id_to_cost_map_1stfile[pipe_id]
                elif pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_1stfile[pipe_id] = id_to_cost_map_2ndfile[pipe_id]
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1stfile = dict(sorted(difference_cost_pipeid_1stfile.items(), key=lambda item: item[1], reverse=True))
            
            par_2ndfiletab_1stfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_1stfile)}<br>"
            par_2ndfiletab_1stfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_1stfile.keys())}<br><br>"
            par_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            for pipe_id in sorted_difference_cost_pipeid_1stfile:
                par_2ndfiletab_1stfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_2ndfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")

                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                
                for i in range(len(pipeData1stfile["pipeID"])):
                    if pipeData1stfile["pipeID"][i] == pipe_id:
                        diameter = pipeData1stfile["diameter"][i]
                        length = pipeData1stfile["length"][i]
                        cost = pipeData1stfile["cost"][i]
                        flow = pipeData1stfile["flow"][i]
                        speed = pipeData1stfile["speed"][i]
                        par_2ndfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")
                par_2ndfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_1stfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})</b><br><br><br>")
                par_2ndfiletab_1stfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 2ndfile tab with 1stfile data is stored")
                
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1stfile = dict(sorted(difference_cost_pipeid_1stfile.items(), key=lambda item: item[1], reverse=False))
            
            par_1stfiletab_2ndfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_1stfile)}<br>"
            par_1stfiletab_2ndfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_1stfile.keys())}<br><br>"
            par_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            for pipe_id in sorted_difference_cost_pipeid_1stfile:
                par_1stfiletab_2ndfile += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                for i in range(len(pipeData1stfile["pipeID"])):
                    if pipeData1stfile["pipeID"][i] == pipe_id:
                        diameter = pipeData1stfile["diameter"][i]
                        length = pipeData1stfile["length"][i]
                        cost = pipeData1stfile["cost"][i]
                        flow = pipeData1stfile["flow"][i]
                        speed = pipeData1stfile["speed"][i]
                        par_1stfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")

                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1stfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")
                par_1stfiletab_2ndfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1stfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})</b><br><br>")
                par_1stfiletab_2ndfile += "----------------------------------------------------<br><br>"
        logger.info("Paragraph for 1stfile tab with 2ndfile data is stored")

        if pipeData3rdfile is not None:
            unique_id = unique_pipeid_2ndfile.copy()
            for i in range(len(pipeData3rdfile["pipeID"])):
                pipe_id = pipeData3rdfile["pipeID"][i]
                diameter = pipeData3rdfile["diameter"][i]
                length = pipeData3rdfile["length"][i]
                parallel = pipeData3rdfile["parallel"][i]
                cost = pipeData3rdfile["cost"][i]
                flow = pipeData3rdfile["flow"][i]
                speed = pipeData3rdfile["speed"][i]
                
                id_to_cost_map_3rdfile[pipe_id] += cost  # Aggregate cost for each pipeID in 3rdfile data

                if cost ==0  and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_3rdfile[pipe_id] = False
                else:
                    exist_pipe_status_3rdfile[pipe_id] = True
                
                if pipe_id not in unique_pipeid_2ndfile:
                    different_pipe_3rdfile.append(pipe_id)

                # Find the pipe id which are diffrent from 1stfile to 3rdfile
                if cost!=0 :
                    
                    
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_2ndfile:
                        different_pipe_3rdfile.append(pipe_id)
                    elif length != pipeid_length_map_2ndfile[(pipe_id, diameter, parallel)]:
                        different_pipe_3rdfile.append(pipe_id)
                    elif cost != pipeid_cost_map_2ndfile[(pipe_id, diameter, parallel)]:
                        different_pipe_3rdfile.append(pipe_id)
                    elif flow != pipeid_flow_map_2ndfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_2ndfile[(pipe_id, diameter, parallel)])
                        if flowdiff > 0.01:
                            different_pipe_3rdfile.append(pipe_id)
                    elif speed != pipeif_speed_map_2ndfile[(pipe_id, diameter, parallel)]:
                        speeddiff = abs(speed - pipeif_speed_map_2ndfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            different_pipe_3rdfile.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_3rdfile.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)


            if(len(unique_id) > 0) :
                different_pipe_3rdfile+=unique_id
            
            
            different_pipe_3rdfile = list(dict.fromkeys(different_pipe_3rdfile))  # Remove duplicates   
            
            logger.info("Pipe ID which are diffrent in 3rdfile output file compare to the 2ndfile output file : "+ str(different_pipe_3rdfile)) 
            
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_3rdfile:
                if pipe_id in id_to_cost_map_2ndfile and pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = id_to_cost_map_2ndfile[pipe_id] - id_to_cost_map_3rdfile[pipe_id]
                elif pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = id_to_cost_map_2ndfile[pipe_id]
                elif pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_3rdfile[pipe_id] = -id_to_cost_map_3rdfile[pipe_id]
                else:
                    difference_cost_pipeid_3rdfile[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_3rdfile = dict(sorted(difference_cost_pipeid_3rdfile.items(), key=lambda item: item[1], reverse=True))
            
            par_2ndfiletab_3rdfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_3rdfile)}<br>"
            par_2ndfiletab_3rdfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_3rdfile.keys())}<br><br>"
            par_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            #prepare the paragraph for 2ndfile tab with 3rdfile data
            for pipe_id in sorted_difference_cost_pipeid_3rdfile:
                par_2ndfiletab_3rdfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_2ndfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")

                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                
                for i in range(len(pipeData3rdfile["pipeID"])):
                        diameter = pipeData3rdfile["diameter"][i]
                        length = pipeData3rdfile["length"][i]
                        cost = pipeData3rdfile["cost"][i]
                        flow = pipeData3rdfile["flow"][i]
                        speed = pipeData3rdfile["speed"][i]
                        par_2ndfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :<b> <br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")
                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; <b>Difference in cost : {round(sorted_difference_cost_pipeid_3rdfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})</b><br><br><br>")
                par_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 2ndfile tab with 3rdfile data is stored")
            
            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_3rdfile = dict(sorted(difference_cost_pipeid_3rdfile.items(), key=lambda item: item[1], reverse=False))
            
            par_2ndfiletab_3rdfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_3rdfile)}<br>"
            par_2ndfiletab_3rdfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_3rdfile.keys())}<br><br>"
            par_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            #prepare the paragraph for 3rdfile tab with 2ndfile data
            for pipe_id in sorted_difference_cost_pipeid_3rdfile:
                par_3rdfiletab_2ndfile += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                for i in range(len(pipeData3rdfile["pipeID"])):
                    if pipeData3rdfile["pipeID"][i] == pipe_id:
                        diameter = pipeData3rdfile["diameter"][i]
                        length = pipeData3rdfile["length"][i]
                        cost = pipeData3rdfile["cost"][i]
                        flow = pipeData3rdfile["flow"][i]
                        speed = pipeData3rdfile["speed"][i]
                        par_3rdfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br><br>")

                par_3rdfiletab_2ndfile += ( f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):

                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_3rdfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")
                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_3rdfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_3rdfile[pipe_id], id_to_cost_map_3rdfile[pipe_id])})</b><br><br><br>")
                par_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 3rdfile tab with 2ndfile data is stored")
                        
        edge_trace ,edge_text, edge_colors, edge_text_color= data_processor.process_edges_for_diameter_graph_plotting_2ndfile(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1stfile, different_pipe_3rdfile, exist_pipe_status_1stfile, exist_pipe_status_3rdfile)
        
        logger.info("Edge trace created for 2ndfile pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_2ndfile(G, pos, unique_parallel_pipes, edge_colors, pipeData1stfile, pipeData3rdfile, different_pipe_1stfile, different_pipe_3rdfile, exist_pipe_status_1stfile, exist_pipe_status_3rdfile, id_to_cost_map_1stfile, id_to_cost_map_3rdfile, id_to_cost_map_2ndfile, sorted_difference_cost_pipeid_1stfile, sorted_difference_cost_pipeid_3rdfile)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=17.5,
                color=edge_text_color,  # You can change the color as needed
                family='Arial Black'
            )
        )
        
        logger.info("Edge label trace created for 2ndfile pipe data graph")
        
        pipeFig_2ndfile = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
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
        
        pipeFig_2ndfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        logger.info("Pipe figure created for 2ndfile graph")   
        
        pipeFig_1stfile = go.Figure()
        pipeFig_3rdfile = go.Figure()
        
        if (pipeData1stfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1stfile)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1stfile, parrallel_pipes)
            logger.info("Creating 1stfile graph with 2ndfile data")
            logger.info("Parallel Pipes : " + str(parrallel_pipes))
            print("Number of Pipes in 1stfile data: ", no_of_pipe)
            pipeFig_1stfile, _, _, _, _, _, _ = self.create_pipe_1stfile_graph(pos, nodeData1stfile, pipeData1stfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, node_data, pipe_data, nodeData3rdfile, pipeData3rdfile, G1, start+1)
            
        
        if (pipeData3rdfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData3rdfile)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData3rdfile, parrallel_pipes)
            logger.info("Creating 3rdfile graph with 2ndfile data")
            pipeFig_3rdfile, _, _, _, _, _, _ = self.create_pipe_3rdfile_graph(pos, nodeData3rdfile, pipeData3rdfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, node_data, pipe_data, G2, start+1)

        return pipeFig_2ndfile, pipeFig_1stfile, pipeFig_3rdfile, par_2ndfiletab_1stfile, par_2ndfiletab_3rdfile, par_1stfiletab_2ndfile, par_3rdfiletab_2ndfile
    
    
    
    def create_pipe_3rdfile_graph(self, pos,node_data, pipe_data, unique_parallel_pipes, no_of_pipes, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, nodeData2ndfile, pipeData2ndfile, G, start) :
        data_processor = OutputDataProcessor()
        total_length_pipe_map, elevation_map = data_processor.process_main_network_pipedata(mainNodeData, mainpipe)
        node_head_map = {} 
        par_3rdfiletab_1stfile = ""  # Paragraph for 3rdfile tab with 1stfile data
        par_3rdfiletab_2ndfile = ""  # Paragraph for 3rdfile tab with 2ndfile data
        par_1stfiletab_3rdfile = ""  # Paragraph for 1stfile tab with 3rdfile data
        par_2ndfiletab_3rdfile = ""  # Paragraph for 2ndfile tab with 3rdfile data
        id_to_cost_map_3rdfile = defaultdict(float)  # Map to store pipeID to cost
        
        for i in range(len(node_data["nodeID"])):
            node_id = node_data["nodeID"][i]
            head = node_data["Head"][i]
            node_head_map[node_id] = head
        
        logger.info(f"3rdfile Graph Head Map : " + str(node_head_map))
        
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
                size=10,
                color="#AABFF5", 
                line=dict(width=1, color='black')
            )
        )
        
        logger.info("Node trace created for 3rdfile graph")
        
        
        different_pipe_1stfile = []
        different_pipe_2ndfile = []
        pipeid_length_map_3rdfile ={}
        pipeid_cost_map_3rdfile={}
        pipeid_flow_map_3rdfile ={}
        pipeif_speed_map_3rdfile={}
        difference_cost_pipeid_1stfile ={}
        difference_cost_pipeid_2ndfile ={}
        unique_pipeid_3rdfile= []
        exist_pipe_status_1stfile = {} #static parallel pipe flow and speed is same or not
        exist_pipe_status_2ndfile = {}
        flow_parallel = {} #for the static pipe which cost is zero 
        sorted_difference_cost_pipeid_1stfile ={}
        sorted_difference_cost_pipeid_2ndfile ={}
        speed_parallel= {}  #for the static pipe which cost is zero
        id_to_cost_map_1stfile = defaultdict(float)  # Map to store pipeID to cost for 1stfile data
        id_to_cost_map_2ndfile = defaultdict(float)  # Map to store pipeID to cost for 2ndfile data
        
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
            
            if pipe_id not in unique_pipeid_3rdfile:
                unique_pipeid_3rdfile.append(pipe_id)
            
            if cost ==0:
                flow_parallel[pipe_id]=flow
                speed_parallel[pipe_id]=speed

            pipeid_length_map_3rdfile[(pipe_id,diameter,parallel)]=length
            pipeid_cost_map_3rdfile[(pipe_id,diameter,parallel)]=cost
            pipeid_flow_map_3rdfile[(pipe_id,diameter,parallel)]=flow
            pipeif_speed_map_3rdfile[(pipe_id,diameter,parallel)]=speed
            id_to_cost_map_3rdfile[pipe_id] += cost  # Aggregate cost for each pipeID
        
        logger.info("1 hour Result File Pipe ID to Cost Map : " + str(id_to_cost_map_3rdfile))
                
        if pipeData1stfile is not None:
            unique_id = unique_pipeid_3rdfile.copy()
            for i in range(len(pipeData1stfile["pipeID"])):
                pipe_id = pipeData1stfile["pipeID"][i]
                diameter = pipeData1stfile["diameter"][i]
                length = pipeData1stfile["length"][i]
                parallel = pipeData1stfile["parallel"][i]
                cost = pipeData1stfile["cost"][i]
                flow = pipeData1stfile["flow"][i]
                speed = pipeData1stfile["speed"][i]

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_1stfile[pipe_id] = False

                id_to_cost_map_1stfile[pipe_id] += cost  # Aggregate cost for each pipeID in 2ndfile data
                
                # Find the pipe id which are diffrent from 3rdfile to 1stfile
                if cost!=0 :
                    
                    
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_3rdfile:
                        different_pipe_1stfile.append(pipe_id)
                    elif length != pipeid_length_map_3rdfile[(pipe_id, diameter, parallel)]:
                        different_pipe_1stfile.append(pipe_id)
                    elif cost != pipeid_cost_map_3rdfile[(pipe_id, diameter, parallel)]:
                        different_pipe_1stfile.append(pipe_id)
                    elif flow != pipeid_flow_map_3rdfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_3rdfile[(pipe_id, diameter, parallel)])
                        if flowdiff > 0.01:
                            different_pipe_1stfile.append(pipe_id) 
                    elif speed != pipeif_speed_map_3rdfile[(pipe_id, diameter, parallel)]:
                        speeddiff = abs(speed - pipeif_speed_map_3rdfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            different_pipe_1stfile.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_1stfile.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist

                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)
                
                if pipe_id not in unique_pipeid_3rdfile:
                    different_pipe_1stfile.append(pipe_id)

            if len(unique_id) > 0:
                different_pipe_1stfile+=unique_id
                
            different_pipe_1stfile= list(dict.fromkeys(different_pipe_1stfile))  # Remove duplicates
            
            logger.info("Pipe ID which are diffrent in 1stfile output file compare to the 3rdfile output file : "+ str(different_pipe_1stfile))
            #find the diffrance cost between one minute and one hour
            for pipe_id in different_pipe_1stfile:
                if pipe_id in id_to_cost_map_1stfile and pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_1stfile[pipe_id] = id_to_cost_map_3rdfile[pipe_id] - id_to_cost_map_1stfile[pipe_id]
                elif pipe_id in id_to_cost_map_1stfile:
                    difference_cost_pipeid_1stfile[pipe_id]= - id_to_cost_map_1stfile[pipe_id]
                elif pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_1stfile[pipe_id] = id_to_cost_map_3rdfile[pipe_id]
                else:
                    difference_cost_pipeid_1stfile[pipe_id] = 0
            
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1stfile = dict(sorted(difference_cost_pipeid_1stfile.items(), key=lambda item: item[1], reverse=True))
            
            par_3rdfiletab_1stfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_1stfile)}<br>"
            par_3rdfiletab_1stfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_1stfile.keys())}<br><br>"
            par_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
            
            for pipe_id in sorted_difference_cost_pipeid_1stfile:
                par_3rdfiletab_1stfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_3rdfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")

                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                
                for i in range(len(pipeData1stfile["pipeID"])):
                    if pipeData1stfile["pipeID"][i] == pipe_id:
                        diameter = pipeData1stfile["diameter"][i]
                        length = pipeData1stfile["length"][i]
                        cost = pipeData1stfile["cost"][i]
                        flow = pipeData1stfile["flow"][i]
                        speed = pipeData1stfile["speed"][i]
                        par_3rdfiletab_1stfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")
                par_3rdfiletab_1stfile += (f"&nbsp; &nbsp; &nbsp;<b>Difference in cost : {round(sorted_difference_cost_pipeid_1stfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_3rdfile[pipe_id])})</b><br><br><br>")
                par_3rdfiletab_1stfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 3rdfile tab with 1stfile data is stored")
            # ascending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_1stfile = dict(sorted(difference_cost_pipeid_1stfile.items(), key=lambda item: item[1], reverse=False))
            
            
            par_1stfiletab_3rdfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_1stfile)}<br>"
            par_1stfiletab_3rdfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_1stfile.keys())}<br><br>"
            par_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            for pipe_id in sorted_difference_cost_pipeid_1stfile:
                par_1stfiletab_3rdfile += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>1stfile Data :</b> <br>")
                for i in range(len(pipeData1stfile["pipeID"])):
                    if pipeData1stfile["pipeID"][i] == pipe_id:
                        diameter = pipeData1stfile["diameter"][i]
                        length = pipeData1stfile["length"][i]
                        cost = pipeData1stfile["cost"][i]
                        flow = pipeData1stfile["flow"][i]
                        speed = pipeData1stfile["speed"][i]
                        par_1stfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 1stfile : {round(id_to_cost_map_1stfile[pipe_id], 2):,}<br><br>")
                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_1stfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")
                par_1stfiletab_3rdfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_1stfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_1stfile[pipe_id], id_to_cost_map_1stfile[pipe_id])})</b><br><br><br>")
                par_1stfiletab_3rdfile += "----------------------------------------------------<br><br>"
            logger.info("Paragraph for 1stfile tab with 3rdfile data is stored")

        if pipeData2ndfile is not None:
            unique_id = unique_pipeid_3rdfile.copy()
            for i in range(len(pipeData2ndfile["pipeID"])):
                pipe_id = pipeData2ndfile["pipeID"][i]
                diameter = pipeData2ndfile["diameter"][i]
                length = pipeData2ndfile["length"][i]
                parallel = pipeData2ndfile["parallel"][i]
                cost = pipeData2ndfile["cost"][i]
                flow = pipeData2ndfile["flow"][i]
                speed = pipeData2ndfile["speed"][i]
                
                id_to_cost_map_2ndfile[pipe_id] += cost  # Aggregate cost for each pipeID in 2ndfile data

                if cost ==0 and (flow_parallel[pipe_id] != flow or speed_parallel[pipe_id] != speed):
                    exist_pipe_status_2ndfile[pipe_id] = False

                if pipe_id not in unique_pipeid_3rdfile:
                    # print(1)
                    different_pipe_2ndfile.append(pipe_id)
                
                # Find the pipe id which are diffrent from 2ndfile to 3rdfile
                if cost!=0 :
                    
                    
                    if (pipe_id, diameter,parallel) not in pipeid_length_map_3rdfile:
                        different_pipe_2ndfile.append(pipe_id)
                    elif length != pipeid_length_map_3rdfile[(pipe_id, diameter, parallel)]:
                        different_pipe_2ndfile.append(pipe_id)
                    elif cost != pipeid_cost_map_3rdfile[(pipe_id, diameter, parallel)]:
                        # print(4)
                        different_pipe_2ndfile.append(pipe_id)
                    elif flow != pipeid_flow_map_3rdfile[(pipe_id, diameter, parallel)]:
                        flowdiff = abs(flow - pipeid_flow_map_3rdfile[(pipe_id, diameter, parallel)])
                        # print(5)
                        if flowdiff > 0.01:
                            different_pipe_2ndfile.append(pipe_id)
                    elif speed != pipeif_speed_map_3rdfile[(pipe_id, diameter, parallel)]:
                        # print(6)
                        speeddiff = abs(speed - pipeif_speed_map_3rdfile[(pipe_id, diameter, parallel)])
                        if speeddiff > 0.01:
                            different_pipe_2ndfile.append(pipe_id)
                    else:   
                        None
                elif cost ==0 and parallel ==0 and no_of_pipes[pipe_id]>1 :
                    different_pipe_2ndfile.append(pipe_id)
                    # If cost is zero and parallel is not parallel, consider it as different: because there is no parallel pipe exist
                
                if pipe_id in unique_id:
                    unique_id.remove(pipe_id)

            if(len(unique_id) > 0):
                print(8)
                different_pipe_2ndfile+=unique_id
                    
            different_pipe_2ndfile = list(dict.fromkeys(different_pipe_2ndfile))  # Remove duplicates    
            
            logger.info("Pipe ID which are diffrent in 2ndfile output file compare to the 3rdfile output file : "+ str(different_pipe_2ndfile))
            #find the diffrance cost between one minute and 1 hour
            for pipe_id in different_pipe_2ndfile:
                if pipe_id in id_to_cost_map_2ndfile and pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = id_to_cost_map_3rdfile[pipe_id] - id_to_cost_map_2ndfile[pipe_id]
                elif pipe_id in id_to_cost_map_2ndfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = -id_to_cost_map_2ndfile[pipe_id]
                elif pipe_id in id_to_cost_map_3rdfile:
                    difference_cost_pipeid_2ndfile[pipe_id] = id_to_cost_map_3rdfile[pipe_id]
                else:
                    difference_cost_pipeid_2ndfile[pipe_id] = 0
        
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_2ndfile = dict(sorted(difference_cost_pipeid_2ndfile.items(), key=lambda item: item[1], reverse=True))
            
            par_3rdfiletab_2ndfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_2ndfile)}<br>"
            par_3rdfiletab_2ndfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_2ndfile.keys())}<br><br>"
            par_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            #prepare the paragraph for 2ndfile tab with 3rdfile data
            for pipe_id in sorted_difference_cost_pipeid_2ndfile:
                par_3rdfiletab_2ndfile += (f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_3rdfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")

                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                
                for i in range(len(pipeData2ndfile["pipeID"])) :
                    if pipeData2ndfile["pipeID"][i] == pipe_id:
                        diameter = pipeData2ndfile["diameter"][i]
                        length = pipeData2ndfile["length"][i]
                        cost = pipeData2ndfile["cost"][i]
                        flow = pipeData2ndfile["flow"][i]
                        speed = pipeData2ndfile["speed"][i]
                        par_3rdfiletab_2ndfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")
                par_3rdfiletab_2ndfile += (f"&nbsp; &nbsp; <b>Difference in cost : {round(sorted_difference_cost_pipeid_2ndfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_3rdfile[pipe_id])})</b><br><br><br>")
                par_3rdfiletab_2ndfile += "----------------------------------------------------<br><br>"
            
            logger.info("Paragraph for 2ndfile tab with 3rdfile data is stored")
            # descending sort the dictonary based on the cost difference
            sorted_difference_cost_pipeid_2ndfile = dict(sorted(difference_cost_pipeid_2ndfile.items(), key=lambda item: item[1], reverse=False))
            
            par_2ndfiletab_3rdfile += f"Total Pipes with Cost, Flow, or Speed Differences : {len(sorted_difference_cost_pipeid_2ndfile)}<br>"
            par_2ndfiletab_3rdfile += f"Pipes ID : {', '.join(str(k) for k in sorted_difference_cost_pipeid_2ndfile.keys())}<br><br>"
            par_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
            
            #prepare the paragraph for 3rdfile tab with 2ndfile data
            for pipe_id in sorted_difference_cost_pipeid_2ndfile:
                par_2ndfiletab_3rdfile += ( f"<b>Pipe ID : {pipe_id}</b><br>"
                                            f"&nbsp; &nbsp; &nbsp; <b>2ndfile Data :</b> <br>")
                for i in range(len(pipeData2ndfile["pipeID"])):
                    if pipeData2ndfile["pipeID"][i] == pipe_id:
                        diameter = pipeData2ndfile["diameter"][i]
                        length = pipeData2ndfile["length"][i]
                        cost = pipeData2ndfile["cost"][i]
                        flow = pipeData2ndfile["flow"][i]
                        speed = pipeData2ndfile["speed"][i]
                        par_2ndfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")

                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 2ndfile : {round(id_to_cost_map_2ndfile[pipe_id], 2):,}<br><br>")

                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp; <b>3rdfile Data :</b> <br>")
                
                for i in range(len(pipe_data["pipeID"])):
                    if pipe_data["pipeID"][i] == pipe_id:
                        diameter = pipe_data["diameter"][i]
                        length = pipe_data["length"][i]
                        cost = pipe_data["cost"][i]
                        flow = pipe_data["flow"][i]
                        speed = pipe_data["speed"][i]
                        par_2ndfiletab_3rdfile += (
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Diameter : {round(diameter, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Length : {round(length, 2):,} m<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Cost : {round(cost, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; flow : {round(flow, 2):,}<br>"
                                            f"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Speed : {round(speed, 2):,}<br><br>")
                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; &nbsp;Total cost of 3rdfile : {round(id_to_cost_map_3rdfile[pipe_id], 2):,}<br><br>")
                par_2ndfiletab_3rdfile += (f"&nbsp; &nbsp; <b>Difference in cost : {-round(sorted_difference_cost_pipeid_2ndfile[pipe_id], 2):,} ({data_processor.percentage_difference(sorted_difference_cost_pipeid_2ndfile[pipe_id], id_to_cost_map_2ndfile[pipe_id])})</b><br><br><br>")
                par_2ndfiletab_3rdfile += "----------------------------------------------------<br><br>"
                
            logger.info("Paragraph for 3rdfile tab with 2ndfile data is stored")
        edge_trace ,edge_text, edge_colors, edge_text_color= data_processor.process_edges_for_diameter_graph_plotting_3rdfile(G, pos, pipe_data, total_length_pipe_map, unique_parallel_pipes, different_pipe_1stfile, different_pipe_2ndfile, exist_pipe_status_1stfile, exist_pipe_status_2ndfile)
        
        logger.info("Edge trace created for 3rdfile pipe data graph")
        
        edge_label_x, edge_label_y = data_processor.process_edge_label_positions_for_graph_plotting(G, pos, unique_parallel_pipes)
        
        edge_hovertext =data_processor.process_edge_hovertext_for_diameter_graph_3rdfile(G, pos, unique_parallel_pipes, edge_colors, pipeData1stfile, 
                                                                                         pipeData2ndfile, different_pipe_1stfile, different_pipe_2ndfile, exist_pipe_status_1stfile, exist_pipe_status_2ndfile
                                                                                         , id_to_cost_map_1stfile, id_to_cost_map_2ndfile, id_to_cost_map_3rdfile,
                                                                                         sorted_difference_cost_pipeid_1stfile, sorted_difference_cost_pipeid_2ndfile)
        
        edge_label_trace = go.Scatter(
            x=edge_label_x,
            y=edge_label_y,
            text=edge_text,  # Text to be displayed as labels
            hovertext=edge_hovertext,  # Hover information to be displayed when hovering over the labels
            mode='text',
            hoverinfo='text',  # This allows the hovertext to be shown (since hovertext acts like "text")
            textposition='middle center',
            textfont=dict(
                size=17.5,
                color=edge_text_color,  # You can change the color as needed
                family='Arial Black'
            )
        )
        
        logger.info("Edge label trace created for 3rdfile pipe data graph")
        
        pipeFig_3rdfile = go.Figure(data=edge_trace+ [node_trace, edge_label_trace],
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
        
        pipeFig_3rdfile.update_layout(
            paper_bgcolor='white',  # background outside the plot
            plot_bgcolor='white',   # background inside the plot grid
        )
        
        logger.info("Pipe figure created for 3rdfile graph")
        
        pipeFig_1stfile = go.Figure()
        pipeFig_2ndfile = go.Figure()
        
        if (pipeData1stfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData1stfile)
            G1, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData1stfile, parrallel_pipes)
            logger.info("Creating 1stfile graph with 3rdfile data")
            pipeFig_1stfile, _, _, _, _, _, _ = self.create_pipe_1stfile_graph(pos, nodeData1stfile, pipeData1stfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData2ndfile, pipeData2ndfile, node_data, pipe_data, G1, start+1)


        if (pipeData2ndfile is not None) and (start == 0):
            parrallel_pipes = data_processor.get_unique_parallel_pipes(pipeData2ndfile)
            G2, no_of_pipe = self.create_graph_with_parallel_and_mutliple_edges(pos, pipeData2ndfile, parrallel_pipes)
            logger.info("Creating 2ndfile graph with 3rdfile data")
            pipeFig_2ndfile, _, _, _, _, _, _ = self.create_pipe_2ndfile_graph(pos, nodeData2ndfile, pipeData2ndfile, parrallel_pipes, no_of_pipe, mainNodeData, mainpipe, nodeData1stfile, pipeData1stfile, node_data, pipe_data, G2, start+1)

        return pipeFig_3rdfile, pipeFig_1stfile, pipeFig_2ndfile, par_3rdfiletab_1stfile, par_3rdfiletab_2ndfile, par_1stfiletab_3rdfile, par_2ndfiletab_3rdfile
    
    
    

    
    
    
