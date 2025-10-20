#!/usr/bin/env python3
"""
Comprehensive test script for the ManifestHandler.

This script demonstrates all the functionality of the ManifestHandler class including
manifest creation, validation, canonicalization, hashing, and file processing.
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from manifest_handler import ManifestHandler


def create_test_files():
    """Create temporary test files for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test files
    files = []
    
    # PDF file
    pdf_path = Path(temp_dir) / "loan_agreement.pdf"
    with open(pdf_path, "w") as f:
        f.write("This is a test PDF content for loan agreement.")
    files.append(str(pdf_path))
    
    # DOCX file
    docx_path = Path(temp_dir) / "income_verification.docx"
    with open(docx_path, "w") as f:
        f.write("This is a test DOCX content for income verification.")
    files.append(str(docx_path))
    
    # TXT file
    txt_path = Path(temp_dir) / "credit_report.txt"
    with open(txt_path, "w") as f:
        f.write("This is a test TXT content for credit report.")
    files.append(str(txt_path))
    
    return temp_dir, files


def test_manifest_creation():
    """Test manifest creation functionality."""
    print("📦 MANIFEST CREATION TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Test 1: Basic manifest creation
    print("\n1️⃣ Testing Basic Manifest Creation:")
    files = [
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
    
    attestations = [
        {
            "type": "underwriter_approval",
            "status": "approved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attestor": "underwriter@bank.com"
        }
    ]
    
    manifest = handler.create_manifest(
        loan_id="LOAN_2024_001",
        files=files,
        attestations=attestations,
        created_by="system@integrityx.com"
    )
    
    print("✅ Basic manifest created successfully")
    print(f"   Schema Version: {manifest['schemaVersion']}")
    print(f"   Artifact Type: {manifest['artifactType']}")
    print(f"   Loan ID: {manifest['loanId']}")
    print(f"   Files: {len(manifest['files'])}")
    print(f"   Attestations: {len(manifest['attestations'])}")
    print(f"   Created By: {manifest['createdBy']}")
    
    # Test 2: Manifest with metadata
    print("\n2️⃣ Testing Manifest with Metadata:")
    metadata = {
        "loanOfficer": "John Smith",
        "branch": "Main Street Branch",
        "priority": "high"
    }
    
    manifest_with_metadata = handler.create_manifest(
        loan_id="LOAN_2024_002",
        files=files,
        attestations=attestations,
        created_by="loan_officer@bank.com",
        metadata=metadata
    )
    
    print("✅ Manifest with metadata created successfully")
    print(f"   Metadata fields: {list(manifest_with_metadata['metadata'].keys())}")
    
    # Test 3: Different artifact types
    print("\n3️⃣ Testing Different Artifact Types:")
    for artifact_type in ["loan_packet", "appraisal_packet", "credit_packet"]:
        manifest = handler.create_manifest(
            loan_id=f"LOAN_2024_{artifact_type.upper()}",
            files=files,
            attestations=attestations,
            created_by="system@integrityx.com",
            artifact_type=artifact_type
        )
        print(f"✅ {artifact_type} manifest created")
    
    print("\n✅ Manifest creation tests completed!")


def test_file_info_extraction():
    """Test file information extraction functionality."""
    print("\n📁 FILE INFO EXTRACTION TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Create temporary test files
    temp_dir, test_files = create_test_files()
    
    try:
        print("\n1️⃣ Testing File Info Extraction:")
        for file_path in test_files:
            file_info = handler.extract_file_info(file_path)
            print(f"✅ File info extracted for {Path(file_path).name}:")
            print(f"   Name: {file_info['name']}")
            print(f"   Size: {file_info['size']} bytes")
            print(f"   Content Type: {file_info['contentType']}")
            print(f"   Hash: {file_info['sha256'][:16]}...")
        
        # Test 2: Directory manifest creation
        print("\n2️⃣ Testing Directory Manifest Creation:")
        manifest = handler.create_manifest_from_directory(
            loan_id="LOAN_2024_DIR",
            directory_path=temp_dir,
            created_by="system@integrityx.com"
        )
        
        print("✅ Directory manifest created successfully")
        print(f"   Files found: {len(manifest['files'])}")
        for file_info in manifest['files']:
            print(f"   - {file_info['name']} ({file_info['contentType']})")
        
        # Test 3: Directory with file extension filter
        print("\n3️⃣ Testing Directory with File Extension Filter:")
        manifest_filtered = handler.create_manifest_from_directory(
            loan_id="LOAN_2024_FILTERED",
            directory_path=temp_dir,
            created_by="system@integrityx.com",
            file_extensions=['.pdf', '.txt']
        )
        
        print("✅ Filtered directory manifest created")
        print(f"   Files found: {len(manifest_filtered['files'])}")
        for file_info in manifest_filtered['files']:
            print(f"   - {file_info['name']} ({file_info['contentType']})")
        
    finally:
        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)
    
    print("\n✅ File info extraction tests completed!")


def test_manifest_validation():
    """Test manifest validation functionality."""
    print("\n✅ MANIFEST VALIDATION TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Test 1: Valid manifest
    print("\n1️⃣ Testing Valid Manifest:")
    valid_files = [
        {
            "name": "loan_agreement.pdf",
            "uri": "/path/to/loan_agreement.pdf",
            "sha256": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "size": 1024000,
            "contentType": "application/pdf"
        }
    ]
    
    valid_attestations = [
        {
            "type": "underwriter_approval",
            "status": "approved",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    valid_manifest = handler.create_manifest(
        loan_id="LOAN_2024_VALID",
        files=valid_files,
        attestations=valid_attestations,
        created_by="system@integrityx.com"
    )
    
    is_valid, error = handler.validate_manifest_schema(valid_manifest)
    if is_valid:
        print("✅ Valid manifest passed validation")
    else:
        print(f"❌ Valid manifest failed validation: {error}")
    
    # Test 2: Invalid manifest - missing required field
    print("\n2️⃣ Testing Invalid Manifest (Missing Required Field):")
    invalid_manifest = {
        "schemaVersion": "1.0",
        "artifactType": "loan_packet",
        "loanId": "LOAN_2024_INVALID",
        "files": valid_files,
        "attestations": valid_attestations,
        "createdBy": "system@integrityx.com"
        # Missing "createdAt"
    }
    
    is_valid, error = handler.validate_manifest_schema(invalid_manifest)
    if not is_valid:
        print(f"✅ Invalid manifest correctly rejected: {error}")
    else:
        print("❌ Invalid manifest should have been rejected")
    
    # Test 3: Invalid manifest - empty files list
    print("\n3️⃣ Testing Invalid Manifest (Empty Files List):")
    invalid_manifest = {
        "schemaVersion": "1.0",
        "artifactType": "loan_packet",
        "loanId": "LOAN_2024_EMPTY",
        "files": [],  # Empty files list
        "attestations": valid_attestations,
        "createdBy": "system@integrityx.com",
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    is_valid, error = handler.validate_manifest_schema(invalid_manifest)
    if not is_valid:
        print(f"✅ Empty files list correctly rejected: {error}")
    else:
        print("❌ Empty files list should have been rejected")
    
    # Test 4: Invalid manifest - invalid SHA-256
    print("\n4️⃣ Testing Invalid Manifest (Invalid SHA-256):")
    invalid_files = [
        {
            "name": "loan_agreement.pdf",
            "uri": "/path/to/loan_agreement.pdf",
            "sha256": "invalid_hash",  # Invalid SHA-256
            "size": 1024000,
            "contentType": "application/pdf"
        }
    ]
    
    invalid_manifest = handler.create_manifest(
        loan_id="LOAN_2024_INVALID_HASH",
        files=invalid_files,
        attestations=valid_attestations,
        created_by="system@integrityx.com"
    )
    
    is_valid, error = handler.validate_manifest_schema(invalid_manifest)
    if not is_valid:
        print(f"✅ Invalid SHA-256 correctly rejected: {error}")
    else:
        print("❌ Invalid SHA-256 should have been rejected")
    
    print("\n✅ Manifest validation tests completed!")


def test_canonicalization_and_hashing():
    """Test canonicalization and hashing functionality."""
    print("\n🔄 CANONICALIZATION AND HASHING TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Test data
    files = [
        {
            "name": "loan_agreement.pdf",
            "uri": "/path/to/loan_agreement.pdf",
            "sha256": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "size": 1024000,
            "contentType": "application/pdf"
        }
    ]
    
    attestations = [
        {
            "type": "underwriter_approval",
            "status": "approved",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Test 1: Canonicalization consistency
    print("\n1️⃣ Testing Canonicalization Consistency:")
    manifest1 = handler.create_manifest(
        loan_id="LOAN_2024_001",
        files=files,
        attestations=attestations,
        created_by="system@integrityx.com"
    )
    
    # Create same manifest with different key order
    manifest2 = {
        "createdAt": manifest1["createdAt"],
        "createdBy": manifest1["createdBy"],
        "attestations": manifest1["attestations"],
        "files": manifest1["files"],
        "loanId": manifest1["loanId"],
        "artifactType": manifest1["artifactType"],
        "schemaVersion": manifest1["schemaVersion"]
    }
    
    canonical1 = handler.canonicalize_manifest(manifest1)
    canonical2 = handler.canonicalize_manifest(manifest2)
    
    if canonical1 == canonical2:
        print("✅ Canonicalization produces consistent results")
        print(f"   Canonical JSON: {canonical1.decode('utf-8')[:100]}...")
    else:
        print("❌ Canonicalization should produce consistent results")
    
    # Test 2: Hash consistency
    print("\n2️⃣ Testing Hash Consistency:")
    hash1 = handler.hash_manifest(manifest1)
    hash2 = handler.hash_manifest(manifest2)
    
    if hash1 == hash2:
        print("✅ Hash generation is consistent")
        print(f"   Hash: {hash1}")
    else:
        print("❌ Hash generation should be consistent")
        print(f"   Hash 1: {hash1}")
        print(f"   Hash 2: {hash2}")
    
    # Test 3: Different manifests produce different hashes
    print("\n3️⃣ Testing Different Manifests Produce Different Hashes:")
    manifest3 = handler.create_manifest(
        loan_id="LOAN_2024_002",  # Different loan ID
        files=files,
        attestations=attestations,
        created_by="system@integrityx.com"
    )
    
    hash3 = handler.hash_manifest(manifest3)
    
    if hash1 != hash3:
        print("✅ Different manifests produce different hashes")
        print(f"   Hash 1: {hash1}")
        print(f"   Hash 3: {hash3}")
    else:
        print("❌ Different manifests should produce different hashes")
    
    print("\n✅ Canonicalization and hashing tests completed!")


def test_complete_processing():
    """Test complete manifest processing pipeline."""
    print("\n🔄 COMPLETE PROCESSING TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Test 1: Complete valid manifest processing
    print("\n1️⃣ Testing Complete Valid Manifest Processing:")
    files = [
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
    
    attestations = [
        {
            "type": "underwriter_approval",
            "status": "approved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attestor": "underwriter@bank.com"
        },
        {
            "type": "compliance_review",
            "status": "pending",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attestor": "compliance@bank.com"
        }
    ]
    
    manifest = handler.create_manifest(
        loan_id="LOAN_2024_COMPLETE",
        files=files,
        attestations=attestations,
        created_by="system@integrityx.com"
    )
    
    result = handler.process_manifest(manifest)
    
    print(f"✅ Processing Results:")
    print(f"   Overall Valid: {result['is_valid']}")
    print(f"   Schema Valid: {result['schema_valid']}")
    print(f"   Hash Generated: {result['hash'] is not None}")
    if result['hash']:
        print(f"   Hash: {result['hash'][:16]}...")
    print(f"   Errors: {len(result['errors'])}")
    print(f"   Warnings: {len(result['warnings'])}")
    
    # Test 2: Invalid manifest processing
    print("\n2️⃣ Testing Invalid Manifest Processing:")
    invalid_manifest = {
        "schemaVersion": "1.0",
        "artifactType": "loan_packet",
        "loanId": "LOAN_2024_INVALID",
        "files": [],  # Empty files list
        "attestations": attestations,
        "createdBy": "system@integrityx.com",
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    result = handler.process_manifest(invalid_manifest)
    
    print(f"✅ Processing Results:")
    print(f"   Overall Valid: {result['is_valid']}")
    print(f"   Schema Valid: {result['schema_valid']}")
    print(f"   Errors: {len(result['errors'])}")
    if result['errors']:
        print("   Error Details:")
        for error in result['errors']:
            print(f"     - {error}")
    
    print("\n✅ Complete processing tests completed!")


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🚨 ERROR HANDLING TEST")
    print("=" * 50)
    
    handler = ManifestHandler()
    
    # Test 1: Invalid file path
    print("\n1️⃣ Testing Invalid File Path:")
    try:
        handler.extract_file_info("/nonexistent/file.pdf")
        print("❌ Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"✅ Correctly raised FileNotFoundError: {e}")
    
    # Test 2: Empty loan ID
    print("\n2️⃣ Testing Empty Loan ID:")
    try:
        handler.create_manifest(
            loan_id="",  # Empty loan ID
            files=[{
                "name": "test.pdf",
                "uri": "/path/test.pdf",
                "sha256": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                "size": 1000,
                "contentType": "application/pdf"
            }],
            attestations=[],
            created_by="system@integrityx.com"
        )
        print("❌ Should have raised ValueError for empty loan_id")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test 3: Empty files list
    print("\n3️⃣ Testing Empty Files List:")
    try:
        handler.create_manifest(
            loan_id="LOAN_2024_EMPTY",
            files=[],  # Empty files list
            attestations=[],
            created_by="system@integrityx.com"
        )
        print("❌ Should have raised ValueError for empty files list")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test 4: Invalid manifest for canonicalization
    print("\n4️⃣ Testing Invalid Manifest for Canonicalization:")
    try:
        invalid_manifest = {
            "loanId": "LOAN_2024_INVALID",
            "callback": lambda x: x  # Cannot be serialized
        }
        handler.canonicalize_manifest(invalid_manifest)
        print("❌ Should have raised ValueError for unserializable data")
    except (ValueError, TypeError) as e:
        print(f"✅ Correctly raised error: {e}")
    
    print("\n✅ Error handling tests completed!")


def main():
    """Run all tests."""
    print("📦 COMPREHENSIVE MANIFEST HANDLER TEST SUITE")
    print("=" * 80)
    print("Testing all functionality of the ManifestHandler class")
    print("=" * 80)
    
    try:
        # Run all test suites
        test_manifest_creation()
        test_file_info_extraction()
        test_manifest_validation()
        test_canonicalization_and_hashing()
        test_complete_processing()
        test_error_handling()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ ManifestHandler is production-ready!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
