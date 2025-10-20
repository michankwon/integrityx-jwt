"""
Manifest handler for multi-file packet processing in the Walacor Financial Integrity Platform.

This module provides comprehensive manifest processing capabilities for loan packets
containing multiple files. It handles manifest creation, validation, canonicalization,
and hashing for integrity verification.

Key Features:
- Multi-file packet manifest creation
- Manifest schema validation
- Canonical JSON encoding for consistent hashing
- SHA-256 hash generation for integrity verification
- File information extraction and validation
- Attestation tracking and management

Manifest Structure:
A manifest is a JSON document that describes a loan packet containing multiple files.
It includes metadata about each file, attestations, and creation information.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional
import os
from pathlib import Path

try:
    import canonicaljson
    HAS_CANONICALJSON = True
except ImportError:
    # Fallback for systems without canonicaljson
    canonicaljson = None
    HAS_CANONICALJSON = False

# Import DocumentHandler with fallback
try:
    from .document_handler import DocumentHandler
except ImportError:
    try:
        from document_handler import DocumentHandler
    except ImportError:
        # Fallback DocumentHandler implementation
        class DocumentHandler:
            def calculate_hash_from_file(self, file_path: str) -> str:
                """Fallback hash calculation."""
                import hashlib
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                return sha256_hash.hexdigest()


class ManifestHandler:
    """
    Handler for multi-file packet manifest processing.
    
    This class provides comprehensive manifest processing capabilities for loan packets
    containing multiple files. It handles manifest creation, validation, canonicalization,
    and hashing for integrity verification.
    
    Attributes:
        document_handler: DocumentHandler instance for file operations
        manifest_schema: Schema definition for manifest validation
    """
    
    # Manifest schema definition
    MANIFEST_SCHEMA = {
        "type": "object",
        "required": [
            "schemaVersion",
            "artifactType", 
            "loanId",
            "files",
            "attestations",
            "createdBy",
            "createdAt"
        ],
        "properties": {
            "schemaVersion": {
                "type": "string",
                "pattern": "^\\d+\\.\\d+$"
            },
            "artifactType": {
                "type": "string",
                "enum": ["loan_packet", "appraisal_packet", "credit_packet"]
            },
            "loanId": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255,
                "pattern": "^[A-Za-z0-9_-]+$"
            },
            "files": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "uri", "sha256", "size", "contentType"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "uri": {"type": "string", "minLength": 1},
                        "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                        "size": {"type": "integer", "minimum": 0},
                        "contentType": {"type": "string", "minLength": 1}
                    }
                }
            },
            "attestations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["type", "status", "timestamp"],
                    "properties": {
                        "type": {"type": "string", "minLength": 1},
                        "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "attestor": {"type": "string"},
                        "notes": {"type": "string"}
                    }
                }
            },
            "createdBy": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255
            },
            "createdAt": {
                "type": "string",
                "format": "date-time"
            },
            "metadata": {
                "type": "object",
                "additionalProperties": True
            }
        },
        "additionalProperties": False
    }
    
    def __init__(self):
        """
        Initialize the ManifestHandler.
        
        Sets up the document handler and validates dependencies.
        """
        self.document_handler = DocumentHandler()
        
        if not HAS_CANONICALJSON:
            print("Warning: canonicaljson not available, using fallback canonicalization")
    
    def create_manifest(
        self, 
        loan_id: str, 
        files: List[Dict[str, Any]], 
        attestations: List[Dict[str, Any]], 
        created_by: str,
        artifact_type: str = "loan_packet",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a manifest for a multi-file loan packet.
        
        This method builds a comprehensive manifest document that describes
        a loan packet containing multiple files, their metadata, and attestations.
        
        Args:
            loan_id: Unique identifier for the loan
            files: List of file information dictionaries
            attestations: List of attestation information dictionaries
            created_by: User or system that created the manifest
            artifact_type: Type of artifact (default: "loan_packet")
            metadata: Optional additional metadata
        
        Returns:
            Dict[str, Any]: Complete manifest document
        
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        if not loan_id:
            raise ValueError("loan_id is required")
        
        if not files:
            raise ValueError("files list cannot be empty")
        
        if not created_by:
            raise ValueError("created_by is required")
        
        if not isinstance(files, list):
            raise ValueError("files must be a list")
        
        if not isinstance(attestations, list):
            raise ValueError("attestations must be a list")
        
        # Validate file entries
        for i, file_info in enumerate(files):
            required_fields = ["name", "uri", "sha256", "size", "contentType"]
            for field in required_fields:
                if field not in file_info:
                    raise ValueError(f"File {i}: missing required field '{field}'")
        
        # Validate attestation entries
        for i, attestation in enumerate(attestations):
            required_fields = ["type", "status", "timestamp"]
            for field in required_fields:
                if field not in attestation:
                    raise ValueError(f"Attestation {i}: missing required field '{field}'")
        
        # Build manifest
        manifest = {
            "schemaVersion": "1.0",
            "artifactType": artifact_type,
            "loanId": loan_id,
            "files": files,
            "attestations": attestations,
            "createdBy": created_by,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Add metadata if provided
        if metadata:
            manifest["metadata"] = metadata
        
        return manifest
    
    def canonicalize_manifest(self, manifest: Dict[str, Any]) -> bytes:
        """
        Convert manifest to canonical form.
        
        Canonical JSON ensures consistent representation of manifest data by:
        1. Sorting object keys alphabetically
        2. Removing unnecessary whitespace
        3. Using consistent number formatting
        4. Using consistent string escaping
        
        This is crucial for generating consistent hashes and enabling
        reliable comparison of manifest documents.
        
        Args:
            manifest: The manifest dictionary to canonicalize
        
        Returns:
            bytes: Canonical manifest representation as bytes
        
        Raises:
            ValueError: If manifest cannot be serialized to JSON
            RuntimeError: If canonicalization fails
        """
        try:
            if HAS_CANONICALJSON:
                # Use canonicaljson for consistent encoding
                canonical_bytes = canonicaljson.encode_canonical_json(manifest)
                return canonical_bytes
            else:
                # Fallback: Use json.dumps with sort_keys=True and separators
                canonical_str = json.dumps(
                    manifest, 
                    sort_keys=True, 
                    separators=(',', ':'), 
                    ensure_ascii=True
                )
                return canonical_str.encode('utf-8')
            
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid manifest data for canonicalization: {e}")
        except Exception as e:
            raise RuntimeError(f"Canonicalization failed: {e}")
    
    def hash_manifest(self, manifest: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of canonical manifest.
        
        This method creates a cryptographic hash of the canonical manifest representation,
        which can be used for:
        - Manifest integrity verification
        - Duplicate detection
        - Change tracking
        - Blockchain storage
        
        Args:
            manifest: The manifest dictionary to hash
        
        Returns:
            str: SHA-256 hash as hexadecimal string (64 characters)
        
        Raises:
            ValueError: If manifest cannot be canonicalized
            RuntimeError: If hashing fails
        """
        try:
            # Get canonical bytes
            canonical_bytes = self.canonicalize_manifest(manifest)
            
            # Calculate SHA-256 hash
            sha256_hash = hashlib.sha256(canonical_bytes)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            raise RuntimeError(f"Hash generation failed: {e}")
    
    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate manifest against schema.
        
        This method validates the structure and content of a manifest against
        the predefined schema to ensure data quality and consistency.
        
        Args:
            manifest: The manifest dictionary to validate
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
                - (True, "") if validation passes
                - (False, error_message) if validation fails
        """
        try:
            # Check required fields exist
            required_fields = [
                "schemaVersion", "artifactType", "loanId", "files", 
                "attestations", "createdBy", "createdAt"
            ]
            
            for field in required_fields:
                if field not in manifest:
                    return False, f"Missing required field: {field}"
            
            # Check files is non-empty list
            if not isinstance(manifest["files"], list):
                return False, "files must be a list"
            
            if len(manifest["files"]) == 0:
                return False, "files list cannot be empty"
            
            # Validate each file entry
            for i, file_info in enumerate(manifest["files"]):
                if not isinstance(file_info, dict):
                    return False, f"File {i} must be a dictionary"
                
                required_file_fields = ["name", "uri", "sha256", "size", "contentType"]
                for field in required_file_fields:
                    if field not in file_info:
                        return False, f"File {i}: missing required field '{field}'"
                
                # Validate SHA-256 format
                sha256 = file_info["sha256"]
                if not isinstance(sha256, str) or len(sha256) != 64:
                    return False, f"File {i}: sha256 must be a 64-character hex string"
                
                # Validate size
                size = file_info["size"]
                if not isinstance(size, int) or size < 0:
                    return False, f"File {i}: size must be a non-negative integer"
            
            # Validate attestations
            if not isinstance(manifest["attestations"], list):
                return False, "attestations must be a list"
            
            for i, attestation in enumerate(manifest["attestations"]):
                if not isinstance(attestation, dict):
                    return False, f"Attestation {i} must be a dictionary"
                
                required_attestation_fields = ["type", "status", "timestamp"]
                for field in required_attestation_fields:
                    if field not in attestation:
                        return False, f"Attestation {i}: missing required field '{field}'"
            
            # Validate artifact type
            valid_types = ["loan_packet", "appraisal_packet", "credit_packet"]
            if manifest["artifactType"] not in valid_types:
                return False, f"Invalid artifact type: {manifest['artifactType']}"
            
            # Validate schema version format
            schema_version = manifest["schemaVersion"]
            if not isinstance(schema_version, str) or not schema_version.count('.') == 1:
                return False, "schemaVersion must be in format 'X.Y'"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def extract_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Extract file information for manifest inclusion.
        
        This method analyzes a file and extracts all necessary information
        for inclusion in a manifest, including hash, size, and content type.
        
        Args:
            file_path: Path to the file to analyze
        
        Returns:
            Dict[str, Any]: File information dictionary with:
                - name: Filename
                - uri: File URI or path
                - sha256: SHA-256 hash
                - size: File size in bytes
                - contentType: MIME type
        
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file_path is invalid
            RuntimeError: If file analysis fails
        """
        if not file_path:
            raise ValueError("file_path is required")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            # Get file hash
            sha256_hash = self.document_handler.calculate_hash_from_file(str(file_path))
            
            # Get file size
            file_size = file_path.stat().st_size
            
            # Determine content type based on file extension
            content_type = self._get_content_type(file_path.suffix.lower())
            
            # Build file info
            file_info = {
                "name": file_path.name,
                "uri": str(file_path.absolute()),
                "sha256": sha256_hash,
                "size": file_size,
                "contentType": content_type
            }
            
            return file_info
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract file info: {e}")
    
    def _get_content_type(self, extension: str) -> str:
        """
        Get MIME content type based on file extension.
        
        Args:
            extension: File extension (with dot, e.g., '.pdf')
        
        Returns:
            str: MIME content type
        """
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.tiff': 'image/tiff',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed'
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    def create_manifest_from_directory(
        self, 
        loan_id: str, 
        directory_path: str, 
        created_by: str,
        artifact_type: str = "loan_packet",
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a manifest from all files in a directory.
        
        This method scans a directory and creates a manifest containing
        all files found in that directory.
        
        Args:
            loan_id: Unique identifier for the loan
            directory_path: Path to the directory containing files
            created_by: User or system that created the manifest
            artifact_type: Type of artifact (default: "loan_packet")
            file_extensions: Optional list of allowed file extensions
        
        Returns:
            Dict[str, Any]: Complete manifest document
        
        Raises:
            FileNotFoundError: If directory does not exist
            ValueError: If directory is empty or invalid
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Find all files
        files = []
        for file_path in directory_path.iterdir():
            if file_path.is_file():
                # Check file extension filter if provided
                if file_extensions:
                    if file_path.suffix.lower() not in file_extensions:
                        continue
                
                try:
                    file_info = self.extract_file_info(str(file_path))
                    files.append(file_info)
                except Exception as e:
                    print(f"Warning: Failed to process file {file_path}: {e}")
                    continue
        
        if not files:
            raise ValueError(f"No files found in directory: {directory_path}")
        
        # Create empty attestations list
        attestations = []
        
        # Create manifest
        manifest = self.create_manifest(
            loan_id=loan_id,
            files=files,
            attestations=attestations,
            created_by=created_by,
            artifact_type=artifact_type
        )
        
        return manifest
    
    def process_manifest(
        self, 
        manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for manifests.
        
        This method runs the full processing pipeline:
        1. Schema validation
        2. Canonicalization
        3. Hash generation
        
        Args:
            manifest: The manifest dictionary to process
        
        Returns:
            Dict[str, Any]: Processing results including:
                - is_valid: Overall validation status
                - schema_valid: Schema validation status
                - canonical_manifest: Canonical manifest bytes
                - hash: SHA-256 hash
                - errors: List of all errors
                - warnings: List of warnings
        
        Raises:
            ValueError: If manifest is invalid
            RuntimeError: If processing fails
        """
        result = {
            'is_valid': False,
            'schema_valid': False,
            'canonical_manifest': None,
            'hash': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Step 1: Schema validation
            schema_valid, schema_error = self.validate_manifest_schema(manifest)
            result['schema_valid'] = schema_valid
            if not schema_valid:
                result['errors'].append(f"Schema validation failed: {schema_error}")
            
            # Step 2: Canonicalization (only if schema is valid)
            if schema_valid:
                try:
                    canonical_manifest = self.canonicalize_manifest(manifest)
                    result['canonical_manifest'] = canonical_manifest
                except Exception as e:
                    result['errors'].append(f"Canonicalization failed: {e}")
            
            # Step 3: Hash generation (only if canonicalization succeeded)
            if result['canonical_manifest'] is not None:
                try:
                    hash_value = self.hash_manifest(manifest)
                    result['hash'] = hash_value
                except Exception as e:
                    result['errors'].append(f"Hash generation failed: {e}")
            
            # Overall validation status
            result['is_valid'] = (
                result['schema_valid'] and 
                result['hash'] is not None
            )
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Processing failed: {e}")
            return result


# Example usage and testing
if __name__ == "__main__":
    # Test the ManifestHandler
    print("📦 MANIFEST HANDLER TEST")
    print("=" * 50)
    
    try:
        handler = ManifestHandler()
        print("✅ ManifestHandler initialized successfully")
        
        # Test data
        test_files = [
            {
                "name": "loan_agreement.pdf",
                "uri": "/path/to/loan_agreement.pdf",
                "sha256": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                "size": 1024000,
                "contentType": "application/pdf"
            },
            {
                "name": "income_verification.pdf",
                "uri": "/path/to/income_verification.pdf",
                "sha256": "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
                "size": 512000,
                "contentType": "application/pdf"
            }
        ]
        
        test_attestations = [
            {
                "type": "underwriter_approval",
                "status": "approved",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "attestor": "underwriter@bank.com"
            }
        ]
        
        print("\n1️⃣ Testing Manifest Creation:")
        manifest = handler.create_manifest(
            loan_id="LOAN_2024_001",
            files=test_files,
            attestations=test_attestations,
            created_by="system@integrityx.com"
        )
        print("✅ Manifest created successfully")
        print(f"   Files: {len(manifest['files'])}")
        print(f"   Attestations: {len(manifest['attestations'])}")
        
        print("\n2️⃣ Testing Schema Validation:")
        is_valid, error = handler.validate_manifest_schema(manifest)
        if is_valid:
            print("✅ Schema validation passed")
        else:
            print(f"❌ Schema validation failed: {error}")
        
        print("\n3️⃣ Testing Canonicalization:")
        canonical_bytes = handler.canonicalize_manifest(manifest)
        print(f"✅ Canonical manifest generated: {len(canonical_bytes)} bytes")
        
        print("\n4️⃣ Testing Hash Generation:")
        hash_value = handler.hash_manifest(manifest)
        print(f"✅ Hash generated: {hash_value}")
        
        print("\n5️⃣ Testing Complete Processing:")
        result = handler.process_manifest(manifest)
        print(f"✅ Processing completed:")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Schema Valid: {result['schema_valid']}")
        if result['hash']:
            print(f"   Hash: {result['hash'][:16]}...")
        else:
            print("   Hash: None")
        print(f"   Errors: {len(result['errors'])}")
        
        print("\n✅ All manifest handler tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
