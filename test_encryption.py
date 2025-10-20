#!/usr/bin/env python3
"""
Test script for the encryption service.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from encryption_service import EncryptionService

def test_encryption_service():
    """Test the encryption service functionality."""
    print("🔐 Testing Encryption Service...")
    
    try:
        # Initialize encryption service
        print("1. Initializing encryption service...")
        encryption_service = EncryptionService()
        print("✅ Encryption service initialized")
        
        # Test data
        test_borrower_data = {
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "ssn_last4": "1234",
            "id_last4": "5678",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "90210",
                "country": "United States"
            },
            "employment_status": "Employed",
            "annual_income": 75000
        }
        
        print("\n2. Testing field encryption...")
        # Test individual field encryption
        test_email = "test@example.com"
        encrypted_email = encryption_service.encrypt_field(test_email)
        decrypted_email = encryption_service.decrypt_field(encrypted_email)
        
        print(f"Original: {test_email}")
        print(f"Encrypted: {encrypted_email[:50]}...")
        print(f"Decrypted: {decrypted_email}")
        print(f"✅ Field encryption/decryption successful: {test_email == decrypted_email}")
        
        print("\n3. Testing borrower data encryption...")
        # Test borrower data encryption
        encrypted_data = encryption_service.encrypt_borrower_data(test_borrower_data)
        print("✅ Borrower data encrypted")
        
        # Check which fields were encrypted
        print("\nEncrypted fields:")
        for field in ['email', 'phone', 'ssn_last4', 'id_last4']:
            if field in encrypted_data:
                original = test_borrower_data[field]
                encrypted = encrypted_data[field]
                print(f"  {field}: {original} -> {encrypted[:30]}...")
        
        if 'address' in encrypted_data and 'street' in encrypted_data['address']:
            original_street = test_borrower_data['address']['street']
            encrypted_street = encrypted_data['address']['street']
            print(f"  address.street: {original_street} -> {encrypted_street[:30]}...")
        
        print("\n4. Testing borrower data decryption...")
        # Test borrower data decryption
        decrypted_data = encryption_service.decrypt_borrower_data(encrypted_data)
        print("✅ Borrower data decrypted")
        
        # Verify decryption
        print("\nVerification:")
        for field in ['email', 'phone', 'ssn_last4', 'id_last4']:
            if field in decrypted_data:
                original = test_borrower_data[field]
                decrypted = decrypted_data[field]
                match = original == decrypted
                print(f"  {field}: {match} ({original} == {decrypted})")
        
        if 'address' in decrypted_data and 'street' in decrypted_data['address']:
            original_street = test_borrower_data['address']['street']
            decrypted_street = decrypted_data['address']['street']
            match = original_street == decrypted_street
            print(f"  address.street: {match} ({original_street} == {decrypted_street})")
        
        print("\n5. Testing encryption status detection...")
        # Test encryption status detection
        status = encryption_service.get_encryption_status(encrypted_data)
        print("Encryption status:")
        for field, is_encrypted in status.items():
            print(f"  {field}: {'🔒 Encrypted' if is_encrypted else '🔓 Plain'}")
        
        print("\n🎉 All encryption tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_encryption_service()
    sys.exit(0 if success else 1)

