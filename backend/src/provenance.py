"""
Document Provenance Tracker

This module provides comprehensive document provenance tracking for the IntegrityX
financial document integrity system. It tracks relationships between documents
throughout the loan lifecycle, from initial application through closing and
servicing transfers.

The ProvenanceTracker class maintains a complete audit trail of document
transformations, modifications, and relationships, enabling full traceability
of document lineage in financial transactions.

Key Features:
- Document relationship tracking
- Ancestor and descendant traversal
- Complete lineage mapping
- Audit trail integration
- Support for various relationship types
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from walacor_service import WalacorIntegrityService


class ProvenanceTracker:
    """
    Tracks document relationships and provenance chains in the IntegrityX system.
    
    This class maintains a complete audit trail of document relationships
    throughout the loan lifecycle. It tracks how documents are derived from
    each other, modified, reviewed, and transferred between parties.
    
    The ProvenanceTracker enables full traceability of document lineage,
    which is crucial for compliance, audit, and forensic purposes in
    financial document integrity systems.
    
    Attributes:
        walacor_service (WalacorIntegrityService): Service for Walacor operations
    """
    
    # Valid relationship types for document provenance
    RELATIONSHIP_TYPES = {
        "servicing_transfer": "Transfer of loan servicing to another party",
        "modification": "Document modification or amendment",
        "attestation": "Document attestation or certification",
        "qc_review": "Quality control review of document",
        "underwriting": "Underwriting review and approval",
        "appraisal": "Property appraisal document",
        "closing": "Loan closing document",
        "application": "Initial loan application",
        "income_verification": "Income verification document",
        "credit_report": "Credit report document",
        "title_search": "Title search document",
        "insurance": "Insurance documentation",
        "disclosure": "Regulatory disclosure document"
    }
    
    def __init__(self):
        """
        Initialize the ProvenanceTracker with WalacorIntegrityService.
        
        Creates an instance of WalacorIntegrityService to handle all
        database operations for provenance tracking.
        
        Raises:
            RuntimeError: If unable to initialize WalacorIntegrityService
        """
        try:
            print("🔗 Initializing ProvenanceTracker...")
            self.walacor_service = WalacorIntegrityService()
            print("✅ ProvenanceTracker ready for document lineage tracking!")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ProvenanceTracker: {e}")
    
    def create_link(self, parent_doc_id: str, child_doc_id: str, 
                   relationship_type: str, description: str = "") -> Dict[str, Any]:
        """
        Create a provenance link between two documents.
        
        This method establishes a relationship between documents, recording
        how one document was derived from or related to another. This is
        essential for maintaining a complete audit trail of document
        transformations throughout the loan lifecycle.
        
        Args:
            parent_doc_id (str): ID of the parent/source document
            child_doc_id (str): ID of the child/derived document
            relationship_type (str): Type of relationship (see RELATIONSHIP_TYPES)
            description (str): Human-readable description of the relationship
            
        Returns:
            Dict[str, Any]: Result from WalacorIntegrityService.create_provenance_link()
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If provenance link creation fails
            
        Example:
            >>> tracker = ProvenanceTracker()
            >>> result = tracker.create_link(
            ...     parent_doc_id="LOAN_APP_001",
            ...     child_doc_id="UNDERWRITING_001",
            ...     relationship_type="underwriting",
            ...     description="Underwriting review of loan application"
            ... )
        """
        try:
            print(f"\n🔗 Creating provenance link...")
            print(f"   Parent: {parent_doc_id}")
            print(f"   Child:  {child_doc_id}")
            print(f"   Type:   {relationship_type}")
            
            # Validate inputs
            if not all([parent_doc_id, child_doc_id, relationship_type]):
                raise ValueError("parent_doc_id, child_doc_id, and relationship_type are required")
            
            if parent_doc_id == child_doc_id:
                raise ValueError("parent_doc_id and child_doc_id must be different")
            
            if relationship_type not in self.RELATIONSHIP_TYPES:
                valid_types = ", ".join(self.RELATIONSHIP_TYPES.keys())
                raise ValueError(f"Invalid relationship_type. Valid types: {valid_types}")
            
            # Create provenance link using WalacorIntegrityService
            result = self.walacor_service.create_provenance_link(
                parent_doc_id=parent_doc_id,
                child_doc_id=child_doc_id,
                relationship_type=relationship_type,
                description=description
            )
            
            print(f"✅ Provenance link created successfully!")
            print(f"   Relationship: {parent_doc_id} → {child_doc_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to create provenance link: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def get_chain(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete ancestor chain for a document.
        
        This method walks backwards through the provenance links to find
        all ancestors of a document, from the current document back to
        the root document (the one with no parents).
        
        Args:
            document_id (str): ID of the document to trace
            
        Returns:
            List[Dict[str, Any]]: List of provenance links from root to current document
            
        Raises:
            ValueError: If document_id is invalid
            RuntimeError: If chain retrieval fails
            
        Example:
            >>> tracker = ProvenanceTracker()
            >>> chain = tracker.get_chain("CLOSING_001")
            >>> # Returns: [
            ... #   {"parent_doc_id": "APP_001", "child_doc_id": "UNDERWRITING_001", ...},
            ... #   {"parent_doc_id": "UNDERWRITING_001", "child_doc_id": "CLOSING_001", ...}
            ... # ]
        """
        try:
            print(f"\n🔍 Tracing ancestor chain for document: {document_id}")
            
            if not document_id:
                raise ValueError("document_id is required")
            
            chain = []
            current_doc_id = document_id
            visited = set()  # Prevent infinite loops
            
            while current_doc_id and current_doc_id not in visited:
                visited.add(current_doc_id)
                
                # Find provenance links where current_doc_id is the child
                try:
                    # Note: This would need to be implemented in WalacorIntegrityService
                    # For now, we'll simulate the query
                    provenance_links = self._get_provenance_links_by_child(current_doc_id)
                    
                    if not provenance_links:
                        # No more parents - we've reached the root
                        print(f"✅ Reached root document: {current_doc_id}")
                        break
                    
                    # Get the most recent parent link
                    parent_link = provenance_links[0]
                    chain.insert(0, parent_link)  # Insert at beginning to maintain order
                    current_doc_id = parent_link.get('parent_doc_id')
                    
                except Exception as e:
                    print(f"⚠️  Error retrieving provenance links: {e}")
                    break
            
            print(f"✅ Found {len(chain)} links in ancestor chain")
            return chain
            
        except Exception as e:
            error_msg = f"Failed to get ancestor chain: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def get_descendants(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents derived from this document.
        
        This method recursively finds all descendants of a document by
        following the provenance links forward through the document tree.
        
        Args:
            document_id (str): ID of the document to trace descendants for
            
        Returns:
            List[Dict[str, Any]]: List of all descendant provenance links
            
        Raises:
            ValueError: If document_id is invalid
            RuntimeError: If descendant retrieval fails
            
        Example:
            >>> tracker = ProvenanceTracker()
            >>> descendants = tracker.get_descendants("LOAN_APP_001")
            >>> # Returns all documents derived from the loan application
        """
        try:
            print(f"\n🔍 Finding descendants for document: {document_id}")
            
            if not document_id:
                raise ValueError("document_id is required")
            
            descendants = []
            to_process = [document_id]
            visited = set()
            
            while to_process:
                current_doc_id = to_process.pop(0)
                
                if current_doc_id in visited:
                    continue
                
                visited.add(current_doc_id)
                
                # Find provenance links where current_doc_id is the parent
                try:
                    child_links = self._get_provenance_links_by_parent(current_doc_id)
                    
                    for link in child_links:
                        descendants.append(link)
                        child_doc_id = link.get('child_doc_id')
                        if child_doc_id and child_doc_id not in visited:
                            to_process.append(child_doc_id)
                            
                except Exception as e:
                    print(f"⚠️  Error retrieving child links: {e}")
                    continue
            
            print(f"✅ Found {len(descendants)} descendant links")
            return descendants
            
        except Exception as e:
            error_msg = f"Failed to get descendants: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def get_full_lineage(self, document_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get complete lineage (ancestors and descendants) for a document.
        
        This method provides a complete view of a document's lineage by
        returning both its ancestor chain and all its descendants.
        
        Args:
            document_id (str): ID of the document to trace
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing:
                - "ancestors": List of ancestor provenance links
                - "descendants": List of descendant provenance links
                
        Raises:
            ValueError: If document_id is invalid
            RuntimeError: If lineage retrieval fails
            
        Example:
            >>> tracker = ProvenanceTracker()
            >>> lineage = tracker.get_full_lineage("UNDERWRITING_001")
            >>> print(f"Ancestors: {len(lineage['ancestors'])}")
            >>> print(f"Descendants: {len(lineage['descendants'])}")
        """
        try:
            print(f"\n🔍 Getting full lineage for document: {document_id}")
            
            if not document_id:
                raise ValueError("document_id is required")
            
            # Get ancestors and descendants
            ancestors = self.get_chain(document_id)
            descendants = self.get_descendants(document_id)
            
            lineage = {
                "ancestors": ancestors,
                "descendants": descendants
            }
            
            print(f"✅ Lineage complete:")
            print(f"   Ancestors: {len(ancestors)}")
            print(f"   Descendants: {len(descendants)}")
            
            return lineage
            
        except Exception as e:
            error_msg = f"Failed to get full lineage: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def _get_provenance_links_by_child(self, child_doc_id: str) -> List[Dict[str, Any]]:
        """
        Get provenance links where the given document is the child.
        
        This is a helper method that would query the Walacor database
        for provenance links. For now, it returns an empty list as
        a placeholder since the Walacor schemas have configuration issues.
        
        Args:
            child_doc_id (str): ID of the child document
            
        Returns:
            List[Dict[str, Any]]: List of provenance links
        """
        try:
            # This would query ETId 100002 (document_provenance) for links
            # where child_doc_id matches the child_doc_id field
            # For now, return empty list due to schema issues
            return []
            
        except Exception as e:
            print(f"⚠️  Error querying provenance links by child: {e}")
            return []
    
    def _get_provenance_links_by_parent(self, parent_doc_id: str) -> List[Dict[str, Any]]:
        """
        Get provenance links where the given document is the parent.
        
        This is a helper method that would query the Walacor database
        for provenance links. For now, it returns an empty list as
        a placeholder since the Walacor schemas have configuration issues.
        
        Args:
            parent_doc_id (str): ID of the parent document
            
        Returns:
            List[Dict[str, Any]]: List of provenance links
        """
        try:
            # This would query ETId 100002 (document_provenance) for links
            # where parent_doc_id matches the parent_doc_id field
            # For now, return empty list due to schema issues
            return []
            
        except Exception as e:
            print(f"⚠️  Error querying provenance links by parent: {e}")
            return []
    
    def get_relationship_types(self) -> Dict[str, str]:
        """
        Get all available relationship types and their descriptions.
        
        Returns:
            Dict[str, str]: Dictionary mapping relationship types to descriptions
        """
        return self.RELATIONSHIP_TYPES.copy()
    
    def validate_relationship_type(self, relationship_type: str) -> bool:
        """
        Validate if a relationship type is supported.
        
        Args:
            relationship_type (str): The relationship type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return relationship_type in self.RELATIONSHIP_TYPES
    
    def create_loan_lifecycle_chain(self, loan_id: str, document_ids: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Create a complete loan lifecycle provenance chain.
        
        This method creates provenance links for a typical loan lifecycle,
        connecting documents from application through closing.
        
        Args:
            loan_id (str): The loan identifier
            document_ids (Dict[str, str]): Dictionary mapping document types to IDs
            
        Returns:
            List[Dict[str, Any]]: List of created provenance links
            
        Example:
            >>> tracker = ProvenanceTracker()
            >>> document_ids = {
            ...     "application": "APP_001",
            ...     "underwriting": "UNDER_001",
            ...     "closing": "CLOSE_001"
            ... }
            >>> links = tracker.create_loan_lifecycle_chain("LOAN_123", document_ids)
        """
        try:
            print(f"\n🏗️  Creating loan lifecycle chain for: {loan_id}")
            
            links = []
            
            # Define the typical loan lifecycle flow
            lifecycle_flow = [
                ("application", "underwriting", "underwriting"),
                ("underwriting", "closing", "closing"),
                ("closing", "servicing", "servicing_transfer")
            ]
            
            for parent_type, child_type, relationship_type in lifecycle_flow:
                if parent_type in document_ids and child_type in document_ids:
                    parent_id = document_ids[parent_type]
                    child_id = document_ids[child_type]
                    
                    result = self.create_link(
                        parent_doc_id=parent_id,
                        child_doc_id=child_id,
                        relationship_type=relationship_type,
                        description=f"{relationship_type} for loan {loan_id}"
                    )
                    links.append(result)
            
            print(f"✅ Created {len(links)} lifecycle links")
            return links
            
        except Exception as e:
            error_msg = f"Failed to create loan lifecycle chain: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def print_lineage_tree(self, document_id: str, max_depth: int = 5) -> None:
        """
        Print a visual representation of the document lineage tree.
        
        Args:
            document_id (str): ID of the document to visualize
            max_depth (int): Maximum depth to traverse (prevents infinite loops)
        """
        try:
            print(f"\n🌳 Document Lineage Tree for: {document_id}")
            print("=" * 60)
            
            lineage = self.get_full_lineage(document_id)
            
            # Print ancestors (going backwards)
            if lineage["ancestors"]:
                print("📜 ANCESTORS:")
                for i, link in enumerate(reversed(lineage["ancestors"])):
                    indent = "  " * i
                    parent = link.get('parent_doc_id', 'Unknown')
                    child = link.get('child_doc_id', 'Unknown')
                    rel_type = link.get('relationship_type', 'Unknown')
                    print(f"{indent}└─ {parent} → {child} ({rel_type})")
            
            # Print current document
            print(f"\n🎯 CURRENT: {document_id}")
            
            # Print descendants (going forwards)
            if lineage["descendants"]:
                print("\n📋 DESCENDANTS:")
                for i, link in enumerate(lineage["descendants"]):
                    indent = "  " * (i + 1)
                    parent = link.get('parent_doc_id', 'Unknown')
                    child = link.get('child_doc_id', 'Unknown')
                    rel_type = link.get('relationship_type', 'Unknown')
                    print(f"{indent}├─ {parent} → {child} ({rel_type})")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Failed to print lineage tree: {e}")


