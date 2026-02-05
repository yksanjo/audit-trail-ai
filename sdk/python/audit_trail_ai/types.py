"""Type definitions for the Audit Trail AI SDK."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComplianceStandard(str, Enum):
    """Supported compliance standards."""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    GDPR = "GDPR"
    CCPA = "CCPA"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"


class DecisionType(str, Enum):
    """Types of AI decisions."""
    CLASSIFICATION = "CLASSIFICATION"
    GENERATION = "GENERATION"
    RECOMMENDATION = "RECOMMENDATION"
    PREDICTION = "PREDICTION"
    ANALYSIS = "ANALYSIS"
    SUMMARIZATION = "SUMMARIZATION"
    CUSTOM = "CUSTOM"


@dataclass
class LLMInteraction:
    """LLM interaction data."""
    prompt: str
    response: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Optional[float] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    latency_ms: int = 0
    raw_request: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "response": self.response,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "latency_ms": self.latency_ms,
            "raw_request": self.raw_request,
            "raw_response": self.raw_response,
        }


@dataclass
class DecisionContext:
    """Decision context."""
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": self.application_id,
            "application_version": self.application_version,
            "environment": self.environment,
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "business_unit": self.business_unit,
            "project_id": self.project_id,
            "workflow_id": self.workflow_id,
            "source_data_ids": self.source_data_ids,
            "related_decisions": self.related_decisions,
            "parent_decision_id": self.parent_decision_id,
            "data_classification": self.data_classification,
            "legal_basis": self.legal_basis,
            "consent_reference": self.consent_reference,
            "context_data": self.context_data,
        }


@dataclass
class AuditLogEntry:
    """Audit log entry."""
    id: str
    decision_id: str
    created_at: datetime
    organization_id: str
    user_id: Optional[str]
    model_name: str
    decision_type: DecisionType
    full_hash: str
    merkle_root: Optional[str]
    blockchain_tx_hash: Optional[str]
    is_gdpr_deleted: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        return cls(
            id=data["id"],
            decision_id=data["decision_id"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            organization_id=data["organization_id"],
            user_id=data.get("user_id"),
            model_name=data["model_name"],
            decision_type=DecisionType(data["decision_type"]),
            full_hash=data["full_hash"],
            merkle_root=data.get("merkle_root"),
            blockchain_tx_hash=data.get("blockchain_tx_hash"),
            is_gdpr_deleted=data.get("is_gdpr_deleted", False),
        )
