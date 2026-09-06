import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response

import time
import hashlib
from backend.config import UPLOADS_DIR, PERSON_CAPTURES_DIR, PERSON_CONFIDENCE_THRESHOLD, EXPORTS_DIR

router = APIRouter(prefix="/api/persons", tags=["Persons"])

@router.post("/detect")
async def detect_persons(request: Request, file: UploadFile = File(...)):
    """Detect persons in uploaded evidence image (source='uploaded', RED boxes)"""
    t0 = time.time()
    file_id = f"EVID-{uuid.uuid4().hex[:8]}"
    file_path = os.path.join(UPLOADS_DIR, f"{file_id}_{file.filename}")
    
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
        
    file_hash = hashlib.sha256(content).hexdigest()
    detector = request.app.state.person_detector
    detections = detector.detect_persons(image_path=file_path, confidence_threshold=PERSON_CONFIDENCE_THRESHOLD)
    
    annotated_bytes = detector.draw_annotated_image(content, detections, source_type='uploaded')
    annotated_path = os.path.join(UPLOADS_DIR, f"annotated_{file_id}.jpg")
    with open(annotated_path, "wb") as f:
        f.write(annotated_bytes)
        
    db = request.app.state.db
    now = datetime.now().isoformat()
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    try:
        det_id = f"PDET-{uuid.uuid4().hex[:8]}"
        conn.execute("""
            INSERT INTO person_detections (id, source_image, detection_count, timestamp, bboxes_json, confidence_scores_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (det_id, annotated_path, len(detections), now, json.dumps([d["bbox"] for d in detections]), json.dumps([d["confidence"] for d in detections])))
        conn.commit()
    finally:
        conn.close()
        
    import cv2
    import numpy as np
    img_arr = np.frombuffer(content, np.uint8)
    decoded = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    img_h, img_w = decoded.shape[:2] if decoded is not None else (720, 1280)
    
    persons = []
    for idx, d in enumerate(detections):
        x1, y1, x2, y2 = d["bbox"]
        w = max(0, x2 - x1)
        h = max(0, y2 - y1)
        area_pct = round((w * h) / (max(1, img_w * img_h)) * 100, 2)
        persons.append({
            "person_index": idx + 1,
            "bounding_box": {"x": x1, "y": y1, "width": w, "height": h},
            "confidence": round(float(d["confidence"]), 4),
            "source": "uploaded",
            "area_percentage": area_pct,
            "timestamp": now
        })
        
    return {
        "status": "success",
        "detection_id": det_id,
        "source_type": "uploaded",
        "image_width": img_w,
        "image_height": img_h,
        "persons": persons,
        "total_persons": len(persons),
        "count": len(persons),
        "processing_time_ms": round((time.time() - t0) * 1000, 1),
        "file_name": file.filename,
        "sha256_hash": file_hash,
        "timestamp": now
    }

@router.post("/detect-frame")
async def detect_frame(request: Request, file: UploadFile = File(None), frame: UploadFile = File(None)):
    """Fast detection on live webcam frame (source='live', GREEN boxes)"""
    upload = frame or file
    if upload is None:
        raise HTTPException(status_code=400, detail="No frame uploaded")
        
    t0 = time.time()
    image_data = await upload.read()
    detector = request.app.state.person_detector
    
    detections = detector.detect_persons(image_data=image_data, fast_mode=True, confidence_threshold=PERSON_CONFIDENCE_THRESHOLD)
    now = datetime.now().isoformat()
    
    persons = []
    for idx, d in enumerate(detections):
        x1, y1, x2, y2 = d["bbox"]
        w = max(0, x2 - x1)
        h = max(0, y2 - y1)
        persons.append({
            "person_index": idx + 1,
            "bounding_box": {"x": x1, "y": y1, "width": w, "height": h},
            "confidence": round(float(d["confidence"]), 4),
            "source": "live",
            "area_percentage": 0.0,
            "timestamp": now
        })
        
    return {
        "status": "success",
        "source_type": "live",
        "persons_count": len(persons),
        "persons": persons,
        "processing_time_ms": round((time.time() - t0) * 1000, 1),
        "timestamp": now
    }

@router.post("/batch-detect")
async def batch_detect(request: Request, files: List[UploadFile] = File(...)):
    """Batch detect from multiple images"""
    results = []
    detector = request.app.state.person_detector
    
    for file in files:
        image_data = await file.read()
        detections = detector.detect_persons(image_data=image_data, confidence_threshold=PERSON_CONFIDENCE_THRESHOLD)
        results.append({
            "filename": file.filename,
            "count": len(detections),
            "detections": detections
        })
        
    return {"status": "success", "results": results}

@router.post("/capture")
async def capture_frame(request: Request, file: UploadFile = File(None), frame: UploadFile = File(None)):
    """Save captured live frame with blockchain seal"""
    upload = frame or file
    if upload is None:
        raise HTTPException(status_code=400, detail="No frame uploaded")
        
    image_data = await upload.read()
    detector = request.app.state.person_detector
    
    detections = detector.detect_persons(image_data=image_data, fast_mode=True, confidence_threshold=PERSON_CONFIDENCE_THRESHOLD)
    annotated_bytes = detector.draw_annotated_image(image_data, detections, source_type='live')
    
    cap_id = f"CAP-{uuid.uuid4().hex[:8]}"
    cap_path = os.path.join(PERSON_CAPTURES_DIR, f"{cap_id}.jpg")
    
    with open(cap_path, "wb") as f:
        f.write(annotated_bytes)
        
    file_hash = hashlib.sha256(annotated_bytes).hexdigest()
    blockchain = request.app.state.blockchain
    blockchain.add_block(file_hash, f"{cap_id}.jpg", "image/jpeg", "SYSTEM")
    
    db = request.app.state.db
    now = datetime.now().isoformat()
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    try:
        conn.execute("""
            INSERT INTO person_captures (id, capture_path, detection_count, timestamp, blockchain_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (cap_id, cap_path, len(detections), now, file_hash))
        conn.commit()
    finally:
        conn.close()
        
    return {"status": "success", "capture_id": cap_id, "blockchain_hash": file_hash}

@router.get("/history")
async def get_history(request: Request):
    """List detection history"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT * FROM person_detections ORDER BY timestamp DESC LIMIT 100")
        rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
    return rows

@router.get("/export-log")
async def export_log(request: Request):
    """Export detection log as CSV"""
    import csv
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT * FROM person_detections ORDER BY timestamp DESC")
        rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
        
    csv_path = os.path.join(EXPORTS_DIR, "person_detections.csv")
    with open(csv_path, "w", newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=["id", "source_image", "detection_count", "timestamp", "bboxes_json", "confidence_scores_json"])
            writer.writeheader()
            writer.writerows(rows)
        else:
            writer = csv.writer(f)
            writer.writerow(["id", "source_image", "detection_count", "timestamp", "bboxes_json", "confidence_scores_json"])
        
    return FileResponse(csv_path, filename="person_detections.csv")

@router.get("/annotated/{detection_id}")
async def get_annotated_image(request: Request, detection_id: str):
    """Serve pre-annotated image"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT source_image FROM person_detections WHERE id = ?", (detection_id,))
        row = cursor.fetchone()
        if not row or not os.path.exists(row["source_image"]):
            raise HTTPException(status_code=404, detail="Annotated image not found")
        return FileResponse(row["source_image"])
    finally:
        conn.close()
