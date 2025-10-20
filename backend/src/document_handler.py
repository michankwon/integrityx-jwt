"""
Document Handler for Financial Integrity System

This module provides cryptographic hash-based document integrity verification.
We store ONLY cryptographic hashes in Walacor, not the actual files, allowing
us to verify 50MB+ documents using just 64-character hashes.

Key Benefits:
- Efficient storage: Only 64-character hashes stored in database
- Fast verification: Compare hashes instead of full file content
- Tamper detection: Any file modification changes the hash
- Scalable: Works with documents of any size
"""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class DocumentHandler:
    """
    Handles document storage and cryptographic hash generation for financial integrity.
    
    This class implements a hash-based approach where only SHA-256 hashes are stored
    in the Walacor database, not the actual document files. This allows for efficient
    verification of document integrity without storing large files in the database.
    
    Attributes:
        storage_path (Path): Base directory for document storage
    """
    
    def __init__(self, storage_path: str = "data/documents"):
        """
        Initialize DocumentHandler with storage path.
        
        Args:
            storage_path (str): Base directory for document storage. 
                               Defaults to "data/documents"
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def calculate_hash_from_bytes(self, file_bytes: bytes) -> str:
        """
        Calculate SHA-256 hash from file bytes.
        
        This method generates a cryptographic hash that uniquely identifies
        the document content. Any change to the file will result in a different hash.
        
        Args:
            file_bytes (bytes): The file content as bytes
            
        Returns:
            str: SHA-256 hash as hexadecimal string (64 characters)
            
        Example:
            >>> handler = DocumentHandler()
            >>> content = b"Hello, World!"
            >>> hash_value = handler.calculate_hash_from_bytes(content)
            >>> len(hash_value)
            64
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_bytes)
        return sha256_hash.hexdigest()
    
    def calculate_hash_from_file(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash from file on disk.
        
        This method efficiently processes large files by reading them in 4096-byte
        chunks, making it suitable for documents of any size including 50MB+ files.
        
        Args:
            file_path (str): Path to the file to hash
            
        Returns:
            str: SHA-256 hash as hexadecimal string (64 characters)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
            
        Example:
            >>> handler = DocumentHandler()
            >>> hash_value = handler.calculate_hash_from_file("document.pdf")
            >>> len(hash_value)
            64
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as file:
                # Read file in 4096-byte chunks for memory efficiency
                while chunk := file.read(4096):
                    sha256_hash.update(chunk)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")
        
        return sha256_hash.hexdigest()
    
    def save_document(self, file_bytes: bytes, loan_id: str, document_type: str, 
                     file_extension: str = "pdf") -> Dict[str, Any]:
        """
        Save document to storage and return metadata including hash.
        
        Documents are saved with timestamp-based naming to ensure uniqueness:
        format: {document_type}_{timestamp}.{extension}
        location: {storage_path}/{loan_id}/{filename}
        
        Args:
            file_bytes (bytes): The document content as bytes
            loan_id (str): Unique identifier for the loan
            document_type (str): Type of document (e.g., "contract", "statement")
            file_extension (str): File extension without dot. Defaults to "pdf"
            
        Returns:
            Dict[str, Any]: Document metadata containing:
                - file_path (str): Full path to saved file
                - file_size (int): Size of file in bytes
                - document_hash (str): SHA-256 hash of the document
                - filename (str): Name of the saved file
                
        Example:
            >>> handler = DocumentHandler()
            >>> content = b"PDF content here..."
            >>> result = handler.save_document(content, "LOAN123", "contract")
            >>> result["document_hash"]
            "a1b2c3d4e5f6..."
        """
        # Create loan-specific directory
        loan_dir = self.storage_path / loan_id
        loan_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{document_type}_{timestamp}.{file_extension}"
        file_path = loan_dir / filename
        
        # Save file
        with open(file_path, 'wb') as file:
            file.write(file_bytes)
        
        # Calculate hash and metadata
        document_hash = self.calculate_hash_from_bytes(file_bytes)
        file_size = len(file_bytes)
        
        return {
            "file_path": str(file_path),
            "file_size": file_size,
            "document_hash": document_hash,
            "filename": filename
        }
    
    def get_document_path(self, loan_id: str, document_type: str) -> Optional[str]:
        """
        Find the most recent document of a specific type for a loan.
        
        Searches for files matching the pattern: {document_type}_*.{extension}
        and returns the path to the most recently created file.
        
        Args:
            loan_id (str): Unique identifier for the loan
            document_type (str): Type of document to find
            
        Returns:
            Optional[str]: Path to the most recent document, or None if not found
            
        Example:
            >>> handler = DocumentHandler()
            >>> path = handler.get_document_path("LOAN123", "contract")
            >>> print(path)
            "data/documents/LOAN123/contract_20241202_143022.pdf"
        """
        loan_dir = self.storage_path / loan_id
        
        if not loan_dir.exists():
            return None
        
        # Find all files matching the document type pattern
        pattern = f"{document_type}_*"
        matching_files = list(loan_dir.glob(pattern))
        
        if not matching_files:
            return None
        
        # Return the most recently modified file
        most_recent = max(matching_files, key=lambda f: f.stat().st_mtime)
        return str(most_recent)
    
    def verify_document_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify document integrity by comparing calculated hash with expected hash.
        
        This method is used to ensure that a document hasn't been tampered with
        since it was originally processed and stored.
        
        Args:
            file_path (str): Path to the document to verify
            expected_hash (str): The expected SHA-256 hash
            
        Returns:
            bool: True if document integrity is verified, False otherwise
            
        Example:
            >>> handler = DocumentHandler()
            >>> is_valid = handler.verify_document_integrity(
            ...     "document.pdf", 
            ...     "a1b2c3d4e5f6..."
            ... )
            >>> print(is_valid)
            True
        """
        try:
            calculated_hash = self.calculate_hash_from_file(file_path)
            return calculated_hash == expected_hash
        except (FileNotFoundError, IOError):
            return False
    
    def get_document_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a document.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            Optional[Dict[str, Any]]: Document information or None if file doesn't exist
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None
            
            stat = file_path_obj.stat()
            document_hash = self.calculate_hash_from_file(file_path)
            
            return {
                "file_path": str(file_path_obj),
                "filename": file_path_obj.name,
                "file_size": stat.st_size,
                "document_hash": document_hash,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime)
            }
        except (FileNotFoundError, IOError):
            return None



