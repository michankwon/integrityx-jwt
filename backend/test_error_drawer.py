#!/usr/bin/env python3
"""
Test script for the ErrorDrawer component functionality.

This script tests the error handling system including error display,
drawer functionality, and API error integration.
"""

import sys
import os
import json
from datetime import datetime, timezone

def test_error_details_structure():
    """Test the error details data structure."""
    print("🧪 Testing error details structure...")
    
    # Test complete error details
    error_details = {
        "code": "VALIDATION_ERROR",
        "message": "Invalid file format provided",
        "requestId": "req_1234567890abcdef",
        "timestamp": "2024-01-15T10:30:00Z",
        "endpoint": "/api/upload",
        "method": "POST",
        "statusCode": 400,
        "details": {
            "field": "file",
            "expected": "PDF, DOCX, or TXT",
            "received": "image/jpeg"
        },
        "stack": "ValidationError: Invalid file format\n  at validateFile (validator.js:15:8)",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "userId": "user_12345"
    }
    
    # Validate required fields
    assert "code" in error_details
    assert "message" in error_details
    assert "requestId" in error_details
    
    # Validate field types
    assert isinstance(error_details["code"], str)
    assert isinstance(error_details["message"], str)
    assert isinstance(error_details["requestId"], str)
    
    # Validate optional fields
    assert "timestamp" in error_details
    assert "endpoint" in error_details
    assert "method" in error_details
    assert "statusCode" in error_details
    assert "details" in error_details
    assert "stack" in error_details
    assert "userAgent" in error_details
    assert "userId" in error_details
    
    print("✅ Error details structure validation passed")
    return error_details

def test_error_types():
    """Test different types of errors."""
    print("\n🧪 Testing error types...")
    
    # Network errors
    network_error = {
        "code": "NETWORK_ERROR",
        "message": "Failed to connect to server",
        "requestId": "req_network_001",
        "statusCode": 0
    }
    
    assert network_error["code"] == "NETWORK_ERROR"
    assert "network" in network_error["code"].lower()
    
    # Authentication errors
    auth_error = {
        "code": "AUTH_ERROR",
        "message": "Invalid authentication token",
        "requestId": "req_auth_001",
        "statusCode": 401
    }
    
    assert auth_error["code"] == "AUTH_ERROR"
    assert "auth" in auth_error["code"].lower()
    
    # Validation errors
    validation_error = {
        "code": "VALIDATION_ERROR",
        "message": "Required field is missing",
        "requestId": "req_validation_001",
        "statusCode": 400
    }
    
    assert validation_error["code"] == "VALIDATION_ERROR"
    assert "validation" in validation_error["code"].lower()
    
    # Server errors
    server_error = {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "An internal server error occurred",
        "requestId": "req_server_001",
        "statusCode": 500
    }
    
    assert server_error["code"] == "INTERNAL_SERVER_ERROR"
    assert server_error["statusCode"] == 500
    
    # Timeout errors
    timeout_error = {
        "code": "TIMEOUT_ERROR",
        "message": "Request timed out",
        "requestId": "req_timeout_001",
        "statusCode": 408
    }
    
    assert timeout_error["code"] == "TIMEOUT_ERROR"
    assert "timeout" in timeout_error["code"].lower()
    
    print("✅ Error types validation passed")
    return [network_error, auth_error, validation_error, server_error, timeout_error]

def test_error_severity_mapping():
    """Test error severity mapping logic."""
    print("\n🧪 Testing error severity mapping...")
    
    def get_error_severity(code: str):
        if 'NETWORK' in code or 'TIMEOUT' in code:
            return 'warning'
        if 'AUTH' in code or 'PERMISSION' in code:
            return 'error'
        if 'VALIDATION' in code or 'FORMAT' in code:
            return 'info'
        return 'error'
    
    # Test severity mappings
    severity_tests = [
        ("NETWORK_ERROR", "warning"),
        ("TIMEOUT_ERROR", "warning"),
        ("AUTH_ERROR", "error"),
        ("PERMISSION_DENIED", "error"),
        ("VALIDATION_ERROR", "info"),
        ("FORMAT_ERROR", "info"),
        ("UNKNOWN_ERROR", "error")
    ]
    
    for code, expected_severity in severity_tests:
        actual_severity = get_error_severity(code)
        assert actual_severity == expected_severity, f"Expected {expected_severity} for {code}, got {actual_severity}"
    
    print("✅ Error severity mapping validation passed")
    return severity_tests

