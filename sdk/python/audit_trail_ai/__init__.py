"""Audit Trail AI Python SDK.

Tamper-proof logging for AI decisions with SOC2/ISO27001/GDPR compliance.
"""
__version__ = "1.0.0"

from audit_trail_ai.client import AuditClient
from audit_trail_ai.decorators import audit_llm_call
from audit_trail_ai.types import (
    AuditLogEntry,
    LLMInteraction,
    DecisionContext,
    ComplianceStandard,
)

__all__ = [
    "AuditClient",
    "audit_llm_call",
    "AuditLogEntry",
    "LLMInteraction",
    "DecisionContext",
    "ComplianceStandard",
]
