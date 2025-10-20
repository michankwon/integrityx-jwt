"""
Time Machine Service

This module provides time-travel capabilities for document state management,
allowing users to view and restore document states at any point in history.

Features:
- Document state snapshots
- Historical state viewing
- State restoration capabilities
- Timeline visualization
- Change tracking and auditing
"""

import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class StateChangeType(Enum):
    """Types of state changes that can be tracked."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESTORED = "restored"
    ATTESTED = "attested"
    VERIFIED = "verified"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class DocumentState:
    """Represents a document state at a specific point in time."""
    state_id: str
    document_id: str
    version: int
    timestamp: datetime
    state_data: Dict[str, Any]
    change_type: StateChangeType
    changed_by: str
    change_description: str
    parent_state_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StateSnapshot:
    """A snapshot of document state for time travel."""
    snapshot_id: str
    document_id: str
    timestamp: datetime
    state_data: Dict[str, Any]
    version: int
    created_by: str
    description: str
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TimeMachine:
    """
    Time Machine service for document state management and time travel.
    
    This service provides comprehensive document state tracking, allowing users
    to view document states at any point in time and restore previous states.
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the Time Machine service.
        
        Args:
            db_service: Database service for storing state history
        """
        self.db_service = db_service
        self.state_history = {}  # document_id -> List[DocumentState]
        self.snapshots = {}  # document_id -> List[StateSnapshot]
        self.max_history_size = 1000  # Maximum states to keep per document
        
        logger.info("✅ Time Machine service initialized")
    
    def create_state_snapshot(self, document_id: str, state_data: Dict[str, Any], 
                            created_by: str, description: str = "", 
                            tags: Optional[List[str]] = None) -> StateSnapshot:
        """
        Create a snapshot of the current document state.
        
        Args:
            document_id: ID of the document
            state_data: Current state data
            created_by: User creating the snapshot
            description: Description of the snapshot
            tags: Tags for categorization
            
        Returns:
            Created state snapshot
        """
        try:
            # Get current version
            current_version = self._get_current_version(document_id)
            
            # Create snapshot
            snapshot = StateSnapshot(
                snapshot_id=str(uuid.uuid4()),
                document_id=document_id,
                timestamp=datetime.now(timezone.utc),
                state_data=state_data.copy(),
                version=current_version + 1,
                created_by=created_by,
                description=description,
                tags=tags or []
            )
            
            # Store snapshot
            if document_id not in self.snapshots:
                self.snapshots[document_id] = []
            self.snapshots[document_id].append(snapshot)
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=document_id,
                    event_type="state_snapshot_created",
                    payload_json=json.dumps({
                        "snapshot_id": snapshot.snapshot_id,
                        "version": snapshot.version,
                        "description": snapshot.description,
                        "tags": snapshot.tags,
                        "created_by": created_by
                    }),
                    created_by=created_by
                )
            
            logger.info(f"✅ State snapshot created for document {document_id}: {snapshot.snapshot_id}")
            
        except Exception as e:
            logger.error(f"Failed to create state snapshot: {e}")
            raise
        
        return snapshot
    
    def record_state_change(self, document_id: str, state_data: Dict[str, Any],
                          change_type: StateChangeType, changed_by: str,
                          change_description: str = "", metadata: Dict[str, Any] = None) -> DocumentState:
        """
        Record a state change for a document.
        
        Args:
            document_id: ID of the document
            state_data: New state data
            change_type: Type of change
            changed_by: User making the change
            change_description: Description of the change
            metadata: Additional metadata
            
        Returns:
            Created document state
        """
        try:
            # Get current version and parent state
            current_version = self._get_current_version(document_id)
            parent_state_id = self._get_latest_state_id(document_id)
            
            # Create new state
            state = DocumentState(
                state_id=str(uuid.uuid4()),
                document_id=document_id,
                version=current_version + 1,
                timestamp=datetime.now(timezone.utc),
                state_data=state_data.copy(),
                change_type=change_type,
                changed_by=changed_by,
                change_description=change_description,
                parent_state_id=parent_state_id,
                metadata=metadata or {}
            )
            
            # Store state
            if document_id not in self.state_history:
                self.state_history[document_id] = []
            self.state_history[document_id].append(state)
            
            # Maintain history size limit
            self._maintain_history_size(document_id)
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=document_id,
                    event_type="state_change_recorded",
                    payload_json=json.dumps({
                        "state_id": state.state_id,
                        "version": state.version,
                        "change_type": change_type.value,
                        "change_description": change_description,
                        "parent_state_id": parent_state_id,
                        "metadata": metadata or {}
                    }),
                    created_by=changed_by
                )
            
            logger.info(f"✅ State change recorded for document {document_id}: {state.state_id}")
            
        except Exception as e:
            logger.error(f"Failed to record state change: {e}")
            raise
        
        return state
    
    def get_document_state_at_time(self, document_id: str, target_time: datetime) -> Optional[DocumentState]:
        """
        Get the document state at a specific point in time.
        
        Args:
            document_id: ID of the document
            target_time: Target timestamp
            
        Returns:
            Document state at the specified time, or None if not found
        """
        try:
            if document_id not in self.state_history:
                return None
            
            states = self.state_history[document_id]
            
            # Find the state that was active at the target time
            for state in reversed(states):  # Start from most recent
                if state.timestamp <= target_time:
                    return state
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get document state at time: {e}")
            return None
    
    def get_document_state_by_version(self, document_id: str, version: int) -> Optional[DocumentState]:
        """
        Get the document state by version number.
        
        Args:
            document_id: ID of the document
            version: Version number
            
        Returns:
            Document state for the specified version, or None if not found
        """
        try:
            if document_id not in self.state_history:
                return None
            
            states = self.state_history[document_id]
            
            for state in states:
                if state.version == version:
                    return state
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get document state by version: {e}")
            return None
    
    def get_document_timeline(self, document_id: str, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[DocumentState]:
        """
        Get the timeline of document states within a time range.
        
        Args:
            document_id: ID of the document
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
            
        Returns:
            List of document states in the time range
        """
        try:
            if document_id not in self.state_history:
                return []
            
            states = self.state_history[document_id]
            
            # Filter by time range
            if start_time:
                states = [s for s in states if s.timestamp >= start_time]
            if end_time:
                states = [s for s in states if s.timestamp <= end_time]
            
            # Sort by timestamp
            states.sort(key=lambda x: x.timestamp)
            
            return states
        
        except Exception as e:
            logger.error(f"Failed to get document timeline: {e}")
            return []
    
    def restore_document_state(self, document_id: str, target_state_id: str,
                             restored_by: str, restore_reason: str = "") -> DocumentState:
        """
        Restore a document to a previous state.
        
        Args:
            document_id: ID of the document
            target_state_id: ID of the state to restore to
            restored_by: User performing the restore
            restore_reason: Reason for restoration
            
        Returns:
            New document state after restoration
        """
        try:
            # Find the target state
            target_state = self._find_state_by_id(document_id, target_state_id)
            if not target_state:
                raise ValueError(f"State {target_state_id} not found for document {document_id}")
            
            # Create new state with restored data
            restored_state = DocumentState(
                state_id=str(uuid.uuid4()),
                document_id=document_id,
                version=self._get_current_version(document_id) + 1,
                timestamp=datetime.now(timezone.utc),
                state_data=target_state.state_data.copy(),
                change_type=StateChangeType.RESTORED,
                changed_by=restored_by,
                change_description=f"Restored to state {target_state_id}: {restore_reason}",
                parent_state_id=target_state_id,
                metadata={
                    "restore_reason": restore_reason,
                    "original_state_timestamp": target_state.timestamp.isoformat(),
                    "original_state_version": target_state.version
                }
            )
            
            # Store restored state
            if document_id not in self.state_history:
                self.state_history[document_id] = []
            self.state_history[document_id].append(restored_state)
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=document_id,
                    event_type="document_state_restored",
                    payload_json=json.dumps({
                        "restored_state_id": restored_state.state_id,
                        "target_state_id": target_state_id,
                        "restore_reason": restore_reason,
                        "original_timestamp": target_state.timestamp.isoformat(),
                        "original_version": target_state.version
                    }),
                    created_by=restored_by
                )
            
            logger.info(f"✅ Document {document_id} restored to state {target_state_id}")
            
        except Exception as e:
            logger.error(f"Failed to restore document state: {e}")
            raise
        
        return restored_state
    
    def compare_states(self, state1_id: str, state2_id: str) -> Dict[str, Any]:
        """
        Compare two document states and return differences.
        
        Args:
            state1_id: ID of the first state
            state2_id: ID of the second state
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Find both states
            state1 = self._find_state_by_id_global(state1_id)
            state2 = self._find_state_by_id_global(state2_id)
            
            if not state1 or not state2:
                raise ValueError("One or both states not found")
            
            # Compare state data
            differences = self._deep_compare(state1.state_data, state2.state_data)
            
            comparison = {
                "state1": {
                    "state_id": state1.state_id,
                    "version": state1.version,
                    "timestamp": state1.timestamp.isoformat(),
                    "changed_by": state1.changed_by
                },
                "state2": {
                    "state_id": state2.state_id,
                    "version": state2.version,
                    "timestamp": state2.timestamp.isoformat(),
                    "changed_by": state2.changed_by
                },
                "differences": differences,
                "time_difference": (state2.timestamp - state1.timestamp).total_seconds(),
                "version_difference": state2.version - state1.version
            }
            
            logger.info(f"✅ States compared: {state1_id} vs {state2_id}")
            
        except Exception as e:
            logger.error(f"Failed to compare states: {e}")
            raise
        
        return comparison
    
    def get_state_statistics(self, document_id: str) -> Dict[str, Any]:
        """
        Get statistics about document state history.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary containing state statistics
        """
        try:
            if document_id not in self.state_history:
                return {"error": "Document not found"}
            
            states = self.state_history[document_id]
            
            if not states:
                return {"error": "No state history found"}
            
            # Calculate statistics
            total_states = len(states)
            first_state = min(states, key=lambda x: x.timestamp)
            last_state = max(states, key=lambda x: x.timestamp)
            
            # Count by change type
            change_type_counts = {}
            for state in states:
                change_type = state.change_type.value
                change_type_counts[change_type] = change_type_counts.get(change_type, 0) + 1
            
            # Count by user
            user_counts = {}
            for state in states:
                user = state.changed_by
                user_counts[user] = user_counts.get(user, 0) + 1
            
            # Calculate time span
            time_span = (last_state.timestamp - first_state.timestamp).total_seconds()
            
            statistics = {
                "document_id": document_id,
                "total_states": total_states,
                "first_state": {
                    "state_id": first_state.state_id,
                    "version": first_state.version,
                    "timestamp": first_state.timestamp.isoformat(),
                    "changed_by": first_state.changed_by
                },
                "last_state": {
                    "state_id": last_state.state_id,
                    "version": last_state.version,
                    "timestamp": last_state.timestamp.isoformat(),
                    "changed_by": last_state.changed_by
                },
                "time_span_seconds": time_span,
                "change_type_distribution": change_type_counts,
                "user_activity": user_counts,
                "snapshots_count": len(self.snapshots.get(document_id, [])),
                "average_changes_per_day": total_states / max(time_span / 86400, 1)  # 86400 seconds in a day
            }
            
            logger.info(f"✅ State statistics generated for document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to get state statistics: {e}")
            statistics = {"error": str(e)}
        
        return statistics
    
    def get_snapshots(self, document_id: str, tags: List[str] = None) -> List[StateSnapshot]:
        """
        Get snapshots for a document, optionally filtered by tags.
        
        Args:
            document_id: ID of the document
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching snapshots
        """
        try:
            if document_id not in self.snapshots:
                return []
            
            snapshots = self.snapshots[document_id]
            
            # Filter by tags if provided
            if tags:
                filtered_snapshots = []
                for snapshot in snapshots:
                    if any(tag in snapshot.tags for tag in tags):
                        filtered_snapshots.append(snapshot)
                snapshots = filtered_snapshots
            
            # Sort by timestamp (most recent first)
            snapshots.sort(key=lambda x: x.timestamp, reverse=True)
            
            return snapshots
        
        except Exception as e:
            logger.error(f"Failed to get snapshots: {e}")
            return []
    
    def delete_snapshot(self, document_id: str, snapshot_id: str, deleted_by: str) -> bool:
        """
        Delete a snapshot.
        
        Args:
            document_id: ID of the document
            snapshot_id: ID of the snapshot to delete
            deleted_by: User deleting the snapshot
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if document_id not in self.snapshots:
                return False
            
            snapshots = self.snapshots[document_id]
            
            # Find and remove the snapshot
            for i, snapshot in enumerate(snapshots):
                if snapshot.snapshot_id == snapshot_id:
                    del snapshots[i]
                    
                    # Store deletion event
                    if self.db_service:
                        self.db_service.insert_event(
                            artifact_id=document_id,
                            event_type="snapshot_deleted",
                            payload_json=json.dumps({
                                "snapshot_id": snapshot_id,
                                "deleted_by": deleted_by
                            }),
                            created_by=deleted_by
                        )
                    
                    logger.info(f"✅ Snapshot {snapshot_id} deleted for document {document_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to delete snapshot: {e}")
            return False
    
    def _get_current_version(self, document_id: str) -> int:
        """Get the current version number for a document."""
        if document_id not in self.state_history or not self.state_history[document_id]:
            return 0
        
        return max(state.version for state in self.state_history[document_id])
    
    def _get_latest_state_id(self, document_id: str) -> Optional[str]:
        """Get the ID of the latest state for a document."""
        if document_id not in self.state_history or not self.state_history[document_id]:
            return None
        
        latest_state = max(self.state_history[document_id], key=lambda x: x.timestamp)
        return latest_state.state_id
    
    def _find_state_by_id(self, document_id: str, state_id: str) -> Optional[DocumentState]:
        """Find a state by ID within a specific document."""
        if document_id not in self.state_history:
            return None
        
        for state in self.state_history[document_id]:
            if state.state_id == state_id:
                return state
        
        return None
    
    def _find_state_by_id_global(self, state_id: str) -> Optional[DocumentState]:
        """Find a state by ID across all documents."""
        for document_id, states in self.state_history.items():
            for state in states:
                if state.state_id == state_id:
                    return state
        
        return None
    
    def _maintain_history_size(self, document_id: str):
        """Maintain the maximum history size for a document."""
        if document_id not in self.state_history:
            return
        
        states = self.state_history[document_id]
        
        if len(states) > self.max_history_size:
            # Keep only the most recent states
            states.sort(key=lambda x: x.timestamp, reverse=True)
            self.state_history[document_id] = states[:self.max_history_size]
    
    def _deep_compare(self, obj1: Any, obj2: Any, path: str = "") -> List[Dict[str, Any]]:
        """Deep compare two objects and return differences."""
        differences = []
        
        try:
            if type(obj1) != type(obj2):
                differences.append({
                    "path": path,
                    "type": "type_change",
                    "old_value": str(type(obj1)),
                    "new_value": str(type(obj2))
                })
                return differences
            
            if isinstance(obj1, dict):
                all_keys = set(obj1.keys()) | set(obj2.keys())
                for key in all_keys:
                    new_path = f"{path}.{key}" if path else key
                    
                    if key not in obj1:
                        differences.append({
                            "path": new_path,
                            "type": "added",
                            "new_value": obj2[key]
                        })
                    elif key not in obj2:
                        differences.append({
                            "path": new_path,
                            "type": "removed",
                            "old_value": obj1[key]
                        })
                    else:
                        differences.extend(self._deep_compare(obj1[key], obj2[key], new_path))
            
            elif isinstance(obj1, list):
                max_len = max(len(obj1), len(obj2))
                for i in range(max_len):
                    new_path = f"{path}[{i}]"
                    
                    if i >= len(obj1):
                        differences.append({
                            "path": new_path,
                            "type": "added",
                            "new_value": obj2[i]
                        })
                    elif i >= len(obj2):
                        differences.append({
                            "path": new_path,
                            "type": "removed",
                            "old_value": obj1[i]
                        })
                    else:
                        differences.extend(self._deep_compare(obj1[i], obj2[i], new_path))
            
            else:
                if obj1 != obj2:
                    differences.append({
                        "path": path,
                        "type": "changed",
                        "old_value": obj1,
                        "new_value": obj2
                    })
        
        except Exception as e:
            logger.error(f"Error in deep compare: {e}")
            differences.append({
                "path": path,
                "type": "error",
                "error": str(e)
            })
        
        return differences