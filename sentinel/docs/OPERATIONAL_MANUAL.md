# SENTINEL v2.0 — OPERATIONAL LAW ENFORCEMENT MANUAL
**For: Ministry of Home Affairs / National Crime Records Bureau / Women Safety Division**  
**Theme: Blockchain & Cybersecurity**  
**Classification: CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE**  

---

## 1. System Vision & Objective

The primary objective of **SENTINEL v2.0** is to transform disparate, unstructured, multi-agency criminal intelligence into actionable, court-admissible visual knowledge graphs.

### The 3 Core Tenets
1. **ZERO Manual Data Entry**: Ingest raw PDFs, scanned FIRs (OCR), Excel/CSV CDR logs, bank statements, and wiretap transcripts with automatic entity extraction and Jaro-Winkler entity resolution.
2. **ZERO Missed Connections**: Graph centrality algorithms uncover non-obvious "Shadow Kingpins" who shield themselves behind intermediaries, layered Hawala money transfers, and burner hardware swapping.
3. **100% Cryptographic Audit Trail**: Every ingestion, inspection, graph query, and dossier generation is cryptographically sealed in an immutable SHA-256 blockchain ledger satisfying Indian Evidence Act Section 65B requirements.

---

## 2. The 10 Workload-Reduction Auto-Features

### Auto-Feature 1: Smart Ingestion & Schema Auto-Mapping
- Drops any digital PDF, scanned image, or raw CSV.
- Automatically recognizes headers across Indian telecom operators (Airtel, Jio, Vi, BSNL) and major banks (SBI, PNB, HDFC, ICICI).
- Extracts entities (Phones, Aadhaar hashes, Vehicle registrations, IPC sections, Bank accounts).

### Auto-Feature 2: Cross-Case Intelligence Linker
- Ingested entities are scanned in real-time against all historical FIRs in the database.
- Matches across phone numbers, vehicle registrations, and fuzzy suspect names (>88% Jaro-Winkler similarity).
- Flags co-accused appearances across different police stations and districts.

### Auto-Feature 3: 1-Click Network Expansion
- Double-clicking any suspect node on the Cytoscape graph canvas triggers a 2-hop radius discovery traversal, expanding associates, burner SIMs, and front companies in real-time.

### Auto-Feature 4: Continuous Pattern Detection Alerts
- 10 rule engines monitor graph topology, financial flow, and telecom logs:
  1. *Shadow Kingpin Discovery* (High betweenness >95th percentile, Low direct degree $\le 4$)
  2. *Hawala AML Round-Trip Cycles* ($A \to B \to C \to D \to A$ within 72h)
  3. *Burner Hardware Reuse* (Same IMEI across $\ge 2$ SIM cards)
  4. *Pre-Crime Communication Surge* (>2x baseline within 24h prior to incident)
  5. *Post-Crime Radio Silence* (>80% traffic cessation across all target numbers)
  6. *Nocturnal Safehouse Co-location* (2+ targets at same tower $<500$m within 45 min)
  7. *Structuring / Smurfing Flags* (Repeated transactions in ₹45,000 – ₹49,999 range)
  8. *Rapid Fan-In / Fan-Out Money Mule Nodes*
  9. *Sequential SIM Swapping Chains*
  10. *High-Centrality Recidivism Risk*

### Auto-Feature 5: Natural Language Intelligence Assistant
- Translates plain Hindi/English investigation questions into Cypher/NetworkX traversals:
  - *"Who is the leader of the Dhanbad extortion gang?"*
  - *"Show money trail from Account X to Account Y"*
  - *"Find all suspects who were in Ranchi on 15th January"*
  - *"Which cases are connected to phone +91-9876500001?"*

### Auto-Feature 6: Multi-Source Chronological Timeline
- Merges calls, bank transfers, tower pings, and FIR registrations into a single time-series stream.
- Flags pre-crime coordination spikes and post-crime silence windows.

### Auto-Feature 7: Court-Ready PDF Dossier Generator
- 1-Click PDF export containing suspect photo placeholder, biographical summary, 5-metric mathematical centrality table, asset associations, and a cryptographic QR code verifying the SHA-256 blockchain integrity block.

