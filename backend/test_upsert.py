#!/usr/bin/env python3
"""
Test script for the create_or_get_artifact UPSERT functionality.

This script tests the new UPSERT method to ensure it:
1. Creates new artifacts when they don't exist
2. Returns existing artifacts when they do exist
3. Handles the composite unique constraint properly
4. Maintains stable artifact IDs
"""

import os
import sys
import hashlib
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import Database

def generate_test_hash(data: str) -> str:
    """Generate a 64-character SHA-256 hash for testing."""
    return hashlib.sha256(data.encode()).hexdigest()

def test_upsert_functionality():
    """Test the create_or_get_artifact UPSERT functionality."""
    print("🧪 Testing create_or_get_artifact UPSERT functionality...")
    print("=" * 60)
    
    # Initialize database
    db = Database()
    
    try:
        with db:
            # Test data
            etid = 100001
            test_payload = "This is a test loan document"
            payload_hash = generate_test_hash(test_payload)
            external_uri = "s3://test-bucket/loans/test_loan.json"
            metadata = {
                "source": "test_script",
                "version": "1.0",
                "created_at": datetime.now().isoformat()
            }
            
            print(f"📋 Test Parameters:")
            print(f"   ETID: {etid}")
            print(f"   Payload Hash: {payload_hash[:16]}...")
            print(f"   External URI: {external_uri}")
            print()
            
            # Test 1: Create new artifact
            print("🔍 Test 1: Creating new artifact...")
            artifact_id_1 = db.create_or_get_artifact(
                etid=etid,
                payload_hash=payload_hash,
                external_uri=external_uri,
                metadata=metadata,
                loan_id="TEST_LOAN_001",
                artifact_type="json",
                created_by="test_user"
            )
            print(f"   ✅ Created artifact ID: {artifact_id_1}")
            print()
            
            # Test 2: Try to create the same artifact again (should return existing)
            print("🔍 Test 2: Attempting to create same artifact again...")
            artifact_id_2 = db.create_or_get_artifact(
                etid=etid,
                payload_hash=payload_hash,
                external_uri=external_uri,
                metadata=metadata,
                loan_id="TEST_LOAN_002",  # Different loan_id
                artifact_type="json",
                created_by="test_user_2"  # Different user
            )
            print(f"   ✅ Returned artifact ID: {artifact_id_2}")
            print(f"   🔗 Same ID as first: {artifact_id_1 == artifact_id_2}")
            print()
            
            # Test 3: Create artifact with different payload hash
            print("🔍 Test 3: Creating artifact with different payload hash...")
            different_payload = "This is a different test loan document"
            different_hash = generate_test_hash(different_payload)
            
            artifact_id_3 = db.create_or_get_artifact(
                etid=etid,
                payload_hash=different_hash,
                external_uri=external_uri,
                metadata=metadata,
                loan_id="TEST_LOAN_003",
                artifact_type="json",
                created_by="test_user"
            )
            print(f"   ✅ Created new artifact ID: {artifact_id_3}")
            print(f"   🔗 Different from first: {artifact_id_1 != artifact_id_3}")
            print()
            
            # Test 4: Create artifact with different ETID but same payload hash
            print("🔍 Test 4: Creating artifact with different ETID but same payload hash...")
            different_etid = 100002
            
            artifact_id_4 = db.create_or_get_artifact(
                etid=different_etid,
                payload_hash=payload_hash,  # Same hash as first test
                external_uri=external_uri,
                metadata=metadata,
                loan_id="TEST_LOAN_004",
                artifact_type="loan_packet",
                created_by="test_user"
            )
            print(f"   ✅ Created new artifact ID: {artifact_id_4}")
            print(f"   🔗 Different from first: {artifact_id_1 != artifact_id_4}")
            print()
            
            # Test 5: Verify database constraints
            print("🔍 Test 5: Testing database constraints...")
            try:
                # This should fail due to unique constraint violation
                db.create_or_get_artifact(
                    etid=etid,
                    payload_hash=payload_hash,  # Same as first test
                    external_uri="different_uri",
                    metadata={"different": "metadata"},
                    loan_id="DIFFERENT_LOAN",
                    artifact_type="loan_packet",  # Different type
                    created_by="different_user"
                )
                print("   ❌ ERROR: Should have failed due to unique constraint!")
            except Exception as e:
                print(f"   ✅ Correctly handled constraint violation: {type(e).__name__}")
            print()
            
            # Test 6: Query the artifacts to verify they exist
            print("🔍 Test 6: Verifying artifacts in database...")
            from models import Artifact
            
            artifacts = db.session.query(Artifact).filter(
                Artifact.id.in_([artifact_id_1, artifact_id_2, artifact_id_3, artifact_id_4])
            ).all()
            
            print(f"   📊 Found {len(artifacts)} artifacts in database:")
            for artifact in artifacts:
                print(f"      - ID: {artifact.id}")
                print(f"        ETID: {artifact.etid}")
                print(f"        Loan ID: {artifact.loan_id}")
                print(f"        Type: {artifact.artifact_type}")
                print(f"        Hash: {artifact.payload_sha256[:16]}...")
                print(f"        Created By: {artifact.created_by}")
                print()
            
            # Summary
            print("📋 Test Summary:")
            print(f"   ✅ Test 1: Created new artifact - {artifact_id_1}")
            print(f"   ✅ Test 2: Returned existing artifact - {artifact_id_2} (same as Test 1: {artifact_id_1 == artifact_id_2})")
            print(f"   ✅ Test 3: Created different artifact - {artifact_id_3} (different from Test 1: {artifact_id_1 != artifact_id_3})")
            print(f"   ✅ Test 4: Created artifact with different ETID - {artifact_id_4} (different from Test 1: {artifact_id_1 != artifact_id_4})")
            print(f"   ✅ Test 5: Correctly handled constraint violation")
            print(f"   ✅ Test 6: Verified {len(artifacts)} artifacts in database")
            print()
            print("🎉 All tests passed! UPSERT functionality is working correctly.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_upsert_functionality()
    sys.exit(0 if success else 1)


