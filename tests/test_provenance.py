"""
Tests for Provenance API endpoints.

Tests the creation, listing, and idempotency of provenance links.
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.src.models import Base, Artifact, ProvenanceLink
from backend.src.database import Database


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_provenance.db"
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
def sample_artifacts(db_session):
    """Create sample artifacts for testing."""
    artifacts = []
    for i in range(3):
        artifact = Artifact(
            etid=100001,
            payload_sha256=f"test_hash_{i}",
            external_uri=f"test://example.com/doc_{i}.pdf",
            metadata={"index": i},
            walacor_tx_id=f"test_tx_{i}"
        )
        db_session.add(artifact)
        artifacts.append(artifact)
    
    db_session.commit()
    for artifact in artifacts:
        db_session.refresh(artifact)
    
    return artifacts


class TestProvenanceAPI:
    """Test suite for Provenance API endpoints."""
    
    def test_create_provenance_link_success(self, client, sample_artifacts):
        """Test successful provenance link creation."""
        parent_artifact = sample_artifacts[0]
        child_artifact = sample_artifacts[1]
        
        link_data = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": child_artifact.id,
            "relation": "contains"
        }
        
        response = client.post("/api/provenance/link", json=link_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        
        link = data["data"]
        assert link["parentArtifactId"] == parent_artifact.id
        assert link["childArtifactId"] == child_artifact.id
        assert link["relation"] == "contains"
        assert "id" in link
        assert "createdAt" in link
    
    def test_create_provenance_link_duplicate_idempotent(self, client, sample_artifacts):
        """Test that creating duplicate provenance links is idempotent."""
        parent_artifact = sample_artifacts[0]
        child_artifact = sample_artifacts[1]
        
        link_data = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": child_artifact.id,
            "relation": "contains"
        }
        
        # Create first link
        response1 = client.post("/api/provenance/link", json=link_data)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["ok"] is True
        first_link_id = data1["data"]["id"]
        
        # Create duplicate link (should return existing)
        response2 = client.post("/api/provenance/link", json=link_data)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["ok"] is True
        second_link_id = data2["data"]["id"]
        
        # Should return the same link ID (idempotent)
        assert first_link_id == second_link_id
    
    def test_create_provenance_link_missing_parent(self, client, sample_artifacts):
        """Test provenance link creation with non-existent parent artifact."""
        child_artifact = sample_artifacts[0]
        
        link_data = {
            "parentArtifactId": "non_existent_parent",
            "childArtifactId": child_artifact.id,
            "relation": "contains"
        }
        
        response = client.post("/api/provenance/link", json=link_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_create_provenance_link_missing_child(self, client, sample_artifacts):
        """Test provenance link creation with non-existent child artifact."""
        parent_artifact = sample_artifacts[0]
        
        link_data = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": "non_existent_child",
            "relation": "contains"
        }
        
        response = client.post("/api/provenance/link", json=link_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_create_provenance_link_invalid_relation(self, client, sample_artifacts):
        """Test provenance link creation with invalid relation type."""
        parent_artifact = sample_artifacts[0]
        child_artifact = sample_artifacts[1]
        
        link_data = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": child_artifact.id,
            "relation": "invalid_relation"
        }
        
        # Should still work as we don't validate relation types strictly
        response = client.post("/api/provenance/link", json=link_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_list_children_success(self, client, sample_artifacts):
        """Test successful children listing."""
        parent_artifact = sample_artifacts[0]
        child1 = sample_artifacts[1]
        child2 = sample_artifacts[2]
        
        # Create links
        for child in [child1, child2]:
            link_data = {
                "parentArtifactId": parent_artifact.id,
                "childArtifactId": child.id,
                "relation": "contains"
            }
            response = client.post("/api/provenance/link", json=link_data)
            assert response.status_code == 200
        
        # List children
        response = client.get(f"/api/provenance/children?parentId={parent_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "children" in data["data"]
        
        children = data["data"]["children"]
        assert len(children) == 2
        
        child_ids = [child["childArtifactId"] for child in children]
        assert child1.id in child_ids
        assert child2.id in child_ids
    
    def test_list_children_empty(self, client, sample_artifacts):
        """Test listing children for artifact with no children."""
        parent_artifact = sample_artifacts[0]
        
        response = client.get(f"/api/provenance/children?parentId={parent_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "children" in data["data"]
        assert len(data["data"]["children"]) == 0
    
    def test_list_children_missing_parent(self, client):
        """Test listing children for non-existent parent artifact."""
        response = client.get("/api/provenance/children?parentId=non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_list_children_with_relation_filter(self, client, sample_artifacts):
        """Test listing children with relation filter."""
        parent_artifact = sample_artifacts[0]
        child1 = sample_artifacts[1]
        child2 = sample_artifacts[2]
        
        # Create links with different relations
        link_data1 = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": child1.id,
            "relation": "contains"
        }
        response = client.post("/api/provenance/link", json=link_data1)
        assert response.status_code == 200
        
        link_data2 = {
            "parentArtifactId": parent_artifact.id,
            "childArtifactId": child2.id,
            "relation": "derived_from"
        }
        response = client.post("/api/provenance/link", json=link_data2)
        assert response.status_code == 200
        
        # List children with relation filter
        response = client.get(f"/api/provenance/children?parentId={parent_artifact.id}&relation=contains")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        children = data["data"]["children"]
        assert len(children) == 1
        assert children[0]["childArtifactId"] == child1.id
        assert children[0]["relation"] == "contains"
    
    def test_list_parents_success(self, client, sample_artifacts):
        """Test successful parents listing."""
        child_artifact = sample_artifacts[0]
        parent1 = sample_artifacts[1]
        parent2 = sample_artifacts[2]
        
        # Create links
        for parent in [parent1, parent2]:
            link_data = {
                "parentArtifactId": parent.id,
                "childArtifactId": child_artifact.id,
                "relation": "derived_from"
            }
            response = client.post("/api/provenance/link", json=link_data)
            assert response.status_code == 200
        
        # List parents
        response = client.get(f"/api/provenance/parents?childId={child_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "parents" in data["data"]
        
        parents = data["data"]["parents"]
        assert len(parents) == 2
        
        parent_ids = [parent["parentArtifactId"] for parent in parents]
        assert parent1.id in parent_ids
        assert parent2.id in parent_ids
    
    def test_list_parents_empty(self, client, sample_artifacts):
        """Test listing parents for artifact with no parents."""
        child_artifact = sample_artifacts[0]
        
        response = client.get(f"/api/provenance/parents?childId={child_artifact.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert "parents" in data["data"]
        assert len(data["data"]["parents"]) == 0
    
    def test_list_parents_missing_child(self, client):
        """Test listing parents for non-existent child artifact."""
        response = client.get("/api/provenance/parents?childId=non_existent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data
        assert "ARTIFACT_NOT_FOUND" in data["error"]["code"]
    
    def test_list_parents_with_relation_filter(self, client, sample_artifacts):
        """Test listing parents with relation filter."""
        child_artifact = sample_artifacts[0]
        parent1 = sample_artifacts[1]
        parent2 = sample_artifacts[2]
        
        # Create links with different relations
        link_data1 = {
            "parentArtifactId": parent1.id,
            "childArtifactId": child_artifact.id,
            "relation": "derived_from"
        }
        response = client.post("/api/provenance/link", json=link_data1)
        assert response.status_code == 200
        
        link_data2 = {
            "parentArtifactId": parent2.id,
            "childArtifactId": child_artifact.id,
            "relation": "supersedes"
        }
        response = client.post("/api/provenance/link", json=link_data2)
        assert response.status_code == 200
        
        # List parents with relation filter
        response = client.get(f"/api/provenance/parents?childId={child_artifact.id}&relation=derived_from")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        parents = data["data"]["parents"]
        assert len(parents) == 1
        assert parents[0]["parentArtifactId"] == parent1.id
        assert parents[0]["relation"] == "derived_from"


class TestProvenanceRepository:
    """Test suite for ProvenanceRepository methods."""
    
    def test_link_creation(self, db_session, sample_artifacts):
        """Test provenance link creation through repository."""
        from backend.src.repositories import ProvenanceRepository
        
        repo = ProvenanceRepository()
        parent_artifact = sample_artifacts[0]
        child_artifact = sample_artifacts[1]
        
        link = repo.link(
            session=db_session,
            parent_id=parent_artifact.id,
            child_id=child_artifact.id,
            relation="contains"
        )
        
        assert link.id is not None
        assert link.parent_artifact_id == parent_artifact.id
        assert link.child_artifact_id == child_artifact.id
        assert link.relation == "contains"
    
    def test_link_idempotency(self, db_session, sample_artifacts):
        """Test that link creation is idempotent."""
        from backend.src.repositories import ProvenanceRepository
        
        repo = ProvenanceRepository()
        parent_artifact = sample_artifacts[0]
        child_artifact = sample_artifacts[1]
        
        # Create first link
        link1 = repo.link(
            session=db_session,
            parent_id=parent_artifact.id,
            child_id=child_artifact.id,
            relation="contains"
        )
        
        # Create duplicate link (should return existing)
        link2 = repo.link(
            session=db_session,
            parent_id=parent_artifact.id,
            child_id=child_artifact.id,
            relation="contains"
        )
        
        # Should return the same link
        assert link1.id == link2.id
        assert link1.parent_artifact_id == link2.parent_artifact_id
        assert link1.child_artifact_id == link2.child_artifact_id
    
    def test_list_children(self, db_session, sample_artifacts):
        """Test listing children through repository."""
        from backend.src.repositories import ProvenanceRepository
        
        repo = ProvenanceRepository()
        parent_artifact = sample_artifacts[0]
        child1 = sample_artifacts[1]
        child2 = sample_artifacts[2]
        
        # Create links
        repo.link(db_session, parent_artifact.id, child1.id, "contains")
        repo.link(db_session, parent_artifact.id, child2.id, "derived_from")
        
        # List children
        children = repo.list_children(db_session, parent_id=parent_artifact.id)
        
        assert len(children) == 2
        child_ids = [child.child_artifact_id for child in children]
        assert child1.id in child_ids
        assert child2.id in child_ids
    
    def test_list_parents(self, db_session, sample_artifacts):
        """Test listing parents through repository."""
        from backend.src.repositories import ProvenanceRepository
        
        repo = ProvenanceRepository()
        child_artifact = sample_artifacts[0]
        parent1 = sample_artifacts[1]
        parent2 = sample_artifacts[2]
        
        # Create links
        repo.link(db_session, parent1.id, child_artifact.id, "derived_from")
        repo.link(db_session, parent2.id, child_artifact.id, "supersedes")
        
        # List parents
        parents = repo.list_parents(db_session, child_id=child_artifact.id)
        
        assert len(parents) == 2
        parent_ids = [parent.parent_artifact_id for parent in parents]
        assert parent1.id in parent_ids
        assert parent2.id in parent_ids


if __name__ == "__main__":
    pytest.main([__file__])

