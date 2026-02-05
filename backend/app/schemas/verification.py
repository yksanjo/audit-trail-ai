"""Verification schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VerifyRequest(BaseModel):
    """Request to verify audit log integrity."""
    decision_id: Optional[str] = None
    audit_log_id: Optional[UUID] = None
    merkle_root: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    organization_id: Optional[str] = None


class MerkleProof(BaseModel):
    """Merkle proof for verification."""
    leaf_hash: str
    leaf_index: int
    proof_path: List[Dict[str, Any]]
    root_hash: str
    verified: bool


class BlockchainVerification(BaseModel):
    """Blockchain verification details."""
    chain_id: int
    tx_hash: str
    block_number: int
    block_hash: str
    timestamp: datetime
    verified: bool
    confirmations: int


class VerificationResult(BaseModel):
    """Individual verification result."""
    decision_id: str
    audit_log_id: UUID
    hash_verified: bool
    merkle_verified: bool
    blockchain_verified: bool
    tampered: bool
    details: Dict[str, Any]


class VerifyResponse(BaseModel):
    """Verification response."""
    verified: bool
    verification_time: datetime
    total_checked: int
    tampered_count: int
    results: List[VerificationResult]
    
    # Summary
    merkle_root: Optional[str]
    blockchain_tx_hash: Optional[str]
    integrity_score: float  # 0.0 to 1.0


class IntegrityReport(BaseModel):
    """Comprehensive integrity report."""
    generated_at: datetime
    organization_id: Optional[str]
    
    # Overall status
    overall_integrity: bool
    integrity_score: float
    
    # Checks performed
    hash_chain_verified: bool
    merkle_tree_verified: bool
    blockchain_anchors_verified: bool
    sequence_integrity_verified: bool
    
    # Statistics
    total_logs: int
    verified_logs: int
    tampered_logs: int
    missing_logs: int
    gdpr_deleted_logs: int
    
    # Details
    merkle_roots_checked: int
    blockchain_anchors_checked: int
    failed_verifications: List[Dict[str, Any]]
    
    # Recommendations
    recommendations: List[str]


class TamperAlert(BaseModel):
    """Alert for detected tampering."""
    alert_id: str
    detected_at: datetime
    severity: str  # low, medium, high, critical
    
    decision_id: str
    audit_log_id: UUID
    expected_hash: str
    actual_hash: str
    
    # Context
    merkle_root: Optional[str]
    blockchain_tx_hash: Optional[str]
    
    # Response
    auto_containment_triggered: bool
    notified_admins: List[str]
    incident_ticket_id: Optional[str]
