"""
SENTINEL v2.0 — Movement Tracker & CDR Trail Replay
Builds chronological movement polylines from CDR tower hits, computes
dwell-time percentages per district/zone, and classifies time-of-day markers.
"""

from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

class MovementTracker:
    def __init__(self, tower_mapper=None):
        self.tower_mapper = tower_mapper

    def get_time_of_day_color(self, hour: int) -> str:
        if 6 <= hour < 12:
            return "#facc15"  # Yellow - Morning
        elif 12 <= hour < 18:
            return "#fb923c"  # Orange - Afternoon
        else:
            return "#ef4444"  # Red - Night

    def get_suspect_trail(self, phone_number: str, cdrs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds chronological movement trail for a suspect's phone number.
        """
        user_cdrs = [
            c for c in cdrs 
            if c.get("caller_number") == phone_number or c.get("receiver_number") == phone_number
        ]
        
        # Sort chronologically
        user_cdrs.sort(key=lambda x: x.get("timestamp", ""))

        waypoints = []
        district_hits = []

        for idx, c in enumerate(user_cdrs):
            ts_str = c.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", ""))
                hour = dt.hour
                date_formatted = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                hour = 12
                date_formatted = ts_str

            lat = float(c.get("tower_lat", 0.0))
            lon = float(c.get("tower_lon", 0.0))

            if lat != 0.0 and lon != 0.0:
                t_id = c.get("tower_id", "")
                t_info = self.tower_mapper.get_tower(t_id) if self.tower_mapper else None
                dist = t_info.get("district", "Unknown") if t_info else "National Highway"
                district_hits.append(dist)

                waypoints.append({
                    "sequence": idx + 1,
                    "lat": lat,
                    "lon": lon,
                    "tower_id": t_id,
                    "district": dist,
                    "timestamp": ts_str,
                    "formatted_time": date_formatted,
                    "hour": hour,
                    "color": self.get_time_of_day_color(hour),
                    "duration_sec": c.get("duration_sec", 60),
                    "call_partner": c.get("receiver_number") if c.get("caller_number") == phone_number else c.get("caller_number")
                })

        # Calculate dwell percentages per district
        dwell_percentages = {}
        if district_hits:
            counts = Counter(district_hits)
            total = len(district_hits)
            for d, count in counts.items():
                dwell_percentages[d] = round((count / total) * 100.0, 1)

        return {
            "phone_number": phone_number,
            "total_hits": len(waypoints),
            "waypoints": waypoints,
            "dwell_percentages": dwell_percentages,
            "polyline_coordinates": [[w["lat"], w["lon"]] for w in waypoints]
        }
