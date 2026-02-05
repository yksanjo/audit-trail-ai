"""Blockchain anchoring models for immutable audit trails."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnchorStatus(str, PyEnum):
    """Status of blockchain anchor."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    FINALIZED = "FINALIZED"


class BlockchainAnchor(Base):
    """Blockchain anchor for Merkle root."""
    
    __tablename__ = "blockchain_anchors"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Anchor identification
    anchor_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Merkle root reference
    merkle_root_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("merkle_roots.id", ondelete="SET NULL"),
        nullable=True,
    )
    root_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    
    # Blockchain details
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    network_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Transaction details
    tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)
    block_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    block_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    gas_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gas_price_gwei: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Smart contract
    contract_address: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    event_data: Mapped[Optional[dict]] = mapped_column(nullable=True)
    
    # Status tracking
    status: Mapped[AnchorStatus] = mapped_column(
        Enum(AnchorStatus),
        default=AnchorStatus.PENDING,
        nullable=False,
    )
    
    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Retry tracking
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Verification
    verification_tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Relationship
    merkle_root: Mapped[Optional["MerkleRoot"]] = relationship(
        back_populates="blockchain_anchor",
        foreign_keys=[merkle_root_id],
    )
    
    __table_args__ = (
        Index("ix_blockchain_anchors_status", "status", "submitted_at"),
        Index("ix_blockchain_anchors_chain", "chain_id", "block_number"),
    )


class TombstoneRecord(Base):
    """Cryptographic tombstones for GDPR-compliant deletion."""
    
    __tablename__ = "tombstone_records"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Original record reference
    original_audit_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="SET NULL"),
        nullable=True,
    )
    original_decision_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Deletion metadata
    deleted_by: Mapped[str] = mapped_column(String(255), nullable=False)
    deletion_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    legal_basis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Cryptographic proof
    original_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    deletion_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    merkle_proof: Mapped[Optional[dict]] = mapped_column(nullable=True)
    
    # Blockchain anchor of deletion
    deletion_anchor_tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Retention
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    permanent_retention_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Verification
    deletion_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Notes
    auditor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_tombstones_created", "created_at"),
        Index("ix_tombstones_original_hash", "original_hash"),
    )