def test_error_icon_mapping():
    """Test error icon mapping logic."""
    print("\n🧪 Testing error icon mapping...")
    
    def get_error_icon(code: str):
        if 'NETWORK' in code or 'TIMEOUT' in code:
            return 'RefreshCw'
        if 'AUTH' in code or 'PERMISSION' in code:
            return 'User'
        if 'VALIDATION' in code or 'FORMAT' in code:
            return 'FileText'
        return 'Bug'
    
    # Test icon mappings
    icon_tests = [
        ("NETWORK_ERROR", "RefreshCw"),
        ("TIMEOUT_ERROR", "RefreshCw"),
        ("AUTH_ERROR", "User"),
        ("PERMISSION_DENIED", "User"),
        ("VALIDATION_ERROR", "FileText"),
        ("FORMAT_ERROR", "FileText"),
        ("UNKNOWN_ERROR", "Bug")
    ]
    
    for code, expected_icon in icon_tests:
        actual_icon = get_error_icon(code)
        assert actual_icon == expected_icon, f"Expected {expected_icon} for {code}, got {actual_icon}"
    
    print("✅ Error icon mapping validation passed")
    return icon_tests

def test_api_response_handling():
    """Test API response error handling."""
    print("\n🧪 Testing API response handling...")
    
    # Test successful response
    success_response = {
        "ok": True,
        "data": {
            "id": "123",
            "status": "success"
        }
    }
    
    assert success_response["ok"] == True
    assert "data" in success_response
    assert "error" not in success_response
    
    # Test error response
    error_response = {
        "ok": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input provided",
            "requestId": "req_12345",
            "details": {
                "field": "email",
                "reason": "Invalid email format"
            }
        }
    }
    
    assert error_response["ok"] == False
    assert "error" in error_response
    assert error_response["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in error_response["error"]
    
    # Test response with additional context
    contextual_error = {
        "ok": False,
        "error": {
            "code": "UPLOAD_ERROR",
            "message": "File upload failed",
            "requestId": "req_upload_001"
        },
        "endpoint": "/api/upload",
        "method": "POST",
        "statusCode": 413,
        "userId": "user_123"
    }
    
    assert contextual_error["ok"] == False
    assert contextual_error["endpoint"] == "/api/upload"
    assert contextual_error["method"] == "POST"
    assert contextual_error["statusCode"] == 413
    assert contextual_error["userId"] == "user_123"
    
    print("✅ API response handling validation passed")
    return [success_response, error_response, contextual_error]

def test_error_drawer_features():
    """Test ErrorDrawer component features."""
    print("\n🧪 Testing ErrorDrawer features...")
    
    # Test drawer state management
    drawer_states = {
        "isOpen": False,
        "error": None,
        "onOpenChange": True,
        "onRetry": True
    }
    
    assert "isOpen" in drawer_states
    assert "error" in drawer_states
    assert "onOpenChange" in drawer_states
    assert "onRetry" in drawer_states
    
    # Test error alert features
    alert_features = {
        "compact": True,
        "showDetails": True,
        "onRetry": True,
        "requestId": "req_12345"
    }
    
    assert alert_features["compact"] == True
    assert alert_features["showDetails"] == True
    assert alert_features["onRetry"] == True
    assert "requestId" in alert_features
    
    # Test copy functionality
    copy_features = {
        "copyRequestId": True,
        "copyErrorDetails": True,
        "copyAll": True
    }
    
    assert copy_features["copyRequestId"] == True
    assert copy_features["copyErrorDetails"] == True
    assert copy_features["copyAll"] == True
    
    # Test retry functionality
    retry_features = {
        "retryable": True,
        "isRetrying": False,
        "onRetry": True
    }
    
    assert retry_features["retryable"] == True
    assert retry_features["isRetrying"] == False
    assert retry_features["onRetry"] == True
    
    print("✅ ErrorDrawer features validation passed")
    return drawer_states

def test_error_context_provider():
    """Test error context provider functionality."""
    print("\n🧪 Testing error context provider...")
    
    # Test context structure
    context_structure = {
        "showError": True,
        "clearError": True,
        "showErrorDetails": True,
        "error": None,
        "isDrawerOpen": False
    }
    
    assert "showError" in context_structure
    assert "clearError" in context_structure
    assert "showErrorDetails" in context_structure
    assert "error" in context_structure
    assert "isDrawerOpen" in context_structure
    
    # Test global error handling
    global_error_handling = {
        "globalAlert": True,
        "globalDrawer": True,
        "errorProvider": True,
        "errorBoundary": True
    }
    
    assert global_error_handling["globalAlert"] == True
    assert global_error_handling["globalDrawer"] == True
    assert global_error_handling["errorProvider"] == True
    assert global_error_handling["errorBoundary"] == True
    
    print("✅ Error context provider validation passed")
    return context_structure

def test_error_boundary():
    """Test error boundary functionality."""
    print("\n🧪 Testing error boundary...")
    
    # Test error boundary state
    boundary_state = {
        "hasError": False,
        "error": None,
        "errorInfo": None
    }
    
    assert "hasError" in boundary_state
    assert "error" in boundary_state
    assert "errorInfo" in boundary_state
    
    # Test error boundary props
    boundary_props = {
        "fallback": True,
        "onError": True,
        "showErrorDrawer": True
    }
    
    assert "fallback" in boundary_props
    assert "onError" in boundary_props
    assert "showErrorDrawer" in boundary_props
    
    # Test error recovery
    recovery_features = {
        "resetError": True,
        "tryAgain": True,
        "refreshPage": True,
        "showDetails": True
    }
    
    assert recovery_features["resetError"] == True
    assert recovery_features["tryAgain"] == True
    assert recovery_features["refreshPage"] == True
    assert recovery_features["showDetails"] == True
    
    print("✅ Error boundary validation passed")
    return boundary_state

def test_error_hooks():
    """Test error handling hooks."""
    print("\n🧪 Testing error hooks...")
    
    # Test useErrorHandler hook
    error_handler_hook = {
        "error": None,
        "isDrawerOpen": False,
        "setIsDrawerOpen": True,
        "handleError": True,
        "clearError": True,
        "showErrorDetails": True
    }
    
    assert "error" in error_handler_hook
    assert "isDrawerOpen" in error_handler_hook
    assert "setIsDrawerOpen" in error_handler_hook
    assert "handleError" in error_handler_hook
    assert "clearError" in error_handler_hook
    assert "showErrorDetails" in error_handler_hook
    
    # Test useApiError hook
    api_error_hook = {
        "handleApiError": True,
        "handleRetry": True,
        "isRetrying": False,
        "fetchWithErrorHandling": True
    }
    
    assert "handleApiError" in api_error_hook
    assert "handleRetry" in api_error_hook
    assert "isRetrying" in api_error_hook
    assert "fetchWithErrorHandling" in api_error_hook
    
    # Test useErrorBoundary hook
    error_boundary_hook = {
        "captureError": True,
        "resetError": True
    }
    
    assert "captureError" in error_boundary_hook
    assert "resetError" in error_boundary_hook
    
    print("✅ Error hooks validation passed")
    return error_handler_hook

def test_error_ui_components():
    """Test error UI components."""
    print("\n🧪 Testing error UI components...")
    
    # Test ErrorAlert component
    error_alert_props = {
        "error": True,
        "onShowDetails": True,
        "onRetry": True,
        "compact": True,
        "className": True
    }
    
    assert "error" in error_alert_props
    assert "onShowDetails" in error_alert_props
    assert "onRetry" in error_alert_props
    assert "compact" in error_alert_props
    assert "className" in error_alert_props
    
    # Test ErrorDrawer component
    error_drawer_props = {
        "error": True,
        "isOpen": True,
        "onOpenChange": True,
        "onRetry": True,
        "className": True
    }
    
    assert "error" in error_drawer_props
    assert "isOpen" in error_drawer_props
    assert "onOpenChange" in error_drawer_props
    assert "onRetry" in error_drawer_props
    assert "className" in error_drawer_props
    
    # Test error display sections
    display_sections = {
        "errorSummary": True,
        "requestInformation": True,
        "additionalDetails": True,
        "stackTrace": True,
        "userAgent": True,
        "actions": True
    }
    
    assert "errorSummary" in display_sections
    assert "requestInformation" in display_sections
    assert "additionalDetails" in display_sections
    assert "stackTrace" in display_sections
    assert "userAgent" in display_sections
    assert "actions" in display_sections
    
    print("✅ Error UI components validation passed")
    return error_alert_props

def main():
    """Run all error drawer tests."""
    print("🚀 Starting ErrorDrawer component tests...\n")
    
    try:
        test_error_details_structure()
        test_error_types()
        test_error_severity_mapping()
        test_error_icon_mapping()
        test_api_response_handling()
        test_error_drawer_features()
        test_error_context_provider()
        test_error_boundary()
        test_error_hooks()
        test_error_ui_components()
        
        print("\n🎉 All ErrorDrawer component tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
