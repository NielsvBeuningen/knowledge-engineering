# Load default libraries
import streamlit as st

from lib.GraphDB import GraphDB
from lib.Visualizer import Visualizer

# Load configuration
import yaml
from yaml.loader import SafeLoader

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

tab1, tab2 = st.tabs(["Query", "Graph"])

with tab1:
    st.header("Run Queries")
    example_exp = st.expander("Example Queries", expanded=False)
    update_btns = {}
        
    with example_exp:
        st.write("Show all nodes")
        st.code("MATCH (n) RETURN n LIMIT 10")
        if st.button("Load", key="all_nodes"):
            st.session_state.example_loaded = "MATCH (n) RETURN n LIMIT 10"
            st.rerun()
        
        st.write("Show all relationships")
        st.code("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10")
        if st.button("Load", key="all_relationships"):
            st.session_state.example_loaded = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10"
            st.rerun()
        
    if st.session_state.example_loaded != "":
        query_input = st.text_area("Query", st.session_state.example_loaded, key="query_input")
    else:
        query_input = st.text_area("Query", "MATCH (n) RETURN n LIMIT 10", key="query_input")
    
    if st.button("Run Query"):
        results = st.session_state.db.run_query(
            query = query_input
            )
        st.header("Results")
        st.write(results)

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
        st.info(f"Graph loaded with {st.session_state.graph_size} nodes")
        col1, col2 = st.columns(2)
        col1.warning("Hospital Nodes are yellow")
        col2.error("SA2 Region Nodes are red")
        st.session_state.visualizer.graph_display(
            st.session_state.graph_database, 
            colors = st.session_state.config["VISUALIZATION"]["COLORS"],
            height = 600
            )



