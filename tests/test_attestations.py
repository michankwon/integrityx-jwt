"""
Tests for Attestations API endpoints.

Tests the creation, listing, and validation of attestations.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.src.models import Base, Artifact, Attestation
from backend.src.database import Database


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_attestations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_services] = lambda: {
        "db": Database(session=db_session),
        "attestation_repo": AttestationRepository(),
        "provenance_repo": ProvenanceRepository()
    }
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_artifact(db_session):
    """Create a sample artifact for testing."""
    artifact = Artifact(
        etid=100001,
        payload_sha256="test_hash_12345",
        external_uri="test://example.com/doc.pdf",
        metadata={"test": "data"},
        walacor_tx_id="test_tx_123"
    )
    db_session.add(artifact)
    db_session.commit()
    db_session.refresh(artifact)
    return artifact


class TestAttestationsAPI:
    """Test suite for Attestations API endpoints."""
    
    def test_create_attestation_success(self, client, sample_artifact):
        """Test successful attestation creation."""
        attestation_data = {
            "artifactId": sample_artifact.id,
            "etid": "ATTESTATION_ETID_001",
            "kind": "qc_check",
            "issuedBy": "test_user",
            "details": {
                "score": 95,
                "notes": "Quality check passed",
                "checker": "automated_system"
            }
        }
        
        response = client.post("/api/attestations", json=attestation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        
        attestation = data["data"]
        assert attestation["artifactId"] == sample_artifact.id
        assert attestation["kind"] == "qc_check"
        assert attestation["issuedBy"] == "test_user"
        assert attestation["details"]["score"] == 95
        assert "id" in attestation
        assert "createdAt" in attestation
    
    def test_create_attestation_missing_artifact(self, client):
        """Test attestation creation with non-existent artifact."""
        attestation_data = {
            "artifactId": "non_existent_id",
            "etid": "ATTESTATION_ETID_001",
            "kind": "qc_check",
            "issuedBy": "test_user",
            "details": {"test": "data"}
        }
        
        response = client.post("/api/attestations", json=attestation_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_create_attestation_invalid_json(self, client, sample_artifact):
        """Test attestation creation with invalid JSON details."""
        attestation_data = {
            "artifactId": sample_artifact.id,
            "etid": "ATTESTATION_ETID_001",
            "kind": "qc_check",
            "issuedBy": "test_user",
            "details": "invalid_json_string"  # Should be a dict
        }
        
        response = client.post("/api/attestations", json=attestation_data)
        
        # Should still work as the API accepts any JSON structure
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_create_attestation_missing_required_fields(self, client, sample_artifact):
        """Test attestation creation with missing required fields."""
        # Missing kind
        attestation_data = {
            "artifactId": sample_artifact.id,
            "etid": "ATTESTATION_ETID_001",
            "issuedBy": "test_user",
            "details": {"test": "data"}
        }
        
        response = client.post("/api/attestations", json=attestation_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_list_attestations_success(self, client, sample_artifact):
        """Test successful attestation listing."""
        # Create some test attestations
        attestations_data = [
            {
                "artifactId": sample_artifact.id,
                "etid": "ATTESTATION_ETID_001",
                "kind": "qc_check",
                "issuedBy": "user1",
                "details": {"score": 95}
            },
            {
                "artifactId": sample_artifact.id,
                "etid": "ATTESTATION_ETID_001",
                "kind": "kyc_passed",
                "issuedBy": "user2",
                "details": {"verified": True}
            }
        ]
        
        # Create attestations
        for att_data in attestations_data:
            response = client.post("/api/attestations", json=att_data)
            assert response.status_code == 200
        
        # List attestations
        response = client.get(f"/api/attestations?artifactId={sample_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "attestations" in data["data"]
        
        attestations = data["data"]["attestations"]
        assert len(attestations) == 2
        
        # Check that attestations are ordered by creation date (newest first)
        assert attestations[0]["kind"] == "kyc_passed"  # Created second
        assert attestations[1]["kind"] == "qc_check"    # Created first
    
    def test_list_attestations_empty(self, client, sample_artifact):
        """Test listing attestations for artifact with no attestations."""
        response = client.get(f"/api/attestations?artifactId={sample_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "attestations" in data["data"]
        assert len(data["data"]["attestations"]) == 0
    
    def test_list_attestations_missing_artifact(self, client):
        """Test listing attestations for non-existent artifact."""
        response = client.get("/api/attestations?artifactId=non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_list_attestations_pagination(self, client, sample_artifact):
        """Test attestation listing with pagination."""
        # Create 5 test attestations
        for i in range(5):
            attestation_data = {
                "artifactId": sample_artifact.id,
                "etid": "ATTESTATION_ETID_001",
                "kind": f"test_kind_{i}",
                "issuedBy": f"user_{i}",
                "details": {"index": i}
            }
            response = client.post("/api/attestations", json=attestation_data)
            assert response.status_code == 200
        
        # Test with limit
        response = client.get(f"/api/attestations?artifactId={sample_artifact.id}&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["attestations"]) == 3
        
        # Test with offset
        response = client.get(f"/api/attestations?artifactId={sample_artifact.id}&limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["attestations"]) == 2
    
    def test_attestation_json_validation(self, client, sample_artifact):
        """Test various JSON structures for attestation details."""
        test_cases = [
            {"simple": "value"},
            {"nested": {"level": 2, "data": [1, 2, 3]}},
            {"array": [{"item": 1}, {"item": 2}]},
            {"null_value": None},
            {"boolean": True},
            {"number": 42.5}
        ]
        
        for i, details in enumerate(test_cases):
            attestation_data = {
                "artifactId": sample_artifact.id,
                "etid": "ATTESTATION_ETID_001",
                "kind": f"test_kind_{i}",
                "issuedBy": "test_user",
                "details": details
            }
            
            response = client.post("/api/attestations", json=attestation_data)
            assert response.status_code == 200
            data = response.json()
            assert data["ok"] is True
            assert data["data"]["details"] == details


class TestAttestationRepository:
    """Test suite for AttestationRepository methods."""
    
    def test_create_attestation(self, db_session, sample_artifact):
        """Test attestation creation through repository."""
        from backend.src.repositories import AttestationRepository
        
        repo = AttestationRepository()
        attestation = repo.create(
            session=db_session,
            artifact_id=sample_artifact.id,
            etid="ATTESTATION_ETID_001",
            kind="qc_check",
            issued_by="test_user",
            details={"score": 95}
        )
        
        assert attestation.id is not None
        assert attestation.artifact_id == sample_artifact.id
        assert attestation.kind == "qc_check"
        assert attestation.issued_by == "test_user"
        assert attestation.details == {"score": 95}
    
    def test_list_for_artifact(self, db_session, sample_artifact):
        """Test listing attestations for an artifact."""
        from backend.src.repositories import AttestationRepository
        
        repo = AttestationRepository()
        
        # Create multiple attestations
        for i in range(3):
            repo.create(
                session=db_session,
                artifact_id=sample_artifact.id,
                etid="ATTESTATION_ETID_001",
                kind=f"kind_{i}",
                issued_by=f"user_{i}",
                details={"index": i}
            )
        
        # List attestations
        attestations = repo.list_for_artifact(
            session=db_session,
            artifact_id=sample_artifact.id
        )
        
        assert len(attestations) == 3
        # Should be ordered by creation date (newest first)
        assert attestations[0].kind == "kind_2"
        assert attestations[1].kind == "kind_1"
        assert attestations[2].kind == "kind_0"


if __name__ == "__main__":
    pytest.main([__file__])

