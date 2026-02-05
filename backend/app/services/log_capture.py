"""Service for capturing and storing audit logs."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import (
    AuditLog,
    ComplianceMarker,
    ComplianceStandard,
    DecisionContext,
    DecisionType,
    LLMInteraction,
)
from app.schemas.audit import AuditLogCreate, ComplianceMarkerCreate
from app.services.hasher import hash_service


class LogCaptureService:
    """Service for capturing AI decision audit logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def capture_log(
        self,
        log_data: AuditLogCreate,
    ) -> AuditLog:
        """Capture a new audit log entry."""
        # Compute hashes
        hashes = hash_service.compute_audit_hash(
            input_data=log_data.interaction.prompt,
            output_data=log_data.interaction.response,
            context=log_data.context.model_dump(),
            metadata={
                "organization_id": log_data.organization_id,
                "user_id": log_data.user_id,
                "model_name": log_data.model_name,
                "decision_type": log_data.decision_type.value,
            },
        )
        
        # Create audit log
        audit_log = AuditLog(
            id=uuid.uuid4(),
            organization_id=log_data.organization_id,
            user_id=log_data.user_id,
            session_id=log_data.session_id,
            model_name=log_data.model_name,
            model_version=log_data.model_version,
            provider=log_data.provider,
            decision_type=log_data.decision_type,
            decision_id=log_data.decision_id or f"dec_{uuid.uuid4().hex[:12]}",
            input_hash=hashes["input_hash"],
            output_hash=hashes["output_hash"],
            context_hash=hashes["context_hash"],
            full_hash=hashes["full_hash"],
        )
        
        # Create LLM interaction
        interaction = LLMInteraction(
            id=uuid.uuid4(),
            audit_log_id=audit_log.id,
            prompt=log_data.interaction.prompt,
            response=log_data.interaction.response,
            prompt_tokens=log_data.interaction.prompt_tokens,
            completion_tokens=log_data.interaction.completion_tokens,
            total_tokens=log_data.interaction.total_tokens,
            estimated_cost_usd=log_data.interaction.estimated_cost_usd,
            temperature=log_data.interaction.temperature,
            max_tokens=log_data.interaction.max_tokens,
            top_p=log_data.interaction.top_p,
            latency_ms=log_data.interaction.latency_ms,
            raw_request=log_data.interaction.raw_request,
            raw_response=log_data.interaction.raw_response,
        )
        
        # Create decision context
        context = DecisionContext(
            id=uuid.uuid4(),
            audit_log_id=audit_log.id,
            application_id=log_data.context.application_id,
            application_version=log_data.context.application_version,
            environment=log_data.context.environment,
            request_id=log_data.context.request_id,
            client_ip=log_data.context.client_ip,
            user_agent=log_data.context.user_agent,
            business_unit=log_data.context.business_unit,
            project_id=log_data.context.project_id,
            workflow_id=log_data.context.workflow_id,
            source_data_ids=log_data.context.source_data_ids,
            related_decisions=log_data.context.related_decisions,
            parent_decision_id=log_data.context.parent_decision_id,
            data_classification=log_data.context.data_classification,
            legal_basis=log_data.context.legal_basis,
            consent_reference=log_data.context.consent_reference,
            context_data=log_data.context.context_data,
        )
        
        # Add to database
        self.db.add(audit_log)
        self.db.add(interaction)
        self.db.add(context)
        
        # Add compliance markers
        if log_data.compliance_markers:
            for marker_data in log_data.compliance_markers:
                marker = ComplianceMarker(
                    id=uuid.uuid4(),
                    audit_log_id=audit_log.id,
                    standard=marker_data.standard,
                    requirement_id=marker_data.requirement_id,
                    control_id=marker_data.control_id,
                    evidence_data=marker_data.evidence_data,
                    reviewer_notes=marker_data.reviewer_notes,
                )
                self.db.add(marker)
        
        await self.db.flush()
        await self.db.refresh(audit_log)
        
        return audit_log
    
    async def get_log_by_decision_id(
        self,
        decision_id: str,
        include_deleted: bool = False,
    ) -> Optional[AuditLog]:
        """Get audit log by decision ID."""
        query = select(AuditLog).where(AuditLog.decision_id == decision_id)
        if not include_deleted:
            query = query.where(AuditLog.is_gdpr_deleted == False)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_logs_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_deleted: bool = False,
    ) -> tuple[List[AuditLog], int]:
        """Get paginated audit logs for organization."""
        from sqlalchemy import func
        
        query = select(AuditLog).where(
            AuditLog.organization_id == organization_id
        )
        count_query = select(func.count(AuditLog.id)).where(
            AuditLog.organization_id == organization_id
        )
        
        if not include_deleted:
            query = query.where(AuditLog.is_gdpr_deleted == False)
            count_query = count_query.where(AuditLog.is_gdpr_deleted == False)
        
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
            count_query = count_query.where(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
            count_query = count_query.where(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        count_result = await self.db.execute(count_query)
        
        return result.scalars().all(), count_result.scalar()
    
    async def get_decision_lineage(
        self,
        decision_id: str,
    ) -> Dict[str, Any]:
        """Get decision lineage with all related decisions."""
        # Get the root decision
        root = await self.get_log_by_decision_id(decision_id)
        if not root:
            return {"root_decision_id": decision_id, "nodes": [], "total_nodes": 0}
        
        nodes = []
        visited = set()
        queue = [root]
        
        while queue:
            current = queue.pop(0)
            if current.decision_id in visited:
                continue
            visited.add(current.decision_id)
            
            nodes.append({
                "decision_id": current.decision_id,
                "parent_decision_id": current.context.parent_decision_id if current.context else None,
                "created_at": current.created_at,
                "model_name": current.model_name,
                "decision_type": current.decision_type,
                "full_hash": current.full_hash,
                "verified": current.blockchain_tx_hash is not None,
            })
            
            # Find children
            if current.context and current.context.related_decisions:
                for related_id in current.context.related_decisions:
                    if related_id not in visited:
                        child = await self.get_log_by_decision_id(related_id)
                        if child:
                            queue.append(child)
        
        return {
            "root_decision_id": decision_id,
            "nodes": nodes,
            "total_nodes": len(nodes),
            "verified_integrity": all(n["verified"] for n in nodes),
        }
