"""Audit Trail AI Client."""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from audit_trail_ai.types import (
    AuditLogEntry,
    ComplianceStandard,
    DecisionContext,
    DecisionType,
    LLMInteraction,
)


class AuditClient:
    """Client for the Audit Trail AI API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        organization_id: Optional[str] = None,
        auto_anchor: bool = True,
    ):
        """Initialize the audit client."""
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.organization_id = organization_id
        self.auto_anchor = auto_anchor
        
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )

    def _generate_decision_id(self) -> str:
        """Generate a unique decision ID."""
        timestamp = datetime.utcnow().isoformat()
        return f"dec_{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}"

    def log_llm_interaction(
        self,
        model_name: str,
        prompt: str,
        response: str,
        provider: str = "openai",
        model_version: str = "unknown",
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        decision_type: DecisionType = DecisionType.GENERATION,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: int = 0,
        temperature: Optional[float] = None,
        context: Optional[DecisionContext] = None,
        compliance_standards: Optional[List[ComplianceStandard]] = None,
        **kwargs,
    ) -> AuditLogEntry:
        """Log an LLM interaction."""
        org_id = organization_id or self.organization_id
        if not org_id:
            raise ValueError("organization_id is required")

        decision_id = self._generate_decision_id()
        
        interaction = LLMInteraction(
            prompt=prompt,
            response=response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            temperature=temperature,
        )
        
        ctx = context or DecisionContext(
            environment="production",
            data_classification="INTERNAL",
        )
        
        markers = []
        if compliance_standards:
            for standard in compliance_standards:
                markers.append({
                    "standard": standard.value,
                    "requirement_id": f"{standard.value}_AUDIT_001",
                })
        
        payload = {
            "organization_id": org_id,
            "user_id": user_id,
            "session_id": session_id,
            "model_name": model_name,
            "model_version": model_version,
            "provider": provider,
            "decision_type": decision_type.value,
            "decision_id": decision_id,
            "interaction": interaction.to_dict(),
            "context": ctx.to_dict(),
            "compliance_markers": markers,
        }
        
        response = self.client.post("/api/v1/audit/logs", json=payload)
        response.raise_for_status()
        
        return AuditLogEntry.from_dict(response.json())

    def verify_decision(self, decision_id: str) -> Dict[str, Any]:
        """Verify the integrity of a decision."""
        response = self.client.post(
            "/api/v1/verify/",
            json={"decision_id": decision_id},
        )
        response.raise_for_status()
        return response.json()

    def get_decision_lineage(self, decision_id: str) -> Dict[str, Any]:
        """Get the decision lineage."""
        response = self.client.get(f"/api/v1/audit/lineage/{decision_id}")
        response.raise_for_status()
        return response.json()

    def request_gdpr_deletion(
        self,
        user_id: str,
        organization_id: Optional[str] = None,
        reason: str = "User request",
    ) -> Dict[str, Any]:
        """Request GDPR deletion for a user."""
        org_id = organization_id or self.organization_id
        if not org_id:
            raise ValueError("organization_id is required")
        
        payload = {
            "user_id": user_id,
            "organization_id": org_id,
            "reason": reason,
            "requested_by": "sdk_client",
            "request_date": datetime.utcnow().isoformat(),
        }
        
        response = self.client.post("/api/v1/compliance/gdpr/delete", json=payload)
        response.raise_for_status()
        return response.json()

    def export_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
        organization_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Export audit logs."""
        org_id = organization_id or self.organization_id
        if not org_id:
            raise ValueError("organization_id is required")
        
        payload = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "format": format,
            "organization_id": org_id,
            "include_deleted": False,
            "signed": True,
            "evidence_level": "full",
        }
        
        response = self.client.post("/api/v1/compliance/export", json=payload)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
