import sys
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src directory to Python path for local imports
sys.path.append(str(Path(__file__).parent))

from walacor_service import WalacorIntegrityService


# Security Configuration Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.xlsx', '.jpg', '.png']
DANGEROUS_PATTERNS = [b'<script', b'javascript:', b'<?php', b'<iframe', b'<object', b'<embed']
DANGEROUS_CHARS = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
MAX_INPUT_LENGTH = 255
DEFAULT_RATE_LIMIT = 100  # requests per hour


class SecurityManager:
    """
    Comprehensive security manager for the IntegrityX financial document system.
    
    This class implements security best practices including file validation,
    input sanitization, rate limiting, secure token generation, and password
    hashing. It provides defense-in-depth security measures to protect against
    common attack vectors in financial applications.
    
    Key Security Features:
    - File upload validation (type, size, content scanning)
    - Input sanitization to prevent injection attacks
    - Rate limiting to prevent abuse and DoS attacks
    - Cryptographically secure token generation
    - Secure password hashing with salt
    - Malicious content detection
    
    Security Best Practices Implemented:
    - Principle of least privilege
    - Defense in depth
    - Fail secure defaults
    - Input validation and sanitization
    - Rate limiting and abuse prevention
    - Cryptographic security for sensitive operations
    
    Example Usage:
        security = SecurityManager()
        
        # Validate file upload
        result = security.validate_file_upload("document.pdf", file_size, file_content)
        if result['valid']:
            # Process file
            pass
        
        # Sanitize user input
        clean_input = security.sanitize_input(user_input)
        
        # Check rate limits
        if security.check_rate_limit("user123", "upload", 50):
            # Allow action
            pass
    """
    
    def __init__(self):
        """
        Initialize the SecurityManager with empty tracking dictionaries.
        
        In production, these would be stored in a secure database or cache
        with appropriate TTL and cleanup mechanisms.
        """
        # Track failed authentication attempts
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        # Track rate limiting per user/action
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        try:
            self.walacor_service = WalacorIntegrityService()
            print("✅ SecurityManager initialized with comprehensive security controls!")
        except Exception as e:
            print(f"⚠️  SecurityManager initialized in offline mode: {e}")
            self.walacor_service = None
    
    def validate_file_upload(self, filename: str, file_size: int, file_content: bytes) -> Dict[str, Any]:
        """
        Validate file upload for security compliance.
        
        This method performs comprehensive file validation including:
        - File extension whitelist checking
        - File size limits
        - Basic malicious content scanning
        - Security policy compliance
        
        Args:
            filename (str): Name of the uploaded file
            file_size (int): Size of the file in bytes
            file_content (bytes): First 1024 bytes of file content for scanning
        
        Returns:
            Dict[str, Any]: Validation result containing:
                - valid (bool): Whether file passes all security checks
                - error (str): Error message if validation fails
                - warnings (List[str]): Security warnings (if any)
        """
        print("\n🔒 Validating file upload security...")
        print(f"   File: {filename}")
        print(f"   Size: {file_size:,} bytes")
        
        warnings = []
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                "warnings": []
            }
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            return {
                "valid": False,
                "error": f"File size {file_size:,} bytes exceeds maximum allowed size of {MAX_FILE_SIZE:,} bytes",
                "warnings": []
            }
        
        # Check for suspiciously large files (warning)
        if file_size > MAX_FILE_SIZE * 0.8:  # 80% of max size
            warnings.append(f"Large file detected: {file_size:,} bytes")
        
        # Basic malicious content check
        if file_content:
            content_check = self._scan_file_content(file_content)
            if not content_check["safe"]:
                return {
                    "valid": False,
                    "error": f"Potentially malicious content detected: {content_check['reason']}",
                    "warnings": []
                }
            
            if content_check["warnings"]:
                warnings.extend(content_check["warnings"])
        
        # Additional security checks
        if self._is_suspicious_filename(filename):
            warnings.append("Suspicious filename pattern detected")
        
        result = {
            "valid": True,
            "error": None,
            "warnings": warnings
        }
        
        if warnings:
            print(f"⚠️  Security warnings: {len(warnings)}")
            for warning in warnings:
                print(f"   - {warning}")
        else:
            print("✅ File passed all security checks")
        
        return result
    
    def sanitize_input(self, input_str: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        This method removes dangerous characters and patterns that could be
        used in SQL injection, XSS, or other injection attacks. It also
        enforces length limits to prevent buffer overflow attacks.
        
        Args:
            input_str (str): Raw user input to sanitize
        
        Returns:
            str: Sanitized input string safe for processing
        """
        if not input_str:
            return ""
        
        # Convert to string if not already
        sanitized = str(input_str)
        
        # Remove dangerous characters and patterns
        for dangerous_char in DANGEROUS_CHARS:
            sanitized = sanitized.replace(dangerous_char, "")
        
        # Remove additional dangerous patterns
        dangerous_patterns = [
            "script", "javascript", "vbscript", "onload", "onerror",
            "onclick", "onmouseover", "onfocus", "onblur", "onchange"
        ]
        
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        
        # Limit length to prevent buffer overflow
        if len(sanitized) > MAX_INPUT_LENGTH:
            sanitized = sanitized[:MAX_INPUT_LENGTH]
            print(f"⚠️  Input truncated to {MAX_INPUT_LENGTH} characters")
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def check_rate_limit(self, user_id: str, action: str, limit_per_hour: int = DEFAULT_RATE_LIMIT) -> bool:
        """
        Check if user has exceeded rate limits for a specific action.
        
        This method implements sliding window rate limiting to prevent abuse
        and DoS attacks. It tracks attempts per user/action combination and
        enforces hourly limits.
        
        Args:
            user_id (str): Unique identifier for the user
            action (str): Action being performed (e.g., 'upload', 'verify')
            limit_per_hour (int): Maximum attempts allowed per hour
        
        Returns:
            bool: True if within rate limit, False if exceeded
        """
        if not user_id or not action:
            return False
        
        key = f"{user_id}_{action}"
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Initialize if not exists
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old attempts (older than 1 hour)
        self.rate_limits[key] = [
            attempt_time for attempt_time in self.rate_limits[key]
            if attempt_time > one_hour_ago
        ]
        
        # Check if within limit
        current_count = len(self.rate_limits[key])
        if current_count >= limit_per_hour:
            print(f"🚫 Rate limit exceeded for {user_id}: {action} ({current_count}/{limit_per_hour})")
            return False
        
        # Add current attempt
        self.rate_limits[key].append(now)
        
        print(f"✅ Rate limit check passed for {user_id}: {action} ({current_count + 1}/{limit_per_hour})")
        return True
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.
        
        This method uses the secrets module to generate cryptographically
        secure random tokens suitable for authentication, session management,
        and other security-sensitive operations.
        
        Args:
            length (int): Length of token in bytes (default: 32)
        
        Returns:
            str: Cryptographically secure token
        """
        if length < 16:
            raise ValueError("Token length must be at least 16 bytes for security")
        
        token = secrets.token_urlsafe(length)
        print(f"🔑 Generated secure token: {token[:16]}...")
        return token
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using PBKDF2 with salt.
        
        This method implements secure password hashing using PBKDF2-HMAC-SHA256
        with a random salt. This provides protection against rainbow table
        attacks and makes brute force attacks computationally expensive.
        
        Args:
            password (str): Plain text password to hash
        
        Returns:
            str: Hashed password in format "salt$hash"
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate random salt
        salt = secrets.token_hex(16)  # 32 character hex string
        
        # Hash password with salt using PBKDF2
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        # Combine salt and hash
        hashed_password = f"{salt}${hash_bytes.hex()}"
        
        print("🔐 Password hashed securely with salt")
        return hashed_password
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against its stored hash.
        
        This method extracts the salt from the stored hash and re-hashes
        the provided password to verify it matches the stored value.
        
        Args:
            password (str): Plain text password to verify
            stored_hash (str): Stored hash in format "salt$hash"
        
        Returns:
            bool: True if password matches, False otherwise
        """
        if not password or not stored_hash:
            return False
        
        try:
            # Split salt and hash
            salt, hash_hex = stored_hash.split('$', 1)
            
            # Re-hash password with same salt
            hash_bytes = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000  # Same iterations as hash_password
            )
            
            # Compare hashes
            return hash_bytes.hex() == hash_hex
            
        except (ValueError, IndexError):
            print("⚠️  Invalid stored hash format")
            return False
    
    def _scan_file_content(self, content: bytes) -> Dict[str, Any]:
        """
        Scan file content for potentially malicious patterns.
        
        Args:
            content (bytes): File content to scan (first 1024 bytes)
        
        Returns:
            Dict[str, Any]: Scan result with safety status and warnings
        """
        warnings = []
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in content.lower():
                return {
                    "safe": False,
                    "reason": f"Dangerous pattern detected: {pattern.decode()}",
                    "warnings": []
                }
        
        # Check for suspicious file headers
        if content.startswith(b'%PDF'):
            # PDF file - additional checks could be added here
            pass
        elif content.startswith(b'PK'):
            # ZIP-based format (docx, xlsx) - additional checks could be added
            pass
        elif content.startswith(b'\xff\xd8\xff'):
            # JPEG file
            pass
        elif content.startswith(b'\x89PNG'):
            # PNG file
            pass
        else:
            warnings.append("Unknown file format detected")
        
        # Check for embedded scripts in document files
        if b'<script' in content.lower() or b'javascript:' in content.lower():
            return {
                "safe": False,
                "reason": "Embedded script detected in document",
                "warnings": []
            }
        
        return {
            "safe": True,
            "reason": None,
            "warnings": warnings
        }
    
    def _is_suspicious_filename(self, filename: str) -> bool:
        """
        Check if filename contains suspicious patterns.
        
        Args:
            filename (str): Filename to check
        
        Returns:
            bool: True if filename is suspicious
        """
        suspicious_patterns = [
            '..',  # Directory traversal
            'cmd', 'exec', 'system',  # Command execution
            'admin', 'root', 'administrator',  # Privilege escalation
            'backup', 'temp', 'tmp',  # Temporary files
            'test', 'debug', 'dev'  # Development files
        ]
        
        filename_lower = filename.lower()
        for pattern in suspicious_patterns:
            if pattern in filename_lower:
                return True
        
        return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Get current security statistics and status.
        
        Returns:
            Dict[str, Any]: Security statistics including rate limits, failed attempts, etc.
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Count active rate limits
        active_rate_limits = 0
        for key, attempts in self.rate_limits.items():
            recent_attempts = [t for t in attempts if t > one_hour_ago]
            if recent_attempts:
                active_rate_limits += 1
        
        # Count recent failed attempts
        recent_failed_attempts = 0
        for key, attempts in self.failed_attempts.items():
            recent_attempts = [t for t in attempts if t > one_hour_ago]
            recent_failed_attempts += len(recent_attempts)
        
        return {
            "active_rate_limits": active_rate_limits,
            "recent_failed_attempts": recent_failed_attempts,
            "max_file_size": MAX_FILE_SIZE,
            "allowed_extensions": ALLOWED_EXTENSIONS,
            "max_input_length": MAX_INPUT_LENGTH,
            "default_rate_limit": DEFAULT_RATE_LIMIT,
            "security_status": "operational"
        }
    
    def cleanup_old_attempts(self) -> int:
        """
        Clean up old rate limit and failed attempt records.
        
        Returns:
            int: Number of old records cleaned up
        """
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        cleaned_count = 0
        
        # Clean rate limits
        for key in self.rate_limits.keys():
            old_count = len(self.rate_limits[key])
            self.rate_limits[key] = [
                attempt_time for attempt_time in self.rate_limits[key]
                if attempt_time > one_hour_ago
            ]
            new_count = len(self.rate_limits[key])
            cleaned_count += (old_count - new_count)
            
            # Remove empty entries
            if not self.rate_limits[key]:
                del self.rate_limits[key]
        
        # Clean failed attempts
        for key in self.failed_attempts.keys():
            old_count = len(self.failed_attempts[key])
            self.failed_attempts[key] = [
                attempt_time for attempt_time in self.failed_attempts[key]
                if attempt_time > one_hour_ago
            ]
            new_count = len(self.failed_attempts[key])
            cleaned_count += (old_count - new_count)
            
            # Remove empty entries
            if not self.failed_attempts[key]:
                del self.failed_attempts[key]
        
        if cleaned_count > 0:
            print(f"🧹 Cleaned up {cleaned_count} old security records")
        
        return cleaned_count
