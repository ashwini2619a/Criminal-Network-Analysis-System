# IBVAP — Intelligent Border Video Analytics Platform

> **Problem Statement 26187** · Sashastra Seema Bal (SSB), Ministry of Home Affairs  
> *All-in-One Software-Defined Edge AI Surveillance Engine & Real-Time Alert C2 Server*

---

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8%2BByteTrack-FF6F00.svg)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV%20%2B%20CLAHE-5C3EE8.svg)](https://opencv.org/)
[![Chain of Custody](https://img.shields.io/badge/Security-SHA--256%20Chain%20of%20Custody-green.svg)](https://www.sqlite.org/)

---

## 📌 Executive Summary

**IBVAP** is an enterprise-grade, software-defined edge AI surveillance platform designed for remote border outposts (BOPs). It ingests standard RTSP / ONVIF camera streams or USB webcam inputs, executes real-time computer vision heuristics and deep neural inference at the edge, anchors evidence using SHA-256 cryptographic hashes, and streams real-time tactical alerts to a command-and-control (C2) dashboard.

---

## 🎯 Key Features & Capabilities

### 1. 🎥 RTSP & Webcam Video Ingestion
- Auto-reconnecting frame grabber with exponential backoff.
- Native support for standard RTSP camera feeds, local video files, and USB webcams (`cv2.CAP_DSHOW` enabled for Windows low-latency capture).
- Graceful synthetic frame fallback when cameras are disconnected.

### 2. 🌙 Adaptive Night-Vision Enhancement
- Automatic luminance check in LAB color space (`LOW_LIGHT_THRESHOLD = 60`).
- Adaptive **CLAHE (Contrast Limited Adaptive Histogram Equalization)** on the L-channel to preserve color perception without over-amplifying low-light sensor noise.

### 3. 🎯 Multi-Object Detection & ByteTrack
- YOLOv8 + ByteTrack persistent target tracking across frame occlusions.
- Detects and classifies **Humans**, **Vehicles (Cars, Trucks, Motorcycles, Buses)**, and suspicious targets.

### 4. ⚡ Directional Virtual Tripwire & Polygon Geofencing
- **Virtual Tripwire**: Vector cross-product math calculates exact line-segment intersection and direction of travel (A→B vs B→A).
- **Geofence Polygons**: **Inclusion Zones** (triggers instant intrusion alert) and **Exclusion Zones** (suppresses benign activity inside authorized bounds).

### 5. 🐍 Behavior Heuristics
- **Crawling / Crouching Detection**: Monitors bounding box aspect ratio ($W / H > 1.35$) over consecutive frames to detect covert border movement.
- **Loitering Detection**: Tracks stationary target spatial radius ($\le 100\text{px}$) over configurable time windows ($> 45\text{s}$).

### 6. 👤 Facial Recognition System (FRS)
- Integrated **SCRFD** face detection + **ArcFace 512-D** feature embeddings + **FAISS** vector search.
- Instant match against known watchlist with vector distance thresholds ($0.68$).

### 7. 🚗 Automatic Number Plate Recognition (ANPR)
- High-resolution license plate extraction powered by **PaddleOCR**.
- **Indian RTO Regex Validation**: Matches official formats (`MH12AB1234`, `DL01C5678`, etc.).

### 8. 🔒 Zero-Trust Blockchain Chain-of-Custody
- Cryptographic hash formula:  
  $$\text{SHA-256}(\text{JPEG Keyframe} \mathbin{\Vert} \text{CameraID} \mathbin{\Vert} \text{Timestamp} \mathbin{\Vert} \text{BopID} \mathbin{\Vert} \text{AlertType})$$
- Immutable SQLite store-and-forward queue with online verification API (`POST /api/v1/verify`).
- Hyperledger Fabric Go chaincode included for enterprise ledger integration (`blockchain/chaincode.go`).

---

## 🏗️ System Architecture

```mermaid
graph TD
    CAM[RTSP Stream / USB Webcam / Video File] --> INGEST[Video Ingestion Worker]
    INGEST --> CLAHE[Night Vision: CLAHE in LAB Space]
    CLAHE --> DETECT[YOLOv8 + ByteTrack Multi-Object Tracking]
    
    subgraph Edge Heuristics & Analytics
        DETECT --> TRIP[Directional Virtual Tripwire]
        DETECT --> GEO[Polygon Inclusion / Exclusion Geofence]
        DETECT --> CRAWL[Crawling / Aspect-Ratio Analysis]
        DETECT --> LOITER[Loitering Timeout Monitor]
        DETECT --> FRS[SCRFD + ArcFace 512D FRS]
        DETECT --> ANPR[PaddleOCR + Indian RTO Regex ANPR]
    end

    TRIP & GEO & CRAWL & LOITER & FRS & ANPR --> AUDIT[SHA-256 Chain of Custody + SQLite Queue]
    AUDIT --> WS[FastAPI C2 Server]
    WS --> UI[Tactical HTML / React Command Dashboard]
```

---

## 📂 Repository Structure

```
ibvap/
├── main.py                    # Consolidated single-file engine & FastAPI C2 server
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Containerized production stack
├── .gitignore                 # Excludes weights (*.pt), DBs (*.db), node_modules
├── edge_engine/               # Modular Python edge analytics package
│   ├── config.py              # Configuration schemas & environment variables
│   ├── enhancement.py         # CLAHE night-vision pipeline
│   ├── detector.py            # YOLOv8 + ByteTrack object detector
│   ├── geometry.py            # Vector cross-product tripwire & Shapely geofencing
│   ├── behavior.py            # Crawling & loitering heuristic engines
│   ├── frs.py                 # Facial Recognition System (SCRFD + ArcFace)
│   ├── anpr.py                # License plate recognition & RTO regex validator
│   └── security.py            # SHA-256 evidence hashing & SQLite store-and-forward
├── backend/                   # FastAPI REST API & WebSocket handlers
│   ├── server.py              # Application router & WebSocket stream managers
│   └── database.py            # Audit log database manager
├── blockchain/                # Zero-Trust Evidence Ledger
│   └── chaincode.go           # Hyperledger Fabric Go chaincode
└── frontend/                  # Standalone React C2 Dashboard
    ├── src/                   # React components (VideoFeed, Alerts, MapView)
    └── package.json           # Frontend dependencies
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.14
- **OpenCV & PyTorch**: Automatically installed via requirements

### 2. Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/vishnukant74248/IBVAP.git
cd IBVAP
pip install -r requirements.txt
```

### 3. Running the Server

#### 🔹 Default Mode (Synthetic Border Test Feed):
```bash
python main.py
```

#### 🔹 Laptop Camera Access (Webcam Index 0):
```powershell
$env:IBVAP_RTSP_URL="0"; $env:PYTHONIOENCODING="utf-8"; python main.py
```

#### 🔹 Custom RTSP Stream Input:
```powershell
$env:IBVAP_RTSP_URL="rtsp://admin:password@192.168.1.100:554/stream1"; python main.py
```

---

## 🌐 Tactical Command Dashboard

Once started, open your web browser to access:
* **Tactical Command Center**: [http://localhost:8000](http://localhost:8000)
* **Live WebSocket Video Stream**: `ws://localhost:8000/ws/stream`
* **Live WebSocket Alert Stream**: `ws://localhost:8000/ws/alerts`
* **Evidence Audit Trail**: [http://localhost:8000/audit-trail](http://localhost:8000/audit-trail)

---

## 🔌 API Reference

### `POST /api/v1/verify`
Verifies the cryptographic integrity of an evidence hash against the on-disk chain-of-custody.

**Request Body:**
```json
{
  "event_id": "EVT_20260904_142510_101",
  "test_hash": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
}
```

**Response:**
```json
{
  "verified": true,
  "event_id": "EVT_20260904_142510_101",
  "bop_id": "BOP_SECTOR_07_JAMSHEDPUR"
}
```

---

## 🐳 Docker Deployment

To launch the full production environment with container isolation:
```bash
docker-compose up --build -d
```

---

## 📜 License & Compliance

Developed for **Problem Statement 26187** (SSB, Ministry of Home Affairs). Built under zero-trust defense system architectural principles.
