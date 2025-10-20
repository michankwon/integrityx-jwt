"""
Encryption Service for Sensitive Borrower Data

This module provides encryption and decryption capabilities for sensitive borrower information
using Fernet symmetric encryption from the cryptography library.

Features:
- Automatic encryption key generation and management
- Field-level encryption for sensitive borrower data
- GDPR-compliant data protection
- Secure key storage in environment variables
- Comprehensive logging without exposing sensitive data

Sensitive fields encrypted:
- ssn_last4: Social Security Number last 4 digits
- id_last4: Government ID last 4 digits  
- phone: Full phone number
- email: Email address (GDPR compliance)
- address_line1, address_line2: Street address information
"""

import os
import base64
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class EncryptionService:
    """
    Service for encrypting and decrypting sensitive borrower data.
    
    Uses Fernet symmetric encryption to protect sensitive fields in borrower information.
    Automatically generates and manages encryption keys stored in environment variables.
    """
    
    # Sensitive fields that require encryption
    SENSITIVE_FIELDS = {
        'ssn_last4',
        'id_last4', 
        'phone',
        'email',
        'address_line1',
        'address_line2'
    }
    
    # Address fields that need special handling
    ADDRESS_FIELDS = {
        'street': 'address_line1',  # Map 'street' to 'address_line1' for encryption
        'address_line1': 'address_line1',
        'address_line2': 'address_line2'
    }
    
    def __init__(self, env_file_path: Optional[str] = None):
        """
        Initialize the encryption service.
        
        Loads or generates encryption key from environment variables.
        If no key exists, generates a new one and saves it to .env file.
        
        Args:
            env_file_path (Optional[str]): Path to .env file. Defaults to None (auto-detect)
            
        Raises:
            ValueError: If unable to load or generate encryption key
        """
        try:
            # Load environment variables
            if env_file_path:
                load_dotenv(env_file_path)
            else:
                load_dotenv()
            
            # Get or generate encryption key
            encryption_key = self._get_or_generate_key()
            
            # Initialize Fernet cipher
            self.cipher = Fernet(encryption_key)
            
            logger.info("✅ Encryption service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption service: {e}")
            raise ValueError(f"Encryption service initialization failed: {e}")
    
    def _get_or_generate_key(self) -> bytes:
        """
        Get encryption key from environment or generate a new one.
        
        Returns:
            bytes: Encryption key for Fernet cipher
            
        Raises:
            ValueError: If unable to load or generate key
        """
        try:
            # Try to get existing key from environment
            key_str = os.getenv('ENCRYPTION_KEY')
            
            if key_str:
                logger.info("Loading existing encryption key from environment")
                return key_str.encode()
            
            # Generate new key if none exists
            logger.info("No encryption key found, generating new key")
            new_key = Fernet.generate_key()
            key_str = new_key.decode()
            
            # Save to .env file
            self._save_key_to_env(key_str)
            
            logger.info("✅ New encryption key generated and saved to .env file")
            return new_key
            
        except Exception as e:
            logger.error(f"Failed to get or generate encryption key: {e}")
            raise ValueError(f"Encryption key management failed: {e}")
    
    def _save_key_to_env(self, key_str: str) -> None:
        """
        Save encryption key to .env file.
        
        Args:
            key_str (str): Encryption key as string
        """
        try:
            env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
            
            # Read existing .env content
            existing_content = ""
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # Check if ENCRYPTION_KEY already exists
            if 'ENCRYPTION_KEY=' in existing_content:
                logger.warning("ENCRYPTION_KEY already exists in .env file, not overwriting")
                return
            
            # Append new key to .env file
            with open(env_file, 'a') as f:
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(f'\n# Encryption key for sensitive data\n')
                f.write(f'ENCRYPTION_KEY={key_str}\n')
            
            logger.info(f"Encryption key saved to {env_file}")
            
        except Exception as e:
            logger.error(f"Failed to save encryption key to .env file: {e}")
            raise
    
    def encrypt_field(self, plaintext: str) -> str:
        """
        Encrypt a single field value.
        
        Args:
            plaintext (str): Plain text to encrypt
            
        Returns:
            str: Base64-encoded encrypted string
            
        Raises:
            ValueError: If encryption fails
        """
        try:
            if not plaintext:
                return plaintext
            
            # Encrypt the plaintext
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            
            # Encode as base64 string
            encrypted_str = base64.b64encode(encrypted_bytes).decode()
            
            logger.debug(f"Field encrypted successfully (length: {len(encrypted_str)})")
            return encrypted_str
            
        except Exception as e:
            logger.error(f"Failed to encrypt field: {e}")
            raise ValueError(f"Field encryption failed: {e}")
    
    def decrypt_field(self, ciphertext: str) -> str:
        """
        Decrypt a single field value.
        
        Args:
            ciphertext (str): Base64-encoded encrypted string
            
        Returns:
            str: Decrypted plain text
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            if not ciphertext:
                return ciphertext
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(ciphertext.encode())
            
            # Decrypt the bytes
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Convert back to string
            plaintext = decrypted_bytes.decode()
            
            logger.debug(f"Field decrypted successfully (length: {len(plaintext)})")
            return plaintext
            
        except Exception as e:
            logger.error(f"Failed to decrypt field: {e}")
            raise ValueError(f"Field decryption failed: {e}")
    
    def encrypt_borrower_data(self, borrower_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in borrower data.
        
        Args:
            borrower_dict (Dict[str, Any]): Borrower data dictionary
            
        Returns:
            Dict[str, Any]: Borrower data with sensitive fields encrypted
        """
        try:
            if not borrower_dict:
                return borrower_dict
            
            encrypted_data = borrower_dict.copy()
            encrypted_count = 0
            
            # Encrypt direct sensitive fields
            for field in self.SENSITIVE_FIELDS:
                if field in encrypted_data and encrypted_data[field]:
                    original_value = encrypted_data[field]
                    encrypted_data[field] = self.encrypt_field(str(original_value))
                    encrypted_count += 1
                    logger.debug(f"Encrypted field: {field}")
            
            # Handle address fields specially
            if 'address' in encrypted_data and isinstance(encrypted_data['address'], dict):
                address = encrypted_data['address'].copy()
                
                # Map 'street' to 'address_line1' for encryption
                if 'street' in address and address['street']:
                    address['street'] = self.encrypt_field(str(address['street']))
                    encrypted_count += 1
                    logger.debug("Encrypted address field: street")
                
                # Encrypt other address fields
                for addr_field in ['address_line1', 'address_line2']:
                    if addr_field in address and address[addr_field]:
                        address[addr_field] = self.encrypt_field(str(address[addr_field]))
                        encrypted_count += 1
                        logger.debug(f"Encrypted address field: {addr_field}")
                
                encrypted_data['address'] = address
            
            logger.info(f"✅ Encrypted {encrypted_count} sensitive fields in borrower data")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Failed to encrypt borrower data: {e}")
            raise ValueError(f"Borrower data encryption failed: {e}")
    
    def decrypt_borrower_data(self, borrower_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in borrower data.
        
        Args:
            borrower_dict (Dict[str, Any]): Borrower data with encrypted fields
            
        Returns:
            Dict[str, Any]: Borrower data with sensitive fields decrypted
        """
        try:
            if not borrower_dict:
                return borrower_dict
            
            decrypted_data = borrower_dict.copy()
            decrypted_count = 0
            
            # Decrypt direct sensitive fields
            for field in self.SENSITIVE_FIELDS:
                if field in decrypted_data and decrypted_data[field]:
                    try:
                        encrypted_value = decrypted_data[field]
                        decrypted_data[field] = self.decrypt_field(str(encrypted_value))
                        decrypted_count += 1
                        logger.debug(f"Decrypted field: {field}")
                    except Exception as e:
                        # If decryption fails, assume field is not encrypted
                        logger.debug(f"Field {field} appears to be unencrypted: {e}")
            
            # Handle address fields specially
            if 'address' in decrypted_data and isinstance(decrypted_data['address'], dict):
                address = decrypted_data['address'].copy()
                
                # Decrypt 'street' field
                if 'street' in address and address['street']:
                    try:
                        address['street'] = self.decrypt_field(str(address['street']))
                        decrypted_count += 1
                        logger.debug("Decrypted address field: street")
                    except Exception as e:
                        logger.debug(f"Address field 'street' appears to be unencrypted: {e}")
                
                # Decrypt other address fields
                for addr_field in ['address_line1', 'address_line2']:
                    if addr_field in address and address[addr_field]:
                        try:
                            address[addr_field] = self.decrypt_field(str(address[addr_field]))
                            decrypted_count += 1
                            logger.debug(f"Decrypted address field: {addr_field}")
                        except Exception as e:
                            logger.debug(f"Address field {addr_field} appears to be unencrypted: {e}")
                
                decrypted_data['address'] = address
            
            logger.info(f"✅ Decrypted {decrypted_count} sensitive fields in borrower data")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Failed to decrypt borrower data: {e}")
            raise ValueError(f"Borrower data decryption failed: {e}")
    
    def is_encrypted_field(self, value: str) -> bool:
        """
        Check if a field value appears to be encrypted.
        
        Args:
            value (str): Field value to check
            
        Returns:
            bool: True if value appears to be encrypted
        """
        try:
            if not value:
                return False
            
            # Try to decode as base64 and decrypt
            base64.b64decode(value.encode())
            return True
            
        except Exception:
            return False
    
    def get_encryption_status(self, borrower_dict: Dict[str, Any]) -> Dict[str, bool]:
        """
        Get encryption status for all sensitive fields in borrower data.
        
        Args:
            borrower_dict (Dict[str, Any]): Borrower data to check
            
        Returns:
            Dict[str, bool]: Field names mapped to encryption status
        """
        status = {}
        
        # Check direct sensitive fields
        for field in self.SENSITIVE_FIELDS:
            if field in borrower_dict:
                status[field] = self.is_encrypted_field(str(borrower_dict[field]))
        
        # Check address fields
        if 'address' in borrower_dict and isinstance(borrower_dict['address'], dict):
            address = borrower_dict['address']
            for addr_field in ['street', 'address_line1', 'address_line2']:
                if addr_field in address:
                    status[f"address.{addr_field}"] = self.is_encrypted_field(str(address[addr_field]))
        
        return status


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None

def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Returns:
        EncryptionService: Global encryption service instance
    """
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    
    return _encryption_service

