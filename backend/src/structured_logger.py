"""
Structured logging utilities for the Walacor Financial Integrity API.

This module provides structured logging capabilities with request tracking,
user identification, and performance metrics while ensuring no secrets are logged.
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from functools import wraps

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
start_time_var: ContextVar[Optional[float]] = ContextVar('start_time', default=None)

# Configure structured logger
logger = logging.getLogger('walacor_api')
logger.setLevel(logging.INFO)

# Create formatter for structured JSON logs
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs."""
    
    def format(self, record):
        # Base log structure
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add request context if available
        if request_id_var.get():
            log_entry['request_id'] = request_id_var.get()
        
        if user_id_var.get():
            log_entry['user_id'] = user_id_var.get()
        
        # Add any extra fields from the record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

# Set up handler with structured formatter
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)

# Prevent duplicate logs
logger.propagate = False


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def sanitize_for_logging(data: Any) -> Any:
    """
    Sanitize data for logging by removing or masking sensitive information.
    
    Args:
        data: The data to sanitize
        
    Returns:
        Sanitized data safe for logging
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key contains sensitive information
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in [
                'password', 'secret', 'key', 'token', 'auth', 'credential',
                'private', 'api_key', 'access_key', 'secret_key', 'walacor_password'
            ]):
                # Mask sensitive values
                if isinstance(value, str) and len(value) > 8:
                    sanitized[key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    sanitized[key] = '***MASKED***'
            else:
                # Recursively sanitize nested data
                sanitized[key] = sanitize_for_logging(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    elif isinstance(data, str):
        # Check for common secret patterns in strings
        if any(pattern in data.lower() for pattern in [
            'password=', 'secret=', 'key=', 'token=', 'auth='
        ]):
            return '***MASKED_STRING***'
        return data
    else:
        return data


def extract_user_id_from_request(request_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract user ID from request data.
    
    Args:
        request_data: The request data to extract user ID from
        
    Returns:
        User ID if found, None otherwise
    """
    # Check common user ID fields
    user_id_fields = ['user_id', 'userId', 'created_by', 'createdBy', 'user']
    
    for field in user_id_fields:
        if field in request_data:
            return str(request_data[field])
    
    # Check nested objects
    for key, value in request_data.items():
        if isinstance(value, dict):
            user_id = extract_user_id_from_request(value)
            if user_id:
                return user_id
    
    return None


def extract_etid_from_request(request_data: Dict[str, Any]) -> Optional[int]:
    """
    Extract ETID from request data.
    
    Args:
        request_data: The request data to extract ETID from
        
    Returns:
        ETID if found, None otherwise
    """
    etid_fields = ['etid', 'entity_type_id', 'entityTypeId']
    
    for field in etid_fields:
        if field in request_data:
            try:
                return int(request_data[field])
            except (ValueError, TypeError):
                continue
    
    return None


def extract_hash_prefix(hash_value: str, prefix_length: int = 8) -> str:
    """
    Extract a prefix from a hash for logging purposes.
    
    Args:
        hash_value: The full hash value
        prefix_length: Length of prefix to extract
        
    Returns:
        Hash prefix for logging
    """
    if not hash_value or not isinstance(hash_value, str):
        return 'none'
    
    return hash_value[:prefix_length] if len(hash_value) >= prefix_length else hash_value


def log_endpoint_request(
    endpoint: str,
    method: str,
    request_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    etid: Optional[int] = None,
    hash_prefix: Optional[str] = None,
    latency_ms: Optional[float] = None,
    result: Optional[str] = None,
    error: Optional[str] = None,
    **extra_fields
):
    """
    Log an endpoint request with structured data.
    
    Args:
        endpoint: The endpoint path
        method: HTTP method
        request_data: Request data (will be sanitized)
        user_id: User ID if available
        etid: Entity Type ID if available
        hash_prefix: Hash prefix for logging
        latency_ms: Request latency in milliseconds
        result: Result status (success, error, etc.)
        error: Error message if applicable
        **extra_fields: Additional fields to include in the log
    """
    # Sanitize request data
    sanitized_data = sanitize_for_logging(request_data) if request_data else None
    
    # Build log entry
    log_entry = {
        'endpoint': endpoint,
        'method': method,
        'result': result or 'unknown',
    }
    
    # Add optional fields
    if user_id:
        log_entry['user_id'] = user_id
    elif user_id_var.get():
        log_entry['user_id'] = user_id_var.get()
    
    if etid is not None:
        log_entry['etid'] = etid
    
    if hash_prefix:
        log_entry['hash_prefix'] = hash_prefix
    
    if latency_ms is not None:
        log_entry['latency_ms'] = round(latency_ms, 2)
    
    if error:
        log_entry['error'] = error
    
    # Add sanitized request data if present
    if sanitized_data:
        log_entry['request_data'] = sanitized_data
    
    # Add extra fields
    log_entry.update(extra_fields)
    
    # Log with appropriate level
    if error:
        logger.error('Endpoint request completed with error', extra={'extra_fields': log_entry})
    else:
        logger.info('Endpoint request completed', extra={'extra_fields': log_entry})


def log_endpoint_start(
    endpoint: str,
    method: str,
    request_data: Optional[Dict[str, Any]] = None,
    **extra_fields
):
    """
    Log the start of an endpoint request.
    
    Args:
        endpoint: The endpoint path
        method: HTTP method
        request_data: Request data (will be sanitized)
        **extra_fields: Additional fields to include in the log
    """
    # Sanitize request data
    sanitized_data = sanitize_for_logging(request_data) if request_data else None
    
    # Build log entry
    log_entry = {
        'endpoint': endpoint,
        'method': method,
        'phase': 'start',
    }
    
    # Add sanitized request data if present
    if sanitized_data:
        log_entry['request_data'] = sanitized_data
    
    # Add extra fields
    log_entry.update(extra_fields)
    
    logger.info('Endpoint request started', extra={'extra_fields': log_entry})


