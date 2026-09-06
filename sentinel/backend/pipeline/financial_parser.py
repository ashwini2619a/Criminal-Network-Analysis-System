"""
SENTINEL v2.0 — Financial Transaction Parser
Parses bank statement CSV/Excel exports, UPI transaction dumps, and extracts
sender/receiver accounts, IFSC codes, UTR references, and transaction amounts.
"""

import os
import re
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class FinancialParser:
    def __init__(self):
        self.column_aliases = {
            "sender_account": ["sender_acc", "sender_account", "from_account", "debit_account", "remitter_acc"],
            "receiver_account": ["receiver_acc", "receiver_account", "to_account", "credit_account", "beneficiary_acc"],
            "amount": ["amount", "txn_amount", "transaction_amount", "debit", "credit"],
            "utr": ["utr", "reference_no", "ref_no", "transaction_id", "txn_id", "rrn"],
            "timestamp": ["date", "timestamp", "txn_date", "value_date", "datetime"],
            "sender_name": ["sender_name", "remitter_name", "from_name"],
            "receiver_name": ["receiver_name", "beneficiary_name", "to_name"],
            "sender_bank": ["sender_bank", "bank_name", "bank"],
            "ifsc": ["ifsc", "ifsc_code", "branch_ifsc"]
        }

    def detect_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        mapping = {}
        headers_lower = [h.strip().lower().replace(" ", "_") for h in headers]
        for canonical, aliases in self.column_aliases.items():
            for i, h in enumerate(headers_lower):
                if h in aliases or any(alias in h for alias in aliases):
                    mapping[canonical] = headers[i]
                    break
        return mapping

    def parse_csv(self, file_path: str, custom_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        transactions = []
        if not os.path.exists(file_path):
            return transactions

        with open(file_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            mapping = custom_mapping or self.detect_column_mapping(headers)

            for idx, row in enumerate(reader):
                s_acc = row.get(mapping.get("sender_account", ""), "").strip()
                r_acc = row.get(mapping.get("receiver_account", ""), "").strip()
                amt_str = row.get(mapping.get("amount", ""), "0").replace(",", "").replace("₹", "").strip()

                try:
                    amount = float(amt_str)
                except Exception:
                    amount = 0.0

                if not s_acc or not r_acc or amount <= 0:
                    continue

                is_structuring = (45000.0 <= amount < 50000.0)

                transactions.append({
                    "id": f"TX-UPLOAD-{idx+1}",
                    "sender_account": s_acc,
                    "sender_name": row.get(mapping.get("sender_name", ""), "Unknown Sender"),
                    "sender_ifsc": row.get(mapping.get("ifsc", ""), "SBIN0001234"),
                    "sender_bank": row.get(mapping.get("sender_bank", ""), "State Bank of India"),
                    "receiver_account": r_acc,
                    "receiver_name": row.get(mapping.get("receiver_name", ""), "Unknown Receiver"),
                    "receiver_ifsc": row.get(mapping.get("ifsc", ""), "SBIN0005678"),
                    "receiver_bank": "HDFC Bank",
                    "amount": amount,
                    "utr": row.get(mapping.get("utr", ""), f"UTR{idx+100000}"),
                    "timestamp": row.get(mapping.get("timestamp", ""), datetime.now().isoformat()),
                    "transaction_type": "NEFT" if amount > 50000 else "UPI",
                    "pattern": "STRUCTURING" if is_structuring else "NORMAL",
                    "is_suspicious": is_structuring or amount > 250000
                })

        return transactions
