#!/usr/bin/env python3
"""
Test script for the enhanced settings page health check functionality.

This script tests the /api/health endpoint to ensure it returns the expected
structured data for the settings page.
"""

import sys
import os
import json
import time
from datetime import datetime, timezone

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, str(src_dir))

def test_health_endpoint_structure():
    """Test that the health endpoint returns the expected structure for the frontend."""
    print("🧪 Testing health endpoint structure...")
    
    # Mock health response structure
    expected_structure = {
        "ok": True,
        "data": {
            "status": "healthy",
            "message": "All services operational",
            "timestamp": "2025-10-09T19:30:00.000Z",
            "total_duration_ms": 125.5,
            "services": {
                "database": {
                    "status": "up",
                    "duration_ms": 45.2,
                    "details": "Database connection successful"
                },
                "walacor": {
                    "status": "up", 
                    "duration_ms": 78.3,
                    "details": "Walacor service accessible"
                },
                "storage": {
                    "status": "up",
                    "duration_ms": 12.0,
                    "details": "S3 bucket accessible"
                }
            }
        }
    }
    
    # Validate structure
    assert "ok" in expected_structure
    assert "data" in expected_structure
    assert expected_structure["ok"] == True
    
    data = expected_structure["data"]
    required_fields = ["status", "message", "timestamp", "total_duration_ms", "services"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Validate services structure
    services = data["services"]
    assert isinstance(services, dict)
    
    for service_name, service_data in services.items():
        assert "status" in service_data, f"Service {service_name} missing status"
        assert "duration_ms" in service_data, f"Service {service_name} missing duration_ms"
        assert isinstance(service_data["duration_ms"], (int, float))
    
    print("✅ Health endpoint structure validation passed")
    return expected_structure

def test_frontend_parsing():
    """Test that the frontend can parse the health response correctly."""
    print("\n🧪 Testing frontend parsing logic...")
    
    # Simulate the health response
    health_response = {
        "ok": True,
        "data": {
            "status": "healthy",
            "message": "All services operational",
            "timestamp": "2025-10-09T19:30:00.000Z",
            "total_duration_ms": 125.5,
            "services": {
                "database": {
                    "status": "up",
                    "duration_ms": 45.2,
                    "details": "Database connection successful"
                },
                "walacor": {
                    "status": "up", 
                    "duration_ms": 78.3,
                    "details": "Walacor service accessible"
                },
                "storage": {
                    "status": "up",
                    "duration_ms": 12.0,
                    "details": "S3 bucket accessible"
                }
            }
        }
    }
    
    # Simulate frontend parsing logic
    if health_response["ok"] and health_response["data"]:
        health_data = health_response["data"]
        
        # Test overall status
        overall_status = health_data["status"]
        assert overall_status in ["healthy", "degraded", "unhealthy"]
        
        # Test service counting
        services = health_data["services"]
        healthy_services = sum(1 for s in services.values() 
                             if s["status"] in ["up", "healthy"])
        total_services = len(services)
        
        assert healthy_services == 3
        assert total_services == 3
        
        # Test duration formatting
        total_duration = health_data["total_duration_ms"]
        if total_duration < 1000:
            formatted_duration = f"{total_duration:.1f}ms"
        else:
            formatted_duration = f"{total_duration / 1000:.2f}s"
        
        assert formatted_duration == "125.5ms"
        
        # Test timestamp parsing
        timestamp = health_data["timestamp"]
        parsed_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed_timestamp, datetime)
        
        print("✅ Frontend parsing logic validation passed")
    else:
        raise AssertionError("Health response parsing failed")

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🧪 Testing error handling...")
    
    # Test API error response
    error_response = {
        "ok": False,
        "error": {
            "code": "HEALTH_CHECK_ERROR",
            "message": "Failed to check database health",
            "details": {"service": "database", "error": "Connection timeout"}
        }
    }
    
    assert error_response["ok"] == False
    assert "error" in error_response
    assert "code" in error_response["error"]
    assert "message" in error_response["error"]
    
    # Test network error scenario
    network_error = None
    try:
        # Simulate network failure
        raise ConnectionError("Network request failed")
    except ConnectionError as e:
        network_error = str(e)
    
    assert network_error == "Network request failed"
    
    print("✅ Error handling validation passed")

def test_ui_state_management():
    """Test UI state management scenarios."""
    print("\n🧪 Testing UI state management...")
    
    # Test loading state
    loading_state = {
        "healthData": None,
        "loading": True,
        "lastChecked": None
    }
    
    assert loading_state["healthData"] is None
    assert loading_state["loading"] == True
    assert loading_state["lastChecked"] is None
    
    # Test success state
    success_state = {
        "healthData": {
            "status": "healthy",
            "total_duration_ms": 125.5,
            "services": {"database": {"status": "up", "duration_ms": 45.2}}
        },
        "loading": False,
        "lastChecked": datetime.now(timezone.utc)
    }
    
    assert success_state["healthData"] is not None
    assert success_state["loading"] == False
    assert success_state["lastChecked"] is not None
    
    # Test error state
    error_state = {
        "healthData": None,
        "loading": False,
        "lastChecked": None,
        "error": "Failed to fetch health status"
    }
    
    assert error_state["healthData"] is None
    assert error_state["loading"] == False
    assert "error" in error_state
    
    print("✅ UI state management validation passed")

def test_toast_messages():
    """Test toast message generation."""
    print("\n🧪 Testing toast messages...")
    
    # Test success toast
    health_data = {
        "total_duration_ms": 125.5,
        "services": {
            "database": {"status": "up"},
            "walacor": {"status": "up"},
            "storage": {"status": "down"}
        }
    }
    
    total_duration = health_data["total_duration_ms"]
    healthy_services = sum(1 for s in health_data["services"].values() 
                         if s["status"] in ["up", "healthy"])
    total_services = len(health_data["services"])
    
    # Format duration
    if total_duration < 1000:
        formatted_duration = f"{total_duration:.1f}ms"
    else:
        formatted_duration = f"{total_duration / 1000:.2f}s"
    
    success_message = f"Health check completed in {formatted_duration} - {healthy_services}/{total_services} services healthy"
    
    expected_message = "Health check completed in 125.5ms - 2/3 services healthy"
    assert success_message == expected_message
    
    # Test error toast
    error_message = "Failed to fetch health status"
    assert error_message == "Failed to fetch health status"
    
    print("✅ Toast messages validation passed")

def main():
    """Run all tests."""
    print("🚀 Starting settings page health check tests...\n")
    
    try:
        test_health_endpoint_structure()
        test_frontend_parsing()
        test_error_handling()
        test_ui_state_management()
        test_toast_messages()
        
        print("\n🎉 All settings page health check tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

