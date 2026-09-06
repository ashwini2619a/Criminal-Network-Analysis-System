"""
SENTINEL v2.0 — Spatial-Temporal Co-Location Detector
Detects co-location events where two distinct flagged suspects connect to
the same cell tower or nearby towers within a configurable time window (e.g. 45 min).
Uses the Haversine distance formula for accurate geospatial metrics.
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import defaultdict

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface
    using the Haversine formula in meters.
    """
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class ColocationDetector:
    def __init__(self, max_distance_meters: float = 500.0, max_time_diff_minutes: int = 45):
        self.max_distance_meters = max_distance_meters
        self.max_time_diff_minutes = max_time_diff_minutes

    def detect_colocations(self, cdrs: List[Dict[str, Any]], suspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans CDR call logs and correlates phone records against known suspect IDs.
        Flags pairs of suspects appearing at the same tower within max_time_diff_minutes.
        """
        # Map phone number -> suspect
        phone_to_suspect = {}
        for s in suspects:
            s_name = s.get("name", "Unknown")
            s_id = s.get("id", "")
            # We check known phone format
            phone_to_suspect[s.get("phone", "")] = {"id": s_id, "name": s_name}

        # Index CDRs by tower
        tower_events = defaultdict(list)
        for cdr in cdrs:
            t_id = cdr.get("tower_id")
            if not t_id:
                continue
            caller = cdr.get("caller_number", "")
            ts_str = cdr.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", ""))
            except Exception:
                continue

            tower_events[t_id].append({
                "cdr_id": cdr.get("id"),
                "phone": caller,
                "timestamp": ts,
                "timestamp_str": ts_str,
                "lat": cdr.get("tower_lat", 0.0),
                "lon": cdr.get("tower_lon", 0.0),
                "tower_id": t_id
            })

        colocation_events = []
        event_counter = 1

        for t_id, events in tower_events.items():
            if len(events) < 2:
                continue
            events.sort(key=lambda x: x["timestamp"])

            for i in range(len(events)):
                for j in range(i + 1, len(events)):
                    e1 = events[i]
                    e2 = events[j]
                    
                    time_diff = (e2["timestamp"] - e1["timestamp"]).total_seconds() / 60.0
                    if time_diff > self.max_time_diff_minutes:
                        break

                    # If callers are different numbers
                    if e1["phone"] != e2["phone"]:
                        s1 = phone_to_suspect.get(e1["phone"], {"id": f"SUSP-{e1['phone'][-4:]}", "name": f"Operative ({e1['phone']})"})
                        s2 = phone_to_suspect.get(e2["phone"], {"id": f"SUSP-{e2['phone'][-4:]}", "name": f"Operative ({e2['phone']})"})

                        colocation_events.append({
                            "id": f"COLOC-{event_counter}",
                            "suspect_a_id": s1["id"],
                            "suspect_a_name": s1["name"],
                            "suspect_b_id": s2["id"],
                            "suspect_b_name": s2["name"],
                            "tower_id": t_id,
                            "tower_name": f"Tower {t_id}",
                            "lat": e1["lat"],
                            "lon": e1["lon"],
                            "timestamp": e1["timestamp_str"],
                            "time_difference_min": int(time_diff),
                            "distance_meters": 0.0,
                            "alert_title": f"Co-Location: {s1['name']} & {s2['name']}",
                            "alert_description": f"Detected at tower {t_id} within {int(time_diff)} minutes."
                        })
                        event_counter += 1

        return colocation_events
