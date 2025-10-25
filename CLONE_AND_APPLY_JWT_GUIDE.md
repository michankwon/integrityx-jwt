# 🚀 Apply JWT to Any GitHub Repository - Complete Guide

This guide shows you how to clone any GitHub repository and add the same JWT digital signature implementation with **5-minute token expiration**.

## 📋 **Step 1: Clone Target Repository**

```bash
# Clone any FastAPI repository you want to add JWT to
git clone https://github.com/username/target-repo.git
cd target-repo

# Create a new branch for JWT implementation
git checkout -b add-jwt-signatures
```

## 🔑 **Step 2: Download JWT Implementation Files**

```bash
# Download JWT service (core implementation)
curl -O https://raw.githubusercontent.com/michankwon/integrityx-jwt/main/backend/src/jwt_service.py

# Download key generation script
curl -O https://raw.githubusercontent.com/michankwon/integrityx-jwt/main/backend/generate_jwt_keys.py

# Download quick setup script
curl -O https://raw.githubusercontent.com/michankwon/integrityx-jwt/main/deploy_jwt.sh
chmod +x deploy_jwt.sh
```

## ⚡ **Step 3: Run Quick Setup**

```bash
# Run the automated setup script
./deploy_jwt.sh
```

This will:
- Add JWT dependencies to requirements.txt
- Generate RSA keys (jwt_private_key.pem, jwt_public_key.pem)
- Create .env.example template
- Update .gitignore for security

## 🕐 **Step 4: Configure 5-Minute Token Expiration**

Create/edit `.env` file:

```env
# JWT Configuration - 5 MINUTE TOKENS
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=your-app-name
JWT_TTL_SECONDS=300
```

**Key Change**: `JWT_TTL_SECONDS=300` (5 minutes = 300 seconds)

## 📁 **Step 5: Install JWT Service**

```bash
# Create src directory if it doesn't exist
mkdir -p src

# Move JWT service to correct location
mv jwt_service.py src/jwt_service.py

# Install dependencies
pip install cryptography PyJWT
```

## 🗄️ **Step 6: Add Database Column**

If the project uses Alembic:

```bash
# Create migration
alembic revision -m "add_jwt_signature_column"
```

Edit the migration file:
```python
def upgrade() -> None:
    op.add_column('your_table_name', sa.Column('signature_jwt', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('your_table_name', 'signature_jwt')
```

Run migration:
```bash
alembic upgrade head
```

## 🔧 **Step 7: Integrate JWT into Main App**

Add to your `main.py` (or equivalent):

```python
from src.jwt_service import initialize_jwt_service, get_jwt_service
import os

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Initialize JWT service with 5-minute expiration
    jwt_private_key = os.getenv('JWT_PRIVATE_KEY_PATH', 'jwt_private_key.pem')
    jwt_public_key = os.getenv('JWT_PUBLIC_KEY_PATH', 'jwt_public_key.pem')
    jwt_issuer = os.getenv('JWT_ISSUER', 'your-app-name')
    jwt_ttl = int(os.getenv('JWT_TTL_SECONDS', '300'))  # 5 minutes
    
    initialize_jwt_service(jwt_private_key, jwt_public_key, jwt_issuer, jwt_ttl)
    print(f"✅ JWT service initialized with {jwt_ttl/60} minute expiration")
```

## 📝 **Step 8: Add JWT Signing to Your Endpoints**

Find your document/data creation endpoints and add JWT signing:

```python
from src.jwt_service import get_jwt_service

@app.post("/api/your-endpoint")  # Replace with your actual endpoint
async def create_document(data: YourDataModel):
    # ... your existing logic ...
    
    # Create JWT signature with 5-minute expiration
    jwt_service = get_jwt_service()
    jwt_token = jwt_service.sign_artifact(document_id, document_data_dict)
    
    # Save JWT to database (adjust table/model names)
    your_record.signature_jwt = jwt_token  # Replace with your model field
    db.commit()
    
    return {
        "id": document_id,
        "signature_jwt": jwt_token,
        "expires_in_minutes": 5,
        # ... other response data
    }
```

## 🔍 **Step 9: Add JWT Verification to Your Endpoints**

Find your verification/retrieval endpoints:

