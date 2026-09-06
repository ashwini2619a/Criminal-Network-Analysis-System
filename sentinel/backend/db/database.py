"""
SENTINEL v2.0 — SQLite Persistent Database
Thread-safe persistence layer for cases, collaborative case board, alerts,
RBAC users, immutable audit logging, and evidence chain of custody.
"""

import sqlite3
import os
import json
import uuid
import threading
from datetime import datetime
from typing import List, Dict, Optional, Any

from backend.config import DB_PATH

_lock = threading.RLock()

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with _lock:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)
        
        # 2. Audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                username TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # 3. Evidence Blockchain log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_chain (
                id TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT,
                previous_hash TEXT,
                timestamp TEXT NOT NULL,
                uploaded_by TEXT,
                chain_index INTEGER,
                block_hash TEXT NOT NULL
            )
        """)
        
        # 4. Uploads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                sha256_hash TEXT NOT NULL,
                upload_timestamp TEXT NOT NULL,
                status TEXT,
                extracted_entities_count INTEGER DEFAULT 0
            )
        """)
        
        # 5. Case Board (Collaborative Kanban)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caseboard (
                id TEXT PRIMARY KEY,
                case_no TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                crime_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_officer TEXT NOT NULL,
                lead_suspect TEXT,
                suspect_count INTEGER DEFAULT 1,
                evidence_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                notes_json TEXT DEFAULT '[]'
            )
        """)
        
        # 6. Automated Pattern Detection Alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                alert_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                entity_id TEXT,
                entity_name TEXT,
                entity_type TEXT,
                timestamp TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}',
                acknowledged INTEGER DEFAULT 0,
                action_url TEXT
            )
        """)
        
        # 7. Shared Graph Annotations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                author TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # 8. Face Profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_profiles (
                id TEXT PRIMARY KEY,
                suspect_name TEXT NOT NULL,
                embedding_json TEXT NOT NULL,
                registered_by TEXT,
                timestamp TEXT NOT NULL,
                thumbnail_path TEXT
            )
        """)

        # 9. Face Match Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_match_log (
                id TEXT PRIMARY KEY,
                face_id TEXT NOT NULL,
                source_image TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                match_timestamp TEXT NOT NULL,
                bbox_json TEXT
            )
        """)

        # 10. Person Detections (Evidence)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS person_detections (
                id TEXT PRIMARY KEY,
                source_image TEXT NOT NULL,
                detection_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                bboxes_json TEXT,
                confidence_scores_json TEXT
            )
        """)

        # 11. Person Captures (Live)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS person_captures (
                id TEXT PRIMARY KEY,
                capture_path TEXT NOT NULL,
                detection_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                blockchain_hash TEXT
            )
        """)
        
        # High-Selectivity Query Performance Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_hash ON evidence_chain(file_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_timestamp ON evidence_chain(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uploads_hash ON uploads(sha256_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_caseboard_status ON caseboard(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_caseboard_case_no ON caseboard(case_no)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_type_priority ON alerts(alert_type, priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_annotations_node_id ON annotations(node_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_face_match_face_id ON face_match_log(face_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person_detections_ts ON person_detections(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_person_captures_ts ON person_captures(timestamp)")
        
        conn.commit()
        
        # Pre-seed default test users if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            import hashlib
            def h(p):
                return hashlib.sha256(f"SENTINEL_SALT_{p}".encode()).hexdigest()
                
            now = datetime.now().isoformat()
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                           ("U-ADMIN", "admin", h("sentinel2024"), "ADMIN", now, now))
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                           ("U-INV", "investigator", h("investigator2026"), "INVESTIGATOR", now, None))
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                           ("U-ANL", "analyst", h("analyst2026"), "ANALYST", now, None))
            conn.commit()
            
        conn.close()

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def log_audit(self, user_id: str, username: str, action: str, resource: str = "", details: str = "", ip_address: str = "127.0.0.1") -> str:
        import uuid
        entry_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().isoformat()
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute(
                "INSERT INTO audit_log (id, user_id, username, action, resource, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (entry_id, user_id, username, action, resource, details, ip_address, now)
            )
            conn.commit()
            conn.close()
        return entry_id

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return rows

    # --- Caseboard Operations ---
    def get_caseboard_cards(self) -> List[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT * FROM caseboard ORDER BY updated_at DESC")
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["notes"] = json.loads(d.get("notes_json") or "[]")
                rows.append(d)
            conn.close()
            return rows

    def add_case_card(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        with _lock:
            conn = get_connection(self.db_path)
            notes_json = json.dumps(card_data.get("notes", []))
            conn.execute(
                """INSERT OR REPLACE INTO caseboard 
                   (id, case_no, title, crime_type, severity, status, assigned_officer, lead_suspect, suspect_count, evidence_count, created_at, updated_at, notes_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    card_data["id"], card_data["case_no"], card_data["title"], card_data["crime_type"],
                    card_data["severity"], card_data["status"], card_data["assigned_officer"],
                    card_data.get("lead_suspect"), card_data.get("suspect_count", 1),
                    card_data.get("evidence_count", 0), card_data["created_at"], card_data["updated_at"],
                    notes_json
                )
            )
            conn.commit()
            conn.close()
            return card_data

    def update_case_status(self, case_id: str, new_status: str) -> bool:
        now = datetime.now().isoformat()
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("UPDATE caseboard SET status = ?, updated_at = ? WHERE id = ?", (new_status, now, case_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    # --- Alerts Operations ---
    def add_alert(self, alert_data: Dict[str, Any]) -> str:
        with _lock:
            conn = get_connection(self.db_path)
            meta_json = json.dumps(alert_data.get("metadata", {}))
            conn.execute(
                """INSERT OR REPLACE INTO alerts 
                   (id, alert_type, priority, title, description, entity_id, entity_name, entity_type, timestamp, metadata_json, acknowledged, action_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert_data["id"], alert_data["alert_type"], alert_data["priority"], alert_data["title"],
                    alert_data["description"], alert_data.get("entity_id"), alert_data.get("entity_name"),
                    alert_data.get("entity_type"), alert_data["timestamp"], meta_json,
                    1 if alert_data.get("acknowledged") else 0, alert_data.get("action_url")
                )
            )
            conn.commit()
            conn.close()
            return alert_data["id"]

    def get_alerts(self, limit: int = 100, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            query = "SELECT * FROM alerts"
            if unacknowledged_only:
                query += " WHERE acknowledged = 0"
            query += " ORDER BY timestamp DESC LIMIT ?"
            cursor = conn.execute(query, (limit,))
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["metadata"] = json.loads(d.get("metadata_json") or "{}")
                d["acknowledged"] = bool(d.get("acknowledged"))
                rows.append(d)
            conn.close()
            return rows

    def acknowledge_alert(self, alert_id: str) -> bool:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    def dismiss_alert(self, alert_id: str) -> bool:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    def escalate_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            alert = dict(row)
            now = datetime.now().isoformat()
            case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"
            case_no = f"FIR-{datetime.now().year}/{uuid.uuid4().hex[:4].upper()}"
            case_card = {
                "id": case_id,
                "case_no": case_no,
                "title": f"ESCALATED: {alert.get('title', 'Pattern Alert')}",
                "crime_type": alert.get("alert_type", "SECURITY_ALERT"),
                "severity": alert.get("priority", "HIGH"),
                "status": "ACTIVE_INVESTIGATION",
                "assigned_officer": "Insp. R. K. Sharma (CID)",
                "lead_suspect": alert.get("entity_name") or "Under Investigation",
                "suspect_count": 1,
                "evidence_count": 1,
                "created_at": now,
                "updated_at": now,
                "notes": [f"Escalated from automated alert {alert_id} ({alert.get('alert_type')}) on {now}."]
            }
            conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
            conn.commit()
            conn.close()
            self.add_case_card(case_card)
            return case_card

    # --- Uploads & Evidence Chain ---
    def add_upload(self, upload_data: Dict[str, Any]):
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO uploads (id, file_name, file_type, file_size, sha256_hash, upload_timestamp, status, extracted_entities_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    upload_data["id"], upload_data["file_name"], upload_data.get("file_type"),
                    upload_data.get("file_size"), upload_data["sha256_hash"], upload_data["upload_timestamp"],
                    upload_data.get("status", "SEALED"), upload_data.get("extracted_entities_count", 0)
                )
            )
            conn.commit()
            conn.close()

    def get_uploads(self) -> List[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT * FROM uploads ORDER BY upload_timestamp DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return rows

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None

    def get_users(self) -> List[Dict[str, Any]]:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("SELECT id, username, role, created_at, last_login FROM users ORDER BY created_at ASC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return rows

    def delete_case_card(self, case_id: str) -> bool:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("DELETE FROM caseboard WHERE id = ?", (case_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    def clear_case_cards(self):
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute("DELETE FROM caseboard")
            conn.commit()
            conn.close()

    def delete_alert(self, alert_id: str) -> bool:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    def clear_alerts(self):
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute("DELETE FROM alerts")
            conn.commit()
            conn.close()

    def delete_upload(self, upload_id: str) -> bool:
        with _lock:
            conn = get_connection(self.db_path)
            cursor = conn.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success

    def clear_uploads(self):
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute("DELETE FROM uploads")
            conn.commit()
            conn.close()

    def clear_all_data(self):
        """Purges alerts, uploads, caseboard cards, and non-genesis evidence to return database to clean slate."""
        with _lock:
            conn = get_connection(self.db_path)
            conn.execute("DELETE FROM alerts")
            conn.execute("DELETE FROM uploads")
            conn.execute("DELETE FROM caseboard")
            conn.execute("DELETE FROM evidence_chain WHERE chain_index > 0")
            conn.commit()
            conn.close()
