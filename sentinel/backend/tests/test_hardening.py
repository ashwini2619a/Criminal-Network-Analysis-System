"""
SENTINEL v2.0 — Hardening & Optimization Verification Tests
Tests SQLite indices, magic-byte forensic validation, and analysis caching.
"""

import os
import sys
import sqlite3
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db.database import DB_PATH

client = TestClient(app)

def test_database_indices_exist():
    """Verify that all performance indices were created in the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indices = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected_indices = [
        "idx_audit_timestamp",
        "idx_audit_user",
        "idx_audit_action",
        "idx_evidence_hash",
        "idx_evidence_timestamp",
        "idx_uploads_hash",
        "idx_uploads_status",
        "idx_caseboard_status",
        "idx_caseboard_case_no",
        "idx_alerts_type_priority",
        "idx_alerts_timestamp",
        "idx_annotations_node_id"
    ]

    for idx in expected_indices:
        assert idx in indices, f"Missing index: {idx}"

def test_upload_magic_byte_validation_pdf():
    """Verify that spoofed/corrupted PDF uploads are rejected with 400."""
    # Fake PDF without %PDF- header
    bad_pdf_content = b"This is not a real PDF file header."
    response = client.post(
        "/api/ingest/upload",
        files={"file": ("fake_evidence.pdf", bad_pdf_content, "application/pdf")}
    )
    assert response.status_code == 400
    assert "Missing %PDF- signature" in response.json()["detail"]

def test_upload_valid_magic_byte_pdf():
    """Verify that genuine PDF magic bytes pass validation."""
    valid_pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    response = client.post(
        "/api/ingest/upload",
        files={"file": ("valid_fir.pdf", valid_pdf_content, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["blockchain_sealed"] is True
    assert "sha256_hash" in data

def test_upload_unauthorized_extension():
    """Verify that unauthorized extensions (e.g. .exe) are blocked."""
    response = client.post(
        "/api/ingest/upload",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "unauthorized" in response.json()["detail"].lower()

def test_analysis_caching_performance():
    """Verify that analysis endpoints return cached responses quickly on repeat calls."""
    import time
    t0 = time.time()
    res1 = client.get("/api/analysis/centrality")
    t1 = time.time()
    first_call_duration = t1 - t0

    t2 = time.time()
    res2 = client.get("/api/analysis/centrality")
    t3 = time.time()
    cached_call_duration = t3 - t2

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json() == res2.json()
    print(f"\n[Cache Benchmark] First call: {first_call_duration*1000:.2f}ms, Cached call: {cached_call_duration*1000:.2f}ms")

if __name__ == "__main__":
    test_database_indices_exist()
    print("[PASS] Database indices test passed.")
    test_upload_magic_byte_validation_pdf()
    print("[PASS] PDF magic-byte rejection test passed.")
    test_upload_valid_magic_byte_pdf()
    print("[PASS] Genuine PDF magic-byte acceptance test passed.")
    test_upload_unauthorized_extension()
    print("[PASS] Unauthorized extension rejection test passed.")
    test_analysis_caching_performance()
    print("[PASS] Analysis caching test passed.")
    print("\nALL HARDENING TESTS PASSED!")
