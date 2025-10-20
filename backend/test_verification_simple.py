#!/usr/bin/env python3
"""
Simple test for the Verification Portal functionality.
"""

import requests
import json
import tempfile
import os

def test_verification_portal_simple():
    """Test the verification portal with a simple approach."""
    print("🔐 Testing Verification Portal (Simple)...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Create a test JSON file and upload it
        print("1. Creating and uploading test artifact...")
        
        test_data = {
            "loan_id": "VERIFICATION_TEST_001",
            "borrower_name": "John Doe",
            "loan_amount": 500000,
            "created_by": "test_user"
        }
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file_path = f.name
        
        try:
            # Upload the file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.json', f, 'application/json')}
                data = {
                    'loan_id': 'VERIFICATION_TEST_001',
                    'created_by': 'test_user'
                }
                
                response = requests.post(f"{base_url}/api/ingest-json", files=files, data=data)
                
                if response.status_code != 200:
                    print(f"❌ Failed to create test artifact: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                artifact_id = response.json()["data"]["artifact_id"]
                print(f"✅ Created test artifact: {artifact_id}")
        
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
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
        
        # Step 4: Test privacy preservation
        print("4. Testing privacy preservation...")
        response_text = json.dumps(verification_result)
        sensitive_fields = ["borrower_name", "loan_amount", "John Doe", "500000"]
        
        privacy_violations = []
        for field in sensitive_fields:
            if field in response_text:
                privacy_violations.append(field)
        
        if privacy_violations:
            print(f"❌ Privacy violation detected! Sensitive data exposed: {privacy_violations}")
            return False
        
        print("✅ Privacy preservation test passed - no sensitive data exposed")
        
        print("🎉 Verification Portal test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Verification Portal Test...")
    print("=" * 60)
    
    test_passed = test_verification_portal_simple()
    
    print("\n" + "=" * 60)
    if test_passed:
        print("🎉 Verification Portal test PASSED!")
        print("🔐 Privacy-preserving verification system is working correctly!")
    else:
        print("❌ Verification Portal test FAILED!")

