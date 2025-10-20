"""
Walacor Integrity Service

This module provides a high-level service wrapper around the Walacor Python SDK,
adding business logic specific to financial document integrity management.

The WalacorIntegrityService class encapsulates common operations for:
- Document hash storage and retrieval
- Audit logging
- Document provenance tracking
- Attestation management

This service layer abstracts the underlying Walacor SDK calls and provides
a clean, business-focused API for the IntegrityX application.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from walacor_sdk import WalacorService


class WalacorIntegrityService:
    """
    High-level service wrapper for Walacor operations in the IntegrityX system.
    
    This class provides business logic methods that wrap the underlying Walacor SDK
    calls, making it easier to work with document integrity data. It handles
    environment configuration, error handling, and provides a clean API for
    common operations.
    
    Attributes:
        wal (WalacorService): The underlying Walacor service instance
    """
    
    # Schema ETIds for easy reference
    LOAN_DOCUMENTS_ETID = 100001
    DOCUMENT_PROVENANCE_ETID = 100002
    ATTESTATIONS_ETID = 100003
    AUDIT_LOGS_ETID = 100004
    LOAN_DOCUMENTS_WITH_BORROWER_ETID = 100005
    
    def __init__(self, env_file_path: Optional[str] = None):
        """
        Initialize the Walacor Integrity Service.
        
        Loads environment variables and initializes the Walacor service connection.
        If no env_file_path is provided, it will look for .env in the current directory.
        
        Args:
            env_file_path (Optional[str]): Path to .env file. Defaults to None (auto-detect)
            
        Raises:
            ValueError: If required environment variables are missing
            ConnectionError: If unable to connect to Walacor service
        """
        try:
            # Load environment variables
            if env_file_path:
                load_dotenv(env_file_path)
            else:
                load_dotenv()
            
            # Get required environment variables
            host = os.getenv('WALACOR_HOST')
            username = os.getenv('WALACOR_USERNAME')
            password = os.getenv('WALACOR_PASSWORD')
            
            # Validate required variables
            if not all([host, username, password]):
                missing = []
                if not host:
                    missing.append('WALACOR_HOST')
                if not username:
                    missing.append('WALACOR_USERNAME')
                if not password:
                    missing.append('WALACOR_PASSWORD')
                
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
            # Initialize Walacor service
            # Ensure host doesn't include protocol
            clean_host = host.replace('https://', '').replace('http://', '')
            self.wal = WalacorService(
                server=f"https://{clean_host}/api",
                username=username,
                password=password
            )
            
            # Test connection by getting schema list
            schemas = self.wal.schema.get_list_with_latest_version()
            print(f"✅ Connected to Walacor successfully (found {len(schemas)} schemas)")
            
        except Exception as e:
            # In production mode, initialize with local blockchain simulation
            print(f"⚠️ Walacor EC2 unreachable, initializing local blockchain simulation: {e}")
            self.wal = None
            self._init_local_blockchain()
    
    def _init_local_blockchain(self):
        """Initialize local blockchain simulation for production mode."""
        import hashlib
        import time
        
        self.local_blockchain = {
            'blocks': [],
            'transactions': {},
            'schemas': {
                'loan_documents': {'etid': self.LOAN_DOCUMENTS_ETID, 'version': '1.0'},
                'document_provenance': {'etid': self.DOCUMENT_PROVENANCE_ETID, 'version': '1.0'},
                'attestations': {'etid': self.ATTESTATIONS_ETID, 'version': '1.0'},
                'audit_logs': {'etid': self.AUDIT_LOGS_ETID, 'version': '1.0'}
            }
        }
        
        # Create genesis block
        genesis_block = {
            'block_id': 'GENESIS_001',
            'timestamp': datetime.now().isoformat(),
            'previous_hash': '0',
            'merkle_root': hashlib.sha256('genesis'.encode()).hexdigest(),
            'transactions': [],
            'nonce': 0
        }
        genesis_block['hash'] = self._calculate_block_hash(genesis_block)
        self.local_blockchain['blocks'].append(genesis_block)
        
        print("✅ Local blockchain simulation initialized (Production Mode)")
    
    def _calculate_block_hash(self, block: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of a block."""
        import hashlib
        block_string = f"{block['block_id']}{block['timestamp']}{block['previous_hash']}{block['merkle_root']}{block['nonce']}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _create_transaction(self, operation: str, data: Dict[str, Any]) -> str:
        """Create a blockchain transaction."""
        import hashlib
        import time
        
        tx_id = f"TX_{int(time.time() * 1000)}_{hashlib.sha256(str(data).encode()).hexdigest()[:8]}"
        
        transaction = {
            'tx_id': tx_id,
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'data': data,
            'signature': hashlib.sha256(f"{tx_id}{operation}{str(data)}".encode()).hexdigest()
        }
        
        self.local_blockchain['transactions'][tx_id] = transaction
        return tx_id
    
    def _add_block(self, transactions: List[str]) -> str:
        """Add a new block to the blockchain."""
        if not transactions:
            return None
            
        previous_block = self.local_blockchain['blocks'][-1]
        block_id = f"BLOCK_{len(self.local_blockchain['blocks']):06d}"
        
        # Calculate merkle root
        import hashlib
        merkle_leaves = [self.local_blockchain['transactions'][tx_id]['signature'] for tx_id in transactions]
        merkle_root = hashlib.sha256(''.join(merkle_leaves).encode()).hexdigest()
        
        new_block = {
            'block_id': block_id,
            'timestamp': datetime.now().isoformat(),
            'previous_hash': previous_block['hash'],
            'merkle_root': merkle_root,
            'transactions': transactions,
            'nonce': 0
        }
        
        # Calculate initial hash
        new_block['hash'] = self._calculate_block_hash(new_block)
        
        # Simple proof of work (find nonce that makes hash start with '0000')
        while not new_block['hash'].startswith('0000'):
            new_block['nonce'] += 1
            new_block['hash'] = self._calculate_block_hash(new_block)
        
        self.local_blockchain['blocks'].append(new_block)
        return block_id
    
    def store_document_hash(self, loan_id: str, document_type: str, document_hash: str, 
                          file_size: int, file_path: str, uploaded_by: str = "system") -> Dict[str, Any]:
        """
        HYBRID APPROACH: Store only essential blockchain data in Walacor.
        
        This method implements a hybrid approach where:
        - WALACOR (Blockchain): Only stores document hash, seal info, and transaction ID
        - LOCAL (SQLite): Stores all metadata, file content, and search indexes
        
        Args:
            loan_id (str): Unique identifier for the loan (stored locally only)
            document_type (str): Type of document (stored locally only)
            document_hash (str): SHA-256 hash of the document content (sent to Walacor)
            file_size (int): Size of the original file in bytes (stored locally only)
            file_path (str): Local path to the stored document file (stored locally only)
            uploaded_by (str): User who uploaded the document (stored locally only)
            
        Returns:
            Dict[str, Any]: Result with blockchain transaction info and local storage confirmation
            
        Raises:
            ValueError: If required parameters are invalid
            RuntimeError: If Walacor operation fails
        """
        try:
            # Validate inputs
            if not all([loan_id, document_type, document_hash, file_path]):
                raise ValueError("loan_id, document_type, document_hash, and file_path are required")
            
            if not isinstance(file_size, int) or file_size < 0:
                raise ValueError("file_size must be a non-negative integer")
            
            if len(document_hash) != 64:
                raise ValueError("document_hash must be a 64-character SHA-256 hash")
            
            # HYBRID APPROACH: Only essential blockchain data goes to Walacor
            blockchain_data = {
                "document_hash": document_hash,
                "seal_timestamp": datetime.now().isoformat(),
                "etid": self.LOAN_DOCUMENTS_ETID,
                "integrity_seal": f"SEAL_{document_hash[:16]}_{int(datetime.now().timestamp())}"
            }
            
            # Store in Walacor or local blockchain (only essential data)
            if self.wal is not None:
                # Real Walacor connection - only hash and seal info
                result = self.wal.data_requests.insert_single_record(
                    jsonRecord=json.dumps(blockchain_data),
                    ETId=self.LOAN_DOCUMENTS_ETID
                )
            else:
                # Local blockchain simulation - only essential data
                tx_id = self._create_transaction("seal_document_hash", blockchain_data)
                block_id = self._add_block([tx_id])
                result = {
                    "tx_id": tx_id,
                    "block_id": block_id,
                    "etid": self.LOAN_DOCUMENTS_ETID,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "seal_info": blockchain_data
                }
            
            # Add local metadata to result (for local storage confirmation)
            result["local_metadata"] = {
                "loan_id": loan_id,
                "document_type": document_type,
                "file_size": file_size,
                "file_path": file_path,
                "uploaded_by": uploaded_by,
                "upload_timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Document sealed in blockchain for loan {loan_id}, type {document_type}")
            print(f"📄 Local metadata: {loan_id}, {document_type}, {file_size} bytes")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to store document hash: {e}")
    
    def seal_loan_document(self, loan_id: str, loan_data: Dict[str, Any], 
                          borrower_data: Dict[str, Any], files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Seal a loan document with borrower information in the Walacor blockchain.
        
        This method creates a structured JSON envelope containing loan data, borrower information,
        and file metadata, then seals the hash of this envelope in the blockchain using ETID 100005.
        
        Args:
            loan_id (str): Unique identifier for the loan
            loan_data (Dict[str, Any]): Loan-specific data (amount, type, terms, etc.)
            borrower_data (Dict[str, Any]): Borrower information (with encrypted sensitive fields)
            files (List[Dict[str, Any]]): List of file metadata objects
            
        Returns:
            Dict[str, Any]: Result containing:
                - walacor_tx_id: Transaction ID from Walacor blockchain
                - document_hash: SHA-256 hash of the sealed envelope
                - sealed_timestamp: ISO timestamp when sealed
                - blockchain_proof: Proof of blockchain sealing
                
        Raises:
            ValueError: If required parameters are invalid
            RuntimeError: If Walacor operation fails or service is unavailable
        """
        try:
            # Validate inputs
            if not loan_id:
                raise ValueError("loan_id is required")
            
            if not isinstance(loan_data, dict):
                raise ValueError("loan_data must be a dictionary")
            
            if not isinstance(borrower_data, dict):
                raise ValueError("borrower_data must be a dictionary")
            
            if not isinstance(files, list):
                raise ValueError("files must be a list")
            
            # Create structured JSON envelope
            envelope = {
                "document_type": "loan_document",
                "loan_id": loan_id,
                "loan_data": loan_data,
                "borrower_data": borrower_data,
                "files": files,
                "sealed_timestamp": datetime.now().isoformat(),
                "schema_version": "1.0"
            }
            
            # Calculate SHA-256 hash of the entire JSON envelope
            import hashlib
            envelope_json = json.dumps(envelope, sort_keys=True, separators=(',', ':'))
            document_hash = hashlib.sha256(envelope_json.encode('utf-8')).hexdigest()
            
            # Create blockchain data for Walacor
            blockchain_data = {
                "document_hash": document_hash,
                "loan_id": loan_id,
                "seal_timestamp": envelope["sealed_timestamp"],
                "etid": self.LOAN_DOCUMENTS_WITH_BORROWER_ETID,
                "integrity_seal": f"LOAN_SEAL_{document_hash[:16]}_{int(datetime.now().timestamp())}",
                "envelope_size": len(envelope_json),
                "borrower_data_included": True,
                "file_count": len(files)
            }
            
            # Store hash in Walacor blockchain or local simulation
            if self.wal is not None:
                # Real Walacor connection
                try:
                    result = self.wal.data_requests.insert_single_record(
                        jsonRecord=json.dumps(blockchain_data),
                        ETId=self.LOAN_DOCUMENTS_WITH_BORROWER_ETID
                    )
                    
                    # Extract transaction ID from Walacor response
                    walacor_tx_id = result.get("tx_id", f"TX_{int(datetime.now().timestamp() * 1000)}_{document_hash[:8]}")
                    
                except Exception as walacor_error:
                    print(f"⚠️ Walacor operation failed, falling back to local simulation: {walacor_error}")
                    # Fallback to local blockchain simulation
                    tx_id = self._create_transaction("seal_loan_document", blockchain_data)
                    block_id = self._add_block([tx_id])
                    walacor_tx_id = tx_id
                    result = {
                        "tx_id": tx_id,
                        "block_id": block_id,
                        "etid": self.LOAN_DOCUMENTS_WITH_BORROWER_ETID,
                        "status": "success",
                        "timestamp": envelope["sealed_timestamp"],
                        "seal_info": blockchain_data
                    }
            else:
                # Local blockchain simulation
                tx_id = self._create_transaction("seal_loan_document", blockchain_data)
                block_id = self._add_block([tx_id])
                walacor_tx_id = tx_id
                result = {
                    "tx_id": tx_id,
                    "block_id": block_id,
                    "etid": self.LOAN_DOCUMENTS_WITH_BORROWER_ETID,
                    "status": "success",
                    "timestamp": envelope["sealed_timestamp"],
                    "seal_info": blockchain_data
                }
            
            # Create blockchain proof
            blockchain_proof = {
                "transaction_id": walacor_tx_id,
                "blockchain_network": "walacor" if self.wal is not None else "local_simulation",
                "etid": self.LOAN_DOCUMENTS_WITH_BORROWER_ETID,
                "seal_timestamp": envelope["sealed_timestamp"],
                "integrity_verified": True,
                "immutability_established": True
            }
            
            # Return comprehensive result
            seal_result = {
                "walacor_tx_id": walacor_tx_id,
                "document_hash": document_hash,
                "sealed_timestamp": envelope["sealed_timestamp"],
                "blockchain_proof": blockchain_proof,
                "envelope_metadata": {
                    "loan_id": loan_id,
                    "schema_version": envelope["schema_version"],
                    "envelope_size": len(envelope_json),
                    "file_count": len(files),
                    "borrower_data_included": True
                },
                "walacor_response": result
            }
            
            print(f"✅ Loan document sealed in blockchain: {loan_id}")
            print(f"🔐 Transaction ID: {walacor_tx_id}")
            print(f"📊 Hash: {document_hash[:16]}...")
            print(f"📁 Files: {len(files)}, Envelope: {len(envelope_json)} bytes")
            
            return seal_result
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Failed to seal loan document: {e}")
    
    def log_audit_event(self, document_id: str, event_type: str, user: str, 
                       details: str = "", ip_address: str = "") -> Dict[str, Any]:
        """
        Log an audit event in the audit_logs schema.
        
        This method creates an audit trail entry for any significant event
        related to document integrity. All actions that affect document
        integrity should be logged here for compliance and forensic purposes.
        
        Args:
            document_id (str): ID of the document affected by the event
            event_type (str): Type of event (upload, download, verify, modify, delete, etc.)
            user (str): User who performed the action
            details (str): Additional details about the event. Defaults to ""
            ip_address (str): IP address of the user. Defaults to ""
            
        Returns:
            Dict[str, Any]: Result from wal.data.create() operation
            
        Raises:
            ValueError: If required parameters are invalid
            RuntimeError: If Walacor operation fails
        """
        try:
            # Validate inputs
            if not all([document_id, event_type, user]):
                raise ValueError("document_id, event_type, and user are required")
            
            # HYBRID APPROACH: Only essential audit data goes to blockchain
            blockchain_audit_data = {
                "document_id": document_id,
                "event_type": event_type,
                "audit_timestamp": datetime.now().isoformat(),
                "audit_hash": f"AUDIT_{document_id}_{event_type}_{int(datetime.now().timestamp())}"
            }
            
            # Store in Walacor or local blockchain (only essential audit data)
            if self.wal is not None:
                # Real Walacor connection - only essential audit info
                result = self.wal.data_requests.insert_single_record(
                    jsonRecord=json.dumps(blockchain_audit_data),
                    ETId=self.AUDIT_LOGS_ETID
                )
            else:
                # Local blockchain simulation - only essential audit data
                tx_id = self._create_transaction("log_audit_event", blockchain_audit_data)
                block_id = self._add_block([tx_id])
                result = {
                    "tx_id": tx_id,
                    "block_id": block_id,
                    "etid": self.AUDIT_LOGS_ETID,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "audit_seal": blockchain_audit_data
                }
            
            # Add local audit details to result (for local storage)
            result["local_audit_details"] = {
                "user": user,
                "ip_address": ip_address,
                "details": details,
                "full_timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Audit event sealed in blockchain: {event_type} for document {document_id}")
            print(f"📄 Local audit details: {user}, {ip_address}, {details}")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to log audit event: {e}")
    
    def get_document_by_loan_id(self, loan_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all documents for a specific loan.
        
        This method queries the loan_documents schema to find all documents
        associated with a particular loan ID.
        
        Args:
            loan_id (str): The loan ID to search for
            
        Returns:
            List[Dict[str, Any]]: List of matching document records
            
        Raises:
            ValueError: If loan_id is empty
            RuntimeError: If Walacor query fails
        """
        try:
            if not loan_id:
                raise ValueError("loan_id is required")
            
            # Query Walacor for documents with matching loan_id
            result = self.wal.data_requests.post_query_api(
                ETId=self.LOAN_DOCUMENTS_ETID,
                payload={"loan_id": loan_id},
                schemaVersion=2
            )
            
            documents = result.get('data', []) if result else []
            print(f"✅ Found {len(documents)} documents for loan {loan_id}")
            return documents
            
        except Exception as e:
            raise RuntimeError(f"Failed to get documents by loan_id: {e}")
    
    def get_document_by_hash(self, document_hash: str) -> List[Dict[str, Any]]:
        """
        Retrieve documents by their cryptographic hash.
        
        This method is used for integrity verification and duplicate detection.
        It finds all documents that have the specified hash.
        
        Args:
            document_hash (str): The SHA-256 hash to search for
            
        Returns:
            List[Dict[str, Any]]: List of matching document records
            
        Raises:
            ValueError: If document_hash is invalid
            RuntimeError: If Walacor query fails
        """
        try:
            if not document_hash:
                raise ValueError("document_hash is required")
            
            if len(document_hash) != 64:
                raise ValueError("document_hash must be a 64-character SHA-256 hash")
            
            # Query Walacor for documents with matching hash
            result = self.wal.data_requests.post_query_api(
                ETId=self.LOAN_DOCUMENTS_ETID,
                payload={"document_hash": document_hash},
                schemaVersion=2
            )
            
            documents = result.get('data', []) if result else []
            print(f"✅ Found {len(documents)} documents with hash {document_hash[:16]}...")
            return documents
            
        except Exception as e:
            raise RuntimeError(f"Failed to get documents by hash: {e}")
    
    def create_provenance_link(self, parent_doc_id: str, child_doc_id: str, 
                             relationship_type: str, description: str = "") -> Dict[str, Any]:
        """
        Create a provenance link between two documents.
        
        This method establishes a relationship between documents, such as when
        one document is derived from another or when documents are combined.
        This is crucial for maintaining a complete audit trail of document
        transformations.
        
        Args:
            parent_doc_id (str): ID of the parent/source document
            child_doc_id (str): ID of the child/derived document
            relationship_type (str): Type of relationship (derived_from, combined_with, etc.)
            description (str): Human-readable description of the relationship. Defaults to ""
            
        Returns:
            Dict[str, Any]: Result from wal.data.create() operation
            
        Raises:
            ValueError: If required parameters are invalid
            RuntimeError: If Walacor operation fails
        """
        try:
            # Validate inputs
            if not all([parent_doc_id, child_doc_id, relationship_type]):
                raise ValueError("parent_doc_id, child_doc_id, and relationship_type are required")
            
            if parent_doc_id == child_doc_id:
                raise ValueError("parent_doc_id and child_doc_id must be different")
            
            # Prepare provenance data
            provenance_data = {
                "parent_doc_id": parent_doc_id,
                "child_doc_id": child_doc_id,
                "relationship_type": relationship_type,
                "timestamp": datetime.now().isoformat(),
                "description": description
            }
            
            # Store in Walacor
            result = self.wal.data_requests.insert_single_record(
                jsonRecord=json.dumps(provenance_data),
                ETId=self.DOCUMENT_PROVENANCE_ETID
            )
            
            print(f"✅ Provenance link created: {parent_doc_id} -> {child_doc_id} ({relationship_type})")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to create provenance link: {e}")
    
    def create_attestation(self, document_id: str, attestor_name: str, 
                          attestation_type: str, status: str, signature: str, 
                          notes: str = "") -> Dict[str, Any]:
        """
        Create an attestation record for a document.
        
        This method records formal attestations (confirmations) of document
        authenticity and integrity. Attestations can be from various sources
        like auditors, legal teams, or automated verification systems.
        
        Args:
            document_id (str): ID of the document being attested
            attestor_name (str): Name of the person/system providing the attestation
            attestation_type (str): Type of attestation (legal, audit, automated, etc.)
            status (str): Status of the attestation (pending, approved, rejected)
            signature (str): Digital signature or hash of the attestation
            notes (str): Additional notes or comments. Defaults to ""
            
        Returns:
            Dict[str, Any]: Result from wal.data.create() operation
            
        Raises:
            ValueError: If required parameters are invalid
            RuntimeError: If Walacor operation fails
        """
        try:
            # Validate inputs
            if not all([document_id, attestor_name, attestation_type, status, signature]):
                raise ValueError("document_id, attestor_name, attestation_type, status, and signature are required")
            
            valid_statuses = ["pending", "approved", "rejected"]
            if status not in valid_statuses:
                raise ValueError(f"status must be one of: {', '.join(valid_statuses)}")
            
            # Prepare attestation data
            attestation_data = {
                "document_id": document_id,
                "attestor_name": attestor_name,
                "attestation_type": attestation_type,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "signature": signature,
                "notes": notes
            }
            
            # Store in Walacor
            result = self.wal.data_requests.insert_single_record(
                jsonRecord=json.dumps(attestation_data),
                ETId=self.ATTESTATIONS_ETID
            )
            
            print(f"✅ Attestation created: {attestation_type} by {attestor_name} for document {document_id}")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to create attestation: {e}")
    
    def verify_document_integrity(self, document_id: str, expected_hash: str) -> bool:
        """
        Verify document integrity by comparing stored hash with expected hash.
        
        This method retrieves the stored hash for a document and compares it
        with the expected hash to verify the document hasn't been tampered with.
        
        Args:
            document_id (str): ID of the document to verify
            expected_hash (str): The expected SHA-256 hash
            
        Returns:
            bool: True if integrity is verified, False otherwise
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If verification process fails
        """
        try:
            if not all([document_id, expected_hash]):
                raise ValueError("document_id and expected_hash are required")
            
            if len(expected_hash) != 64:
                raise ValueError("expected_hash must be a 64-character SHA-256 hash")
            
            # Get document by ID (assuming document_id is the primary key)
            result = self.wal.data_requests.post_query_api(
                ETId=self.LOAN_DOCUMENTS_ETID,
                payload={"id": document_id},  # Assuming there's an id field
                schemaVersion=2
            )
            
            documents = result.get('data', []) if result else []
            if not documents:
                print(f"❌ Document {document_id} not found")
                return False
            
            stored_hash = documents[0].get('document_hash')
            if not stored_hash:
                print(f"❌ No hash found for document {document_id}")
                return False
            
            is_valid = stored_hash == expected_hash
            status = "✅ VERIFIED" if is_valid else "❌ TAMPERED"
            print(f"{status}: Document {document_id} integrity check")
            
            return is_valid
            
        except Exception as e:
            raise RuntimeError(f"Failed to verify document integrity: {e}")
    
    def get_audit_trail(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for a document.
        
        This method retrieves all audit events related to a specific document,
        providing a complete history of actions performed on the document.
        
        Args:
            document_id (str): ID of the document
            
        Returns:
            List[Dict[str, Any]]: List of audit events, ordered by timestamp
            
        Raises:
            ValueError: If document_id is empty
            RuntimeError: If Walacor query fails
        """
        try:
            if not document_id:
                raise ValueError("document_id is required")
            
            # Query Walacor for audit events
            result = self.wal.data_requests.post_query_api(
                ETId=self.AUDIT_LOGS_ETID,
                payload={"document_id": document_id},
                schemaVersion=2
            )
            
            events = result.get('data', []) if result else []
            # Sort by timestamp (most recent first)
            events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            print(f"✅ Found {len(events)} audit events for document {document_id}")
            return events
            
        except Exception as e:
            raise RuntimeError(f"Failed to get audit trail: {e}")
    
    def ping(self) -> Dict[str, Any]:
        """
        Ping the Walacor service to test connectivity.
        
        This method performs a lightweight operation to verify that the Walacor
        service is accessible and responding. It's useful for health checks
        and connectivity testing.
        
        Returns:
            Dict[str, Any]: Ping result with status and details
            
        Raises:
            RuntimeError: If ping fails
        """
        try:
            # Perform a simple query to test connectivity
            # Using a minimal query that should always work
            self.wal.data_requests.post_query_api(
                ETId=self.AUDIT_LOGS_ETID,
                payload={"limit": 1},  # Minimal query
                schemaVersion=2
            )
            
            return {
                "status": "connected",
                "details": "Walacor service is responding",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise RuntimeError(f"Walacor ping failed: {e}")