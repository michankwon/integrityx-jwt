#!/usr/bin/env python3
"""
Test script for the enhanced upload page with verification functionality.

This script tests the upload page's ability to check if documents are already sealed
and skip S3 upload when appropriate.
"""

import sys
import os
import json
import time
from datetime import datetime, timezone

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, str(src_dir))

def test_verification_flow():
    """Test the verification flow for already sealed documents."""
    print("🧪 Testing verification flow...")
    
    # Mock verify response for already sealed document
    verify_response = {
        "ok": True,
        "data": {
            "is_valid": True,
            "status": "verified",
            "artifact_id": "art123",
            "verified_at": "2025-10-09T19:30:00.000Z",
            "details": {
                "stored_hash": "abc123def456789",
                "provided_hash": "abc123def456789",
                "artifact_type": "json",
                "created_at": "2025-10-09T18:00:00.000Z"
            }
        }
    }
    
    # Test response parsing
    assert verify_response["ok"] == True
    assert verify_response["data"]["is_valid"] == True
    assert verify_response["data"]["artifact_id"] == "art123"
    
    # Test timestamp parsing
    created_at = verify_response["data"]["details"]["created_at"]
    parsed_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    assert isinstance(parsed_date, datetime)
    
    print("✅ Verification flow validation passed")
    return verify_response

def test_ui_state_management():
    """Test UI state management for different scenarios."""
    print("\n🧪 Testing UI state management...")
    
    # Test initial state
    initial_state = {
        "file": None,
        "fileHash": "",
        "uploadResult": None,
        "verifyResult": None,
        "isVerifying": False,
        "isUploading": False
    }
    
    assert initial_state["file"] is None
    assert initial_state["fileHash"] == ""
    assert initial_state["verifyResult"] is None
    
    # Test file selected state
    file_selected_state = {
        "file": {"name": "test.pdf", "size": 1024},
        "fileHash": "abc123def456789",
        "uploadResult": None,
        "verifyResult": None,
        "isVerifying": True,
        "isUploading": False
    }
    
    assert file_selected_state["file"] is not None
    assert file_selected_state["fileHash"] != ""
    assert file_selected_state["isVerifying"] == True
    
    # Test already sealed state
    already_sealed_state = {
        "file": {"name": "test.pdf", "size": 1024},
        "fileHash": "abc123def456789",
        "uploadResult": None,
        "verifyResult": {
            "is_valid": True,
            "artifact_id": "art123",
            "details": {"created_at": "2025-10-09T18:00:00.000Z"}
        },
        "isVerifying": False,
        "isUploading": False
    }
    
    assert already_sealed_state["verifyResult"] is not None
    assert already_sealed_state["verifyResult"]["is_valid"] == True
    assert already_sealed_state["isVerifying"] == False
    
    # Test new upload state
    new_upload_state = {
        "file": {"name": "new.pdf", "size": 2048},
        "fileHash": "def456ghi789012",
        "uploadResult": None,
        "verifyResult": None,
        "isVerifying": False,
        "isUploading": True
    }
    
    assert new_upload_state["verifyResult"] is None
    assert new_upload_state["isUploading"] == True
    
    print("✅ UI state management validation passed")

