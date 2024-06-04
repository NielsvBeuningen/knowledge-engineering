from neo4j import GraphDatabase

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
        tx.run(query, hospital_id=hospital_id, sa2_5dig=sa2_5dig, distance_time=distance_time, accessible=accessible, further_than_2h=further_than_2h)
        
    def fetch_data(self, categories, limit):
        graph = {}
        with self.driver.session(database=self.database) as session:     
            for category in categories:  
                nodes = {}   
                query = f"""
                MATCH (n:{category})
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT {limit}
                """
                result = session.run(query)
                for i, record in enumerate(result):
                    if record[0]["id"] not in nodes:
                        nodes[record[0]["id"]] = {"node": record[0], "relations": []}
                    nodes[record[0]["id"]]["relations"].append({"relation": record[1], "node": record[2]})
                    
                graph[category] = nodes
        return graph