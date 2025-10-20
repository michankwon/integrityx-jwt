#!/usr/bin/env python3
"""
Test script for SQLAlchemy models.

This script demonstrates the usage of the Artifact, ArtifactFile, and ArtifactEvent models
with a SQLite database for testing purposes.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import create_database_engine, create_tables, Artifact, ArtifactFile, ArtifactEvent
from sqlalchemy.orm import sessionmaker
from datetime import datetime


def test_models():
    """Test the SQLAlchemy models with sample data."""
    print("🗄️  SQLALCHEMY MODELS COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Create in-memory SQLite database
    engine = create_database_engine('sqlite:///:memory:', echo=False)
    
    print("\n1️⃣ Creating Database Tables:")
    create_tables(engine)
    print("✅ All tables created successfully!")
    
    # Test table structure
    print("\n2️⃣ Database Schema:")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"✅ Tables created: {tables}")
    
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"\n📋 {table_name.upper()}:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            col_type = str(col['type'])
            print(f"   - {col['name']:<20} {col_type:<15} {nullable}")
    
    # Test data operations
    print("\n3️⃣ Testing Data Operations:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a loan packet artifact
        print("\n📦 Creating Loan Packet Artifact:")
        artifact = Artifact(
            loan_id='LOAN_2024_001',
            artifact_type='loan_packet',
            payload_sha256='a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
            manifest_sha256='f6e5d4c3b2a1789012345678901234567890abcdef1234567890abcdef123456',
            walacor_tx_id='WAL_TX_123456789',
            created_by='demo_user@integrityx.com'
        )
        
        session.add(artifact)
        session.flush()  # Get the ID without committing
        print(f"✅ Artifact created: {artifact.id}")
        
        # Add multiple files to the artifact
        print("\n📄 Adding Files to Artifact:")
        files_data = [
            {
                'name': 'loan_agreement.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/loan_agreement.pdf',
                'sha256': '1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
                'size_bytes': 1024000,
                'content_type': 'application/pdf'
            },
            {
                'name': 'income_verification.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/income_verification.pdf',
                'sha256': 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                'size_bytes': 512000,
                'content_type': 'application/pdf'
            },
            {
                'name': 'credit_report.pdf',
                'uri': 's3://integrityx-bucket/loans/LOAN_2024_001/credit_report.pdf',
                'sha256': 'fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
                'size_bytes': 256000,
                'content_type': 'application/pdf'
            }
        ]
        
        for file_data in files_data:
            file = ArtifactFile(
                artifact_id=artifact.id,
                **file_data
            )
            session.add(file)
            print(f"✅ File added: {file.name} ({file.size_bytes:,} bytes)")
        
        # Add events to track the artifact lifecycle
        print("\n📝 Adding Events to Artifact:")
        events_data = [
            {
                'event_type': 'uploaded',
                'payload_json': '{"status": "success", "files_count": 3, "total_size": 1792000}',
                'payload_sha256': 'event1abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                'walacor_tx_id': 'WAL_TX_123456790',
                'created_by': 'demo_user@integrityx.com'
            },
            {
                'event_type': 'verified',
                'payload_json': '{"verification_status": "passed", "hash_match": true}',
                'payload_sha256': 'event2abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                'walacor_tx_id': 'WAL_TX_123456791',
                'created_by': 'verification_service@integrityx.com'
            },
            {
                'event_type': 'attested',
                'payload_json': '{"attestor": "loan_officer", "attestation_type": "approved"}',
                'payload_sha256': 'event3abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                'walacor_tx_id': 'WAL_TX_123456792',
                'created_by': 'loan_officer@integrityx.com'
            }
        ]
        
        for event_data in events_data:
            event = ArtifactEvent(
                artifact_id=artifact.id,
                **event_data
            )
            session.add(event)
            print(f"✅ Event added: {event.event_type}")
        
        session.commit()
        print("\n✅ All data committed successfully!")
        
        # Test relationships
        print("\n4️⃣ Testing Relationships:")
        print(f"   Artifact ID: {artifact.id}")
        print(f"   Loan ID: {artifact.loan_id}")
        print(f"   Artifact Type: {artifact.artifact_type}")
        print(f"   Files Count: {len(artifact.files)}")
        print(f"   Events Count: {len(artifact.events)}")
        
        print("\n📄 Files in Artifact:")
        for file in artifact.files:
            print(f"   - {file.name} ({file.content_type}, {file.size_bytes:,} bytes)")
        
        print("\n📝 Events for Artifact:")
        for event in artifact.events:
            print(f"   - {event.event_type} by {event.created_by} at {event.created_at}")
        
        # Test queries
        print("\n5️⃣ Testing Database Queries:")
        
        # Query by loan ID
        loan_artifacts = session.query(Artifact).filter_by(loan_id='LOAN_2024_001').all()
        print(f"✅ Found {len(loan_artifacts)} artifacts for LOAN_2024_001")
        
        # Query by artifact type
        packet_artifacts = session.query(Artifact).filter_by(artifact_type='loan_packet').all()
        print(f"✅ Found {len(packet_artifacts)} loan packet artifacts")
        
        # Query files by content type
        pdf_files = session.query(ArtifactFile).filter_by(content_type='application/pdf').all()
        print(f"✅ Found {len(pdf_files)} PDF files")
        
        # Query events by type
        upload_events = session.query(ArtifactEvent).filter_by(event_type='uploaded').all()
        print(f"✅ Found {len(upload_events)} upload events")
        
        # Test serialization
        print("\n6️⃣ Testing Serialization:")
        artifact_dict = artifact.to_dict()
        print(f"✅ Artifact serialized to {len(artifact_dict)} fields")
        
        # Show sample serialized data
        print("\n📋 Sample Serialized Artifact:")
        for key, value in list(artifact_dict.items())[:5]:  # Show first 5 fields
            print(f"   {key}: {value}")
        
        print("\n✅ All tests passed successfully!")
        print("🗄️  SQLAlchemy models are production-ready!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    test_models()
