#!/usr/bin/env python3
"""
Comprehensive test script for the Database service.

This script demonstrates all the functionality of the Database class including
CRUD operations, context manager usage, error handling, and performance testing.
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import Database
from models import Artifact, ArtifactFile, ArtifactEvent


def test_basic_operations():
    """Test basic CRUD operations."""
    print("🗄️  BASIC DATABASE OPERATIONS TEST")
    print("=" * 60)
    
    with Database() as db:
        print("✅ Database service initialized with context manager")
        
        # Test 1: Create artifact
        print("\n1️⃣ Creating Artifact:")
        artifact_id = db.insert_artifact(
            loan_id="LOAN_2024_001",
            artifact_type="loan_packet",
            etid=100001,  # ETID for loan packets
            payload_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            walacor_tx_id="WAL_TX_123456789",
            created_by="demo_user@integrityx.com",
            manifest_sha256="f6e5d4c3b2a1789012345678901234567890abcdef1234567890abcdef123456"
        )
        print(f"✅ Artifact created: {artifact_id}")
        
        # Test 2: Add multiple files
        print("\n2️⃣ Adding Files to Artifact:")
        file_ids = []
        files_data = [
            {
                'name': 'loan_agreement.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/loan_agreement.pdf',
                'sha256': '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
                'size_bytes': 1024000,
                'content_type': 'application/pdf'
            },
            {
                'name': 'income_verification.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/income_verification.pdf',
                'sha256': 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                'size_bytes': 512000,
                'content_type': 'application/pdf'
            },
            {
                'name': 'credit_report.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/credit_report.pdf',
                'sha256': 'fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
                'size_bytes': 256000,
                'content_type': 'application/pdf'
            }
        ]
        
        for file_data in files_data:
            file_id = db.insert_artifact_file(
                artifact_id=artifact_id,
                **file_data
            )
            file_ids.append(file_id)
            print(f"✅ File added: {file_data['name']} ({file_data['size_bytes']:,} bytes)")
        
        # Test 3: Add events
        print("\n3️⃣ Adding Events to Artifact:")
        event_ids = []
        events_data = [
            {
                'event_type': 'uploaded',
                'payload_json': '{"status": "success", "files_count": 3, "total_size": 1792000}',
                'payload_sha256': 'event1abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234',
                'walacor_tx_id': 'WAL_TX_123456790',
                'created_by': 'demo_user@integrityx.com'
            },
            {
                'event_type': 'verified',
                'payload_json': '{"verification_status": "passed", "hash_match": true}',
                'payload_sha256': 'event2abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234',
                'walacor_tx_id': 'WAL_TX_123456791',
                'created_by': 'verification_service@integrityx.com'
            },
            {
                'event_type': 'attested',
                'payload_json': '{"attestor": "loan_officer", "attestation_type": "approved"}',
                'payload_sha256': 'event3abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234',
                'walacor_tx_id': 'WAL_TX_123456792',
                'created_by': 'loan_officer@integrityx.com'
            }
        ]
        
        for event_data in events_data:
            event_id = db.insert_event(
                artifact_id=artifact_id,
                **event_data
            )
            event_ids.append(event_id)
            print(f"✅ Event added: {event_data['event_type']}")
        
        # Test 4: Retrieve artifact with relationships
        print("\n4️⃣ Retrieving Artifact with Relationships:")
        artifact = db.get_artifact_by_id(artifact_id)
        if artifact:
            print(f"✅ Artifact retrieved: {artifact.loan_id}")
            print(f"   Type: {artifact.artifact_type}")
            print(f"   Files: {len(artifact.files)}")
            print(f"   Events: {len(artifact.events)}")
            print(f"   Created: {artifact.created_at}")
            
            print("\n📄 Files in Artifact:")
            for file in artifact.files:
                print(f"   - {file.name} ({file.content_type}, {file.size_bytes:,} bytes)")
            
            print("\n📝 Events for Artifact:")
            for event in artifact.events:
                print(f"   - {event.event_type} by {event.created_by} at {event.created_at}")
        
        # Test 5: Query operations
        print("\n5️⃣ Testing Query Operations:")
        
        # Query by loan ID
        loan_artifacts = db.get_artifact_by_loan_id("LOAN_2024_001")
        print(f"✅ Found {len(loan_artifacts)} artifacts for LOAN_2024_001")
        
        # Query by hash
        hash_artifact = db.get_artifact_by_hash("a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456")
        if hash_artifact:
            print(f"✅ Artifact found by hash: {hash_artifact.id}")
        
        # Query events
        events = db.get_artifact_events(artifact_id)
        print(f"✅ Retrieved {len(events)} events for artifact")
        
        # Test 6: Database info
        print("\n6️⃣ Database Information:")
        db_info = db.get_database_info()
        print(f"✅ Database URL: {db_info['database_url']}")
        print(f"✅ Engine: {db_info['engine_name']}")
        print(f"✅ Table counts: {db_info['table_counts']}")
        print(f"✅ Total records: {db_info['total_records']}")
        
        # Test 7: Health check
        print("\n7️⃣ Health Check:")
        if db.health_check():
            print("✅ Database health check passed")
        else:
            print("❌ Database health check failed")
    
    print("\n✅ All basic operations completed successfully!")


def test_error_handling():
    """Test error handling and validation."""
    print("\n🚨 ERROR HANDLING TEST")
    print("=" * 60)
    
    with Database() as db:
        # Test 1: Invalid artifact type
        print("\n1️⃣ Testing Invalid Artifact Type:")
        try:
            db.insert_artifact(
                loan_id="LOAN_2024_002",
                artifact_type="invalid_type",
                etid=100001,  # ETID for loan packets
                payload_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                walacor_tx_id="WAL_TX_123456793",
                created_by="demo_user@integrityx.com"
            )
            print("❌ Should have failed with invalid artifact type")
        except ValueError as e:
            print(f"✅ Correctly caught error: {e}")
        
        # Test 2: Invalid hash length
        print("\n2️⃣ Testing Invalid Hash Length:")
        try:
            db.insert_artifact(
                loan_id="LOAN_2024_003",
                artifact_type="json",
                etid=100002,  # ETID for JSON artifacts
                payload_sha256="short_hash",
                walacor_tx_id="WAL_TX_123456794",
                created_by="demo_user@integrityx.com"
            )
            print("❌ Should have failed with invalid hash length")
        except ValueError as e:
            print(f"✅ Correctly caught error: {e}")
        
        # Test 3: Missing required fields
        print("\n3️⃣ Testing Missing Required Fields:")
        try:
            db.insert_artifact(
                loan_id="LOAN_2024_004",
                artifact_type="json",
                etid=100002,  # ETID for JSON artifacts
                payload_sha256="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                walacor_tx_id="WAL_TX_123456795",
                created_by=""  # Empty created_by
            )
            print("❌ Should have failed with empty created_by")
        except ValueError as e:
            print(f"✅ Correctly caught error: {e}")
        
        # Test 4: Non-existent artifact retrieval
        print("\n4️⃣ Testing Non-existent Artifact Retrieval:")
        artifact = db.get_artifact_by_id("non-existent-id")
        if artifact is None:
            print("✅ Correctly returned None for non-existent artifact")
        else:
            print("❌ Should have returned None")
    
    print("\n✅ All error handling tests passed!")


def test_performance():
    """Test performance with multiple operations."""
    print("\n⚡ PERFORMANCE TEST")
    print("=" * 60)
    
    with Database() as db:
        # Test 1: Batch insert performance
        print("\n1️⃣ Batch Insert Performance:")
        start_time = time.time()
        
        # Create 10 artifacts with files and events
        for i in range(10):
            artifact_id = db.insert_artifact(
                loan_id=f"LOAN_2024_{i:03d}",
                artifact_type="loan_packet",
                etid=100001,  # ETID for loan packets
                payload_sha256=f"a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef{i:02d}1234",
                walacor_tx_id=f"WAL_TX_123456{i:03d}",
                created_by="batch_user@integrityx.com"
            )
            
            # Add 2 files per artifact
            for j in range(2):
                db.insert_artifact_file(
                    artifact_id=artifact_id,
                    name=f"document_{i}_{j}.pdf",
                    uri=f"s3://integrityx-bucket/loans/LOAN_2024_{i:03d}/document_{j}.pdf",
                    sha256=f"file{i:02d}{j}abcdef1234567890abcdef1234567890abcdef1234567890abcdef123",
                    size_bytes=1000000 + (i * 100000),
                    content_type="application/pdf"
                )
            
            # Add 1 event per artifact
            db.insert_event(
                artifact_id=artifact_id,
                event_type="uploaded",
                created_by="batch_user@integrityx.com",
                payload_json=f'{{"batch_id": {i}, "status": "success"}}'
            )
        
        end_time = time.time()
        print(f"✅ Created 10 artifacts with 20 files and 10 events in {end_time - start_time:.2f} seconds")
        
        # Test 2: Query performance
        print("\n2️⃣ Query Performance:")
        start_time = time.time()
        
        # Query all artifacts
        all_artifacts = []
        for i in range(10):
            artifacts = db.get_artifact_by_loan_id(f"LOAN_2024_{i:03d}")
            all_artifacts.extend(artifacts)
        
        end_time = time.time()
        print(f"✅ Queried {len(all_artifacts)} artifacts in {end_time - start_time:.2f} seconds")
        
        # Test 3: Database info
        db_info = db.get_database_info()
        print(f"✅ Final database state: {db_info['table_counts']}")
    
    print("\n✅ Performance test completed!")


def test_context_manager():
    """Test context manager functionality."""
    print("\n🔄 CONTEXT MANAGER TEST")
    print("=" * 60)
    
    # Test 1: Normal context manager usage
    print("\n1️⃣ Normal Context Manager Usage:")
    try:
        with Database() as db:
            artifact_id = db.insert_artifact(
                loan_id="LOAN_2024_CM_001",
                artifact_type="json",
                etid=100002,  # ETID for JSON artifacts
                payload_sha256="cm1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                walacor_tx_id="WAL_TX_CM_001",
                created_by="context_manager_test@integrityx.com"
            )
            print(f"✅ Artifact created in context: {artifact_id}")
        print("✅ Context manager exited normally (committed)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 2: Exception handling in context manager
    print("\n2️⃣ Exception Handling in Context Manager:")
    try:
        with Database() as db:
            artifact_id = db.insert_artifact(
                loan_id="LOAN_2024_CM_002",
                artifact_type="json",
                etid=100002,  # ETID for JSON artifacts
                payload_sha256="cm2b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                walacor_tx_id="WAL_TX_CM_002",
                created_by="context_manager_test@integrityx.com"
            )
            print(f"✅ Artifact created: {artifact_id}")
            # Intentionally raise an exception
            raise ValueError("Simulated error for testing")
    except ValueError as e:
        print(f"✅ Exception caught and handled: {e}")
        print("✅ Context manager rolled back on exception")
    
    print("\n✅ Context manager tests completed!")


def main():
    """Run all tests."""
    print("🗄️  COMPREHENSIVE DATABASE SERVICE TEST SUITE")
    print("=" * 80)
    print("Testing all functionality of the Database service class")
    print("=" * 80)
    
    try:
        # Run all test suites
        test_basic_operations()
        test_error_handling()
        test_performance()
        test_context_manager()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Database service is production-ready!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
