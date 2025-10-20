#!/usr/bin/env python
"""
Schema Initialization Script for IntegrityX Financial Document System

This script initializes all required Walacor schemas for the financial document
integrity system. It creates the four core schemas needed for document tracking,
provenance, attestations, and audit logging.

Usage:
    python scripts/initialize_schemas.py

Requirements:
    - .env file with Walacor credentials
    - walacor-python-sdk installed
    - Active connection to Walacor instance

Schemas Created:
    1. loan_documents (ETId: 100001) - Document metadata and hashes
    2. document_provenance (ETId: 100002) - Document relationships
    3. attestations (ETId: 100003) - Document attestations
    4. audit_logs (ETId: 100004) - Audit trail
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    from walacor_sdk import WalacorService
    from schemas import LoanSchemas
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure walacor-python-sdk is installed and src/schemas.py exists")
    sys.exit(1)


def load_environment():
    """
    Load environment variables from .env file.
    
    Returns:
        tuple: (host, username, password) or (None, None, None) if failed
    """
    try:
        # Load .env file from project root
        env_path = project_root / ".env"
        if not env_path.exists():
            print(f"❌ .env file not found at: {env_path}")
            return None, None, None
        
        load_dotenv(env_path)
        
        host = os.getenv('WALACOR_HOST')
        username = os.getenv('WALACOR_USERNAME')
        password = os.getenv('WALACOR_PASSWORD')
        
        if not all([host, username, password]):
            print("❌ Missing required environment variables:")
            print(f"   WALACOR_HOST: {'✓' if host else '✗'}")
            print(f"   WALACOR_USERNAME: {'✓' if username else '✗'}")
            print(f"   WALACOR_PASSWORD: {'✓' if password else '✗'}")
            return None, None, None
        
        print("✅ Environment variables loaded successfully")
        print(f"   Host: {host}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        
        return host, username, password
        
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return None, None, None


def initialize_walacor_service(host, username, password):
    """
    Initialize Walacor service with credentials.
    
    Args:
        host (str): Walacor host address
        username (str): Walacor username
        password (str): Walacor password
        
    Returns:
        WalacorService or None if failed
    """
    try:
        print(f"\n📡 Connecting to Walacor at: {host}")
        
        wal = WalacorService(
            server=f"http://{host}/api",
            username=username,
            password=password
        )
        
        # Test connection by getting schema list
        schemas = wal.schema.get_list_with_latest_version()
        print("✅ Connected to Walacor successfully!")
        print(f"   Found {len(schemas)} existing schemas")
        
        return wal
        
    except Exception as e:
        print(f"❌ Failed to connect to Walacor: {e}")
        return None


def create_schema_with_error_handling(wal, schema_name, create_method):
    """
    Create a schema with comprehensive error handling.
    
    Args:
        wal (WalacorService): Walacor service instance
        schema_name (str): Name of the schema for logging
        create_method (callable): Method to create the schema
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n🔧 Creating {schema_name} schema...")
        create_method(wal)
        print(f"✅ {schema_name} schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create {schema_name} schema: {e}")
        
        # Provide specific error guidance
        if "already exists" in str(e).lower():
            print(f"   ℹ️  {schema_name} schema may already exist")
        elif "permission" in str(e).lower():
            print("   ℹ️  Check user permissions for schema creation")
        elif "connection" in str(e).lower():
            print("   ℹ️  Check network connection to Walacor")
        
        return False


def main():
    """
    Main function to initialize all schemas.
    """
    print("=" * 70)
    print("INTEGRITYX SCHEMA INITIALIZATION")
    print("=" * 70)
    print("Initializing Walacor schemas for financial document integrity system")
    print()
    
    # Step 1: Load environment variables
    print("📋 Step 1: Loading environment variables...")
    host, username, password = load_environment()
    if not all([host, username, password]):
        print("\n❌ Cannot proceed without valid environment variables")
        sys.exit(1)
    
    # Step 2: Initialize Walacor service
    print("\n📋 Step 2: Connecting to Walacor...")
    wal = initialize_walacor_service(host, username, password)
    if not wal:
        print("\n❌ Cannot proceed without Walacor connection")
        sys.exit(1)
    
    # Step 3: Create schemas
    print("\n📋 Step 3: Creating schemas...")
    
    schema_results = {}
    
    # Create loan_documents schema
    schema_results['loan_documents'] = create_schema_with_error_handling(
        wal, "loan_documents", LoanSchemas.create_loan_document_schema
    )
    
    # Create document_provenance schema
    schema_results['document_provenance'] = create_schema_with_error_handling(
        wal, "document_provenance", LoanSchemas.create_provenance_schema
    )
    
    # Create attestations schema
    schema_results['attestations'] = create_schema_with_error_handling(
        wal, "attestations", LoanSchemas.create_attestation_schema
    )
    
    # Create audit_logs schema
    schema_results['audit_logs'] = create_schema_with_error_handling(
        wal, "audit_logs", LoanSchemas.create_audit_log_schema
    )
    
    # Step 4: Summary
    print("\n" + "=" * 70)
    print("SCHEMA INITIALIZATION SUMMARY")
    print("=" * 70)
    
    successful_schemas = sum(1 for success in schema_results.values() if success)
    total_schemas = len(schema_results)
    
    print(f"Total schemas: {total_schemas}")
    print(f"Successful: {successful_schemas}")
    print(f"Failed: {total_schemas - successful_schemas}")
    print()
    
    for schema_name, success in schema_results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {schema_name:<20} {status}")
    
    print()
    
    if successful_schemas == total_schemas:
        print("🎉 All schemas created successfully!")
        print("Your IntegrityX system is ready to use.")
        sys.exit(0)
    elif successful_schemas > 0:
        print("⚠️  Some schemas were created successfully.")
        print("Check the errors above and retry failed schemas if needed.")
        sys.exit(1)
    else:
        print("❌ No schemas were created successfully.")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Schema initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
