"""
SENTINEL v2.0 — JWT Authentication Handler
Generates and decodes signed HMAC-SHA256 JWT bearer tokens with expiration.
"""

import hmac
import hashlib
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from backend.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64url_decode(data: str) -> bytes:
    pad = 4 - (len(data) % 4)
    if pad < 4:
        data += '=' * pad
    return base64.urlsafe_b64decode(data.encode('utf-8'))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload["exp"] = int(expire.timestamp())

    hdr_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    pay_b64 = _b64url_encode(json.dumps(payload).encode('utf-8'))

    signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{hdr_b64}.{pay_b64}.{sig_b64}"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    parts = token.split('.')
    if len(parts) != 3:
        return None

    hdr_b64, pay_b64, sig_b64 = parts
    signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()

    try:
        provided_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload_bytes = _b64url_decode(pay_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))

        # Expiry check
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            return None

        return payload
    except Exception:
        return None
