export interface AuditLog {
  id: string
  created_at: string
  sequence_number: number
  organization_id: string
  user_id: string | null
  session_id: string | null
  model_name: string
  model_version: string
  provider: string
  decision_type: string
  decision_id: string
  input_hash: string
  output_hash: string
  context_hash: string
  full_hash: string
  merkle_root: string | null
  blockchain_tx_hash: string | null
  is_gdpr_deleted: boolean
  gdpr_deleted_at: string | null
  interaction: LLMInteraction
  context: DecisionContext
  compliance_markers: ComplianceMarker[]
}

export interface LLMInteraction {
  prompt: string
  response: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  estimated_cost_usd: number | null
  temperature: number | null
  max_tokens: number | null
  top_p: number | null
  latency_ms: number
  raw_request: Record<string, unknown> | null
  raw_response: Record<string, unknown> | null
}

export interface DecisionContext {
  application_id: string | null
  application_version: string | null
  environment: string
  request_id: string | null
  client_ip: string | null
  user_agent: string | null
  business_unit: string | null
  project_id: string | null
  workflow_id: string | null
  source_data_ids: string[] | null
  related_decisions: string[] | null
  parent_decision_id: string | null
  data_classification: string
  legal_basis: string | null
  consent_reference: string | null
  context_data: Record<string, unknown> | null
}

export interface ComplianceMarker {
  id: string
  standard: string
  requirement_id: string
  control_id: string | null
  evidence_data: Record<string, unknown> | null
  reviewer_notes: string | null
  is_compliant: boolean
  verified_at: string | null
  verified_by: string | null
}

export interface DecisionLineageNode {
  decision_id: string
  parent_decision_id: string | null
  created_at: string
  model_name: string
  decision_type: string
  full_hash: string
  verified: boolean
}

export interface DecisionLineage {
  root_decision_id: string
  nodes: DecisionLineageNode[]
  total_nodes: number
  verified_integrity: boolean
}

export interface VerificationResult {
  decision_id: string
  audit_log_id: string
  hash_verified: boolean
  merkle_verified: boolean
  blockchain_verified: boolean
  tampered: boolean
  details: {
    full_hash: string
    merkle_root: string | null
    blockchain_tx_hash: string | null
  }
}

export interface VerificationResponse {
  verified: boolean
  verification_time: string
  total_checked: number
  tampered_count: number
  results: VerificationResult[]
  merkle_root: string | null
  blockchain_tx_hash: string | null
  integrity_score: number
}

export interface MerkleProof {
  leaf_hash: string
  leaf_index: number
  proof_path: Array<{
    hash: string
    position: 'left' | 'right'
  }>
  root_hash: string
  verified: boolean
}

export interface IntegrityReport {
  generated_at: string
  organization_id: string
  overall_integrity: boolean
  integrity_score: number
  hash_chain_verified: boolean
  merkle_tree_verified: boolean
  blockchain_anchors_verified: boolean
  sequence_integrity_verified: boolean
  total_logs: number
  verified_logs: number
  tampered_logs: number
  missing_logs: number
  gdpr_deleted_logs: number
  merkle_roots_checked: number
  blockchain_anchors_checked: number
  failed_verifications: Array<{
    decision_id: string
    expected_hash: string
    timestamp: string
  }>
  recommendations: string[]
}

export interface ComplianceReport {
  organization_id: string
  generated_at: string
  report_period_start: string
  report_period_end: string
  standards: string[]
  metrics: {
    total_decisions: number
    decisions_with_evidence: number
    decisions_with_gdpr_markers: number
    blockchain_anchored: number
    failed_integrity_checks: number
    pending_deletions: number
    completed_deletions: number
  }
  controls: Array<{
    control_id: string
    standard: string
    requirement_id: string
    total_decisions: number
    compliant_decisions: number
    compliance_rate: number
  }>
  findings: unknown[]
  recommendations: string[]
}

export interface ExportRequest {
  start_date: string
  end_date: string
  format: 'json' | 'csv' | 'xlsx' | 'pdf' | 'xml'
  organization_id?: string
  compliance_standard?: string
  decision_types?: string[]
  include_deleted: boolean
  signed: boolean
  evidence_level: 'full' | 'summary' | 'hash_only'
}

export interface ExportResponse {
  export_id: string
  status: string
  download_url: string | null
  expires_at: string | null
  file_size_bytes: number | null
  checksum: string | null
  signature: string | null
  record_count: number | null
  created_at: string
}

export interface GDPRDeletionRequest {
  user_id: string
  organization_id: string
  reason: string
  legal_basis: string
  requested_by: string
  request_date: string
  include_all_sessions: boolean
  specific_decision_ids?: string[]
  date_range_start?: string
  date_range_end?: string
}

export interface GDPRDeletionResponse {
  deletion_id: string
  status: string
  requested_at: string
  completed_at: string | null
  affected_decisions: number
  tombstone_ids: string[]
  deletion_proof_hash: string | null
  blockchain_tx_hash: string | null
  verification_url: string | null
  retention_until: string
}

export interface AuditStats {
  organization_id: string
  total_decisions: number
  blockchain_anchored: number
  gdpr_deleted: number
  models_used: Record<string, number>
  decision_types: Record<string, number>
}
