"""Audit log API routes."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.audit import (
    AuditLogCreate,
    AuditLogList,
    AuditLogResponse,
    DecisionLineageResponse,
)
from app.services.log_capture import LogCaptureService

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


def get_capture_service(db: AsyncSession = Depends(get_db)) -> LogCaptureService:
    """Get log capture service."""
    return LogCaptureService(db)


@router.post(
    "/logs",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create audit log",
    description="Capture a new AI decision audit log",
)
async def create_audit_log(
    log_data: AuditLogCreate,
    service: LogCaptureService = Depends(get_capture_service),
) -> AuditLogResponse:
    """Create a new audit log entry."""
    try:
        audit_log = await service.capture_log(log_data)
        return AuditLogResponse.model_validate(audit_log)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit log: {str(e)}",
        )


@router.get(
    "/logs",
    response_model=AuditLogList,
    summary="List audit logs",
    description="Get paginated list of audit logs for an organization",
)
async def list_audit_logs(
    organization_id: str = Query(..., description="Organization ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    include_deleted: bool = Query(False, description="Include GDPR deleted logs"),
    service: LogCaptureService = Depends(get_capture_service),
) -> AuditLogList:
    """List audit logs with pagination."""
    skip = (page - 1) * page_size
    
    logs, total = await service.get_logs_by_organization(
        organization_id=organization_id,
        skip=skip,
        limit=page_size,
        start_date=start_date,
        end_date=end_date,
        include_deleted=include_deleted,
    )
    
    pages = (total + page_size - 1) // page_size
    
    return AuditLogList(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/logs/{decision_id}",
    response_model=AuditLogResponse,
    summary="Get audit log",
    description="Get a specific audit log by decision ID",
)
async def get_audit_log(
    decision_id: str,
    include_deleted: bool = Query(False, description="Include if GDPR deleted"),
    service: LogCaptureService = Depends(get_capture_service),
) -> AuditLogResponse:
    """Get audit log by decision ID."""
    log = await service.get_log_by_decision_id(decision_id, include_deleted)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log with decision ID '{decision_id}' not found",
        )
    
    return AuditLogResponse.model_validate(log)


@router.get(
    "/lineage/{decision_id}",
    response_model=DecisionLineageResponse,
    summary="Get decision lineage",
    description="Get the complete decision lineage tree",
)
async def get_decision_lineage(
    decision_id: str,
    service: LogCaptureService = Depends(get_capture_service),
) -> DecisionLineageResponse:
    """Get decision lineage with related decisions."""
    lineage = await service.get_decision_lineage(decision_id)
    
    if not lineage["nodes"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision '{decision_id}' not found",
        )
    
    from app.schemas.audit import DecisionLineageNode
    
    return DecisionLineageResponse(
        root_decision_id=lineage["root_decision_id"],
        nodes=[DecisionLineageNode(**node) for node in lineage["nodes"]],
        total_nodes=lineage["total_nodes"],
        verified_integrity=lineage["verified_integrity"],
    )


@router.get(
    "/stats/{organization_id}",
    summary="Get audit statistics",
    description="Get statistics for an organization",
)
async def get_audit_stats(
    organization_id: str,
    service: LogCaptureService = Depends(get_capture_service),
) -> dict:
    """Get audit statistics."""
    logs, total = await service.get_logs_by_organization(
        organization_id=organization_id,
        limit=1000000,  # Get all for stats
    )
    
    # Calculate stats
    anchored = sum(1 for log in logs if log.blockchain_tx_hash)
    gdpr_deleted = sum(1 for log in logs if log.is_gdpr_deleted)
    
    models = {}
    decision_types = {}
    
    for log in logs:
        models[log.model_name] = models.get(log.model_name, 0) + 1
        dt = log.decision_type.value
        decision_types[dt] = decision_types.get(dt, 0) + 1
    
    return {
        "organization_id": organization_id,
        "total_decisions": total,
        "blockchain_anchored": anchored,
        "gdpr_deleted": gdpr_deleted,
        "models_used": models,
        "decision_types": decision_types,
    }


@router.post(
    "/batch",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Batch create audit logs",
    description="Create multiple audit logs in one request",
)
async def batch_create_audit_logs(
    logs: List[AuditLogCreate],
    service: LogCaptureService = Depends(get_capture_service),
) -> List[AuditLogResponse]:
    """Batch create audit logs."""
    results = []
    for log_data in logs:
        audit_log = await service.capture_log(log_data)
        results.append(AuditLogResponse.model_validate(audit_log))
    
    return results
