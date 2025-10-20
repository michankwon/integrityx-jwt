#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Walacor Financial Integrity Platform

This script helps set up PostgreSQL database for the Walacor platform.
It can create the database, user, and run migrations.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description):
    """Run a shell command and return the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True, result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False, str(e)

def check_postgresql_installed():
    """Check if PostgreSQL is installed and running."""
    print("🔍 Checking PostgreSQL installation...")
    
    # Check if psql command exists
    success, output = run_command("which psql", "Checking psql command")
    if not success:
        print("❌ PostgreSQL client (psql) not found. Please install PostgreSQL.")
        return False
    
    # Check if PostgreSQL service is running
    success, output = run_command("pg_isready", "Checking PostgreSQL service")
    if not success:
        print("❌ PostgreSQL service is not running. Please start PostgreSQL.")
        return False
    
    print("✅ PostgreSQL is installed and running")
    return True

def create_database_and_user():
    """Create database and user for the application."""
    print("🔧 Setting up database and user...")
    
    # Database configuration
    db_name = "walacor_integrity"
    db_user = "walacor_user"
    db_password = "walacor_password"
    db_host = "localhost"
    db_port = "5432"
    
    try:
        # Connect to PostgreSQL as superuser
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user="postgres",  # Default superuser
            password=os.getenv("POSTGRES_PASSWORD", "postgres")  # You may need to set this
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                    CREATE ROLE {db_user} WITH LOGIN PASSWORD '{db_password}';
                END IF;
            END
            $$;
        """)
        
        # Create database if not exists
        cursor.execute(f"""
            SELECT 1 FROM pg_database WHERE datname = '{db_name}'
        """)
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"ℹ️ Database '{db_name}' already exists")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user}")
        
        cursor.close()
        conn.close()
        
        print("✅ Database and user setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_connection():
    """Test connection to the new database."""
    print("🔍 Testing database connection...")
    
    try:
        # Test connection with new credentials
        engine = create_engine("postgresql://walacor_user:walacor_password@localhost:5432/walacor_integrity")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful! PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_env_file():
    """Create .env file with PostgreSQL configuration."""
    print("📝 Creating .env file with PostgreSQL configuration...")
    
    env_content = """# =============================================================================
# POSTGRESQL DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql://walacor_user:walacor_password@localhost:5432/walacor_integrity

# =============================================================================
# WALACOR SERVICE CONFIGURATION
# =============================================================================
WALACOR_HOST=13.220.225.175
WALACOR_USERNAME=Admin
WALACOR_PASSWORD=Th!51s1T@gMu

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL=INFO

# =============================================================================
# DOCUMENT PROCESSING CONFIGURATION
# =============================================================================
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,doc,xlsx,xls,txt,jpg,png,tiff,json,xml

# =============================================================================
# AI/ML CONFIGURATION
# =============================================================================
ENABLE_OCR=true
ENABLE_DOCUMENT_CLASSIFICATION=true
ENABLE_AUTO_EXTRACTION=true
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created with PostgreSQL configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def install_dependencies():
    """Install PostgreSQL dependencies."""
    print("📦 Installing PostgreSQL dependencies...")
    
    dependencies = [
        "psycopg2-binary==2.9.9",
        "sqlalchemy[postgresql]==2.0.23",
        "alembic==1.13.1"
    ]
    
    for dep in dependencies:
        success, output = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            print(f"⚠️ Warning: Failed to install {dep}")
    
    print("✅ Dependencies installation completed")

def main():
    """Main setup function."""
    print("🚀 PostgreSQL Setup for Walacor Financial Integrity Platform")
    print("=" * 60)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\n❌ Setup failed: PostgreSQL not properly installed")
        print("\n📋 To install PostgreSQL:")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        print("   CentOS: sudo yum install postgresql-server postgresql-contrib")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create database and user
    if not create_database_and_user():
        print("\n❌ Setup failed: Could not create database and user")
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print("\n❌ Setup failed: Could not connect to database")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("\n⚠️ Warning: Could not create .env file")
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Start the backend: python main.py")
    print("   2. The application will automatically create tables")
    print("   3. Test the API endpoints")
    
    print("\n🔧 Database connection details:")
    print("   Host: localhost")
    print("   Port: 5432")
    print("   Database: walacor_integrity")
    print("   User: walacor_user")
    print("   Password: walacor_password")

if __name__ == "__main__":
    main()
