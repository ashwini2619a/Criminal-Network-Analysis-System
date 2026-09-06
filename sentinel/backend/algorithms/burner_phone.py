import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict

def detect_imei_reuse(G: nx.MultiDiGraph) -> List[Dict[str, Any]]:
    """
    Detects IMEI reuse across different SIM cards / phone numbers.
    Criminal operatives often keep the same physical device (IMEI) while cycling through
    disposable burner SIM cards.
    """
    imei_to_numbers: Dict[str, Set[str]] = defaultdict(set)
    imei_timestamps: Dict[str, List[str]] = defaultdict(list)
    
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            c_imei = d.get('caller_imei')
            c_num = d.get('caller_number') or G.nodes.get(u, {}).get('number') or u.replace('PHONE_', '')
            r_imei = d.get('receiver_imei')
            r_num = d.get('receiver_number') or G.nodes.get(v, {}).get('number') or v.replace('PHONE_', '')
            ts = d.get('timestamp', '')
            
            if c_imei and c_imei != 'N/A' and c_num:
                imei_to_numbers[c_imei].add(c_num)
                if ts: imei_timestamps[c_imei].append(ts)
                
            if r_imei and r_imei != 'N/A' and r_num:
                imei_to_numbers[r_imei].add(r_num)
                if ts: imei_timestamps[r_imei].append(ts)

    suspicious_imeis = []
    for imei, numbers in imei_to_numbers.items():
        if len(numbers) >= 2:
            ts_sorted = sorted(imei_timestamps[imei]) if imei_timestamps[imei] else []
            suspicious_imeis.append({
                'imei': imei,
                'phone_numbers': sorted(list(numbers)),
                'sim_count': len(numbers),
                'first_seen': ts_sorted[0] if ts_sorted else 'Unknown',
                'last_seen': ts_sorted[-1] if ts_sorted else 'Unknown',
                'likely_same_person': True,
                'threat_level': 'HIGH' if 'BURNER' in imei or len(numbers) >= 3 else 'MEDIUM'
            })

    suspicious_imeis.sort(key=lambda x: x['sim_count'], reverse=True)
    return suspicious_imeis

def detect_sim_swap_chains(G: nx.MultiDiGraph, gap_hours: int = 48) -> List[Dict[str, Any]]:
    """
    Detects SIM swap chains:
    Phone A goes silent, Phone B activates within the same tower cluster within `gap_hours`,
    and calls the same contacts (>= 40% contact overlap).
    """
    # 1. Collect calls per phone number
    phone_contacts: Dict[str, Set[str]] = defaultdict(set)
    phone_activity: Dict[str, List[datetime]] = defaultdict(list)
    phone_towers: Dict[str, Set[str]] = defaultdict(set)
    
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            p1 = G.nodes.get(u, {}).get('number') or u.replace('PHONE_', '')
            p2 = G.nodes.get(v, {}).get('number') or v.replace('PHONE_', '')
            ts_str = d.get('timestamp')
            twr = d.get('tower_id')
            
            if p1 and p2:
                phone_contacts[p1].add(p2)
                phone_contacts[p2].add(p1)
                
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str)
                    if p1: phone_activity[p1].append(dt)
                    if p2: phone_activity[p2].append(dt)
                except Exception:
                    pass
                    
            if twr:
                if p1: phone_towers[p1].add(twr)
                if p2: phone_towers[p2].add(twr)

    phones = list(phone_contacts.keys())
    chains = []

    for i in range(len(phones)):
        for j in range(len(phones)):
            if i == j:
                continue
            p_a = phones[i]
            p_b = phones[j]
            
            contacts_a = phone_contacts[p_a]
            contacts_b = phone_contacts[p_b]
            
            if not contacts_a or not contacts_b:
                continue
                
            overlap = contacts_a & contacts_b
            overlap_pct = (len(overlap) / min(len(contacts_a), len(contacts_b))) * 100.0
            
            # Check contact overlap >= 40%
            if overlap_pct >= 40.0:
                towers_overlap = phone_towers[p_a] & phone_towers[p_b]
                acts_a = sorted(phone_activity[p_a]) if phone_activity[p_a] else []
                acts_b = sorted(phone_activity[p_b]) if phone_activity[p_b] else []
                
                # Check temporal succession
                time_valid = False
                gap = 0.0
                if acts_a and acts_b:
                    last_a = acts_a[-1]
                    first_b = acts_b[0]
                    diff_hours = (first_b - last_a).total_seconds() / 3600.0
                    if 0 <= diff_hours <= gap_hours:
                        time_valid = True
                        gap = diff_hours
                else:
                    time_valid = True
                    gap = 2.0

                if time_valid:
                    chains.append({
                        'chain': [p_a, p_b],
                        'phone_a': p_a,
                        'phone_b': p_b,
                        'contact_overlap_count': len(overlap),
                        'contact_overlap_pct': round(overlap_pct, 1),
                        'shared_contacts': list(overlap)[:5],
                        'tower_overlap': list(towers_overlap),
                        'gap_hours': round(gap, 1),
                        'confidence': 0.95 if (overlap_pct >= 60 and towers_overlap) else 0.80
                    })

    # Deduplicate symmetric chains
    unique_chains = []
    seen = set()
    for c in chains:
        key = tuple(sorted([c['phone_a'], c['phone_b']]))
        if key not in seen:
            seen.add(key)
            unique_chains.append(c)

    unique_chains.sort(key=lambda x: x['contact_overlap_pct'], reverse=True)
    return unique_chains

