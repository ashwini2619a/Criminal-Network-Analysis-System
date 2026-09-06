"""
SENTINEL v2.0 — Collaborative Case Board Router (Screen 13, Auto-Feature 9)
Manages Kanban workflow columns:
NEW -> UNDER_ANALYSIS -> LEADS_GENERATED -> CHARGESHEET_READY
with shared investigator annotations and officer assignments.
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.models.enums import CaseStatus, CrimeType, Severity
from backend.models.schemas import CaseCard, MoveCaseRequest

router = APIRouter(prefix="/api/caseboard", tags=["caseboard"])

class AddNoteRequest(BaseModel):
    case_id: str
    officer: str
    note: str

@router.get("/cards")
async def get_caseboard_cards(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        return []

    cards = db.get_caseboard_cards()
    if not cards or len(cards) < 8:
        # Seed initial realistic cases from incidents if empty
        graph_store = getattr(request.app.state, "graph_store", None)
        G = graph_store.graph if graph_store else None
        
        incidents = [d for n, d in G.nodes(data=True) if d.get("node_type") == "Incident"] if G else []
        seeded = []
        statuses = [CaseStatus.NEW, CaseStatus.UNDER_ANALYSIS, CaseStatus.LEADS_GENERATED, CaseStatus.CHARGESHEET_READY]
        officers = ["Inspector R. K. Choudhary", "SI Animesh Verma", "Inspector Sunita Rao", "DSP Rajesh Mishra"]

        total_to_seed = max(8, len(incidents))
        for idx in range(min(8, total_to_seed)):
            inc = incidents[idx] if idx < len(incidents) else {}
            now = datetime.now().isoformat()
            st = statuses[idx % len(statuses)]
            card = {
                "id": f"CASE-{inc.get('fir_no', f'2026/{100+idx}').replace('/', '-')}",
                "case_no": inc.get("fir_no", f"FIR/2026/{100+idx}"),
                "title": f"Organized {inc.get('crime_type', 'EXTORTION').title()} Case at {inc.get('police_station', 'Kotwali PS')}",
                "crime_type": inc.get("crime_type", "EXTORTION"),
                "severity": inc.get("severity", "HIGH"),
                "status": st.value,
                "assigned_officer": officers[idx % len(officers)],
                "lead_suspect": "Vikram Sinha" if idx % 2 == 0 else "Sunil @ Bullet",
                "suspect_count": 3,
                "evidence_count": 4,
                "created_at": inc.get("date_time", now),
                "updated_at": now,
                "notes": [
                    {"author": officers[idx % len(officers)], "text": "Technical CDR tower and financial trail attached to docket.", "timestamp": now}
                ]
            }
            db.add_case_card(card)
            seeded.append(card)
        return seeded

    return cards

@router.post("/move")
async def move_case(body: MoveCaseRequest, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database uninitialized")

    success = db.update_case_status(body.case_id, body.new_status.value)
    if not success:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"status": "ok", "case_id": body.case_id, "new_status": body.new_status.value}

@router.post("/add")
async def add_case(body: CaseCard, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database uninitialized")

    card_data = body.dict()
    db.add_case_card(card_data)
    return card_data

@router.delete("/cards/{case_id}")
async def delete_case(case_id: str, request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database uninitialized")
    success = db.delete_case_card(case_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return {"status": "ok", "deleted_case_id": case_id}

@router.post("/clear")
async def clear_cases(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=500, detail="Database uninitialized")
    db.clear_case_cards()
    return {"status": "ok", "message": "All caseboard dockets cleared"}
