"""
Backend models package for Walacor Financial Integrity Platform.

This package contains SQLAlchemy models for managing artifacts, files, and events
in the financial document integrity system.
"""

from .models import (
    Base,
    Artifact,
    ArtifactFile,
    ArtifactEvent,
    create_database_engine,
    create_tables,
    drop_tables
)

__all__ = [
    'Base',
    'Artifact',
    'ArtifactFile', 
    'ArtifactEvent',
    'create_database_engine',
    'create_tables',
    'drop_tables'
]


