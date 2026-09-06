import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

def detect_money_cycles(G: nx.MultiDiGraph, max_hours: int = 72) -> List[Dict[str, Any]]:
    """
    Detects multi-hop mule account layering and cyclic money flows under PMLA 2002 / FIU-IND guidelines.
    Note: Traditional informal Hawala relies on Angadia book transfers; in domestic banking telemetry,
    these closed loops highlight mule account structuring, smurfing, and rapid layering across shell entities.
    """
    money_edges = []
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'TRANSFERRED_MONEY' or d.get('type') == 'TRANSFERRED_MONEY':
            money_edges.append((u, v, k, d))
            
    if not money_edges:
        return []

    # Build directed graph of money transactions
    G_money = nx.DiGraph()
    for u, v, k, d in money_edges:
        if G_money.has_edge(u, v):
            G_money[u][v]['amount'] += float(d.get('amount', 0))
            if 'transactions' not in G_money[u][v]:
                G_money[u][v]['transactions'] = []
            G_money[u][v]['transactions'].append(d)
        else:
            G_money.add_edge(
                u, v,
                amount=float(d.get('amount', 0)),
                transactions=[d],
                timestamp=d.get('timestamp', '')
            )

    cycles_found = []
    try:
        candidate_cycles = [c for c in nx.simple_cycles(G_money, length_bound=5) if 2 < len(c) <= 5]
        
        for cycle in candidate_cycles:
            total_amount = 0.0
            tx_details = []
            timestamps = []
            
            for i in range(len(cycle)):
                src = cycle[i]
                dst = cycle[(i + 1) % len(cycle)]
                if G_money.has_edge(src, dst):
                    edge_data = G_money[src][dst]
                    amt = edge_data.get('amount', 0.0)
                    total_amount += amt
                    tx_details.append({
                        'from': src,
                        'to': dst,
                        'amount': amt
                    })
                    for tx in edge_data.get('transactions', []):
                        ts = tx.get('timestamp')
                        if ts:
                            try:
                                timestamps.append(datetime.fromisoformat(ts))
                            except Exception:
                                pass
                                
            # Calculate time span if timestamps available
            time_span_hours = 0.0
            if len(timestamps) >= 2:
                time_span_hours = (max(timestamps) - min(timestamps)).total_seconds() / 3600.0
            else:
                time_span_hours = 36.0  # Estimated average

            if time_span_hours <= max_hours or not timestamps:
                risk_level = "CRITICAL" if total_amount >= 500000 else "HIGH" if total_amount >= 100000 else "MEDIUM"
                
                # Fetch readable labels for nodes
                node_labels = []
                for n in cycle:
                    node_data = G.nodes.get(n, {})
                    node_labels.append(node_data.get('label') or node_data.get('name') or n)

                cycles_found.append({
                    'cycle_nodes': cycle,
                    'cycle_labels': node_labels,
                    'total_amount': total_amount,
                    'time_span_hours': round(time_span_hours, 1),
                    'risk_level': risk_level,
                    'transactions': tx_details
                })
    except Exception as e:
        print(f"Error detecting money cycles: {e}")

    return cycles_found

def detect_fan_in_fan_out(G: nx.MultiDiGraph) -> List[Dict[str, Any]]:
    """
    Detects 'Fan-in -> Fan-out' accounts:
    - Many small deposits followed by one or a few large withdrawals (consolidation / layering)
    - Or one large deposit followed by many rapid small disbursements (smurfing)
    """
    results = []
    
    # Collect all incoming and outgoing financial transactions per account/person
    inflow: Dict[str, List[float]] = defaultdict(list)
    outflow: Dict[str, List[float]] = defaultdict(list)
    
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'TRANSFERRED_MONEY' or d.get('type') == 'TRANSFERRED_MONEY':
            amt = float(d.get('amount', 0))
            if amt > 0:
                outflow[u].append(amt)
                inflow[v].append(amt)

    all_accounts = set(inflow.keys()) | set(outflow.keys())
    
    for acc in all_accounts:
        in_counts = len(inflow[acc])
        out_counts = len(outflow[acc])
        in_sum = sum(inflow[acc])
        out_sum = sum(outflow[acc])
        
        node_data = G.nodes.get(acc, {})
        acc_name = node_data.get('label') or node_data.get('name') or acc
        
        # Fan-in pattern: 3+ incoming deposits, 1-2 outgoing, total outflow >= 70% of inflow
        is_fan_in = in_counts >= 3 and 1 <= out_counts <= 2 and (out_sum >= 0.7 * in_sum if in_sum > 0 else False)
        
        # Fan-out pattern: 1-2 incoming deposits, 3+ outgoing disbursements
        is_fan_out = 1 <= in_counts <= 2 and out_counts >= 3 and (out_sum <= 1.3 * in_sum if in_sum > 0 else False)

        if is_fan_in or is_fan_out:
            pattern = "BOTH" if (is_fan_in and is_fan_out) else "FAN_IN" if is_fan_in else "FAN_OUT"
            risk = min(100.0, ((in_counts + out_counts) * 8.0) + (max(in_sum, out_sum) / 50000.0))
            
            results.append({
                'account_id': acc,
                'account_name': acc_name,
                'in_count': in_counts,
                'out_count': out_counts,
                'in_total': round(in_sum, 2),
                'out_total': round(out_sum, 2),
                'pattern_type': pattern,
                'risk_score': round(risk, 1)
            })

    # Sort by risk score descending
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results

