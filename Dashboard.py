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
            "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25", 
            key="query_input")
    
    if st.button("Run Query"):
        st.session_state.graph_results = st.session_state.db.run_query(
            query = query_input
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
            st.session_state.visualizer.graph_display(
                data = st.session_state.graph_results, 
                colors = st.session_state.config["VISUALIZATION"]["COLORS"],
                height = 600
                )
        with subtab2:
            data = st.session_state.graph_results
            
            category = st.selectbox(
                label="Select a category to display",
                options=["Hospitals", "SA2s", "Distances"]
                )
            
            if category == "Hospitals":
                filtered_data = [record["hospital"] for record in data]
                # Use hospital name as index
                filtered_data = pd.DataFrame(filtered_data).set_index("hospital_name")
                # filtered_data = filtered_data.drop(columns=["hospital_name"])
            elif category == "SA2s":
                filtered_data = [record["sa2"] for record in data]
                filtered_data = pd.DataFrame(filtered_data).set_index("sa2_name")
            elif category == "Distances":
                st.write(data)
                filtered_data = [{
                    "hospital_name": record["hospital"]["hospital_name"],
                    "sa2": record["hospital"]["hospital_name"],
                    "distance (seconds)": record["relation"]["distance_time"],
                    "accessible": record["relation"]["accessible"],
                    "further_than_2_hours": record["relation"]["further_than_2h"],
                     
                     } for record in data]
                filtered_data = pd.DataFrame(filtered_data)
            
            # Drop duplicates
            filtered_data = filtered_data.drop_duplicates()
            
            st.dataframe(filtered_data)

with tab2:
    st.header("Explore Knowledge Graph")
    config_exp = st.expander("Graph Settings", expanded=True)
    with config_exp:
        graph_limit = st.slider(
            label="Limit the number of nodes", 
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
        st.session_state.visualizer.graph_display(
            st.session_state.graph_database, 
            colors = st.session_state.config["VISUALIZATION"]["COLORS"],
            height = 600
            )



