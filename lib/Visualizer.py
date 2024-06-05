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
            'distance_time': row["relation"]["distance_time"]} for row in data if None not in row.values())
        
        dict_data = {
            'hospitals': {row["hospital"]["hospital_name"]: row["hospital"] for row in data if None not in row.values()} ,
            'sa2': {row["sa2"]["sa2_name"]: row["sa2"] for row in data if None not in row.values()},
            'relation': {f"{row["hospital"]["hospital_name"]}_{row["sa2"]["sa2_name"]}": row["relation"] for row in data if None not in row.values()}
            }
        
        df_select = pd.DataFrame(graph_data, columns=['hospital', 'sa2', 'distance_time'])  

        if len(df_select) > 0:
            G = nx.from_pandas_edgelist(df_select, 'hospital', 'sa2', ['distance_time'])
        else:
            G = nx.Graph()

        # Add nodes without edges
        for row in data:
            if None in row.values():
                if row["hospital"] is not None:
                    G.add_node(row["hospital"]["hospital_name"])
                    dict_data["hospitals"][row["hospital"]["hospital_name"]] = row["hospital"]
                if row["sa2"] is not None:
                    G.add_node(row["sa2"]["sa2_name"])
                    dict_data["sa2"][row["sa2"]["sa2_name"]] = row["sa2"]

        # Check if graph is empty
        if len(G.nodes) == 0:
            st.error("No data to display")
            st.stop()

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
            if node["label"] in dict_data["hospitals"]:
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
            dict_key = f"{edge['from']}_{edge['to']}"
            if dict_key not in dict_data["relation"]:
                dict_key = f"{edge['to']}_{edge['from']}"
            related_data = dict_data["relation"][dict_key]
            edge["title"] = f"""Travel time: {round(float(edge['distance_time']), 2)} seconds
            Accessible: {related_data["accessible"]}
            Further than 2 hours: {related_data["further_than_2h"]}
            """
            
            edge["value"] = edge["distance_time"]
            
            distance_time = float(edge["distance_time"])
            if distance_time > 7200:
                edge["color"] = colors["Edges"]["far"]
            elif distance_time > 1800:
                edge["color"] = colors["Edges"]["mid"]
            else:
                edge["color"] = colors["Edges"]["close"]

        # Save and read graph as HTML file (on Streamlit Sharing)
        file_path = os.path.join("pyvis_graph.html")
        network.save_graph(file_path)
        HtmlFile = open(file_path, 'r', encoding='utf-8')

        col1, col2 = st.columns(2)
        col1.warning("Hospital Nodes are yellow")
        col2.info("SA2 Region Nodes are blue")

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=height)