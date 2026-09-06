from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import os
import hmac

SECRET_KEY = "super-secret-key-sentinel-2024"
TOKEN_EXPIRE_MINUTES = 480

RBAC_PERMISSIONS = {
    "ADMIN": ["read", "write", "delete", "admin"],
    "INVESTIGATOR": ["read", "write"],
    "ANALYST": ["read"]
}

def hash_password(password: str) -> str:
    """Generates a secure salted SHA-256 password hash."""
    salt = "sentinel_law_enforcement_salt"
    return hashlib.sha256(f"{salt}_{password}".encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salted hash."""
    calc_hash = hash_password(plain_password)
    return hmac.compare_digest(calc_hash, hashed_password)

def create_access_token(data: dict) -> str:
    """Generates an HMAC access token."""
    import json, base64
    payload = data.copy()
    expire = (datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)).isoformat()
    payload["exp"] = expire
    raw = json.dumps(payload, sort_keys=True).encode('utf-8')
    sig = hmac.new(SECRET_KEY.encode('utf-8'), raw, hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(raw).decode('utf-8') + "." + sig
    return token

def decode_token(token: str) -> dict:
    import json, base64
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return {}
        raw = base64.urlsafe_b64decode(parts[0].encode('utf-8'))
        sig = parts[1]
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return {}
        payload = json.loads(raw.decode('utf-8'))
        if "exp" in payload:
            try:
                exp_time = datetime.fromisoformat(payload["exp"])
                if datetime.utcnow() > exp_time:
                    return {}
            except Exception:
                pass
        return payload
    except Exception:
        return {}

def check_permission(role: str, action: str) -> bool:
    allowed_actions = RBAC_PERMISSIONS.get(role.upper(), [])
    return action in allowed_actions

class AuthService:
    def __init__(self):
        self.users = {
            "admin": {
                "id": "1",
                "username": "admin",
                "password_hash": hash_password("sentinel2024"),
                "role": "ADMIN",
                "last_login": datetime.now().isoformat()
            },
            "investigator": {
                "id": "2",
                "username": "investigator",
                "password_hash": hash_password("investigator123"),
                "role": "INVESTIGATOR",
                "last_login": datetime.now().isoformat()
            },
            "analyst": {
                "id": "3",
                "username": "analyst",
                "password_hash": hash_password("analyst123"),
                "role": "ANALYST",
                "last_login": datetime.now().isoformat()
            }
        }

    def create_default_admin(self):
        pass

    def get_users(self) -> List[Dict[str, Any]]:
        return list(self.users.values())

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.users.get(username)
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        return user