def detect_structuring(G: nx.MultiDiGraph, threshold: float = 50000.0) -> List[Dict[str, Any]]:
    """
    Detects financial structuring (smurfing):
    Multiple transactions intentionally placed just below mandatory CTR reporting thresholds
    (e.g., between ₹45,000 and ₹49,999 in India where ₹50,000 triggers PAN/KYC/reporting requirements).
    """
    structured_by_sender: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'TRANSFERRED_MONEY' or d.get('type') == 'TRANSFERRED_MONEY':
            amt = float(d.get('amount', 0))
            # Just below threshold (90% to 99.9% of threshold)
            if (threshold * 0.9) <= amt < threshold:
                sender_data = G.nodes.get(u, {})
                recv_data = G.nodes.get(v, {})
                structured_by_sender[u].append({
                    'amount': amt,
                    'receiver_id': v,
                    'receiver_name': recv_data.get('label') or recv_data.get('name') or v,
                    'utr': d.get('utr', 'N/A'),
                    'timestamp': d.get('timestamp', 'Recent')
                })

    alerts = []
    for sender_id, tx_list in structured_by_sender.items():
        if len(tx_list) >= 1:  # Even 1 is suspicious, but 2+ is high risk
            sender_data = G.nodes.get(sender_id, {})
            total_amt = sum(t['amount'] for t in tx_list)
            pattern_type = f"{len(tx_list)}x Just-below ₹50K Sub-threshold Transfers"
            
            alerts.append({
                'account_id': sender_id,
                'account_name': sender_data.get('label') or sender_data.get('name') or sender_id,
                'suspicious_transactions': tx_list,
                'total_structured_amount': round(total_amt, 2),
                'count': len(tx_list),
                'pattern_type': pattern_type,
                'risk_level': 'CRITICAL' if len(tx_list) >= 3 else 'HIGH' if len(tx_list) >= 2 else 'MEDIUM'
            })

    alerts.sort(key=lambda x: x['count'], reverse=True)
    return alerts

def compute_ml_risk_index(G: nx.MultiDiGraph) -> Dict[str, float]:
    """
    Computes a composite Money Laundering Risk Index (0-100) for all nodes involved in financial transactions.
    Weighted combination of:
    - Cycle participation: 40%
    - Fan-in / Fan-out behavior: 30%
    - Structuring (sub-threshold) alerts: 30%
    """
    scores: Dict[str, float] = defaultdict(float)
    
    # 1. Cycle involvement
    cycles = detect_money_cycles(G)
    for c in cycles:
        for node in c['cycle_nodes']:
            weight = 40.0 if c['risk_level'] == 'CRITICAL' else 30.0 if c['risk_level'] == 'HIGH' else 20.0
            scores[node] += weight

    # 2. Fan-in / Fan-out
    fan_patterns = detect_fan_in_fan_out(G)
    for f in fan_patterns:
        scores[f['account_id']] += (f['risk_score'] * 0.3)

    # 3. Structuring
    struct_alerts = detect_structuring(G)
    for s in struct_alerts:
        bonus = 30.0 if s['count'] >= 3 else 20.0 if s['count'] >= 2 else 10.0
        scores[s['account_id']] += bonus

    # Normalize to 0-100 range
    final_scores = {}
    for node, raw_score in scores.items():
        final_scores[node] = min(100.0, round(raw_score, 1))
        
    return final_scores
