import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

def build_event_timeline(G: nx.MultiDiGraph) -> List[Dict[str, Any]]:
    """
    Builds a unified chronological timeline of all incidents, communication calls,
    and financial transfers across all network entities.
    """
    events = []

    # 1. Incidents
    for n, d in G.nodes(data=True):
        if d.get('node_type') == 'Incident' or d.get('type') == 'Incident':
            ts = d.get('date_time')
            if ts:
                events.append({
                    'id': f"INC_{n}",
                    'timestamp': ts,
                    'event_type': 'INCIDENT',
                    'title': f"FIR: {d.get('fir_no', 'N/A')}",
                    'description': d.get('description', ''),
                    'severity': d.get('severity', 'MEDIUM'),
                    'location': d.get('police_station', ''),
                    'entities': [n]
                })

    # 2. Calls
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            ts = d.get('timestamp')
            if ts:
                u_label = G.nodes.get(u, {}).get('label') or u
                v_label = G.nodes.get(v, {}).get('label') or v
                events.append({
                    'id': f"CALL_{k}_{u}_{v}",
                    'timestamp': ts,
                    'event_type': 'CALL',
                    'title': f"Call: {u_label} -> {v_label}",
                    'description': f"Duration: {d.get('duration_sec', 0)}s, Tower: {d.get('tower_id', 'N/A')}",
                    'severity': 'LOW',
                    'entities': [u, v]
                })

    # 3. Transactions
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'TRANSFERRED_MONEY' or d.get('type') == 'TRANSFERRED_MONEY':
            ts = d.get('timestamp')
            if ts:
                u_label = G.nodes.get(u, {}).get('label') or u
                v_label = G.nodes.get(v, {}).get('label') or v
                amt = float(d.get('amount', 0))
                sev = 'CRITICAL' if amt >= 500000 else 'HIGH' if amt >= 50000 else 'MEDIUM'
                events.append({
                    'id': f"TX_{k}_{u}_{v}",
                    'timestamp': ts,
                    'event_type': 'TRANSACTION',
                    'title': f"Transfer: ₹{amt:,.2f}",
                    'description': f"{u_label} -> {v_label} via {d.get('transaction_type', 'NEFT')} (UTR: {d.get('utr', 'N/A')})",
                    'severity': sev,
                    'entities': [u, v]
                })

    # Sort chronologically
    def parse_ts(x):
        try:
            return datetime.fromisoformat(x['timestamp'])
        except Exception:
            return datetime.min

    events.sort(key=parse_ts)
    return events

def detect_pre_crime_spikes(G: nx.MultiDiGraph, window_hours: int = 48) -> List[Dict[str, Any]]:
    """
    Detects unusual communication surges immediately prior to criminal incidents (24-48 hours before).
    """
    # 1. Gather incidents
    incidents = []
    for n, d in G.nodes(data=True):
        if d.get('node_type') == 'Incident' or d.get('type') == 'Incident':
            ts = d.get('date_time')
            if ts:
                try:
                    incidents.append({
                        'id': n,
                        'fir_no': d.get('fir_no', 'N/A'),
                        'time': datetime.fromisoformat(ts),
                        'desc': d.get('description', '')
                    })
                except Exception:
                    pass

    # 2. Gather calls
    calls = []
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            ts = d.get('timestamp')
            if ts:
                try:
                    calls.append({
                        'time': datetime.fromisoformat(ts),
                        'caller': u,
                        'receiver': v
                    })
                except Exception:
                    pass

    if not calls or not incidents:
        return []

    # Calculate baseline call rate per window
    min_time = min(c['time'] for c in calls)
    max_time = max(c['time'] for c in calls)
    total_span_hours = max(1.0, (max_time - min_time).total_seconds() / 3600.0)
    baseline_rate = (len(calls) / total_span_hours) * window_hours

    spikes = []
    for inc in incidents:
        inc_time = inc['time']
        window_start = inc_time - timedelta(hours=window_hours)
        
        # Calls inside pre-crime window
        calls_in_window = [c for c in calls if window_start <= c['time'] < inc_time]
        count = len(calls_in_window)
        
        spike_ratio = round(count / max(1.0, baseline_rate), 2)
        z_score = round((count - baseline_rate) / max(1.0, (baseline_rate ** 0.5)), 2)
        if spike_ratio >= 1.5 or count >= 4:
            involved = set()
            for c in calls_in_window:
                involved.add(c['caller'])
                involved.add(c['receiver'])

            spikes.append({
                'incident_id': inc['id'],
                'fir_no': inc['fir_no'],
                'incident_date': inc_time.isoformat(),
                'incident_desc': inc['desc'][:100] + '...',
                'call_count': count,
                'baseline_count': round(baseline_rate, 1),
                'spike_ratio': spike_ratio,
                'z_score': z_score,
                'involved_entity_count': len(involved),
                'threat_level': 'CRITICAL' if (spike_ratio >= 3.0 or z_score >= 3.0) else 'HIGH'
            })

    spikes.sort(key=lambda x: x['spike_ratio'], reverse=True)
    return spikes

