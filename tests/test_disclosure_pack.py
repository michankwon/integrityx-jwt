"""
Tests for Disclosure Pack API endpoint.

Tests the generation and content of disclosure packs.
"""

import pytest
import json
import zipfile
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.src.models import Base, Artifact, Attestation, ProvenanceLink
from backend.src.database import Database


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_disclosure_pack.db"
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
def sample_artifact_with_data(db_session):
    """Create a sample artifact with attestations and provenance links."""
    # Create main artifact
    artifact = Artifact(
        etid=100001,
        payload_sha256="test_hash_12345",
        external_uri="test://example.com/doc.pdf",
        metadata={"test": "data", "version": "1.0"},
        walacor_tx_id="test_tx_123"
    )
    db_session.add(artifact)
    db_session.commit()
    db_session.refresh(artifact)
    
    # Create related artifacts
    related_artifact = Artifact(
        etid=100001,
        payload_sha256="related_hash_67890",
        external_uri="test://example.com/related.pdf",
        metadata={"related": True},
        walacor_tx_id="related_tx_456"
    )
    db_session.add(related_artifact)
    db_session.commit()
    db_session.refresh(related_artifact)
    
    # Create attestations
    attestations = [
        Attestation(
            artifact_id=artifact.id,
            etid="ATTESTATION_ETID_001",
            kind="qc_check",
            issued_by="quality_team",
            details={"score": 95, "notes": "High quality document"}
        ),
        Attestation(
            artifact_id=artifact.id,
            etid="ATTESTATION_ETID_001",
            kind="kyc_passed",
            issued_by="compliance_team",
            details={"verified": True, "method": "document_scan"}
        )
    ]
    
    for att in attestations:
        db_session.add(att)
    
    # Create provenance link
    provenance_link = ProvenanceLink(
        parent_artifact_id=related_artifact.id,
        child_artifact_id=artifact.id,
        relation="derived_from"
    )
    db_session.add(provenance_link)
    
    db_session.commit()
    
    return artifact, related_artifact, attestations, provenance_link


