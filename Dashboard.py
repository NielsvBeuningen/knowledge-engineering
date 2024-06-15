# Load default libraries
import streamlit as st

from lib.GraphDB import GraphDB
from lib.Visualizer import Visualizer

# Load configuration
import yaml
from yaml.loader import SafeLoader

import pandas as pd

try:
    if "config" not in st.session_state:
        with open('config.yaml') as config_file:
            st.session_state.config = yaml.load(config_file, Loader=SafeLoader)

    if "db" not in st.session_state:
        st.session_state.db = GraphDB(
            uri=st.session_state.config["DATABASE"]["URI"], 
            user=st.session_state.config["DATABASE"]["USER"], 
            password=st.session_state.config["DATABASE"]["PASSWORD"], 
            database=st.session_state.config["DATABASE"]["DBNAME"]
            )
        
    if "visualizer" not in st.session_state:
        st.session_state.visualizer = Visualizer()
        
    if "graph_results" not in st.session_state:
        st.session_state.graph_results = None
        
    if "graph_database" not in st.session_state:
        st.session_state.graph_database = None
        st.session_state.graph_size = None
        
    if "example_loaded" not in st.session_state:
        st.session_state.example_loaded = ""

except Exception as e:
    st.error(st.session_state.config["MESSAGES"]["ERRORS"]["START"])
    st.error(e)
    st.stop()

st.set_page_config(
    page_title="Graph Dashboard"
)

tab1, tab2 = st.tabs(["Query", "Full Graph"])

with tab1:
    st.header("Run Queries")
    example_exp = st.expander("Example Queries", expanded=False)
    update_btns = {}
        
    with example_exp:
        for query_key in st.session_state.config["EXAMPLE_QUERIES"]:
            example_query = st.session_state.config["EXAMPLE_QUERIES"][query_key]
            st.write(example_query["description"])
            st.code(example_query["query"])
            if st.button("Load", key=example_query["key"]):
                st.session_state.example_loaded = example_query["query"]
                st.rerun()
        
    if st.session_state.example_loaded != "":
        query_input = st.text_area("Query", st.session_state.example_loaded, key="query_input")
    else:
        query_input = st.text_area(
            "Query", 
            st.session_state.config["DEFAULT_QUERY"], 
            key="query_input")
    
    query_limit = st.slider(
            label="Limit the number of relationships to display", 
            min_value=1, 
            max_value=1000, 
            value=25
            )
    
    if st.button("Run Query"):
        st.session_state.graph_results = st.session_state.db.run_query(
            query = query_input,
            query_limit = query_limit
            )
    
    if st.session_state.graph_results is None:
        st.info("Please run a query to see the results.")
    else:
        st.header("Results")
        subtab1, subtab2 = st.tabs(["Graph", "Table"])
        
        with subtab1:
            st.subheader("Graph")
            st.write(f"""
                    The graph below shows the relationships between the nodes in the query.
                    You can hover over the nodes and edges to see more information.
                    """)
            st.write(f"""
                    **:green[Green]** edges are closer than 30 minutes. 
                    **:orange[Orange]** edges are between 30 minutes and 2 hours. 
                    **:red[Red]** edges are further than 2 hours.
                    """)
            
            config_query = st.expander("Graph Configuration", expanded=True)
            node_distance_query = config_query.slider(
                label="Node Distance", 
                min_value=100, 
                max_value=1000, 
                value=500,
                key="node_distance_query"
                )
            
            scale_pop_query = config_query.checkbox(
                label="Scale node size based on population",
                value=True
                )
            
            st.session_state.visualizer.graph_display(
                data = st.session_state.graph_results, 
                colors = st.session_state.config["VISUALIZATION"]["COLORS"],
                height = 600,
                node_distance = node_distance_query,
                population_scaling = scale_pop_query
                )

        with subtab2:
            data = st.session_state.graph_results
            
            category = st.selectbox(
                label="Select a category to display",
                options=["Hospitals", "SA2s", "Distances"]
                )
            
            if category == "Hospitals":
                filtered_data = [record["hospital"] for record in data if record["hospital"] is not None]
                if len(filtered_data) > 0:
                    filtered_data = pd.DataFrame(filtered_data).rename(
                        columns=st.session_state.config["VISUALIZATION"]["COLUMN_NAMING"]["HOSPITALS"]
                        ).set_index(st.session_state.config["VISUALIZATION"]["COLUMN_NAMING"]["HOSPITALS"]["hospital_name"])

            elif category == "SA2s":
                filtered_data = [record["sa2"] for record in data if record["sa2"] is not None]
                if len(filtered_data) > 0:
                    filtered_data = pd.DataFrame(filtered_data).rename(
                        columns=st.session_state.config["VISUALIZATION"]["COLUMN_NAMING"]["SA2"]
                        ).set_index(st.session_state.config["VISUALIZATION"]["COLUMN_NAMING"]["SA2"]["sa2_name"])
            elif category == "Distances":
                hospitals = [record["hospital"] for record in data if record["hospital"] is not None]
                sa2 = [record["sa2"] for record in data if record["sa2"] is not None]
                if len(hospitals) and len(sa2) > 0:
                    method = st.radio(
                        label="Select a filtering method",
                        options=[
                            "Show All",
                            "Group by Hospital",
                            "Group by SA2"
                            ]
                    )
                    
                    filtered_data = [{
                        "hospital_name": record["hospital"]["hospital_name"] if record["hospital"] is not None else None,
                        "sa2": record["sa2"]["sa2_name"] if record["sa2"] is not None else None,
                        "distance (seconds)": record["relation"]["distance_time"] if record["relation"] is not None else None,
                        "accessible": record["relation"]["accessible"] if record["relation"] is not None else None,
                        "further_than_2_hours": record["relation"]["further_than_2h"] if record["relation"] is not None else None,
                        
                        } for record in data]
                    filtered_data = pd.DataFrame(filtered_data)
                    
                    if method == "Group by Hospital":
                        filtered_data = filtered_data.groupby("hospital_name").agg(
                            {
                                "sa2": "count",
                                "distance (seconds)": "mean",
                                "accessible": "mean",
                                "further_than_2_hours": "mean"
                                }
                            )
                        # Multiply by 100 to get percentage
                        filtered_data["accessible"] = round(filtered_data["accessible"] * 100, 2)
                        filtered_data["further_than_2_hours"] = round(filtered_data["further_than_2_hours"] * 100)
                        
                        # Rename index
                        filtered_data.index.name = "Hospital Name"
                        
                        # Rename columns
                        filtered_data.columns = [
                            "Number of SA2s",
                            "Mean Distance (seconds)",
                            "Accessible (%)",
                            "Further than 2 hours (%)"
                            ]
                        
                    elif method == "Group by SA2":
                        filtered_data = filtered_data.groupby("sa2").agg(
                            {
                                "hospital_name": "count",
                                "distance (seconds)": "mean",
                                "accessible": "mean",
                                "further_than_2_hours": "mean"
                                }
                            ) 
                        
                        # Multiply by 100 to get percentage
                        filtered_data["accessible"] = round(filtered_data["accessible"] * 100, 2)
                        filtered_data["further_than_2_hours"] = round(filtered_data["further_than_2_hours"] * 100, 2)
                    
                        # Rename index
                        filtered_data.index.name = "SA2 Name"
                    
                        # Rename columns
                        filtered_data.columns = [
                            "Number of Hospitals",
                            "Mean Distance (seconds)",
                            "Accessible (%)",
                            "Further than 2 hours (%)"
                            ]
                        
                    else:
                        filtered_data.columns = [
                            "Hospital Name",
                            "SA2 Name",
                            "Distance (seconds)",
                            "Accessible",
                            "Further than 2 hours"
                            ]
                    
                else:
                    filtered_data = []
            
            
            
            if len(filtered_data) > 0:
                # Drop duplicates
                filtered_data = filtered_data.drop_duplicates()
                st.dataframe(filtered_data)
            else:
                st.info("No data to display")

