#!/usr/bin/env python3
"""
Test script for the new Attestation and Provenance endpoints.

This script tests the new API endpoints to ensure they work correctly.
"""

import sys
import os
import json
import requests
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_attestation_endpoints():
    """Test attestation endpoints."""
    print("🧪 Testing Attestation endpoints...")
    
    base_url = "http://localhost:8000"
    
    # First, create a test artifact
    print("Creating test artifact...")
    artifact_data = {
        "loan_id": "TEST_LOAN_001",
        "created_by": "test_user"
    }
    
    try:
        response = requests.post(f"{base_url}/api/ingest-json", json=artifact_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact: {response.status_code}")
            return False
        
        artifact_response = response.json()
        if not artifact_response.get("ok"):
            print(f"❌ Failed to create test artifact: {artifact_response}")
            return False
        
        artifact_id = artifact_response["data"]["artifact_id"]
        print(f"✅ Created test artifact: {artifact_id}")
        
        # Test creating an attestation
        print("Creating attestation...")
        attestation_data = {
            "artifactId": artifact_id,
            "etid": "ATTESTATION_ETID_001",
            "kind": "qc_check",
            "issuedBy": "test_user",
            "details": {
                "score": 95,
                "notes": "Quality check passed"
            }
        }
        
        response = requests.post(f"{base_url}/api/attestations", json=attestation_data)
        if response.status_code != 200:
            print(f"❌ Failed to create attestation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        attestation_response = response.json()
        if not attestation_response.get("ok"):
            print(f"❌ Failed to create attestation: {attestation_response}")
            return False
        
        attestation_id = attestation_response["data"]["id"]
        print(f"✅ Created attestation: {attestation_id}")
        
        # Test listing attestations
        print("Listing attestations...")
        response = requests.get(f"{base_url}/api/attestations?artifactId={artifact_id}")
        if response.status_code != 200:
            print(f"❌ Failed to list attestations: {response.status_code}")
            return False
        
        list_response = response.json()
        if not list_response.get("ok"):
            print(f"❌ Failed to list attestations: {list_response}")
            return False
        
        attestations = list_response["data"]["attestations"]
        if len(attestations) != 1:
            print(f"❌ Expected 1 attestation, got {len(attestations)}")
            return False
        
        print(f"✅ Listed {len(attestations)} attestations")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_provenance_endpoints():
    """Test provenance endpoints."""
    print("🧪 Testing Provenance endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Create two test artifacts
        print("Creating test artifacts...")
        artifact1_data = {
            "loan_id": "TEST_LOAN_002",
            "created_by": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ingest-json", json=artifact1_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact 1: {response.status_code}")
            return False
        
        artifact1_id = response.json()["data"]["artifact_id"]
        
        artifact2_data = {
            "loan_id": "TEST_LOAN_003",
            "created_by": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ingest-json", json=artifact2_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact 2: {response.status_code}")
            return False
        
        artifact2_id = response.json()["data"]["artifact_id"]
        
        print(f"✅ Created test artifacts: {artifact1_id}, {artifact2_id}")
        
        # Test creating a provenance link
        print("Creating provenance link...")
        link_data = {
            "parentArtifactId": artifact1_id,
            "childArtifactId": artifact2_id,
            "relation": "contains"
        }
        
        response = requests.post(f"{base_url}/api/provenance/link", json=link_data)
        if response.status_code != 200:
            print(f"❌ Failed to create provenance link: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        link_response = response.json()
        if not link_response.get("ok"):
            print(f"❌ Failed to create provenance link: {link_response}")
            return False
        
        link_id = link_response["data"]["id"]
        print(f"✅ Created provenance link: {link_id}")
        
        # Test listing children
        print("Listing children...")
        response = requests.get(f"{base_url}/api/provenance/children?parentId={artifact1_id}")
        if response.status_code != 200:
            print(f"❌ Failed to list children: {response.status_code}")
            return False
        
        children_response = response.json()
        if not children_response.get("ok"):
            print(f"❌ Failed to list children: {children_response}")
            return False
        
        children = children_response["data"]["children"]
        if len(children) != 1:
            print(f"❌ Expected 1 child, got {len(children)}")
            return False
        
        print(f"✅ Listed {len(children)} children")
        
        # Test listing parents
        print("Listing parents...")
        response = requests.get(f"{base_url}/api/provenance/parents?childId={artifact2_id}")
        if response.status_code != 200:
            print(f"❌ Failed to list parents: {response.status_code}")
            return False
        
        parents_response = response.json()
        if not parents_response.get("ok"):
            print(f"❌ Failed to list parents: {parents_response}")
            return False
        
        parents = parents_response["data"]["parents"]
        if len(parents) != 1:
            print(f"❌ Expected 1 parent, got {len(parents)}")
            return False
        
        print(f"✅ Listed {len(parents)} parents")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_disclosure_pack_endpoint():
    """Test disclosure pack endpoint."""
    print("🧪 Testing Disclosure Pack endpoint...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Create a test artifact
        print("Creating test artifact...")
        artifact_data = {
            "loan_id": "TEST_LOAN_004",
            "created_by": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ingest-json", json=artifact_data)
        if response.status_code != 200:
            print(f"❌ Failed to create test artifact: {response.status_code}")
            return False
        
        artifact_id = response.json()["data"]["artifact_id"]
        print(f"✅ Created test artifact: {artifact_id}")
        
        # Test generating disclosure pack
        print("Generating disclosure pack...")
        response = requests.get(f"{base_url}/api/disclosure-pack?id={artifact_id}")
        if response.status_code != 200:
            print(f"❌ Failed to generate disclosure pack: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Check if it's a ZIP file
        content_type = response.headers.get("content-type")
        if "application/zip" not in content_type:
            print(f"❌ Expected ZIP file, got: {content_type}")
            return False
        
        # Check content disposition
        content_disposition = response.headers.get("content-disposition")
        if f"disclosure_{artifact_id}.zip" not in content_disposition:
            print(f"❌ Expected correct filename, got: {content_disposition}")
            return False
        
        print(f"✅ Generated disclosure pack: {len(response.content)} bytes")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting API endpoint tests...\n")
    
    try:
        # Test attestation endpoints
        attestation_success = test_attestation_endpoints()
        print()
        
        # Test provenance endpoints
        provenance_success = test_provenance_endpoints()
        print()
        
        # Test disclosure pack endpoint
        disclosure_success = test_disclosure_pack_endpoint()
        print()
        
        if attestation_success and provenance_success and disclosure_success:
            print("🎉 All endpoint tests passed!")
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()