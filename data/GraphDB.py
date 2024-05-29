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
    def create_sa2(self, sa2_5dig, sa2_name, area):
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(self._create_sa2, sa2_5dig, sa2_name, area)
        
    @staticmethod
    def _create_sa2(tx, sa2_5dig, sa2_name, area):
        query = (
            "CREATE (s:SA2 {id: $sa2_5dig, sa2_name: $sa2_name, area: $area}) "
        )
        tx.run(query, sa2_5dig=sa2_5dig, sa2_name=sa2_name, area=area)

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

    def add_relation_sa2_hospital(self, hospital_id, sa2_5dig, distance_time):
        with self.driver.session(database=self.database) as session:
            session.write_transaction(self._add_relation_sa2_hospital, hospital_id, sa2_5dig, distance_time)

    @staticmethod
    def _add_relation_sa2_hospital(tx, hospital_id, sa2_5dig, distance_time):
        query = (
            "MATCH (s:SA2 {id: $sa2_5dig}) (h:Hospital {id: $hospital_id}) "
            "CREATE (h)-[:REACHABLE_VIA {distance_time: $distance_time}]->(s) "
        )
        tx.run(query, hospital_id=hospital_id, sa2_5dig=sa2_5dig, distance_time=distance_time)
    