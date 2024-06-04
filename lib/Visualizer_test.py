import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from tqdm import tqdm

class Visualizer:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        pass

    def make_network_df(self, graph_dict) -> pd.DataFrame:
        """
        Function to create a DataFrame from the graph data
        
        :param graph_dict: Dictionary with the graph data
        
        :return: DataFrame with the graph data
        """
        
        network_data = []
        for node_id, node_dict in graph_dict.items():
            for relation in node_dict['relations']:
                network_data.append({
                    'hospital': node_dict['node']['hospital_name'],
                    'sa2': relation['node']['sa2_name'],
                    'distance_time': relation["relation"]['distance_time'],
                    'accessible': relation["relation"]['accessible'],
                    'further_than_2h': relation["relation"]['further_than_2h']
                })
                                        
        return pd.DataFrame(network_data)



    def plot_graph(self, network_df: pd.DataFrame, save_path: str | None = None) -> None:
        """
        Function to plot a network graph of the data
        
        :param network_df: DataFrame with the network data
        
        :return: None
        """
        
        # Get unique countries and subjects
        unique_hospitals = network_df['hospital'].to_list()
        unique_sa2 = network_df['sa2'].to_list()

        # Create graph
        G = nx.Graph()

        print("Creating nodes...")

        # Add nodes
        G.add_nodes_from(unique_hospitals, type='hospital')
        G.add_nodes_from(unique_sa2, type='sa2')

        print("Creating edges...")

        # Add edges
        for index, row in tqdm(network_df.iterrows()):
            G.add_edge(row['hospital'], row['sa2'])

        print("Creating layout...")
        pos = nx.spring_layout(G, seed=self.seed)

        edge_x = []
        edge_y = []

        print("Creating edge traces...")
        for edge in tqdm(G.edges()):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='text',
            mode='lines',
            showlegend=False
            )

        hospital_x = []
        hospital_y = []

        sa2_x = []
        sa2_y = []

        print("Creating node traces...")

        # Populate the lists based on the node type
        for node in tqdm(G.nodes()):
            G.nodes[node]['pos'] = pos[node]
            x, y = G.nodes[node]['pos']
            if G.nodes[node]['type'] == 'hospital':
                hospital_x.append(x)
                hospital_y.append(y)
            elif G.nodes[node]['type'] == 'sa2':
                sa2_x.append(x)
                sa2_y.append(y)

        # Create the country nodes trace with red rectangles
        hospital_trace = go.Scatter(
            name="Hospitals",
            x=hospital_x, y=hospital_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='red',
                size=10,
                line_width=1,
                symbol='square'
            )
        )

        # Create the subject nodes trace with blue circles
        sa2_trace = go.Scatter(
            name="SA2 Regions",
            x=sa2_x, y=sa2_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='blue',
                size=10,
                line_width=1
            )
        )

        # Create text for the hoverinfo for the country nodes and the subject nodes
        hospital_text = []
        sa2_text = []
        edge_text = []
        
        print("Annotating nodes...")
        for node, adjacencies in tqdm(enumerate(G.adjacency())):        
            if G.nodes[adjacencies[0]]['type'] == 'hospital':
                hospital_text.append(f"""
                    Hospital: {adjacencies[0]}
                    """)
            elif G.nodes[adjacencies[0]]['type'] == 'sa2':         
                sa2_text.append(f"""
                    SA2: {adjacencies[0]}
                    """)
                
        print("Annotating edges...")
        for edge in tqdm(G.edges()):
            edge_text.append(f"""
                Hospital: {edge[0]}
                SA2: {edge[1]}
                """)
            
        # Add the text to the traces
        hospital_trace.text = hospital_text
        sa2_trace.text = sa2_text
        edge_trace.text = edge_text

        print("Finalizing plot...")
        fig = go.Figure(data=[edge_trace, hospital_trace, sa2_trace],
                    layout=go.Layout(
                        title='<br>Network graph for Hospital and SA2 Graph',
                        titlefont_size=20,
                        showlegend=True,
                        hovermode='closest',
                        margin=dict(b=60,l=60,r=60,t=60),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        fig.show()
        
        if save_path is not None:
            print("Saving plot...")
            # Save the figure as an HTML file
            fig.write_html(save_path)
            print("Plot saved!")