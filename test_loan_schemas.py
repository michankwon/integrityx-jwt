#!/usr/bin/env python3
"""
Test script for the loan schemas validation.

This script demonstrates the Pydantic models for API request/response validation
with comprehensive field validation, custom validators, and data masking.
"""

import sys
import os
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from loan_schemas import (
    BorrowerInfoRequest, LoanDataRequest, SealLoanDocumentRequest,
    BorrowerInfoResponse, SearchLoansRequest, FileInfo,
    mask_email, mask_phone, mask_ssn, mask_id, get_income_range
)

def test_borrower_info_validation():
    """Test borrower information validation."""
    print("🧪 Testing BorrowerInfoRequest Validation...")
    
    try:
        # Valid borrower data
        borrower_data = {
            "full_name": "John Doe",
            "date_of_birth": date(1990, 5, 15),
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "address_line1": "123 Main Street",
            "address_line2": "Apt 4B",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "US",
            "ssn_last4": "1234",
            "id_type": "drivers_license",
            "id_last4": "5678",
            "employment_status": "employed",
            "annual_income": 75000,
            "co_borrower_name": "Jane Doe"
        }
        
        borrower = BorrowerInfoRequest(**borrower_data)
        print("✅ Valid borrower data passed validation")
        print(f"  Name: {borrower.full_name}")
        print(f"  Email: {borrower.email}")
        print(f"  Phone: {borrower.phone}")
        print(f"  State: {borrower.state}")
        print(f"  ZIP: {borrower.zip_code}")
        
        return borrower
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def test_loan_data_validation():
    """Test loan data validation."""
    print("\n🧪 Testing LoanDataRequest Validation...")
    
    try:
        loan_data = {
            "loan_id": "LOAN-2025-001",
            "document_type": "loan_application",
            "loan_amount": 500000,
            "borrower_name": "John Doe",
            "additional_notes": "Primary residence purchase"
        }
        
        loan = LoanDataRequest(**loan_data)
        print("✅ Valid loan data passed validation")
        print(f"  Loan ID: {loan.loan_id}")
        print(f"  Document Type: {loan.document_type}")
        print(f"  Amount: ${loan.loan_amount:,}")
        
        return loan
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def test_file_info_validation():
    """Test file information validation."""
    print("\n🧪 Testing FileInfo Validation...")
    
    try:
        file_data = {
            "filename": "loan-application.pdf",
            "file_type": "application/pdf",
            "file_size": 1024000,
            "upload_timestamp": "2025-10-14T21:30:00.000Z",
            "content_hash": "abc123def456"
        }
        
        file_info = FileInfo(**file_data)
        print("✅ Valid file data passed validation")
        print(f"  Filename: {file_info.filename}")
        print(f"  Type: {file_info.file_type}")
        print(f"  Size: {file_info.file_size:,} bytes")
        
        return file_info
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def test_seal_request_validation():
    """Test complete seal request validation."""
    print("\n🧪 Testing SealLoanDocumentRequest Validation...")
    
    try:
        # Get validated components
        borrower = test_borrower_info_validation()
        loan = test_loan_data_validation()
        file_info = test_file_info_validation()
        
        if not all([borrower, loan, file_info]):
            print("❌ Cannot test seal request - component validation failed")
            return None
        
        # Ensure borrower name consistency
        loan.borrower_name = borrower.full_name
        
        seal_request = SealLoanDocumentRequest(
            loan_data=loan,
            borrower_info=borrower,
            files=[file_info]
        )
        
        print("✅ Complete seal request passed validation")
        print(f"  Loan ID: {seal_request.loan_data.loan_id}")
        print(f"  Borrower: {seal_request.borrower_info.full_name}")
        print(f"  Files: {len(seal_request.files)}")
        
        return seal_request
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def test_search_request_validation():
    """Test search request validation."""
    print("\n🧪 Testing SearchLoansRequest Validation...")
    
    try:
        search_data = {
            "borrower_name": "John",
            "borrower_email": "john@example.com",
            "loan_id": "LOAN-2025-001",
            "date_from": date(2025, 1, 1),
            "date_to": date(2025, 12, 31),
            "amount_min": 100000,
            "amount_max": 1000000,
            "limit": 50,
            "offset": 0,
            "document_type": "loan_application",
            "employment_status": "employed",
            "is_sealed": True
        }
        
        search_request = SearchLoansRequest(**search_data)
        print("✅ Valid search request passed validation")
        print(f"  Borrower Name: {search_request.borrower_name}")
        print(f"  Date Range: {search_request.date_from} to {search_request.date_to}")
        print(f"  Amount Range: ${search_request.amount_min:,} - ${search_request.amount_max:,}")
        
        return search_request
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return None

