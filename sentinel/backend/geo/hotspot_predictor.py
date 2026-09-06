"""
SENTINEL v2.0 — Crime Hotspot & Density Predictor
Aggregates spatial incidents to generate Leaflet.heat compatible points: [lat, lon, intensity].
"""

from typing import List, Dict, Any

class HotspotPredictor:
    def compute_heatmap_points(self, incidents: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Returns list of [lat, lon, intensity] formatted for leaflet.heat overlays.
        """
        points = []
        for inc in incidents:
            lat = float(inc.get("lat", 0.0))
            lon = float(inc.get("lon", 0.0))
            if lat != 0.0 and lon != 0.0:
                sev = inc.get("severity", "MEDIUM")
                intensity = 1.0 if sev == "CRITICAL" else (0.75 if sev == "HIGH" else 0.5)
                points.append([lat, lon, intensity])
        return points
