"""Compliance API routes."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.compliance import (
    ComplianceReport,
    ExportFormat,
    ExportRequest,
    ExportResponse,
    GDPRDeletionRequest,
    GDPRDeletionResponse,
)
from app.services.export_service import ExportService
from app.services.gdpr_service import GDPRService

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    """Get export service."""
    return ExportService(db)


def get_gdpr_service(db: AsyncSession = Depends(get_db)) -> GDPRService:
    """Get GDPR service."""
    return GDPRService(db)


@router.post(
    "/export",
    response_model=ExportResponse,
    summary="Export audit logs",
    description="Export audit logs in various formats for compliance",
)
async def export_audit_logs(
    request: ExportRequest,
    service: ExportService = Depends(get_export_service),
) -> ExportResponse:
    """Export audit logs for compliance."""
    try:
        return await service.export_audit_logs(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.get(
    "/export/{export_id}/download",
    summary="Download export",
    description="Download a completed export file",
)
async def download_export(
    export_id: str,
) -> dict:
    """Download export file."""
    # In production, this would stream the file from storage
    return {
        "export_id": export_id,
        "download_url": f"/storage/exports/{export_id}",
        "message": "Use the download_url to fetch the file",
    }


@router.post(
    "/gdpr/delete",
    response_model=GDPRDeletionResponse,
    summary="GDPR deletion request",
    description="Request GDPR-compliant deletion of user data",
)
async def gdpr_delete(
    request: GDPRDeletionRequest,
    service: GDPRService = Depends(get_gdpr_service),
) -> GDPRDeletionResponse:
    """Process GDPR deletion request."""
    try:
        return await service.request_deletion(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion request failed: {str(e)}",
        )


@router.get(
    "/gdpr/deletion-history/{user_id}",
    summary="Get deletion history",
    description="Get history of GDPR deletions for a user",
)
async def get_deletion_history(
    user_id: str,
    organization_id: str = Query(..., description="Organization ID"),
    service: GDPRService = Depends(get_gdpr_service),
) -> dict:
    """Get deletion history for a user."""
    history = await service.get_deletion_history(user_id, organization_id)
    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "deletions": history,
    }


@router.get(
    "/gdpr/data-portability/{user_id}",
    summary="Data portability export",
    description="Export user data for portability request",
)
async def data_portability_export(
    user_id: str,
    organization_id: str = Query(..., description="Organization ID"),
    service: GDPRService = Depends(get_gdpr_service),
) -> dict:
    """Export user data for portability."""
    return await service.export_data_portability(user_id, organization_id)


@router.get(
    "/report/{organization_id}",
    response_model=ComplianceReport,
    summary="Generate compliance report",
    description="Generate comprehensive compliance report",
)
async def generate_compliance_report(
    organization_id: str,
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    standards: List[str] = Query(default=["SOC2", "ISO27001"]),
    service: ExportService = Depends(get_export_service),
) -> ComplianceReport:
    """Generate compliance report."""
    try:
        return await service.generate_compliance_report(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            standards=standards,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@router.get(
    "/standards",
    summary="List compliance standards",
    description="Get supported compliance standards",
)
async def list_compliance_standards() -> dict:
    """List supported compliance standards."""
    from app.models.audit_log import ComplianceStandard
    
    return {
        "standards": [
            {
                "id": s.value,
                "name": s.name,
                "description": _get_standard_description(s),
            }
            for s in ComplianceStandard
        ]
    }


def _get_standard_description(standard: "ComplianceStandard") -> str:
    """Get description for compliance standard."""
    descriptions = {
        "SOC2": "Service Organization Control 2 - Security, availability, processing integrity",
        "ISO27001": "Information Security Management System standard",
        "GDPR": "General Data Protection Regulation",
        "CCPA": "California Consumer Privacy Act",
        "HIPAA": "Health Insurance Portability and Accountability Act",
        "PCI_DSS": "Payment Card Industry Data Security Standard",
    }
    return descriptions.get(standard.value, "")


@router.get(
    "/retention-policy/{organization_id}",
    summary="Get retention policy",
    description="Get data retention policy for organization",
)
async def get_retention_policy(
    organization_id: str,
) -> dict:
    """Get data retention policy."""
    from app.config import get_settings
    settings = get_settings()
    
    return {
        "organization_id": organization_id,
        "standard_retention_days": settings.retention_days,
        "gdpr_deletion_retention_days": settings.gdpr_deletion_retention_days,
        "auto_delete_after_retention": False,
        "require_approval_for_deletion": True,
        "classifications": {
            "PUBLIC": 365,
            "INTERNAL": 2555,
            "CONFIDENTIAL": 3650,
            "RESTRICTED": 7300,
        },
    }
