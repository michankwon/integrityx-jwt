"""
Repository classes for database operations.

This module provides repository classes that encapsulate database operations
for different models, following the repository pattern for clean separation
of concerns and testability.

Repositories:
- AttestationRepository: Operations for attestation management
- ProvenanceRepository: Operations for provenance link management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging

from .models import Attestation, ProvenanceLink

logger = logging.getLogger(__name__)


class AttestationRepository:
    """
    Repository for attestation-related database operations.
    
    Provides methods for creating, querying, and managing attestations
    associated with artifacts.
    """
    
    def create(
        self, 
        session: Session, 
        *, 
        artifact_id: str, 
        etid: str, 
        kind: str, 
        issued_by: str, 
        details: dict
    ) -> Attestation:
        """
        Create a new attestation.
        
        Args:
            session: Database session
            artifact_id: ID of the artifact being attested
            etid: Entity Type ID for Walacor
            kind: Type of attestation (e.g., 'qc_check', 'kyc_passed')
            issued_by: User or service ID that issued the attestation
            details: Free-form metadata as dictionary
            
        Returns:
            Created Attestation instance
            
        Raises:
            ValueError: If required parameters are missing or invalid
            IntegrityError: If database constraints are violated
        """
        if not all([artifact_id, etid, kind, issued_by]):
            raise ValueError("artifact_id, etid, kind, and issued_by are required")
        
        if not isinstance(details, dict):
            raise ValueError("details must be a dictionary")
        
        attestation = Attestation(
            artifact_id=artifact_id,
            etid=etid,
            kind=kind,
            issued_by=issued_by,
            details=details
        )
        
        session.add(attestation)
        session.flush()  # Get the ID without committing
        
        logger.info(f"Created attestation {attestation.id} for artifact {artifact_id} (kind: {kind})")
        return attestation
    
    def list_for_artifact(
        self, 
        session: Session, 
        *, 
        artifact_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Attestation]:
        """
        List attestations for a specific artifact.
        
        Args:
            session: Database session
            artifact_id: ID of the artifact
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of Attestation instances, ordered by creation date (newest first)
        """
        if not artifact_id:
            raise ValueError("artifact_id is required")
        
        query = session.query(Attestation).filter(
            Attestation.artifact_id == artifact_id
        ).order_by(Attestation.created_at.desc())
        
        attestations = query.offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(attestations)} attestations for artifact {artifact_id}")
        return attestations
    
    def get_by_id(self, session: Session, attestation_id: int) -> Optional[Attestation]:
        """
        Get an attestation by its ID.
        
        Args:
            session: Database session
            attestation_id: ID of the attestation
            
        Returns:
            Attestation instance if found, None otherwise
        """
        return session.query(Attestation).filter(Attestation.id == attestation_id).first()
    
    def list_by_kind(
        self, 
        session: Session, 
        *, 
        kind: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Attestation]:
        """
        List attestations by kind.
        
        Args:
            session: Database session
            kind: Type of attestation to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of Attestation instances
        """
        if not kind:
            raise ValueError("kind is required")
        
        query = session.query(Attestation).filter(
            Attestation.kind == kind
        ).order_by(Attestation.created_at.desc())
        
        attestations = query.offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(attestations)} attestations of kind '{kind}'")
        return attestations


class ProvenanceRepository:
    """
    Repository for provenance link-related database operations.
    
    Provides methods for creating, querying, and managing provenance
    relationships between artifacts.
    """
    
    def link(
        self, 
        session: Session, 
        *, 
        parent_id: str, 
        child_id: str, 
        relation: str
    ) -> ProvenanceLink:
        """
        Create a provenance link between two artifacts.
        
        This method is idempotent - if a link already exists between
        the same parent and child artifacts, it returns the existing link.
        
        Args:
            session: Database session
            parent_id: ID of the parent artifact
            child_id: ID of the child artifact
            relation: Type of relationship (e.g., 'contains', 'derived_from')
            
        Returns:
            ProvenanceLink instance (newly created or existing)
            
        Raises:
            ValueError: If required parameters are missing or invalid
            IntegrityError: If database constraints are violated
        """
        if not all([parent_id, child_id, relation]):
            raise ValueError("parent_id, child_id, and relation are required")
        
        if parent_id == child_id:
            raise ValueError("parent_id and child_id must be different")
        
        # Check if link already exists
        existing_link = session.query(ProvenanceLink).filter(
            ProvenanceLink.parent_artifact_id == parent_id,
            ProvenanceLink.child_artifact_id == child_id
        ).first()
        
        if existing_link:
            logger.info(f"Provenance link already exists between {parent_id} and {child_id}")
            return existing_link
        
        # Create new link
        provenance_link = ProvenanceLink(
            parent_artifact_id=parent_id,
            child_artifact_id=child_id,
            relation=relation
        )
        
        try:
            session.add(provenance_link)
            session.flush()  # Get the ID without committing
            
            logger.info(f"Created provenance link {provenance_link.id}: {parent_id} -> {child_id} ({relation})")
            return provenance_link
            
        except IntegrityError as e:
            # Handle race condition where another process created the same link
            session.rollback()
            logger.warning(f"Integrity error during provenance link creation, retrying: {e}")
            
            # Try to find the existing link again
            existing_link = session.query(ProvenanceLink).filter(
                ProvenanceLink.parent_artifact_id == parent_id,
                ProvenanceLink.child_artifact_id == child_id
            ).first()
            
            if existing_link:
                logger.info(f"Found existing provenance link on retry: {existing_link.id}")
                return existing_link
            else:
                raise
    
    def list_children(
        self, 
        session: Session, 
        *, 
        parent_id: str, 
        relation: Optional[str] = None
    ) -> List[ProvenanceLink]:
        """
        List all child artifacts for a given parent artifact.
        
        Args:
            session: Database session
            parent_id: ID of the parent artifact
            relation: Optional filter by relationship type
            
        Returns:
            List of ProvenanceLink instances
        """
        if not parent_id:
            raise ValueError("parent_id is required")
        
        query = session.query(ProvenanceLink).filter(
            ProvenanceLink.parent_artifact_id == parent_id
        )
        
        if relation:
            query = query.filter(ProvenanceLink.relation == relation)
        
        links = query.order_by(ProvenanceLink.created_at.desc()).all()
        
        logger.info(f"Retrieved {len(links)} child links for parent {parent_id}")
        return links
    
    def list_parents(
        self, 
        session: Session, 
        *, 
        child_id: str, 
        relation: Optional[str] = None
    ) -> List[ProvenanceLink]:
        """
        List all parent artifacts for a given child artifact.
        
        Args:
            session: Database session
            child_id: ID of the child artifact
            relation: Optional filter by relationship type
            
        Returns:
            List of ProvenanceLink instances
        """
        if not child_id:
            raise ValueError("child_id is required")
        
        query = session.query(ProvenanceLink).filter(
            ProvenanceLink.child_artifact_id == child_id
        )
        
        if relation:
            query = query.filter(ProvenanceLink.relation == relation)
        
        links = query.order_by(ProvenanceLink.created_at.desc()).all()
        
        logger.info(f"Retrieved {len(links)} parent links for child {child_id}")
        return links
    
    def get_by_id(self, session: Session, link_id: int) -> Optional[ProvenanceLink]:
        """
        Get a provenance link by its ID.
        
        Args:
            session: Database session
            link_id: ID of the provenance link
            
        Returns:
            ProvenanceLink instance if found, None otherwise
        """
        return session.query(ProvenanceLink).filter(ProvenanceLink.id == link_id).first()
    
    def delete_link(
        self, 
        session: Session, 
        *, 
        parent_id: str, 
        child_id: str
    ) -> bool:
        """
        Delete a provenance link between two artifacts.
        
        Args:
            session: Database session
            parent_id: ID of the parent artifact
            child_id: ID of the child artifact
            
        Returns:
            True if a link was deleted, False if no link existed
        """
        if not all([parent_id, child_id]):
            raise ValueError("parent_id and child_id are required")
        
        link = session.query(ProvenanceLink).filter(
            ProvenanceLink.parent_artifact_id == parent_id,
            ProvenanceLink.child_artifact_id == child_id
        ).first()
        
        if link:
            session.delete(link)
            logger.info(f"Deleted provenance link between {parent_id} and {child_id}")
            return True
        else:
            logger.info(f"No provenance link found between {parent_id} and {child_id}")
            return False
    
    def get_lineage(
        self, 
        session: Session, 
        *, 
        artifact_id: str, 
        max_depth: int = 10
    ) -> dict:
        """
        Get the complete lineage (ancestors and descendants) for an artifact.
        
        Args:
            session: Database session
            artifact_id: ID of the artifact
            max_depth: Maximum depth to traverse (prevents infinite loops)
            
        Returns:
            Dictionary with 'ancestors' and 'descendants' lists
        """
        if not artifact_id:
            raise ValueError("artifact_id is required")
        
        ancestors = []
        descendants = []
        visited = set()
        
        def collect_ancestors(current_id: str, depth: int = 0):
            if depth >= max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            parent_links = self.list_parents(session, child_id=current_id)
            
            for link in parent_links:
                ancestors.append(link)
                collect_ancestors(link.parent_artifact_id, depth + 1)
        
        def collect_descendants(current_id: str, depth: int = 0):
            if depth >= max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            child_links = self.list_children(session, parent_id=current_id)
            
            for link in child_links:
                descendants.append(link)
                collect_descendants(link.child_artifact_id, depth + 1)
        
        collect_ancestors(artifact_id)
        visited.clear()  # Reset for descendants
        collect_descendants(artifact_id)
        
        logger.info(f"Retrieved lineage for {artifact_id}: {len(ancestors)} ancestors, {len(descendants)} descendants")
        
        return {
            'ancestors': ancestors,
            'descendants': descendants
        }

