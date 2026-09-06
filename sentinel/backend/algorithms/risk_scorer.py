"""
SENTINEL v2.0 — Multi-Factor Threat & Risk Scorer
Computes normalized risk scores (0-100) combining structural network centrality,
criminal records, violent IPC section severity, and financial laundering flags.
"""

from typing import Dict, Any

class ThreatRiskScorer:
    def __init__(self):
        # Weights for composite threat calculation
        self.w_centrality = 0.35
        self.w_offense_history = 0.30
        self.w_financial_flags = 0.20
        self.w_communication = 0.15

    def calculate_composite_risk(self, person_data: Dict[str, Any], centrality_score: float = 0.5, has_hawala: bool = False, call_surge: bool = False) -> float:
        """
        Returns normalized risk score between 0.0 and 100.0.
        """
        # 1. Base offense score
        record = person_data.get("criminal_record_no", "")
        status = person_data.get("status", "SUSPECT")
        
        base_offense = 50.0
        if status in ("CONVICTED", "ACCUSED"):
            base_offense += 30.0
        elif status == "ABSCONDING":
            base_offense += 40.0
        if record:
            base_offense += 10.0
        base_offense = min(100.0, base_offense)

        # 2. Centrality contribution (scaled 0-100)
        centrality_val = min(100.0, centrality_score * 100.0)

        # 3. Financial flags
        financial_val = 90.0 if has_hawala else (60.0 if person_data.get("suspicious_financials") else 20.0)

        # 4. Communication surge flags
        comm_val = 95.0 if call_surge else 30.0

        composite = (
            (self.w_centrality * centrality_val) +
            (self.w_offense_history * base_offense) +
            (self.w_financial_flags * financial_val) +
            (self.w_communication * comm_val)
        )

        return round(min(100.0, max(1.0, composite)), 1)
