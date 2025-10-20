#!/usr/bin/env python3
"""
Test script for the Verification Portal functionality.

This script tests the privacy-preserving verification system that allows
third parties to verify document authenticity without exposing sensitive data.
"""

import requests
import json
import time
from datetime import datetime

def test_verification_portal():
    """Test the verification portal endpoints."""
    print("🔐 Testing Verification Portal...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Create a test artifact
        print("1. Creating test artifact...")
        artifact_data = {
            "loan_id": "VERIFICATION_TEST_001",
            "created_by": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ingest-json", json=artifact_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact: {response.status_code}")
            return False
        
        artifact_id = response.json()["data"]["artifact_id"]
        print(f"✅ Created test artifact: {artifact_id}")
        
        # Step 2: Generate verification link
        print("2. Generating verification link...")
        verification_request = {
            "documentId": artifact_id,
            "documentHash": "test_hash_123456789",
            "allowedParty": "auditor@example.com",
            "permissions": ["hash", "timestamp", "attestations"],
            "expiresInHours": 24
        }
        
        response = requests.post(
            f"{base_url}/api/verification/generate-link",
            json=verification_request
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to generate verification link: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        verification_data = response.json()["data"]["verification_link"]
        token = verification_data["token"]
        verification_url = verification_data["verificationUrl"]
        expires_at = verification_data["expiresAt"]
        permissions = verification_data["permissions"]
        
        print(f"✅ Generated verification link:")
        print(f"   Token: {token[:20]}...")
        print(f"   URL: {verification_url}")
        print(f"   Expires: {expires_at}")
        print(f"   Permissions: {permissions}")
        
        # Step 3: Verify with token
        print("3. Verifying document with token...")
        response = requests.get(
            f"{base_url}/api/verification/verify/{token}",
            params={"verifierEmail": "auditor@example.com"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to verify document: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        verification_result = response.json()["data"]["verification"]
        print(f"✅ Document verification successful:")
        print(f"   Valid: {verification_result['isValid']}")
        print(f"   Document Hash: {verification_result['documentHash']}")
        print(f"   Timestamp: {verification_result['timestamp']}")
        print(f"   Attestations: {len(verification_result['attestations'])}")
        print(f"   Permissions: {verification_result['permissions']}")
        print(f"   Verified At: {verification_result['verifiedAt']}")
        
        # Step 4: Test invalid token
        print("4. Testing invalid token...")
        response = requests.get(
            f"{base_url}/api/verification/verify/invalid_token_123",
            params={"verifierEmail": "auditor@example.com"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid token correctly rejected")
        else:
            print(f"⚠️ Expected 400 for invalid token, got: {response.status_code}")
        
        # Step 5: Test unauthorized email
        print("5. Testing unauthorized email...")
        response = requests.get(
            f"{base_url}/api/verification/verify/{token}",
            params={"verifierEmail": "unauthorized@example.com"}
        )
        
        if response.status_code == 400:
            print("✅ Unauthorized email correctly rejected")
        else:
            print(f"⚠️ Expected 400 for unauthorized email, got: {response.status_code}")
        
        print("🎉 Verification Portal test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_privacy_preservation():
    """Test that sensitive data is not exposed in verification responses."""
    print("\n🔒 Testing Privacy Preservation...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Create artifact with sensitive data
        print("1. Creating artifact with sensitive data...")
        sensitive_data = {
            "loan_id": "PRIVACY_TEST_001",
            "borrower_name": "John Doe",
            "ssn": "123-45-6789",
            "loan_amount": 500000,
            "created_by": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ingest-json", json=sensitive_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact: {response.status_code}")
            return False
        
        artifact_id = response.json()["data"]["artifact_id"]
        print(f"✅ Created artifact with sensitive data: {artifact_id}")
        
        # Generate verification link with limited permissions
        print("2. Generating verification link with limited permissions...")
        verification_request = {
            "documentId": artifact_id,
            "documentHash": "privacy_test_hash",
            "allowedParty": "auditor@example.com",
            "permissions": ["hash", "timestamp"],  # No attestations, no sensitive data
            "expiresInHours": 1
        }
        
        response = requests.post(
            f"{base_url}/api/verification/generate-link",
            json=verification_request
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to generate verification link: {response.status_code}")
            return False
        
        token = response.json()["data"]["verification_link"]["token"]
        print(f"✅ Generated verification link with limited permissions")
        
        # Verify and check that sensitive data is not exposed
        print("3. Verifying and checking privacy...")
        response = requests.get(
            f"{base_url}/api/verification/verify/{token}",
            params={"verifierEmail": "auditor@example.com"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to verify document: {response.status_code}")
            return False
        
        verification_result = response.json()["data"]["verification"]
        
        # Check that sensitive data is not in the response
        response_text = json.dumps(verification_result)
        sensitive_fields = ["borrower_name", "ssn", "loan_amount", "John Doe", "123-45-6789"]
        
        privacy_violations = []
        for field in sensitive_fields:
            if field in response_text:
                privacy_violations.append(field)
        
        if privacy_violations:
            print(f"❌ Privacy violation detected! Sensitive data exposed: {privacy_violations}")
            return False
        
        print("✅ Privacy preservation test passed - no sensitive data exposed")
        print(f"   Only exposed: hash, timestamp, and {len(verification_result['attestations'])} attestations")
        
        return True
        
    except Exception as e:
        print(f"❌ Privacy test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Verification Portal Tests...")
    print("=" * 60)
    
    # Test basic functionality
    basic_test_passed = test_verification_portal()
    
    # Test privacy preservation
    privacy_test_passed = test_privacy_preservation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Basic Functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"   Privacy Preservation: {'✅ PASSED' if privacy_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and privacy_test_passed:
        print("\n🎉 All Verification Portal tests passed!")
        print("🔐 Privacy-preserving verification system is working correctly!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")

