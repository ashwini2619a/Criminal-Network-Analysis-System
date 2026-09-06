"""
SENTINEL v2.0 — Central Configuration
Provides environment constants, file storage paths, and algorithm thresholds.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
TEST_DOCS_DIR = os.path.join(DATA_DIR, "test_documents")
DB_PATH = os.path.join(BASE_DIR, "data", "sentinel.db")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(TEST_DOCS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Data Initialization Flag: default False (clean slate for real data)
LOAD_SAMPLE_DATA = os.environ.get("LOAD_SAMPLE_DATA", "false").lower() == "true"

# Security & Tokens
SECRET_KEY = os.environ.get("SENTINEL_SECRET_KEY", "SENTINEL_CYBER_MHA_OFFLINE_SECRET_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Algorithm Thresholds
HAWALA_STRUCTURING_THRESHOLD = 50000.0  # PAN reporting limit
HAWALA_CYCLE_MAX_HOURS = 72
BURNER_CONTACT_OVERLAP_THRESHOLD = 0.40  # 40% contact overlap
PRE_CRIME_SPIKE_RATIO = 2.5              # 250% baseline surge
COLOCATION_DISTANCE_METERS = 500.0
COLOCATION_TIME_WINDOW_MIN = 45

# Feature Flags
USE_NEO4J = os.environ.get("SENTINEL_USE_NEO4J", "false").lower() == "true"
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "sentinel2026")

# NVIDIA AI Investigation Chat API
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")
NVIDIA_INVOKE_URL = os.environ.get("NVIDIA_INVOKE_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")
NVIDIA_ALTERNATIVE_MODEL = "moonshotai/kimi-k3"

# Face Tracker Configuration
FACE_SIMILARITY_THRESHOLD = 0.6
FACE_THUMBNAILS_DIR = os.path.join(BASE_DIR, "data", "face_thumbnails")
FACE_MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
os.makedirs(FACE_THUMBNAILS_DIR, exist_ok=True)

# Person Tracker Configuration
PERSON_CONFIDENCE_THRESHOLD = 0.5
PERSON_LIVE_FAST_MODE_IMGSZ = 320
PERSON_EVIDENCE_IMGSZ = 640
PERSON_CAPTURES_DIR = os.path.join(BASE_DIR, "data", "person_captures")
os.makedirs(PERSON_CAPTURES_DIR, exist_ok=True)

# Bounding Box Color Convention (BGR for OpenCV)
BBOX_COLOR_LIVE = (94, 197, 34)        # GREEN (#22c55e) in OpenCV BGR: B=94, G=197, R=34
BBOX_COLOR_UPLOADED = (68, 68, 239)    # RED (#ef4444) in OpenCV BGR: B=68, G=68, R=239
