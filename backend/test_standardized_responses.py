#!/usr/bin/env python3
"""
Test script for standardized API responses.

This script tests the new standardized response format across all endpoints.
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timezone

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_response_models():
    """Test the standardized response models."""
    print("🧪 Testing standardized response models...")
    
    try:
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, Any
        
        # Define the models inline
        class ErrorDetail(BaseModel):
            code: str = Field(..., description="Error code")
            message: str = Field(..., description="Error message")
            details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
        
        class StandardResponse(BaseModel):
            ok: bool = Field(..., description="Success status")
            data: Optional[Dict[str, Any]] = Field(None, description="Response data")
            error: Optional[ErrorDetail] = Field(None, description="Error information")
        
        # Test success response
        success_response = StandardResponse(
            ok=True,
            data={
                "message": "Operation successful",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": {"id": "123", "status": "completed"}
            }
        )
        print("✅ Success response model works")
        
        # Test error response
        error_response = StandardResponse(
            ok=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid input provided",
                details={"field": "email", "issue": "invalid format"}
            )
        )
        print("✅ Error response model works")
        
        # Test serialization
        success_dict = success_response.dict()
        error_dict = error_response.dict()
        
        assert success_dict["ok"] == True
        assert error_dict["ok"] == False
        assert error_dict["error"]["code"] == "VALIDATION_ERROR"
        
        print("✅ Response serialization works")
        print("🎉 All response models work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Response model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_helper_functions():
    """Test the helper functions for creating responses."""
    print("\n🧪 Testing response helper functions...")
    
    try:
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, Any
        
        # Define the models inline
        class ErrorDetail(BaseModel):
            code: str = Field(..., description="Error code")
            message: str = Field(..., description="Error message")
            details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
        
        class StandardResponse(BaseModel):
            ok: bool = Field(..., description="Success status")
            data: Optional[Dict[str, Any]] = Field(None, description="Response data")
            error: Optional[ErrorDetail] = Field(None, description="Error information")
        
        # Define helper functions
        def create_success_response(data: Dict[str, Any]) -> StandardResponse:
            """Create a standardized success response."""
            return StandardResponse(ok=True, data=data)
        
        def create_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> StandardResponse:
            """Create a standardized error response."""
            return StandardResponse(
                ok=False,
                error=ErrorDetail(code=code, message=message, details=details)
            )
        
        # Test success response creation
        test_data = {
            "user_id": "123",
            "name": "John Doe",
            "email": "john@example.com"
        }
        success_resp = create_success_response(test_data)
        
        assert success_resp.ok == True
        assert success_resp.data == test_data
        assert success_resp.error is None
        print("✅ Success response helper works")
        
        # Test error response creation
        error_resp = create_error_response(
            code="USER_NOT_FOUND",
            message="User with ID 123 not found",
            details={"user_id": "123", "searched_at": datetime.now(timezone.utc).isoformat()}
        )
        
        assert error_resp.ok == False
        assert error_resp.data is None
        assert error_resp.error.code == "USER_NOT_FOUND"
        assert error_resp.error.message == "User with ID 123 not found"
        assert error_resp.error.details["user_id"] == "123"
        print("✅ Error response helper works")
        
        print("🎉 All helper functions work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_consistency():
    """Test response consistency across different scenarios."""
    print("\n🧪 Testing response consistency...")
    
    try:
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, Any
        
        # Define the models inline
        class ErrorDetail(BaseModel):
            code: str = Field(..., description="Error code")
            message: str = Field(..., description="Error message")
            details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
        
        class StandardResponse(BaseModel):
            ok: bool = Field(..., description="Success status")
            data: Optional[Dict[str, Any]] = Field(None, description="Response data")
            error: Optional[ErrorDetail] = Field(None, description="Error information")
        
        # Test different success scenarios
        scenarios = [
            {
                "name": "Health Check",
                "data": {
                    "status": "healthy",
                    "services": {"db": "up", "walacor": "up"},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            },
            {
                "name": "Document Upload",
                "data": {
                    "artifact_id": "abc123",
                    "walacor_tx_id": "tx456",
                    "sealed_at": datetime.now(timezone.utc).isoformat()
                }
            },
            {
                "name": "Verification Result",
                "data": {
                    "is_valid": True,
                    "status": "ok",
                    "verified_at": datetime.now(timezone.utc).isoformat()
                }
            }
        ]
        
        for scenario in scenarios:
            response = StandardResponse(ok=True, data=scenario["data"])
            
            # Verify structure
            assert response.ok == True
            assert response.data is not None
            assert response.error is None
            
            # Verify data content
            for key, value in scenario["data"].items():
                assert response.data[key] == value
            
            print(f"✅ {scenario['name']} response structure correct")
        
        # Test different error scenarios
        error_scenarios = [
            {
                "name": "Validation Error",
                "code": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "details": {"field": "email", "issue": "invalid format"}
            },
            {
                "name": "Not Found Error",
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "details": {"resource": "artifact", "id": "123"}
            },
            {
                "name": "Server Error",
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": None
            }
        ]
        
        for scenario in error_scenarios:
            response = StandardResponse(
                ok=False,
                error=ErrorDetail(
                    code=scenario["code"],
                    message=scenario["message"],
                    details=scenario["details"]
                )
            )
            
            # Verify structure
            assert response.ok == False
            assert response.data is None
            assert response.error is not None
            assert response.error.code == scenario["code"]
            assert response.error.message == scenario["message"]
            
            print(f"✅ {scenario['name']} error structure correct")
        
        print("🎉 All response consistency tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Response consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_serialization():
    """Test JSON serialization of responses."""
    print("\n🧪 Testing JSON serialization...")
    
    try:
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, Any
        
        # Define the models inline
        class ErrorDetail(BaseModel):
            code: str = Field(..., description="Error code")
            message: str = Field(..., description="Error message")
            details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
        
        class StandardResponse(BaseModel):
            ok: bool = Field(..., description="Success status")
            data: Optional[Dict[str, Any]] = Field(None, description="Response data")
            error: Optional[ErrorDetail] = Field(None, description="Error information")
        
        # Test success response serialization
        success_data = {
            "message": "Operation successful",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": {"id": "123", "status": "completed"}
        }
        success_response = StandardResponse(ok=True, data=success_data)
        success_json = success_response.json()
        success_dict = json.loads(success_json)
        
        assert success_dict["ok"] == True
        assert success_dict["data"]["message"] == "Operation successful"
        assert "timestamp" in success_dict["data"]
        assert success_dict["error"] is None
        print("✅ Success response JSON serialization works")
        
        # Test error response serialization
        error_response = StandardResponse(
            ok=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid input provided",
                details={"field": "email", "issue": "invalid format"}
            )
        )
        error_json = error_response.json()
        error_dict = json.loads(error_json)
        
        assert error_dict["ok"] == False
        assert error_dict["data"] is None
        assert error_dict["error"]["code"] == "VALIDATION_ERROR"
        assert error_dict["error"]["message"] == "Invalid input provided"
        assert error_dict["error"]["details"]["field"] == "email"
        print("✅ Error response JSON serialization works")
        
        # Test round-trip serialization
        original_response = StandardResponse(ok=True, data={"test": "value"})
        serialized = original_response.json()
        deserialized = StandardResponse.parse_raw(serialized)
        
        assert deserialized.ok == original_response.ok
        assert deserialized.data == original_response.data
        print("✅ Round-trip serialization works")
        
        print("🎉 All JSON serialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all standardized response tests."""
    print("🚀 Testing standardized API responses...")
    print("=" * 60)
    
    tests = [
        test_response_models,
        test_helper_functions,
        test_response_consistency,
        test_json_serialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            if await test():
                passed += 1
        else:
            if test():
                passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Standardized responses are ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

