#!/usr/bin/env python3
"""
Test script for Attestations and Provenance models and repositories.

This script tests the new models and repository methods to ensure they work correctly.
"""

import sys
import os
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import Base, Artifact, Attestation, ProvenanceLink, create_database_engine
from src.repositories import AttestationRepository, ProvenanceRepository
from sqlalchemy.orm import sessionmaker

def test_models():
    """Test the new models."""
    print("🧪 Testing Attestation and ProvenanceLink models...")
    
    # Test Attestation model
    attestation = Attestation(
        artifact_id="test-artifact-123",
        etid="ATTESTATION_ETID_001",
        kind="qc_check",
        issued_by="user_123",
        details={"score": 95, "notes": "Quality check passed"}
    )
    
    assert attestation.artifact_id == "test-artifact-123"
    assert attestation.etid == "ATTESTATION_ETID_001"
    assert attestation.kind == "qc_check"
    assert attestation.issued_by == "user_123"
    assert attestation.details["score"] == 95
    
    # Test ProvenanceLink model
    provenance_link = ProvenanceLink(
        parent_artifact_id="parent-123",
        child_artifact_id="child-456",
        relation="contains"
    )
    
    assert provenance_link.parent_artifact_id == "parent-123"
    assert provenance_link.child_artifact_id == "child-456"
    assert provenance_link.relation == "contains"
    
    # Test to_dict methods
    attestation_dict = attestation.to_dict()
    assert "id" in attestation_dict
    assert attestation_dict["artifact_id"] == "test-artifact-123"
    assert attestation_dict["kind"] == "qc_check"
    
    provenance_dict = provenance_link.to_dict()
    assert "id" in provenance_dict
    assert provenance_dict["parent_artifact_id"] == "parent-123"
    assert provenance_dict["relation"] == "contains"
    
    print("✅ Models test passed")
    return True

def test_repositories():
    """Test the repository methods."""
    print("🧪 Testing repository methods...")
    
    # Create in-memory database for testing
    engine = create_database_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create test artifacts
        artifact1 = Artifact(
            loan_id="LOAN_001",
            artifact_type="json",
            etid=100001,
            payload_sha256="a" * 64,
            walacor_tx_id="WAL_TX_001",
            created_by="test_user"
        )
        artifact2 = Artifact(
            loan_id="LOAN_001",
            artifact_type="json",
            etid=100002,
            payload_sha256="b" * 64,
            walacor_tx_id="WAL_TX_002",
            created_by="test_user"
        )
        
        session.add(artifact1)
        session.add(artifact2)
        session.commit()
        
        # Test AttestationRepository
        attestation_repo = AttestationRepository()
        
        # Create attestation
        attestation = attestation_repo.create(
            session,
            artifact_id=artifact1.id,
            etid="ATTESTATION_ETID_001",
            kind="qc_check",
            issued_by="user_123",
            details={"score": 95, "notes": "Quality check passed"}
        )
        
        assert attestation.id is not None
        assert attestation.artifact_id == artifact1.id
        assert attestation.kind == "qc_check"
        
        # List attestations for artifact
        attestations = attestation_repo.list_for_artifact(session, artifact_id=artifact1.id)
        assert len(attestations) == 1
        assert attestations[0].kind == "qc_check"
        
        # Test ProvenanceRepository
        provenance_repo = ProvenanceRepository()
        
        # Create provenance link
        link = provenance_repo.link(
            session,
            parent_id=artifact1.id,
            child_id=artifact2.id,
            relation="contains"
        )
        
        assert link.id is not None
        assert link.parent_artifact_id == artifact1.id
        assert link.child_artifact_id == artifact2.id
        assert link.relation == "contains"
        
        # Test idempotency - should return existing link
        link2 = provenance_repo.link(
            session,
            parent_id=artifact1.id,
            child_id=artifact2.id,
            relation="contains"
        )
        
        assert link.id == link2.id  # Should be the same link
        
        # List children
        children = provenance_repo.list_children(session, parent_id=artifact1.id)
        assert len(children) == 1
        assert children[0].child_artifact_id == artifact2.id
        
        # List parents
        parents = provenance_repo.list_parents(session, child_id=artifact2.id)
        assert len(parents) == 1
        assert parents[0].parent_artifact_id == artifact1.id
        
        # Test lineage
        lineage = provenance_repo.get_lineage(session, artifact_id=artifact1.id)
        assert len(lineage["descendants"]) == 1
        assert len(lineage["ancestors"]) == 0
        
        print("✅ Repository test passed")
        return True
        
    finally:
        session.close()

def test_error_handling():
    """Test error handling in repositories."""
    print("🧪 Testing error handling...")
    
    # Create in-memory database for testing
    engine = create_database_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        attestation_repo = AttestationRepository()
        provenance_repo = ProvenanceRepository()
        
        # Test missing required parameters
        try:
            attestation_repo.create(session, artifact_id="", etid="", kind="", issued_by="", details={})
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        try:
            provenance_repo.link(session, parent_id="", child_id="", relation="")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Test self-reference prevention
        try:
            provenance_repo.link(session, parent_id="same", child_id="same", relation="contains")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        print("✅ Error handling test passed")
        return True
        
    finally:
        session.close()

def main():
    """Run all tests."""
    print("🚀 Starting Attestations and Provenance tests...\n")
    
    try:
        test_models()
        test_repositories()
        test_error_handling()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
