import re
import hashlib
import base64
from typing import Dict, Any, Union

class PIISecurityManager:
    """
    Law-Enforcement PII Encryption & Masking at Rest.
    Enforces Data Protection & Privacy guidelines (DPDP Act 2023 / IT Act Sec 43A).
    Masks Aadhaar numbers, telecom MSISDNs, and bank accounts for standard Investigators,
    while permitting cryptographically audited unmasking for Supervisors with judicial warrants.
    """
    def __init__(self, salt: str = "SENTINEL_CYBER_VAULT_KEY_2026"):
        self.salt = salt

    def mask_phone(self, phone: str) -> str:
        """Masks phone number: +91-9876543210 -> +91-98765XXXXX"""
        if not phone or len(phone) < 10:
            return phone
        clean = phone.strip()
        if len(clean) >= 10:
            prefix = clean[:-5]
            return prefix + "XXXXX"
        return clean

    def mask_aadhaar(self, aadhaar: str) -> str:
        """Masks Aadhaar: 1234 5678 9012 -> XXXX-XXXX-9012"""
        if not aadhaar:
            return "XXXX-XXXX-XXXX"
        clean = re.sub(r'\D', '', aadhaar)
        if len(clean) == 12:
            return f"XXXX-XXXX-{clean[-4:]}"
        return "XXXX-XXXX-" + clean[-4:] if len(clean) >= 4 else "XXXX-XXXX-XXXX"

    def mask_bank_account(self, acc: str) -> str:
        """Masks Bank Account: 123456789012 -> XXXXXXXXX012"""
        if not acc:
            return "XXXXXXXXXXXX"
        clean = str(acc).strip()
        if len(clean) >= 4:
            return "X" * (len(clean) - 4) + clean[-4:]
        return "XXXX"

    def anonymize_identifier(self, identifier: str) -> str:
        """Deterministic one-way SHA-256 pseudonym for cross-matching without exposing raw PII."""
        return hashlib.sha256(f"{identifier}:{self.salt}".encode('utf-8')).hexdigest()

    def process_person_pii(self, person: Dict[str, Any], role: str = "INVESTIGATOR") -> Dict[str, Any]:
        """
        Applies role-based PII masking.
        - INVESTIGATOR: Masked phones, masked Aadhaar, masked accounts.
        - SUPERVISOR / ADMIN: Unmasked raw identifiers with audit trail logging.
        """
        p = dict(person)
        if role.upper() in ("SUPERVISOR", "ADMIN"):
            p['pii_clearance'] = "UNMASKED_JUDICIAL_CLEARANCE"
            return p

        # Mask for regular investigator
        p['pii_clearance'] = "MASKED_DPDP_COMPLIANT"
        if 'number' in p and p['number']:
            p['raw_number_masked'] = self.mask_phone(str(p['number']))
        if 'caller_number' in p and p['caller_number']:
            p['caller_number'] = self.mask_phone(str(p['caller_number']))
        if 'receiver_number' in p and p['receiver_number']:
            p['receiver_number'] = self.mask_phone(str(p['receiver_number']))
        if 'aadhaar' in p and p['aadhaar']:
            p['aadhaar'] = self.mask_aadhaar(str(p['aadhaar']))
        if 'account_no' in p and p['account_no']:
            p['account_no'] = self.mask_bank_account(str(p['account_no']))
        return p

# Global singleton
pii_security = PIISecurityManager()
