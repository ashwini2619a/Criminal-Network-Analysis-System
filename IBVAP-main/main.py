"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  IBVAP — Intelligent Border Video Analytics Platform                       ║
║  All-in-One Edge Surveillance Engine & Real-Time Alert Server              ║
║                                                                            ║
║  Problem Statement 26187 · SSB, Ministry of Home Affairs                   ║
║  Single-file production build with:                                        ║
║    1. RTSP/Webcam ingestion with auto-reconnect & adaptive FPS             ║
║    2. Adaptive CLAHE night-vision (LAB color space)                        ║
║    3. YOLOv8 + ByteTrack multi-object tracking                            ║
║    4. Directional virtual tripwire (vector cross product)                  ║
║    5. Inclusion/Exclusion polygon geofencing                               ║
║    6. Crawling heuristic (aspect ratio over consecutive frames)            ║
║    7. Loitering detection (stationary radius timeout)                      ║
║    8. Facial Recognition System (SCRFD + ArcFace 512-D + FAISS)           ║
║    9. ANPR — PaddleOCR + Indian RTO regex validation                      ║
║   10. SHA-256 chain-of-custody + SQLite store-and-forward audit            ║
║   11. FastAPI REST + WebSocket C2 backend                                  ║
║   12. Embedded tactical HTML dashboard                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import base64
import cv2
import hashlib
import json
import logging
import math
import numpy as np
import os
import pickle
import queue
import re
import sqlite3
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from shapely.geometry import LineString, Point, Polygon

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & LOGGING
# ═══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("IBVAP")

CONFIG = {
    # ── Identity ────────────────────────────────────────────────────────────
    "BOP_ID":       os.getenv("IBVAP_BOP_ID",    "BOP_SECTOR_07_JAMSHEDPUR"),
    "CAMERA_ID":    os.getenv("IBVAP_CAMERA_ID",  "CAM_PERIMETER_NORTH_01"),

    # ── Video ───────────────────────────────────────────────────────────────
    "VIDEO_SOURCE":       os.getenv("IBVAP_RTSP_URL", "0"),   # RTSP URL, file, or "0" for webcam
    "INFERENCE_WIDTH":    640,
    "INFERENCE_HEIGHT":   480,
    "FPS_STATIC":         8,
    "FPS_ACTIVE":         25,

    # ── Enhancement ─────────────────────────────────────────────────────────
    "LOW_LIGHT_THRESHOLD":  60,
    "CLAHE_CLIP_LIMIT":     3.0,
    "CLAHE_TILE_SIZE":      (8, 8),

    # ── Behavior Thresholds ─────────────────────────────────────────────────
    "CRAWL_AR_THRESH":          1.35,
    "CRAWL_CONSECUTIVE_FRAMES": 6,
    "LOITER_RADIUS_PX":         100,
    "LOITER_TIMEOUT_SEC":       45,
    "ALERT_COOLDOWN_SEC":       30,

    # ── FRS (Facial Recognition System) ─────────────────────────────────────
    "FACE_SIMILARITY_THRESHOLD": 0.68,
    "FAISS_INDEX_PATH":          "ibvap_faces.index",

    # ── ANPR ────────────────────────────────────────────────────────────────
    "ANPR_REGEX": r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$",

    # ── Security & Networking ───────────────────────────────────────────────
    "DB_PATH":   "ibvap_edge_audit.db",
    "API_PORT":  int(os.getenv("IBVAP_PORT", "8000")),
}

# Coerce webcam index if numeric
if CONFIG["VIDEO_SOURCE"].isdigit():
    CONFIG["VIDEO_SOURCE"] = int(CONFIG["VIDEO_SOURCE"])


# ═══════════════════════════════════════════════════════════════════════════════
# §1  CYBERSECURITY: SHA-256 EVIDENCE HASHING & SQLITE AUDIT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class SecurityAuditEngine:
    """Zero-trust chain-of-custody: every alert is SHA-256-anchored and
    persisted in an offline-capable SQLite store-and-forward queue."""

    def __init__(self, db_path: str = CONFIG["DB_PATH"]):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id    TEXT UNIQUE NOT NULL,
                    bop_id      TEXT,
                    camera_id   TEXT,
                    timestamp   TEXT,
                    alert_type  TEXT,
                    sha256_hash TEXT,
                    synced      INTEGER DEFAULT 0,
                    metadata    TEXT,
                    keyframe    BLOB
                )
            """)
            conn.commit()

    @staticmethod
    def compute_evidence_hash(frame_bytes: bytes, camera_id: str,
                              timestamp: str, bop_id: str,
                              alert_type: str) -> str:
        """SHA-256( JPEG ‖ camera_id ‖ timestamp ‖ bop_id ‖ alert_type )"""
        payload = (frame_bytes
                   + camera_id.encode()
                   + timestamp.encode()
                   + bop_id.encode()
                   + alert_type.encode())
        return hashlib.sha256(payload).hexdigest()

    def record_event(self, event_id: str, alert_type: str,
                     metadata: dict, frame: np.ndarray) -> str:
        _, buf = cv2.imencode(".jpg", frame)
        frame_bytes = buf.tobytes()
        ts = datetime.now(timezone.utc).isoformat()

        evidence_hash = self.compute_evidence_hash(
            frame_bytes, CONFIG["CAMERA_ID"], ts,
            CONFIG["BOP_ID"], alert_type
        )

        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO audit_trail
                        (event_id, bop_id, camera_id, timestamp,
                         alert_type, sha256_hash, synced, metadata, keyframe)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """, (
                    event_id, CONFIG["BOP_ID"], CONFIG["CAMERA_ID"],
                    ts, alert_type, evidence_hash,
                    json.dumps(metadata, default=str),
                    frame_bytes,
                ))
                conn.commit()

        logger.info(f"🔒 Evidence anchored: {alert_type} | SHA-256: {evidence_hash[:24]}…")
        return evidence_hash

    def get_unsynced(self, limit: int = 10) -> list:
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute(
                    "SELECT id, event_id, bop_id, camera_id, timestamp, "
                    "alert_type, sha256_hash, metadata, keyframe "
                    "FROM audit_trail WHERE synced = 0 LIMIT ?", (limit,)
                ).fetchall()
        return rows

    def mark_synced(self, row_id: int):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE audit_trail SET synced = 1 WHERE id = ?", (row_id,))
                conn.commit()

    def verify(self, event_id: str, test_hash: str) -> Optional[bool]:
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT sha256_hash FROM audit_trail WHERE event_id = ?",
                    (event_id,)
                ).fetchone()
        if row is None:
            return None
        return row[0] == test_hash


