import networkx as nx
try:
    import community as community_louvain
except ImportError:
    community_louvain = None
from typing import Dict, List, Any
from collections import defaultdict

def detect_communities(G: nx.MultiDiGraph) -> Dict[str, int]:
    if G.number_of_nodes() == 0:
        return {}
    G_simple = nx.Graph(G)
    if community_louvain:
        try:
            return community_louvain.best_partition(G_simple)
        except Exception:
            pass
    try:
        communities = list(nx.algorithms.community.greedy_modularity_communities(G_simple))
        partition = {}
        for i, comm in enumerate(communities):
            for node in comm:
                partition[node] = i
        return partition
    except Exception:
        return {n: 0 for n in G.nodes()}

def get_community_details(G: nx.MultiDiGraph, partition: Dict[str, int]) -> List[Dict[str, Any]]:
    communities = defaultdict(list)
    for node, comm_id in partition.items():
        communities[comm_id].append(node)
    details = []
    G_simple = nx.Graph(G)
    for comm_id, members in communities.items():
        subgraph = G_simple.subgraph(members)
        size = len(members)
        density = nx.density(subgraph) if size > 1 else 0.0
        key_member = max(members, key=lambda n: G_simple.degree(n)) if members else None
        details.append({
            'id': comm_id,
            'size': size,
            'members': [{'node_id': m, 'name': G.nodes[m].get('name', str(m)), 'node_type': G.nodes[m].get('node_type', 'Unknown')} for m in members],
            'density': density,
            'key_member': key_member
        })
    return details

def find_bridge_nodes(G: nx.MultiDiGraph, partition: Dict[str, int]) -> List[Dict[str, Any]]:
    bridges = []
    G_simple = nx.Graph(G)
    for node in G_simple.nodes():
        connected_comms = set()
        for neighbor in G_simple.neighbors(node):
            if neighbor in partition:
                connected_comms.add(partition[neighbor])
        if len(connected_comms) > 1:
            bridges.append({
                'node_id': node,
                'name': G.nodes[node].get('name', str(node)),
                'node_type': G.nodes[node].get('node_type', 'Unknown'),
                'communities_connected': list(connected_comms),
                'bridge_score': len(connected_comms)
            })
    bridges.sort(key=lambda x: x['bridge_score'], reverse=True)
    return bridges
