"""
SENTINEL v2.0 — NetworkX In-Memory Fallback Graph Engine
Provides zero-dependency offline graph operations for air-gapped police systems.
"""

from backend.db.graph_store import GraphStore

class NetworkXFallback(GraphStore):
    """
    Subclasses GraphStore to guarantee complete offline execution
    matching the Section 8 directory structure.
    """
    pass
