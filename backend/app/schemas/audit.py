"""Audit log schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.audit_log import ComplianceStandard, DecisionType


class LLMInteractionCreate(BaseModel):
    """Schema for creating LLM interaction."""
    prompt: str
    response: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: Optional[float] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    latency_ms: int
    raw_request: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


class DecisionContextCreate(BaseModel):
    """Schema for creating decision context."""
    application_id: Optional[str] = None
    application_version: Optional[str] = None
    environment: str = "production"
    request_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    business_unit: Optional[str] = None
    project_id: Optional[str] = None
    workflow_id: Optional[str] = None
    source_data_ids: Optional[List[str]] = None
    related_decisions: Optional[List[str]] = None
    parent_decision_id: Optional[str] = None
    data_classification: str = "INTERNAL"
    legal_basis: Optional[str] = None
    consent_reference: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class ComplianceMarkerCreate(BaseModel):
    """Schema for creating compliance marker."""
    standard: ComplianceStandard
    requirement_id: str
    control_id: Optional[str] = None
    evidence_data: Optional[Dict[str, Any]] = None
    reviewer_notes: Optional[str] = None


class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry."""
    organization_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    model_name: str
    model_version: str = "unknown"
    provider: str
    
    decision_type: DecisionType
    decision_id: str
    
    interaction: LLMInteractionCreate
    context: DecisionContextCreate
    compliance_markers: Optional[List[ComplianceMarkerCreate]] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    sequence_number: int
    
    organization_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    
    model_name: str
    model_version: str
    provider: str
    decision_type: DecisionType
    decision_id: str
    
    input_hash: str
    output_hash: str
    context_hash: str
    full_hash: str
    
    merkle_root: Optional[str]
    blockchain_tx_hash: Optional[str]
    is_gdpr_deleted: bool
    gdpr_deleted_at: Optional[datetime]
    
    interaction: Dict[str, Any]
    context: Dict[str, Any]
    compliance_markers: List[Dict[str, Any]]


class AuditLogList(BaseModel):
    """Schema for paginated audit log list."""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DecisionLineageNode(BaseModel):
    """Node in decision lineage."""
    decision_id: str
    parent_decision_id: Optional[str]
    created_at: datetime
    model_name: str
    decision_type: DecisionType
    full_hash: str
    verified: bool


class DecisionLineageResponse(BaseModel):
    """Schema for decision lineage response."""
    root_decision_id: str
    nodes: List[DecisionLineageNode]
    total_nodes: int
    verified_integrity: bool
