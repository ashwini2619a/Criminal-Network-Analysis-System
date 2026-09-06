"""
SENTINEL v2.0 — Cell Tower Geospatial Mapper
Maps telecom tower coordinates, coverage azimuth sectors, and operator metrics.
"""

from typing import List, Dict, Any, Optional

class TowerMapper:
    def __init__(self, towers: Optional[List[Dict[str, Any]]] = None):
        self.towers = towers or []
        self.tower_index = {t.get("tower_id", t.get("id")): t for t in self.towers}

    def load_towers(self, towers: List[Dict[str, Any]]):
        self.towers = towers
        self.tower_index = {t.get("tower_id", t.get("id")): t for t in self.towers}

    def get_tower(self, tower_id: str) -> Optional[Dict[str, Any]]:
        return self.tower_index.get(tower_id)

    def get_all_towers(self) -> List[Dict[str, Any]]:
        return self.towers

    def get_towers_by_district(self, district: str) -> List[Dict[str, Any]]:
        return [t for t in self.towers if t.get("district", "").lower() == district.lower()]
