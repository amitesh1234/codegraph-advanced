import os
from neo4j import GraphDatabase

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver

def run_query(cypher, params=None):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [record.data() for record in result]

def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None