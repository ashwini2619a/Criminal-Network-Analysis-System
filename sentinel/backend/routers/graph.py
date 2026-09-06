from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import networkx as nx

router = APIRouter(prefix='/api/graph', tags=['graph'])

class SearchQuery(BaseModel):
    query: Optional[str] = None
    q: Optional[str] = None

def safe_serialize_node(node_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(data)
    res['id'] = str(node_id)
    if 'label' not in res:
        res['label'] = res.get('name', str(node_id))
    if 'node_type' not in res:
        res['node_type'] = res.get('type', 'Unknown')
    return res

def safe_serialize_edge(u: str, v: str, data: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(data)
    res['source'] = str(u)
    res['target'] = str(v)
    if 'edge_type' not in res:
        res['edge_type'] = res.get('type', 'RELATED_TO')
    if 'label' not in res:
        res['label'] = res['edge_type']
    return res

@router.get('')
@router.get('/')
@router.get('/full')
async def get_full_graph(request: Request):
    """Returns the complete criminal network graph (all nodes and edges)."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        return {'nodes': [], 'edges': [], 'total_nodes': 0, 'total_edges': 0, 'error': 'Graph store not initialized'}
    if graph_store.graph.number_of_nodes() == 0:
        return {'nodes': [], 'edges': [], 'total_nodes': 0, 'total_edges': 0}

    G: nx.MultiDiGraph = graph_store.graph
    nodes = [safe_serialize_node(n, d) for n, d in G.nodes(data=True)]
    edges = [safe_serialize_edge(u, v, d) for u, v, k, d in G.edges(data=True, keys=True)]

    return {
        'nodes': nodes,
        'edges': edges,
        'total_nodes': len(nodes),
        'total_edges': len(edges)
    }

@router.get('/node/{node_id}')
async def get_node_details(node_id: str, request: Request):
    """Returns detailed profile for a single entity including immediate connections."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    actual_id = graph_store.resolve_node_id(node_id)
    if not actual_id or not graph_store.graph.has_node(actual_id):
        raise HTTPException(status_code=404, detail=f"Entity {node_id} not found in intelligence graph.")

    G: nx.MultiDiGraph = graph_store.graph
    node_data = safe_serialize_node(actual_id, G.nodes[actual_id])

    connected_edges = []
    for u, v, k, d in G.edges(data=True, keys=True):
        if u == actual_id or v == actual_id:
            connected_edges.append(safe_serialize_edge(u, v, d))

    return {
        'node': node_data,
        'connections': connected_edges,
        'degree': len(connected_edges)
    }

@router.get('/node/{node_id}/expand')
@router.get('/expand/{node_id}')
async def expand_node(node_id: str, request: Request, depth: int = Query(default=2, ge=1, le=4)):
    """Returns N-hop neighborhood subgraph around an entity."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    subgraph_data = graph_store.get_neighbors(node_id, depth=depth)
    return subgraph_data

@router.get('/path')
@router.get('/shortest-path')
async def get_shortest_path(request: Request, source: str = Query(...), target: str = Query(...)):
    """Computes the shortest criminal/financial link path between any two targets."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    path_nodes = graph_store.shortest_path(source, target)
    if not path_nodes:
        return {'found': False, 'path': [], 'edges': [], 'nodes': []}

    G: nx.MultiDiGraph = graph_store.graph
    path_edges = []
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        edge_data = None
        if G.has_edge(u, v):
            edge_data = safe_serialize_edge(u, v, list(G.get_edge_data(u, v).values())[0])
        elif G.has_edge(v, u):
            edge_data = safe_serialize_edge(v, u, list(G.get_edge_data(v, u).values())[0])
        
        if edge_data:
            path_edges.append(edge_data)

    node_objects = [safe_serialize_node(n, G.nodes[n]) for n in path_nodes if G.has_node(n)]

    return {
        'found': True,
        'path': path_nodes,
        'nodes': node_objects,
        'edges': path_edges
    }

@router.get('/search')
async def search_graph_nodes_get(request: Request, q: str = Query("")):
    """GET query parameter text search."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or not q:
        return []

    results = graph_store.search_nodes(q)
    return [safe_serialize_node(r['id'], r) for r in results]

@router.post('/search')
async def search_graph_nodes_post(query: SearchQuery, request: Request):
    """POST body text search."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    search_term = query.query or query.q or ""
    if not graph_store or not search_term:
        return {'results': []}

    results = graph_store.search_nodes(search_term)
    return {'results': [safe_serialize_node(r['id'], r) for r in results], 'count': len(results)}

@router.get('/stats')
async def get_graph_statistics(request: Request):
    """Summary metrics of entities and relationships by categorical type."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store:
        return {'total_nodes': 0, 'total_edges': 0, 'nodes_by_type': {}, 'edges_by_type': {}}

    return graph_store.get_stats()

@router.get('/one-click-expand/{node_id}')
async def one_click_network_expansion(node_id: str, request: Request, depth: int = Query(default=2, ge=1, le=3)):
    """
    Auto-Feature 3: One-Click Network Expansion
    Starts with one suspect, phone, or account -> auto-expands 1st and 2nd degree
    contacts, financial links, and co-accused to render the full interactive sub-network.
    """
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    result = graph_store.expand_network(node_id, depth=depth)
    return result

@router.get('/subgraph')
async def get_filtered_subgraph(
    request: Request,
    node_type: Optional[str] = Query(None),
    min_risk: Optional[float] = Query(None),
    crime_type: Optional[str] = Query(None)
):
    """Returns a filtered subgraph based on analytical criteria."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        return {'nodes': [], 'edges': [], 'total_nodes': 0, 'total_edges': 0}

    G: nx.MultiDiGraph = graph_store.graph
    matching_nodes = []
    for n, d in G.nodes(data=True):
        if node_type and d.get('node_type') != node_type:
            continue
        if min_risk is not None and float(d.get('risk_score', 0)) < min_risk:
            continue
        if crime_type and d.get('crime_type') != crime_type:
            continue
        matching_nodes.append(n)

    sub = G.subgraph(matching_nodes)
    nodes = [safe_serialize_node(n, d) for n, d in sub.nodes(data=True)]
    edges = [safe_serialize_edge(u, v, d) for u, v, k, d in sub.edges(data=True, keys=True)]

    return {'nodes': nodes, 'edges': edges, 'total_nodes': len(nodes), 'total_edges': len(edges)}

@router.delete('/node/{node_id}')
async def delete_graph_node(node_id: str, request: Request):
    """Deletes an entity node and its incident edges from the active intelligence graph."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    actual_id = graph_store.resolve_node_id(node_id)
    if not actual_id or not graph_store.graph.has_node(actual_id):
        raise HTTPException(status_code=404, detail=f"Entity node {node_id} not found in graph.")

    graph_store.graph.remove_node(actual_id)
    graph_store.version += 1
    return {
        "status": "ok",
        "deleted_node_id": actual_id,
        "remaining_nodes": graph_store.graph.number_of_nodes(),
        "remaining_edges": graph_store.graph.number_of_edges()
    }

@router.post('/clear')
async def clear_graph(request: Request):
    """Purges all nodes and edges from the intelligence graph."""
    graph_store = getattr(request.app.state, 'graph_store', None)
    if not graph_store or graph_store.graph is None:
        raise HTTPException(status_code=500, detail="Graph store uninitialized.")

    nodes_removed = graph_store.graph.number_of_nodes()
    edges_removed = graph_store.graph.number_of_edges()
    graph_store.graph.clear()
    graph_store.version += 1
    return {
        "status": "ok",
        "nodes_removed": nodes_removed,
        "edges_removed": edges_removed,
        "message": "Graph successfully cleared to 0 nodes and 0 edges."
    }

