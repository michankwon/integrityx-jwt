"""
Walacor Schema Definitions for Financial Document Integrity System

This module defines the database schemas used to store document integrity information
in Walacor. The schemas are designed to support cryptographic hash-based document
verification and audit trails.

Key Schemas:
- loan_documents: Stores document metadata and cryptographic hashes
- document_provenance: Tracks relationships between documents
- attestations: Records document attestations and signatures
- audit_logs: Maintains comprehensive audit trail
"""

from walacor_sdk.schema import (
    CreateSchemaRequest,
    CreateSchemaDefinition,
    CreateFieldRequest,
    CreateIndexRequest
)
from walacor_sdk.utils.enums import FieldType
from walacor_sdk import WalacorService
from typing import Any


class LoanSchemas:
    """
    Static class containing methods to create Walacor schemas for loan document integrity.
    
    This class provides methods to create the four core schemas needed for the
    financial document integrity system:
    1. loan_documents - Document metadata and hashes
    2. document_provenance - Document relationships
    3. attestations - Document attestations
    4. audit_logs - Audit trail
    """
    
    @staticmethod
    def create_loan_document_schema(wal: WalacorService) -> Any:
        """
        Create the loan_documents schema for storing document metadata and hashes.
        
        This schema stores only cryptographic hashes of documents, not the actual files.
        This allows for efficient storage and fast integrity verification of large documents.
        
        Schema Fields:
        - loan_id: Unique identifier for the loan
        - document_type: Type of document (contract, statement, etc.)
        - document_hash: SHA-256 hash of the document content
        - file_size: Size of the original file in bytes
        - upload_timestamp: When the document was uploaded
        - uploaded_by: User who uploaded the document
        - file_path: Local path to the stored document file
        
        Indexes:
        - loan_id: For fast lookup of all documents for a loan
        - document_hash: For integrity verification and duplicate detection
        
        Args:
            wal (WalacorService): Walacor service instance
            
        Returns:
            Any: Result of schema creation
        """
        schema_req = CreateSchemaRequest(
            ETId=50,
            SV=1,
            Schema=CreateSchemaDefinition(
                ETId=100001,
                TableName="loan_documents",
                Family="loan_integrity",
                Fields=[
                    CreateFieldRequest(
                        FieldName="loan_id",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="document_type",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="document_hash",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="file_size",
                        DataType=FieldType.INTEGER,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="upload_timestamp",
                        DataType=FieldType.DATETIME_EPOCH,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="uploaded_by",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="file_path",
                        DataType=FieldType.TEXT,
                        Required=True
                    )
                ],
                Indexes=[
                    CreateIndexRequest(
                        Fields=["loan_id"],
                        IndexValue="idx_loan_id"
                    ),
                    CreateIndexRequest(
                        Fields=["document_hash"],
                        IndexValue="idx_document_hash"
                    )
                ]
            )
        )
        
        return wal.schema.create_schema(schema_req)
    
    @staticmethod
    def create_provenance_schema(wal: WalacorService) -> Any:
        """
        Create the document_provenance schema for tracking document relationships.
        
        This schema tracks relationships between documents, such as when one document
        is derived from another, or when documents are combined or split. This is
        crucial for maintaining a complete audit trail of document transformations.
        
        Schema Fields:
        - parent_doc_id: ID of the parent/source document
        - child_doc_id: ID of the child/derived document
        - relationship_type: Type of relationship (derived_from, combined_with, etc.)
        - timestamp: When the relationship was established
        - description: Human-readable description of the relationship
        
        Indexes:
        - parent_doc_id: For finding all documents derived from a parent
        - child_doc_id: For finding the parent of a document
        
        Args:
            wal (WalacorService): Walacor service instance
            
        Returns:
            Any: Result of schema creation
        """
        schema_req = CreateSchemaRequest(
            ETId=50,
            SV=1,
            Schema=CreateSchemaDefinition(
                ETId=100002,
                TableName="document_provenance",
                Family="loan_integrity",
                Fields=[
                    CreateFieldRequest(
                        FieldName="parent_doc_id",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="child_doc_id",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="relationship_type",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="timestamp",
                        DataType=FieldType.DATETIME_EPOCH,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="description",
                        DataType=FieldType.TEXT,
                        Required=False
                    )
                ],
                Indexes=[
                    CreateIndexRequest(
                        Fields=["parent_doc_id"],
                        IndexValue="idx_parent_doc_id"
                    ),
                    CreateIndexRequest(
                        Fields=["child_doc_id"],
                        IndexValue="idx_child_doc_id"
                    )
                ]
            )
        )
        
        return wal.schema.create_schema(schema_req)
    
    @staticmethod
    def create_attestation_schema(wal: WalacorService) -> Any:
        """
        Create the attestations schema for recording document attestations and signatures.
        
        This schema stores attestations (formal confirmations) of document authenticity
        and integrity. Attestations can be from various sources like auditors, legal
        teams, or automated verification systems.
        
        Schema Fields:
        - document_id: ID of the document being attested
        - attestor_name: Name of the person/system providing the attestation
        - attestation_type: Type of attestation (legal, audit, automated, etc.)
        - status: Status of the attestation (pending, approved, rejected)
        - timestamp: When the attestation was made
        - signature: Digital signature or hash of the attestation
        - notes: Additional notes or comments about the attestation
        
        Indexes:
        - document_id: For finding all attestations for a document
        
        Args:
            wal (WalacorService): Walacor service instance
            
        Returns:
            Any: Result of schema creation
        """
        schema_req = CreateSchemaRequest(
            ETId=50,
            SV=1,
            Schema=CreateSchemaDefinition(
                ETId=100003,
                TableName="attestations",
                Family="loan_integrity",
                Fields=[
                    CreateFieldRequest(
                        FieldName="document_id",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="attestor_name",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="attestation_type",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="status",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="timestamp",
                        DataType=FieldType.DATETIME_EPOCH,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="signature",
                        DataType=FieldType.TEXT,
                        Required=False
                    ),
                    CreateFieldRequest(
                        FieldName="notes",
                        DataType=FieldType.TEXT,
                        Required=False
                    )
                ],
                Indexes=[
                    CreateIndexRequest(
                        Fields=["document_id"],
                        IndexValue="idx_document_id"
                    )
                ]
            )
        )
        
        return wal.schema.create_schema(schema_req)
    
    @staticmethod
    def create_audit_log_schema(wal: WalacorService) -> Any:
        """
        Create the audit_logs schema for maintaining comprehensive audit trails.
        
        This schema records all significant events related to documents, providing
        a complete audit trail for compliance and forensic purposes. Every action
        that affects document integrity is logged here.
        
        Schema Fields:
        - document_id: ID of the document affected by the event
        - event_type: Type of event (upload, download, verify, modify, delete, etc.)
        - user: User who performed the action
        - timestamp: When the event occurred
        - ip_address: IP address of the user (for security tracking)
        - details: Additional details about the event (JSON or text)
        
        Indexes:
        - document_id: For finding all events related to a document
        - timestamp: For time-based queries and reporting
        
        Args:
            wal (WalacorService): Walacor service instance
            
        Returns:
            Any: Result of schema creation
        """
        schema_req = CreateSchemaRequest(
            ETId=50,
            SV=1,
            Schema=CreateSchemaDefinition(
                ETId=100004,
                TableName="audit_logs",
                Family="loan_integrity",
                Fields=[
                    CreateFieldRequest(
                        FieldName="document_id",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="event_type",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="user",
                        DataType=FieldType.TEXT,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="timestamp",
                        DataType=FieldType.DATETIME_EPOCH,
                        Required=True
                    ),
                    CreateFieldRequest(
                        FieldName="ip_address",
                        DataType=FieldType.TEXT,
                        Required=False
                    ),
                    CreateFieldRequest(
                        FieldName="details",
                        DataType=FieldType.TEXT,
                        Required=False
                    )
                ],
                Indexes=[
                    CreateIndexRequest(
                        Fields=["document_id"],
                        IndexValue="idx_document_id"
                    ),
                    CreateIndexRequest(
                        Fields=["timestamp"],
                        IndexValue="idx_timestamp"
                    )
                ]
            )
        )
        
        return wal.schema.create_schema(schema_req)
    
    @staticmethod
    def create_all_schemas(wal: WalacorService) -> dict:
        """
        Create all loan document integrity schemas at once.
        
        This convenience method creates all four schemas in the correct order
        and returns a dictionary with the results.
        
        Args:
            wal (WalacorService): Walacor service instance
            
        Returns:
            dict: Dictionary containing results of all schema creations
        """
        results = {}
        
        try:
            print("Creating loan_documents schema...")
            results['loan_documents'] = LoanSchemas.create_loan_document_schema(wal)
            print("✅ loan_documents schema created")
        except Exception as e:
            print(f"❌ Failed to create loan_documents schema: {e}")
            results['loan_documents'] = None
        
        try:
            print("Creating document_provenance schema...")
            results['document_provenance'] = LoanSchemas.create_provenance_schema(wal)
            print("✅ document_provenance schema created")
        except Exception as e:
            print(f"❌ Failed to create document_provenance schema: {e}")
            results['document_provenance'] = None
        
        try:
            print("Creating attestations schema...")
            results['attestations'] = LoanSchemas.create_attestation_schema(wal)
            print("✅ attestations schema created")
        except Exception as e:
            print(f"❌ Failed to create attestations schema: {e}")
            results['attestations'] = None
        
        try:
            print("Creating audit_logs schema...")
            results['audit_logs'] = LoanSchemas.create_audit_log_schema(wal)
            print("✅ audit_logs schema created")
        except Exception as e:
            print(f"❌ Failed to create audit_logs schema: {e}")
            results['audit_logs'] = None
        
        return results
