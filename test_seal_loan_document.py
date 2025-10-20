#!/usr/bin/env python3
"""
Test script for the new seal_loan_document method in WalacorIntegrityService.

This script demonstrates how to use the new method for sealing loan documents
with borrower information in the Walacor blockchain.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from walacor_service import WalacorIntegrityService

def test_seal_loan_document():
    """Test the new seal_loan_document method."""
    print("🔐 Testing New seal_loan_document Method...")
    
    try:
        # Initialize Walacor service
        print("1. Initializing Walacor service...")
        walacor_service = WalacorIntegrityService()
        print("✅ Walacor service initialized")
        
        # Test data
        loan_id = "LOAN_2025_METHOD_TEST"
        loan_data = {
            "document_type": "Loan Application",
            "loan_amount": 500000,
            "additional_notes": "Test loan with new seal method",
            "created_by": "test_user"
        }
        
        borrower_data = {
            "full_name": "Test Borrower",
            "date_of_birth": "1990-01-01",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "address": {
                "street": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210",
                "country": "United States"
            },
            "ssn_last4": "1234",
            "id_type": "Driver's License",
            "id_last4": "5678",
            "employment_status": "Employed",
            "annual_income": 100000
        }
        
        files = [{
            "filename": "loan-application.pdf",
            "file_type": "application/pdf",
            "file_size": 1024000,
            "upload_timestamp": "2025-10-14T21:30:00.000Z",
            "content_hash": "abc123def456"
        }]
        
        print("\n2. Testing seal_loan_document method...")
        # Test the new method
        result = walacor_service.seal_loan_document(
            loan_id=loan_id,
            loan_data=loan_data,
            borrower_data=borrower_data,
            files=files
        )
        
        print("✅ Loan document sealed successfully!")
        
        # Display results
        print(f"\n📊 Results:")
        print(f"  Transaction ID: {result['walacor_tx_id']}")
        print(f"  Document Hash: {result['document_hash'][:16]}...")
        print(f"  Sealed At: {result['sealed_timestamp']}")
        print(f"  ETID: {result['blockchain_proof']['etid']}")
        print(f"  Network: {result['blockchain_proof']['blockchain_network']}")
        print(f"  Envelope Size: {result['envelope_metadata']['envelope_size']} bytes")
        print(f"  File Count: {result['envelope_metadata']['file_count']}")
        print(f"  Borrower Data Included: {result['envelope_metadata']['borrower_data_included']}")
        
        print(f"\n🔍 Blockchain Proof:")
        proof = result['blockchain_proof']
        print(f"  Transaction ID: {proof['transaction_id']}")
        print(f"  Integrity Verified: {proof['integrity_verified']}")
        print(f"  Immutability Established: {proof['immutability_established']}")
        
        print(f"\n📁 Envelope Metadata:")
        metadata = result['envelope_metadata']
        print(f"  Loan ID: {metadata['loan_id']}")
        print(f"  Schema Version: {metadata['schema_version']}")
        print(f"  Envelope Size: {metadata['envelope_size']} bytes")
        print(f"  File Count: {metadata['file_count']}")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_seal_loan_document()
    sys.exit(0 if success else 1)