class TestDisclosurePackAPI:
    """Test suite for Disclosure Pack API endpoint."""
    
    def test_disclosure_pack_success(self, client, sample_artifact_with_data):
        """Test successful disclosure pack generation."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "content-disposition" in response.headers
        assert f"disclosure_{artifact.id}.zip" in response.headers["content-disposition"]
        
        # Verify ZIP content
        zip_content = response.content
        assert len(zip_content) > 0
        
        # Extract and verify ZIP structure
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # Check required files are present
            required_files = [
                "proof.json",
                "artifact.json", 
                "attestations.json",
                "audit_events.json",
                "manifest.json"
            ]
            
            for required_file in required_files:
                assert required_file in file_list, f"Missing required file: {required_file}"
    
    def test_disclosure_pack_content_artifact_json(self, client, sample_artifact_with_data):
        """Test that artifact.json contains correct artifact data."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            artifact_json = zip_file.read("artifact.json")
            artifact_data = json.loads(artifact_json)
            
            assert artifact_data["id"] == artifact.id
            assert artifact_data["etid"] == artifact.etid
            assert artifact_data["payload_sha256"] == artifact.payload_sha256
            assert artifact_data["external_uri"] == artifact.external_uri
            assert artifact_data["metadata"] == artifact.metadata
            assert artifact_data["walacor_tx_id"] == artifact.walacor_tx_id
            assert "created_at" in artifact_data
    
    def test_disclosure_pack_content_attestations_json(self, client, sample_artifact_with_data):
        """Test that attestations.json contains correct attestation data."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            attestations_json = zip_file.read("attestations.json")
            attestations_data = json.loads(attestations_json)
            
            assert len(attestations_data) == 2
            
            # Check attestation details
            qc_attestation = next(att for att in attestations_data if att["kind"] == "qc_check")
            assert qc_attestation["issued_by"] == "quality_team"
            assert qc_attestation["details"]["score"] == 95
            assert qc_attestation["details"]["notes"] == "High quality document"
            
            kyc_attestation = next(att for att in attestations_data if att["kind"] == "kyc_passed")
            assert kyc_attestation["issued_by"] == "compliance_team"
            assert kyc_attestation["details"]["verified"] is True
            assert kyc_attestation["details"]["method"] == "document_scan"
    
    def test_disclosure_pack_content_manifest_json(self, client, sample_artifact_with_data):
        """Test that manifest.json contains correct metadata."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            manifest_json = zip_file.read("manifest.json")
            manifest_data = json.loads(manifest_json)
            
            # Check manifest structure
            assert manifest_data["disclosure_pack_version"] == "1.0"
            assert manifest_data["artifact_id"] == artifact.id
            assert manifest_data["artifact_hash"] == artifact.payload_sha256
            assert manifest_data["artifact_etid"] == artifact.etid
            assert manifest_data["algorithm"] == "SHA-256"
            assert manifest_data["app_version"] == "1.0.0"
            assert manifest_data["total_attestations"] == 2
            assert manifest_data["walacor_tx_id"] == artifact.walacor_tx_id
            
            # Check required fields
            assert "generated_at" in manifest_data
            assert "created_at" in manifest_data
            assert "total_events" in manifest_data
    
    def test_disclosure_pack_content_audit_events_json(self, client, sample_artifact_with_data):
        """Test that audit_events.json contains audit events."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            events_json = zip_file.read("audit_events.json")
            events_data = json.loads(events_json)
            
            # Should be a list (may be empty if no events exist)
            assert isinstance(events_data, list)
    
    def test_disclosure_pack_content_proof_json(self, client, sample_artifact_with_data):
        """Test that proof.json contains proof data or error message."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            proof_json = zip_file.read("proof.json")
            proof_data = json.loads(proof_json)
            
            # Should contain either proof data or error message
            assert "walacor_tx_id" in proof_data
            assert proof_data["walacor_tx_id"] == artifact.walacor_tx_id
    
    def test_disclosure_pack_artifact_not_found(self, client):
        """Test disclosure pack generation for non-existent artifact."""
        response = client.get("/api/disclosure-pack?id=non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_disclosure_pack_missing_id_parameter(self, client):
        """Test disclosure pack generation with missing ID parameter."""
        response = client.get("/api/disclosure-pack")
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_disclosure_pack_empty_id_parameter(self, client):
        """Test disclosure pack generation with empty ID parameter."""
        response = client.get("/api/disclosure-pack?id=")
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_disclosure_pack_large_artifact(self, client, db_session):
        """Test disclosure pack generation for artifact with many attestations."""
        # Create artifact
        artifact = Artifact(
            etid=100001,
            payload_sha256="large_test_hash",
            external_uri="test://example.com/large_doc.pdf",
            metadata={"size": "large"},
            walacor_tx_id="large_tx_123"
        )
        db_session.add(artifact)
        db_session.commit()
        db_session.refresh(artifact)
        
        # Create many attestations
        for i in range(50):
            attestation = Attestation(
                artifact_id=artifact.id,
                etid="ATTESTATION_ETID_001",
                kind=f"test_kind_{i}",
                issued_by=f"user_{i}",
                details={"index": i, "data": f"test_data_{i}"}
            )
            db_session.add(attestation)
        
        db_session.commit()
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        
        assert response.status_code == 200
        zip_content = response.content
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            attestations_json = zip_file.read("attestations.json")
            attestations_data = json.loads(attestations_json)
            
            # Should contain all attestations (up to limit of 100)
            assert len(attestations_data) == 50
            
            # Check manifest reflects correct count
            manifest_json = zip_file.read("manifest.json")
            manifest_data = json.loads(manifest_json)
            assert manifest_data["total_attestations"] == 50
    
    def test_disclosure_pack_zip_integrity(self, client, sample_artifact_with_data):
        """Test that the generated ZIP file is valid and can be extracted."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        zip_content = response.content
        
        # Test ZIP file integrity
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
                # Test that we can read all files
                for file_name in zip_file.namelist():
                    file_content = zip_file.read(file_name)
                    assert len(file_content) > 0, f"File {file_name} is empty"
                    
                    # Test that JSON files are valid JSON
                    if file_name.endswith('.json'):
                        try:
                            json.loads(file_content)
                        except json.JSONDecodeError as e:
                            pytest.fail(f"Invalid JSON in {file_name}: {e}")
        except zipfile.BadZipFile as e:
            pytest.fail(f"Invalid ZIP file: {e}")
    
    def test_disclosure_pack_content_disposition_header(self, client, sample_artifact_with_data):
        """Test that Content-Disposition header is correctly set."""
        artifact, related_artifact, attestations, provenance_link = sample_artifact_with_data
        
        response = client.get(f"/api/disclosure-pack?id={artifact.id}")
        
        content_disposition = response.headers.get("content-disposition")
        assert content_disposition is not None
        assert "attachment" in content_disposition
        assert f"filename=\"disclosure_{artifact.id}.zip\"" in content_disposition


if __name__ == "__main__":
    pytest.main([__file__])

