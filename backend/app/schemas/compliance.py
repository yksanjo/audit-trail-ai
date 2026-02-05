"""Compliance-related schemas."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.audit_log import ComplianceStandard


class ExportFormat(str, Enum):
    """Export format types."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    PDF = "pdf"
    XML = "xml"


class ExportRequest(BaseModel):
    """Request to export audit logs."""
    start_date: datetime
    end_date: datetime
    format: ExportFormat = ExportFormat.JSON
    organization_id: Optional[str] = None
    compliance_standard: Optional[ComplianceStandard] = None
    decision_types: Optional[List[str]] = None
    include_deleted: bool = False
    signed: bool = True
    
    # SOC2/ISO27001 specific
    control_ids: Optional[List[str]] = None
    evidence_level: str = "full"  # full, summary, hash_only


class ExportResponse(BaseModel):
    """Export response."""
    export_id: str
    status: str  # pending, processing, completed, failed
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    signature: Optional[str] = None
    record_count: Optional[int] = None
    created_at: datetime


class ComplianceMetrics(BaseModel):
    """Compliance metrics."""
    total_decisions: int
    decisions_with_evidence: int
    decisions_with_gdpr_markers: int
    blockchain_anchored: int
    failed_integrity_checks: int
    pending_deletions: int
    completed_deletions: int


class ControlCompliance(BaseModel):
    """Compliance status for a specific control."""
    control_id: str
    standard: ComplianceStandard
    requirement_id: str
    total_decisions: int
    compliant_decisions: int
    compliance_rate: float
    last_audit_date: Optional[datetime]


class ComplianceReport(BaseModel):
    """Comprehensive compliance report."""
    organization_id: str
    generated_at: datetime
    report_period_start: datetime
    report_period_end: datetime
    standards: List[ComplianceStandard]
    
    metrics: ComplianceMetrics
    controls: List[ControlCompliance]
    
    # SOC2 Type II specific
    availability_uptime: Optional[float] = None
    confidentiality_score: Optional[float] = None
    processing_integrity_score: Optional[float] = None
    
    # ISO27001 specific
    risk_assessment_date: Optional[datetime] = None
    management_review_date: Optional[datetime] = None
    
    findings: List[Dict[str, Any]]
    recommendations: List[str]


class GDPRDeletionRequest(BaseModel):
    """Request for GDPR-compliant deletion."""
    user_id: str
    organization_id: str
    reason: str
    legal_basis: str = "Article 17 - Right to erasure"
    requested_by: str
    request_date: datetime = Field(default_factory=datetime.utcnow)
    retention_override_days: Optional[int] = None
    
    # Scope
    include_all_sessions: bool = True
    specific_decision_ids: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class GDPRDeletionResponse(BaseModel):
    """Response for GDPR deletion request."""
    deletion_id: str
    status: str  # pending, in_progress, completed, failed
    requested_at: datetime
    completed_at: Optional[datetime]
    
    affected_decisions: int
    tombstone_ids: List[str]
    deletion_proof_hash: Optional[str]
    blockchain_tx_hash: Optional[str]
    
    verification_url: Optional[str]
    retention_until: datetime


class DataRetentionPolicy(BaseModel):
    """Data retention policy configuration."""
    organization_id: str
    standard_retention_days: int = 2555  # 7 years
    gdpr_deletion_retention_days: int = 90
    audit_trail_retention_days: int = 3650  # 10 years
    
    auto_delete_after_retention: bool = False
    require_approval_for_deletion: bool = True
    blockchain_anchor_before_deletion: bool = True
    
    classifications: Dict[str, int]  # classification -> retention days
