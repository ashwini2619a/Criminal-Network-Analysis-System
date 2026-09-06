import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional

class BlockchainAuditTrail:
    def __init__(self):
        self.chain = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_block = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "file_hash": "genesis",
            "file_name": "genesis",
            "file_type": "genesis",
            "uploaded_by": "system",
            "previous_hash": "0"
        }
        genesis_block["block_hash"] = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)

    def _calculate_hash(self, block: Dict) -> str:
        block_string = f"{block['index']}{block['timestamp']}{block['file_hash']}{block['previous_hash']}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
        except Exception:
            pass # handle error properly in real scenario
        return hasher.hexdigest()

    def add_block(self, file_hash: str, file_name: str, file_type: str, uploaded_by: str) -> Dict:
        last_block = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": datetime.utcnow().isoformat(),
            "file_hash": file_hash,
            "file_name": file_name,
            "file_type": file_type,
            "uploaded_by": uploaded_by,
            "previous_hash": last_block["block_hash"]
        }
        new_block["block_hash"] = self._calculate_hash(new_block)
        self.chain.append(new_block)
        return new_block

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block["previous_hash"] != previous_block["block_hash"]:
                return False

            if current_block["block_hash"] != self._calculate_hash(current_block):
                return False
        return True

    def simulate_tamper(self, block_index: int = 1, tampered_hash: Optional[str] = None) -> Dict:
        """Simulates malicious tampering on a specific block to demonstrate cryptographic fraud detection."""
        if len(self.chain) <= 1:
            self.add_block(
                file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                file_name="FIR_001_Interception.pdf",
                file_type="PDF",
                uploaded_by="Investigator #4092"
            )
        target_idx = min(max(1, block_index), len(self.chain) - 1)
        
        if not hasattr(self, '_original_blocks'):
            self._original_blocks = {}
        if target_idx not in self._original_blocks:
            self._original_blocks[target_idx] = dict(self.chain[target_idx])

        malicious_hash = tampered_hash or "FRAUDULENT_TAMPERED_HASH_00000000000000000000000000000000"
        self.chain[target_idx]["file_hash"] = malicious_hash
        self.chain[target_idx]["block_hash"] = "COMPROMISED_HASH_VIOLATING_MERKLE_LINK"
        return {
            "status": "TAMPER_SIMULATED",
            "tampered_block_index": target_idx,
            "forged_file_hash": malicious_hash,
            "integrity_broken": True
        }

    def restore_integrity(self) -> Dict:
        """Restores chain integrity by repairing all compromised hashes and restoring original evidence."""
        if hasattr(self, '_original_blocks') and self._original_blocks:
            for idx, orig in self._original_blocks.items():
                if idx < len(self.chain):
                    self.chain[idx] = dict(orig)
            self._original_blocks.clear()

        # Recalculate valid chain hashes
        for i in range(1, len(self.chain)):
            self.chain[i]["previous_hash"] = self.chain[i - 1]["block_hash"]
            self.chain[i]["block_hash"] = self._calculate_hash(self.chain[i])

        return {
            "status": "INTEGRITY_RESTORED",
            "integrity_valid": self.verify_chain(),
            "total_blocks": len(self.chain)
        }

    def get_chain(self) -> List[Dict]:
        return self.chain

    def get_block(self, file_hash: str) -> Optional[Dict]:
        for block in self.chain:
            if block["file_hash"] == file_hash:
                return block
        return None
