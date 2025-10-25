"""
SQLAlchemy models for the Walacor Financial Integrity Platform.

This module defines the database models for managing artifacts, files, and events
in the financial document integrity system. The models are designed to work with
both traditional SQL databases and can be extended for blockchain integration.

Models:
- Artifact: Main entity representing a loan document or packet
- ArtifactFile: Individual files within an artifact
- ArtifactEvent: Audit trail and event tracking for artifacts
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, Index, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column
from datetime import datetime, timezone
import uuid
from typing import List, Optional

Base = declarative_base()

# Constants for foreign key references
ARTIFACTS_TABLE = "artifacts.id"


class Artifact(Base):
    """
    Main artifact model representing a loan document or packet.
    
    An artifact is the primary entity in the system, representing either:
    - A JSON document containing loan data
    - A loan packet containing multiple files
    
    Attributes:
        id: Unique identifier (UUID4)
        loan_id: Loan identifier for grouping related artifacts
        artifact_type: Type of artifact ('json' or 'loan_packet')
        payload_sha256: SHA-256 hash of the main payload
        manifest_sha256: SHA-256 hash of the manifest (for loan packets)
        walacor_tx_id: Transaction ID from Walacor blockchain
        schema_version: Version of the schema used
        created_by: User or system that created the artifact
        created_at: Timestamp of creation
    """
    
    __tablename__ = 'artifacts'
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core fields
    loan_id = Column(String(255), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)  # 'json' or 'loan_packet'
    etid = Column(Integer, nullable=False)  # Entity Type ID for Walacor
    payload_sha256 = Column(String(64), nullable=False, index=True)
    manifest_sha256 = Column(String(64), nullable=True)
    walacor_tx_id = Column(String(255), nullable=False)
    schema_version = Column(String(20), default='1.0')
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Hybrid approach fields
    blockchain_seal = Column(String(255), nullable=True)  # Blockchain seal information
    local_metadata = Column(JSON, nullable=True)  # All local metadata (file_size, file_path, etc.)
    borrower_info = Column(JSON, nullable=True)  # Borrower information for loan documents
    signature_jwt = Column(Text, nullable=True)  # JWT signature for canonical payload
    
    # Relationships
    files = relationship("ArtifactFile", back_populates="artifact", cascade="all, delete-orphan")
    events = relationship("ArtifactEvent", back_populates="artifact", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_artifact_loan_type', 'loan_id', 'artifact_type'),
        Index('idx_artifact_created_at', 'created_at'),
        Index('idx_artifact_walacor_tx', 'walacor_tx_id'),
        Index('idx_artifact_etid_payload', 'etid', 'payload_sha256', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<Artifact(id='{self.id}', loan_id='{self.loan_id}', type='{self.artifact_type}')>"
    
    def to_dict(self) -> dict:
        """Convert artifact to dictionary representation."""
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'artifact_type': self.artifact_type,
            'etid': self.etid,
            'payload_sha256': self.payload_sha256,
            'manifest_sha256': self.manifest_sha256,
            'walacor_tx_id': self.walacor_tx_id,
            'schema_version': self.schema_version,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'blockchain_seal': self.blockchain_seal,
            'signature_jwt': self.signature_jwt,
            'local_metadata': self.local_metadata,
            'borrower_info': self.borrower_info,
            'files_count': len(self.files) if self.files else 0,
            'events_count': len(self.events) if self.events else 0
        }


class ArtifactFile(Base):
    """
    Model representing individual files within an artifact.
    
    For loan packets, this represents each file in the packet.
    For JSON artifacts, this might represent attached documents.
    
    Attributes:
        id: Unique identifier (UUID4)
        artifact_id: Foreign key to the parent artifact
        name: Original filename
        uri: URI or path to the file
        sha256: SHA-256 hash of the file content
        size_bytes: File size in bytes
        content_type: MIME type of the file
    """
    
    __tablename__ = 'artifact_files'
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    artifact_id = Column(String(36), ForeignKey('artifacts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # File metadata
    name = Column(String(500), nullable=False)
    uri = Column(Text, nullable=False)
    sha256 = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=True)
    
    # Relationships
    artifact = relationship("Artifact", back_populates="files")
    
    # Indexes
    __table_args__ = (
        Index('idx_file_sha256', 'sha256'),
        Index('idx_file_content_type', 'content_type'),
        Index('idx_file_size', 'size_bytes'),
    )
    
    def __repr__(self) -> str:
        return f"<ArtifactFile(id='{self.id}', name='{self.name}', size={self.size_bytes})>"
    
    def to_dict(self) -> dict:
        """Convert file to dictionary representation."""
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'name': self.name,
            'uri': self.uri,
            'sha256': self.sha256,
            'size_bytes': self.size_bytes,
            'content_type': self.content_type
        }


class ArtifactEvent(Base):
    """
    Model representing events and audit trail for artifacts.
    
    This model tracks all significant events that occur with an artifact,
    providing a complete audit trail for compliance and debugging.
    
    Attributes:
        id: Unique identifier (UUID4)
        artifact_id: Foreign key to the parent artifact
        event_type: Type of event ('uploaded', 'verified', 'attested', etc.)
        payload_json: JSON string containing event-specific data
        payload_sha256: SHA-256 hash of the payload (for integrity)
        walacor_tx_id: Transaction ID from Walacor blockchain
        created_by: User or system that triggered the event
        created_at: Timestamp of the event
    """
    
    __tablename__ = 'artifact_events'
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    artifact_id = Column(String(36), ForeignKey('artifacts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Event data
    event_type = Column(String(100), nullable=False)
    payload_json = Column(Text, nullable=True)
    payload_sha256 = Column(String(64), nullable=True)
    walacor_tx_id = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    artifact = relationship("Artifact", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index('idx_event_type', 'event_type'),
        Index('idx_event_created_at', 'created_at'),
        Index('idx_event_created_by', 'created_by'),
        Index('idx_event_walacor_tx', 'walacor_tx_id'),
        Index('idx_event_artifact_type', 'artifact_id', 'event_type'),
    )
    
    def __repr__(self) -> str:
        return f"<ArtifactEvent(id='{self.id}', type='{self.event_type}', artifact='{self.artifact_id}')>"
    
    def to_dict(self) -> dict:
        """Convert event to dictionary representation."""
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'event_type': self.event_type,
            'payload_json': self.payload_json,
            'payload_sha256': self.payload_sha256,
            'walacor_tx_id': self.walacor_tx_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Attestation(Base):
    """
    Model representing attestations for artifacts.
    
    Attestations are certifications or validations that can be applied to artifacts,
    such as quality checks, KYC verification, policy compliance, etc.
    
    Attributes:
        id: Unique identifier (auto-incrementing integer)
        artifact_id: Foreign key to the parent artifact
        etid: Entity Type ID for Walacor (e.g., ATTESTATION_ETID)
        kind: Type of attestation ('qc_check', 'kyc_passed', 'policy_ok', etc.)
        issued_by: User or service ID that issued the attestation
        details: Free-form metadata as JSON
        created_at: Timestamp of creation
    """
    
    __tablename__ = "attestations"
    
    # Primary key
    id = mapped_column(Integer, primary_key=True)
    
    # Foreign key
    artifact_id = mapped_column(ForeignKey(ARTIFACTS_TABLE, ondelete="CASCADE"), index=True, nullable=False)
    
    # Attestation data
    etid = mapped_column(String(120), nullable=False, index=True)  # e.g., ATTESTATION_ETID
    kind = mapped_column(String(64), nullable=False)  # "qc_check" | "kyc_passed" | "policy_ok" | ...
    issued_by = mapped_column(String(120), nullable=False)  # user or service id
    details = mapped_column(JSON, nullable=False, default=dict)  # free-form metadata
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    artifact = relationship("Artifact")
    
    # Indexes and constraints
    __table_args__ = (
        Index("ix_attestation_artifact_kind", "artifact_id", "kind"),
    )
    
    def __repr__(self) -> str:
        return f"<Attestation(id={self.id}, artifact_id='{self.artifact_id}', kind='{self.kind}')>"
    
    def to_dict(self) -> dict:
        """Convert attestation to dictionary representation."""
        return {
            'id': self.id,
            'artifact_id': self.artifact_id,
            'etid': self.etid,
            'kind': self.kind,
            'issued_by': self.issued_by,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProvenanceLink(Base):
    """
    Model representing provenance relationships between artifacts.
    
    Provenance links establish relationships between artifacts, such as:
    - A loan packet contains multiple documents
    - A document is derived from another document
    - A document supersedes a previous version
    
    Attributes:
        id: Unique identifier (auto-incrementing integer)
        parent_artifact_id: Foreign key to the parent artifact
        child_artifact_id: Foreign key to the child artifact
        relation: Type of relationship ('contains', 'derived_from', 'supersedes', etc.)
        created_at: Timestamp of creation
    """
    
    __tablename__ = "provenance_links"
    
    # Primary key
    id = mapped_column(Integer, primary_key=True)
    
    # Foreign keys
    parent_artifact_id = mapped_column(ForeignKey(ARTIFACTS_TABLE, ondelete="CASCADE"), index=True, nullable=False)
    child_artifact_id = mapped_column(ForeignKey(ARTIFACTS_TABLE, ondelete="CASCADE"), index=True, nullable=False, unique=False)
    
    # Relationship data
    relation = mapped_column(String(64), nullable=False)  # "contains" | "derived_from" | "supersedes" | ...
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    parent_artifact = relationship("Artifact", foreign_keys=[parent_artifact_id])
    child_artifact = relationship("Artifact", foreign_keys=[child_artifact_id])
    
    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint("parent_artifact_id", "child_artifact_id", name="uq_prov_parent_child"),
    )
    
    def __repr__(self) -> str:
        return f"<ProvenanceLink(id={self.id}, parent='{self.parent_artifact_id}', child='{self.child_artifact_id}', relation='{self.relation}')>"
    
    def to_dict(self) -> dict:
        """Convert provenance link to dictionary representation."""
        return {
            'id': self.id,
            'parent_artifact_id': self.parent_artifact_id,
            'child_artifact_id': self.child_artifact_id,
            'relation': self.relation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Database engine configuration
def create_database_engine(database_url: str, echo: bool = False):
    """
    Create a SQLAlchemy database engine.
    
    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements (for debugging)
        
    Returns:
        SQLAlchemy engine instance
    """
    return create_engine(database_url, echo=echo)


def create_tables(engine):
    """
    Create all tables defined in the models.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """
    Drop all tables defined in the models.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)


# Example usage and testing
if __name__ == "__main__":
    # Example database URL (SQLite for testing)
    DATABASE_URL = "sqlite:///./integrityx.db"
    
    # Create engine
    engine = create_database_engine(DATABASE_URL, echo=True)
    
    # Create tables
    print("Creating database tables...")
    create_tables(engine)
    print("✅ Tables created successfully!")
    
    # Example of creating an artifact
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a sample artifact
        artifact = Artifact(
            loan_id="LOAN_2024_001",
            artifact_type="loan_packet",
            etid=100001,  # Entity Type ID for loan packets
            payload_sha256="a1b2c3d4e5f6" * 8,  # 64 character hash
            manifest_sha256="f6e5d4c3b2a1" * 8,
            walacor_tx_id="WAL_TX_123456789",
            created_by="demo_user@integrityx.com"
        )
        
        session.add(artifact)
        session.commit()
        
        # Add a file to the artifact
        file = ArtifactFile(
            artifact_id=artifact.id,
            name="loan_agreement.pdf",
            uri="s3://integrityx-bucket/loans/LOAN_2024_001/loan_agreement.pdf",
            sha256="1234567890abcdef" * 4,  # 64 character hash
            size_bytes=1024000,
            content_type="application/pdf"
        )
        
        session.add(file)
        
        # Add an event
        event = ArtifactEvent(
            artifact_id=artifact.id,
            event_type="uploaded",
            payload_json='{"status": "success", "files_count": 1}',
            payload_sha256="abcdef1234567890" * 4,
            walacor_tx_id="WAL_TX_123456790",
            created_by="demo_user@integrityx.com"
        )
        
        session.add(event)
        session.commit()
        
        print("✅ Sample data created successfully!")
        print(f"Artifact: {artifact}")
        print(f"File: {file}")
        print(f"Event: {event}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()
