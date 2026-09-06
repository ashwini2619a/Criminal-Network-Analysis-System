"""
SENTINEL v2.0 — Excel & CSV Intelligence Exporter
Exports suspect rosters, CDR logs, financial transactions, and blockchain audits
to CSV and multi-sheet Excel files (.xlsx).
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any

from backend.config import EXPORTS_DIR

class ExcelExporter:
    def export_suspects_csv(self, suspects: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            filename = f"SUSPECTS_EXPORT_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
        path = os.path.join(EXPORTS_DIR, filename)

        fieldnames = ["id", "name", "gender", "age", "district", "state", "risk_score", "threat_level", "status", "criminal_record_no"]
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for s in suspects:
                writer.writerow(s)
        return path

    def export_financial_transactions_csv(self, transactions: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            filename = f"TRANSACTIONS_EXPORT_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
        path = os.path.join(EXPORTS_DIR, filename)

        fieldnames = ["id", "sender_name", "sender_account", "receiver_name", "receiver_account", "amount", "utr", "timestamp", "transaction_type", "pattern"]
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for t in transactions:
                writer.writerow(t)
        return path

    def export_cdr_logs_csv(self, cdrs: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            filename = f"CDR_EXPORT_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
        path = os.path.join(EXPORTS_DIR, filename)

        fieldnames = ["id", "caller_number", "receiver_number", "duration_sec", "timestamp", "tower_id", "tower_lat", "tower_lon", "caller_imei"]
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for c in cdrs:
                writer.writerow(c)
        return path
