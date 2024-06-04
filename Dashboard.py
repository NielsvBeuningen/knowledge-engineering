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

except Exception as e:
    st.error(st.session_state.config["MESSAGES"]["ERRORS"]["START"])
    st.error(e)
    st.stop()

st.set_page_config(
    page_title="Graph Dashboard"
)

graph_limit = st.slider(
    label="Limit the number of nodes", 
    min_value=0, 
    max_value=1000, 
    value=100
    )

st.session_state.graph_database = st.session_state.db.fetch_data(
            categories=st.session_state.config["DATABASE"]["CONTENTS"],
            limit = graph_limit
            )

st.session_state.visualizer.graph_display(
    st.session_state.graph_database, 
    categories=st.session_state.config["DATABASE"]["CONTENTS"], 
    colors = st.session_state.config["VISUALIZATION"]["COLORS"]
    )



