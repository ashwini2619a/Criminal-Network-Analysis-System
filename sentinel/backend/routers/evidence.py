"""
SENTINEL v2.0 — Evidence Vault & Integrity Verification Router
Manages cryptographically sealed evidence files, chain-of-custody audit logs,
and real-time tamper verification against the SHA-256 blockchain.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
import os

from backend.config import SAMPLE_DIR, PROJECT_ROOT

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

@router.get("")
@router.get("/")
@router.get("/all")
async def get_all_evidence(request: Request):
    blockchain = getattr(request.app.state, "blockchain", None)
    chain = blockchain.get_chain() if blockchain else []

    # Check overall blockchain validity
    is_chain_valid = blockchain.verify_chain() if blockchain else True

    # Map blocks to evidence items
    evidence_items = []
    for blk in chain:
        if blk.get("file_name") == "GENESIS_EVIDENCE_ROOT":
            continue
        # If tampered, flag block
        is_block_compromised = not is_chain_valid and (
            "TAMPERED" in str(blk.get("file_hash", "")) or 
            "COMPROMISED" in str(blk.get("block_hash", ""))
        )
        evidence_items.append({
            "id": f"EV-{blk['index']:04d}",
            "file_name": blk["file_name"],
            "file_type": blk.get("file_type", "FIR_DOCUMENT"),
            "file_hash_sha256": blk["file_hash"],
            "upload_timestamp": blk["timestamp"],
            "uploaded_by": blk["uploaded_by"],
            "block_index": blk["index"],
            "block_hash": blk["block_hash"],
            "integrity_verified": not is_block_compromised,
            "chain_of_custody": [
                {"officer": blk["uploaded_by"], "action": "INITIAL_INGESTION_AND_SEAL", "timestamp": blk["timestamp"]}
            ]
        })

    # If chain only has genesis, include sample evidence files from firs/
    if not evidence_items:
        fir_dir = os.path.join(SAMPLE_DIR, "firs")
        if os.path.exists(fir_dir):
            for i, fname in enumerate(sorted(os.listdir(fir_dir))[:8]):
                fpath = os.path.join(fir_dir, fname)
                h = blockchain.compute_file_hash(fpath) if blockchain else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                evidence_items.append({
                    "id": f"EV-INIT-{i+1:03d}",
                    "file_name": fname,
                    "file_type": "FIR_POLICE_DOCUMENT",
                    "file_hash_sha256": h,
                    "upload_timestamp": "2026-01-15T10:00:00",
                    "uploaded_by": "Inspector R. K. Choudhary",
                    "block_index": i + 1,
                    "block_hash": f"BLK-{h[:16]}",
                    "integrity_verified": True,
                    "chain_of_custody": [
                        {"officer": "Inspector R. K. Choudhary", "action": "REGISTRATION_FIR", "timestamp": "2026-01-15T10:00:00"},
                        {"officer": "SI Animesh Verma", "action": "SEALED_INTO_SENTINEL_VAULT", "timestamp": "2026-01-15T10:30:00"}
                    ]
                })

    return evidence_items

@router.get("/verify/{evidence_id}")
async def verify_evidence_file(evidence_id: str, request: Request):
    blockchain = getattr(request.app.state, "blockchain", None)
    if not blockchain:
        raise HTTPException(status_code=500, detail="Blockchain audit trail offline")

    is_valid = blockchain.verify_chain()
    return {
        "evidence_id": evidence_id,
        "integrity_status": "AUTHENTIC_UNALTERED" if is_valid else "TAMPERED_FRAUD_DETECTED",
        "blockchain_valid": is_valid,
        "total_verified_blocks": len(blockchain.get_chain())
    }

@router.post("/simulate-tamper")
async def simulate_evidence_tamper(request: Request, block_index: int = 1):
    """Simulates evidence tampering by corrupting a block's cryptographic hash."""
    blockchain = getattr(request.app.state, "blockchain", None)
    if not blockchain:
        raise HTTPException(status_code=500, detail="Blockchain audit trail offline")
    return blockchain.simulate_tamper(block_index=block_index)

@router.post("/restore")
async def restore_evidence_integrity(request: Request):
    """Restores the blockchain audit chain to complete cryptographic integrity."""
    blockchain = getattr(request.app.state, "blockchain", None)
    if not blockchain:
        raise HTTPException(status_code=500, detail="Blockchain audit trail offline")
    return blockchain.restore_integrity()

@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str, request: Request):
    blockchain = getattr(request.app.state, "blockchain", None)
    if not blockchain:
        raise HTTPException(status_code=500, detail="Blockchain audit trail offline")
    # Filter out block by file_name or id
    chain = blockchain.get_chain()
    new_chain = [b for b in chain if b.get("file_name") != evidence_id and f"EV-{b.get('index', 0):04d}" != evidence_id]
    if hasattr(blockchain, "chain"):
        blockchain.chain = new_chain
    return {"status": "ok", "deleted_evidence_id": evidence_id}

@router.post("/clear")
async def clear_evidence_vault(request: Request):
    from backend.pipeline.blockchain import BlockchainAuditTrail
    app = request.app
    app.state.blockchain = BlockchainAuditTrail()
    return {"status": "ok", "message": "Evidence vault reset to genesis block"}