```python
@app.post("/api/verify")  # Replace with your actual endpoint
async def verify_document(request: YourVerifyModel):
    # ... your existing verification logic ...
    
    # Add JWT verification
    jwt_result = {"verified": False, "error": "No JWT signature found"}
    if your_record.signature_jwt:  # Replace with your model field
        jwt_service = get_jwt_service()
        jwt_result = jwt_service.verify_signature(your_record.signature_jwt)
        
        # Check if token expired (5 minutes)
        if not jwt_result['verified'] and 'expired' in jwt_result.get('error', '').lower():
            jwt_result['error'] = "JWT signature expired (5-minute limit exceeded)"
    
    return {
        "is_valid": True,  # your existing validation
        "jwt_signature": jwt_result,
        "token_lifetime_minutes": 5,
        # ... other response data
    }
```

## 🏥 **Step 10: Add JWT to Health Check**

```python
@app.get("/health")
async def health_check():
    services = {}
    
    # ... other service checks ...
    
    # JWT service check
    try:
        jwt_service = get_jwt_service()
        services["jwt"] = {
            "status": "up",
            "details": f"JWT service operational (5-min tokens, issuer: {jwt_service.issuer})",
            "token_lifetime_minutes": 5,
            "error": None
        }
    except Exception as e:
        services["jwt"] = {
            "status": "down",
            "details": None,
            "error": str(e)
        }
    
    return {"services": services}
```

## 🧪 **Step 11: Test JWT Implementation**

```bash
# Start your application
uvicorn main:app --reload --port 8000  # Adjust as needed

# Test document creation (creates JWT)
curl -X POST "http://localhost:8000/api/your-endpoint" \
  -H "Content-Type: application/json" \
  -d '{"your": "data"}'

# Test verification (includes JWT check)
curl -X POST "http://localhost:8000/api/verify" \
  -H "Content-Type: application/json" \
  -d '{"id": "your-document-id"}'

# Test health check
curl -X GET "http://localhost:8000/health"

# Test token expiration (wait 6 minutes and verify again)
```

## ⏰ **Step 12: Test 5-Minute Expiration**

```bash
# Create a document
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/your-endpoint" \
  -H "Content-Type: application/json" \
  -d '{"test": "5-minute-expiration"}')

echo "Document created, waiting 6 minutes to test expiration..."
sleep 360  # Wait 6 minutes

# Verify - should show JWT expired
curl -X POST "http://localhost:8000/api/verify" \
  -H "Content-Type: application/json" \
  -d '{"id": "your-document-id"}'
```

## 🔄 **Step 13: Commit Your Changes**

```bash
# Add all changes
git add .

# Commit JWT implementation
git commit -m "🔐 Add JWT Digital Signatures with 5-minute expiration

✅ Features Added:
- RS256 JWT signatures with 2048-bit RSA keys
- 5-minute token expiration for enhanced security
- Automatic document signing on creation
- JWT verification on document retrieval
- Database integration with signature storage
- Health monitoring with JWT status
- Complete error handling and logging

🔒 Security: Short-lived tokens (5 minutes) for maximum security"

# Push to your fork/branch
git push origin add-jwt-signatures
```

## 🎯 **Key Configuration for 5-Minute Tokens**

**Environment Variable:**
```env
JWT_TTL_SECONDS=300  # 5 minutes = 300 seconds
```

**Service Initialization:**
```python
jwt_ttl = int(os.getenv('JWT_TTL_SECONDS', '300'))  # 5 minutes default
initialize_jwt_service(private_key, public_key, issuer, jwt_ttl)
```

**Benefits of 5-Minute Expiration:**
- ✅ **Enhanced Security**: Tokens expire quickly
- ✅ **Reduced Attack Window**: Stolen tokens are useless after 5 minutes
- ✅ **Perfect for High-Security Applications**: Financial, legal, medical documents
- ✅ **Compliance Ready**: Meets strict security requirements

## 🚨 **Important Notes**

1. **Token Lifetime**: Tokens expire in exactly 5 minutes from creation
2. **Re-signing**: Documents may need re-signing if verification is needed after 5 minutes
3. **Testing**: Use `sleep 360` (6 minutes) to test expiration
4. **Security**: Never commit `.pem` files to git
5. **Backup**: Keep your RSA keys secure and backed up

## 🎉 **You're Done!**

Your cloned repository now has:
- ✅ JWT digital signatures with 5-minute expiration
- ✅ Automatic document signing
- ✅ Cryptographic verification with tamper detection
- ✅ Enhanced security with short-lived tokens
- ✅ Production-ready implementation

**The same JWT functionality from your original implementation, now with ultra-secure 5-minute token expiration!** 🔐⏰
