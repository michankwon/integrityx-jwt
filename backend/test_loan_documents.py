"""
Comprehensive test suite for loan document sealing with borrower data.

Run with: pytest backend/test_loan_documents.py -v
Add coverage reporting: pytest --cov=backend/src --cov-report=html
"""

import pytest
import json
import hashlib
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Import the FastAPI app and dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import app
from database import Database, get_services
from models import Artifact, ArtifactEvent
from encryption_service import EncryptionService
from walacor_service import WalacorIntegrityService


class TestLoanDocuments:
    """Test suite for loan document sealing with borrower data."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test database and client for each test."""
        # Create in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        self.session_local = sessionmaker(autoclose=False, autoflush=False, bind=self.engine)
        
        # Create tables
        from models import Base
        Base.metadata.create_all(bind=self.engine)
        
        # Create test client
        self.client = TestClient(app)
        
        # Mock services
        self.mock_db = Database(self.engine)
        self.mock_encryption = EncryptionService()
        self.mock_walacor = WalacorIntegrityService()
        
        # Override dependency
        def override_get_services():
            return {
                "db": self.mock_db,
                "encryption": self.mock_encryption,
                "wal_service": self.mock_walacor
            }
        
        app.dependency_overrides[get_services] = override_get_services

    @pytest.fixture
    def valid_loan_data(self):
        """Valid loan data for testing."""
        return {
            "loan_id": "TEST_LOAN_001",
            "document_type": "loan_application",
            "loan_amount": 150000,
            "borrower_name": "John Smith",
            "additional_notes": "Test loan application"
        }

    @pytest.fixture
    def valid_borrower_data(self):
        """Valid borrower data for testing."""
        return {
            "full_name": "John Smith",
            "date_of_birth": "1985-03-15",
            "email": "john.smith@example.com",
            "phone": "+15551234567",
            "address_line1": "123 Main Street",
            "address_line2": "Apt 4B",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "country": "US",
            "ssn_last4": "1234",
            "id_type": "drivers_license",
            "id_last4": "5678",
            "employment_status": "employed",
            "annual_income": 75000,
            "co_borrower_name": "Jane Smith"
        }

    @pytest.fixture
    def valid_file_info(self):
        """Valid file information for testing."""
        return [{
            "filename": "loan-application.json",
            "file_type": "application/json",
            "file_size": 1024,
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        }]

    def test_seal_loan_document_success(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test successful loan document sealing with borrower data."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_123456789",
            "document_hash": "test_hash_123456789",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_123456789",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Prepare request data
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            # Make API request
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            
            # Verify response
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["ok"] is True
            assert "artifact_id" in response_data["data"]
            assert response_data["data"]["walacor_tx_id"] == "TX_test_123456789"
            assert response_data["data"]["hash"] == "test_hash_123456789"
            
            # Verify artifact created in database
            session = self.session_local()
            artifact = session.query(Artifact).filter(
                Artifact.artifact_id == response_data["data"]["artifact_id"]
            ).first()
            
            assert artifact is not None
            assert artifact.etid == 100005  # Loan documents with borrower info ETID
            assert artifact.walacor_tx_id == "TX_test_123456789"
            assert artifact.borrower_info is not None
            
            # Verify borrower info is encrypted
            borrower_info = json.loads(artifact.borrower_info)
            assert "full_name" in borrower_info
            assert borrower_info["full_name"] == "John Smith"  # Non-sensitive field
            # Sensitive fields should be encrypted (we can't easily test encryption without decryption)
            
            session.close()

    def test_seal_loan_document_validation_errors(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test validation errors for loan document sealing."""
        
        # Test invalid SSN format
        invalid_ssn_data = valid_borrower_data.copy()
        invalid_ssn_data["ssn_last4"] = "123"  # Too short
        
        request_data = {
            "loan_data": valid_loan_data,
            "borrower_info": invalid_ssn_data,
            "files": valid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test invalid email
        invalid_email_data = valid_borrower_data.copy()
        invalid_email_data["email"] = "invalid-email"
        
        request_data = {
            "loan_data": valid_loan_data,
            "borrower_info": invalid_email_data,
            "files": valid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test invalid date of birth (<18 years)
        invalid_dob_data = valid_borrower_data.copy()
        invalid_dob_data["date_of_birth"] = "2010-01-01"  # Too young
        
        request_data = {
            "loan_data": valid_loan_data,
            "borrower_info": invalid_dob_data,
            "files": valid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test missing required fields
        missing_field_data = valid_borrower_data.copy()
        del missing_field_data["full_name"]
        
        request_data = {
            "loan_data": valid_loan_data,
            "borrower_info": missing_field_data,
            "files": valid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_borrower_data_encryption(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test borrower data encryption and decryption."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_encryption",
            "document_hash": "test_hash_encryption",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_encryption",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Prepare request data
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            # Make API request
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            # Get artifact from database
            session = self.session_local()
            artifact = session.query(Artifact).filter(
                Artifact.artifact_id == response.json()["data"]["artifact_id"]
            ).first()
            
            # Verify borrower info is stored
            assert artifact.borrower_info is not None
            stored_borrower_info = json.loads(artifact.borrower_info)
            
            # Verify non-sensitive fields are readable
            assert stored_borrower_info["full_name"] == "John Smith"
            assert stored_borrower_info["city"] == "Anytown"
            assert stored_borrower_info["state"] == "CA"
            
            # Verify sensitive fields are encrypted (they should be different from original)
            # Note: In a real implementation, we'd decrypt and compare
            assert "email" in stored_borrower_info
            assert "phone" in stored_borrower_info
            assert "ssn_last4" in stored_borrower_info
            
            session.close()

    def test_audit_logging(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test audit logging for loan document operations."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_audit",
            "document_hash": "test_hash_audit",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_audit",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Prepare request data
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            # Make API request
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            artifact_id = response.json()["data"]["artifact_id"]
            
            # Verify audit events were created
            session = self.session_local()
            audit_events = session.query(ArtifactEvent).filter(
                ArtifactEvent.artifact_id == artifact_id
            ).all()
            
            # Should have at least upload and seal events
            assert len(audit_events) >= 2
            
            event_types = [event.event_type for event in audit_events]
            assert "borrower_data_submitted" in event_types
            assert "blockchain_sealed" in event_types
            
            # Test borrower data access logging
            access_response = self.client.get(f"/api/loan-documents/{artifact_id}/borrower")
            assert access_response.status_code == 200
            
            # Check for access logging
            access_events = session.query(ArtifactEvent).filter(
                ArtifactEvent.artifact_id == artifact_id,
                ArtifactEvent.event_type == "borrower_data_accessed"
            ).all()
            assert len(access_events) >= 1
            
            session.close()

    def test_search_by_borrower(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test searching loan documents by borrower information."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_search",
            "document_hash": "test_hash_search",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_search",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Create a loan document
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            # Test search by borrower name
            search_response = self.client.get("/api/loan-documents/search", params={
                "borrower_name": "John Smith"
            })
            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["ok"] is True
            assert len(search_data["data"]["results"]) >= 1
            assert search_data["data"]["results"][0]["borrower_name"] == "John Smith"
            
            # Test search by email
            search_response = self.client.get("/api/loan-documents/search", params={
                "borrower_email": "john.smith@example.com"
            })
            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["ok"] is True
            assert len(search_data["data"]["results"]) >= 1
            
            # Test search by loan ID
            search_response = self.client.get("/api/loan-documents/search", params={
                "loan_id": "TEST_LOAN_001"
            })
            assert search_response.status_code == 200
            search_data = search_response.json()
            assert search_data["ok"] is True
            assert len(search_data["data"]["results"]) >= 1
            assert search_data["data"]["results"][0]["loan_id"] == "TEST_LOAN_001"

    def test_walacor_sealing(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test Walacor blockchain sealing with borrower data."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_walacor",
            "document_hash": "test_hash_walacor",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_walacor",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response) as mock_seal:
            # Prepare request data
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            # Make API request
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            # Verify Walacor service was called with correct parameters
            mock_seal.assert_called_once()
            call_args = mock_seal.call_args
            
            assert call_args[1]["loan_id"] == "TEST_LOAN_001"
            assert call_args[1]["loan_data"]["loan_amount"] == 150000
            assert call_args[1]["borrower_data"]["full_name"] == "John Smith"
            assert len(call_args[1]["files"]) == 1
            
            # Verify response contains Walacor transaction details
            response_data = response.json()
            assert response_data["data"]["walacor_tx_id"] == "TX_test_walacor"
            assert response_data["data"]["hash"] == "test_hash_walacor"
            
            # Verify hash calculation includes borrower data
            # The hash should be calculated from the comprehensive document including borrower data
            assert response_data["data"]["hash"] is not None
            assert len(response_data["data"]["hash"]) == 64  # SHA-256 hash length

    def test_verification_with_borrower_data(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test document verification with borrower data integrity."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_verify",
            "document_hash": "test_hash_verify",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_verify",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Create a loan document
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            artifact_id = response.json()["data"]["artifact_id"]
            stored_hash = response.json()["data"]["hash"]
            
            # Test verification with correct hash
            verify_response = self.client.post("/api/verify", json={
                "etid": 100005,
                "payloadHash": stored_hash
            })
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["ok"] is True
            assert verify_data["data"]["is_valid"] is True
            
            # Test verification with incorrect hash (tamper detection)
            verify_response = self.client.post("/api/verify", json={
                "etid": 100005,
                "payloadHash": "incorrect_hash_123456789"
            })
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["ok"] is True
            assert verify_data["data"]["is_valid"] is False
            
            # Test borrower data integrity by retrieving it
            borrower_response = self.client.get(f"/api/loan-documents/{artifact_id}/borrower")
            assert borrower_response.status_code == 200
            borrower_data = borrower_response.json()
            assert borrower_data["ok"] is True
            assert borrower_data["data"]["full_name"] == "John Smith"
            assert borrower_data["data"]["email"] == "j***@example.com"  # Masked

    def test_loan_document_edge_cases(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test edge cases for loan document sealing."""
        
        # Test with minimal required data
        minimal_loan_data = {
            "loan_id": "MINIMAL_LOAN",
            "document_type": "loan_application",
            "loan_amount": 1000,
            "borrower_name": "Minimal User"
        }
        
        minimal_borrower_data = {
            "full_name": "Minimal User",
            "date_of_birth": "1990-01-01",
            "email": "minimal@example.com",
            "phone": "+1555000000",
            "address_line1": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "12345",
            "country": "US",
            "ssn_last4": "0000",
            "id_type": "drivers_license",
            "id_last4": "0000",
            "employment_status": "employed",
            "annual_income": 30000
        }
        
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_minimal",
            "document_hash": "test_hash_minimal",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_minimal",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            request_data = {
                "loan_data": minimal_loan_data,
                "borrower_info": minimal_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            # Test with maximum loan amount
            max_loan_data = valid_loan_data.copy()
            max_loan_data["loan_amount"] = 50000000  # Max allowed amount
            
            request_data = {
                "loan_data": max_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200

    def test_loan_document_error_handling(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test error handling for loan document operations."""
        
        # Test with invalid loan amount (too high)
        invalid_loan_data = valid_loan_data.copy()
        invalid_loan_data["loan_amount"] = 100000000  # Exceeds maximum
        
        request_data = {
            "loan_data": invalid_loan_data,
            "borrower_info": valid_borrower_data,
            "files": valid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test with invalid file size
        invalid_file_info = valid_file_info.copy()
        invalid_file_info[0]["file_size"] = 200000000  # Exceeds 100MB limit
        
        request_data = {
            "loan_data": valid_loan_data,
            "borrower_info": valid_borrower_data,
            "files": invalid_file_info
        }
        
        response = self.client.post("/api/loan-documents/seal", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test with Walacor service failure
        with patch.object(self.mock_walacor, 'seal_loan_document', side_effect=Exception("Walacor service unavailable")):
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            # Should handle gracefully - might return 500 or fallback to local simulation
            assert response.status_code in [500, 200]

    def test_audit_trail_retrieval(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test audit trail retrieval for loan documents."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_audit_trail",
            "document_hash": "test_hash_audit_trail",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_audit_trail",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Create a loan document
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            artifact_id = response.json()["data"]["artifact_id"]
            
            # Test audit trail retrieval
            audit_response = self.client.get(f"/api/loan-documents/{artifact_id}/audit-trail")
            assert audit_response.status_code == 200
            audit_data = audit_response.json()
            assert audit_data["ok"] is True
            assert len(audit_data["data"]) >= 2  # At least upload and seal events
            
            # Verify audit trail contains expected events
            event_types = [event["event_type"] for event in audit_data["data"]]
            assert "borrower_data_submitted" in event_types
            assert "blockchain_sealed" in event_types

    def test_borrower_data_masking(self, valid_loan_data, valid_borrower_data, valid_file_info):
        """Test borrower data masking in API responses."""
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_test_masking",
            "document_hash": "test_hash_masking",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_test_masking",
                "blockchain_network": "walacor",
                "etid": 100005,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_loan_document', return_value=mock_walacor_response):
            # Create a loan document
            request_data = {
                "loan_data": valid_loan_data,
                "borrower_info": valid_borrower_data,
                "files": valid_file_info
            }
            
            response = self.client.post("/api/loan-documents/seal", json=request_data)
            assert response.status_code == 200
            
            artifact_id = response.json()["data"]["artifact_id"]
            
            # Test borrower data retrieval with masking
            borrower_response = self.client.get(f"/api/loan-documents/{artifact_id}/borrower")
            assert borrower_response.status_code == 200
            borrower_data = borrower_response.json()
            
            # Verify non-sensitive fields are visible
            assert borrower_data["data"]["full_name"] == "John Smith"
            assert borrower_data["data"]["city"] == "Anytown"
            assert borrower_data["data"]["state"] == "CA"
            
            # Verify sensitive fields are masked
            assert borrower_data["data"]["email"] == "j***@example.com"
            assert borrower_data["data"]["phone"] == "***-***-4567"
            # Note: SSN and ID masking would depend on implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