def detect_post_crime_silence(G: nx.MultiDiGraph, silence_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Detects post-crime 'radio silence':
    Suspects actively calling before an incident, then dropping communication by >70%
    immediately following the crime to evade CDR monitoring.
    """
    # 1. Incidents
    incidents = []
    for n, d in G.nodes(data=True):
        if d.get('node_type') == 'Incident' or d.get('type') == 'Incident':
            ts = d.get('date_time')
            if ts:
                try:
                    incidents.append({
                        'id': n,
                        'fir_no': d.get('fir_no', 'N/A'),
                        'time': datetime.fromisoformat(ts)
                    })
                except Exception:
                    pass

    # 2. Calls per entity
    entity_calls: Dict[str, List[datetime]] = defaultdict(list)
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            ts = d.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    entity_calls[u].append(dt)
                    entity_calls[v].append(dt)
                except Exception:
                    pass

    silence_alerts = []
    for inc in incidents:
        inc_time = inc['time']
        pre_start = inc_time - timedelta(hours=silence_hours)
        post_end = inc_time + timedelta(hours=silence_hours)

        for entity_id, times in entity_calls.items():
            pre_count = len([t for t in times if pre_start <= t < inc_time])
            post_count = len([t for t in times if inc_time <= t <= post_end])

            if pre_count >= 2 and post_count == 0:
                drop_pct = 100.0
                node_data = G.nodes.get(entity_id, {})
                name = node_data.get('label') or node_data.get('name') or entity_id
                
                silence_alerts.append({
                    'incident_id': inc['id'],
                    'fir_no': inc['fir_no'],
                    'entity_id': entity_id,
                    'entity_name': name,
                    'pre_activity_count': pre_count,
                    'post_activity_count': post_count,
                    'drop_percentage': drop_pct,
                    'alert': 'Complete Post-Incident Radio Silence'
                })

    return silence_alerts[:15]

def compute_activity_patterns(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Aggregates communication patterns: hourly distribution (24 hrs), daily distribution (7 days),
    peak activity windows, and date bounds.
    """
    hourly = [0] * 24
    daily = [0] * 7  # 0=Mon, 6=Sun
    all_timestamps = []

    for u, v, k, d in G.edges(data=True, keys=True):
        ts = d.get('timestamp')
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                hourly[dt.hour] += 1
                daily[dt.weekday()] += 1
                all_timestamps.append(dt)
            except Exception:
                pass

    peak_hours = sorted(range(24), key=lambda h: hourly[h], reverse=True)[:3]
    total_events = sum(hourly)

    date_range = {
        'start': min(all_timestamps).strftime("%Y-%m-%d") if all_timestamps else "2024-01-01",
        'end': max(all_timestamps).strftime("%Y-%m-%d") if all_timestamps else "2024-12-31"
    }

    return {
        'hourly_distribution': hourly,
        'daily_distribution': daily,
        'peak_hours': peak_hours,
        'total_events': total_events,
        'date_range': date_range
    }
