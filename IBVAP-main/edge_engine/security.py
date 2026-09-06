import sqlite3
import threading
import time
import hashlib
import cv2
import requests
import logging
import base64
import json
from typing import Optional
import numpy as np

from edge_engine.config import get_config

logger = logging.getLogger(__name__)

class ChainOfCustody:
    def __init__(self):
        self.config = get_config()
        self.db_path = self.config.sqlite_db_path
        self.lock = threading.Lock()
        self._init_db()
        self._stop_event = threading.Event()
        self.sync_thread: Optional[threading.Thread] = None

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS offline_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bop_id TEXT,
                    camera_id TEXT,
                    timestamp TEXT,
                    alert_type TEXT,
                    sha256_hash TEXT,
                    synced_status INTEGER DEFAULT 0,
                    keyframe_blob BLOB
                )
            ''')
            conn.commit()
            conn.close()

    def hash_evidence(self, keyframe: np.ndarray, camera_id: str, timestamp: str, bop_id: str, alert_type: str) -> str:
        _, buffer = cv2.imencode('.jpg', keyframe)
        img_bytes = buffer.tobytes()
        metadata = f"{camera_id}_{timestamp}_{bop_id}_{alert_type}".encode('utf-8')
        payload = img_bytes + metadata
        return hashlib.sha256(payload).hexdigest()

    def store_event(self, bop_id: str, camera_id: str, timestamp: str, alert_type: str, hash_val: str, keyframe: np.ndarray):
        _, buffer = cv2.imencode('.jpg', keyframe)
        img_bytes = buffer.tobytes()
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO offline_audit (bop_id, camera_id, timestamp, alert_type, sha256_hash, synced_status, keyframe_blob)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            ''', (bop_id, camera_id, timestamp, alert_type, hash_val, img_bytes))
            conn.commit()
            conn.close()

    def start_sync_worker(self):
        if self.sync_thread is not None and self.sync_thread.is_alive():
            return
        self._stop_event.clear()
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()

    def stop_sync_worker(self):
        self._stop_event.set()
        if self.sync_thread is not None:
            self.sync_thread.join(timeout=2.0)

    def get_unsynced_count(self) -> int:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM offline_audit WHERE synced_status = 0')
            count = c.fetchone()[0]
            conn.close()
            return count

    def _sync_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.config.sync_interval_sec)
            try:
                with self.lock:
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    c.execute('SELECT id, bop_id, camera_id, timestamp, alert_type, sha256_hash, keyframe_blob FROM offline_audit WHERE synced_status = 0 LIMIT 10')
                    rows = c.fetchall()
                    conn.close()
                    
                if not rows:
                    continue
                    
                for row in rows:
                    row_id, bop_id, cam_id, ts, alert, hsh, blob = row
                    
                    thumbnail_b64 = base64.b64encode(blob).decode('utf-8')
                    payload = {
                        'bop_id': bop_id,
                        'camera_id': cam_id,
                        'timestamp': ts,
                        'alert_type': alert,
                        'sha256_hash': hsh,
                        'severity': 'HIGH',
                        'description': f"{alert} alert detected",
                        'thumbnail_b64': thumbnail_b64
                    }
                    
                    try:
                        response = requests.post(self.config.backend_api_url, json=payload, timeout=5)
                        if response.status_code == 200:
                            with self.lock:
                                conn = sqlite3.connect(self.db_path)
                                c = conn.cursor()
                                c.execute('UPDATE offline_audit SET synced_status = 1 WHERE id = ?', (row_id,))
                                conn.commit()
                                conn.close()
                    except requests.exceptions.RequestException as e:
                        logger.error(f"HTTP request error during sync: {e}")
                        
            except Exception as e:
                logger.error(f"Sync error: {e}")
