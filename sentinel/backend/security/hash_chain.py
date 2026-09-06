"""
SENTINEL v2.0 — Evidence Hash Chain Verifier
Provides one-click evidence file verification against the blockchain registry.
"""

from typing import Dict, Any
from backend.security.blockchain_audit import BlockchainAuditTrail

class HashChainVerifier:
    def __init__(self, blockchain: BlockchainAuditTrail):
        self.blockchain = blockchain

    def verify_file(self, file_path: str) -> Dict[str, Any]:
        file_hash = self.blockchain.compute_file_hash(file_path)
        for block in self.blockchain.get_chain():
            if block.get("file_hash") == file_hash:
                return {
                    "matched": True,
                    "block_index": block["index"],
                    "timestamp": block["timestamp"],
                    "sealed_by": block["uploaded_by"],
                    "block_hash": block["block_hash"],
                    "status": "SEALED_VALID"
                }
        return {
            "matched": False,
            "computed_hash": file_hash,
            "status": "UNSEALED_OR_TAMPERED"
        }
