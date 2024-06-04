import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

class Visualizer:
    def __init__(self):
        pass
    
    def graph_display(self, data, categories, colors):
        nodes = []
        edges = [] 
        for category in categories:
            for id, info in data[category].items():
                id = str(id)
                name = info['node']["name"]
                
                nodes.append( 
                    Node(id=id,         
                        label=name, 
                        size=5,
                        color=colors[category]
                        )
                    )
                
                # If there is a relation, add the edge
                for relation in info['relations']:
                    if relation['node'] is not None:
                        edge = Edge(
                            source=id, 
                            target=str(relation['node']["id"]), 
                            type=relation['relation']["type"],
                            label=relation['relation']["type"]
                            )
                        edges.append(edge)
                        st.write(edge)

        config = Config(width=1080,
                        height=1300,
                        directed=False, 
                        physics=False, 
                        hierarchical=False
                        )

        agraph(nodes=nodes, 
                edges=edges, 
                config=config)