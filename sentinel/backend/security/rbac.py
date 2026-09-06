"""
SENTINEL v2.0 — Role-Based Access Control (RBAC)
Maps permissions for ADMIN, INVESTIGATOR, and ANALYST roles.
"""

from typing import Set, Dict
from backend.models.enums import UserRole

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    UserRole.ADMIN.value: {
        "view_graph", "edit_graph", "upload_evidence", "delete_evidence",
        "generate_dossier", "view_audit_log", "manage_users", "acknowledge_alerts",
        "modify_caseboard", "export_reports"
    },
    UserRole.INVESTIGATOR.value: {
        "view_graph", "edit_graph", "upload_evidence",
        "generate_dossier", "acknowledge_alerts",
        "modify_caseboard", "export_reports"
    },
    UserRole.ANALYST.value: {
        "view_graph", "generate_dossier", "export_reports"
    }
}

def check_permission(user_role: str, action: str) -> bool:
    perms = ROLE_PERMISSIONS.get(user_role.upper(), set())
    return action in perms
