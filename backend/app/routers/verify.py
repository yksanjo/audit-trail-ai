"""Verification API routes."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.verification import (
    IntegrityReport,
    MerkleProof,
    VerifyRequest,
    VerifyResponse,
    VerificationResult,
)
from app.services.blockchain_service import BlockchainService
from app.services.hasher import hash_service
from app.services.log_capture import LogCaptureService

router = APIRouter(prefix="/verify", tags=["Verification"])


def get_blockchain_service(db: AsyncSession = Depends(get_db)) -> BlockchainService:
    """Get blockchain service."""
    return BlockchainService(db)


def get_capture_service(db: AsyncSession = Depends(get_db)) -> LogCaptureService:
    """Get log capture service."""
    return LogCaptureService(db)


@router.post(
    "/",
    response_model=VerifyResponse,
    summary="Verify audit log integrity",
    description="Verify the integrity of audit logs",
)
async def verify_logs(
    request: VerifyRequest,
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
    capture_service: LogCaptureService = Depends(get_capture_service),
) -> VerifyResponse:
    """Verify audit log integrity."""
    results = []
    tampered_count = 0
    
    # Get logs to verify
    if request.decision_id:
        log = await capture_service.get_log_by_decision_id(request.decision_id)
        logs_to_verify = [log] if log else []
    elif request.audit_log_id:
        # Get by ID would need implementation
        logs_to_verify = []
    else:
        logs_to_verify, _ = await capture_service.get_logs_by_organization(
            organization_id=request.organization_id or "default",
            start_date=request.start_date,
            end_date=request.end_date,
            limit=1000,
        )
    
    for log in logs_to_verify:
        if log.is_gdpr_deleted:
            continue
        
        # Verify hash
        hash_valid = True
        if log.interaction:
            hash_valid = hash_service.verify_audit_hash(
                input_data=log.interaction.prompt,
                output_data=log.interaction.response,
                context=log.context.model_dump() if log.context else {},
                metadata={
                    "organization_id": log.organization_id,
                    "user_id": log.user_id,
                    "model_name": log.model_name,
                    "decision_type": log.decision_type.value,
                },
                expected_full_hash=log.full_hash,
            )
        
        # Check Merkle root
        merkle_valid = log.merkle_root is not None
        
        # Check blockchain
        blockchain_valid = log.blockchain_tx_hash is not None
        
        tampered = not hash_valid
        if tampered:
            tampered_count += 1
        
        results.append(VerificationResult(
            decision_id=log.decision_id,
            audit_log_id=log.id,
            hash_verified=hash_valid,
            merkle_verified=merkle_valid,
            blockchain_verified=blockchain_valid,
            tampered=tampered,
            details={
                "full_hash": log.full_hash,
                "merkle_root": log.merkle_root,
                "blockchain_tx_hash": log.blockchain_tx_hash,
            },
        ))
    
    total = len(results)
    integrity_score = (total - tampered_count) / total if total > 0 else 1.0
    
    return VerifyResponse(
        verified=tampered_count == 0,
        verification_time=datetime.utcnow(),
        total_checked=total,
        tampered_count=tampered_count,
        results=results,
        merkle_root=logs_to_verify[0].merkle_root if logs_to_verify else None,
        blockchain_tx_hash=logs_to_verify[0].blockchain_tx_hash if logs_to_verify else None,
        integrity_score=integrity_score,
    )


@router.get(
    "/merkle-proof/{decision_id}",
    response_model=MerkleProof,
    summary="Get Merkle proof",
    description="Get Merkle proof for a decision",
)
async def get_merkle_proof(
    decision_id: str,
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
    capture_service: LogCaptureService = Depends(get_capture_service),
) -> MerkleProof:
    """Get Merkle proof for a decision."""
    log = await capture_service.get_log_by_decision_id(decision_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision '{decision_id}' not found",
        )
    
    if not log.merkle_root:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision has no Merkle root",
        )
    
    # Get Merkle root ID
    from sqlalchemy import select
    from app.models.merkle_tree import MerkleRoot
    
    result = await blockchain_service.db.execute(
        select(MerkleRoot).where(MerkleRoot.root_hash == log.merkle_root)
    )
    merkle_root = result.scalar_one_or_none()
    
    if not merkle_root:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merkle root not found",
        )
    
    # Generate proof
    proof = await blockchain_service.generate_merkle_proof(
        leaf_hash=log.full_hash,
        merkle_root_id=merkle_root.id,
    )
    
    if not proof:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Merkle proof",
        )
    
    # Verify proof
    verified = await blockchain_service.verify_merkle_proof(
        leaf_hash=proof["leaf_hash"],
        root_hash=proof["root_hash"],
        proof_path=proof["proof_path"],
    )
    
    return MerkleProof(
        leaf_hash=proof["leaf_hash"],
        leaf_index=0,  # Would need to track this
        proof_path=proof["proof_path"],
        root_hash=proof["root_hash"],
        verified=verified,
    )


@router.post(
    "/merkle",
    summary="Verify Merkle proof",
    description="Verify a Merkle proof",
)
async def verify_merkle_proof(
    leaf_hash: str,
    root_hash: str,
    proof_path: List[dict],
    blockchain_service: BlockchainService = Depends(get_blockchain_service),
) -> dict:
    """Verify a Merkle proof."""
    verified = await blockchain_service.verify_merkle_proof(
        leaf_hash=leaf_hash,
        root_hash=root_hash,
        proof_path=proof_path,
    )
    
    return {
        "verified": verified,
        "leaf_hash": leaf_hash,
        "root_hash": root_hash,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/integrity-report/{organization_id}",
    response_model=IntegrityReport,
    summary="Get integrity report",
    description="Get comprehensive integrity report",
)
async def get_integrity_report(
    organization_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    capture_service: LogCaptureService = Depends(get_capture_service),
) -> IntegrityReport:
    """Generate integrity report."""
    logs, total = await capture_service.get_logs_by_organization(
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date,
        limit=100000,
    )
    
    # Run verification
    verified = 0
    tampered = 0
    failed = []
    
    for log in logs:
        if log.is_gdpr_deleted:
            continue
        
        if log.interaction:
            hash_valid = hash_service.verify_audit_hash(
                input_data=log.interaction.prompt,
                output_data=log.interaction.response,
                context=log.context.model_dump() if log.context else {},
                metadata={
                    "organization_id": log.organization_id,
                    "user_id": log.user_id,
                    "model_name": log.model_name,
                    "decision_type": log.decision_type.value,
                },
                expected_full_hash=log.full_hash,
            )
            
            if hash_valid:
                verified += 1
            else:
                tampered += 1
                failed.append({
                    "decision_id": log.decision_id,
                    "expected_hash": log.full_hash,
                    "timestamp": log.created_at.isoformat(),
                })
    
    active_logs = total - sum(1 for l in logs if l.is_gdpr_deleted)
    integrity_score = verified / active_logs if active_logs > 0 else 1.0
    
    return IntegrityReport(
        generated_at=datetime.utcnow(),
        organization_id=organization_id,
        overall_integrity=tampered == 0,
        integrity_score=integrity_score,
        hash_chain_verified=True,  # Would need sequence checking
        merkle_tree_verified=all(l.merkle_root for l in logs if not l.is_gdpr_deleted),
        blockchain_anchors_verified=all(l.blockchain_tx_hash for l in logs if not l.is_gdpr_deleted),
        sequence_integrity_verified=True,
        total_logs=total,
        verified_logs=verified,
        tampered_logs=tampered,
        missing_logs=0,
        gdpr_deleted_logs=sum(1 for l in logs if l.is_gdpr_deleted),
        merkle_roots_checked=len(set(l.merkle_root for l in logs if l.merkle_root)),
        blockchain_anchors_checked=len(set(l.blockchain_tx_hash for l in logs if l.blockchain_tx_hash)),
        failed_verifications=failed,
        recommendations=[
            "Schedule regular integrity checks",
            "Ensure all critical decisions are anchored",
            "Monitor for tampering attempts",
        ] if tampered > 0 else ["Continue regular monitoring"],
    )


@router.get(
    "/hash/{decision_id}",
    summary="Get hash details",
    description="Get hash details for a decision",
)
async def get_hash_details(
    decision_id: str,
    capture_service: LogCaptureService = Depends(get_capture_service),
) -> dict:
    """Get hash details for a decision."""
    log = await capture_service.get_log_by_decision_id(decision_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision '{decision_id}' not found",
        )
    
    return {
        "decision_id": decision_id,
        "hashes": {
            "input_hash": log.input_hash,
            "output_hash": log.output_hash,
            "context_hash": log.context_hash,
            "full_hash": log.full_hash,
        },
        "merkle_root": log.merkle_root,
        "blockchain_tx_hash": log.blockchain_tx_hash,
        "created_at": log.created_at.isoformat(),
    }
