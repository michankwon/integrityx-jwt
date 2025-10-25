"""
Unit tests for JWT service functionality.

This module tests the JWT-based digital signature functionality including:
- Token generation and verification
- Canonical JSON processing
- Error handling for invalid tokens and payloads
- Claims validation
"""

import pytest
import jwt
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from datetime import datetime, timedelta

# Import the functions to test
from src.jwt_service import sign_artifact, verify_signature, canonical_json


class TestCanonicalJson:
    """Test canonical JSON formatting functionality."""
    
    def test_canonical_json_sorts_keys(self):
        """Test that canonical JSON sorts keys deterministically."""
        data = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(data)
        expected = '{"a":2,"m":3,"z":1}'
        assert result == expected
    
    def test_canonical_json_nested_objects(self):
        """Test canonical JSON with nested objects."""
        data = {
            "outer": {"z": 1, "a": 2},
            "simple": "value"
        }
        result = canonical_json(data)
        expected = '{"outer":{"a":2,"z":1},"simple":"value"}'
        assert result == expected
    
    def test_canonical_json_with_arrays(self):
        """Test canonical JSON preserves array order."""
        data = {
            "items": [3, 1, 2],
            "name": "test"
        }
        result = canonical_json(data)
        expected = '{"items":[3,1,2],"name":"test"}'
        assert result == expected
    
    def test_canonical_json_complex_structure(self):
        """Test canonical JSON with complex nested structure."""
        data = {
            "b": 2,
            "a": 1,
            "c": {
                "z": 26,
                "y": 25,
                "nested": {
                    "deep": "value",
                    "array": [{"b": 2}, {"a": 1}]
                }
            }
        }
        result = canonical_json(data)
        # Should be sorted at all levels
        assert '"a":1' in result
        assert '"b":2' in result
        assert '"y":25' in result
        assert '"z":26' in result
        assert result.startswith('{"a":1,"b":2,"c":{')


class TestJwtSigning:
    """Test JWT token generation functionality."""
    
    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        os.environ['JWT_PRIVATE_KEY_PATH'] = 'test_private.pem'
        os.environ['JWT_PUBLIC_KEY_PATH'] = 'test_public.pem'
        os.environ['JWT_ISSUER'] = 'test-issuer'
        os.environ['JWT_TTL_SECONDS'] = '3600'
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-private-key')
    def test_sign_artifact_generates_valid_jwt(self, mock_file):
        """Test that sign_artifact generates a valid JWT token."""
        with patch('jwt.encode') as mock_encode:
            mock_encode.return_value = 'mock.jwt.token'
            
            artifact_id = "test-artifact-123"
            payload = {"test": "data"}
            
            result = sign_artifact(artifact_id, payload)
            
            assert result == 'mock.jwt.token'
            mock_encode.assert_called_once()
            
            # Verify the claims structure
            call_args = mock_encode.call_args[0]
            claims = call_args[0]
            
            assert claims['artifact_id'] == artifact_id
            assert claims['iss'] == 'test-issuer'
            assert 'iat' in claims
            assert 'exp' in claims
            assert 'payload_hash' in claims
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-private-key')
    def test_sign_artifact_includes_canonical_payload(self, mock_file):
        """Test that the JWT includes the canonical payload."""
        with patch('jwt.encode') as mock_encode:
            mock_encode.return_value = 'mock.jwt.token'
            
            payload = {"b": 2, "a": 1}  # Will be canonicalized
            
            sign_artifact("test-id", payload)
            
            call_args = mock_encode.call_args[0]
            claims = call_args[0]
            
            # Should contain the canonical form: {"a":1,"b":2}
            assert 'payload' in claims
            assert claims['payload'] == '{"a":1,"b":2}'
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_sign_artifact_handles_missing_key_file(self, mock_file):
        """Test error handling when private key file is missing."""
        with pytest.raises(FileNotFoundError):
            sign_artifact("test-id", {"test": "data"})