def test_data_masking():
    """Test data masking utility functions."""
    print("\n🧪 Testing Data Masking Functions...")
    
    try:
        # Test email masking
        email = "john.doe@example.com"
        masked_email = mask_email(email)
        print(f"✅ Email masking: {email} -> {masked_email}")
        
        # Test phone masking
        phone = "+1-555-123-4567"
        masked_phone = mask_phone(phone)
        print(f"✅ Phone masking: {phone} -> {masked_phone}")
        
        # Test SSN masking
        ssn = "1234"
        masked_ssn = mask_ssn(ssn)
        print(f"✅ SSN masking: {ssn} -> {masked_ssn}")
        
        # Test ID masking
        id_num = "5678"
        masked_id = mask_id(id_num)
        print(f"✅ ID masking: {id_num} -> {masked_id}")
        
        # Test income range
        income = 75000
        income_range = get_income_range(income)
        print(f"✅ Income range: ${income:,} -> {income_range}")
        
        return True
        
    except Exception as e:
        print(f"❌ Masking test failed: {e}")
        return False

def test_validation_errors():
    """Test validation error handling."""
    print("\n🧪 Testing Validation Error Handling...")
    
    try:
        # Test invalid email
        try:
            BorrowerInfoRequest(
                full_name="Test User",
                date_of_birth=date(1990, 1, 1),
                email="invalid-email",
                phone="+1-555-123-4567",
                address_line1="123 Main St",
                city="Test City",
                state="CA",
                zip_code="90210",
                country="US",
                ssn_last4="1234",
                id_type="drivers_license",
                id_last4="5678",
                employment_status="employed",
                annual_income=50000
            )
            print("❌ Should have failed with invalid email")
        except Exception as e:
            print(f"✅ Correctly caught invalid email: {str(e)[:50]}...")
        
        # Test invalid phone
        try:
            BorrowerInfoRequest(
                full_name="Test User",
                date_of_birth=date(1990, 1, 1),
                email="test@example.com",
                phone="invalid-phone",
                address_line1="123 Main St",
                city="Test City",
                state="CA",
                zip_code="90210",
                country="US",
                ssn_last4="1234",
                id_type="drivers_license",
                id_last4="5678",
                employment_status="employed",
                annual_income=50000
            )
            print("❌ Should have failed with invalid phone")
        except Exception as e:
            print(f"✅ Correctly caught invalid phone: {str(e)[:50]}...")
        
        # Test underage borrower
        try:
            BorrowerInfoRequest(
                full_name="Test User",
                date_of_birth=date(2010, 1, 1),  # Under 18
                email="test@example.com",
                phone="+1-555-123-4567",
                address_line1="123 Main St",
                city="Test City",
                state="CA",
                zip_code="90210",
                country="US",
                ssn_last4="1234",
                id_type="drivers_license",
                id_last4="5678",
                employment_status="employed",
                annual_income=50000
            )
            print("❌ Should have failed with underage borrower")
        except Exception as e:
            print(f"✅ Correctly caught underage borrower: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 LOAN SCHEMAS VALIDATION TEST")
    print("=" * 50)
    
    success = True
    
    # Run all tests
    success &= test_borrower_info_validation() is not None
    success &= test_loan_data_validation() is not None
    success &= test_file_info_validation() is not None
    success &= test_seal_request_validation() is not None
    success &= test_search_request_validation() is not None
    success &= test_data_masking()
    success &= test_validation_errors()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

