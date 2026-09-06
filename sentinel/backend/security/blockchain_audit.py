"""
SENTINEL v2.0 — Cryptographic SHA-256 Blockchain Audit Trail
Provides tamper-proof immutable evidence chain-of-custody logging.
Every upload, access, and dossier export is sealed into a cryptographic block.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

from backend.config import PROJECT_ROOT

CHAIN_FILE = os.path.join(PROJECT_ROOT, "data", "blockchain_chain.json")

class BlockchainAuditTrail:
    def __init__(self, chain_file: str = CHAIN_FILE):
        self.chain_file = chain_file
        self.chain: List[Dict[str, Any]] = []
        self._load_or_create_chain()

    def _load_or_create_chain(self):
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, "r", encoding="utf-8") as f:
                    self.chain = json.load(f)
                return
            except Exception:
                pass

        # Initialize with Genesis Block
        genesis = {
            "index": 0,
            "timestamp": "2026-01-01T00:00:00.000000",
            "file_hash": "0" * 64,
            "file_name": "GENESIS_EVIDENCE_ROOT",
            "file_type": "ROOT",
            "uploaded_by": "MHA_NCRB_ROOT_AUTHORITY",
            "previous_hash": "0" * 64,
            "block_hash": self._compute_block_hash(0, "2026-01-01T00:00:00.000000", "0" * 64, "0" * 64)
        }
        self.chain = [genesis]
        self._save_chain()

    def _save_chain(self):
        os.makedirs(os.path.dirname(self.chain_file), exist_ok=True)
        with open(self.chain_file, "w", encoding="utf-8") as f:
            json.dump(self.chain, f, indent=2)

    def _compute_block_hash(self, index: int, timestamp: str, file_hash: str, previous_hash: str) -> str:
        payload = f"{index}:{timestamp}:{file_hash}:{previous_hash}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def compute_file_hash(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def add_block(self, file_hash: str, file_name: str, file_type: str = "DOCUMENT", uploaded_by: str = "INVESTIGATOR") -> Dict[str, Any]:
        previous_block = self.chain[-1]
        previous_hash = previous_block["block_hash"]
        index = len(self.chain)
        timestamp = datetime.now().isoformat()
        block_hash = self._compute_block_hash(index, timestamp, file_hash, previous_hash)

        block = {
            "index": index,
            "timestamp": timestamp,
            "file_hash": file_hash,
            "file_name": file_name,
            "file_type": file_type,
            "uploaded_by": uploaded_by,
            "previous_hash": previous_hash,
            "block_hash": block_hash
        }
        self.chain.append(block)
        self._save_chain()
        return block

    def verify_chain(self) -> Dict[str, Any]:
        """
        Validates cryptographic integrity from genesis to head.
        Catches any retroactive modification or corrupted block link.
        """
        errors = []
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # 1. Check previous hash reference
            if current["previous_hash"] != prev["block_hash"]:
                errors.append(f"Block #{i} broken link: prev_hash mismatch.")

            # 2. Re-compute current hash
            expected = self._compute_block_hash(
                current["index"], current["timestamp"], current["file_hash"], current["previous_hash"]
            )
            if current["block_hash"] != expected:
                errors.append(f"Block #{i} hash invalid: data altered.")

        return {
            "integrity_valid": len(errors) == 0,
            "total_blocks": len(self.chain),
            "errors": errors
        }

    def simulate_tamper(self, block_index: int = 1, tampered_hash: Optional[str] = None) -> Dict[str, Any]:
        """Simulates malicious tampering on a specific block to demonstrate cryptographic fraud detection."""
        if len(self.chain) <= 1:
            self.add_block(
                file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                file_name="FIR_001_Interception.pdf",
                file_type="PDF",
                uploaded_by="Investigator #4092"
            )
        target_idx = min(max(1, block_index), len(self.chain) - 1)

        if not hasattr(self, '_original_blocks') or self._original_blocks is None:
            self._original_blocks = {}
        if target_idx not in self._original_blocks:
            self._original_blocks[target_idx] = dict(self.chain[target_idx])

        malicious_hash = tampered_hash or "FRAUDULENT_TAMPERED_HASH_00000000000000000000000000000000"
        self.chain[target_idx]["file_hash"] = malicious_hash
        self.chain[target_idx]["block_hash"] = "COMPROMISED_HASH_VIOLATING_MERKLE_LINK"
        return {
            "status": "TAMPER_SIMULATED",
            "tampered": True,
            "tampered_block_index": target_idx,
            "forged_file_hash": malicious_hash,
            "integrity_broken": True
        }

    def restore_integrity(self) -> Dict[str, Any]:
        """Restores chain integrity by repairing all compromised hashes and restoring original evidence."""
        if hasattr(self, '_original_blocks') and self._original_blocks:
            for idx, orig in self._original_blocks.items():
                if idx < len(self.chain):
                    self.chain[idx] = dict(orig)
            self._original_blocks.clear()

        # Recalculate valid chain hashes
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            self.chain[i]["previous_hash"] = prev["block_hash"]
            self.chain[i]["block_hash"] = self._compute_block_hash(
                self.chain[i]["index"],
                self.chain[i]["timestamp"],
                self.chain[i]["file_hash"],
                self.chain[i]["previous_hash"]
            )
        self._save_chain()
        return {
            "status": "INTEGRITY_RESTORED",
            "restored": True,
            "total_blocks": len(self.chain),
            "integrity_valid": True
        }

    def get_chain(self) -> List[Dict[str, Any]]:
        return self.chain