# ═══════════════════════════════════════════════════════════════════════════════
# §2  IMAGE PREPROCESSING: ADAPTIVE NIGHT / FOG ENHANCER
# ═══════════════════════════════════════════════════════════════════════════════
class NightVisionEnhancer:
    """Applies CLAHE in LAB color space when average luminance drops below
    the configured threshold.  CLAHE object is cached for zero-alloc reuse."""

    def __init__(self):
        self.clahe = cv2.createCLAHE(
            clipLimit=CONFIG["CLAHE_CLIP_LIMIT"],
            tileGridSize=CONFIG["CLAHE_TILE_SIZE"],
        )

    def enhance(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        avg_lum = np.mean(l_ch)

        if avg_lum < CONFIG["LOW_LIGHT_THRESHOLD"]:
            l_enhanced = self.clahe.apply(l_ch)
            enhanced = cv2.merge((l_enhanced, a_ch, b_ch))
            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR), True
        return frame, False


# ═══════════════════════════════════════════════════════════════════════════════
# §3  GEOMETRIC BOUNDARY & VIRTUAL TRIPWIRE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class BoundaryEngine:
    """Directional tripwires (vector cross-product sign change) and
    inclusion/exclusion polygon zones using Shapely geometry."""

    def __init__(self, w: int, h: int):
        # Tripwire across 60% height of frame
        self.tripwire_p1 = (int(w * 0.1), int(h * 0.6))
        self.tripwire_p2 = (int(w * 0.9), int(h * 0.6))
        self.tripwire_line = LineString([self.tripwire_p1, self.tripwire_p2])

        # Exclusion zone (lower region)
        self.restricted_poly = Polygon([
            (int(w * 0.3), int(h * 0.65)),
            (int(w * 0.7), int(h * 0.65)),
            (int(w * 0.8), int(h * 0.95)),
            (int(w * 0.2), int(h * 0.95)),
        ])

        # Store raw coords for drawing
        self.restricted_coords = list(self.restricted_poly.exterior.coords)

    def check_tripwire_crossing(self, prev: Tuple, curr: Tuple) -> bool:
        """Return True when entity traverses the tripwire in the
        unauthorized direction (top → bottom, i.e. cross product > 0)."""
        if not prev or not curr or prev == curr:
            return False

        movement = LineString([prev, curr])
        if not movement.intersects(self.tripwire_line):
            return False

        x1, y1 = self.tripwire_p1
        x2, y2 = self.tripwire_p2
        xt, yt = curr
        cross = (x2 - x1) * (yt - y1) - (y2 - y1) * (xt - x1)
        return cross > 0

    def is_in_restricted_zone(self, point: Tuple) -> bool:
        return self.restricted_poly.contains(Point(point))


# ═══════════════════════════════════════════════════════════════════════════════
# §4  BEHAVIOR ANALYTICS: CRAWLING & LOITERING HEURISTICS
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class TrackState:
    positions: deque = field(default_factory=lambda: deque(maxlen=300))
    timestamps: deque = field(default_factory=lambda: deque(maxlen=300))
    aspect_ratios: deque = field(default_factory=lambda: deque(maxlen=60))
    last_seen: float = 0.0

