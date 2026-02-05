"""Merkle tree models for cryptographic integrity."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MerkleNode(Base):
    """Individual node in the Merkle tree."""
    
    __tablename__ = "merkle_nodes"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Node identification
    node_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Node type
    is_leaf: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_root: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # References
    audit_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("audit_logs.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Tree structure
    left_child_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    right_child_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    parent_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    
    # Associated root
    root_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("merkle_roots.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Verification data
    proof_path: Mapped[Optional[list]] = mapped_column(nullable=True)
    
    __table_args__ = (
        Index("ix_merkle_nodes_level_pos", "level", "position"),
        Index("ix_merkle_nodes_root", "root_id"),
    )


class MerkleRoot(Base):
    """Root of a Merkle tree at a specific point in time."""
    
    __tablename__ = "merkle_roots"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Root identification
    root_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    
    # Tree metadata
    tree_depth: Mapped[int] = mapped_column(Integer, nullable=False)
    leaf_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Sequence range
    start_sequence: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    end_sequence: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Blockchain anchoring
    blockchain_anchor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("blockchain_anchors.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Status
    is_anchored: Mapped[bool] = mapped_column(default=False, nullable=False)
    anchored_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Verification
    verification_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    blockchain_anchor: Mapped[Optional["BlockchainAnchor"]] = relationship(
        back_populates="merkle_root",
        foreign_keys="BlockchainAnchor.merkle_root_id",
    )
    nodes: Mapped[list[MerkleNode]] = relationship("MerkleNode", back_populates=None)
    
    __table_args__ = (
        Index("ix_merkle_roots_created", "created_at"),
        Index("ix_merkle_roots_anchored", "is_anchored", "anchored_at"),
    )