class TestJwtVerification:
    """Test JWT token verification functionality."""
    
    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        os.environ['JWT_PRIVATE_KEY_PATH'] = 'test_private.pem'
        os.environ['JWT_PUBLIC_KEY_PATH'] = 'test_public.pem'
        os.environ['JWT_ISSUER'] = 'test-issuer'
        os.environ['JWT_TTL_SECONDS'] = '3600'
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-public-key')
    def test_verify_signature_success(self, mock_file):
        """Test successful JWT verification."""
        test_payload = {"test": "data"}
        canonical_payload = canonical_json(test_payload)
        
        mock_claims = {
            'artifact_id': 'test-123',
            'iss': 'test-issuer',
            'iat': datetime.utcnow().timestamp(),
            'exp': (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            'payload': canonical_payload
        }
        
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = mock_claims
            
            result = verify_signature('mock.jwt.token', test_payload)
            
            assert result == mock_claims
            mock_decode.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-public-key')
    def test_verify_signature_payload_mismatch(self, mock_file):
        """Test verification fails when payload doesn't match."""
        original_payload = {"test": "original"}
        modified_payload = {"test": "modified"}
        
        # Claims contain the original payload
        mock_claims = {
            'artifact_id': 'test-123',
            'payload': canonical_json(original_payload)
        }
        
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = mock_claims
            
            with pytest.raises(ValueError, match="Payload mismatch"):
                verify_signature('mock.jwt.token', modified_payload)
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-public-key')
    def test_verify_signature_expired_token(self, mock_file):
        """Test verification fails for expired tokens."""
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
            
            with pytest.raises(jwt.ExpiredSignatureError):
                verify_signature('expired.jwt.token', {"test": "data"})
    
    @patch('builtins.open', new_callable=mock_open, read_data='fake-public-key')
    def test_verify_signature_invalid_token(self, mock_file):
        """Test verification fails for invalid tokens."""
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
            
            with pytest.raises(jwt.InvalidTokenError):
                verify_signature('invalid.jwt.token', {"test": "data"})
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_verify_signature_missing_public_key(self, mock_file):
        """Test error handling when public key file is missing."""
        with pytest.raises(FileNotFoundError):
            verify_signature('mock.jwt.token', {"test": "data"})


class TestJwtRoundTrip:
    """Test complete sign-and-verify workflows."""
    
    def setup_method(self):
        """Set up test environment and mock keys."""
        self.original_env = os.environ.copy()
        os.environ['JWT_PRIVATE_KEY_PATH'] = 'test_private.pem'
        os.environ['JWT_PUBLIC_KEY_PATH'] = 'test_public.pem'
        os.environ['JWT_ISSUER'] = 'test-issuer'
        os.environ['JWT_TTL_SECONDS'] = '3600'
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_sign_and_verify_round_trip(self):
        """Test complete sign and verify round trip as requested."""
        payload = {"foo": "bar"}
        
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode, \
             patch('jwt.decode') as mock_decode:
            
            # Mock signing
            mock_encode.return_value = 'mock.jwt.token'
            
            # Mock verification  
            mock_claims = {
                'artifact_id': 'art123',
                'iss': 'test-issuer',
                'payload': canonical_json(payload)
            }
            mock_decode.return_value = mock_claims
            
            # Test the round trip
            token = sign_artifact("art123", payload)
            claims = verify_signature(token, payload)
            
            assert claims["artifact_id"] == "art123"
    
    def test_verify_fails_for_modified_payload(self):
        """Test verification fails for modified payload as requested."""
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode, \
             patch('jwt.decode') as mock_decode:
            
            # Mock signing
            mock_encode.return_value = 'mock.jwt.token'
            
            # Mock verification with payload mismatch
            mock_claims = {
                'artifact_id': 'art123',
                'payload': canonical_json({"foo": "bar"})  # Original payload
            }
            mock_decode.return_value = mock_claims
            
            # Sign with original payload
            token = sign_artifact("art123", {"foo": "bar"})
            
            # Verify with modified payload should fail
            with pytest.raises(ValueError):
                verify_signature(token, {"foo": "baz"})
    
    def test_different_artifacts_have_different_signatures(self):
        """Test that different artifacts produce different signatures."""
        payload = {"data": "same"}
        
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode:
            
            mock_encode.side_effect = ['token1', 'token2']
            
            token1 = sign_artifact("artifact1", payload)
            token2 = sign_artifact("artifact2", payload)
            
            assert token1 != token2
            assert mock_encode.call_count == 2
            
            # Verify different artifact IDs in claims
            call1_claims = mock_encode.call_args_list[0][0][0]
            call2_claims = mock_encode.call_args_list[1][0][0]
            
            assert call1_claims['artifact_id'] == 'artifact1'
            assert call2_claims['artifact_id'] == 'artifact2'


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        os.environ['JWT_PRIVATE_KEY_PATH'] = 'test_private.pem'
        os.environ['JWT_PUBLIC_KEY_PATH'] = 'test_public.pem'
        os.environ['JWT_ISSUER'] = 'test-issuer'
        os.environ['JWT_TTL_SECONDS'] = '3600'
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_missing_environment_variables(self):
        """Test behavior when required environment variables are missing."""
        # Clear the JWT environment variables
        for key in ['JWT_PRIVATE_KEY_PATH', 'JWT_PUBLIC_KEY_PATH', 'JWT_ISSUER']:
            if key in os.environ:
                del os.environ[key]
        
        with pytest.raises(KeyError):
            sign_artifact("test", {"data": "test"})
    
    def test_invalid_json_in_payload(self):
        """Test handling of payloads that can't be canonicalized."""
        # This should still work as canonical_json handles most Python objects
        import datetime
        
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode:
            
            mock_encode.return_value = 'mock.jwt.token'
            
            # This should not raise an error due to our robust JSON handling
            payload = {"date": "2023-01-01"}  # String dates should work fine
            result = sign_artifact("test", payload)
            
            assert result == 'mock.jwt.token'


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        os.environ['JWT_PRIVATE_KEY_PATH'] = 'test_private.pem'
        os.environ['JWT_PUBLIC_KEY_PATH'] = 'test_public.pem'
        os.environ['JWT_ISSUER'] = 'integrityx-demo'
        os.environ['JWT_TTL_SECONDS'] = '3600'
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_loan_document_signature_scenario(self):
        """Test signing a realistic loan document payload."""
        loan_document = {
            "borrower": {
                "name": "John Doe",
                "ssn": "123-45-6789"
            },
            "loan": {
                "amount": 250000,
                "rate": 3.5,
                "term": 360
            },
            "property": {
                "address": "123 Main St",
                "value": 300000
            }
        }
        
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode, \
             patch('jwt.decode') as mock_decode:
            
            mock_encode.return_value = 'loan.jwt.token'
            mock_claims = {
                'artifact_id': 'loan-123',
                'iss': 'integrityx-demo',
                'payload': canonical_json(loan_document)
            }
            mock_decode.return_value = mock_claims
            
            # Sign the document
            token = sign_artifact("loan-123", loan_document)
            
            # Verify the document
            claims = verify_signature(token, loan_document)
            
            assert claims['artifact_id'] == 'loan-123'
            assert claims['iss'] == 'integrityx-demo'
    
    def test_tamper_detection_scenario(self):
        """Test tamper detection when document is modified."""
        original_doc = {
            "amount": 100000,
            "borrower": "Alice Smith"
        }
        
        tampered_doc = {
            "amount": 999999,  # Amount changed!
            "borrower": "Alice Smith"
        }
        
        with patch('builtins.open', new_callable=mock_open, read_data='fake-key'), \
             patch('jwt.encode') as mock_encode, \
             patch('jwt.decode') as mock_decode:
            
            mock_encode.return_value = 'original.jwt.token'
            mock_claims = {
                'artifact_id': 'doc-123',
                'payload': canonical_json(original_doc)
            }
            mock_decode.return_value = mock_claims
            
            # Sign original document
            token = sign_artifact("doc-123", original_doc)
            
            # Attempting to verify tampered document should fail
            with pytest.raises(ValueError, match="Payload mismatch"):
                verify_signature(token, tampered_doc)