### Auto-Feature 8: Predictive Crime Hotspot & Recidivism Engine
- Machine learning risk score combining degree, betweenness, PageRank, past convictions, and syndicate hierarchy level into a 0-100 index.
- Geospatial kernel density heatmap predicting high-probability future rendezvous points.

### Auto-Feature 9: Collaborative Multi-Officer Case Board (Kanban)
- 4 pipeline stages: `Ingested & Registered` $\to$ `Under Graph Analysis` $\to$ `Actionable Leads` $\to$ `Chargesheet Ready`.
- Real-time card status updates, officer assignments, and shared investigator notes.

### Auto-Feature 10: Automated Intelligence Reporting Suite
- Daily Digest: Executive overview of new active threats and recommended actions.
- Weekly Intelligence Brief: Strategic trends and target rankings.
- Monthly Statistics: Disruption analytics, clearance rates, and funds frozen.
- 1-Click Excel/CSV exports for suspects, financial transactions, and CDR logs.

---

## 3. The 6 Planted Criminal Patterns & How to Demonstrate Them

### Pattern 1: The Shadow Kingpin (*Vikram Sinha*)
- **Screen**: `/suspect` and `/alerts`
- **What it shows**: Vikram Sinha maintains very few direct telephone connections (degree = 3), yet holds the highest betweenness centrality score in the entire criminal network (0.3842). He acts as the sole bottleneck bridging the tactical extortion cell in Dhanbad with the high-level Hawala laundering front in Kolkata.

### Pattern 2: Hawala Round-Trip Laundering Loop
- **Screen**: `/financial` and `/alerts`
- **What it shows**: Circular directed graph transaction cycle:
  $$\text{Vikram Sinha} \xrightarrow{₹49,500} \text{Anita Devi} \xrightarrow{₹49,500} \text{Ramesh Yadav} \xrightarrow{₹49,500} \text{Deepak Tiwari} \xrightarrow{₹49,500} \text{Vikram Sinha}$$
  All 4 transactions executed in 27 hours under the ₹50,000 PAN reporting threshold (Section 139A Income Tax Act).

### Pattern 3: Burner Hardware Triangulation (IMEI Reuse)
- **Screen**: `/cdr` and `/alerts`
- **What it shows**: Single physical hardware transceiver (IMEI `860492040192834`) utilized sequentially with 3 different SIM cards (`+91-9876500001`, `+91-9876500002`, `+91-9876500003`) while maintaining an 85% contact overlap.

### Pattern 4: Pre-Crime Surge & Post-Crime Silence
- **Screen**: `/timeline` and `/alerts`
- **What it shows**: Prior to FIR #2026/115, call volume spiked by 500% (35 calls in 24 hours vs. 6.7 baseline) between Vikram Sinha and operative Sunil @ Bullet. Immediately after the crime was committed, all communication ceased completely for 72 hours.

### Pattern 5: Cross-State Organized Syndicate
- **Screen**: `/graph` and `/map`
- **What it shows**: Network clusters spanning Jharkhand (Ranchi, Dhanbad, Bokaro), Bihar (Patna, Gaya), and West Bengal (Kolkata), operating under front organizations including "Eastern Regional Women Safety & Trafficking Ring" and "Dhanbad Coalfield Syndicate".

### Pattern 6: Nocturnal Co-Location Rendezvous
- **Screen**: `/map` (Layer 7)
- **What it shows**: GPS/Tower proximity algorithm detects suspect Vikram Sinha and associate Ramesh Yadav appearing simultaneously at Ormanjhi Tower corridor between 02:15 AM and 03:00 AM with spatial separation under 350 meters.

---

## 4. 1-Click Startup Instructions

### Method A: Windows Desktop 1-Click Launcher
Double-click `sentinel/start_sentinel.bat` or run in PowerShell:
```powershell
.\start_sentinel.ps1
```
This automatically boots the FastAPI core on port 8000, boots the React UI on port 5173, and launches the dashboard in your default browser.

### Method B: Manual Command Line
```powershell
# Terminal 1: Backend
cd sentinel\backend
$env:PYTHONIOENCODING="utf-8"
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd sentinel\frontend
npm run dev
```

### Method C: Automated Live Terminal Demonstration
```powershell
cd sentinel
$env:PYTHONIOENCODING="utf-8"
backend\.venv\Scripts\python.exe demo_sentinel.py
```