def with_structured_logging(endpoint: str, method: str = 'POST'):
    """
    Decorator to add structured logging to endpoint functions.
    
    Args:
        endpoint: The endpoint path
        method: HTTP method
        
    Returns:
        Decorated function with structured logging
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate request ID
            request_id = generate_request_id()
            request_id_var.set(request_id)
            
            # Record start time
            start_time = time.time()
            start_time_var.set(start_time)
            
            # Extract request data from kwargs (FastAPI dependency injection)
            request_data = {}
            user_id = None
            etid = None
            hash_prefix = None
            
            # Try to extract data from common FastAPI patterns
            for key, value in kwargs.items():
                if hasattr(value, 'dict'):  # Pydantic model
                    request_data[key] = value.dict()
                elif hasattr(value, '__dict__'):  # Object with attributes
                    request_data[key] = str(value)
                elif isinstance(value, (str, int, float, bool)):
                    request_data[key] = value
                else:
                    request_data[key] = str(value)
            
            # Extract user ID, ETID, and hash from request data
            user_id = extract_user_id_from_request(request_data)
            etid = extract_etid_from_request(request_data)
            
            # Look for hash fields
            hash_fields = ['payloadHash', 'payload_hash', 'hash', 'sha256']
            for field in hash_fields:
                if field in request_data:
                    hash_prefix = extract_hash_prefix(str(request_data[field]))
                    break
            
            # Set context variables
            if user_id:
                user_id_var.set(user_id)
            
            # Log request start
            log_endpoint_start(
                endpoint=endpoint,
                method=method,
                request_data=request_data,
                request_id=request_id
            )
            
            result = 'success'
            error = None
            
            try:
                # Execute the endpoint function
                response = await func(*args, **kwargs)
                return response
                
            except Exception as e:
                result = 'error'
                error = str(e)
                raise
                
            finally:
                # Calculate latency
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                # Log request completion
                log_endpoint_request(
                    endpoint=endpoint,
                    method=method,
                    request_data=request_data,
                    user_id=user_id,
                    etid=etid,
                    hash_prefix=hash_prefix,
                    latency_ms=latency_ms,
                    result=result,
                    error=error,
                    request_id=request_id
                )
                
                # Clear context variables
                request_id_var.set(None)
                user_id_var.set(None)
                start_time_var.set(None)
        
        return wrapper
    return decorator


def log_database_operation(
    operation: str,
    table: str,
    record_id: Optional[str] = None,
    latency_ms: Optional[float] = None,
    error: Optional[str] = None,
    **extra_fields
):
    """
    Log a database operation with structured data.
    
    Args:
        operation: Database operation (insert, update, delete, select)
        table: Table name
        record_id: Record ID if applicable
        latency_ms: Operation latency in milliseconds
        error: Error message if applicable
        **extra_fields: Additional fields to include in the log
    """
    log_entry = {
        'operation': operation,
        'table': table,
        'component': 'database',
    }
    
    if record_id:
        log_entry['record_id'] = record_id
    
    if latency_ms is not None:
        log_entry['latency_ms'] = round(latency_ms, 2)
    
    if error:
        log_entry['error'] = error
    
    # Add extra fields
    log_entry.update(extra_fields)
    
    # Log with appropriate level
    if error:
        logger.error('Database operation failed', extra={'extra_fields': log_entry})
    else:
        logger.info('Database operation completed', extra={'extra_fields': log_entry})


def log_external_service_call(
    service: str,
    operation: str,
    latency_ms: Optional[float] = None,
    status_code: Optional[int] = None,
    error: Optional[str] = None,
    **extra_fields
):
    """
    Log an external service call with structured data.
    
    Args:
        service: External service name (walacor, s3, etc.)
        operation: Operation performed
        latency_ms: Call latency in milliseconds
        status_code: HTTP status code if applicable
        error: Error message if applicable
        **extra_fields: Additional fields to include in the log
    """
    log_entry = {
        'service': service,
        'operation': operation,
        'component': 'external_service',
    }
    
    if latency_ms is not None:
        log_entry['latency_ms'] = round(latency_ms, 2)
    
    if status_code is not None:
        log_entry['status_code'] = status_code
    
    if error:
        log_entry['error'] = error
    
    # Add extra fields
    log_entry.update(extra_fields)
    
    # Log with appropriate level
    if error:
        logger.error('External service call failed', extra={'extra_fields': log_entry})
    else:
        logger.info('External service call completed', extra={'extra_fields': log_entry})


# Example usage and testing
if __name__ == "__main__":
    # Test structured logging
    log_endpoint_request(
        endpoint="/api/health",
        method="GET",
        latency_ms=45.2,
        result="success"
    )
    
    log_endpoint_request(
        endpoint="/api/seal",
        method="POST",
        request_data={"etid": 100001, "payloadHash": "abc123def456"},
        user_id="user123",
        etid=100001,
        hash_prefix="abc123de",
        latency_ms=120.5,
        result="success"
    )
    
    log_endpoint_request(
        endpoint="/api/verify",
        method="POST",
        request_data={"etid": 100002, "payloadHash": "def456ghi789"},
        user_id="user456",
        etid=100002,
        hash_prefix="def456gh",
        latency_ms=89.3,
        result="error",
        error="Artifact not found"
    )