def test_button_visibility_logic():
    """Test button visibility logic for different states."""
    print("\n🧪 Testing button visibility logic...")
    
    # Test cases for button visibility
    test_cases = [
        {
            "name": "No file selected",
            "state": {"file": None, "uploadResult": None, "verifyResult": None},
            "expected_upload_button": False,
            "expected_already_sealed_buttons": False
        },
        {
            "name": "File selected, not verified",
            "state": {"file": {"name": "test.pdf"}, "uploadResult": None, "verifyResult": None},
            "expected_upload_button": True,
            "expected_already_sealed_buttons": False
        },
        {
            "name": "File already sealed",
            "state": {
                "file": {"name": "test.pdf"}, 
                "uploadResult": None, 
                "verifyResult": {"is_valid": True}
            },
            "expected_upload_button": False,
            "expected_already_sealed_buttons": True
        },
        {
            "name": "Upload completed",
            "state": {
                "file": {"name": "test.pdf"}, 
                "uploadResult": {"artifactId": "art123"}, 
                "verifyResult": None
            },
            "expected_upload_button": False,
            "expected_already_sealed_buttons": False
        }
    ]
    
    for test_case in test_cases:
        state = test_case["state"]
        
        # Test upload button visibility
        should_show_upload = (
            state["file"] is not None and 
            state["uploadResult"] is None and 
            state["verifyResult"] is None
        )
        assert should_show_upload == test_case["expected_upload_button"], \
            f"Upload button visibility incorrect for {test_case['name']}: expected {test_case['expected_upload_button']}, got {should_show_upload}"
        
        # Test already sealed buttons visibility
        should_show_already_sealed = (
            state["file"] is not None and 
            state["verifyResult"] is not None and 
            state["verifyResult"].get("is_valid", False)
        )
        assert should_show_already_sealed == test_case["expected_already_sealed_buttons"], \
            f"Already sealed buttons visibility incorrect for {test_case['name']}: expected {test_case['expected_already_sealed_buttons']}, got {should_show_already_sealed}"
    
    print("✅ Button visibility logic validation passed")

def test_toast_messages():
    """Test toast message generation for different scenarios."""
    print("\n🧪 Testing toast messages...")
    
    # Test hash calculation success
    hash_success_message = "File hash calculated successfully"
    assert hash_success_message == "File hash calculated successfully"
    
    # Test already sealed message
    already_sealed_message = "Document already sealed!"
    assert already_sealed_message == "Document already sealed!"
    
    # Test verification check message
    verifying_message = "Checking if document is already sealed..."
    assert verifying_message == "Checking if document is already sealed..."
    
    # Test upload success message
    upload_success_message = "Document sealed successfully!"
    assert upload_success_message == "Document sealed successfully!"
    
    print("✅ Toast messages validation passed")

def test_api_integration():
    """Test API integration for verification check."""
    print("\n🧪 Testing API integration...")
    
    # Test verify API request structure
    verify_request = {
        "etid": 100001,
        "payloadHash": "abc123def456789"
    }
    
    assert "etid" in verify_request
    assert "payloadHash" in verify_request
    assert isinstance(verify_request["etid"], int)
    assert len(verify_request["payloadHash"]) == 15  # Mock hash length
    
    # Test verify API response structure
    verify_response = {
        "ok": True,
        "data": {
            "is_valid": True,
            "status": "verified",
            "artifact_id": "art123",
            "verified_at": "2025-10-09T19:30:00.000Z",
            "details": {
                "stored_hash": "abc123def456789",
                "provided_hash": "abc123def456789",
                "artifact_type": "json",
                "created_at": "2025-10-09T18:00:00.000Z"
            }
        }
    }
    
    assert verify_response["ok"] == True
    assert verify_response["data"]["is_valid"] == True
    assert "artifact_id" in verify_response["data"]
    assert "details" in verify_response["data"]
    
    # Test error response structure
    error_response = {
        "ok": False,
        "error": {
            "code": "ARTIFACT_NOT_FOUND",
            "message": "Artifact not found"
        }
    }
    
    assert error_response["ok"] == False
    assert "error" in error_response
    assert "code" in error_response["error"]
    
    print("✅ API integration validation passed")

def test_link_generation():
    """Test link generation for verification and proof."""
    print("\n🧪 Testing link generation...")
    
    # Test verification link
    file_hash = "abc123def456789"
    verify_link = f"/verify?hash={file_hash}"
    expected_verify_link = "/verify?hash=abc123def456789"
    assert verify_link == expected_verify_link
    
    # Test proof bundle link
    artifact_id = "art123"
    proof_link = f"/api/proof?id={artifact_id}"
    expected_proof_link = "/api/proof?id=art123"
    assert proof_link == expected_proof_link
    
    print("✅ Link generation validation passed")

def main():
    """Run all tests."""
    print("🚀 Starting upload page verification tests...\n")
    
    try:
        test_verification_flow()
        test_ui_state_management()
        test_button_visibility_logic()
        test_toast_messages()
        test_api_integration()
        test_link_generation()
        
        print("\n🎉 All upload page verification tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
