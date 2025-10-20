"""
Document Verifier - Core Tampering Detection Logic

This module provides the core tampering detection functionality for the IntegrityX
financial document integrity system. It compares cryptographic hashes to detect
any unauthorized modifications to documents.

The DocumentVerifier class is the heart of the integrity verification system,
providing methods to verify document authenticity by comparing current file
hashes with stored hashes in the Walacor database.

Key Features:
- Hash-based tampering detection
- Audit trail logging
- Support for file paths and byte streams
- Comprehensive verification results
- Helpful error messages for demo purposes
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from document_handler import DocumentHandler
from walacor_service import WalacorIntegrityService


class DocumentVerifier:
    """
    Core tampering detection logic for financial document integrity verification.
    
    This class provides the primary functionality for detecting document tampering
    by comparing cryptographic hashes. It integrates with the DocumentHandler for
    hash calculation and WalacorIntegrityService for database operations.
    
    The verifier is designed to be the central component for all document integrity
    checks in the IntegrityX system, providing comprehensive verification results
    and maintaining a complete audit trail.
    
    Attributes:
        document_handler (DocumentHandler): Handler for document operations
        walacor_service (WalacorIntegrityService): Service for Walacor operations
    """
    
    def __init__(self):
        """
        Initialize the DocumentVerifier with required services.
        
        Creates instances of DocumentHandler and WalacorIntegrityService to
        provide the complete document verification functionality.
        
        Raises:
            ConnectionError: If unable to initialize WalacorIntegrityService
            RuntimeError: If unable to initialize DocumentHandler
        """
        try:
            print("🔧 Initializing DocumentVerifier...")
            
            # Initialize document handler for hash calculations
            self.document_handler = DocumentHandler()
            print("✅ DocumentHandler initialized")
            
            # Initialize Walacor service for database operations
            self.walacor_service = WalacorIntegrityService()
            print("✅ WalacorIntegrityService initialized")
            
            print("✅ DocumentVerifier ready for tampering detection!")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DocumentVerifier: {e}")
    
    def verify_document(self, file_path: str, loan_id: str) -> Dict[str, Any]:
        """
        Verify document integrity by comparing current hash with stored hash.
        
        This is the core tampering detection method. It calculates the current
        hash of the document and compares it with the hash stored in Walacor
        for the specified loan. Any difference indicates tampering.
        
        Args:
            file_path (str): Path to the document file to verify
            loan_id (str): Loan ID to look up the stored hash
            
        Returns:
            Dict[str, Any]: Verification result containing:
                - is_valid (bool): True if document is authentic
                - current_hash (str): SHA-256 hash of current file
                - stored_hash (str): SHA-256 hash stored in database
                - tampered (bool): True if document has been modified
                - original_upload_time (str): When document was originally uploaded
                - verification_time (str): When this verification was performed
                - details (dict): Additional verification details
                
        Raises:
            FileNotFoundError: If the document file doesn't exist
            ValueError: If loan_id is invalid
            RuntimeError: If verification process fails
        """
        try:
            print(f"\n🔍 Starting document verification...")
            print(f"   File: {file_path}")
            print(f"   Loan ID: {loan_id}")
            
            # Validate inputs
            if not file_path or not loan_id:
                raise ValueError("file_path and loan_id are required")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document file not found: {file_path}")
            
            # Calculate current hash
            print("📊 Calculating current document hash...")
            current_hash = self.document_handler.calculate_hash_from_file(file_path)
            print(f"✅ Current hash: {current_hash[:16]}...")
            
            # Get stored document records for this loan
            print("🔍 Looking up stored document records...")
            stored_documents = self.walacor_service.get_document_by_loan_id(loan_id)
            
            if not stored_documents:
                print("⚠️  No stored documents found for this loan")
                return self._create_verification_result(
                    is_valid=False,
                    current_hash=current_hash,
                    stored_hash=None,
                    tampered=None,
                    original_upload_time=None,
                    verification_time=datetime.now().isoformat(),
                    details={
                        "error": "No stored documents found for this loan",
                        "loan_id": loan_id,
                        "file_path": file_path
                    }
                )
            
            # Find matching document by file path or use the most recent
            stored_doc = None
            for doc in stored_documents:
                if doc.get('file_path') == file_path:
                    stored_doc = doc
                    break
            
            if not stored_doc:
                # Use the most recent document if no exact path match
                stored_doc = stored_documents[0]
                print("⚠️  No exact path match, using most recent document")
            
            stored_hash = stored_doc.get('document_hash')
            original_upload_time = stored_doc.get('upload_timestamp')
            
            print(f"✅ Stored hash: {stored_hash[:16] if stored_hash else 'None'}...")
            print(f"✅ Original upload: {original_upload_time}")
            
            # Compare hashes
            is_valid = current_hash == stored_hash
            tampered = not is_valid if stored_hash else None
            
            print(f"🔍 Hash comparison: {'✅ IDENTICAL' if is_valid else '❌ DIFFERENT'}")
            
            # Log verification attempt to audit trail
            try:
                self.walacor_service.log_audit_event(
                    document_id=stored_doc.get('UID', 'unknown'),
                    event_type="verify",
                    user="system",
                    details=f"Document verification: {'PASSED' if is_valid else 'FAILED'}"
                )
                print("✅ Audit event logged")
            except Exception as e:
                print(f"⚠️  Failed to log audit event: {e}")
            
            # Create verification result
            result = self._create_verification_result(
                is_valid=is_valid,
                current_hash=current_hash,
                stored_hash=stored_hash,
                tampered=tampered,
                original_upload_time=original_upload_time,
                verification_time=datetime.now().isoformat(),
                details={
                    "loan_id": loan_id,
                    "file_path": file_path,
                    "stored_document_id": stored_doc.get('UID'),
                    "file_size": stored_doc.get('file_size'),
                    "document_type": stored_doc.get('document_type'),
                    "uploaded_by": stored_doc.get('uploaded_by')
                }
            )
            
            # Print summary
            if is_valid:
                print("🎉 DOCUMENT VERIFICATION PASSED - No tampering detected!")
            else:
                print("🚨 DOCUMENT VERIFICATION FAILED - Tampering detected!")
            
            return result
            
        except Exception as e:
            error_msg = f"Document verification failed: {e}"
            print(f"❌ {error_msg}")
            
            # Log error to audit trail
            try:
                self.walacor_service.log_audit_event(
                    document_id="unknown",
                    event_type="verify_error",
                    user="system",
                    details=f"Verification error: {str(e)}"
                )
            except:
                pass  # Don't fail if audit logging fails
            
            raise RuntimeError(error_msg)
    
    def verify_from_bytes(self, file_bytes: bytes, loan_id: str) -> Dict[str, Any]:
        """
        Verify document integrity from byte data instead of file path.
        
        This method is useful for verifying uploaded files in web applications
        like Streamlit, where files are provided as byte streams rather than
        file paths.
        
        Args:
            file_bytes (bytes): The document content as bytes
            loan_id (str): Loan ID to look up the stored hash
            
        Returns:
            Dict[str, Any]: Verification result (same format as verify_document)
            
        Raises:
            ValueError: If file_bytes or loan_id is invalid
            RuntimeError: If verification process fails
        """
        try:
            print(f"\n🔍 Starting document verification from bytes...")
            print(f"   Bytes size: {len(file_bytes)} bytes")
            print(f"   Loan ID: {loan_id}")
            
            # Validate inputs
            if not file_bytes or not loan_id:
                raise ValueError("file_bytes and loan_id are required")
            
            # Calculate current hash from bytes
            print("📊 Calculating current document hash from bytes...")
            current_hash = self.document_handler.calculate_hash_from_bytes(file_bytes)
            print(f"✅ Current hash: {current_hash[:16]}...")
            
            # Get stored document records for this loan
            print("🔍 Looking up stored document records...")
            stored_documents = self.walacor_service.get_document_by_loan_id(loan_id)
            
            if not stored_documents:
                print("⚠️  No stored documents found for this loan")
                return self._create_verification_result(
                    is_valid=False,
                    current_hash=current_hash,
                    stored_hash=None,
                    tampered=None,
                    original_upload_time=None,
                    verification_time=datetime.now().isoformat(),
                    details={
                        "error": "No stored documents found for this loan",
                        "loan_id": loan_id,
                        "file_size": len(file_bytes)
                    }
                )
            
            # Use the most recent document
            stored_doc = stored_documents[0]
            stored_hash = stored_doc.get('document_hash')
            original_upload_time = stored_doc.get('upload_timestamp')
            
            print(f"✅ Stored hash: {stored_hash[:16] if stored_hash else 'None'}...")
            print(f"✅ Original upload: {original_upload_time}")
            
            # Compare hashes
            is_valid = current_hash == stored_hash
            tampered = not is_valid if stored_hash else None
            
            print(f"🔍 Hash comparison: {'✅ IDENTICAL' if is_valid else '❌ DIFFERENT'}")
            
            # Log verification attempt to audit trail
            try:
                self.walacor_service.log_audit_event(
                    document_id=stored_doc.get('UID', 'unknown'),
                    event_type="verify_bytes",
                    user="system",
                    details=f"Document verification from bytes: {'PASSED' if is_valid else 'FAILED'}"
                )
                print("✅ Audit event logged")
            except Exception as e:
                print(f"⚠️  Failed to log audit event: {e}")
            
            # Create verification result
            result = self._create_verification_result(
                is_valid=is_valid,
                current_hash=current_hash,
                stored_hash=stored_hash,
                tampered=tampered,
                original_upload_time=original_upload_time,
                verification_time=datetime.now().isoformat(),
                details={
                    "loan_id": loan_id,
                    "file_size": len(file_bytes),
                    "stored_document_id": stored_doc.get('UID'),
                    "document_type": stored_doc.get('document_type'),
                    "uploaded_by": stored_doc.get('uploaded_by')
                }
            )
            
            # Print summary
            if is_valid:
                print("🎉 DOCUMENT VERIFICATION PASSED - No tampering detected!")
            else:
                print("🚨 DOCUMENT VERIFICATION FAILED - Tampering detected!")
            
            return result
            
        except Exception as e:
            error_msg = f"Document verification from bytes failed: {e}"
            print(f"❌ {error_msg}")
            
            # Log error to audit trail
            try:
                self.walacor_service.log_audit_event(
                    document_id="unknown",
                    event_type="verify_bytes_error",
                    user="system",
                    details=f"Verification error: {str(e)}"
                )
            except:
                pass  # Don't fail if audit logging fails
            
            raise RuntimeError(error_msg)
    
    def detect_changes(self, original_file_path: str, modified_file_path: str) -> Dict[str, Any]:
        """
        Detect changes between two files by comparing their hashes.
        
        This method compares two files directly without involving the database,
        useful for detecting changes between different versions of a document
        or for comparing a file with a known good version.
        
        Args:
            original_file_path (str): Path to the original file
            modified_file_path (str): Path to the potentially modified file
            
        Returns:
            Dict[str, Any]: Change detection result containing:
                - files_identical (bool): True if files are identical
                - original_hash (str): Hash of the original file
                - modified_hash (str): Hash of the modified file
                - timestamp (str): When the comparison was performed
                - details (dict): Additional comparison details
                
        Raises:
            FileNotFoundError: If either file doesn't exist
            RuntimeError: If comparison process fails
        """
        try:
            print(f"\n🔍 Starting file change detection...")
            print(f"   Original file: {original_file_path}")
            print(f"   Modified file: {modified_file_path}")
            
            # Validate inputs
            if not original_file_path or not modified_file_path:
                raise ValueError("Both file paths are required")
            
            if not os.path.exists(original_file_path):
                raise FileNotFoundError(f"Original file not found: {original_file_path}")
            
            if not os.path.exists(modified_file_path):
                raise FileNotFoundError(f"Modified file not found: {modified_file_path}")
            
            # Calculate hashes
            print("📊 Calculating file hashes...")
            original_hash = self.document_handler.calculate_hash_from_file(original_file_path)
            modified_hash = self.document_handler.calculate_hash_from_file(modified_file_path)
            
            print(f"✅ Original hash: {original_hash[:16]}...")
            print(f"✅ Modified hash: {modified_hash[:16]}...")
            
            # Compare hashes
            files_identical = original_hash == modified_hash
            print(f"🔍 Files identical: {'✅ YES' if files_identical else '❌ NO'}")
            
            # Get file information
            original_size = os.path.getsize(original_file_path)
            modified_size = os.path.getsize(modified_file_path)
            
            # Create result
            result = {
                "files_identical": files_identical,
                "original_hash": original_hash,
                "modified_hash": modified_hash,
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "original_file_path": original_file_path,
                    "modified_file_path": modified_file_path,
                    "original_file_size": original_size,
                    "modified_file_size": modified_size,
                    "size_difference": modified_size - original_size,
                    "change_detected": not files_identical
                }
            }
            
            # Print summary
            if files_identical:
                print("🎉 FILES ARE IDENTICAL - No changes detected!")
            else:
                print("🚨 FILES ARE DIFFERENT - Changes detected!")
                print(f"   Size difference: {modified_size - original_size} bytes")
            
            return result
            
        except Exception as e:
            error_msg = f"File change detection failed: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def _create_verification_result(self, is_valid: bool, current_hash: str, 
                                  stored_hash: Optional[str], tampered: Optional[bool],
                                  original_upload_time: Optional[str], 
                                  verification_time: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized verification result dictionary.
        
        Args:
            is_valid (bool): Whether the document is valid
            current_hash (str): Current document hash
            stored_hash (Optional[str]): Stored document hash
            tampered (Optional[bool]): Whether tampering was detected
            original_upload_time (Optional[str]): Original upload timestamp
            verification_time (str): Verification timestamp
            details (Dict[str, Any]): Additional details
            
        Returns:
            Dict[str, Any]: Standardized verification result
        """
        return {
            "is_valid": is_valid,
            "current_hash": current_hash,
            "stored_hash": stored_hash,
            "tampered": tampered,
            "original_upload_time": original_upload_time,
            "verification_time": verification_time,
            "details": details
        }
    
    def get_verification_summary(self, result: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of verification results.
        
        This method is useful for displaying verification results in a
        user-friendly format, especially in demo applications.
        
        Args:
            result (Dict[str, Any]): Verification result from verify_document or verify_from_bytes
            
        Returns:
            str: Human-readable summary of the verification
        """
        if result["is_valid"]:
            return f"✅ Document is AUTHENTIC - No tampering detected"
        elif result["tampered"]:
            return f"🚨 Document has been TAMPERED - Hashes do not match"
        else:
            return f"⚠️  Cannot verify - No stored record found"
    
    def get_detailed_report(self, result: Dict[str, Any]) -> str:
        """
        Generate a detailed verification report.
        
        Args:
            result (Dict[str, Any]): Verification result
            
        Returns:
            str: Detailed verification report
        """
        report = []
        report.append("=" * 60)
        report.append("DOCUMENT VERIFICATION REPORT")
        report.append("=" * 60)
        
        # Status
        if result["is_valid"]:
            report.append("STATUS: ✅ AUTHENTIC - No tampering detected")
        elif result["tampered"]:
            report.append("STATUS: 🚨 TAMPERED - Document has been modified")
        else:
            report.append("STATUS: ⚠️  UNVERIFIED - No stored record found")
        
        report.append("")
        
        # Hashes
        report.append("HASH COMPARISON:")
        report.append(f"  Current Hash:  {result['current_hash']}")
        if result["stored_hash"]:
            report.append(f"  Stored Hash:   {result['stored_hash']}")
        else:
            report.append("  Stored Hash:   Not found")
        
        report.append("")
        
        # Timestamps
        if result["original_upload_time"]:
            report.append(f"Original Upload: {result['original_upload_time']}")
        report.append(f"Verification:    {result['verification_time']}")
        
        report.append("")
        
        # Details
        if result["details"]:
            report.append("DETAILS:")
            for key, value in result["details"].items():
                report.append(f"  {key}: {value}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