class BehaviorAnalyzer:
    """Detects suspicious crawling (AR > 1.35 for ≥ 6 consecutive frames)
    and loitering (stationary within 100 px radius for > 45 seconds).
    Includes a 30-second cooldown to suppress alert flooding."""

    def __init__(self):
        self.states: Dict[int, TrackState] = {}
        self._cooldowns: Dict[Tuple, float] = {}

    def analyze(self, tracks: List[dict], ts: float) -> List[dict]:
        alerts: List[dict] = []

        # Prune stale tracks
        stale = [k for k, v in self.states.items() if ts - v.last_seen > 10.0]
        for k in stale:
            del self.states[k]

        for t in tracks:
            tid = t["track_id"]
            label = t["label"]
            x1, y1, x2, y2 = t["box"]
            w, h = x2 - x1, y2 - y1
            if h <= 0:
                continue

            cx, cy = x1 + w // 2, y2  # bottom-center

            if tid not in self.states:
                self.states[tid] = TrackState()
            st = self.states[tid]
            st.last_seen = ts
            st.positions.append((cx, cy))
            st.timestamps.append(ts)

            # ── Crawling ────────────────────────────────────────────────
            if label == "person":
                ar = w / float(h)
                st.aspect_ratios.append(ar)
                n = CONFIG["CRAWL_CONSECUTIVE_FRAMES"]
                if len(st.aspect_ratios) >= n:
                    recent = list(st.aspect_ratios)[-n:]
                    if all(a > CONFIG["CRAWL_AR_THRESH"] for a in recent):
                        if ts - self._cooldowns.get((tid, "CRAWLING"), 0) > CONFIG["ALERT_COOLDOWN_SEC"]:
                            self._cooldowns[(tid, "CRAWLING")] = ts
                            alerts.append({
                                "type": "SUSPICIOUS_CRAWLING",
                                "track_id": tid,
                                "aspect_ratio": round(ar, 2),
                            })

            # ── Loitering ───────────────────────────────────────────────
            if len(st.positions) > 1:
                duration = ts - st.timestamps[0]
                if duration > CONFIG["LOITER_TIMEOUT_SEC"]:
                    pts = np.array(list(st.positions))
                    center = np.mean(pts, axis=0)
                    dists = np.linalg.norm(pts - center, axis=1)
                    if np.all(dists < CONFIG["LOITER_RADIUS_PX"]):
                        if ts - self._cooldowns.get((tid, "LOITERING"), 0) > CONFIG["ALERT_COOLDOWN_SEC"]:
                            self._cooldowns[(tid, "LOITERING")] = ts
                            alerts.append({
                                "type": "LOITERING",
                                "track_id": tid,
                                "duration_sec": round(duration, 1),
                            })

        return alerts


