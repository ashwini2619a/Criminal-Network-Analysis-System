# SENTINEL v2.0 — AI-Powered Criminal Network Analysis System

[![System Status](https://img.shields.io/badge/System-Operational-emerald)](#)
[![Problem Statement](https://img.shields.io/badge/PS_ID-26189-cyan)](#)
[![Organization](https://img.shields.io/badge/Organization-Ministry_of_Home_Affairs-blue)](#)
[![Department](https://img.shields.io/badge/Department-NCRB_(Women_Safety_Division)-purple)](#)
[![Theme](https://img.shields.io/badge/Theme-Blockchain_&_Cybersecurity-orange)](#)
[![Statutory Standard](https://img.shields.io/badge/Statutory-Sec_63_BSA_/_65B_IEA-red)](#)

---

## Official Mandate & Problem Statement Specifications

| Parameter | Official Specification |
| :--- | :--- |
| **Problem Statement ID** | **`26189`** |
| **Problem Statement Title** | **AI-Powered Criminal Network Analysis System** |
| **Organization** | **Ministry of Home Affairs (MHA)** |
| **Department** | **National Crime Records Bureau (NCRB), Women Safety Division** |
| **Category** | **Software** |
| **Theme** | **Blockchain & Cybersecurity** |

### Background & Objective
Modern criminal activities operate through complex networks involving associates, intermediaries, financial channels, communication links, locations, and events. Law enforcement agencies collect large volumes of data from multiple sources:
1. **FIRs and Police Reports** (Unstructured legal and narrative text)
2. **Call Detail Records (CDRs)** (Telecom towers, IMEI, IMSI, call durations)
3. **Financial Transaction Records** (Bank transfers, UPI, RTGS, Hawala channels)
4. **Surveillance Reports** (CCTV feeds, video analytics, tripwires)
5. **Social Media Intelligence (OSINT)** (Usernames, handles, Telegram channels, Darknet wallets)
6. **Criminal History Databases** (CCTNS prior convictions, chargesheets, active warrants)
7. **Intelligence Agency Reports** (Multi-jurisdictional agency briefs)

**SENTINEL v2.0** solves the critical challenge of fragmented and unstructured data by providing an end-to-end AI/ML, NLP, and Graph Analytics platform with **Blockchain digital evidence sealing** and real-time **Women Safety edge video analytics**.

---

## Key Subsystems & Capabilities

### 1. Multi-Modal Intelligence Graph
- **Graph Engine**: NetworkX `MultiDiGraph` maintaining 372 nodes and 869 edges across 9 entity types (`Person`, `Phone`, `BankAccount`, `Location`, `Vehicle`, `Organization`, `Incident`, `Evidence`, `Weapon`).
- **Graph Caching**: In-memory thread-safe versioned caching layer providing sub-millisecond query latency for dashboard and network exploration.
- **Dynamic 1-Click Expansion**: Expand suspects to reveal 2-hop associates, burner phones, shell companies, and vehicle ownership.

### 2. Advanced Network Centrality & Kingpin Discovery
- **5 Centrality Algorithms**:
  - *Degree Centrality*: Quantifies direct operational reach.
  - *Betweenness Centrality*: Uncovers communication bottlenecks and clandestine brokers.
  - *Closeness Centrality*: Measures speed of coordination.
  - *PageRank*: Measures algorithmic authority in the syndicate.
  - *Eigenvector Centrality*: Gauges connectivity to high-influence kingpins.
- **Shadow Kingpin Detection**: Flags covert syndicate bosses maintaining low direct degree but dominant betweenness across partitioned sub-networks.

### 3. Hawala & Anti-Money Laundering (AML) Detection
- **Cyclic Money Loops**: Traverses directed financial transaction graphs to detect closed laundering loops ($A \to B \to C \to D \to A$) within tight timeframes ($\le 72\text{ hours}$).
- **Structuring / Smurfing**: Flags rapid sub-₹50,000 banking transfers designed to evade statutory FIU-IND reporting thresholds.
- **Fan-In / Fan-Out**: Identifies funnel accounts and distributor nodes.

### 4. Telecom Forensics & Burner Phone Triangulation
- **IMEI Reuse Detection**: Surfaces burner handsets swapped across multiple SIM cards.
- **SIM Swap Chains**: Detects silent drops followed by immediate co-located activations contacting identical suspect clusters ($\ge 60\%$ overlap).
- **Nocturnal Co-location**: Correlates cell tower CDR records to identify clandestine meetings within $< 500\text{m}$.

### 5. Women Safety Edge AI Video Tracker (`/tracker`)
- **Exclusive Human Gender Tracking**: Exclusively tracks `FEMALE` and `MALE` subjects across transit corridors, dark underpasses, and bus shelters, eliminating non-human clutter.
- **4 Autonomous Behavior Heuristics**:
  1. *Stalking / Shadowing Trajectory Lock*: Flags male subjects following female subjects within $< 3.8\text{m}$ with matching directional velocity vectors.
  2. *Lone Woman Vulnerability Alert*: Flags unaccompanied female subjects in deserted or nocturnal transit zones.
  3. *Group Surrounding / Cornering*: Detects $\ge 2$ male subjects converging upon a female subject's path within $< 2.9\text{m}$.
  4. *Distress Evasion / Flight*: Identifies sudden evasion surges ($> 2.2\times$) by female subjects avoiding approaching suspects.
- **1-Click Dial 112 PCR Dispatch**: Instant PCR van dispatch (`POST /api/tracker/dispatch-pcr`) generating official NCRB dockets and assigning rapid intercept units (e.g. `CHETAK-09`, ETA 3.5 min).

### 6. Statutory Chain of Custody & Evidence Vault
- **Section 63 BSA / 65B IEA Compliance**: Cryptographic SHA-256 blockchain hash chain sealing every uploaded evidence file, OCR extraction, and video frame.
- **Tamper Simulation & Self-Healing**: Real-time cryptographic ledger audit detects byte alterations and provides certified restoration.

### 7. Collaborative Case Board & Alert Center
- **Kanban Investigation Workflow**: Multi-officer case dockets (`NEW`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`) linked directly to graph entities.
- **Automated Alert Triage**: Automated monitors alert on Kingpins, Hawala transactions, Burner Swaps, and Women Safety triggers.

### 8. Court-Certified Dossier & Report Generator
- **ReportLab PDF Engine**: Generates court-admissible forensic dossiers complete with suspect mugshots, centrality matrices, associate graphs, and verification QR codes.

---

## Quick Start (Single-Click Windows Launch)

Launch both backend and frontend systems with one command:

```cmd
run.bat
```

The script automatically verifies your environment, starts the FastAPI server (`http://127.0.0.1:8000`), starts the Vite frontend (`http://localhost:5173`), and launches your default web browser.

---

## Manual Installation & Execution

### Prerequisites
- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Node.js**: 18.0+ / npm 9.0+

### 1. Backend Setup
```cmd
cd sentinel\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend OpenAPI documentation will be available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```cmd
cd sentinel\frontend
npm install
npm run dev
```
The frontend console will be available at: `http://localhost:5173`

---

## Default Tactical Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `sentinel2024` | Full access, system audit, blockchain verification |
| **Investigator** | `investigator` | `investigator2026` | Caseboard editing, PCR dispatch, suspect profiling |
| **Analyst** | `analyst` | `analyst2026` | Intelligence graph, CDR maps, financial flow analysis |

---

## Automated Verification Suite

Run the full end-to-end 20-test verification suite to validate all subsystems:

```cmd
cd sentinel
backend\.venv\Scripts\python.exe backend\verify_suite.py
```

### Verified Test Matrix
- **Test 1**: System Health & Graph Integrity (`372 Nodes, 869 Edges`)
- **Test 2**: Evidence Ingestion History & File Ledger
- **Test 3**: 1-Click Graph Expansion (`Vikram Sinha` Syndicate)
- **Test 4**: Telecom Cell Towers (`30 Towers Geocoded`)
- **Test 5**: CDR Movement Trail Reconstruction
- **Test 6**: Nocturnal Co-Location Events ($<500\text{m}$)
- **Test 7**: Hawala AML Cyclic Loop Detection
- **Test 8**: Burner Phone Triangulation & IMEI Re-use
- **Test 9**: Chronological Event Temporal Timeline
- **Test 10**: AI Natural Language Graph Queries
- **Test 11**: Automated Detection Alert Center
- **Test 12**: Collaborative Case Board Kanban
- **Test 13**: Evidence Vault Blockchain Integrity
- **Test 14**: Daily Intelligence Digest Report Compilation
- **Test 15**: Unstructured FIR Text Entity Extraction (NER)
- **Test 16**: CCTNS Conviction History & Warrant Lookup
- **Test 17**: Court-Certified PDF Dossier Generation
- **Test 18**: Blockchain Tamper Simulation & Proof of Ledger
- **Test 19**: Alert Escalation Lifecycle to FIR Docket
- **Test 20**: Women Safety Edge AI Tracker (Gender AI, 4 Behavior Heuristics, PCR Dispatch)

---

## Architecture & Data Flow

```mermaid
graph TD
    subgraph Data Layer
        DB[(SQLite Persistent Store\nIndexed Audit, Evidence & Cases)]
        STORE[GraphStore: NetworkX MultiDiGraph\n372 Nodes, 869 Edges]
        LEDGER[BlockchainAuditTrail\nSHA-256 Hash Chain]
    end

    subgraph Analytics & AI Core
        CENT[Centrality & Shadow Kingpins]
        HAWALA[Hawala Cycle & Structuring]
        BURNER[Burner Triangulation]
        TRACKER[Women Safety Edge AI\nGender Classification & Stalking Heuristics]
    end

    subgraph API Subsystem (FastAPI)
        R_GRAPH[/api/graph]
        R_ANALYSIS[/api/analysis - Cached]
        R_INGEST[/api/ingest - Magic Byte Validated]
        R_TRACKER[/api/tracker - Live Streams & Dial 112]
        R_EXPORT[/api/export - Court PDF]
    end

    subgraph Frontend Subsystem (React 19 + Vite)
        UI_DASH[Tactical Dashboard]
        UI_TRACK[Women Safety Tracker]
        UI_GRAPH[Graph Explorer]
        UI_MAP[Geo-Intel Map]
        UI_FIN[Financial Flow]
        UI_CASE[Kanban Case Board]
        BOUNDARY[React Error Boundary]
    end

    STORE & DB & LEDGER --> API Subsystem
    API Subsystem --> BOUNDARY --> Frontend Subsystem
```

---

## Statutory Legal Standards
- **Section 63 of Bharatiya Sakshya Adhiniyam (BSA), 2023** (formerly Section 65B of Indian Evidence Act, 1872):
  All digital evidence items, video keyframes, and CDR records processed through SENTINEL generate an immutable SHA-256 cryptographic certificate verifying electronic custody from point of origin to court presentation.

---
**Directorate of Intelligence & Women Safety Operations Center**  
*SENTINEL Tactical Systems v2.0*
