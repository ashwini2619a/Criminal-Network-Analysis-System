/**
 * SENTINEL v2.0 — Complete TypeScript Type Definitions
 * Covers all 11 Node types, 16 Edge types, 8 Geo-Intelligence Map layers,
 * 10 Automated Alert types, Collaborative CaseBoard, and API responses.
 */

export type NodeShape = 'ellipse' | 'triangle' | 'rectangle' | 'diamond' | 'hexagon' | 'star' | 'barrel';
export type LayoutType = 'force' | 'hierarchy' | 'concentric' | 'grid';

export interface FilterState {
  searchQuery: string;
  nodeTypes: string[];
  minRiskScore: number;
}

export interface BaseNode {
  id: string;
  node_type: string;
  label?: string;
  risk_score?: number;
  [key: string]: any;
}

export interface PersonNode extends BaseNode {
  node_type: 'Person';
  name: string;
  aliases: string[];
  age?: number;
  gender?: 'MALE' | 'FEMALE' | 'OTHER';
  father_name?: string;
  national_id_hash?: string;
  cctns_id?: string;
  aadhaar_hash?: string;
  criminal_record_no?: string;
  district?: string;
  state?: string;
  risk_score: number;
  threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'SUSPECT' | 'ACCUSED' | 'CONVICTED' | 'ABSCONDING' | 'WITNESS' | 'VICTIM' | 'INFORMANT';
  mugshot_path?: string | null;
  first_seen?: string;
  last_seen?: string;
  notes?: string;
}

export interface PhoneNode extends BaseNode {
  node_type: 'Phone';
  number: string;
  imei?: string;
  imsi?: string;
  telecom_provider?: string;
  circle?: string;
  is_burner: boolean;
  device_model?: string;
  first_active?: string;
  last_active?: string;
  status?: 'ACTIVE' | 'INACTIVE' | 'SEIZED';
}

export interface BankAccountNode extends BaseNode {
  node_type: 'BankAccount';
  account_no: string;
  ifsc: string;
  bank_name: string;
  branch?: string;
  upi_id?: string;
  holder_name?: string;
  account_type?: 'SAVINGS' | 'CURRENT' | 'WALLET';
  suspicious_flag?: boolean;
  total_volume?: number;
}

export interface LocationNode extends BaseNode {
  node_type: 'Location';
  name: string;
  lat: number;
  lon: number;
  address?: string;
  district?: string;
  state?: string;
  pincode?: string;
  location_type: 'HIDEOUT' | 'CRIME_SCENE' | 'RESIDENCE' | 'OFFICE' | 'TOWER' | 'CHECKPOINT' | 'BORDER' | 'WAREHOUSE' | 'SAFEHOUSE';
  geofence_radius_m: number;
}

export interface CellTowerNode extends BaseNode {
  node_type: 'CellTower';
  tower_id: string;
  name: string;
  operator: string;
  lat: number;
  lon: number;
  azimuth?: number;
  range_m: number;
  sector?: string;
  district?: string;
}

export interface VehicleNode extends BaseNode {
  node_type: 'Vehicle';
  registration_no: string;
  chassis_no?: string;
  engine_no?: string;
  make: string;
  model: string;
  color: string;
  owner_name?: string;
  rto_district?: string;
  is_stolen: boolean;
  is_wanted: boolean;
}

export interface OrganizationNode extends BaseNode {
  node_type: 'Organization';
  name: string;
  aliases: string[];
  type: 'GANG' | 'CARTEL' | 'TERROR_CELL' | 'SHELL_COMPANY' | 'NGO_FRONT' | 'HAWALA_NETWORK';
  threat_level: number;
  leader_id?: string;
  active_states: string[];
  estimated_members: number;
}

export interface IncidentNode extends BaseNode {
  node_type: 'Incident';
  fir_no: string;
  police_station: string;
  district: string;
  state?: string;
  ipc_sections: string[];
  date_time: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  crime_type: 'MURDER' | 'KIDNAPPING' | 'EXTORTION' | 'NARCOTICS' | 'CYBERCRIME' | 'TERRORISM' | 'WOMEN_SAFETY' | 'FRAUD' | 'ARMS' | 'DACOITY';
  description: string;
  investigating_officer?: string;
  status: 'OPEN' | 'UNDER_INVESTIGATION' | 'CHARGESHEET_FILED' | 'CLOSED' | 'REOPENED';
  lat: number;
  lon: number;
}

export interface EvidenceNode extends BaseNode {
  node_type: 'Evidence';
  file_name: string;
  file_type: string;
  file_hash_sha256: string;
  upload_timestamp: string;
  uploaded_by: string;
  source_type: string;
  chain_of_custody: Array<{ officer: string; action: string; timestamp: string }>;
  integrity_verified: boolean;
}

export type AnyNode = PersonNode | PhoneNode | BankAccountNode | LocationNode | CellTowerNode | VehicleNode | OrganizationNode | IncidentNode | EvidenceNode | BaseNode;

export interface BaseEdge {
  id?: string;
  source: string;
  target: string;
  edge_type: string;
  label?: string;
  weight?: number;
  [key: string]: any;
}

export interface GraphData {
  nodes: AnyNode[];
  edges: BaseEdge[];
  total_nodes?: number;
  total_edges?: number;
}

