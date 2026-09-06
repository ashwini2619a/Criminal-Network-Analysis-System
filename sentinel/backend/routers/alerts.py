"""
SENTINEL v2.0 — Automated Alerts Router
Manages the 10 automated pattern detection alert types:
1. Shadow Kingpin Detected (Critical)
2. Hawala Loop Found (Critical)
3. Burner Phone Chain (High)
4. Pre-Crime Communication Spike (High)
5. Post-Crime Silence (High)
6. Financial Structuring (High)
7. Cross-State Movement (Medium)
8. New Gang Member Detected (Medium)
9. Co-Location Event (Medium)
10. Evidence Tampering Attempt (Critical)
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("")
@router.get("/")
@router.get("/all")
async def get_all_alerts(request: Request, limit: int = 100, unacknowledged: bool = False):
    db = getattr(request.app.state, "db", None)
    if not db:
        return []
    return db.get_alerts(limit=limit, unacknowledged_only=unacknowledged)

@router.get("/summary")
async def get_alerts_summary(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        return {"total": 0, "critical": 0, "high": 0, "medium": 0, "unacknowledged": 0}

    alerts = db.get_alerts(limit=500)
    unack = [a for a in alerts if not a.get("acknowledged")]
    return {
        "total": len(alerts),
        "unacknowledged": len(unack),
        "critical": len([a for a in alerts if a.get("priority") == "CRITICAL"]),
        "high": len([a for a in alerts if a.get("priority") == "HIGH"]),
        "medium": len([a for a in alerts if a.get("priority") == "MEDIUM"]),
        "low": len([a for a in alerts if a.get("priority") == "LOW"])
    }

@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    success = db.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return {"status": "ok", "alert_id": alert_id, "acknowledged": True}

@router.post("/dismiss/{alert_id}")
async def dismiss_alert(alert_id: str, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    success = db.dismiss_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return {"status": "ok", "alert_id": alert_id, "dismissed": True}

@router.post("/escalate/{alert_id}")
async def escalate_alert(alert_id: str, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    case = db.escalate_alert(alert_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return {"status": "ok", "alert_id": alert_id, "escalated": True, "case": case}

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    success = db.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return {"status": "ok", "deleted_alert_id": alert_id}

@router.post("/clear")
async def clear_alerts(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    db.clear_alerts()
    return {"status": "ok", "message": "All alert records cleared"}
