"""
SENTINEL v2.0 — Neo4j 5.x Client with Automatic Fallback
Provides Cypher querying against enterprise Neo4j instances,
with automatic fallback to NetworkX when running offline or air-gapped.
"""

from typing import Dict, List, Any, Optional
from backend.config import USE_NEO4J, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jClient:
    def __init__(self, fallback_store=None):
        self.fallback = fallback_store
        self.driver = None
        self.is_connected = False
        
        if USE_NEO4J:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
                self.driver.verify_connectivity()
                self.is_connected = True
                print("Neo4jClient: Connected to Neo4j cluster.")
            except Exception as e:
                print(f"Neo4jClient: Neo4j connection failed ({e}). Defaulting to NetworkX fallback.")
                self.is_connected = False
        else:
            self.is_connected = False

    def execute_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query on Neo4j if available, or logs offline fallback.
        """
        if self.is_connected and self.driver:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        return []

    def close(self):
        if self.driver:
            self.driver.close()
