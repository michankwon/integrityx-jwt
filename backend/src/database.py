"""
Database service class for the Walacor Financial Integrity Platform.

This module provides a high-level interface for database operations using SQLAlchemy.
It includes methods for managing artifacts, files, and events with proper error handling
and context manager support.

Usage:
    with Database() as db:
        artifact_id = db.insert_artifact(...)
        file_id = db.insert_artifact_file(...)
        event_id = db.insert_event(...)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
try:
    from .models import Base, Artifact, ArtifactFile, ArtifactEvent
except ImportError:
    # Fallback for when running as script
    from models import Base, Artifact, ArtifactFile, ArtifactEvent
import os
from typing import Optional, List
import uuid
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_database_operation(operation: str, table: str, record_id: Optional[str] = None, 
                          latency_ms: Optional[float] = None, error: Optional[str] = None, **extra_fields):
    """Log a database operation with structured data."""
    import json
    
    log_entry = {
        'operation': operation,
        'table': table,
        'component': 'database',
    }
    
    if record_id:
        log_entry['record_id'] = record_id
    
    if latency_ms is not None:
        log_entry['latency_ms'] = round(latency_ms, 2)
    
    if error:
        log_entry['error'] = error
    
    # Add extra fields
    log_entry.update(extra_fields)
    
    # Log with appropriate level
    if error:
        logger.error(f"Database operation failed: {json.dumps(log_entry)}")
    else:
        logger.info(f"Database operation completed: {json.dumps(log_entry)}")


class Database:
    """
    Database service class for managing artifacts, files, and events.
    
    This class provides a high-level interface for database operations with
    automatic session management, error handling, and context manager support.
    
    Attributes:
        engine: SQLAlchemy engine instance
        session_factory: Session factory for creating database sessions
        session: Current database session
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the Database service.
        
        Args:
            db_url: Database connection URL. If None, will try to get from environment
                   variable DATABASE_URL or default to SQLite in-memory database.
        
        Raises:
            ValueError: If database URL cannot be determined
            SQLAlchemyError: If database connection fails
        """
        # Get database URL from parameter, environment, or default
        if db_url:
            self.db_url = db_url
        else:
            self.db_url = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        
        if not self.db_url:
            raise ValueError("Database URL must be provided either as parameter or DATABASE_URL environment variable")
        
        try:
            # Create engine
            self.engine = create_engine(
                self.db_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
            )
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.session: Optional[Session] = None
            
            logger.info(f"Database service initialized with URL: {self._mask_url(self.db_url)}")
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in database URL for logging."""
        if '@' in url:
            # Mask password in URL like postgresql://user:password@host/db
            parts = url.split('@')
            if len(parts) == 2:
                user_part = parts[0]
                if ':' in user_part:
                    user_pass = user_part.split(':')
                    if len(user_pass) == 3:  # protocol://user:pass
                        masked = f"{user_pass[0]}://{user_pass[1]}:****@{parts[1]}"
                        return masked
        return url
    
    def __enter__(self) -> 'Database':
        """Enter context manager and create session."""
        self.session = self.session_factory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close session."""
        if self.session:
            if exc_type:
                # Rollback on exception
                self.session.rollback()
                logger.warning(f"Database session rolled back due to exception: {exc_type.__name__}")
            else:
                # Commit on success
                self.session.commit()
                logger.debug("Database session committed successfully")
            
            self.session.close()
            self.session = None
    
    def _ensure_session(self) -> Session:
        """Ensure a database session is available."""
        if not self.session:
            self.session = self.session_factory()
        return self.session
    
    def insert_artifact(
        self,
        loan_id: str,
        artifact_type: str,
        etid: int,
        payload_sha256: str,
        walacor_tx_id: str,
        created_by: str,
        manifest_sha256: Optional[str] = None,
        blockchain_seal: Optional[str] = None,
        local_metadata: Optional[dict] = None,
        borrower_info: Optional[dict] = None
    ) -> str:
        """
        Insert a new artifact into the database.
        
        Args:
            loan_id: Loan identifier
            artifact_type: Type of artifact ('json' or 'loan_packet')
            etid: Entity Type ID for Walacor
            payload_sha256: SHA-256 hash of the payload
            walacor_tx_id: Walacor transaction ID
            created_by: User or system that created the artifact
            manifest_sha256: SHA-256 hash of the manifest (optional)
            blockchain_seal: Blockchain seal information (optional)
            local_metadata: Local metadata dictionary (optional)
            borrower_info: Borrower information dictionary (optional)
        
        Returns:
            str: The ID of the created artifact
        
        Raises:
            ValueError: If required parameters are missing or invalid
            IntegrityError: If database constraint violation occurs
            SQLAlchemyError: If database operation fails
        """
        if not all([loan_id, artifact_type, etid, payload_sha256, walacor_tx_id, created_by]):
            raise ValueError("loan_id, artifact_type, etid, payload_sha256, walacor_tx_id, and created_by are required")
        
        if artifact_type not in ['json', 'loan_packet']:
            raise ValueError("artifact_type must be 'json' or 'loan_packet'")
        
        if len(payload_sha256) != 64:
            raise ValueError("payload_sha256 must be a 64-character SHA-256 hash")
        
        try:
            session = self._ensure_session()
            
            # Check if artifact already exists
            existing_artifact = session.query(Artifact).filter(
                Artifact.etid == etid,
                Artifact.payload_sha256 == payload_sha256
            ).first()
            
            if existing_artifact:
                logger.info(f"Artifact already exists: {existing_artifact.id} for loan {loan_id}")
                
                # Update the existing artifact with new comprehensive document data if provided
                if local_metadata and local_metadata.get('comprehensive_document'):
                    existing_artifact.local_metadata = local_metadata
                    existing_artifact.walacor_tx_id = walacor_tx_id
                    existing_artifact.blockchain_seal = blockchain_seal
                    if borrower_info:
                        existing_artifact.borrower_info = borrower_info
                    session.commit()
                    logger.info(f"Updated existing artifact {existing_artifact.id} with comprehensive document data")
                
                return existing_artifact.id
            
            artifact = Artifact(
                id=str(uuid.uuid4()),
                loan_id=loan_id,
                artifact_type=artifact_type,
                etid=etid,
                payload_sha256=payload_sha256,
                manifest_sha256=manifest_sha256,
                walacor_tx_id=walacor_tx_id,
                created_by=created_by,
                blockchain_seal=blockchain_seal,
                local_metadata=local_metadata,
                borrower_info=borrower_info
            )
            
            session.add(artifact)
            session.flush()  # Get the ID without committing
            session.commit()  # Commit the transaction
            
            logger.info(f"Artifact created: {artifact.id} for loan {loan_id}")
            return artifact.id
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating artifact: {e}")
            session.rollback()
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating artifact: {e}")
            session.rollback()
            raise

    def update_artifact_signature(self, artifact_id: str, signature_jwt: str) -> None:
        """
        Update the JWT signature for an existing artifact.

        Args:
            artifact_id: The artifact identifier.
            signature_jwt: The JWT signature to store.
        """
        if not artifact_id:
            raise ValueError("artifact_id is required")
        if not signature_jwt:
            raise ValueError("signature_jwt is required")

        session = self._ensure_session()
        try:
            artifact = session.query(Artifact).filter(Artifact.id == artifact_id).one_or_none()
            if not artifact:
                raise ValueError(f"Artifact {artifact_id} not found")

            artifact.signature_jwt = signature_jwt
            session.commit()
            logger.info(f"Updated signature for artifact {artifact_id}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error updating artifact signature: {e}")
            raise
    
    def create_or_get_artifact(
        self,
        etid: int,
        payload_hash: str,
        external_uri: str,
        metadata: dict,
        loan_id: Optional[str] = None,
        artifact_type: str = 'json',
        created_by: str = 'system'
    ) -> str:
        """
        Create or get an existing artifact using UPSERT logic.
        
        This method implements an UPSERT operation that:
        1. Tries to find an existing artifact with the same (etid, payload_hash)
        2. If found, returns the existing artifact ID
        3. If not found, creates a new artifact and returns its ID
        
        The method ensures that the same payload hash for a given ETID always
        returns the same stable artifact ID, preventing duplicates.
        
        Args:
            etid: Entity Type ID for Walacor
            payload_hash: SHA-256 hash of the payload
            external_uri: External URI where the artifact is stored
            metadata: Dictionary containing additional metadata
            loan_id: Loan identifier (optional, will be generated if not provided)
            artifact_type: Type of artifact ('json' or 'loan_packet')
            created_by: User or system that created the artifact
        
        Returns:
            str: The stable artifact ID (either existing or newly created)
        
        Raises:
            ValueError: If required parameters are missing or invalid
            SQLAlchemyError: If database operation fails
        """
        start_time = time.time()
        
        if not all([etid, payload_hash, external_uri]):
            raise ValueError("etid, payload_hash, and external_uri are required")
        
        if len(payload_hash) != 64:
            raise ValueError("payload_hash must be a 64-character SHA-256 hash")
        
        if artifact_type not in ['json', 'loan_packet']:
            raise ValueError("artifact_type must be 'json' or 'loan_packet'")
        
        try:
            session = self._ensure_session()
            
            # First, try to find existing artifact with same (etid, payload_hash)
            existing_artifact = session.query(Artifact).filter(
                Artifact.etid == etid,
                Artifact.payload_sha256 == payload_hash
            ).first()
            
            if existing_artifact:
                logger.info(f"Found existing artifact: {existing_artifact.id} for etid={etid}, hash={payload_hash[:16]}...")
                
                # Log successful retrieval
                latency_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    operation="select",
                    table="artifacts",
                    record_id=existing_artifact.id,
                    latency_ms=latency_ms,
                    etid=etid,
                    hash_prefix=payload_hash[:8],
                    action="found_existing"
                )
                
                return existing_artifact.id
            
            # No existing artifact found, create a new one
            logger.info(f"Creating new artifact for etid={etid}, hash={payload_hash[:16]}...")
            
            # Generate loan_id if not provided
            if not loan_id:
                loan_id = f"LOAN_{etid}_{payload_hash[:8].upper()}"
            
            # Generate Walacor transaction ID
            walacor_tx_id = f"WAL_TX_{etid}_{payload_hash[:8].upper()}"
            
            # Extract manifest_sha256 from metadata if present
            manifest_sha256 = metadata.get('manifest_sha256') if isinstance(metadata, dict) else None
            
            # Create new artifact
            artifact = Artifact(
                id=str(uuid.uuid4()),
                loan_id=loan_id,
                artifact_type=artifact_type,
                etid=etid,
                payload_sha256=payload_hash,
                manifest_sha256=manifest_sha256,
                walacor_tx_id=walacor_tx_id,
                created_by=created_by
            )
            
            session.add(artifact)
            session.flush()  # Get the ID without committing
            session.commit()  # Commit the transaction
            
            # Log the creation
            logger.info(f"Artifact created: {artifact.id} for etid={etid}, loan={loan_id}")
            
            # Log successful creation
            latency_ms = (time.time() - start_time) * 1000
            log_database_operation(
                operation="insert",
                table="artifacts",
                record_id=artifact.id,
                latency_ms=latency_ms,
                etid=etid,
                hash_prefix=payload_hash[:8],
                action="created_new"
            )
            
            return artifact.id
            
        except IntegrityError as e:
            # Handle race condition where another process created the same artifact
            logger.warning(f"Integrity error during UPSERT, retrying: {e}")
            session.rollback()
            
            # Retry by querying again
            existing_artifact = session.query(Artifact).filter(
                Artifact.etid == etid,
                Artifact.payload_sha256 == payload_hash
            ).first()
            
            if existing_artifact:
                logger.info(f"Found existing artifact on retry: {existing_artifact.id}")
                
                # Log successful retry
                latency_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    operation="select",
                    table="artifacts",
                    record_id=existing_artifact.id,
                    latency_ms=latency_ms,
                    etid=etid,
                    hash_prefix=payload_hash[:8],
                    action="found_existing_retry"
                )
                
                return existing_artifact.id
            else:
                logger.error(f"Failed to create or find artifact after retry: {e}")
                
                # Log retry failure
                latency_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    operation="upsert",
                    table="artifacts",
                    latency_ms=latency_ms,
                    etid=etid,
                    hash_prefix=payload_hash[:8],
                    error=str(e),
                    action="retry_failed"
                )
                
                raise
                
        except SQLAlchemyError as e:
            logger.error(f"Database error during UPSERT: {e}")
            
            # Log database error
            latency_ms = (time.time() - start_time) * 1000
            log_database_operation(
                operation="upsert",
                table="artifacts",
                latency_ms=latency_ms,
                etid=etid,
                hash_prefix=payload_hash[:8],
                error=str(e),
                action="database_error"
            )
            
            raise
    
    def insert_artifact_file(
        self,
        artifact_id: str,
        name: str,
        uri: str,
        sha256: str,
        size_bytes: int,
        content_type: Optional[str] = None
    ) -> str:
        """
        Insert a new artifact file into the database.
        
        Args:
            artifact_id: ID of the parent artifact
            name: Original filename
            uri: URI or path to the file
            sha256: SHA-256 hash of the file content
            size_bytes: File size in bytes
            content_type: MIME type of the file (optional)
        
        Returns:
            str: The ID of the created file
        
        Raises:
            ValueError: If required parameters are missing or invalid
            IntegrityError: If database constraint violation occurs
            SQLAlchemyError: If database operation fails
        """
        if not all([artifact_id, name, uri, sha256, size_bytes is not None]):
            raise ValueError("artifact_id, name, uri, sha256, and size_bytes are required")
        
        if len(sha256) != 64:
            raise ValueError("sha256 must be a 64-character SHA-256 hash")
        
        if size_bytes < 0:
            raise ValueError("size_bytes must be non-negative")
        
        try:
            session = self._ensure_session()
            
            artifact_file = ArtifactFile(
                id=str(uuid.uuid4()),
                artifact_id=artifact_id,
                name=name,
                uri=uri,
                sha256=sha256,
                size_bytes=size_bytes,
                content_type=content_type
            )
            
            session.add(artifact_file)
            session.flush()  # Get the ID without committing
            session.commit()  # Commit the transaction
            
            logger.info(f"Artifact file created: {artifact_file.id} for artifact {artifact_id}")
            return artifact_file.id
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating artifact file: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating artifact file: {e}")
            raise
    
    def insert_event(
        self,
        artifact_id: str,
        event_type: str,
        created_by: str,
        payload_json: Optional[str] = None,
        payload_sha256: Optional[str] = None,
        walacor_tx_id: Optional[str] = None
    ) -> str:
        """
        Insert a new artifact event into the database.
        
        Args:
            artifact_id: ID of the parent artifact
            event_type: Type of event (e.g., 'uploaded', 'verified', 'attested')
            created_by: User or system that triggered the event
            payload_json: JSON string containing event-specific data (optional)
            payload_sha256: SHA-256 hash of the payload (optional)
            walacor_tx_id: Walacor transaction ID (optional)
        
        Returns:
            str: The ID of the created event
        
        Raises:
            ValueError: If required parameters are missing or invalid
            IntegrityError: If database constraint violation occurs
            SQLAlchemyError: If database operation fails
        """
        if not all([artifact_id, event_type, created_by]):
            raise ValueError("artifact_id, event_type, and created_by are required")
        
        if payload_sha256 and len(payload_sha256) != 64:
            raise ValueError("payload_sha256 must be a 64-character SHA-256 hash")
        
        try:
            session = self._ensure_session()
            
            artifact_event = ArtifactEvent(
                id=str(uuid.uuid4()),
                artifact_id=artifact_id,
                event_type=event_type,
                payload_json=payload_json,
                payload_sha256=payload_sha256,
                walacor_tx_id=walacor_tx_id,
                created_by=created_by
            )
            
            session.add(artifact_event)
            session.flush()  # Get the ID without committing
            session.commit()  # Commit the transaction
            
            logger.info(f"Artifact event created: {artifact_event.id} for artifact {artifact_id}")
            return artifact_event.id
            
        except IntegrityError as e:
            logger.error(f"Integrity error creating artifact event: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating artifact event: {e}")
            raise
    
    def get_artifact_by_id(self, artifact_id: str) -> Optional[Artifact]:
        """
        Get an artifact by its ID with eager loading of related files and events.
        
        Args:
            artifact_id: The ID of the artifact to retrieve
        
        Returns:
            Optional[Artifact]: The artifact with loaded relationships, or None if not found
        
        Raises:
            ValueError: If artifact_id is empty
            SQLAlchemyError: If database operation fails
        """
        if not artifact_id:
            raise ValueError("artifact_id is required")
        
        try:
            session = self._ensure_session()
            
            artifact = session.query(Artifact)\
                .options(
                    joinedload(Artifact.files),
                    joinedload(Artifact.events)
                )\
                .filter(Artifact.id == artifact_id)\
                .first()
            
            if artifact:
                logger.debug(f"Retrieved artifact: {artifact_id}")
            else:
                logger.debug(f"Artifact not found: {artifact_id}")
            
            return artifact
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving artifact {artifact_id}: {e}")
            raise
    
    def get_all_artifacts(self) -> List[Artifact]:
        """
        Get all artifacts from the database with eager loading of related files and events.
        
        Returns:
            List[Artifact]: List of all artifacts with loaded relationships
        
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            session = self._ensure_session()
            
            artifacts = session.query(Artifact)\
                .options(
                    joinedload(Artifact.files),
                    joinedload(Artifact.events)
                )\
                .order_by(Artifact.created_at.desc())\
                .all()
            
            logger.debug(f"Retrieved {len(artifacts)} artifacts")
            return artifacts
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving all artifacts: {e}")
            raise

    def get_artifact_by_loan_id(self, loan_id: str) -> List[Artifact]:
        """
        Get all artifacts for a specific loan ID.
        
        Args:
            loan_id: The loan ID to search for
        
        Returns:
            List[Artifact]: List of artifacts for the loan, ordered by creation date
        
        Raises:
            ValueError: If loan_id is empty
            SQLAlchemyError: If database operation fails
        """
        if not loan_id:
            raise ValueError("loan_id is required")
        
        try:
            session = self._ensure_session()
            
            artifacts = session.query(Artifact)\
                .filter(Artifact.loan_id == loan_id)\
                .order_by(Artifact.created_at.desc())\
                .all()
            
            logger.debug(f"Retrieved {len(artifacts)} artifacts for loan {loan_id}")
            return artifacts
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving artifacts for loan {loan_id}: {e}")
            raise
    
    def get_artifact_by_hash(self, payload_sha256: str) -> Optional[Artifact]:
        """
        Get an artifact by its payload SHA-256 hash.
        
        Args:
            payload_sha256: The SHA-256 hash to search for
        
        Returns:
            Optional[Artifact]: The first matching artifact, or None if not found
        
        Raises:
            ValueError: If payload_sha256 is empty or invalid
            SQLAlchemyError: If database operation fails
        """
        if not payload_sha256:
            raise ValueError("payload_sha256 is required")
        
        if len(payload_sha256) != 64:
            raise ValueError("payload_sha256 must be a 64-character SHA-256 hash")
        
        try:
            session = self._ensure_session()
            
            artifact = session.query(Artifact)\
                .filter(Artifact.payload_sha256 == payload_sha256)\
                .first()
            
            if artifact:
                logger.debug(f"Retrieved artifact by hash: {payload_sha256[:16]}...")
            else:
                logger.debug(f"Artifact not found for hash: {payload_sha256[:16]}...")
            
            return artifact
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving artifact by hash: {e}")
            raise
    
    def get_artifact_events(self, artifact_id: str) -> List[ArtifactEvent]:
        """
        Get all events for a specific artifact, ordered by creation date.
        
        Args:
            artifact_id: The ID of the artifact
        
        Returns:
            List[ArtifactEvent]: List of events for the artifact, ordered by creation date
        
        Raises:
            ValueError: If artifact_id is empty
            SQLAlchemyError: If database operation fails
        """
        if not artifact_id:
            raise ValueError("artifact_id is required")
        
        try:
            session = self._ensure_session()
            
            events = session.query(ArtifactEvent)\
                .filter(ArtifactEvent.artifact_id == artifact_id)\
                .order_by(ArtifactEvent.created_at.asc())\
                .all()
            
            logger.debug(f"Retrieved {len(events)} events for artifact {artifact_id}")
            return events
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving events for artifact {artifact_id}: {e}")
            raise
    
    def close(self):
        """Close the current database session."""
        if self.session:
            self.session.close()
            self.session = None
            logger.debug("Database session closed")
    
    def health_check(self) -> bool:
        """
        Perform a health check on the database connection.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            session = self._ensure_session()
            # Simple query to test connection
            session.execute(text("SELECT 1"))
            logger.debug("Database health check passed")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """
        Get information about the database connection and tables.
        
        Returns:
            dict: Database information including URL, table counts, etc.
        """
        try:
            session = self._ensure_session()
            
            # Get table counts
            artifact_count = session.query(Artifact).count()
            file_count = session.query(ArtifactFile).count()
            event_count = session.query(ArtifactEvent).count()
            
            return {
                'database_url': self._mask_url(self.db_url),
                'engine_name': self.engine.name,
                'table_counts': {
                    'artifacts': artifact_count,
                    'artifact_files': file_count,
                    'artifact_events': event_count
                },
                'total_records': artifact_count + file_count + event_count
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting database info: {e}")
            return {
                'database_url': self._mask_url(self.db_url),
                'error': str(e)
            }

    # ============================================================================
    # COMPLIANCE AUDIT LOGGING METHODS
    # ============================================================================
    
    def log_document_upload(self, artifact_id: str, user_id: str, borrower_name: str, 
                           loan_id: str, ip_address: Optional[str] = None, 
                           user_agent: Optional[str] = None) -> str:
        """
        Log a document upload event for compliance auditing.
        
        Args:
            artifact_id: ID of the uploaded artifact
            user_id: ID of the user who uploaded the document
            borrower_name: Name of the borrower (for audit trail)
            loan_id: ID of the loan document
            ip_address: IP address of the uploader (optional)
            user_agent: User agent string (optional)
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "borrower_name": borrower_name,
            "loan_id": loan_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "action_details": {
                "action": "document_upload",
                "document_type": "loan_document",
                "contains_borrower_data": True
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="borrower_data_submitted",
            created_by=user_id,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )
    
    def log_borrower_data_access(self, artifact_id: str, accessed_by: str, 
                                access_reason: str, ip_address: Optional[str] = None) -> str:
        """
        Log access to borrower data for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact containing borrower data
            accessed_by: ID or email of the person accessing the data
            access_reason: Reason for accessing the data (e.g., 'verification', 'audit')
            ip_address: IP address of the requester (optional)
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accessed_by": accessed_by,
            "access_reason": access_reason,
            "ip_address": ip_address,
            "action_details": {
                "action": "borrower_data_access",
                "data_types_accessed": ["personal_info", "contact_info", "identity_info"],
                "compliance_purpose": access_reason
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="borrower_data_accessed",
            created_by=accessed_by,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )
    
    def log_verification_attempt(self, artifact_id: str, verifier_email: str, 
                                result: str, ip_address: Optional[str] = None) -> str:
        """
        Log a document verification attempt for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact being verified
            verifier_email: Email of the person performing verification
            result: Result of verification ('success', 'failed', 'error')
            ip_address: IP address of the verifier (optional)
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verifier_email": verifier_email,
            "verification_result": result,
            "ip_address": ip_address,
            "action_details": {
                "action": "document_verification",
                "verification_type": "blockchain_integrity_check",
                "compliance_requirement": "document_authenticity"
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="document_verified",
            created_by=verifier_email,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )
    
    def log_data_modification(self, artifact_id: str, field_changed: str, 
                             old_value_hash: str, new_value_hash: str, 
                             modified_by: str) -> str:
        """
        Log data modification for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact being modified
            field_changed: Name of the field that was changed
            old_value_hash: SHA-256 hash of the old value
            new_value_hash: SHA-256 hash of the new value
            modified_by: ID of the user who made the modification
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modified_by": modified_by,
            "field_changed": field_changed,
            "old_value_hash": old_value_hash,
            "new_value_hash": new_value_hash,
            "action_details": {
                "action": "data_modification",
                "change_type": "field_update",
                "compliance_impact": "audit_trail_required"
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="data_modification",
            created_by=modified_by,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )
    
    def log_blockchain_seal(self, artifact_id: str, walacor_tx_id: str, 
                           data_hash: str, sealed_by: str) -> str:
        """
        Log blockchain sealing for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact being sealed
            walacor_tx_id: Walacor transaction ID
            data_hash: SHA-256 hash of the sealed data
            sealed_by: ID of the user who initiated the sealing
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sealed_by": sealed_by,
            "walacor_tx_id": walacor_tx_id,
            "data_hash": data_hash,
            "action_details": {
                "action": "blockchain_sealing",
                "blockchain_network": "walacor",
                "immutability_established": True,
                "compliance_requirement": "document_integrity"
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="blockchain_sealed",
            created_by=sealed_by,
            payload_json=json.dumps(payload, separators=(',', ':')),
            walacor_tx_id=walacor_tx_id
        )
    
    def log_sensitive_data_viewed(self, artifact_id: str, viewer_id: str, 
                                 data_types: List[str], ip_address: Optional[str] = None) -> str:
        """
        Log viewing of sensitive data for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact containing sensitive data
            viewer_id: ID of the person viewing the data
            data_types: List of sensitive data types viewed (e.g., ['ssn', 'email', 'phone'])
            ip_address: IP address of the viewer (optional)
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "viewer_id": viewer_id,
            "data_types_viewed": data_types,
            "ip_address": ip_address,
            "action_details": {
                "action": "sensitive_data_view",
                "privacy_impact": "high",
                "compliance_requirement": "data_access_logging"
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="sensitive_data_viewed",
            created_by=viewer_id,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )
    
    def log_audit_trail_export(self, artifact_id: str, exported_by: str, 
                              export_format: str, ip_address: Optional[str] = None) -> str:
        """
        Log audit trail export for compliance auditing.
        
        Args:
            artifact_id: ID of the artifact whose audit trail was exported
            exported_by: ID of the person who exported the audit trail
            export_format: Format of the export (e.g., 'pdf', 'json', 'csv')
            ip_address: IP address of the exporter (optional)
        
        Returns:
            str: ID of the created audit event
        """
        import json
        from datetime import datetime, timezone
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exported_by": exported_by,
            "export_format": export_format,
            "ip_address": ip_address,
            "action_details": {
                "action": "audit_trail_export",
                "compliance_purpose": "regulatory_reporting",
                "data_retention": "permanent"
            }
        }
        
        return self.insert_event(
            artifact_id=artifact_id,
            event_type="audit_trail_exported",
            created_by=exported_by,
            payload_json=json.dumps(payload, separators=(',', ':'))
        )


# Example usage and testing
if __name__ == "__main__":
    # Test the Database class
    print("🗄️  DATABASE SERVICE TEST")
    print("=" * 50)
    
    try:
        # Test with context manager
        with Database() as db:
            print("✅ Database service initialized")
            
            # Test health check
            if db.health_check():
                print("✅ Database health check passed")
            else:
                print("❌ Database health check failed")
            
            # Test artifact creation
            artifact_id = db.insert_artifact(
                loan_id="LOAN_2024_001",
                artifact_type="loan_packet",
                payload_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                walacor_tx_id="WAL_TX_123456789",
                created_by="demo_user@integrityx.com",
                manifest_sha256="f6e5d4c3b2a1789012345678901234567890abcdef1234567890abcdef123456"
            )
            print(f"✅ Artifact created: {artifact_id}")
            
            # Test file creation
            file_id = db.insert_artifact_file(
                artifact_id=artifact_id,
                name="loan_agreement.pdf",
                uri="s3://integrityx-bucket/loans/LOAN_2024_001/loan_agreement.pdf",
                sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                size_bytes=1024000,
                content_type="application/pdf"
            )
            print(f"✅ File created: {file_id}")
            
            # Test event creation
            event_id = db.insert_event(
                artifact_id=artifact_id,
                event_type="uploaded",
                created_by="demo_user@integrityx.com",
                payload_json='{"status": "success", "files_count": 1}',
                payload_sha256="eventabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345",
                walacor_tx_id="WAL_TX_123456790"
            )
            print(f"✅ Event created: {event_id}")
            
            # Test retrieval
            artifact = db.get_artifact_by_id(artifact_id)
            if artifact:
                print(f"✅ Artifact retrieved: {artifact.loan_id}")
                print(f"   Files: {len(artifact.files)}")
                print(f"   Events: {len(artifact.events)}")
            
            # Test query by loan ID
            loan_artifacts = db.get_artifact_by_loan_id("LOAN_2024_001")
            print(f"✅ Found {len(loan_artifacts)} artifacts for loan")
            
            # Test query by hash
            hash_artifact = db.get_artifact_by_hash("a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456")
            if hash_artifact:
                print(f"✅ Artifact found by hash: {hash_artifact.id}")
            
            # Test events retrieval
            events = db.get_artifact_events(artifact_id)
            print(f"✅ Retrieved {len(events)} events")
            
            # Test database info
            db_info = db.get_database_info()
            print(f"✅ Database info: {db_info['table_counts']}")
        
        print("\n✅ All database operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