with tab2:
    st.header("Explore Knowledge Graph")
    config_exp = st.expander("Graph Settings", expanded=True)
    with config_exp:
        graph_limit = st.slider(
            label="Limit the number of relationships to display", 
            min_value=0, 
            max_value=1000, 
            value=100
            )
    
    if st.button("Load Graph"):
        st.session_state.graph_database = st.session_state.db.fetch_data(
                limit = graph_limit
                )
        st.session_state.graph_size = graph_limit
        
    if st.session_state.graph_database is not None:
        st.subheader("Graph")
        st.write(f"""
                The graph below shows the relationships between the nodes in the query.
                You can hover over the nodes and edges to see more information.
                """)
        st.write(f"""
                **:green[Green]** edges are closer than 30 minutes. 
                **:orange[Orange]** edges are between 30 minutes and 2 hours. 
                **:red[Red]** edges are further than 2 hours.
                """)
        
        config_graph = st.expander("Graph Configuration", expanded=True)
        node_distance_graph = config_graph.slider(
                label="Node Distance", 
                min_value=100, 
                max_value=1000, 
                value=500,
                key="node_distance_graph"
                )
        scale_pop_graph = config_graph.checkbox(
            label="Scale node size based on population",
            value=False
            )
            
        st.session_state.visualizer.graph_display(
            st.session_state.graph_database, 
            colors = st.session_state.config["VISUALIZATION"]["COLORS"],
            height = 600,
            node_distance = node_distance_graph,
            population_scaling = scale_pop_graph
            )



