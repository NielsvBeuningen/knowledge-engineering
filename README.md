# LOE BV. Knowledge Base
## Table of Contents
1. [Setup Repository](#setup-repository)
2. [Setup Knowledge Graph](#setup-knowledge-graph)
3. [Setup Streamlit App](#setup-streamlit-app)
4. [App Documentation](#app-documentation)

## Setup Repository
### Clone Repository
First, fork the repository to your own GitHub account. Then, clone the repository to your local machine.
```bash
git clone https://github.com/YOUR-USERNAME/knowledge-engineering.git
```

### Install Dependencies
Navigate to the repository and install the required dependencies.
```bash
cd knowledge-engineering
pip install -r requirements.txt
```

## Setup Knowledge Graph
### Install Neo4j
Download and install Neo4j Desktop from the [official website](https://neo4j.com/download/).

### Create Database Management System (DBMS)
Load the database dump file for the main graph stored in this repository under `data/processed/maingraph.dump` into Neo4j Desktop. This can be done following this guide: [Importing Data into Neo4j](https://neo4j.com/docs/operations-manual/current/backup-restore/restore-dump/).

### Start Database
Start the DBMS in Neo4j Desktop. The database should now be running on `bolt://localhost:7687`.

## Setup Streamlit App
### Run Streamlit App
Navigate to the main repo directory and run the Streamlit app.
```bash
cd knowledge-engineering
streamlit run Dashboard.py
```

If starting for the first time, you will be prompted to enter the Neo4j credentials. Leave empty and press enter to use the default credentials.

## App Documentation
### Query Knowledge Graph
The main page of the app allows you to query the knowledge graph. Enter a query in the text box and press the "Query" button to see the results.

There are also some predefined queries available in the "Example Queries" dropdown menu. Select a query and press the "Load" button to load it into the text box.

The results of the query are displayed in a network graph. You can click over nodes and edges to see more information about it.

### Explore Knowledge Graph
The "Full Graph" page allows you to explore the knowledge graph by providing the limit of nodes and relationships to display. It then shows a network graph with the specified limit.