# ═══════════════════════════════════════════════════════════════════════════════
# §5  FACIAL RECOGNITION SYSTEM (SCRFD + ArcFace 512-D + FAISS)
# ═══════════════════════════════════════════════════════════════════════════════
class FaceRecognitionSystem:
    """Unconstrained face detection via SCRFD, recognition via ArcFace
    (512-D embedding), with local FAISS IndexFlatIP cosine search.
    Gracefully degrades if insightface/faiss are not installed."""

    def __init__(self):
        self.available = False
        self.lock = threading.Lock()
        self.id_map: Dict[int, str] = {}

        try:
            import faiss
            from insightface.app import FaceAnalysis
            self.faiss = faiss
            self.app = FaceAnalysis(
                name="buffalo_l", root="~/.insightface",
                providers=["CPUExecutionProvider"],
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self.index = faiss.IndexFlatIP(512)
            self._load_index()
            self.available = True
            logger.info("👤 FRS: InsightFace + FAISS loaded successfully.")
        except Exception as e:
            logger.warning(f"👤 FRS: Unavailable ({e}). Face analytics disabled.")

    def _load_index(self):
        idx_path = CONFIG["FAISS_INDEX_PATH"]
        map_path = idx_path + ".map"
        if os.path.exists(idx_path):
            self.index = self.faiss.read_index(idx_path)
            if os.path.exists(map_path):
                with open(map_path, "rb") as f:
                    self.id_map = pickle.load(f)

    def _save_index(self):
        self.faiss.write_index(self.index, CONFIG["FAISS_INDEX_PATH"])
        with open(CONFIG["FAISS_INDEX_PATH"] + ".map", "wb") as f:
            pickle.dump(self.id_map, f)

    def enroll(self, image: np.ndarray, person_id: str) -> bool:
        if not self.available:
            return False
        with self.lock:
            faces = self.app.get(image)
            if not faces or len(faces) != 1:
                return False
            emb = faces[0].normed_embedding.reshape(1, -1).astype(np.float32)
            self.faiss.normalize_L2(emb)
            idx = self.index.ntotal
            self.index.add(emb)
            self.id_map[idx] = person_id
            self._save_index()
            return True

    def identify(self, frame: np.ndarray) -> List[dict]:
        if not self.available or self.index.ntotal == 0:
            return []
        matches = []
        faces = self.app.get(frame)
        if not faces:
            return []
        with self.lock:
            for face in faces:
                emb = face.normed_embedding.reshape(1, -1).astype(np.float32)
                self.faiss.normalize_L2(emb)
                dists, idxs = self.index.search(emb, 1)
                sim = float(dists[0][0])
                best_idx = int(idxs[0][0])
                bbox = tuple(map(int, face.bbox))
                pid = self.id_map.get(best_idx, "UNKNOWN")
                if sim >= CONFIG["FACE_SIMILARITY_THRESHOLD"]:
                    matches.append({"bbox": bbox, "person_id": pid, "similarity": round(sim, 3)})
        return matches


# ═══════════════════════════════════════════════════════════════════════════════
# §6  AUTOMATIC NUMBER PLATE RECOGNITION (ANPR)
# ═══════════════════════════════════════════════════════════════════════════════
class ANPREngine:
    """Crops vehicle bounding boxes, runs PaddleOCR, validates against the
    Indian RTO format: XX 00 XXX 0000.  Gracefully degrades if PaddleOCR
    is not installed."""

    def __init__(self):
        self.available = False
        self.regex = re.compile(CONFIG["ANPR_REGEX"])
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            self.available = True
            logger.info("🚗 ANPR: PaddleOCR loaded successfully.")
        except Exception as e:
            logger.warning(f"🚗 ANPR: Unavailable ({e}). Plate recognition disabled.")

    def process(self, frame: np.ndarray, vehicle_boxes: List[dict]) -> List[dict]:
        if not self.available:
            return []
        results = []
        h_frame, w_frame = frame.shape[:2]

        for vb in vehicle_boxes:
            x1, y1, x2, y2 = map(int, vb["box"])
            # Clamp to frame bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_frame, x2), min(h_frame, y2)
            if x2 <= x1 or y2 <= y1:
                continue

            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            try:
                ocr_out = self.ocr.ocr(crop, cls=True)
            except Exception:
                continue

            if not ocr_out or not ocr_out[0]:
                continue

            for line in ocr_out[0]:
                box_pts, (text, conf) = line
                clean = re.sub(r"[^A-Z0-9]", "", text.upper())
                if not clean or conf < 0.5:
                    continue
                is_valid = bool(self.regex.match(clean))
                results.append({
                    "plate": clean,
                    "confidence": round(conf, 3),
                    "is_valid": is_valid,
                    "vehicle_box": (x1, y1, x2, y2),
                })
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# §7  UNIFIED COMPUTER VISION & INFERENCE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
class EdgeVisionPipeline:
    """Orchestrates all subsystems: enhancement → detection → tracking →
    geometry → behavior → FRS → ANPR → chain-of-custody."""

    def __init__(self):
        self.enhancer = NightVisionEnhancer()
        self.geometry = BoundaryEngine(CONFIG["INFERENCE_WIDTH"], CONFIG["INFERENCE_HEIGHT"])
        self.security = SecurityAuditEngine()
        self.behavior = BehaviorAnalyzer()
        self.frs = FaceRecognitionSystem()
        self.anpr = ANPREngine()

        self.tracked_positions: Dict[int, List[Tuple[int, int]]] = {}

        # YOLO with graceful fallback
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.use_yolo = True
            logger.info("🎯 YOLO model loaded.")
        except Exception as e:
            logger.warning(f"🎯 YOLO unavailable ({e}). Using synthetic detector.")
            self.use_yolo = False

    # ── Detection ───────────────────────────────────────────────────────────
    def _detect(self, frame: np.ndarray) -> List[dict]:
        detections = []
        if self.use_yolo:
            try:
                results = self.model.track(frame, persist=True, verbose=False)[0]
                if results.boxes is not None:
                    boxes = results.boxes.xyxy.cpu().numpy()
                    track_ids = (
                        results.boxes.id.int().cpu().numpy()
                        if results.boxes.id is not None
                        else np.arange(1, len(boxes) + 1)
                    )
                    classes = results.boxes.cls.int().cpu().numpy()
                    confs = results.boxes.conf.cpu().numpy()
                    CLASS_MAP = {0: "person", 1: "bicycle", 2: "car",
                                 3: "motorcycle", 5: "bus", 7: "truck"}
                    for box, tid, cls_id, conf in zip(boxes, track_ids, classes, confs):
                        label = CLASS_MAP.get(int(cls_id))
                        if label and conf > 0.4:
                            detections.append({
                                "box": list(map(int, box)),
                                "track_id": int(tid),
                                "label": label,
                                "confidence": float(conf),
                            })
            except Exception as e:
                logger.warning(f"Tracking error ({e}). Trying fallback detection...")
                try:
                    results = self.model.predict(frame, verbose=False)[0]
                    if results.boxes is not None:
                        boxes = results.boxes.xyxy.cpu().numpy()
                        classes = results.boxes.cls.int().cpu().numpy()
                        confs = results.boxes.conf.cpu().numpy()
                        CLASS_MAP = {0: "person", 1: "bicycle", 2: "car",
                                     3: "motorcycle", 5: "bus", 7: "truck"}
                        for idx, (box, cls_id, conf) in enumerate(zip(boxes, classes, confs), 1):
                            label = CLASS_MAP.get(int(cls_id))
                            if label and conf > 0.4:
                                detections.append({
                                    "box": list(map(int, box)),
                                    "track_id": idx,
                                    "label": label,
                                    "confidence": float(conf),
                                })
                except Exception as e2:
                    logger.error(f"Detection fallback error: {e2}")
        else:
            # Synthetic moving target for UI testing
            h, w = frame.shape[:2]
            t = time.time()
            my = int((t * 40) % (h - 100)) + 50
            mx = int(w * 0.5 + math.sin(t) * 80)
            detections.append({
                "box": [mx - 25, my, mx + 25, my + 80],
                "track_id": 101,
                "label": "person",
                "confidence": 0.92,
            })
            # Synthetic vehicle
            vy = int((t * 25) % (h - 60)) + 30
            detections.append({
                "box": [int(w * 0.7), vy, int(w * 0.7) + 80, vy + 50],
                "track_id": 202,
                "label": "car",
                "confidence": 0.87,
            })
        return detections

    # ── Full Pipeline ───────────────────────────────────────────────────────
    def process_frame(self, raw_frame: np.ndarray) -> Tuple[np.ndarray, List[dict]]:
        frame = cv2.resize(raw_frame, (CONFIG["INFERENCE_WIDTH"], CONFIG["INFERENCE_HEIGHT"]))
        frame, was_enhanced = self.enhancer.enhance(frame)
        ts = time.time()
        iso_ts = datetime.now(timezone.utc).isoformat()
        all_alerts: List[dict] = []

        # ── Object Detection & Tracking ─────────────────────────────────
        detections = self._detect(frame)

        # ── Geometry: Tripwire & Zone ───────────────────────────────────
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            tid = det["track_id"]
            cx, cy = (x1 + x2) // 2, y2  # bottom-center

            # Track history
            if tid not in self.tracked_positions:
                self.tracked_positions[tid] = []
            self.tracked_positions[tid].append((cx, cy))
            if len(self.tracked_positions[tid]) > 30:
                self.tracked_positions[tid].pop(0)

            prev = self.tracked_positions[tid][-2] if len(self.tracked_positions[tid]) >= 2 else None

            # Tripwire
            if prev and self.geometry.check_tripwire_crossing(prev, (cx, cy)):
                eid = f"EV_{int(ts * 1000)}_{tid}_TW"
                meta = {"track_id": tid, "class": det["label"],
                        "confidence": det["confidence"]}
                h = self.security.record_event(eid, "TRIPWIRE_BREACH", meta, frame)
                all_alerts.append({"event_id": eid, "type": "TRIPWIRE_BREACH",
                                   "hash": h, "metadata": meta})

            # Restricted zone
            if self.geometry.is_in_restricted_zone((cx, cy)):
                eid = f"EV_{int(ts * 1000)}_{tid}_RZ"
                meta = {"track_id": tid, "class": det["label"]}
                h = self.security.record_event(eid, "ZONE_INTRUSION", meta, frame)
                all_alerts.append({"event_id": eid, "type": "ZONE_INTRUSION",
                                   "hash": h, "metadata": meta})

        # ── Behavior Analytics ──────────────────────────────────────────
        behavior_alerts = self.behavior.analyze(detections, ts)
        for ba in behavior_alerts:
            eid = f"EV_{int(ts * 1000)}_{ba['track_id']}_{ba['type'][:4]}"
            h = self.security.record_event(eid, ba["type"], ba, frame)
            all_alerts.append({"event_id": eid, "type": ba["type"],
                               "hash": h, "metadata": ba})

        # ── Facial Recognition ──────────────────────────────────────────
        person_dets = [d for d in detections if d["label"] == "person"]
        if person_dets and self.frs.available:
            face_matches = self.frs.identify(frame)
            for fm in face_matches:
                bx1, by1, bx2, by2 = fm["bbox"]
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 200, 0), 2)
                lbl = f'{fm["person_id"]} ({fm["similarity"]:.0%})'
                cv2.putText(frame, lbl, (bx1, by1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)
                if fm["person_id"] != "UNKNOWN":
                    eid = f"EV_{int(ts * 1000)}_FACE_{fm['person_id']}"
                    h = self.security.record_event(eid, "FACE_MATCH", fm, frame)
                    all_alerts.append({"event_id": eid, "type": "FACE_MATCH",
                                       "hash": h, "metadata": fm})

        # ── ANPR ────────────────────────────────────────────────────────
        vehicle_dets = [d for d in detections if d["label"] in ("car", "motorcycle", "truck", "bus")]
        if vehicle_dets and self.anpr.available:
            plates = self.anpr.process(frame, vehicle_dets)
            for p in plates:
                vx1, vy1, vx2, vy2 = p["vehicle_box"]
                color = (0, 255, 0) if p["is_valid"] else (0, 100, 255)
                cv2.putText(frame, p["plate"], (vx1, vy1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                if p["is_valid"]:
                    eid = f"EV_{int(ts * 1000)}_ANPR_{p['plate']}"
                    h = self.security.record_event(eid, "ANPR_HIT", p, frame)
                    all_alerts.append({"event_id": eid, "type": "ANPR_HIT",
                                       "hash": h, "metadata": p})

        # ── Overlay Rendering ───────────────────────────────────────────
        # Tripwire line (cyan)
        cv2.line(frame, self.geometry.tripwire_p1, self.geometry.tripwire_p2,
                 (0, 255, 255), 2)
        cv2.putText(frame, "VIRTUAL FENCE", 
                    (self.geometry.tripwire_p1[0], self.geometry.tripwire_p1[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        # Restricted zone polygon (red)
        pts = np.array(self.geometry.restricted_coords, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 0, 255), 2)

        # Detection bounding boxes & labels
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            is_alerting = any(
                a.get("metadata", {}).get("track_id") == det["track_id"]
                for a in all_alerts
            )
            color = (0, 0, 255) if is_alerting else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID:{det['track_id']} {det['label']}",
                        (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

            # Draw track trail
            trail = self.tracked_positions.get(det["track_id"], [])
            for i in range(1, len(trail)):
                cv2.line(frame, trail[i - 1], trail[i], (255, 255, 0), 1)

        # Night-vision badge
        if was_enhanced:
            cv2.putText(frame, "NIGHT VISION: ACTIVE", (8, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 128), 1)

        # Timestamp watermark
        cv2.putText(frame, iso_ts, (8, CONFIG["INFERENCE_HEIGHT"] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        return frame, all_alerts


# ═══════════════════════════════════════════════════════════════════════════════
# §8  FASTAPI COMMAND & CONTROL SERVER
# ═══════════════════════════════════════════════════════════════════════════════
app = FastAPI(title="IBVAP Edge C2 Server", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

connected_ws: List[WebSocket] = []
latest_frame_b64: str = ""
pipeline_ref: Optional[EdgeVisionPipeline] = None


class VerifyRequest(BaseModel):
    event_id: str
    test_hash: str


@app.get("/health")
def health():
    return {"status": "online", "bop": CONFIG["BOP_ID"], "camera": CONFIG["CAMERA_ID"]}


@app.get("/api/v1/alerts")
def get_alerts(limit: int = 50):
    engine = SecurityAuditEngine()
    with sqlite3.connect(CONFIG["DB_PATH"]) as conn:
        rows = conn.execute(
            "SELECT event_id, bop_id, camera_id, timestamp, alert_type, sha256_hash, metadata "
            "FROM audit_trail ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        {"event_id": r[0], "bop_id": r[1], "camera_id": r[2],
         "timestamp": r[3], "alert_type": r[4], "sha256_hash": r[5],
         "metadata": json.loads(r[6]) if r[6] else {}}
        for r in rows
    ]


@app.post("/api/v1/verify")
def verify_evidence(req: VerifyRequest):
    engine = SecurityAuditEngine()
    result = engine.verify(req.event_id, req.test_hash)
    if result is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"verified": result, "event_id": req.event_id, "test_hash": req.test_hash}


@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await websocket.accept()
    connected_ws.append(websocket)
    logger.info(f"📡 Dashboard connected ({len(connected_ws)} clients)")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        connected_ws.remove(websocket)
        logger.info(f"📡 Dashboard disconnected ({len(connected_ws)} clients)")


@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    """Push latest processed frame as base64 JPEG at ~15 FPS."""
    await websocket.accept()
    try:
        while True:
            if latest_frame_b64:
                await websocket.send_text(latest_frame_b64)
            await asyncio.sleep(0.066)
    except WebSocketDisconnect:
        pass


# ── Embedded C2 Dashboard ──────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IBVAP — Border Surveillance C2</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'tac-dark': '#0a0e1a',
                        'tac-panel': '#111827',
                        'tac-border': '#1f2937',
                        'cyan-acc': '#00f0ff',
                        'alert-red': '#ff3366',
                        'alert-amber': '#ffaa00',
                        'alert-green': '#00ff88',
                    },
                    fontFamily: {
                        mono: ['"JetBrains Mono"', 'monospace'],
                        sans: ['Inter', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        body { background: #0a0e1a; }
        .glass { background: rgba(17,24,39,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(31,41,55,0.6); }
        @keyframes pulse-glow { 0%,100%{box-shadow:0 0 4px #ff3366} 50%{box-shadow:0 0 16px #ff3366} }
        .pulse-dot { animation: pulse-glow 1.5s ease-in-out infinite; }
        @keyframes scanline { from{transform:translateY(-100%)} to{transform:translateY(100%)} }
        .scanline::after { content:''; position:absolute; inset:0; background:linear-gradient(transparent 50%,rgba(0,240,255,0.03) 50%); background-size:100% 4px; pointer-events:none; }
        ::-webkit-scrollbar { width:6px } ::-webkit-scrollbar-track { background:#111827 } ::-webkit-scrollbar-thumb { background:#374151; border-radius:3px }
        ::-webkit-scrollbar-thumb:hover { background:#4b5563 }
    </style>
</head>
<body class="text-white font-sans overflow-hidden h-screen flex flex-col p-3 gap-3">

    <!-- Top Bar -->
    <header class="glass rounded-xl px-5 py-3 flex justify-between items-center shrink-0">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-cyan-acc/10 border border-cyan-acc/40 flex items-center justify-center">
                <svg class="w-5 h-5 text-cyan-acc" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            </div>
            <div>
                <h1 class="font-mono font-bold text-lg tracking-[0.2em] text-cyan-acc drop-shadow-[0_0_10px_rgba(0,240,255,0.6)]">IBVAP</h1>
                <p class="text-[10px] text-gray-500 font-mono">INTELLIGENT BORDER VIDEO ANALYTICS PLATFORM</p>
            </div>
        </div>
        <div class="flex items-center gap-6">
            <div class="text-right">
                <p class="text-[10px] text-gray-500 font-mono">BOP SECTOR</p>
                <p class="text-xs font-mono text-cyan-acc">""" + CONFIG["BOP_ID"] + """</p>
            </div>
            <div class="h-8 w-px bg-tac-border"></div>
            <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-alert-green pulse-dot" id="statusDot"></div>
                <span class="text-xs font-mono" id="statusText">CONNECTING</span>
            </div>
            <div class="font-mono text-sm text-gray-300" id="clock"></div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="flex flex-1 gap-3 min-h-0">

        <!-- Left: Video Feed -->
        <div class="flex-1 flex flex-col gap-3 min-w-0">
            <div class="glass rounded-xl flex-1 p-3 relative overflow-hidden scanline">
                <div class="absolute top-3 left-3 z-10 flex items-center gap-2 bg-black/60 backdrop-blur px-3 py-1.5 rounded-lg border border-tac-border/50">
                    <div class="w-2 h-2 rounded-full bg-alert-red pulse-dot"></div>
                    <span class="font-mono text-xs text-alert-red font-bold">REC</span>
                    <span class="font-mono text-[10px] text-gray-400 ml-2" id="fpsCounter">0 FPS</span>
                </div>
                <div class="absolute top-3 right-3 z-10 bg-black/60 backdrop-blur px-3 py-1.5 rounded-lg border border-tac-border/50">
                    <span class="font-mono text-xs text-cyan-acc">""" + CONFIG["CAMERA_ID"] + """</span>
                </div>
                <img id="videoFrame" class="w-full h-full object-contain rounded-lg" src="" alt="Awaiting feed...">
                <div class="absolute bottom-3 left-3 z-10 bg-black/60 backdrop-blur px-3 py-1.5 rounded-lg border border-tac-border/50">
                    <span class="font-mono text-[10px] text-gray-400">AI ANALYTICS: </span>
                    <span class="font-mono text-[10px] text-alert-green font-bold">ACTIVE</span>
                </div>
            </div>
            <!-- Stats Bar -->
            <div class="glass rounded-xl px-4 py-2 flex justify-between items-center shrink-0">
                <div class="flex gap-6">
                    <div><span class="text-[10px] text-gray-500 font-mono block">TOTAL ALERTS</span><span class="text-lg font-mono font-bold text-alert-red" id="statTotal">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">TRIPWIRE</span><span class="text-lg font-mono font-bold text-alert-amber" id="statTW">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">ZONE</span><span class="text-lg font-mono font-bold text-cyan-acc" id="statZone">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">CRAWLING</span><span class="text-lg font-mono font-bold text-alert-amber" id="statCrawl">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">LOITERING</span><span class="text-lg font-mono font-bold text-alert-green" id="statLoiter">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">FACE MATCH</span><span class="text-lg font-mono font-bold text-purple-400" id="statFace">0</span></div>
                    <div><span class="text-[10px] text-gray-500 font-mono block">ANPR</span><span class="text-lg font-mono font-bold text-blue-400" id="statANPR">0</span></div>
                </div>
            </div>
        </div>

        <!-- Right: Alert Feed -->
        <div class="w-[380px] shrink-0 glass rounded-xl flex flex-col overflow-hidden">
            <div class="px-4 py-3 border-b border-tac-border/40 flex justify-between items-center shrink-0">
                <h2 class="font-mono font-bold text-cyan-acc tracking-wider text-sm flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>
                    INCIDENT FEED
                </h2>
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-alert-red pulse-dot"></div>
                    <span class="text-[10px] font-mono text-gray-400">LIVE</span>
                </div>
            </div>
            <div id="alertFeed" class="flex-1 overflow-y-auto p-3 space-y-2"></div>
        </div>
    </div>

    <script>
        // Clock
        setInterval(() => {
            document.getElementById('clock').textContent = new Date().toLocaleTimeString('en-US', {hour12: false}) + ' IST';
        }, 1000);

        // Stats
        const stats = {total:0, TRIPWIRE_BREACH:0, ZONE_INTRUSION:0, SUSPICIOUS_CRAWLING:0, LOITERING:0, FACE_MATCH:0, ANPR_HIT:0};
        function updateStats(type) {
            stats.total++;
            if (stats[type] !== undefined) stats[type]++;
            document.getElementById('statTotal').textContent = stats.total;
            document.getElementById('statTW').textContent = stats.TRIPWIRE_BREACH;
            document.getElementById('statZone').textContent = stats.ZONE_INTRUSION;
            document.getElementById('statCrawl').textContent = stats.SUSPICIOUS_CRAWLING;
            document.getElementById('statLoiter').textContent = stats.LOITERING;
            document.getElementById('statFace').textContent = stats.FACE_MATCH;
            document.getElementById('statANPR').textContent = stats.ANPR_HIT;
        }

        // Alert colors
        const alertColors = {
            'TRIPWIRE_BREACH': 'border-alert-red', 'ZONE_INTRUSION': 'border-cyan-acc',
            'SUSPICIOUS_CRAWLING': 'border-alert-amber', 'LOITERING': 'border-alert-green',
            'FACE_MATCH': 'border-purple-400', 'ANPR_HIT': 'border-blue-400'
        };
        const typeLabels = {
            'TRIPWIRE_BREACH': '⚡ TRIPWIRE', 'ZONE_INTRUSION': '🚫 ZONE BREACH',
            'SUSPICIOUS_CRAWLING': '🐍 CRAWLING', 'LOITERING': '⏱️ LOITERING',
            'FACE_MATCH': '👤 FACE MATCH', 'ANPR_HIT': '🚗 PLATE DETECTED'
        };

        // WebSocket: Alerts
        let ws;
        function connectAlerts() {
            ws = new WebSocket(`ws://${location.host}/ws/alerts`);
            ws.onopen = () => {
                document.getElementById('statusDot').className = 'w-2 h-2 rounded-full bg-alert-green pulse-dot';
                document.getElementById('statusText').textContent = 'SYS ONLINE';
                document.getElementById('statusText').className = 'text-xs font-mono text-alert-green';
            };
            ws.onmessage = (e) => {
                const d = JSON.parse(e.data);
                updateStats(d.type);
                const feed = document.getElementById('alertFeed');
                const el = document.createElement('div');
                const bc = alertColors[d.type] || 'border-gray-500';
                const tl = typeLabels[d.type] || d.type;
                el.className = `bg-black/40 border-l-4 ${bc} p-3 rounded-lg text-xs space-y-1.5 transition-all animate-[fadeIn_0.3s]`;
                el.innerHTML = `
                    <div class="flex justify-between items-center">
                        <span class="font-mono font-bold text-white">${tl}</span>
                        <span class="text-[10px] text-gray-500 font-mono">${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div class="font-mono text-[10px] text-gray-400">ID: ${d.event_id}</div>
                    <div class="font-mono text-[10px] text-cyan-acc/80 break-all select-all">SHA-256: ${d.hash}</div>
                    <button onclick="verifyHash('${d.event_id}','${d.hash}',this)" class="mt-1 px-2 py-0.5 bg-tac-dark border border-cyan-acc/40 text-cyan-acc rounded text-[10px] font-mono hover:bg-cyan-acc/10 transition-colors">VERIFY HASH</button>
                `;
                feed.prepend(el);
                // Keep max 200
                while (feed.children.length > 200) feed.removeChild(feed.lastChild);
                // Audio beep for critical alerts
                if (['TRIPWIRE_BREACH','FACE_MATCH'].includes(d.type)) {
                    try { const a=new AudioContext(),o=a.createOscillator(),g=a.createGain();o.connect(g);g.connect(a.destination);o.frequency.value=880;g.gain.value=0.08;o.start();setTimeout(()=>o.stop(),150); } catch(e){}
                }
            };
            ws.onclose = () => {
                document.getElementById('statusDot').className = 'w-2 h-2 rounded-full bg-alert-red pulse-dot';
                document.getElementById('statusText').textContent = 'RECONNECTING';
                document.getElementById('statusText').className = 'text-xs font-mono text-alert-red';
                setTimeout(connectAlerts, 2000);
            };
        }
        connectAlerts();

        // Verify hash
        async function verifyHash(eventId, hash, btn) {
            btn.textContent = 'VERIFYING...'; btn.disabled = true;
            try {
                const res = await fetch('/api/v1/verify', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({event_id:eventId, test_hash:hash})});
                const data = await res.json();
                if (data.verified) {
                    btn.textContent = '✅ INTEGRITY VERIFIED';
                    btn.className = btn.className.replace('border-cyan-acc/40 text-cyan-acc','border-alert-green/60 text-alert-green');
                } else {
                    btn.textContent = '❌ HASH MISMATCH';
                    btn.className = btn.className.replace('border-cyan-acc/40 text-cyan-acc','border-alert-red/60 text-alert-red');
                }
            } catch(e) { btn.textContent = '⚠ VERIFY FAILED'; }
        }

        // WebSocket: Video Stream
        let frameCount = 0, lastFpsTime = Date.now();
        function connectStream() {
            const vs = new WebSocket(`ws://${location.host}/ws/stream`);
            vs.onmessage = (e) => {
                document.getElementById('videoFrame').src = 'data:image/jpeg;base64,' + e.data;
                frameCount++;
                const now = Date.now();
                if (now - lastFpsTime >= 1000) {
                    document.getElementById('fpsCounter').textContent = frameCount + ' FPS';
                    frameCount = 0; lastFpsTime = now;
                }
            };
            vs.onclose = () => setTimeout(connectStream, 2000);
        }
        connectStream();
    </script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════════
# §9  THREADED WORKERS: VIDEO INGESTION & ALERT DISPATCH
# ═══════════════════════════════════════════════════════════════════════════════
def run_edge_inference(event_loop: asyncio.AbstractEventLoop):
    """Main inference thread: captures video, runs the full analytics
    pipeline, encodes processed frames, and dispatches alerts via WS."""
    global latest_frame_b64, pipeline_ref

    pipeline = EdgeVisionPipeline()
    pipeline_ref = pipeline

    source = CONFIG["VIDEO_SOURCE"]
    if isinstance(source, int) and os.name == "nt":
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(source)

    synthetic_mode = not cap.isOpened()
    if synthetic_mode:
        logger.warning("📹 No webcam/camera detected or camera busy — fallback to synthetic border feed.")
    else:
        logger.info(f"📹 Live Camera opened successfully: {source}")

    reconnect_delay = 1.0

    while True:
        if not synthetic_mode:
            ret, frame = cap.read()
            if not ret:
                # Attempt reconnect with exponential backoff
                logger.warning(f"📹 Frame read failed. Reconnecting in {reconnect_delay:.0f}s...")
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 30.0)
                cap.release()
                if isinstance(source, int) and os.name == "nt":
                    cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(source)
                if cap.isOpened():
                    reconnect_delay = 1.0
                    logger.info("📹 Reconnected successfully.")
                continue
            reconnect_delay = 1.0
        else:
            # Generate synthetic frame with low-light noise
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (30, 30, 30)
            noise = np.random.randint(0, 15, frame.shape, dtype=np.uint8)
            frame = cv2.add(frame, noise)

        # Run full analytics pipeline
        processed, alerts = pipeline.process_frame(frame)

        # Encode frame for streaming
        _, jpg_buf = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, 70])
        latest_frame_b64 = base64.b64encode(jpg_buf).decode("ascii")

        # Broadcast alerts via WebSocket
        for alert in alerts:
            alert_json = json.dumps(alert, default=str)
            for ws in connected_ws[:]:
                try:
                    asyncio.run_coroutine_threadsafe(ws.send_text(alert_json), event_loop)
                except Exception:
                    pass

        time.sleep(0.04)  # ~25 FPS


# ═══════════════════════════════════════════════════════════════════════════════
# §10  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("""
    +==================================================================+
    |   ___  ______  _    _    ___    ____                             |
    |  |_ _|| __ ) \\| \\  / |  / _ \\  |  _ \\                           |
    |   | | |  _ \\  \\ \\/ /  | |_| | | |_) |                           |
    |   | | | |_) |  \\  /   |  _  | |  __/                            |
    |  |___||____/    \\/    |_| |_| |_|                               |
    |                                                                  |
    |  Intelligent Border Video Analytics Platform  v2.0               |
    |  SSB - Ministry of Home Affairs - Problem Statement 26187       |
    +==================================================================+
    """)

    loop = asyncio.new_event_loop()

    # Start inference thread
    inference_thread = threading.Thread(
        target=run_edge_inference, args=(loop,), daemon=True
    )
    inference_thread.start()

    logger.info(f"🚀 IBVAP C2 Server → http://localhost:{CONFIG['API_PORT']}")
    logger.info(f"📡 WebSocket alerts → ws://localhost:{CONFIG['API_PORT']}/ws/alerts")
    logger.info(f"📹 Video stream    → ws://localhost:{CONFIG['API_PORT']}/ws/stream")

    uvicorn.run(app, host="0.0.0.0", port=CONFIG["API_PORT"], log_level="warning")
