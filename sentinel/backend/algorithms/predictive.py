"""
SENTINEL v2.0 — Predictive Intelligence Engine (Auto-Feature 8)
Implements predictive crime hotspot forecasting, recidivism risk evaluation,
and network recruitment trajectory modeling.
"""

from typing import List, Dict, Any
from collections import defaultdict
import math

class PredictiveIntelligence:
    """
    Analyzes historical spatial, network, and behavioral markers
    to forecast prospective threat patterns.
    """
    def __init__(self, graph_store=None):
        self.graph_store = graph_store

    def predict_crime_hotspots(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Kernel Density / Cluster aggregation forecasting high-risk zones.
        Clusters historical incident coordinates by district & location proximity.
        """
        district_counts = defaultdict(list)
        for inc in incidents:
            dist = inc.get("district", "Unknown")
            lat = inc.get("lat", 0.0)
            lon = inc.get("lon", 0.0)
            sev = inc.get("severity", "MEDIUM")
            weight = 3.0 if sev == "CRITICAL" else (2.0 if sev == "HIGH" else 1.0)
            district_counts[dist].append((lat, lon, weight))

        hotspots = []
        for dist, coords in district_counts.items():
            if not coords:
                continue
            total_weight = sum(w for _, _, w in coords)
            avg_lat = sum(lat * w for lat, _, w in coords) / total_weight
            avg_lon = sum(lon * w for _, lon, w in coords) / total_weight

            # Risk density score scaled 0-100
            density_score = min(98.5, round(total_weight * 7.5 + len(coords) * 4.2, 1))

            hotspots.append({
                "district": dist,
                "center_lat": round(avg_lat, 5),
                "center_lon": round(avg_lon, 5),
                "incident_count": len(coords),
                "weighted_risk": density_score,
                "predicted_threat_level": "CRITICAL" if density_score > 75 else ("HIGH" if density_score > 50 else "MEDIUM"),
                "recommended_action": f"Deploy intensified night patrol and checkpoint surveillance in {dist} corridor."
            })

        hotspots.sort(key=lambda x: x["weighted_risk"], reverse=True)
        return hotspots

    def compute_recidivism_risk(self, suspect: Dict[str, Any], network_degree: int = 5, betweenness: float = 0.05) -> Dict[str, Any]:
        """
        Calculates recidivism probability based on criminal record history,
        network centrality position, and violent offense IPC tags.
        """
        base_score = float(suspect.get("risk_score", 50.0))
        
        # Factor in network connectivity: highly connected individuals recidivate faster
        net_factor = min(25.0, network_degree * 1.8 + betweenness * 100.0)
        
        # Past record indicator
        record_penalty = 15.0 if suspect.get("criminal_record_no") else 5.0
        
        recidivism_prob = min(99.0, max(10.0, round((base_score * 0.5) + net_factor + record_penalty, 1)))

        return {
            "suspect_id": suspect.get("id"),
            "name": suspect.get("name"),
            "recidivism_score": recidivism_prob,
            "risk_tier": "VERY_HIGH" if recidivism_prob > 80 else ("HIGH" if recidivism_prob > 60 else "MODERATE"),
            "key_drivers": [
                f"Network central bridge weight: +{round(net_factor, 1)}%",
                f"Prior registered offense record: +{record_penalty}%",
                f"Baseline threat index: {base_score}"
            ]
        }

    def predict_network_growth(self, G) -> List[Dict[str, Any]]:
        """
        Identifies syndicates exhibiting active communication expansion
        into new peripheral contacts.
        """
        high_recruitment_nodes = []
        for n, data in G.nodes(data=True):
            if data.get("node_type") == "Person":
                out_deg = G.out_degree(n) if hasattr(G, 'out_degree') else G.degree(n)
                in_deg = G.in_degree(n) if hasattr(G, 'in_degree') else G.degree(n)

                # High ratio of outward connections indicates recruiter behavior
                if out_deg >= 4 and out_deg > in_deg:
                    high_recruitment_nodes.append({
                        "node_id": n,
                        "name": data.get("name", n),
                        "recruitment_rate": round(out_deg / max(1, in_deg), 2),
                        "outward_contacts": out_deg,
                        "threat_indicator": "Active Syndicate Recruiter"
                    })

        high_recruitment_nodes.sort(key=lambda x: x["recruitment_rate"], reverse=True)
        return high_recruitment_nodes[:10]
