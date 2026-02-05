"""GDPR/CCPA compliant deletion service with cryptographic tombstones."""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.audit_log import AuditLog
from app.models.blockchain_anchor import TombstoneRecord
from app.schemas.compliance import GDPRDeletionRequest, GDPRDeletionResponse
from app.services.blockchain_service import BlockchainService
from app.services.hasher import hash_service

settings = get_settings()


class GDPRService:
    """Service for GDPR-compliant data handling."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.blockchain = BlockchainService(db)
    
    async def request_deletion(
        self,
        request: GDPRDeletionRequest,
    ) -> GDPRDeletionResponse:
        """Process GDPR deletion request."""
        deletion_id = f"gdpr_del_{uuid.uuid4().hex[:16]}"
        
        # Find matching audit logs
        query = select(AuditLog).where(
            AuditLog.user_id == request.user_id,
            AuditLog.organization_id == request.organization_id,
            AuditLog.is_gdpr_deleted == False,
        )
        
        if request.specific_decision_ids:
            query = query.where(
                AuditLog.decision_id.in_(request.specific_decision_ids)
            )
        
        if request.date_range_start:
            query = query.where(AuditLog.created_at >= request.date_range_start)
        
        if request.date_range_end:
            query = query.where(AuditLog.created_at <= request.date_range_end)
        
        result = await self.db.execute(query)
        logs_to_delete = result.scalars().all()
        
        if not logs_to_delete:
            return GDPRDeletionResponse(
                deletion_id=deletion_id,
                status="completed",
                requested_at=request.request_date,
                affected_decisions=0,
                tombstone_ids=[],
                retention_until=datetime.utcnow(),
            )
        
        # Calculate retention period
        retention_days = request.retention_override_days or settings.gdpr_deletion_retention_days
        retention_until = datetime.utcnow() + timedelta(days=retention_days)
        
        tombstone_ids = []
        
        for log in logs_to_delete:
            # Create cryptographic tombstone
            tombstone = await self._create_tombstone(
                log=log,
                deletion_id=deletion_id,
                requested_by=request.requested_by,
                reason=request.reason,
                legal_basis=request.legal_basis,
                retention_until=retention_until,
            )
            tombstone_ids.append(tombstone.id.hex)
            
            # Mark log as deleted
            log.is_gdpr_deleted = True
            log.gdpr_deleted_at = datetime.utcnow()
            
            # Optionally anchor tombstone to blockchain
            if settings.blockchain_enabled:
                await self._anchor_tombstone(tombstone)
        
        await self.db.flush()
        
        # Create deletion proof
        deletion_proof = self._create_deletion_proof(
            deletion_id=deletion_id,
            tombstone_ids=tombstone_ids,
            requested_by=request.requested_by,
        )
        
        return GDPRDeletionResponse(
            deletion_id=deletion_id,
            status="completed",
            requested_at=request.request_date,
            completed_at=datetime.utcnow(),
            affected_decisions=len(logs_to_delete),
            tombstone_ids=tombstone_ids,
            deletion_proof_hash=deletion_proof,
            retention_until=retention_until,
        )
    
    async def _create_tombstone(
        self,
        log: AuditLog,
        deletion_id: str,
        requested_by: str,
        reason: str,
        legal_basis: str,
        retention_until: datetime,
    ) -> TombstoneRecord:
        """Create cryptographic tombstone for deleted record."""
        deletion_timestamp = datetime.utcnow().isoformat()
        
        # Create tombstone hash
        deletion_hash = hash_service.create_tombstone_hash(
            original_hash=log.full_hash,
            deletion_timestamp=deletion_timestamp,
            deleted_by=requested_by,
            reason=reason,
        )
        
        tombstone = TombstoneRecord(
            id=uuid.uuid4(),
            original_audit_log_id=log.id,
            original_decision_id=log.decision_id,
            deleted_by=requested_by,
            deletion_reason=reason,
            legal_basis=legal_basis,
            original_hash=log.full_hash,
            deletion_hash=deletion_hash,
            permanent_retention_until=retention_until,
        )
        
        self.db.add(tombstone)
        await self.db.flush()
        
        return tombstone
    
    async def _anchor_tombstone(
        self,
        tombstone: TombstoneRecord,
    ) -> None:
        """Anchor tombstone to blockchain for additional proof."""
        try:
            # Create a simple Merkle tree with just the tombstone
            merkle_root = await self.blockchain.build_merkle_tree([tombstone.deletion_hash])
            anchor = await self.blockchain.anchor_to_blockchain(merkle_root)
            
            if anchor:
                tombstone.deletion_anchor_tx_hash = anchor.tx_hash
                tombstone.deletion_verified = True
                tombstone.verified_at = datetime.utcnow()
        except Exception as e:
            # Log error but don't fail deletion
            print(f"Failed to anchor tombstone: {e}")
    
    def _create_deletion_proof(
        self,
        deletion_id: str,
        tombstone_ids: List[str],
        requested_by: str,
    ) -> str:
        """Create proof of deletion."""
        proof_data = {
            "deletion_id": deletion_id,
            "tombstone_ids": tombstone_ids,
            "requested_by": requested_by,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "GDPR_DELETION",
        }
        return hash_service.hash_dict(proof_data)
    
    async def verify_tombstone(
        self,
        tombstone_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Verify a tombstone record."""
        result = await self.db.execute(
            select(TombstoneRecord).where(
                TombstoneRecord.id == uuid.UUID(tombstone_id)
            )
        )
        tombstone = result.scalar_one_or_none()
        
        if not tombstone:
            return None
        
        # Verify deletion hash
        computed_hash = hash_service.create_tombstone_hash(
            original_hash=tombstone.original_hash,
            deletion_timestamp=tombstone.created_at.isoformat(),
            deleted_by=tombstone.deleted_by,
            reason=tombstone.deletion_reason,
        )
        
        hash_valid = computed_hash == tombstone.deletion_hash
        
        return {
            "tombstone_id": tombstone_id,
            "original_decision_id": tombstone.original_decision_id,
            "deletion_verified": hash_valid,
            "blockchain_anchored": tombstone.deletion_anchor_tx_hash is not None,
            "created_at": tombstone.created_at,
            "retention_until": tombstone.permanent_retention_until,
        }
    
    async def get_deletion_history(
        self,
        user_id: str,
        organization_id: str,
    ) -> List[Dict[str, Any]]:
        """Get deletion history for a user."""
        result = await self.db.execute(
            select(TombstoneRecord).where(
                TombstoneRecord.original_decision_id.in_(
                    select(AuditLog.decision_id).where(
                        AuditLog.user_id == user_id,
                        AuditLog.organization_id == organization_id,
                    )
                )
            )
        )
        tombstones = result.scalars().all()
        
        return [
            {
                "tombstone_id": t.id.hex,
                "original_decision_id": t.original_decision_id,
                "deleted_at": t.created_at,
                "deleted_by": t.deleted_by,
                "reason": t.deletion_reason,
                "deletion_hash": t.deletion_hash,
            }
            for t in tombstones
        ]
    
    async def export_data_portability(
        self,
        user_id: str,
        organization_id: str,
    ) -> Dict[str, Any]:
        """Export user data for portability request."""
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.user_id == user_id,
                AuditLog.organization_id == organization_id,
                AuditLog.is_gdpr_deleted == False,
            )
        )
        logs = result.scalars().all()
        
        return {
            "user_id": user_id,
            "organization_id": organization_id,
            "exported_at": datetime.utcnow().isoformat(),
            "total_records": len(logs),
            "data": [
                {
                    "decision_id": log.decision_id,
                    "created_at": log.created_at.isoformat(),
                    "model_name": log.model_name,
                    "decision_type": log.decision_type.value,
                    "input_hash": log.input_hash,
                    "output_hash": log.output_hash,
                    "full_hash": log.full_hash,
                    "merkle_root": log.merkle_root,
                    "blockchain_tx_hash": log.blockchain_tx_hash,
                }
                for log in logs
            ],
        }
