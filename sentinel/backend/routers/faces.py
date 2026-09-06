import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import numpy as np

from backend.config import UPLOADS_DIR, FACE_THUMBNAILS_DIR, FACE_SIMILARITY_THRESHOLD, EXPORTS_DIR
from backend.pipeline.face_processor import FaceProcessor
import cv2

router = APIRouter(prefix="/api/faces", tags=["Faces"])
face_processor = FaceProcessor()

class RegisterFaceRequest(BaseModel):
    suspect_name: Optional[str] = None
    label: Optional[str] = None
    face_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    bbox: Optional[Dict[str, Any]] = None
    source_image: Optional[str] = None

@router.post("/upload")
async def upload_face_image(request: Request, file: UploadFile = File(...)):
    """Accept image, detect faces, extract embeddings, return face_id + bounding boxes"""
    file_id = f"IMG-{uuid.uuid4().hex[:8]}"
    safe_name = os.path.basename(file.filename or "image.jpg")
    file_path = os.path.join(UPLOADS_DIR, f"{file_id}_{safe_name}")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    faces = face_processor.detect_faces(file_path)
    results = []
    
    for idx, bbox in enumerate(faces):
        emb = face_processor.compute_embedding(file_path, bbox)
        emb_list = emb.tolist() if emb is not None and hasattr(emb, 'tolist') else (list(emb) if emb is not None else [0.0] * 128)
        top = int(bbox.get("top", 0))
        right = int(bbox.get("right", 100))
        bottom = int(bbox.get("bottom", 100))
        left = int(bbox.get("left", 0))
        width = max(1, right - left)
        height = max(1, bottom - top)

        results.append({
            "id": f"FACE-{idx+1}",
            "confidence": 0.95,
            "bbox": bbox,
            "bounding_box": {
                "x": left,
                "y": top,
                "width": width,
                "height": height
            },
            "embedding": emb_list,
        })
        
    return {
        "status": "success",
        "file_path": file_path,
        "faces_detected": len(results),
        "faces": results
    }

@router.post("/register")
async def register_face(request: Request, data: RegisterFaceRequest):
    """Register a face as named suspect profile in SQLite"""
    try:
        db = request.app.state.db
    except AttributeError:
        raise HTTPException(status_code=500, detail="Database not initialized")

    face_id = data.face_id or f"FACE-{uuid.uuid4().hex[:8].upper()}"
    suspect_name = data.suspect_name or data.label or "Suspect"
    embedding = data.embedding or [0.0] * 128
    
    thumbnail_path = os.path.join(FACE_THUMBNAILS_DIR, f"{face_id}.jpg")
    if data.source_image and data.bbox and os.path.exists(data.source_image):
        try:
            face_processor.crop_face_thumbnail(data.source_image, data.bbox, thumbnail_path)
        except Exception as e:
            print(f"Thumbnail warning: {e}")

    now = datetime.now().isoformat()
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("""
            INSERT OR REPLACE INTO face_profiles (id, suspect_name, embedding_json, registered_by, timestamp, thumbnail_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (face_id, suspect_name, json.dumps(embedding), "SYSTEM", now, thumbnail_path))
        conn.commit()
    finally:
        conn.close()
        
    return {"status": "success", "face_id": face_id, "suspect_name": suspect_name}

@router.get("/search/{face_id}")
@router.get("/search")
async def search_face(request: Request, face_id: str, min_similarity: Optional[float] = None):
    """Compare face against all evidence images"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT embedding_json FROM face_profiles WHERE id = ?", (face_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Face profile not found")
        known_embedding = np.array(json.loads(row["embedding_json"]))
    finally:
        conn.close()
        
    threshold = (min_similarity / 100.0) if (min_similarity and min_similarity > 1.0) else (min_similarity or FACE_SIMILARITY_THRESHOLD)
    matches = face_processor.scan_directory(known_embedding, UPLOADS_DIR, threshold)
    return {"status": "success", "matches": matches}

@router.post("/scan-all/{face_id}")
async def scan_all(request: Request, face_id: str):
    """Scan registered face against all uploads"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT embedding_json FROM face_profiles WHERE id = ?", (face_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Face profile not found")
        known_embedding = np.array(json.loads(row["embedding_json"]))
    finally:
        conn.close()
        
    matches = face_processor.scan_directory(known_embedding, UPLOADS_DIR, FACE_SIMILARITY_THRESHOLD)
    
    now = datetime.now().isoformat()
    conn = sqlite3.connect(db.db_path)
    try:
        for match in matches:
            match_id = f"MATCH-{uuid.uuid4().hex[:8]}"
            conn.execute("""
                INSERT INTO face_match_log (id, face_id, source_image, similarity_score, match_timestamp, bbox_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (match_id, face_id, match["file_path"], match["similarity"], now, json.dumps(match["bbox"])))
        conn.commit()
    finally:
        conn.close()
        
    return {"status": "success", "matches_found": len(matches)}

@router.get("/profiles")
async def list_profiles(request: Request):
    """List all registered face profiles"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT id, suspect_name, timestamp, thumbnail_path FROM face_profiles")
        rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
    return rows

@router.delete("/profiles/{face_id}")
async def delete_profile(request: Request, face_id: str):
    """Remove a face profile"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    try:
        cursor = conn.execute("DELETE FROM face_profiles WHERE id = ?", (face_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Face profile not found")
    finally:
        conn.close()
    return {"status": "success"}

@router.get("/report/{face_id}")
async def generate_report(request: Request, face_id: str):
    """Generate ReportLab PDF match report"""
    from reportlab.pdfgen import canvas
    
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT * FROM face_profiles WHERE id = ?", (face_id,))
        profile = cursor.fetchone()
        if not profile:
            raise HTTPException(status_code=404, detail="Face profile not found")
            
        cursor = conn.execute("SELECT * FROM face_match_log WHERE face_id = ?", (face_id,))
        matches = cursor.fetchall()
    finally:
        conn.close()
        
    report_path = os.path.join(EXPORTS_DIR, f"face_report_{face_id}.pdf")
    c = canvas.Canvas(report_path)
    c.drawString(100, 800, f"Face Match Report: {profile['suspect_name']}")
    c.drawString(100, 780, f"Face ID: {face_id}")
    c.drawString(100, 760, f"Matches Found: {len(matches)}")
    
    y = 720
    for match in matches:
        if y < 100:
            c.showPage()
            y = 800
        c.drawString(100, y, f"Match: {match['source_image']} (Score: {match['similarity_score']:.2f})")
        y -= 20
        
    c.save()
    return FileResponse(report_path, filename=f"face_report_{face_id}.pdf")

@router.get("/thumbnail/{face_id}")
async def get_thumbnail(request: Request, face_id: str):
    """Serve cropped face thumbnail"""
    db = request.app.state.db
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT thumbnail_path FROM face_profiles WHERE id = ?", (face_id,))
        row = cursor.fetchone()
        if not row or not os.path.exists(row["thumbnail_path"]):
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        return FileResponse(row["thumbnail_path"])
    finally:
        conn.close()
