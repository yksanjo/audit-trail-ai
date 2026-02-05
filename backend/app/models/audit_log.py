"""Audit log models for AI decision tracking."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ComplianceStandard(str, PyEnum):
    """Supported compliance standards."""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    GDPR = "GDPR"
    CCPA = "CCPA"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"


class LogLevel(str, PyEnum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DecisionType(str, PyEnum):
    """Types of AI decisions."""
    CLASSIFICATION = "CLASSIFICATION"
    GENERATION = "GENERATION"
    RECOMMENDATION = "RECOMMENDATION"
    PREDICTION = "PREDICTION"
    ANALYSIS = "ANALYSIS"
    SUMMARIZATION = "SUMMARIZATION"
    CUSTOM = "CUSTOM"


class AuditLog(Base):
    """Main audit log entry for AI decisions."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Timestamp and ordering
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        unique=True,
        nullable=False,
    )
    
    # Organization and user context
    organization_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # AI system context
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Decision classification
    decision_type: Mapped[DecisionType] = mapped_column(
        Enum(DecisionType),
        nullable=False,
    )
    decision_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Content hashes (for integrity verification)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    output_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    context_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    full_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    
    # Encryption and privacy
    encrypted_payload_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_gdpr_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    gdpr_deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Verification
    merkle_root: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    blockchain_tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    
    # Relationships
    interaction: Mapped["LLMInteraction"] = relationship(
        back_populates="audit_log",
        uselist=False,
        cascade="all, delete-orphan",
    )
    context: Mapped["DecisionContext"] = relationship(
        back_populates="audit_log",
        uselist=False,
        cascade="all, delete-orphan",
    )
    compliance_markers: Mapped[List["ComplianceMarker"]] = relationship(
        back_populates="audit_log",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[List["AuditAttachment"]] = relationship(
        back_populates="audit_log",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("ix_audit_logs_org_created", "organization_id", "created_at"),
        Index("ix_audit_logs_model_created", "model_name", "created_at"),
    )


class LLMInteraction(Base):
    """Detailed LLM interaction data (can be encrypted)."""
    
    __tablename__ = "llm_interactions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    audit_log_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Input data
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Output data
    response: Mapped[str] = mapped_column(Text, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Token usage and cost
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Model parameters
    temperature: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    top_p: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Timing
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Raw metadata
    raw_request: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    raw_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationship
    audit_log: Mapped[AuditLog] = relationship(back_populates="interaction")


class DecisionContext(Base):
    """Context in which the decision was made."""
    
    __tablename__ = "decision_contexts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    audit_log_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Application context
    application_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    application_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    
    # Request context
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Business context
    business_unit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Data lineage
    source_data_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    related_decisions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    parent_decision_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Regulatory context
    data_classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="INTERNAL"
    )
    legal_basis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    consent_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Additional context
    context_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationship
    audit_log: Mapped[AuditLog] = relationship(back_populates="context")


class ComplianceMarker(Base):
    """Compliance tags and markers for audit logs."""
    
    __tablename__ = "compliance_markers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    audit_log_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    standard: Mapped[ComplianceStandard] = mapped_column(
        Enum(ComplianceStandard),
        nullable=False,
    )
    requirement_id: Mapped[str] = mapped_column(String(100), nullable=False)
    control_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Evidence
    evidence_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_compliant: Mapped[bool] = mapped_column(default=True, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationship
    audit_log: Mapped[AuditLog] = relationship(back_populates="compliance_markers")
    
    __table_args__ = (
        Index("ix_compliance_markers_standard", "standard", "requirement_id"),
    )


class AuditAttachment(Base):
    """Attachments to audit logs (screenshots, docs, etc)."""
    
    __tablename__ = "audit_attachments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    audit_log_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    
    # Storage
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(50), default="s3")
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationship
    audit_log: Mapped[AuditLog] = relationship(back_populates="attachments")
