import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import asyncio
import json

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import (
    init_db, get_session, AlertEvent, Camera, BOP, WatchlistPerson, WatchlistVehicle,
    AlertType, Severity, CameraStatus, PersonCategory
)

app = FastAPI(title="IBVAP Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_alert_connections: List[WebSocket] = []
        self.active_stream_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect_alert(self, websocket: WebSocket):
        await websocket.accept()
        self.active_alert_connections.append(websocket)
        
    def disconnect_alert(self, websocket: WebSocket):
        if websocket in self.active_alert_connections:
            self.active_alert_connections.remove(websocket)
            
    async def broadcast_alert(self, message: dict):
        for connection in self.active_alert_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass
                
    async def connect_stream(self, websocket: WebSocket, camera_id: str):
        await websocket.accept()
        if camera_id not in self.active_stream_connections:
            self.active_stream_connections[camera_id] = []
        self.active_stream_connections[camera_id].append(websocket)
        
    def disconnect_stream(self, websocket: WebSocket, camera_id: str):
        if camera_id in self.active_stream_connections and websocket in self.active_stream_connections[camera_id]:
            self.active_stream_connections[camera_id].remove(websocket)
            
    async def broadcast_stream(self, camera_id: str, frame_data: str):
        if camera_id in self.active_stream_connections:
            for connection in self.active_stream_connections[camera_id]:
                try:
                    await connection.send_text(frame_data)
                except Exception:
                    pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class AlertCreate(BaseModel):
    bop_id: str
    camera_id: str
    alert_type: str
    severity: str
    timestamp: Optional[datetime] = None
    description: Optional[str] = None
    sha256_hash: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    thumbnail_b64: Optional[str] = None
    track_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

@app.get("/api/v1/alerts")
async def get_alerts(
    page: int = 1,
    size: int = 50,
    bop_id: Optional[str] = None,
    camera_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None
):
    async with get_session() as session:
        query = select(AlertEvent).order_by(AlertEvent.timestamp.desc())
        
        if bop_id:
            query = query.where(AlertEvent.bop_id == bop_id)
        if camera_id:
            query = query.where(AlertEvent.camera_id == camera_id)
        if alert_type:
            query = query.where(AlertEvent.alert_type == AlertType(alert_type))
        if severity:
            query = query.where(AlertEvent.severity == Severity(severity))
            
        total_result = await session.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar_one()
        
        query = query.offset((page - 1) * size).limit(size)
        result = await session.execute(query)
        alerts = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "id": a.id, "bop_id": a.bop_id, "camera_id": a.camera_id,
                    "timestamp": a.timestamp.isoformat(), "alert_type": a.alert_type.value,
                    "severity": a.severity.value, "description": a.description,
                    "sha256_hash": a.sha256_hash, "latitude": a.latitude,
                    "longitude": a.longitude, "thumbnail_b64": a.thumbnail_b64,
                    "track_id": a.track_id, "metadata_json": a.metadata_json,
                    "synced_from_edge": a.synced_from_edge
                } for a in alerts
            ]
        }

