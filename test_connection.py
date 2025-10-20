"""
Test connection to Walacor instance
Run this FIRST to verify your setup works
"""
from walacor_sdk import WalacorService
from dotenv import load_dotenv
import os

def test_walacor_connection():
    """Test connection to Walacor instance"""
    print("=" * 50)
    print("TESTING WALACOR CONNECTION")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env
    host = os.getenv('WALACOR_HOST')
    username = os.getenv('WALACOR_USERNAME')
    password = os.getenv('WALACOR_PASSWORD')
    
    print(f"\n📡 Connecting to: {host}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    
    try:
        # Initialize Walacor service
        wal = WalacorService(
            server=f"http://{host}/api",
            username=username,
            password=password
        )
        
        print("\n✅ Connected to Walacor successfully!")
        
        # Test basic operations
        print("\n🔍 Testing schema operations...")
        schemas = wal.schema.get_list_with_latest_version()
        print(f"✅ Found {len(schemas)} existing schemas")
        
        # Print schema details
        if schemas:
            print("\n📋 Existing Schemas:")
            for schema in schemas[:5]:  # Show first 5
                print(f"   - ETId: {schema.ETId}, Table: {schema.TableName}")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nYou're ready to start building! 🚀")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ CONNECTION FAILED!")
        print("=" * 50)
        print(f"\nError: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check WALACOR_HOST in .env (should be EC2 address)")
        print("2. Verify username and password are correct")
        print("3. Ensure EC2 instance is running")
        print("4. Check security group allows your IP")
        print("5. Verify /api endpoint is accessible")
        
        return False

if __name__ == "__main__":
    test_walacor_connection()