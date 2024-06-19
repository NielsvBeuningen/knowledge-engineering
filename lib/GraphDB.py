from neo4j import GraphDatabase
import streamlit as st

class GraphDB:
    def __init__(self, uri, user, password, database):
        # self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()
        self.database = database

    def close(self):
        self.driver.close()

    ### COMPANY
    def create_sa2(self, sa2_5dig, sa2_name, area, population, pop_percentage, pop_density):
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._create_sa2, sa2_5dig, sa2_name, area, population, pop_percentage, pop_density)
        
    @staticmethod
    def _create_sa2(tx, sa2_5dig, sa2_name, area, population, pop_percentage, pop_density):
        query = (
            "CREATE (s:SA2 {id: $sa2_5dig, sa2_name: $sa2_name, area: $area, population: $population, pop_percentage: $pop_percentage, pop_density: $pop_density}) "
        )
        tx.run(query, sa2_5dig=sa2_5dig, sa2_name=sa2_name, area=area, population=population, pop_percentage=pop_percentage, pop_density=pop_density)

    def create_hospital(
        self, hospital_id, hospital_name, 
        phone_number, address, suburb, 
        postcode, state, lhn, phn, 
        website, description, sector, 
        beds, latitude, longitude
        ):
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(
                self._create_hospital, hospital_id, hospital_name, 
                phone_number, address, suburb, postcode, state, 
                lhn, phn, website, description, sector, beds, latitude, 
                longitude
                )
            
    @staticmethod
    def _create_hospital(
        tx, hospital_id, hospital_name, 
        phone_number, address, suburb, 
        postcode, state, lhn, phn, 
        website, description, sector, 
        beds, latitude, longitude
        ):
        query = (
            "CREATE (h:Hospital {id: $hospital_id, hospital_name: $hospital_name, phone_number: $phone_number, address: $address, suburb: $suburb, postcode: $postcode, state: $state, lhn: $lhn, phn: $phn, website: $website, description: $description, sector: $sector, beds: $beds, latitude: $latitude, longitude: $longitude}) "
        )
        tx.run(query, hospital_id=hospital_id, hospital_name=hospital_name, 
               phone_number=phone_number, address=address, suburb=suburb, 
               postcode=postcode, state=state, lhn=lhn, phn=phn, website=website, 
               description=description, sector=sector, beds=beds, latitude=latitude, 
               longitude=longitude)

    def add_relation_sa2_hospital(self, hospital_id, sa2_5dig, distance_time, accessible, further_than_2h):
        with self.driver.session(database=self.database) as session:
            session.write_transaction(self._add_relation_sa2_hospital, hospital_id, sa2_5dig, distance_time, accessible, further_than_2h)

    @staticmethod
    def _add_relation_sa2_hospital(tx, hospital_id, sa2_5dig, distance_time, accessible, further_than_2h):
        query = (
            "MATCH (h:Hospital {id: $hospital_id}), (s:SA2 {id: $sa2_5dig}) "
            "CREATE (h)-[:REACHABLE_VIA {distance_time: $distance_time, accessible: $accessible, further_than_2h: $further_than_2h}]->(s) "
        )
        tx.run(query, hospital_id=hospital_id, sa2_5dig=sa2_5dig, distance_time=float(distance_time), accessible=accessible, further_than_2h=further_than_2h)
      
    def run_query(self, query: str, query_limit: int, example_key: str) -> list | Exception:
        with self.driver.session(database=self.database) as session:     
            graph = []   
            query = f"{query} LIMIT {query_limit}"
            result = session.run(query)
            
            # If the query is one of the example queries, we need to convert the result to a dictionary
            if st.session_state.example_key in [
                "most_accessible",
                "population_to_beds",
                "least_hospitals",
                "distance_ratio"
            ]:
                for record in result:
                    # Convert record to proper dictionary
                    record_dict = {}
                    for key in record.keys():
                        record_dict[key] = record[key]
                    
                    graph.append(record_dict)
            else:
                # Else we can just append the result to the graph list as hostpital, sa2, relation
                for record in result:
                    if record[0].labels == {"Hospital"}:
                        graph.append(
                            {
                                "hospital": record[0], 
                                "sa2": record[2], 
                                "relation": record[1]
                            })
                    else:
                        graph.append(
                            {
                                "hospital": record[2], 
                                "sa2": record[0], 
                                "relation": record[1]
                            })
        return graph

        
    def fetch_data(self, limit):
        with self.driver.session(database=self.database) as session:     
            graph = []  
            query = f"""
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, r, m
            LIMIT {limit}
            """
            result = session.run(query)
            for record in result:
                if record[0].labels == {"Hospital"}:
                    graph.append(
                        {
                            "hospital": record[0], 
                            "sa2": record[2], 
                            "relation": record[1]
                        })
                else:
                    graph.append(
                        {
                            "hospital": record[2], 
                            "sa2": record[0], 
                            "relation": record[1]
                        })
        return graph