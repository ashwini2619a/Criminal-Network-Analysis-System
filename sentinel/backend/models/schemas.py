"""
SENTINEL v2.0 — Pydantic Validation Schemas
Complete data models for all 11 Node types, 16 Edge types, Geo-Intelligence,
10 Automated Alert types, CaseBoard, Timeline, and API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid

from backend.models.enums import (
    PersonStatus, Gender, ThreatLevel, LocationType, OrgType,
    Severity, CrimeType, IncidentStatus, PhoneStatus, AccountType,
    TransactionType, TransactionPattern, EvidenceSourceType,
    WeaponType, WeaponLicenseStatus, SocialPlatform, UserRole,
    AlertPriority, AlertType, CaseStatus
)

# --- Base Node & Edge Models ---

class BaseNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    node_type: str = Field(..., description="Canonical node type")
    label: str = Field(..., description="Display label for visualization")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary node properties")

class BaseEdge(BaseModel):
    id: Optional[str] = None
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    edge_type: str = Field(..., description="Canonical edge type")
    label: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary edge properties")

# --- Entity Nodes ---

class PersonNode(BaseModel):
    id: str
    name: str
    aliases: List[str] = Field(default_factory=list)
    age: Optional[int] = None
    gender: Optional[Gender] = Gender.MALE
    father_name: Optional[str] = None
    national_id_hash: Optional[str] = Field(None, description="SHA-256 hash of CCTNS/National Police Registry ID")
    cctns_id: Optional[str] = Field(None, description="CCTNS Master Person Identification Number")
    aadhaar_hash: Optional[str] = Field(None, description="Deprecated legacy field (Section 29 Aadhaar Act compliant)")
    criminal_record_no: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    status: PersonStatus = PersonStatus.SUSPECT
    mugshot_path: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    notes: Optional[str] = None
    node_type: str = "Person"
    label: Optional[str] = None

class PhoneNode(BaseModel):
    id: str
    number: str
    imei: Optional[str] = None
    imsi: Optional[str] = None
    telecom_provider: Optional[str] = None
    circle: Optional[str] = None
    is_burner: bool = False
    device_model: Optional[str] = None
    first_active: Optional[str] = None
    last_active: Optional[str] = None
    status: PhoneStatus = PhoneStatus.ACTIVE
    node_type: str = "Phone"
    label: Optional[str] = None

class BankAccountNode(BaseModel):
    id: str
    account_no: str
    ifsc: str
    bank_name: str
    branch: Optional[str] = None
    upi_id: Optional[str] = None
    holder_name: Optional[str] = None
    holder_id: Optional[str] = None
    account_type: AccountType = AccountType.SAVINGS
    suspicious_flag: bool = False
    total_volume: float = 0.0
    node_type: str = "BankAccount"
    label: Optional[str] = None

class LocationNode(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    location_type: LocationType = LocationType.CRIME_SCENE
    geofence_radius_m: int = 500
    node_type: str = "Location"
    label: Optional[str] = None

class CellTowerNode(BaseModel):
    id: str
    tower_id: str
    name: str
    operator: str
    lat: float
    lon: float
    azimuth: Optional[int] = 0
    range_m: int = 1500
    sector: Optional[str] = "SEC-A"
    district: Optional[str] = None
    node_type: str = "CellTower"
    label: Optional[str] = None

class VehicleNode(BaseModel):
    id: str
    registration_no: str
    chassis_no: Optional[str] = None
    engine_no: Optional[str] = None
    make: str
    model: str
    color: str
    owner_name: Optional[str] = None
    owner_id: Optional[str] = None
    rto_district: Optional[str] = None
    is_stolen: bool = False
    is_wanted: bool = False
    node_type: str = "Vehicle"
    label: Optional[str] = None

class OrganizationNode(BaseModel):
    id: str
    name: str
    aliases: List[str] = Field(default_factory=list)
    type: OrgType = OrgType.GANG
    threat_level: int = Field(default=5, ge=1, le=10)
    leader_id: Optional[str] = None
    active_states: List[str] = Field(default_factory=list)
    estimated_members: int = 10
    node_type: str = "Organization"
    label: Optional[str] = None

class IncidentNode(BaseModel):
    id: str
    fir_no: str
    police_station: str
    district: str
    state: str = "Jharkhand"
    ipc_sections: List[str] = Field(default_factory=list)
    date_time: str
    severity: Severity = Severity.HIGH
    crime_type: CrimeType = CrimeType.EXTORTION
    description: str
    investigating_officer: str = "Inspector in-charge"
    status: IncidentStatus = IncidentStatus.UNDER_INVESTIGATION
    lat: float
    lon: float
    accused_ids: List[str] = Field(default_factory=list)
    vehicle_id: Optional[str] = None
    node_type: str = "Incident"
    label: Optional[str] = None

class EvidenceNode(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_hash_sha256: str
    file_size_bytes: int
    upload_timestamp: str
    uploaded_by: str
    source_type: EvidenceSourceType = EvidenceSourceType.FIR
    chain_of_custody: List[Dict[str, Any]] = Field(default_factory=list)
    integrity_verified: bool = True
    node_type: str = "Evidence"
    label: Optional[str] = None

# --- Graph Data Payload ---

class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_nodes: int
    total_edges: int

# --- Analysis & ML Schemas ---

class CentralityMetrics(BaseModel):
    degree: float
    betweenness: float
    closeness: float
    pagerank: float
    eigenvector: float
    composite_risk: float

class KingpinResult(BaseModel):
    node_id: str
    name: str
    risk_score: float
    degree: float
    betweenness: float
    pagerank: float
    status: str
    is_shadow_kingpin: bool = False
    reason: Optional[str] = None

class CommunityResult(BaseModel):
    community_id: int
    size: int
    members: List[Dict[str, Any]]
    density: float
    key_operative: Optional[Dict[str, Any]] = None

class HawalaLoop(BaseModel):
    cycle_nodes: List[str]
    cycle_accounts: List[str]
    total_amount: float
    time_span_hours: float
    risk_level: str
    transactions: List[Dict[str, Any]]

class BurnerPhoneResult(BaseModel):
    imei_reuse: List[Dict[str, Any]]
    sim_swap_chains: List[Dict[str, Any]]
    colocation_clusters: List[Dict[str, Any]]

class TemporalSpikeResult(BaseModel):
    incident_id: str
    fir_no: str
    spike_ratio: float
    call_count: int
    baseline_count: float
    involved_phones: List[str]

# --- Geo-Intelligence Schemas ---

class CoLocationEvent(BaseModel):
    id: str
    suspect_a_id: str
    suspect_a_name: str
    suspect_b_id: str
    suspect_b_name: str
    tower_id: str
    tower_name: str
    lat: float
    lon: float
    timestamp: str
    time_difference_min: int
    distance_meters: float

class GeofenceAlert(BaseModel):
    id: str
    suspect_id: str
    suspect_name: str
    location_id: str
    location_name: str
    geofence_radius_m: int
    detected_at: str
    tower_id: str

# --- 10 Automated Alert Schemas ---

class SecurityAlert(BaseModel):
    id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    description: str
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    action_url: Optional[str] = None

# --- Case Board (Kanban) Schemas ---

class CaseCard(BaseModel):
    id: str
    case_no: str
    title: str
    crime_type: CrimeType
    severity: Severity
    status: CaseStatus
    assigned_officer: str
    lead_suspect: Optional[str] = None
    suspect_count: int = 1
    evidence_count: int = 0
    created_at: str
    updated_at: str
    notes: List[Dict[str, Any]] = Field(default_factory=list)

class MoveCaseRequest(BaseModel):
    case_id: str
    new_status: CaseStatus

# --- AI Chat Schemas ---

class ChatQueryRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class ChatQueryResponse(BaseModel):
    answer: str
    query_type: str
    highlighted_nodes: List[str] = Field(default_factory=list)
    highlighted_edges: List[Dict[str, str]] = Field(default_factory=list)
    subgraph: Optional[Dict[str, Any]] = None
    geo_coordinates: Optional[List[Dict[str, Any]]] = None

# --- Ingestion & Auth Schemas ---

class IngestionResult(BaseModel):
    upload_id: str
    file_name: str
    file_type: str
    sha256_hash: str
    status: str
    extracted_entities_count: int
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    cross_case_links: List[Dict[str, Any]] = Field(default_factory=list)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    role: UserRole
    created_at: str
    last_login: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class SystemTelemetry(BaseModel):
    system_status: str
    total_cases: int
    total_suspects: int
    total_organizations: int
    total_towers: int
    total_transactions: int
    total_nodes: int
    total_edges: int
    active_alerts: int
    blockchain_valid: bool
    db_size_mb: float
    uptime_seconds: float
