import networkx as nx
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

def compute_all_centralities(G: nx.MultiDiGraph) -> Dict[str, Dict[str, float]]:
    """Compute 5 centrality metrics for all nodes."""
    if G.number_of_nodes() == 0:
        return {}
    G_simple = nx.Graph(G)
    centralities: Dict[str, Dict[str, float]] = {n: {} for n in G.nodes()}
    
    # 1. Degree Centrality
    try:
        deg = nx.degree_centrality(G_simple)
        for n, v in deg.items(): centralities[n]['degree'] = v
    except Exception:
        for n in G.nodes(): centralities[n]['degree'] = 0.0

    # 2. Betweenness Centrality
    try:
        bet = nx.betweenness_centrality(G_simple)
        for n, v in bet.items(): centralities[n]['betweenness'] = v
    except Exception:
        for n in G.nodes(): centralities[n]['betweenness'] = 0.0

    # 3. Closeness Centrality
    try:
        clo = nx.closeness_centrality(G_simple)
        for n, v in clo.items(): centralities[n]['closeness'] = v
    except Exception:
        for n in G.nodes(): centralities[n]['closeness'] = 0.0

    # 4. PageRank
    try:
        pr = nx.pagerank(G)
        for n, v in pr.items(): centralities[n]['pagerank'] = v
    except Exception:
        for n in G.nodes(): centralities[n]['pagerank'] = 0.0

    # 5. Eigenvector Centrality
    try:
        eig = nx.eigenvector_centrality(G_simple, max_iter=1000)
        for n, v in eig.items(): centralities[n]['eigenvector'] = v
    except Exception:
        try:
            eig = nx.eigenvector_centrality_numpy(G_simple)
            for n, v in eig.items(): centralities[n]['eigenvector'] = float(v)
        except Exception:
            for n in G.nodes(): centralities[n]['eigenvector'] = 0.0

    return centralities

def compute_composite_risk(centralities: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Weighted composite risk score scaled to 0-100."""
    if not centralities:
        return {}
    metrics = ['degree', 'betweenness', 'closeness', 'pagerank', 'eigenvector']
    weights = {
        'degree': 0.15,
        'betweenness': 0.30,
        'closeness': 0.15,
        'pagerank': 0.25,
        'eigenvector': 0.15
    }
    
    max_vals = {m: max((c.get(m, 0.0) for c in centralities.values()), default=1.0) for m in metrics}
    min_vals = {m: min((c.get(m, 0.0) for c in centralities.values()), default=0.0) for m in metrics}
    
    composite = {}
    for n, c in centralities.items():
        score = 0.0
        for m in metrics:
            val = c.get(m, 0.0)
            rng = max_vals[m] - min_vals[m]
            norm_val = (val - min_vals[m]) / rng if rng > 0 else 0.0
            score += weights[m] * norm_val
        composite[n] = round(score * 100.0, 2)
    return composite

def detect_shadow_kingpins(centralities: Dict[str, Dict[str, float]], G: nx.MultiDiGraph) -> List[Dict[str, Any]]:
    """Detect nodes with high betweenness but low degree."""
    if not centralities:
        return []
    bet_vals = [c['betweenness'] for c in centralities.values()]
    deg_vals = [c['degree'] for c in centralities.values()]
    if not bet_vals or not deg_vals:
        return []
    bet_80 = np.percentile(bet_vals, 80)
    deg_30 = np.percentile(deg_vals, 30)
    shadows = []
    composite = compute_composite_risk(centralities)
    for n, c in centralities.items():
        if c['betweenness'] >= bet_80 and c['degree'] <= deg_30:
            shadows.append({
                'node_id': n,
                'name': G.nodes[n].get('name', str(n)),
                'betweenness': c['betweenness'],
                'degree': c['degree'],
                'composite_risk': composite.get(n, 0.0),
                'risk_score': composite.get(n, 0.0),
                'reason': 'High betweenness with low direct connections'
            })
    return shadows

def get_top_kingpins(G: nx.MultiDiGraph, n: int = 10) -> List[Dict[str, Any]]:
    """Get top N kingpins by composite risk score."""
    centralities = compute_all_centralities(G)
    risk_scores = compute_composite_risk(centralities)
    shadows = {s['node_id'] for s in detect_shadow_kingpins(centralities, G)}
    nodes_data = []
    for node_id, score in risk_scores.items():
        nodes_data.append({
            'node_id': node_id,
            'name': G.nodes[node_id].get('name', str(node_id)),
            'risk_score': score,
            'composite_risk': score,
            'centralities': centralities[node_id],
            'is_shadow_kingpin': node_id in shadows
        })
    nodes_data.sort(key=lambda x: x['risk_score'], reverse=True)
    top_n = nodes_data[:n]
    for i, d in enumerate(top_n):
        d['rank'] = i + 1
    return top_n