@app.get("/api/v1/alerts/{alert_id}")
async def get_alert(alert_id: str):
    async with get_session() as session:
        result = await session.execute(select(AlertEvent).where(AlertEvent.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {
            "id": alert.id, "bop_id": alert.bop_id, "camera_id": alert.camera_id,
            "timestamp": alert.timestamp.isoformat(), "alert_type": alert.alert_type.value,
            "severity": alert.severity.value, "description": alert.description,
            "sha256_hash": alert.sha256_hash, "latitude": alert.latitude,
            "longitude": alert.longitude, "thumbnail_b64": alert.thumbnail_b64,
            "track_id": alert.track_id, "metadata_json": alert.metadata_json,
            "synced_from_edge": alert.synced_from_edge
        }

@app.post("/api/v1/alerts")
async def create_alert(alert: AlertCreate):
    async with get_session() as session:
        new_alert_kwargs = {
            "bop_id": alert.bop_id,
            "camera_id": alert.camera_id,
            "alert_type": AlertType(alert.alert_type),
            "severity": Severity(alert.severity),
            "description": alert.description,
            "sha256_hash": alert.sha256_hash,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "thumbnail_b64": alert.thumbnail_b64,
            "track_id": alert.track_id,
            "metadata_json": alert.metadata_json,
            "synced_from_edge": True
        }
        if alert.timestamp:
            new_alert_kwargs["timestamp"] = alert.timestamp
            
        new_alert = AlertEvent(**new_alert_kwargs)
        session.add(new_alert)
        await session.flush()
        
        alert_dict = {
            "id": new_alert.id,
            "bop_id": new_alert.bop_id,
            "camera_id": new_alert.camera_id,
            "alert_type": new_alert.alert_type.value,
            "severity": new_alert.severity.value,
            "timestamp": new_alert.timestamp.isoformat()
        }
        
        asyncio.create_task(manager.broadcast_alert(alert_dict))
        return {"status": "success", "id": new_alert.id}

class VerifyRequest(BaseModel):
    event_id: str
    test_hash: str

@app.post("/api/v1/verify")
async def verify_hash(req: VerifyRequest):
    async with get_session() as session:
        result = await session.execute(select(AlertEvent).where(AlertEvent.id == req.event_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        verified = (alert.sha256_hash == req.test_hash)
        return {
            "verified": verified,
            "stored_hash": alert.sha256_hash,
            "test_hash": req.test_hash
        }

@app.get("/api/v1/cameras")
async def list_cameras():
    async with get_session() as session:
        result = await session.execute(select(Camera))
        cameras = result.scalars().all()
        return [{"id": c.id, "bop_id": c.bop_id, "name": c.name, "rtsp_url": c.rtsp_url, "status": c.status.value} for c in cameras]

class CameraCreate(BaseModel):
    bop_id: str
    name: str
    rtsp_url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.post("/api/v1/cameras")
async def register_camera(camera: CameraCreate):
    async with get_session() as session:
        new_cam = Camera(
            bop_id=camera.bop_id,
            name=camera.name,
            rtsp_url=camera.rtsp_url,
            latitude=camera.latitude,
            longitude=camera.longitude
        )
        session.add(new_cam)
        await session.flush()
        return {"status": "success", "id": new_cam.id}

@app.get("/api/v1/bops")
async def list_bops():
    async with get_session() as session:
        result = await session.execute(select(BOP))
        bops = result.scalars().all()
        return [{"id": b.id, "name": b.name, "sector": b.sector, "battalion": b.battalion} for b in bops]

@app.get("/api/v1/stats")
async def get_stats():
    async with get_session() as session:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        alerts_today_res = await session.execute(select(func.count()).where(AlertEvent.timestamp >= today))
        alerts_today = alerts_today_res.scalar_one()
        
        active_cameras_res = await session.execute(select(func.count()).where(Camera.status == CameraStatus.ONLINE))
        active_cameras = active_cameras_res.scalar_one()
        
        return {
            "total_alerts_today": alerts_today,
            "active_cameras": active_cameras
        }

@app.get("/api/v1/watchlist/persons")
async def list_watchlist_persons():
    async with get_session() as session:
        result = await session.execute(select(WatchlistPerson))
        persons = result.scalars().all()
        return [{"id": p.id, "name": p.name, "category": p.category.value} for p in persons]

class PersonCreate(BaseModel):
    name: str
    alias: Optional[str] = None
    category: str
    photo_b64: Optional[str] = None
    embedding_b64: Optional[str] = None

@app.post("/api/v1/watchlist/persons")
async def add_watchlist_person(person: PersonCreate):
    async with get_session() as session:
        new_person = WatchlistPerson(
            name=person.name,
            alias=person.alias,
            category=PersonCategory(person.category),
            photo_b64=person.photo_b64,
            embedding_b64=person.embedding_b64
        )
        session.add(new_person)
        await session.flush()
        return {"status": "success", "id": new_person.id}

@app.get("/api/v1/watchlist/vehicles")
async def list_watchlist_vehicles():
    async with get_session() as session:
        result = await session.execute(select(WatchlistVehicle))
        vehicles = result.scalars().all()
        return [{"id": v.id, "plate_number": v.plate_number, "category": v.category.value} for v in vehicles]

class VehicleCreate(BaseModel):
    plate_number: str
    owner_name: Optional[str] = None
    category: str
    flagged_reason: Optional[str] = None

@app.post("/api/v1/watchlist/vehicles")
async def add_watchlist_vehicle(vehicle: VehicleCreate):
    async with get_session() as session:
        new_vehicle = WatchlistVehicle(
            plate_number=vehicle.plate_number,
            owner_name=vehicle.owner_name,
            category=PersonCategory(vehicle.category),
            flagged_reason=vehicle.flagged_reason
        )
        session.add(new_vehicle)
        await session.flush()
        return {"status": "success", "id": new_vehicle.id}

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect_alert(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_alert(websocket)

@app.websocket("/ws/stream/{camera_id}")
async def websocket_stream(websocket: WebSocket, camera_id: str):
    await manager.connect_stream(websocket, camera_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_stream(camera_id, data)
    except WebSocketDisconnect:
        manager.disconnect_stream(websocket, camera_id)

if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
