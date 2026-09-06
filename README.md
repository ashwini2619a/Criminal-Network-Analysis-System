# Criminal Network Analysis System (SENTINEL & SIH 2025)

An AI-driven Defense Surveillance, Edge Video Analytics, and Criminal Network Analysis platform designed for intelligent tracking, real-time threat detection, and comprehensive evidence forensics.

## 🚀 Key Modules & Architecture

### 1. Sentinel Edge Analytics & C2 Platform (`sentinel/`)
- **Live Person & Object Detection**: YOLOv8-powered real-time detection and ByteTrack multi-target tracking.
- **Visual Analytics**: Interactive bounding box rendering (live detection and uploaded photo matching).
- **FastAPI Edge Engine**: RESTful endpoints and real-time WebSocket telemetry for surveillance feeds.
- **Command & Control Dashboard**: Responsive React-based monitoring interface with live feeds and spatial tracking.
- **Audit & Forensics**: Cryptographic hashing and evidence logging.

### 2. SIH 2025 Submission Materials
- **Presentation Deck**: `SIH2025_Criminal_Network_Analysis_System.pptx`
- **Specification Document**: `SIH2025_Criminal_Network_Analysis_System.pdf`
- **Format Reference**: `SIH2025-IDEA-Presentation-Format.pptx`

### 3. Network Monitor (`network_monitor-Ritu/`)
- Distributed device and CCTV camera ping engine, connectivity telemetry, and network status dashboards.

### 4. Intelligent Border Video Analytics Platform (`IBVAP-main/`)
- Core blockchain evidence tracking, vector geofencing, and multi-camera orchestration.

---

## 🛠️ Quick Start

### Sentinel
```bash
cd sentinel
# Windows batch launch
start_sentinel.bat
```

### Network Monitor
```bash
cd network_monitor-Ritu
run.bat
```
