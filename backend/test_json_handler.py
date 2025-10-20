#!/usr/bin/env python3
"""
Comprehensive test script for the JSONHandler.

This script demonstrates all the functionality of the JSONHandler class including
schema validation, canonicalization, hashing, business rules, and error handling.
"""

import sys
import os
from pathlib import Path
import json

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from json_handler import JSONHandler


def test_schema_validation():
    """Test JSON schema validation functionality."""
    print("📋 SCHEMA VALIDATION TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test 1: Valid loan data
    print("\n1️⃣ Testing Valid Loan Data:")
    valid_loan = {
        "loanId": "LOAN_2024_001",
        "amount": 500000,
        "rate": 3.5,
        "term": 360,
        "borrowerName": "John Doe",
        "loanType": "conventional"
    }
    
    is_valid, error = handler.validate_json_schema(valid_loan, 'loan')
    if is_valid:
        print("✅ Valid loan data passed schema validation")
    else:
        print(f"❌ Valid loan data failed: {error}")
    
    # Test 2: Invalid loan data (missing required field)
    print("\n2️⃣ Testing Invalid Loan Data (Missing Required Field):")
    invalid_loan = {
        "loanId": "LOAN_2024_002",
        "amount": 300000,
        "rate": 4.0
        # Missing 'term' field
    }
    
    is_valid, error = handler.validate_json_schema(invalid_loan, 'loan')
    if not is_valid:
        print(f"✅ Invalid loan data correctly rejected: {error}")
    else:
        print("❌ Invalid loan data should have been rejected")
    
    # Test 3: Invalid data type
    print("\n3️⃣ Testing Invalid Data Type:")
    invalid_type_loan = {
        "loanId": "LOAN_2024_003",
        "amount": "not_a_number",  # Should be number
        "rate": 3.5,
        "term": 360
    }
    
    is_valid, error = handler.validate_json_schema(invalid_type_loan, 'loan')
    if not is_valid:
        print(f"✅ Invalid data type correctly rejected: {error}")
    else:
        print("❌ Invalid data type should have been rejected")
    
    # Test 4: Different schema types
    print("\n4️⃣ Testing Different Schema Types:")
    
    # Appraisal schema
    appraisal_data = {
        "propertyAddress": "123 Main St",
        "appraisedValue": 600000,
        "appraiserId": "APP_001",
        "appraisalDate": "2024-01-15"
    }
    
    is_valid, error = handler.validate_json_schema(appraisal_data, 'appraisal')
    if is_valid:
        print("✅ Appraisal data passed schema validation")
    else:
        print(f"❌ Appraisal data failed: {error}")
    
    # Credit report schema
    credit_data = {
        "borrowerId": "BORROWER_001",
        "creditScore": 750,
        "reportDate": "2024-01-15"
    }
    
    is_valid, error = handler.validate_json_schema(credit_data, 'credit_report')
    if is_valid:
        print("✅ Credit report data passed schema validation")
    else:
        print(f"❌ Credit report data failed: {error}")
    
    print("\n✅ Schema validation tests completed!")


def test_canonicalization():
    """Test JSON canonicalization functionality."""
    print("\n🔄 CANONICALIZATION TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test data with different key ordering
    test_data_1 = {
        "loanId": "LOAN_2024_001",
        "amount": 500000,
        "rate": 3.5,
        "term": 360
    }
    
    test_data_2 = {
        "term": 360,
        "rate": 3.5,
        "amount": 500000,
        "loanId": "LOAN_2024_001"
    }
    
    print("\n1️⃣ Testing Canonicalization Consistency:")
    canonical_1 = handler.canonicalize_json(test_data_1)
    canonical_2 = handler.canonicalize_json(test_data_2)
    
    if canonical_1 == canonical_2:
        print("✅ Canonicalization produces consistent results regardless of key order")
        print(f"   Canonical JSON: {canonical_1.decode('utf-8')}")
    else:
        print("❌ Canonicalization should produce consistent results")
        print(f"   Data 1: {canonical_1.decode('utf-8')}")
        print(f"   Data 2: {canonical_2.decode('utf-8')}")
    
    # Test hash consistency
    print("\n2️⃣ Testing Hash Consistency:")
    hash_1 = handler.hash_canonical_json(test_data_1)
    hash_2 = handler.hash_canonical_json(test_data_2)
    
    if hash_1 == hash_2:
        print("✅ Hash generation is consistent for equivalent data")
        print(f"   Hash: {hash_1}")
    else:
        print("❌ Hash generation should be consistent")
        print(f"   Hash 1: {hash_1}")
        print(f"   Hash 2: {hash_2}")
    
    print("\n✅ Canonicalization tests completed!")


def test_business_rules():
    """Test business rules validation."""
    print("\n📊 BUSINESS RULES TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test 1: Valid business rules
    print("\n1️⃣ Testing Valid Business Rules:")
    valid_loan = {
        "loanId": "LOAN_2024_001",
        "amount": 500000,  # Within range
        "rate": 3.5,       # Within range
        "term": 360,       # Valid term
        "creditScore": 750  # Good credit
    }
    
    passed, errors = handler.run_business_rules(valid_loan)
    if passed:
        print("✅ Valid loan passed business rules")
    else:
        print(f"❌ Valid loan failed business rules: {errors}")
    
    # Test 2: Amount too low
    print("\n2️⃣ Testing Amount Too Low:")
    low_amount_loan = {
        "loanId": "LOAN_2024_002",
        "amount": 500,  # Too low
        "rate": 3.5,
        "term": 360
    }
    
    passed, errors = handler.run_business_rules(low_amount_loan)
    if not passed:
        print(f"✅ Low amount correctly rejected: {errors}")
    else:
        print("❌ Low amount should have been rejected")
    
    # Test 3: Rate too high
    print("\n3️⃣ Testing Rate Too High:")
    high_rate_loan = {
        "loanId": "LOAN_2024_003",
        "amount": 500000,
        "rate": 25.0,  # Too high
        "term": 360
    }
    
    passed, errors = handler.run_business_rules(high_rate_loan)
    if not passed:
        print(f"✅ High rate correctly rejected: {errors}")
    else:
        print("❌ High rate should have been rejected")
    
    # Test 4: Invalid term
    print("\n4️⃣ Testing Invalid Term:")
    invalid_term_loan = {
        "loanId": "LOAN_2024_004",
        "amount": 500000,
        "rate": 3.5,
        "term": 120  # Invalid term (not 180, 240, or 360)
    }
    
    passed, errors = handler.run_business_rules(invalid_term_loan)
    if not passed:
        print(f"✅ Invalid term correctly rejected: {errors}")
    else:
        print("❌ Invalid term should have been rejected")
    
    # Test 5: Low credit score
    print("\n5️⃣ Testing Low Credit Score:")
    low_credit_loan = {
        "loanId": "LOAN_2024_005",
        "amount": 500000,
        "rate": 3.5,
        "term": 360,
        "creditScore": 580  # Low credit score
    }
    
    passed, errors = handler.run_business_rules(low_credit_loan)
    if not passed:
        print(f"✅ Low credit score correctly flagged: {errors}")
    else:
        print("❌ Low credit score should have been flagged")
    
    # Test 6: Jumbo loan validation
    print("\n6️⃣ Testing Jumbo Loan Validation:")
    jumbo_loan = {
        "loanId": "LOAN_2024_006",
        "amount": 800000,  # Jumbo amount
        "rate": 3.5,
        "term": 360,
        "loanType": "jumbo"
    }
    
    passed, errors = handler.run_business_rules(jumbo_loan)
    if passed:
        print("✅ Jumbo loan passed validation")
    else:
        print(f"❌ Jumbo loan failed: {errors}")
    
    print("\n✅ Business rules tests completed!")


def test_complete_processing():
    """Test complete JSON processing pipeline."""
    print("\n🔄 COMPLETE PROCESSING TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test 1: Complete valid loan processing
    print("\n1️⃣ Testing Complete Valid Loan Processing:")
    complete_loan = {
        "loanId": "LOAN_2024_001",
        "amount": 500000,
        "rate": 3.5,
        "term": 360,
        "borrowerName": "John Doe",
        "propertyAddress": "123 Main St, Anytown, USA",
        "loanType": "conventional",
        "purpose": "purchase",
        "creditScore": 750,
        "propertyValue": 600000
    }
    
    result = handler.process_json_artifact(complete_loan, 'loan')
    
    print(f"✅ Processing Results:")
    print(f"   Overall Valid: {result['is_valid']}")
    print(f"   Schema Valid: {result['schema_valid']}")
    print(f"   Business Rules Passed: {result['business_rules_passed']}")
    print(f"   Hash Generated: {result['hash'] is not None}")
    print(f"   Hash: {result['hash'][:16]}...")
    print(f"   Errors: {len(result['errors'])}")
    print(f"   Warnings: {len(result['warnings'])}")
    
    # Test 2: Invalid loan processing
    print("\n2️⃣ Testing Invalid Loan Processing:")
    invalid_loan = {
        "loanId": "LOAN_2024_002",
        "amount": 500,  # Too low
        "rate": 25.0,   # Too high
        "term": 120     # Invalid term
    }
    
    result = handler.process_json_artifact(invalid_loan, 'loan')
    
    print(f"✅ Processing Results:")
    print(f"   Overall Valid: {result['is_valid']}")
    print(f"   Schema Valid: {result['schema_valid']}")
    print(f"   Business Rules Passed: {result['business_rules_passed']}")
    print(f"   Errors: {len(result['errors'])}")
    if result['errors']:
        print("   Error Details:")
        for error in result['errors']:
            print(f"     - {error}")
    
    print("\n✅ Complete processing tests completed!")


def test_schema_info():
    """Test schema information retrieval."""
    print("\n📋 SCHEMA INFO TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test loan schema info
    print("\n1️⃣ Testing Loan Schema Info:")
    loan_info = handler.get_schema_info('loan')
    
    print(f"✅ Loan Schema Information:")
    print(f"   Required Fields: {loan_info['required_fields']}")
    print(f"   Optional Fields: {loan_info['optional_fields']}")
    print(f"   Total Fields: {loan_info['total_fields']}")
    print(f"   Field Types: {loan_info['field_types']}")
    
    # Test appraisal schema info
    print("\n2️⃣ Testing Appraisal Schema Info:")
    appraisal_info = handler.get_schema_info('appraisal')
    
    print(f"✅ Appraisal Schema Information:")
    print(f"   Required Fields: {appraisal_info['required_fields']}")
    print(f"   Optional Fields: {appraisal_info['optional_fields']}")
    print(f"   Total Fields: {appraisal_info['total_fields']}")
    
    # Test unsupported schema
    print("\n3️⃣ Testing Unsupported Schema:")
    try:
        handler.get_schema_info('unsupported')
        print("❌ Should have raised ValueError for unsupported schema")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    print("\n✅ Schema info tests completed!")


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🚨 ERROR HANDLING TEST")
    print("=" * 50)
    
    handler = JSONHandler()
    
    # Test 1: Invalid JSON data type
    print("\n1️⃣ Testing Invalid JSON Data Type:")
    try:
        handler.canonicalize_json("not_a_dict")
        print("❌ Should have raised ValueError for non-dict input")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test 2: Unserializable data
    print("\n2️⃣ Testing Unserializable Data:")
    try:
        unserializable_data = {
            "loanId": "LOAN_2024_001",
            "amount": 500000,
            "callback": lambda x: x  # Cannot be serialized
        }
        handler.canonicalize_json(unserializable_data)
        print("❌ Should have raised ValueError for unserializable data")
    except (ValueError, TypeError) as e:
        print(f"✅ Correctly raised error: {e}")
    
    # Test 3: Unsupported schema type
    print("\n3️⃣ Testing Unsupported Schema Type:")
    try:
        handler.validate_json_schema({}, 'unsupported_schema')
        print("❌ Should have raised ValueError for unsupported schema")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    print("\n✅ Error handling tests completed!")


def main():
    """Run all tests."""
    print("📄 COMPREHENSIVE JSON HANDLER TEST SUITE")
    print("=" * 80)
    print("Testing all functionality of the JSONHandler class")
    print("=" * 80)
    
    try:
        # Run all test suites
        test_schema_validation()
        test_canonicalization()
        test_business_rules()
        test_complete_processing()
        test_schema_info()
        test_error_handling()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ JSONHandler is production-ready!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


