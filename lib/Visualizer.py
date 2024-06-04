import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import os

class Visualizer:
    def __init__(self):
        pass
    
    def graph_display(self, data, colors, height=600):
        graph_data = ({
            'hospital': row["hospital"]["hospital_name"],
            'sa2': row["sa2"]["sa2_name"],
            'distance_time': row["relation"]["distance_time"]} for row in data)
        
        dict_data = {
            'hospitals': {row["hospital"]["hospital_name"]: row["hospital"] for row in data} ,
            'sa2': {row["sa2"]["sa2_name"]: row["sa2"] for row in data},
            'relation': {f"{row["hospital"]["hospital_name"]}_{row["sa2"]["sa2_name"]}": row["relation"] for row in data}
            }
        
        df_select = pd.DataFrame(graph_data)                
                
        # Create networkx graph object from pandas dataframe
        G = nx.from_pandas_edgelist(df_select, 'hospital', 'sa2', ['distance_time'])

        # Initiate PyVis network object
        network = Network(
                        height=f'{height}px',
                        width='100%',
                        bgcolor='#222222',
                        font_color='white'
                        )

        # Take Networkx graph and translate it to a PyVis graph format
        network.from_nx(G)
        
        # Color nodes based on type
        for node in network.nodes:
            if node["label"] in df_select["hospital"].unique():
                related_data = dict_data["hospitals"][node["label"]]
                node["color"] = colors["Hospital"]
                node["title"] = f"""Hospital
                Name: {related_data["hospital_name"]}
                Phone: {related_data["phone_number"]}
                Address: {related_data["address"]}
                Suburb: {related_data["suburb"]}
                Postcode: {related_data["postcode"]}
                State: {related_data["state"]}
                LHN: {related_data["lhn"]}
                PHN: {related_data["phn"]}
                Website: {related_data["website"]}
                Description: {related_data["description"]}
                Sector: {related_data["sector"]}                
                """
            else:
                related_data = dict_data["sa2"][node["label"]]
                node["color"] = colors["SA2"]
                node["title"] = f"""SA2 Region
                Name: {related_data["sa2_name"]}
                Area: {related_data["area"]}
                Population: {related_data["population"]}
                Population Percentage: {round(related_data["pop_percentage"], 2)}
                Population Density: {related_data["pop_density"]}
                """
                
        # Color all edges with the same color
        for edge in network.edges:
            edge["color"] = colors["Edge"]

        # Generate network with specific layout settings
        # network.repulsion(
        #     node_distance=420,
        #     central_gravity=0.33,
        #     spring_length=110,
        #     spring_strength=0.10,
        #     damping=0.95
        # )
        
        # Add legend to the graph
        # network.add_node("Hospital", color=colors["Hospital"], x=-600, y=-400, fixed=True)
        # network.add_node("SA2", color=colors["SA2"], x=-600, y=-300, fixed=True)
        
        # Add hover functionality
        for edge in network.edges:
            edge["title"] = f"Travel time: {round(float(edge['distance_time']), 2)} seconds"
            edge["value"] = edge["distance_time"]

        # Save and read graph as HTML file (on Streamlit Sharing)
        file_path = os.path.join("pyvis_graph.html")
        network.save_graph(file_path)
        HtmlFile = open(file_path, 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=height)
                    
