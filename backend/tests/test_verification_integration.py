"""
Integration tests for verification portal with JWT signature support.

This module tests the verification endpoints to ensure they properly include
JWT verification status and can detect document tampering through digital signatures.

Run with: pytest tests/test_verification_integration.py -v
"""

import pytest
import json
import hashlib
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Import the FastAPI app and dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app, get_services
from src.database import Database
from src.models import Artifact, ArtifactEvent
from src.walacor_service import WalacorIntegrityService


class TestVerificationIntegration:
    """Integration tests for verification portal with JWT support."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test database and client for each test."""
        # Create test client
        self.client = TestClient(app)
        
        # Create a proper Database instance for testing
        # The Database constructor will create its own in-memory database and tables
        self.mock_db = Database("sqlite:///:memory:")
        self.mock_walacor = WalacorIntegrityService()
        
        # Override dependency
        def override_get_services():
            return {
                "db": self.mock_db,
                "wal_service": self.mock_walacor,
                "doc_handler": None,  # Mock services for test
                "json_handler": None,
                "manifest_handler": None,
                "attestation_repo": None,
                "provenance_repo": None,
                "verification_portal": None,
                "voice_processor": None,
                "analytics_service": None,
                "ai_anomaly_detector": None,
                "time_machine": None,
                "smart_contracts": None,
                "predictive_analytics": None,
                "document_intelligence": None,
                "advanced_security": None,
                "hybrid_security": None
            }
        
        app.dependency_overrides[get_services] = override_get_services

    @pytest.fixture
    def simple_json_data(self):
        """Simple JSON data for testing."""
        return {
            "document_id": "TEST_DOC_001",
            "document_type": "simple_test",
            "content": "Test document content",
            "metadata": {
                "created_by": "test_user",
                "purpose": "integration_testing"
            }
        }

    def test_simple_json_upload_includes_jwt_signature(self, simple_json_data):
        """Test that simple JSON upload responses include JWT signature."""
        # Mock Walacor service response
        mock_walacor_response = {
            "transaction_id": "TX_simple_jwt_test",
            "document_hash": "simple_test_hash_12345",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "proof_bundle": {
                "blockchain_proof": {
                    "transaction_id": "TX_simple_jwt_test",
                    "blockchain_network": "walacor",
                    "etid": 100001,
                    "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                    "integrity_verified": True,
                    "immutability_established": True
                }
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_document', return_value=mock_walacor_response):
            # Create seal request for simple JSON document
            import hashlib
            import json
            
            # Create a hash of the simple JSON data
            json_str = json.dumps(simple_json_data, sort_keys=True)
            payload_hash = hashlib.sha256(json_str.encode()).hexdigest()
            
            seal_request = {
                "etid": 100001,
                "payloadHash": payload_hash,
                "externalUri": "https://example.com/documents/test_doc_001",
                "metadata": {
                    "comprehensive_document": simple_json_data,  # Include the document for JWT signing
                    "document_type": "simple_test",
                    "created_by": "test_user"
                }
            }
            
            # Use /api/seal endpoint instead of /api/ingest-json
            response = self.client.post("/api/seal", json=seal_request)
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["ok"] is True
            
            # Assert JWT signature is included in upload response
            assert "signature_jwt" in response_data["data"], "Simple JSON upload response must include signature_jwt"
            jwt_signature = response_data["data"]["signature_jwt"]
            assert jwt_signature is not None, "JWT signature cannot be None"
            assert isinstance(jwt_signature, str), "JWT signature must be a string"
            assert len(jwt_signature) > 50, "JWT signature should be substantial"
            
            # Verify other response fields
            assert "artifact_id" in response_data["data"]
            assert "hash" in response_data["data"]
            
            return response_data["data"]  # Return for use in other tests

    def test_verify_endpoint_includes_jwt_verification(self, simple_json_data):
        """Test that verify endpoint responses include JWT verification status."""
        # First, create a document with JWT signature
        mock_walacor_response = {
            "walacor_tx_id": "TX_verify_jwt_test",
            "document_hash": "verify_test_hash_67890",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_verify_jwt_test",
                "blockchain_network": "walacor",
                "etid": 100001,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_document', return_value=mock_walacor_response):
            # Upload document
            upload_response = self.client.post("/api/ingest-json", json=simple_json_data)
            assert upload_response.status_code == 200
            
            upload_data = upload_response.json()["data"]
            artifact_id = upload_data["artifact_id"]
            document_hash = upload_data["hash"]
            
            # Test verification with correct document
            verify_response = self.client.post("/api/verify", json={
                "etid": 100001,
                "payloadHash": document_hash
            })
            
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["ok"] is True
            assert verify_data["data"]["is_valid"] is True
            
            # Assert JWT verification is included
            assert "details" in verify_data["data"], "Verify response must include details"
            assert "jwt_signature" in verify_data["data"]["details"], "Verify response must include jwt_verification"
            jwt_verification = verify_data["data"]["details"]["jwt_signature"]
            
            # Check JWT verification structure
            assert isinstance(jwt_verification, dict), "JWT verification must be a dictionary"
            assert "verified" in jwt_verification, "JWT verification must include 'verified' field"
            assert "error" in jwt_verification, "JWT verification must include 'error' field"
            assert "claims" in jwt_verification, "JWT verification must include 'claims' field"
            
            # If JWT verification succeeded, check claims
            if jwt_verification.get("verified"):
                claims = jwt_verification["claims"]
                assert claims is not None, "JWT claims should exist for verified signatures"
                assert "artifact_id" in claims, "JWT claims must include artifact_id"
                assert claims["artifact_id"] == artifact_id, "JWT artifact_id must match uploaded artifact"

    def test_jwt_tamper_detection_in_verification(self, simple_json_data):
        """Test that JWT verification detects document tampering."""
        # First, create a document with JWT signature
        mock_walacor_response = {
            "walacor_tx_id": "TX_tamper_jwt_test",
            "document_hash": "tamper_test_hash_11111",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_tamper_jwt_test",
                "blockchain_network": "walacor",
                "etid": 100001,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_document', return_value=mock_walacor_response):
            # Upload original document
            upload_response = self.client.post("/api/ingest-json", json=simple_json_data)
            assert upload_response.status_code == 200
            
            # Test verification with tampered hash
            tampered_hash = "tampered_hash_different_from_original_99999"
            verify_response = self.client.post("/api/verify", json={
                "etid": 100001,
                "payloadHash": tampered_hash
            })
            
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["ok"] is True
            assert verify_data["data"]["is_valid"] is False  # Hash mismatch should be detected
            
            # Assert JWT verification is included and detects tampering
            assert "details" in verify_data["data"], "Tamper verification must include details"
            assert "jwt_signature" in verify_data["data"]["details"], "Tamper verification must include JWT verification"
            jwt_verification = verify_data["data"]["details"]["jwt_signature"]
            
            # JWT verification should fail for tampered documents
            # (Either no signature found or signature verification failed)
            if "verified" in jwt_verification:
                assert not jwt_verification["verified"], "JWT verification must fail for tampered documents"
            
            if "error" in jwt_verification and jwt_verification["error"]:
                # Error should indicate the reason for JWT verification failure
                error_msg = jwt_verification["error"]
                assert isinstance(error_msg, str), "JWT error should be a string"

    def test_multiple_document_types_jwt_support(self):
        """Test that JWT signatures work across different document types."""
        document_types = [
            {
                "endpoint": "/api/ingest-json",
                "data": {"type": "simple", "content": "Simple document"},
                "etid": 100001
            },
            {
                "endpoint": "/api/seal",
                "data": {"type": "sealed", "content": "Sealed document"},
                "etid": 100002
            }
        ]
        
        for doc_type in document_types:
            with patch.object(self.mock_walacor, 'seal_document') as mock_seal:
                mock_seal.return_value = {
                    "walacor_tx_id": f"TX_{doc_type['etid']}",
                    "document_hash": f"hash_{doc_type['etid']}",
                    "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
                    "blockchain_proof": {
                        "transaction_id": f"TX_{doc_type['etid']}",
                        "blockchain_network": "walacor",
                        "etid": doc_type['etid'],
                        "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                        "integrity_verified": True,
                        "immutability_established": True
                    }
                }
                
                # Upload document
                response = self.client.post(doc_type["endpoint"], json=doc_type["data"])
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("ok"):
                        # Assert JWT signature is included for all document types
                        assert "signature_jwt" in response_data["data"], f"Document type {doc_type['etid']} must include JWT signature"
                        
                        # Test verification includes JWT verification
                        verify_response = self.client.post("/api/verify", json={
                            "etid": doc_type['etid'],
                            "payloadHash": response_data["data"]["hash"]
                        })
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            if verify_data.get("ok"):
                                assert "details" in verify_data["data"], f"Verification for {doc_type['etid']} must include details"
                                assert "jwt_signature" in verify_data["data"]["details"], f"Verification for {doc_type['etid']} must include JWT verification"

    def test_jwt_verification_with_missing_signature(self):
        """Test JWT verification behavior when signature is missing from database."""
        # Create an artifact directly in database without JWT signature
        session = self.session_local()
        
        test_artifact = Artifact(
            artifact_id="test_no_jwt_123",
            etid=100001,
            payload_sha256="test_hash_no_jwt",
            walacor_tx_id="TX_no_jwt",
            created_by="test",
            signature_jwt=None  # Explicitly no JWT signature
        )
        session.add(test_artifact)
        session.commit()
        session.close()
        
        # Test verification for artifact without JWT signature
        verify_response = self.client.post("/api/verify", json={
            "etid": 100001,
            "payloadHash": "test_hash_no_jwt"
        })
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["ok"] is True
        assert verify_data["data"]["is_valid"] is True  # Hash should still match
        
        # Assert JWT verification handles missing signature gracefully
        assert "jwt_verification" in verify_data["data"], "Verification must include JWT verification even when signature missing"
        jwt_verification = verify_data["data"]["jwt_verification"]
        
        assert not jwt_verification.get("verified", True), "JWT verification should fail when signature is missing"
        assert "error" in jwt_verification, "JWT verification should include error for missing signature"
        
        expected_error_keywords = ["signature", "not", "available", "missing", "none"]
        error_msg = jwt_verification.get("error", "").lower()
        assert any(keyword in error_msg for keyword in expected_error_keywords), f"Error message should indicate missing signature: {error_msg}"

    def test_jwt_verification_performance_impact(self, simple_json_data):
        """Test that JWT verification doesn't significantly impact response times."""
        import time
        
        # Mock Walacor service response
        mock_walacor_response = {
            "walacor_tx_id": "TX_perf_test",
            "document_hash": "perf_test_hash",
            "sealed_timestamp": datetime.now(timezone.utc).isoformat(),
            "blockchain_proof": {
                "transaction_id": "TX_perf_test",
                "blockchain_network": "walacor",
                "etid": 100001,
                "seal_timestamp": datetime.now(timezone.utc).isoformat(),
                "integrity_verified": True,
                "immutability_established": True
            }
        }
        
        with patch.object(self.mock_walacor, 'seal_document', return_value=mock_walacor_response):
            # Upload document
            upload_response = self.client.post("/api/ingest-json", json=simple_json_data)
            assert upload_response.status_code == 200
            
            upload_data = upload_response.json()["data"]
            document_hash = upload_data["hash"]
            
            # Measure verification response time
            start_time = time.time()
            verify_response = self.client.post("/api/verify", json={
                "etid": 100001,
                "payloadHash": document_hash
            })
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert verify_response.status_code == 200
            verify_data = verify_response.json()
            assert verify_data["ok"] is True
            
            # JWT verification should be included
            assert "jwt_verification" in verify_data["data"]
            
            # Response time should be reasonable (less than 1 second for test environment)
            assert response_time < 1.0, f"Verification with JWT should be fast, took {response_time:.3f}s"
            
            print(f"✅ Verification with JWT completed in {response_time:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
