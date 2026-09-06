"""SENTINEL v2.0 — Main FastAPI Application Entry
Mounts all 9 API routers, WebSocket live intel feed, database initialization,
graph store loading, and pre-seeds the 10 automated pattern detection alerts.
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
import time
import asyncio
from datetime import datetime

# Add both backend and project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import Database
from backend.db.graph_store import GraphStore
from backend.security.blockchain_audit import BlockchainAuditTrail
from backend.security.jwt_handler import create_access_token, decode_token
from backend.config import SAMPLE_DIR, DB_PATH, LOAD_SAMPLE_DATA

START_TIME = time.time()

def seed_initial_alerts(db: Database):
    """Pre-seeds the 10 automated pattern detection alerts matching Section 5."""
    existing = db.get_alerts(limit=5)
    if existing:
        return

    now = datetime.now().isoformat()
    demo_alerts = [
        {
            "id": "ALT-001-KINGPIN",
            "alert_type": "SHADOW_KINGPIN",
            "priority": "CRITICAL",
            "title": "Shadow Kingpin Detected: Vikram Sinha",
            "description": "High betweenness centrality (0.3842, >95th percentile) with low direct degree (3 contacts). Subject acts as sole strategic gatekeeper bridging coalfield syndicate to political front.",
            "entity_id": "SUSP-DBA3397F",
            "entity_name": "Vikram Sinha",
            "entity_type": "Person",
            "timestamp": now,
            "metadata": {"betweenness": 0.3842, "degree": 3, "role": "MASTERMIND"},
            "action_url": "/graph?focus=SUSP-DBA3397F",
        },
        {
            "id": "ALT-002-HAWALA",
            "alert_type": "HAWALA_LOOP",
            "priority": "CRITICAL",
            "title": "Hawala Round-Trip Cycle Detected (₹1,98,000 in 48h)",
            "description": "Closed directed money loop detected: Account A ➔ B ➔ C ➔ D ➔ A across Ranchi, Kolkata, and Dhanbad within 48 hours.",
            "entity_id": "TX-HAWALA-1",
            "entity_name": "Coalfield Hawala Cycle",
            "entity_type": "BankAccount",
            "timestamp": now,
            "metadata": {"total_amount": 198000.0, "hops": 4, "time_span_hours": 48},
            "action_url": "/financial",
        },
        {
            "id": "ALT-003-BURNER",
            "alert_type": "BURNER_PHONE_CHAIN",
            "priority": "HIGH",
            "title": "Burner Hardware IMEI Reuse Flagged",
            "description": "IMEI 860492040192834 appeared sequentially with 3 different SIM cards (+91-9876500001, +91-9876500002, +91-9876500003) calling the same contact cluster.",
            "entity_id": "IMEI-860492040192834",
            "entity_name": "Burner Device 01",
            "entity_type": "Phone",
            "timestamp": now,
            "metadata": {"imei": "860492040192834", "sim_count": 3, "contact_overlap": 0.85},
            "action_url": "/cdr",
        },
        {
            "id": "ALT-004-SPIKE",
            "alert_type": "PRE_CRIME_SPIKE",
            "priority": "HIGH",
            "title": "Pre-Crime Communication Surge (500% Spike)",
            "description": "35 rapid calls recorded within 24 hours prior to FIR #2026/115 execution between suspect cell and Bokaro tactical operatives.",
            "entity_id": "INC-115",
            "entity_name": "FIR #2026/115",
            "entity_type": "Incident",
            "timestamp": now,
            "metadata": {"spike_ratio": 5.2, "calls_in_24h": 35, "baseline_daily": 6.7},
            "action_url": "/timeline",
        },
        {
            "id": "ALT-005-SILENCE",
            "alert_type": "POST_CRIME_SILENCE",
            "priority": "HIGH",
            "title": "Post-Crime Radio Silence Alert",
            "description": "Suspect phone +91-9835012345 dropped 100% telecommunication activity immediately following incident occurrence at Bankmore PS.",
            "entity_id": "PHONE_+91-9835012345",
            "entity_name": "+91-9835012345",
            "entity_type": "Phone",
            "timestamp": now,
            "metadata": {"drop_percentage": 100.0, "silent_hours": 72},
            "action_url": "/cdr",
        },
        {
            "id": "ALT-006-STRUCT",
            "alert_type": "FINANCIAL_STRUCTURING",
            "priority": "HIGH",
            "title": "Smurfing / Structuring Limit Evasion",
            "description": "8 transactions executed between ₹48,000 and ₹49,500 to evade mandatory ₹50,000 PAN reporting requirements under Income Tax Act.",
            "entity_id": "ACC-HAWALA-STRUCT",
            "entity_name": "HDFC Structuring Node",
            "entity_type": "BankAccount",
            "timestamp": now,
            "metadata": {"structured_count": 8, "threshold": 50000.0},
            "action_url": "/financial",
        },
        {
            "id": "ALT-007-BORDER",
            "alert_type": "CROSS_STATE_MOVEMENT",
            "priority": "MEDIUM",
            "title": "Cross-State Transit Alert: Jharkhand ➔ Bihar",
            "description": "Suspect tower trajectory crossed state boundary along NH-19 Chauparan checkpoint into Gaya district within 3 hours.",
            "entity_id": "LOC-BORDER-NH19",
            "entity_name": "Chauparan Border Corridor",
            "entity_type": "Location",
            "timestamp": now,
            "metadata": {"from_state": "Jharkhand", "to_state": "Bihar", "route": "NH-19"},
            "action_url": "/map",
        },
        {
            "id": "ALT-008-GANG",
            "alert_type": "NEW_GANG_MEMBER",
            "priority": "MEDIUM",
            "title": "New Operational Contact Joined Syndicate",
            "description": "Previously unflagged mobile +91-9123488888 recorded multiple 200+ second calls with senior gang lieutenant at Jamshedpur.",
            "entity_id": "PHONE_+91-9123488888",
            "entity_name": "+91-9123488888",
            "entity_type": "Phone",
            "timestamp": now,
            "metadata": {"syndicate": "Dhanbad Extortion Syndicate"},
            "action_url": "/graph",
        },
        {
            "id": "ALT-009-COLOC",
            "alert_type": "COLOCATION_EVENT",
            "priority": "MEDIUM",
            "title": "Night Co-Location Detected: Ormanjhi Tower",
            "description": "Suspect A and Suspect C were within 500m at Ormanjhi Tower on NH-33 at 02:30 AM (unusual nocturnal meeting).",
            "entity_id": "TWR-IN-1006",
            "entity_name": "Tower NH33-Ormanjhi",
            "entity_type": "CellTower",
            "timestamp": now,
            "metadata": {"time_diff_min": 12, "distance_m": 120.0},
            "action_url": "/map",
        },
        {
            "id": "ALT-010-INTEG",
            "alert_type": "EVIDENCE_TAMPERING",
            "priority": "CRITICAL",
            "title": "Blockchain Evidence Verification Check: ALL SEALED",
            "description": "Automated SHA-256 blockchain audit completed across 25 FIRs and 500 CDR logs. Hash verification confirmed 100% authentic and tamper-free.",
            "entity_id": "BLOCKCHAIN-ROOT",
            "entity_name": "Evidence Vault Chain",
            "entity_type": "Evidence",
            "timestamp": now,
            "metadata": {"blocks_verified": 26, "tampered": False},
            "action_url": "/evidence",
        },
    ]

    for alt in demo_alerts:
        db.add_alert(alt)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("==================================================")
    print("  SENTINEL v2.0 — AI Criminal Network Analysis   ")
    print("  Initializing Subsystems & Intelligence Graph... ")
    print("==================================================")

    # 1. Initialize SQLite Database
    app.state.db = Database(DB_PATH)

    # 2. Initialize NetworkX GraphStore
    app.state.graph_store = GraphStore()

    # 3. Load synthetic mock intelligence data ONLY if LOAD_SAMPLE_DATA is True
    if LOAD_SAMPLE_DATA and os.path.exists(SAMPLE_DIR):
        print(f"Loading sample intelligence data from {SAMPLE_DIR}...")
        app.state.graph_store.load_from_json(SAMPLE_DIR)
        seed_initial_alerts(app.state.db)
    else:
        print("Clean Slate Mode: Starting with zero dummy graph nodes. Ready for real evidence ingestion.")

    # 4. Initialize Blockchain Audit Trail
    app.state.blockchain = BlockchainAuditTrail()

    # 4.5 Initialize Person Detector
    from backend.pipeline.person_detector import PersonDetector
    app.state.person_detector = PersonDetector()

    # 5. Log startup audit
    app.state.db.log_audit("SYS-01", "SYSTEM", "STARTUP", "SENTINEL Core Engine v2.0 launched", "127.0.0.1")

    curr_nodes = app.state.graph_store.graph.number_of_nodes() if app.state.graph_store.graph else 0
    curr_edges = app.state.graph_store.graph.number_of_edges() if app.state.graph_store.graph else 0
    print(f"SENTINEL v2.0 System Ready: {curr_nodes} Nodes, {curr_edges} Edges.")
    yield

    print("Shutting down SENTINEL system...")

app = FastAPI(
    title='SENTINEL v2.0 API',
    description='AI-Powered Criminal Network Analysis System — Ministry of Home Affairs / NCRB',
    version='2.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all feature routers
from backend.routers import ingest, graph, analysis, geo, chat, export, alerts, evidence, caseboard, faces, persons

app.include_router(ingest.router)
app.include_router(graph.router)
app.include_router(analysis.router)
app.include_router(geo.router)
app.include_router(chat.router)
app.include_router(export.router)
app.include_router(alerts.router)
app.include_router(evidence.router)
app.include_router(caseboard.router)
app.include_router(faces.router)
app.include_router(persons.router)

# Top-level alias endpoints
@app.get("/api/health")
async def health_check():
    nodes = 0
    edges = 0
    if hasattr(app.state, 'graph_store') and app.state.graph_store.graph:
        nodes = app.state.graph_store.graph.number_of_nodes()
        edges = app.state.graph_store.graph.number_of_edges()

    return {
        "status": "ok",
        "nodes": nodes,
        "edges": edges,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "version": "2.0.0"
    }

@app.get("/api/dashboard")
async def top_level_dashboard(request: Request):
    from backend.routers.analysis import get_dashboard_summary
    return await get_dashboard_summary(request)

@app.get("/api/admin/users")
async def get_admin_users(request: Request):
    if hasattr(app.state, 'db'):
        return app.state.db.get_users()
    return []

@app.get("/api/admin/audit")
@app.get("/api/admin/audit-log")
async def get_admin_audit(request: Request):
    if hasattr(app.state, 'db'):
        return app.state.db.get_audit_log(limit=100)
    return []

@app.get("/api/alerts")
async def top_level_alerts(request: Request, limit: int = 100, unacknowledged: bool = False):
    from backend.routers.alerts import get_all_alerts
    return await get_all_alerts(request, limit=limit, unacknowledged=unacknowledged)

@app.get("/api/evidence")
async def top_level_evidence(request: Request):
    from backend.routers.evidence import get_all_evidence
    return await get_all_evidence(request)

@app.post("/api/admin/clear-all-data")
async def clear_all_system_data(request: Request):
    """
    Purges all dummy/sample data across the entire platform:
    - Clears the in-memory NetworkX MultiDiGraph (nodes=0, edges=0)
    - Purges SQLite cases, alerts, and upload records
    - Resets blockchain audit chain to Genesis block
    - Returns system to pristine Clean Slate state ready for real data ingestion.
    """
    nodes_removed = 0
    edges_removed = 0
    if hasattr(app.state, 'graph_store') and app.state.graph_store.graph is not None:
        nodes_removed = app.state.graph_store.graph.number_of_nodes()
        edges_removed = app.state.graph_store.graph.number_of_edges()
        app.state.graph_store.graph.clear()

    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.clear_all_data()
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_DATA", f"Cleared {nodes_removed} nodes and {edges_removed} edges. Clean slate initialized.", "127.0.0.1")

    if hasattr(app.state, 'blockchain') and app.state.blockchain is not None:
        app.state.blockchain = BlockchainAuditTrail()

    return {
        "status": "SUCCESS",
        "nodes": 0,
        "edges": 0,
        "nodes_removed": nodes_removed,
        "edges_removed": edges_removed,
        "message": "All dummy data successfully removed. SENTINEL is now in Clean Slate mode ready for real data ingestion."
    }

@app.post("/api/admin/purge-graph")
async def admin_purge_graph(request: Request):
    """Purges only the Knowledge Graph (nodes & edges) while preserving cases, alerts, and audits."""
    nodes = 0
    edges = 0
    if hasattr(app.state, 'graph_store') and app.state.graph_store.graph is not None:
        nodes = app.state.graph_store.graph.number_of_nodes()
        edges = app.state.graph_store.graph.number_of_edges()
        app.state.graph_store.graph.clear()
        app.state.graph_store.version += 1
    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_GRAPH", f"Purged {nodes} nodes and {edges} edges from graph store.", "127.0.0.1")
    return {"status": "SUCCESS", "nodes_removed": nodes, "edges_removed": edges, "message": f"Graph purged: {nodes} nodes, {edges} edges removed."}

@app.post("/api/admin/purge-cases")
async def admin_purge_cases(request: Request):
    """Purges all Case Board dockets and investigation cards."""
    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.clear_case_cards()
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_CASES", "Purged all caseboard investigation dockets.", "127.0.0.1")
    return {"status": "SUCCESS", "message": "All Case Board dockets purged."}

@app.post("/api/admin/purge-evidence")
async def admin_purge_evidence(request: Request):
    """Resets Evidence Vault and blockchain chain to Genesis block."""
    from backend.pipeline.blockchain import BlockchainAuditTrail
    app.state.blockchain = BlockchainAuditTrail()
    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_EVIDENCE", "Reset evidence vault and blockchain ledger to Genesis block.", "127.0.0.1")
    return {"status": "SUCCESS", "message": "Evidence Vault reset to Genesis block."}

@app.post("/api/admin/purge-alerts")
async def admin_purge_alerts(request: Request):
    """Purges all automated alert notifications and pattern detection records."""
    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.clear_alerts()
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_ALERTS", "Cleared all automated threat detection alerts.", "127.0.0.1")
    return {"status": "SUCCESS", "message": "All automated alerts cleared."}

@app.post("/api/admin/purge-uploads")
async def admin_purge_uploads(request: Request):
    """Purges all uploaded files history and cached extractions."""
    if hasattr(app.state, 'db') and app.state.db is not None:
        app.state.db.clear_uploads()
        app.state.db.log_audit("ADMIN-01", "ADMIN", "PURGE_UPLOADS", "Purged upload records and extraction history.", "127.0.0.1")
    return {"status": "SUCCESS", "message": "All ingestion uploads history purged."}

@app.post("/api/admin/load-sample-data")
async def load_sample_demo_data(request: Request):
    """Loads or restores the standard 372-node synthetic criminal intelligence demo graph."""
    if hasattr(app.state, 'graph_store') and os.path.exists(SAMPLE_DIR):
        app.state.graph_store.load_from_json(SAMPLE_DIR)
        if hasattr(app.state, 'db'):
            seed_initial_alerts(app.state.db)
        return {
            "status": "SUCCESS",
            "nodes": app.state.graph_store.graph.number_of_nodes(),
            "edges": app.state.graph_store.graph.number_of_edges(),
            "message": "Sample intelligence data successfully loaded."
        }
    raise HTTPException(status_code=500, detail="Sample directory not found.")

@app.get("/api/admin/health")
async def get_admin_health(request: Request):
    db_size = 0
    if os.path.exists(DB_PATH):
        db_size = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
    nodes = app.state.graph_store.graph.number_of_nodes() if hasattr(app.state, 'graph_store') else 0
    edges = app.state.graph_store.graph.number_of_edges() if hasattr(app.state, 'graph_store') else 0
    blockchain_valid = True
    if hasattr(app.state, 'blockchain'):
        v_res = app.state.blockchain.verify_chain()
        blockchain_valid = v_res.get("integrity_valid", True) if isinstance(v_res, dict) else bool(v_res)

    return {
        "status": "HEALTHY",
        "database_size_mb": db_size,
        "graph_nodes": nodes,
        "graph_edges": edges,
        "blockchain_integrity": blockchain_valid,
        "uptime_seconds": round(time.time() - START_TIME, 1)
    }

# Real-Time WebSocket Intel Feed
@app.websocket("/ws/intel-feed")
async def websocket_intel_feed(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Emit live telemetry heartbeat / intel push every 5 seconds
            await asyncio.sleep(5)
            await websocket.send_json({
                "type": "INTEL_BEACON",
                "timestamp": datetime.now().isoformat(),
                "active_surveillance_towers": 30,
                "monitored_phones": 80,
                "status": "ONLINE"
            })
    except WebSocketDisconnect:
        pass