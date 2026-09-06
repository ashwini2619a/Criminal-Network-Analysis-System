# SENTINEL — Setup & Architecture Guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SENTINEL — AI-Powered Criminal Network Analysis System
  For: Ministry of Home Affairs / NCRB / Women Safety Division
  Theme: Blockchain & Cybersecurity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Prerequisites
- **Node.js**: v20+ or v24+ (https://nodejs.org)
- **Python**: v3.11+ (https://python.org)
- **Package Manager**: npm / uv
- **Tesseract OCR** (Optional, for scanned physical FIRs)
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki

---

## Quick Start

### 1. Generate Synthetic Intelligence Data
```bash
cd sentinel/data
python generate_mock_data.py
```
This generates realistic Indian law enforcement demo data with:
- **50 Suspects** with Hindi/English names, criminal history, and risk scores
- **192 CDRs** with cell tower coordinates (Delhi, Mumbai, Patna, Ranchi, etc.)
- **100 Financial Transactions** (NEFT, RTGS, UPI) with UTRs
- **15 FIR Text Documents** with embedded IPC sections and entities
- **30 Locations**, **10 Vehicles**, **5 Gangs/Organizations**, **201 Relationships**
- **Planted Patterns**: 1 Hawala loop, 2 burner phone chains, and 1 shadow kingpin (*Deepak Tiwari*)

### 2. Set Up Backend (Python 3.11 + FastAPI + NetworkX)
```bash
cd sentinel/backend
uv venv .venv --python 3.11
# Or: python -m venv .venv

# Activate venv:
# Windows PowerShell:
.venv\Scripts\activate

# Install requirements:
uv pip install -r requirements.txt
```

### 3. Set Up Frontend (React 19 + Vite + TypeScript + Tailwind)
```bash
cd sentinel/frontend
npm install --legacy-peer-deps
npm run build
```

### 4. Run Development Servers
```bash
# Terminal 1 — Backend API:
cd sentinel/backend
.venv\Scripts\uvicorn.exe main:app --reload --port 8000

# Terminal 2 — Frontend UI:
cd sentinel/frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

### 5. Launch Electron Desktop Shell
```bash
cd sentinel
npm start
# Or: npm run dev:electron
```

---

## Complete Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| **Desktop Shell** | Electron 33+ | Native Windows desktop app with IPC bridges and PDF printing |
| **Frontend UI** | React 19 + Vite + TypeScript | High-performance reactive UI with strict typing |
| **Styling** | Tailwind CSS + Dark Tactical Theme | Slate-950 background with Cyan (#06b6d4) and Red (#ef4444) accents |
| **Graph Visualization** | Cytoscape.js | Force-directed graph canvas, zoom/pan, neighborhood expansion |
| **Geospatial Mapping** | Leaflet.js + OpenStreetMap | CDR tower clustering, heatmaps, suspect movement trails |
| **Data Analytics** | Recharts | KPI dashboards, financial flow charts, hourly call timelines |
| **Backend Engine** | Python FastAPI (async) | REST endpoints for ingestion, graph queries, and ML compute |
| **Graph Database** | NetworkX MultiDiGraph | In-memory relationship storage with sub-millisecond traversal |
| **Persistence** | SQLite | Case management, upload registry, and audit logging |
| **NLP Engine** | Custom Indian Law NER | Regex + Lexicons for Phone, Aadhaar, Vehicle, IPC sections |
| **Blockchain Audit** | SHA-256 Hash Chain | Immutable evidence integrity log with cryptographic seals |
| **Authentication** | JWT + RBAC | Role-Based Access Control (Admin, Investigator, Analyst) |

---

## 9 Core Tactical Screens

1. **Tactical Dashboard (`/`)**:
   - High-level KPI cards (Total Cases, Total Suspects, Active Networks, High-Risk Alerts)
   - Top 5 Kingpins leaderboard with composite risk progress bars
   - Threat level distribution pie chart & cases-over-time area chart
   - Network density radial telemetry and recent activity feed

2. **Data Ingestion Center (`/ingest`)**:
   - Drag-and-drop file upload zone (PDF, CSV, XLSX, TXT, Images)
   - Automatic SHA-256 hash sealing into the blockchain audit trail
   - OCR & custom Indian NER extraction pipeline
   - Live entity preview table before committing to the intelligence graph

3. **Interactive Graph Explorer (`/graph`)**:
   - Full-screen Cytoscape.js interactive canvas
   - Shape-coded nodes: Circle=Person, Diamond=Phone, Square=Account, Triangle=Location, Hexagon=Organization
   - Color-coded edges: Red=Criminal, Blue=Financial, Green=Communication, Gray=Inferred
   - Filters sidebar: Entity types, risk threshold slider, date range
   - 2-hop neighborhood expansion, shortest path highlighting, and community overlays

4. **Suspect Profile Dossier (`/suspect/:id`)**:
   - Full identity profile: name, aliases, criminal record number, age, gender
   - Animated risk score gauge (0-100) and 5-metric centrality rankings
   - Connected entities tabs: Phones, Accounts, Vehicles, Associates, Gangs
   - Mini ego-graph and chronological activity timeline
   - Linked FIR references with legal citations

5. **CDR Analysis & Geo-Intelligence Map (`/map`)**:
   - Interactive Leaflet map with dark cartographic basemap
   - Cell tower markers with call frequency popups
   - Crime scene locations and suspect movement polylines
   - Temporal-spatial co-location detection alerts

6. **Financial Flow Analyzer (`/financial`)**:
   - High-risk fund transfer visualizer showing inter-account flows
   - Transaction volume timeline with anomaly amount spikes
   - Cyclic Hawala loop detector panel ($A \to B \to C \to D \to A$)
   - Structuring / smurfing alerts (transactions just below ₹50,000 threshold)

7. **AI Investigation Assistant (`/chat`)**:
   - Conversational AI interface for natural language queries
   - Queries translated directly into NetworkX graph algorithms
   - Instant subgraph highlighting for target entities and shortest paths
   - Sample prompt chips for quick investigative discovery

8. **Dossier Generator & Evidence Vault (`/dossier`)**:
   - One-click court-admissible PDF dossier generation via ReportLab
   - Evidence file vault with SHA-256 integrity verification
   - QR code generation linking to the cryptographic blockchain block
   - Export options: PDF, JSON, XLSX

9. **Admin & Audit Panel (`/admin`)**:
   - User account management with RBAC roles (Admin, Investigator, Analyst)
   - Immutable audit trail log recording all user access, uploads, and queries
   - One-click blockchain integrity verification (flags tampering)
   - Real-time system telemetry: database size, graph nodes/edges, API latency

---

## AI / ML Algorithms

- **Algorithm 1: Kingpin Discovery (Centrality Analysis)**:
  $$\text{Composite Risk} = 0.15 \cdot \text{Degree} + 0.30 \cdot \text{Betweenness} + 0.15 \cdot \text{Closeness} + 0.25 \cdot \text{PageRank} + 0.15 \cdot \text{Eigenvector}$$
  Identifies *Shadow Kingpins* with betweenness $\ge 80$th percentile and direct degree $\le 30$th percentile.

- **Algorithm 2: Community / Gang Detection**:
  Louvain modularity optimization clusters the graph into discrete factions, gangs, and syndicates. Flags bridge nodes operating across multiple groups as potential informants or dual agents.

- **Algorithm 3: Hawala / Money Laundering Detector**:
  Identifies closed directed cycles in financial transfers within 72-hour windows, flags fan-in/fan-out structuring, and calculates a composite Money Laundering Risk Index.

- **Algorithm 4: Burner Phone Triangulation**:
  Detects IMEI reuse across multiple SIM cards, flags sequential SIM swap chains with $\ge 40\%$ contact overlap, and highlights spatial-temporal co-locations within 45-minute windows.

- **Algorithm 5: Temporal Pattern Analysis**:
  Builds unified event timelines, detects pre-crime communication surges (24-48 hours before an incident), and flags post-incident radio silence.

- **Algorithm 6: Indian Law Enforcement NER**:
  Custom regex and dictionary extraction for Indian phone numbers (`+91`), Aadhaar numbers, vehicle registrations (`JH-01-AB-1234`), IPC sections (`u/s 302, 120B, 420`), and Indian names.
