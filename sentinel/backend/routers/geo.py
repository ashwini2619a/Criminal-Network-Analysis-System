"""
SENTINEL v2.0 — Geo-Intelligence & Real Map Router
Powers all 8 map layers:
- Base Map & Satellite
- Crime Scene Markers
- CDR Cell Tower Intelligence & Movement Trails
- Suspect Location Tracking & Geofences
- Investigator Drawing Overlays
- Multi-Suspect Comparison Trails & Co-Location Events
- Jurisdiction & District Boundaries
- Real-Time Intel Feed
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import List, Dict, Any, Optional
import json
import os

from backend.geo.tower_mapper import TowerMapper
from backend.geo.movement_tracker import MovementTracker
from backend.geo.geofence_engine import GeofenceEngine
from backend.geo.hotspot_predictor import HotspotPredictor
from backend.algorithms.colocation import ColocationDetector
from backend.config import SAMPLE_DIR

router = APIRouter(prefix="/api/geo", tags=["geo"])

@router.get("/towers")
async def get_cell_towers(request: Request, district: Optional[str] = None):
    t_path = os.path.join(SAMPLE_DIR, "cell_towers.json")
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            towers = json.load(f)
            if district:
                towers = [t for t in towers if t.get("district", "").lower() == district.lower()]
            return towers
    return []

@router.get("/trail/{phone_number}")
async def get_suspect_trail(phone_number: str, request: Request):
    c_path = os.path.join(SAMPLE_DIR, "cdrs.json")
    t_path = os.path.join(SAMPLE_DIR, "cell_towers.json")
    
    cdrs = []
    towers = []
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            cdrs = json.load(f)
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            towers = json.load(f)

    tm = TowerMapper(towers)
    tracker = MovementTracker(tm)
    return tracker.get_suspect_trail(phone_number, cdrs)

@router.get("/hotspots")
async def get_crime_hotspots(request: Request):
    i_path = os.path.join(SAMPLE_DIR, "incidents.json")
    if os.path.exists(i_path):
        with open(i_path, "r", encoding="utf-8") as f:
            incidents = json.load(f)
            predictor = HotspotPredictor()
            points = predictor.compute_heatmap_points(incidents)
            return {"points": points, "total_incidents": len(incidents)}
    return {"points": [], "total_incidents": 0}

@router.get("/colocations")
async def get_colocation_events(request: Request):
    c_path = os.path.join(SAMPLE_DIR, "cdrs.json")
    s_path = os.path.join(SAMPLE_DIR, "suspects.json")
    cdrs = []
    suspects = []
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            cdrs = json.load(f)
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            suspects = json.load(f)

    detector = ColocationDetector(max_distance_meters=500.0, max_time_diff_minutes=45)
    return detector.detect_colocations(cdrs, suspects)

@router.get("/geofences")
async def get_geofences(request: Request):
    l_path = os.path.join(SAMPLE_DIR, "locations.json")
    if os.path.exists(l_path):
        with open(l_path, "r", encoding="utf-8") as f:
            locations = json.load(f)
            return locations
    return []

@router.post("/compare")
async def compare_suspect_trails(body: Dict[str, List[str]], request: Request):
    phones = body.get("phones", [])
    c_path = os.path.join(SAMPLE_DIR, "cdrs.json")
    t_path = os.path.join(SAMPLE_DIR, "cell_towers.json")
    cdrs = []
    towers = []
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            cdrs = json.load(f)
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            towers = json.load(f)

    tm = TowerMapper(towers)
    tracker = MovementTracker(tm)

    results = {}
    for p in phones:
        results[p] = tracker.get_suspect_trail(p, cdrs)

    return results

@router.get("/incidents")
async def get_map_incidents(request: Request):
    i_path = os.path.join(SAMPLE_DIR, "incidents.json")
    if os.path.exists(i_path):
        with open(i_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
