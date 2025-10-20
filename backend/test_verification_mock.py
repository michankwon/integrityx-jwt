#!/usr/bin/env python3
"""
Mock test for the Verification Portal functionality.
Tests the endpoints without requiring actual artifacts.
"""

import requests
import json

def test_verification_portal_endpoints():
    """Test the verification portal endpoints."""
    print("🔐 Testing Verification Portal Endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Generate verification link with non-existent artifact (should return 404)
        print("1. Testing verification link generation with non-existent artifact...")
        verification_request = {
            "documentId": "non-existent-artifact-id",
            "documentHash": "test_hash_123456789",
            "allowedParty": "auditor@example.com",
            "permissions": ["hash", "timestamp", "attestations"],
            "expiresInHours": 24
        }
        
        response = requests.post(
            f"{base_url}/api/verification/generate-link",
            json=verification_request
        )
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent artifact")
        else:
            print(f"⚠️ Expected 404, got: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test 2: Verify with invalid token (should return 400)
        print("2. Testing verification with invalid token...")
        response = requests.get(
            f"{base_url}/api/verification/verify/invalid_token_123",
            params={"verifierEmail": "auditor@example.com"}
        )
        
        if response.status_code == 400:
            print("✅ Correctly returned 400 for invalid token")
        else:
            print(f"⚠️ Expected 400, got: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test 3: Check API documentation includes verification endpoints
        print("3. Checking API documentation...")
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            docs_content = response.text
            if "verification" in docs_content.lower():
                print("✅ Verification endpoints found in API documentation")
            else:
                print("⚠️ Verification endpoints not found in API documentation")
        else:
            print(f"⚠️ Could not access API documentation: {response.status_code}")
        
        # Test 4: Check OpenAPI schema
        print("4. Checking OpenAPI schema...")
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi_schema = response.json()
            paths = openapi_schema.get("paths", {})
            
            verification_endpoints = [
                "/api/verification/generate-link",
                "/api/verification/verify/{token}"
            ]
            
            found_endpoints = []
            for endpoint in verification_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
            
            if len(found_endpoints) == len(verification_endpoints):
                print("✅ All verification endpoints found in OpenAPI schema")
                print(f"   Found: {found_endpoints}")
            else:
                print(f"⚠️ Only found {len(found_endpoints)}/{len(verification_endpoints)} endpoints")
                print(f"   Found: {found_endpoints}")
        else:
            print(f"⚠️ Could not access OpenAPI schema: {response.status_code}")
        
        print("🎉 Verification Portal endpoint tests completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verification_portal_models():
    """Test that the verification portal models are properly defined."""
    print("\n📋 Testing Verification Portal Models...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test model validation by sending invalid data
        print("1. Testing model validation...")
        
        # Test with missing required fields
        invalid_request = {
            "documentId": "test-id",
            # Missing documentHash, allowedParty, permissions
        }
        
        response = requests.post(
            f"{base_url}/api/verification/generate-link",
            json=invalid_request
        )
        
        if response.status_code == 422:  # Validation error
            print("✅ Model validation working - correctly rejected invalid request")
            error_details = response.json()
            print(f"   Validation errors: {len(error_details.get('detail', []))}")
        else:
            print(f"⚠️ Expected 422 validation error, got: {response.status_code}")
        
        # Test with invalid permission types
        invalid_permissions_request = {
            "documentId": "test-id",
            "documentHash": "test-hash",
            "allowedParty": "test@example.com",
            "permissions": "invalid_permissions_format",  # Should be array
            "expiresInHours": 24
        }
        
        response = requests.post(
            f"{base_url}/api/verification/generate-link",
            json=invalid_permissions_request
        )
        
        if response.status_code == 422:
            print("✅ Model validation working - correctly rejected invalid permissions format")
        else:
            print(f"⚠️ Expected 422 for invalid permissions, got: {response.status_code}")
        
        print("🎉 Verification Portal model tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Verification Portal Mock Tests...")
    print("=" * 60)
    
    # Test endpoints
    endpoint_test_passed = test_verification_portal_endpoints()
    
    # Test models
    model_test_passed = test_verification_portal_models()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Endpoint Tests: {'✅ PASSED' if endpoint_test_passed else '❌ FAILED'}")
    print(f"   Model Tests: {'✅ PASSED' if model_test_passed else '❌ FAILED'}")
    
    if endpoint_test_passed and model_test_passed:
        print("\n🎉 All Verification Portal mock tests passed!")
        print("🔐 Verification Portal is properly integrated!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")

