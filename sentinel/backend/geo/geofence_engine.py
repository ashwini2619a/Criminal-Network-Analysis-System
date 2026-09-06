"""
SENTINEL v2.0 — Geofence Engine
Performs point-in-radius spatial checks around sensitive locations
(witness residences, hideouts, crime scenes, courts, borders).
"""

from typing import List, Dict, Any
from backend.algorithms.colocation import haversine_distance

class GeofenceEngine:
    def __init__(self, locations: List[Dict[str, Any]] = None):
        self.locations = locations or []

    def load_locations(self, locations: List[Dict[str, Any]]):
        self.locations = locations

    def check_geofence_breach(self, lat: float, lon: float, suspect_id: str, suspect_name: str) -> List[Dict[str, Any]]:
        """
        Evaluates if target coordinate breaches any registered geofence perimeter.
        """
        breaches = []
        for loc in self.locations:
            loc_lat = float(loc.get("lat", 0.0))
            loc_lon = float(loc.get("lon", 0.0))
            radius = float(loc.get("geofence_radius_m", 500))

            dist = haversine_distance(lat, lon, loc_lat, loc_lon)
            if dist <= radius:
                breaches.append({
                    "suspect_id": suspect_id,
                    "suspect_name": suspect_name,
                    "location_id": loc.get("id"),
                    "location_name": loc.get("name"),
                    "location_type": loc.get("location_type", "SAFEHOUSE"),
                    "distance_meters": round(dist, 1),
                    "geofence_radius_m": radius,
                    "alert_level": "CRITICAL" if loc.get("location_type") in ("HIDEOUT", "CRIME_SCENE") else "HIGH"
                })

        return breaches