// --- Analysis & ML Types ---

export interface CentralityScores {
  degree: number;
  betweenness: number;
  closeness: number;
  pagerank: number;
  eigenvector: number;
  composite_risk?: number;
}

export interface KingpinResult {
  node_id: string;
  name: string;
  risk_score: number;
  composite_risk?: number;
  rank?: number;
  degree?: number;
  betweenness?: number;
  pagerank?: number;
  status: string;
  is_shadow_kingpin?: boolean;
  reason?: string;
}

export interface CommunityResult {
  community_id: number;
  size: number;
  members: AnyNode[];
  density: number;
  key_operative?: AnyNode;
}

export interface HawalaCycle {
  cycle_nodes: string[];
  cycle_accounts?: string[];
  total_amount: number;
  time_span_hours: number;
  risk_level: string;
  transactions?: any[];
}

export interface StructuringAlert {
  account_id: string;
  account_name?: string;
  suspicious_transactions: any[];
  total_structured_amount: number;
  count: number;
}

// --- Geo-Intelligence Types ---

export interface Waypoint {
  sequence: number;
  lat: number;
  lon: number;
  tower_id: string;
  district: string;
  timestamp: string;
  formatted_time: string;
  hour: number;
  color: string;
  duration_sec: number;
  call_partner?: string;
}

export interface SuspectTrail {
  phone_number: string;
  total_hits: number;
  waypoints: Waypoint[];
  dwell_percentages: Record<string, number>;
  polyline_coordinates: [number, number][];
}

export interface CoLocationEvent {
  id: string;
  suspect_a_id: string;
  suspect_a_name: string;
  suspect_b_id: string;
  suspect_b_name: string;
  tower_id: string;
  tower_name: string;
  lat: number;
  lon: number;
  timestamp: string;
  time_difference_min: number;
  distance_meters: number;
  alert_title: string;
  alert_description: string;
}

// --- Automated Alerts Types ---

export interface SecurityAlert {
  id: string;
  alert_type: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  entity_id?: string;
  entity_name?: string;
  entity_type?: string;
  timestamp: string;
  metadata?: Record<string, any>;
  acknowledged: boolean;
  action_url?: string;
}

// --- CaseBoard (Kanban) Types ---

export interface CaseCardData {
  id: string;
  case_no: string;
  title: string;
  crime_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'NEW' | 'UNDER_ANALYSIS' | 'LEADS_GENERATED' | 'CHARGESHEET_READY';
  assigned_officer: string;
  lead_suspect?: string;
  suspect_count: number;
  evidence_count: number;
  created_at: string;
  updated_at: string;
  notes: Array<{ author: string; text: string; timestamp: string }>;
}

// --- Dashboard & Chat Types ---

export interface DashboardData {
  total_cases: number;
  total_suspects: number;
  active_networks: number;
  high_risk_alerts: number;
  top_kingpins: KingpinResult[];
  threat_distribution: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  recent_activity: any[];
  network_density: number;
  avg_degree: number;
  total_nodes: number;
  total_edges: number;
  cases_over_time: Array<{ month: string; count: number }>;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  query_type?: string;
  highlighted_nodes?: string[];
}

// --- Face Tracker Types ---
export interface DetectedFace {
  face_id: string;
  bounding_box: { x: number; y: number; width: number; height: number };
  confidence: number;
  embedding_status: 'COMPUTED' | 'FAILED';
}

export interface FaceProfile {
  id: string;
  label: string;
  suspect_id?: string;
  suspect_name?: string;
  thumbnail_url: string;
  registered_at: string;
  total_matches: number;
  last_scanned?: string;
}

export interface FaceMatchResult {
  match_id: string;
  face_profile_id: string;
  evidence_file_name: string;
  evidence_file_id: string;
  similarity_score: number;
  matched_face_bbox: { x: number; y: number; width: number; height: number };
  matched_image_url: string;
  source_upload_timestamp: string;
  blockchain_hash?: string;
}

export interface FaceScanSummary {
  face_id: string;
  total_evidence_scanned: number;
  total_matches: number;
  matches: FaceMatchResult[];
  scan_duration_ms: number;
  scan_timestamp: string;
}

// --- Person Tracker Types ---
export type DetectionSource = 'live' | 'uploaded';

export interface DetectedPerson {
  person_index: number;
  bounding_box: { x: number; y: number; width: number; height: number };
  confidence: number;
  source: DetectionSource;
  area_percentage: number;
  timestamp: string;
}

export interface PersonDetectionResult {
  detection_id: string;
  source_type: DetectionSource;
  image_width: number;
  image_height: number;
  persons: DetectedPerson[];
  total_persons: number;
  processing_time_ms: number;
  file_name?: string;
  sha256_hash?: string;
  timestamp: string;
}

export interface LiveDetectionFrame {
  frame_index: number;
  timestamp: string;
  persons_count: number;
  persons: DetectedPerson[];
  fps: number;
}

export interface PersonDetectionHistoryItem {
  id: string;
  file_name: string;
  source_type: DetectionSource;
  persons_detected: number;
  thumbnail_url: string;
  timestamp: string;
  sha256_hash?: string;
}
