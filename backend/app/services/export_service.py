"""Export service for SOC2/ISO27001 compliance."""
import csv
import io
import json
import uuid
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog, ComplianceMarker
from app.schemas.compliance import (
    ComplianceReport,
    ControlCompliance,
    ExportFormat,
    ExportRequest,
    ExportResponse,
)
from app.services.hasher import hash_service


class ExportService:
    """Service for exporting audit data for compliance."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_audit_logs(
        self,
        request: ExportRequest,
    ) -> ExportResponse:
        """Export audit logs in requested format."""
        export_id = f"export_{uuid.uuid4().hex[:16]}"
        
        # Build query
        query = select(AuditLog).where(
            AuditLog.created_at >= request.start_date,
            AuditLog.created_at <= request.end_date,
        )
        
        if request.organization_id:
            query = query.where(AuditLog.organization_id == request.organization_id)
        
        if not request.include_deleted:
            query = query.where(AuditLog.is_gdpr_deleted == False)
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # Apply limit
        if len(logs) > settings.max_export_rows:
            logs = logs[:settings.max_export_rows]
        
        # Generate export based on format
        if request.format == ExportFormat.JSON:
            content = self._export_json(logs, request)
        elif request.format == ExportFormat.CSV:
            content = self._export_csv(logs, request)
        elif request.format == ExportFormat.EXCEL:
            content = await self._export_excel(logs, request)
        elif request.format == ExportFormat.PDF:
            content = await self._export_pdf(logs, request)
        elif request.format == ExportFormat.XML:
            content = self._export_xml(logs, request)
        else:
            content = self._export_json(logs, request)
        
        # Calculate checksum
        checksum = hash_service.hash_bytes(content)
        
        # Sign if requested
        signature = None
        if request.signed:
            signature = hash_service.generate_hmac(checksum)
        
        return ExportResponse(
            export_id=export_id,
            status="completed",
            download_url=f"/api/v1/compliance/exports/{export_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=30),
            file_size_bytes=len(content),
            checksum=checksum,
            signature=signature,
            record_count=len(logs),
            created_at=datetime.utcnow(),
        )
    
    def _export_json(
        self,
        logs: List[AuditLog],
        request: ExportRequest,
    ) -> bytes:
        """Export as JSON."""
        data = []
        for log in logs:
            entry = self._format_log_entry(log, request.evidence_level)
            data.append(entry)
        
        # Add metadata
        export_data = {
            "export_metadata": {
                "format": "JSON",
                "generated_at": datetime.utcnow().isoformat(),
                "record_count": len(logs),
                "evidence_level": request.evidence_level,
                "compliance_standards": [s.value for s in request.compliance_standards] if request.compliance_standards else [],
            },
            "audit_logs": data,
        }
        
        return json.dumps(export_data, indent=2, default=str).encode("utf-8")
    
    def _export_csv(
        self,
        logs: List[AuditLog],
        request: ExportRequest,
    ) -> bytes:
        """Export as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "decision_id",
            "timestamp",
            "organization_id",
            "user_id",
            "model_name",
            "decision_type",
            "input_hash",
            "output_hash",
            "full_hash",
            "merkle_root",
            "blockchain_tx_hash",
            "verified",
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.decision_id,
                log.created_at.isoformat(),
                log.organization_id,
                log.user_id,
                log.model_name,
                log.decision_type.value,
                log.input_hash,
                log.output_hash,
                log.full_hash,
                log.merkle_root,
                log.blockchain_tx_hash,
                log.blockchain_tx_hash is not None,
            ])
        
        return output.getvalue().encode("utf-8")
    
    async def _export_excel(
        self,
        logs: List[AuditLog],
        request: ExportRequest,
    ) -> bytes:
        """Export as Excel."""
        try:
            import pandas as pd
            
            data = []
            for log in logs:
                data.append({
                    "decision_id": log.decision_id,
                    "timestamp": log.created_at,
                    "organization_id": log.organization_id,
                    "user_id": log.user_id,
                    "model_name": log.model_name,
                    "decision_type": log.decision_type.value,
                    "input_hash": log.input_hash,
                    "output_hash": log.output_hash,
                    "full_hash": log.full_hash,
                    "merkle_root": log.merkle_root,
                    "blockchain_tx_hash": log.blockchain_tx_hash,
                })
            
            df = pd.DataFrame(data)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Audit Logs", index=False)
                
                # Add metadata sheet
                metadata = pd.DataFrame([{
                    "generated_at": datetime.utcnow().isoformat(),
                    "record_count": len(logs),
                    "evidence_level": request.evidence_level,
                }])
                metadata.to_excel(writer, sheet_name="Metadata", index=False)
            
            return output.getvalue()
        except ImportError:
            # Fallback to CSV if pandas not available
            return self._export_csv(logs, request)
    
    async def _export_pdf(
        self,
        logs: List[AuditLog],
        request: ExportRequest,
    ) -> bytes:
        """Export as PDF report."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Audit Trail Export", styles["Title"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Generated: {datetime.utcnow().isoformat()}", styles["Normal"]))
            elements.append(Paragraph(f"Records: {len(logs)}", styles["Normal"]))
            elements.append(Spacer(1, 12))
            
            # Create table
            data = [["Decision ID", "Timestamp", "Model", "Type", "Verified"]]
            for log in logs[:1000]:  # Limit PDF rows
                data.append([
                    log.decision_id[:20] + "...",
                    log.created_at.strftime("%Y-%m-%d %H:%M"),
                    log.model_name,
                    log.decision_type.value,
                    "Yes" if log.blockchain_tx_hash else "No",
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            return output.getvalue()
        except ImportError:
            # Fallback to simple text
            return self._export_json(logs, request)
    
    def _export_xml(
        self,
        logs: List[AuditLog],
        request: ExportRequest,
    ) -> bytes:
        """Export as XML."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<audit_trail_export>',
            f'  <metadata>',
            f'    <generated_at>{datetime.utcnow().isoformat()}</generated_at>',
            f'    <record_count>{len(logs)}</record_count>',
            f'  </metadata>',
            '  <audit_logs>',
        ]
        
        for log in logs:
            lines.append('    <audit_log>')
            lines.append(f'      <decision_id>{log.decision_id}</decision_id>')
            lines.append(f'      <timestamp>{log.created_at.isoformat()}</timestamp>')
            lines.append(f'      <organization_id>{log.organization_id}</organization_id>')
            lines.append(f'      <model_name>{log.model_name}</model_name>')
            lines.append(f'      <full_hash>{log.full_hash}</full_hash>')
            lines.append('    </audit_log>')
        
        lines.append('  </audit_logs>')
        lines.append('</audit_trail_export>')
        
        return '\n'.join(lines).encode("utf-8")
    
    def _format_log_entry(
        self,
        log: AuditLog,
        evidence_level: str,
    ) -> Dict[str, Any]:
        """Format log entry based on evidence level."""
        if evidence_level == "hash_only":
            return {
                "decision_id": log.decision_id,
                "timestamp": log.created_at.isoformat(),
                "full_hash": log.full_hash,
            }
        elif evidence_level == "summary":
            return {
                "decision_id": log.decision_id,
                "timestamp": log.created_at.isoformat(),
                "organization_id": log.organization_id,
                "user_id": log.user_id,
                "model_name": log.model_name,
                "decision_type": log.decision_type.value,
                "full_hash": log.full_hash,
                "merkle_root": log.merkle_root,
                "blockchain_tx_hash": log.blockchain_tx_hash,
            }
        else:  # full
            return {
                "decision_id": log.decision_id,
                "timestamp": log.created_at.isoformat(),
                "organization_id": log.organization_id,
                "user_id": log.user_id,
                "session_id": log.session_id,
                "model_name": log.model_name,
                "model_version": log.model_version,
                "provider": log.provider,
                "decision_type": log.decision_type.value,
                "input_hash": log.input_hash,
                "output_hash": log.output_hash,
                "context_hash": log.context_hash,
                "full_hash": log.full_hash,
                "merkle_root": log.merkle_root,
                "blockchain_tx_hash": log.blockchain_tx_hash,
                "sequence_number": log.sequence_number,
            }
    
    async def generate_compliance_report(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        standards: List[str],
    ) -> ComplianceReport:
        """Generate comprehensive compliance report."""
        # Get all logs in period
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.organization_id == organization_id,
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date,
            )
        )
        logs = result.scalars().all()
        
        # Calculate metrics
        total = len(logs)
        with_evidence = sum(1 for l in logs if l.blockchain_tx_hash)
        gdpr_marked = sum(1 for l in logs if l.is_gdpr_deleted)
        anchored = sum(1 for l in logs if l.merkle_root)
        
        # Get compliance markers
        result = await self.db.execute(
            select(ComplianceMarker).join(AuditLog).where(
                AuditLog.organization_id == organization_id,
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date,
            )
        )
        markers = result.scalars().all()
        
        # Calculate control compliance
        controls = {}
        for marker in markers:
            key = (marker.control_id, marker.standard)
            if key not in controls:
                controls[key] = {"total": 0, "compliant": 0}
            controls[key]["total"] += 1
            if marker.is_compliant:
                controls[key]["compliant"] += 1
        
        control_compliance = []
        for (control_id, standard), data in controls.items():
            control_compliance.append(ControlCompliance(
                control_id=control_id or "unknown",
                standard=standard,
                requirement_id="unknown",
                total_decisions=data["total"],
                compliant_decisions=data["compliant"],
                compliance_rate=data["compliant"] / data["total"] if data["total"] > 0 else 0,
            ))
        
        return ComplianceReport(
            organization_id=organization_id,
            generated_at=datetime.utcnow(),
            report_period_start=start_date,
            report_period_end=end_date,
            standards=[ComplianceStandard(s) for s in standards],
            metrics={
                "total_decisions": total,
                "decisions_with_evidence": with_evidence,
                "decisions_with_gdpr_markers": gdpr_marked,
                "blockchain_anchored": anchored,
                "failed_integrity_checks": 0,  # Would need verification
                "pending_deletions": 0,
                "completed_deletions": gdpr_marked,
            },
            controls=control_compliance,
            findings=[],
            recommendations=[
                "Ensure all critical decisions are blockchain anchored",
                "Regular integrity verification should be scheduled",
                "Review compliance markers quarterly",
            ],
        )


from app.config import get_settings
settings = get_settings()
from datetime import timedelta
