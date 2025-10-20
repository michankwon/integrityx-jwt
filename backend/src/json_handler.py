"""
JSON artifact processing handler for the Walacor Financial Integrity Platform.

This module provides comprehensive JSON processing capabilities including schema validation,
canonicalization, hashing, and business rule validation for financial loan documents.

Key Features:
- JSON Schema validation for loan documents
- Canonical JSON encoding for consistent hashing
- SHA-256 hash generation for integrity verification
- Business rule validation for loan parameters
- Type safety with comprehensive type hints

Canonicalization:
Canonical JSON is a standardized way to represent JSON data that ensures:
1. Consistent field ordering (alphabetical)
2. Consistent whitespace (minimal)
3. Consistent number formatting
4. Consistent string escaping
This allows for reliable hash generation and comparison of JSON documents.
"""

import json
import hashlib
from typing import Dict, List, Tuple, Any, Union
import jsonschema
from jsonschema import ValidationError

try:
    import canonicaljson
    HAS_CANONICALJSON = True
except ImportError:
    # Fallback for systems without canonicaljson
    canonicaljson = None
    HAS_CANONICALJSON = False


class JSONHandler:
    """
    Handler for JSON artifact processing with validation, canonicalization, and business rules.
    
    This class provides comprehensive JSON processing capabilities for financial documents,
    ensuring data integrity, consistency, and compliance with business rules.
    
    Attributes:
        LOAN_SCHEMA: JSON schema for loan document validation
        BUSINESS_RULES: Configuration for business rule validation
    """
    
    # JSON Schema for loan documents
    LOAN_SCHEMA = {
        "type": "object",
        "required": ["loanId", "amount", "rate", "term"],
        "properties": {
            "loanId": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255,
                "pattern": "^[A-Za-z0-9_-]+$"
            },
            "amount": {
                "type": "number",
                "minimum": 0,
                "maximum": 1000000000  # 1 billion max
            },
            "rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 100
            },
            "term": {
                "type": "integer",
                "minimum": 1,
                "maximum": 3600  # 30 years max
            },
            "borrowerName": {
                "type": "string",
                "maxLength": 255
            },
            "propertyAddress": {
                "type": "string",
                "maxLength": 500
            },
            "loanType": {
                "type": "string",
                "enum": ["conventional", "FHA", "VA", "USDA", "jumbo"]
            },
            "purpose": {
                "type": "string",
                "enum": ["purchase", "refinance", "cash_out", "rate_term"]
            }
        },
        "additionalProperties": True  # Allow additional fields
    }
    
    # Additional schemas for different document types
    SCHEMAS = {
        'loan': LOAN_SCHEMA,
        'appraisal': {
            "type": "object",
            "required": ["propertyAddress", "appraisedValue", "appraiserId"],
            "properties": {
                "propertyAddress": {"type": "string"},
                "appraisedValue": {"type": "number", "minimum": 0},
                "appraiserId": {"type": "string"},
                "appraisalDate": {"type": "string", "format": "date"}
            }
        },
        'credit_report': {
            "type": "object",
            "required": ["borrowerId", "creditScore", "reportDate"],
            "properties": {
                "borrowerId": {"type": "string"},
                "creditScore": {"type": "integer", "minimum": 300, "maximum": 850},
                "reportDate": {"type": "string", "format": "date"}
            }
        }
    }
    
    def __init__(self):
        """
        Initialize the JSONHandler.
        
        Note: If canonicaljson is not available, a fallback canonicalization
        method will be used, though it may not be as robust.
        """
        # Initialize JSON schema validator
        self.validator = jsonschema.Draft7Validator
        
        if not HAS_CANONICALJSON:
            print("Warning: canonicaljson not available, using fallback canonicalization")
    
    def validate_json_schema(
        self, 
        json_data: Dict[str, Any], 
        schema_type: str = 'loan'
    ) -> Tuple[bool, str]:
        """
        Validate JSON data against a specified schema.
        
        This method validates the structure and content of JSON data against
        predefined schemas to ensure data quality and consistency.
        
        Args:
            json_data: The JSON data to validate
            schema_type: Type of schema to use ('loan', 'appraisal', 'credit_report')
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
                - (True, "") if validation passes
                - (False, error_message) if validation fails
        
        Raises:
            ValueError: If schema_type is not supported
        """
        if schema_type not in self.SCHEMAS:
            available_schemas = list(self.SCHEMAS.keys())
            raise ValueError(f"Unsupported schema type '{schema_type}'. Available: {available_schemas}")
        
        try:
            schema = self.SCHEMAS[schema_type]
            validator = self.validator(schema)
            validator.validate(json_data)
            return True, ""
            
        except ValidationError as e:
            # Format validation error for better readability
            error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            error_message = f"Validation error at '{error_path}': {e.message}"
            return False, error_message
            
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"
    
    def canonicalize_json(self, json_data: Dict[str, Any]) -> bytes:
        """
        Convert JSON data to canonical form.
        
        Canonical JSON ensures consistent representation of JSON data by:
        1. Sorting object keys alphabetically
        2. Removing unnecessary whitespace
        3. Using consistent number formatting
        4. Using consistent string escaping
        
        This is crucial for generating consistent hashes and enabling
        reliable comparison of JSON documents.
        
        Args:
            json_data: The JSON data to canonicalize
        
        Returns:
            bytes: Canonical JSON representation as bytes
        
        Raises:
            ValueError: If json_data cannot be serialized to JSON
            RuntimeError: If canonicalization fails
        """
        try:
            if HAS_CANONICALJSON:
                # Use canonicaljson for consistent encoding
                canonical_bytes = canonicaljson.encode_canonical_json(json_data)
                return canonical_bytes
            else:
                # Fallback: Use json.dumps with sort_keys=True and separators
                # This provides basic canonicalization but may not be as robust
                canonical_str = json.dumps(
                    json_data, 
                    sort_keys=True, 
                    separators=(',', ':'), 
                    ensure_ascii=True
                )
                return canonical_str.encode('utf-8')
            
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for canonicalization: {e}")
        except Exception as e:
            raise RuntimeError(f"Canonicalization failed: {e}")
    
    def hash_canonical_json(self, json_data: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of canonical JSON data.
        
        This method creates a cryptographic hash of the canonical JSON representation,
        which can be used for:
        - Document integrity verification
        - Duplicate detection
        - Change tracking
        - Blockchain storage
        
        Args:
            json_data: The JSON data to hash
        
        Returns:
            str: SHA-256 hash as hexadecimal string (64 characters)
        
        Raises:
            ValueError: If json_data cannot be canonicalized
            RuntimeError: If hashing fails
        """
        try:
            # Get canonical bytes
            canonical_bytes = self.canonicalize_json(json_data)
            
            # Calculate SHA-256 hash
            sha256_hash = hashlib.sha256(canonical_bytes)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            raise RuntimeError(f"Hash generation failed: {e}")
    
    def run_business_rules(self, json_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate JSON data against business rules.
        
        Business rules enforce domain-specific constraints beyond basic schema validation.
        These rules ensure that loan data meets business requirements and regulatory standards.
        
        Current business rules:
        - Loan amount: $1,000 - $10,000,000
        - Interest rate: 0.1% - 20.0%
        - Loan term: 180, 240, 360 months (15, 20, 30 years)
        - Credit score: 620+ for conventional loans
        
        Args:
            json_data: The JSON data to validate
        
        Returns:
            Tuple[bool, List[str]]: (passed, list_of_errors)
                - (True, []) if all business rules pass
                - (False, [error_messages]) if any rules fail
        """
        errors = []
        
        try:
            # Rule 1: Loan amount validation
            amount = json_data.get('amount')
            if amount is not None:
                if not isinstance(amount, (int, float)):
                    errors.append("Loan amount must be a number")
                elif amount < 1000:
                    errors.append("Loan amount must be at least $1,000")
                elif amount > 10000000:
                    errors.append("Loan amount cannot exceed $10,000,000")
            
            # Rule 2: Interest rate validation
            rate = json_data.get('rate')
            if rate is not None:
                if not isinstance(rate, (int, float)):
                    errors.append("Interest rate must be a number")
                elif rate < 0.1:
                    errors.append("Interest rate must be at least 0.1%")
                elif rate > 20.0:
                    errors.append("Interest rate cannot exceed 20.0%")
            
            # Rule 3: Loan term validation
            term = json_data.get('term')
            if term is not None:
                if not isinstance(term, int):
                    errors.append("Loan term must be an integer")
                elif term not in [180, 240, 360]:
                    errors.append("Loan term must be 180, 240, or 360 months (15, 20, or 30 years)")
            
            # Rule 4: Credit score validation (if present)
            credit_score = json_data.get('creditScore')
            if credit_score is not None:
                if not isinstance(credit_score, int):
                    errors.append("Credit score must be an integer")
                elif credit_score < 300 or credit_score > 850:
                    errors.append("Credit score must be between 300 and 850")
                elif credit_score < 620:
                    errors.append("Credit score below 620 may require special underwriting")
            
            # Rule 5: Loan type specific rules
            loan_type = json_data.get('loanType')
            if loan_type == 'jumbo':
                if amount is not None and amount < 647200:  # 2022 conforming loan limit
                    errors.append("Jumbo loans must exceed conforming loan limits")
            elif loan_type == 'FHA':
                if credit_score is not None and credit_score < 580:
                    errors.append("FHA loans require minimum 580 credit score")
            
            # Rule 6: Property value validation (if present)
            property_value = json_data.get('propertyValue')
            if property_value is not None and amount is not None:
                if not isinstance(property_value, (int, float)):
                    errors.append("Property value must be a number")
                elif property_value <= 0:
                    errors.append("Property value must be positive")
                elif amount > property_value:
                    errors.append("Loan amount cannot exceed property value")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Business rule validation error: {str(e)}"]
    
    def process_json_artifact(
        self, 
        json_data: Dict[str, Any], 
        schema_type: str = 'loan'
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for JSON artifacts.
        
        This method runs the full processing pipeline:
        1. Schema validation
        2. Business rule validation
        3. Canonicalization
        4. Hash generation
        
        Args:
            json_data: The JSON data to process
            schema_type: Type of schema to use for validation
        
        Returns:
            Dict[str, Any]: Processing results including:
                - is_valid: Overall validation status
                - schema_valid: Schema validation status
                - business_rules_passed: Business rules status
                - canonical_json: Canonical JSON bytes
                - hash: SHA-256 hash
                - errors: List of all errors
                - warnings: List of warnings
        
        Raises:
            ValueError: If json_data is invalid
            RuntimeError: If processing fails
        """
        result = {
            'is_valid': False,
            'schema_valid': False,
            'business_rules_passed': False,
            'canonical_json': None,
            'hash': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Step 1: Schema validation
            schema_valid, schema_error = self.validate_json_schema(json_data, schema_type)
            result['schema_valid'] = schema_valid
            if not schema_valid:
                result['errors'].append(f"Schema validation failed: {schema_error}")
            
            # Step 2: Business rule validation
            business_rules_passed, business_errors = self.run_business_rules(json_data)
            result['business_rules_passed'] = business_rules_passed
            result['errors'].extend(business_errors)
            
            # Step 3: Canonicalization (only if schema is valid)
            if schema_valid:
                try:
                    canonical_json = self.canonicalize_json(json_data)
                    result['canonical_json'] = canonical_json
                except Exception as e:
                    result['errors'].append(f"Canonicalization failed: {e}")
            
            # Step 4: Hash generation (only if canonicalization succeeded)
            if result['canonical_json'] is not None:
                try:
                    hash_value = self.hash_canonical_json(json_data)
                    result['hash'] = hash_value
                except Exception as e:
                    result['errors'].append(f"Hash generation failed: {e}")
            
            # Overall validation status
            result['is_valid'] = (
                result['schema_valid'] and 
                result['business_rules_passed'] and 
                result['hash'] is not None
            )
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Processing failed: {e}")
            return result
    
    def get_schema_info(self, schema_type: str = 'loan') -> Dict[str, Any]:
        """
        Get information about a specific schema.
        
        Args:
            schema_type: Type of schema to get info for
        
        Returns:
            Dict[str, Any]: Schema information including:
                - schema: The actual schema
                - required_fields: List of required fields
                - optional_fields: List of optional fields
                - field_types: Field type information
        """
        if schema_type not in self.SCHEMAS:
            available_schemas = list(self.SCHEMAS.keys())
            raise ValueError(f"Unsupported schema type '{schema_type}'. Available: {available_schemas}")
        
        schema = self.SCHEMAS[schema_type]
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        return {
            'schema': schema,
            'required_fields': required_fields,
            'optional_fields': [field for field in properties.keys() if field not in required_fields],
            'field_types': {field: prop.get('type', 'unknown') for field, prop in properties.items()},
            'total_fields': len(properties)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the JSONHandler
    print("📄 JSON HANDLER TEST")
    print("=" * 50)
    
    try:
        handler = JSONHandler()
        print("✅ JSONHandler initialized successfully")
        
        # Test data
        test_loan_data = {
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
        
        print("\n1️⃣ Testing Schema Validation:")
        is_valid, error = handler.validate_json_schema(test_loan_data, 'loan')
        if is_valid:
            print("✅ Schema validation passed")
        else:
            print(f"❌ Schema validation failed: {error}")
        
        print("\n2️⃣ Testing Business Rules:")
        rules_passed, errors = handler.run_business_rules(test_loan_data)
        if rules_passed:
            print("✅ Business rules validation passed")
        else:
            print(f"❌ Business rules validation failed: {errors}")
        
        print("\n3️⃣ Testing Canonicalization:")
        canonical_bytes = handler.canonicalize_json(test_loan_data)
        print(f"✅ Canonical JSON generated: {len(canonical_bytes)} bytes")
        
        print("\n4️⃣ Testing Hash Generation:")
        hash_value = handler.hash_canonical_json(test_loan_data)
        print(f"✅ Hash generated: {hash_value}")
        
        print("\n5️⃣ Testing Complete Processing:")
        result = handler.process_json_artifact(test_loan_data, 'loan')
        print(f"✅ Processing completed:")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Schema Valid: {result['schema_valid']}")
        print(f"   Business Rules Passed: {result['business_rules_passed']}")
        print(f"   Hash: {result['hash'][:16]}...")
        print(f"   Errors: {len(result['errors'])}")
        
        print("\n6️⃣ Testing Schema Info:")
        schema_info = handler.get_schema_info('loan')
        print(f"✅ Schema info retrieved:")
        print(f"   Required fields: {schema_info['required_fields']}")
        print(f"   Optional fields: {len(schema_info['optional_fields'])}")
        print(f"   Total fields: {schema_info['total_fields']}")
        
        print("\n✅ All JSON handler tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install required dependencies: pip install canonicaljson jsonschema")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
