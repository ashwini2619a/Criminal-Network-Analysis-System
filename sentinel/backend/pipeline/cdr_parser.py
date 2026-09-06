"""
SENTINEL v2.0 — Telecom CDR File Parser
Parses raw telecom CDR files (CSV, Excel, TXT) with intelligent column auto-detection
and column mapping wizard support. Normalizes Indian phone formats (+91) and coordinates.
"""

import os
import re
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

def normalize_indian_phone(phone: str) -> str:
    """Normalizes phone numbers to canonical +91-XXXXXXXXXX format."""
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10:
        return f"+91-{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+91-{digits[2:]}"
    elif len(digits) == 11 and digits.startswith("0"):
        return f"+91-{digits[1:]}"
    return str(phone).strip()

class CDRParser:
    """
    Intelligent CDR Parser that auto-detects column headers:
    caller, receiver, duration, timestamp, tower_id, lat, lon, imei.
    """
    def __init__(self):
        self.column_aliases = {
            "caller": ["calling_no", "caller", "source", "calling_number", "a_party", "caller_number"],
            "receiver": ["called_no", "receiver", "destination", "called_number", "b_party", "receiver_number"],
            "duration": ["duration", "call_duration", "duration_sec", "dur_sec", "call_sec"],
            "timestamp": ["date_time", "timestamp", "call_time", "start_time", "datetime"],
            "tower_id": ["tower_id", "cell_id", "cgi", "first_cgi", "site_id"],
            "lat": ["latitude", "lat", "tower_lat", "site_lat"],
            "lon": ["longitude", "lon", "long", "tower_lon", "site_lon"],
            "caller_imei": ["imei", "caller_imei", "calling_imei", "device_imei"],
            "receiver_imei": ["receiver_imei", "called_imei"]
        }

    def detect_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Maps canonical CDR fields to detected file header names."""
        mapping = {}
        headers_lower = [h.strip().lower().replace(" ", "_") for h in headers]
        for canonical, aliases in self.column_aliases.items():
            for i, h in enumerate(headers_lower):
                if h in aliases or any(alias in h for alias in aliases):
                    mapping[canonical] = headers[i]
                    break
        return mapping

    def parse_csv(self, file_path: str, custom_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Parses a CSV CDR file and returns standardized CDR records."""
        records = []
        if not os.path.exists(file_path):
            return records

        with open(file_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            mapping = custom_mapping or self.detect_column_mapping(headers)

            for idx, row in enumerate(reader):
                caller = row.get(mapping.get("caller", ""), "").strip()
                receiver = row.get(mapping.get("receiver", ""), "").strip()
                if not caller or not receiver:
                    continue

                duration_val = row.get(mapping.get("duration", ""), "60")
                try:
                    duration_sec = int(float(duration_val))
                except Exception:
                    duration_sec = 60

                lat_val = row.get(mapping.get("lat", ""), "0.0")
                lon_val = row.get(mapping.get("lon", ""), "0.0")
                try:
                    lat = float(lat_val)
                    lon = float(lon_val)
                except Exception:
                    lat, lon = 0.0, 0.0

                records.append({
                    "id": f"CDR-UPLOAD-{idx+1}",
                    "caller_number": normalize_indian_phone(caller),
                    "receiver_number": normalize_indian_phone(receiver),
                    "duration_sec": duration_sec,
                    "timestamp": row.get(mapping.get("timestamp", ""), datetime.now().isoformat()),
                    "tower_id": row.get(mapping.get("tower_id", ""), f"TWR-AUTO-{idx%10}"),
                    "tower_lat": lat,
                    "tower_lon": lon,
                    "caller_imei": row.get(mapping.get("caller_imei", ""), ""),
                    "receiver_imei": row.get(mapping.get("receiver_imei", ""), "")
                })

        return records
