"""
SENTINEL v2.0 — Cross-Case Intelligence Linker (Auto-Feature 2)
Scans newly ingested entities against all historical cases to find
cross-case matches across phones, names, vehicle plates, accounts, and IMEIs.
"""

from typing import List, Dict, Any, Optional
from backend.pipeline.deduplicator import jaro_winkler_similarity

class CrossCaseLinker:
    """
    Automated Cross-Case Entity Linker:
    Flags when an entity appearing in an ingested case has prior appearances
    in other registered FIRs, intelligence reports, or surveillance files.
    """
    def __init__(self, graph_store=None):
        self.graph_store = graph_store

    def scan_for_cross_case_links(self, extracted_entities: List[Dict[str, Any]], current_case_id: str = "") -> List[Dict[str, Any]]:
        if not self.graph_store:
            return []

        cross_case_alerts = []
        G = self.graph_store.graph

        for ent in extracted_entities:
            text = ent.get("text", "").strip()
            ent_type = ent.get("entity_type", "")

            # 1. Exact Phone Match
            if ent_type == "PHONE":
                phone_node_id = f"PHONE_{text}"
                if G.has_node(phone_node_id):
                    # Check what cases / incidents are connected to this phone
                    associated_incidents = []
                    for nbr in list(G.neighbors(phone_node_id)) + list(G.predecessors(phone_node_id)):
                        node_data = G.nodes[nbr]
                        if node_data.get("node_type") == "Incident" and nbr != current_case_id:
                            associated_incidents.append(node_data.get("fir_no", nbr))

                    if associated_incidents:
                        cross_case_alerts.append({
                            "entity_type": "PHONE",
                            "entity_value": text,
                            "match_type": "EXACT",
                            "linked_cases": associated_incidents,
                            "alert_message": f"Phone {text} linked to prior case(s): {', '.join(associated_incidents)}"
                        })

            # 2. Vehicle Registration Match
            elif ent_type == "VEHICLE_REG":
                for n, data in G.nodes(data=True):
                    if data.get("node_type") == "Vehicle":
                        reg = data.get("registration_no", "").replace("-", "").replace(" ", "").upper()
                        clean_text = text.replace("-", "").replace(" ", "").upper()
                        if reg and reg == clean_text:
                            # Find incidents where vehicle was used
                            linked = []
                            for nbr in list(G.neighbors(n)) + list(G.predecessors(n)):
                                if G.nodes[nbr].get("node_type") == "Incident" and nbr != current_case_id:
                                    linked.append(G.nodes[nbr].get("fir_no", nbr))
                            if linked:
                                cross_case_alerts.append({
                                    "entity_type": "VEHICLE",
                                    "entity_value": text,
                                    "match_type": "EXACT",
                                    "linked_cases": linked,
                                    "alert_message": f"Vehicle {text} detected in historical case(s): {', '.join(linked)}"
                                })

            # 3. Fuzzy Person Name Match
            elif ent_type == "PERSON":
                for n, data in G.nodes(data=True):
                    if data.get("node_type") == "Person":
                        p_name = data.get("name", "")
                        sim = jaro_winkler_similarity(text, p_name)
                        if sim >= 0.88:
                            # Look up incidents linked to this person
                            prior_firs = []
                            for nbr in G.neighbors(n):
                                if G.nodes[nbr].get("node_type") == "Incident" and nbr != current_case_id:
                                    prior_firs.append(G.nodes[nbr].get("fir_no", nbr))
                            if prior_firs:
                                cross_case_alerts.append({
                                    "entity_type": "PERSON",
                                    "entity_value": f"{text} ≈ {p_name} ({int(sim*100)}% match)",
                                    "match_type": "FUZZY",
                                    "linked_cases": prior_firs,
                                    "alert_message": f"Suspect '{text}' matches '{p_name}' linked to FIR(s): {', '.join(prior_firs)}"
                                })

        return cross_case_alerts