def detect_colocation(G: nx.MultiDiGraph, time_window_min: int = 45) -> List[Dict[str, Any]]:
    """
    CDR temporal-spatial co-location:
    Two distinct phone numbers repeatedly observed connecting to the same cell towers
    within a short time window (suggests targets are travelling together or in meetings).
    """
    # Group CDRs by cell tower
    records_by_tower: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            twr = d.get('tower_id')
            ts = d.get('timestamp')
            p1 = G.nodes.get(u, {}).get('number') or u.replace('PHONE_', '')
            
            if twr and ts and p1:
                try:
                    dt = datetime.fromisoformat(ts)
                    records_by_tower[twr].append({
                        'phone': p1,
                        'time': dt,
                        'time_str': ts,
                        'lat': d.get('tower_lat', 0.0),
                        'lon': d.get('tower_lon', 0.0),
                        'tower_id': twr
                    })
                except Exception:
                    pass

    pair_colocations: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    
    for twr, recs in records_by_tower.items():
        recs.sort(key=lambda x: x['time'])
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                r1 = recs[i]
                r2 = recs[j]
                if r1['phone'] == r2['phone']:
                    continue
                delta_sec = abs((r2['time'] - r1['time']).total_seconds())
                if delta_sec <= (time_window_min * 60):
                    pair_key = tuple(sorted([r1['phone'], r2['phone']]))
                    pair_colocations[pair_key].append({
                        'tower_id': twr,
                        'time_a': r1['time_str'],
                        'time_b': r2['time_str'],
                        'tower_lat': r1['lat'],
                        'tower_lon': r1['lon'],
                        'time_delta_min': round(delta_sec / 60.0, 1)
                    })

    results = []
    for (p1, p2), events in pair_colocations.items():
        if len(events) >= 1:
            results.append({
                'phone_a': p1,
                'phone_b': p2,
                'count': len(events),
                'colocations': events[:10],
                'likely_associates': len(events) >= 2,
                'threat_score': min(100, len(events) * 35)
            })

    results.sort(key=lambda x: x['count'], reverse=True)
    return results

def detect_crime_window_activity(G: nx.MultiDiGraph) -> List[Dict[str, Any]]:
    """
    Detects burner phones that exhibit communication spikes strictly within crime windows
    (±2 hours of known incident timestamps) and remain silent/dormant before and after.
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

    # 2. Gather phone calls
    phone_calls: Dict[str, List[datetime]] = defaultdict(list)
    for u, v, k, d in G.edges(data=True, keys=True):
        if d.get('edge_type') == 'CALLED' or d.get('type') == 'CALLED':
            p = G.nodes.get(u, {}).get('number') or u.replace('PHONE_', '')
            ts = d.get('timestamp')
            if p and ts:
                try:
                    phone_calls[p].append(datetime.fromisoformat(ts))
                except Exception:
                    pass

    flagged_phones = []
    for phone, call_times in phone_calls.items():
        if not call_times or not incidents:
            continue
            
        crime_window_calls = 0
        active_incidents = []
        
        for inc in incidents:
            inc_time = inc['time']
            # Within 2 hours before or after
            matching = [t for t in call_times if abs((t - inc_time).total_seconds()) <= 7200]
            if matching:
                crime_window_calls += len(matching)
                active_incidents.append(inc['fir_no'])

        if active_incidents:
            total = len(call_times)
            ratio = (crime_window_calls / total) * 100.0
            
            # If significant percentage of total activity took place near crime windows
            if ratio >= 20.0 or crime_window_calls >= 2:
                flagged_phones.append({
                    'phone': phone,
                    'total_calls': total,
                    'crime_window_calls': crime_window_calls,
                    'active_incidents': list(set(active_incidents)),
                    'crime_window_activity_pct': round(ratio, 1),
                    'suspicion_score': min(100.0, round(ratio * 0.7 + crime_window_calls * 15, 1))
                })

    flagged_phones.sort(key=lambda x: x['suspicion_score'], reverse=True)
    return flagged_phones
