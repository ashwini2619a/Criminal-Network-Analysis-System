import sqlite3
import os
import json
from typing import Dict, List, Any, Optional

CRIMINAL_HISTORY_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'criminal_history.sqlite')

class CriminalHistoryManager:
    """
    CCTNS-compatible Criminal History & Prior Conviction Record Manager.
    Stores historical FIR records, court chargesheets, convictions, and warrant statuses
    that directly modulate algorithmic suspect risk scores.
    """
    def __init__(self, db_path: str = CRIMINAL_HISTORY_DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._seed_default_records()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS criminal_history (
                    suspect_id TEXT PRIMARY KEY,
                    name TEXT,
                    aliases TEXT,
                    prior_firs_count INTEGER DEFAULT 0,
                    past_convictions INTEGER DEFAULT 0,
                    chargesheets_filed INTEGER DEFAULT 0,
                    active_warrants INTEGER DEFAULT 0,
                    bail_status TEXT DEFAULT 'CLEAN',
                    gang_affiliation TEXT,
                    history_cases TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _seed_default_records(self):
        """Seed default realistic records for core demo suspects if empty."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM criminal_history")
            if cur.fetchone()[0] > 0:
                return

            records = [
                (
                    "PERSON_VIKRAM_SINHA",
                    "Vikram Sinha",
                    json.dumps(["Vicky", "Bhaiya Ji"]),
                    8,
                    2,
                    6,
                    1,
                    "JUMPED_BAIL",
                    "Ranchi Syndicate",
                    json.dumps([
                        {"fir_no": "FIR/2019/084", "year": 2019, "sections": ["302", "34 IPC"], "court": "Ranchi Sessions Court", "status": "CONVICTED", "description": "Lethal assault and gang intimidation in Doranda area"},
                        {"fir_no": "FIR/2021/142", "year": 2021, "sections": ["384", "120B IPC"], "court": "Patna Special CBI", "status": "CHARGESHEET_FILED", "description": "Extortion of highway construction contractors"},
                        {"fir_no": "FIR/2023/310", "year": 2023, "sections": ["25/27 Arms Act"], "court": "Bokaro CJM Court", "status": "NBW_ACTIVE", "description": "Illegal acquisition and supply of 9mm semi-automatic pistols"}
                    ])
                ),
                (
                    "PERSON_DEEPAK_TIWARI",
                    "Deepak Tiwari",
                    json.dumps(["Pandit Ji", "Broker"]),
                    4,
                    1,
                    3,
                    0,
                    "ON_BAIL",
                    "Delhi Hawala Network",
                    json.dumps([
                        {"fir_no": "FIR/2020/091", "year": 2020, "sections": ["420", "467 IPC"], "court": "Saket District Court", "status": "CONVICTED", "description": "Forging commercial bank guarantees for shell exporters"},
                        {"fir_no": "FIR/2022/198", "year": 2022, "sections": ["120B IPC", "Sec 3/4 PMLA"], "court": "Rouse Avenue Special Court", "status": "UNDER_TRIAL", "description": "Inter-state Hawala transit hub operator"}
                    ])
                ),
                (
                    "PERSON_ANITA_DEVI",
                    "Anita Devi",
                    json.dumps(["Didiji", "Madam"]),
                    3,
                    0,
                    2,
                    0,
                    "ON_BAIL",
                    "Patna Syndicate",
                    json.dumps([
                        {"fir_no": "FIR/2021/045", "year": 2021, "sections": ["364A", "376 IPC"], "court": "Patna Fast Track Court", "status": "UNDER_TRIAL", "description": "Facilitating inter-state human trafficking safehouses"}
                    ])
                ),
                (
                    "PERSON_RAMESH_YADAV",
                    "Ramesh Yadav",
                    json.dumps(["Pahalwan"]),
                    5,
                    1,
                    4,
                    1,
                    "FUGITIVE",
                    "Mining Cartel",
                    json.dumps([
                        {"fir_no": "FIR/2018/112", "year": 2018, "sections": ["307", "353 IPC"], "court": "Dhanbad Court", "status": "CONVICTED", "description": "Armed firing on district police inspection convoy"}
                    ])
                )
            ]

            cur.executemany("""
                INSERT INTO criminal_history 
                (suspect_id, name, aliases, prior_firs_count, past_convictions, chargesheets_filed, active_warrants, bail_status, gang_affiliation, history_cases)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()

    def get_record(self, suspect_id: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Try by suspect_id
            cur.execute("SELECT * FROM criminal_history WHERE suspect_id = ?", (suspect_id,))
            row = cur.fetchone()
            
            # Fallback by name
            if not row and name:
                cur.execute("SELECT * FROM criminal_history WHERE LOWER(name) = LOWER(?)", (name.strip(),))
                row = cur.fetchone()

            if not row and suspect_id:
                # Try partial match (e.g. PERSON_VIKRAM_SINHA -> Vikram Sinha)
                cleaned = suspect_id.replace("PERSON_", "").replace("_", " ")
                cur.execute("SELECT * FROM criminal_history WHERE LOWER(name) = LOWER(?)", (cleaned,))
                row = cur.fetchone()

            if row:
                d = dict(row)
                d['aliases'] = json.loads(d['aliases']) if d['aliases'] else []
                d['history_cases'] = json.loads(d['history_cases']) if d['history_cases'] else []
                return d

        # Default clean / first-time offender record
        return {
            "suspect_id": suspect_id,
            "name": name or suspect_id,
            "aliases": [],
            "prior_firs_count": 0,
            "past_convictions": 0,
            "chargesheets_filed": 0,
            "active_warrants": 0,
            "bail_status": "NO_PRIOR_RECORD",
            "gang_affiliation": "None",
            "history_cases": []
        }

    def compute_risk_modifier(self, suspect_id: str, name: Optional[str] = None) -> float:
        """
        Calculates score modifier (+0 to +40 points) based on verified prior criminal record:
        - Active NBW warrant: +20 points
        - Jumped Bail / Fugitive: +15 points
        - Each past conviction: +10 points (max 20)
        - Each chargesheet: +4 points (max 12)
        - Each prior FIR: +2 points (max 10)
        """
        rec = self.get_record(suspect_id, name)
        if not rec:
            return 0.0

        modifier = 0.0
        if rec.get('active_warrants', 0) > 0:
            modifier += 20.0
        if rec.get('bail_status') in ('JUMPED_BAIL', 'FUGITIVE'):
            modifier += 15.0
        
        modifier += min(20.0, rec.get('past_convictions', 0) * 10.0)
        modifier += min(12.0, rec.get('chargesheets_filed', 0) * 4.0)
        modifier += min(10.0, rec.get('prior_firs_count', 0) * 2.0)

        return min(40.0, modifier)

# Global singleton
criminal_history_db = CriminalHistoryManager()
