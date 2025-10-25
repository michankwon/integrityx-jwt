# 🔐 JWT Digital Signature Implementation Guide

This guide shows you **exactly how to replicate** the JWT digital signature implementation on any project.

## 🎯 **What You'll Get**

- Complete JWT digital signature system using RS256 algorithm
- Automatic document signing on all seal operations
- Database integration with signature storage
- Frontend integration with seamless user experience
- Production-ready error handling and logging

## 📋 **Prerequisites**

- Python 3.8+ project with FastAPI
- SQLAlchemy ORM setup
- Alembic for database migrations
- Basic project structure

## 🚀 **Step-by-Step Implementation**

### **Step 1: Install Dependencies**

Add to your `requirements.txt`:
```txt
cryptography>=41.0.0
PyJWT>=2.8.0
```

Install:
```bash
pip install cryptography PyJWT
```

### **Step 2: Generate JWT Keys**

Create `generate_jwt_keys.py`:
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_jwt_keys():
    """Generate RSA key pair for JWT signing"""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Write keys to files
    with open('jwt_private_key.pem', 'wb') as f:
        f.write(private_pem)
    
    with open('jwt_public_key.pem', 'wb') as f:
        f.write(public_pem)
    
    print("✅ JWT keys generated successfully!")
    print("📁 Files created: jwt_private_key.pem, jwt_public_key.pem")

if __name__ == "__main__":
    generate_jwt_keys()
```

Run it:
```bash
python generate_jwt_keys.py
```

### **Step 3: Create JWT Service**

Create `src/jwt_service.py`:
```python
import jwt
import json
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives import serialization
from typing import Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class JWTService:
    def __init__(self, private_key_path: str, public_key_path: str, issuer: str, ttl_seconds: int = 3600):
        self.issuer = issuer
        self.ttl_seconds = ttl_seconds
        
        # Load keys
        self.private_key = self._load_private_key(private_key_path)
        self.public_key = self._load_public_key(public_key_path)
        
        logger.info(f"✅ JWT service initialized with issuer: {issuer}")
    
    def sign_artifact(self, artifact_id: str, payload_data: dict) -> str:
        """Create JWT signature for an artifact"""
        try:
            now = datetime.now(timezone.utc)
            
            # Create canonical JSON payload
            canonical_payload = json.dumps(payload_data, sort_keys=True, separators=(',', ':'))
            
            # JWT claims
            claims = {
                'iss': self.issuer,
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(seconds=self.ttl_seconds)).timestamp()),
                'artifact_id': artifact_id,
                'payload': canonical_payload
            }
            
            # Sign with RS256
            token = jwt.encode(claims, self.private_key, algorithm='RS256')
            
            logger.info(f"✅ JWT signature created for artifact {artifact_id[:8]}...")
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to sign artifact {artifact_id}: {str(e)}")
            raise
    
    def verify_signature(self, token: str) -> Dict[str, Any]:
        """Verify JWT signature and return claims"""
        try:
            # Decode and verify
            claims = jwt.decode(token, self.public_key, algorithms=['RS256'])
            
            logger.info(f"✅ JWT signature verified for artifact {claims.get('artifact_id', 'unknown')[:8]}...")
            
            return {
                'verified': True,
                'claims': {
                    'artifact_id': claims.get('artifact_id'),
                    'issued_at': datetime.fromtimestamp(claims.get('iat', 0), timezone.utc).isoformat(),
                    'expires_at': datetime.fromtimestamp(claims.get('exp', 0), timezone.utc).isoformat()
                },
                'error': None
            }
            
        except jwt.ExpiredSignatureError:
            return {'verified': False, 'error': 'JWT signature has expired', 'claims': None}
        except jwt.InvalidTokenError as e:
            return {'verified': False, 'error': f'Invalid JWT signature: {str(e)}', 'claims': None}
        except Exception as e:
            logger.error(f"❌ JWT verification error: {str(e)}")
            return {'verified': False, 'error': f'Verification failed: {str(e)}', 'claims': None}
    
    def _load_private_key(self, path: str):
        """Load private key from file"""
        with open(path, 'rb') as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    
    def _load_public_key(self, path: str):
        """Load public key from file"""  
        with open(path, 'rb') as f:
            return serialization.load_pem_public_key(f.read())

# Global service instance
jwt_service: Optional[JWTService] = None

def get_jwt_service() -> JWTService:
    """Get JWT service instance"""
    global jwt_service
    if jwt_service is None:
        raise RuntimeError("JWT service not initialized")
    return jwt_service

def initialize_jwt_service(private_key_path: str, public_key_path: str, issuer: str, ttl_seconds: int = 3600):
    """Initialize JWT service"""
    global jwt_service
    jwt_service = JWTService(private_key_path, public_key_path, issuer, ttl_seconds)
```

### **Step 4: Add Database Column**

Create Alembic migration:
```bash
alembic revision -m "add_jwt_signature_to_artifacts"
```

Edit the migration file:
```python
def upgrade() -> None:
    op.add_column('artifacts', sa.Column('signature_jwt', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('artifacts', 'signature_jwt')
```

Run migration:
```bash
alembic upgrade head
```

### **Step 5: Update Your Main Application**

In your `main.py`:
```python
from src.jwt_service import initialize_jwt_service, get_jwt_service
import os

@app.on_event("startup")
async def startup_event():
    # ... other initialization ...
    
    # Initialize JWT service
    jwt_private_key = os.getenv('JWT_PRIVATE_KEY_PATH', 'jwt_private_key.pem')
    jwt_public_key = os.getenv('JWT_PUBLIC_KEY_PATH', 'jwt_public_key.pem') 
    jwt_issuer = os.getenv('JWT_ISSUER', 'your-app-name')
    jwt_ttl = int(os.getenv('JWT_TTL_SECONDS', '3600'))
    
    initialize_jwt_service(jwt_private_key, jwt_public_key, jwt_issuer, jwt_ttl)
    logger.info(f"✅ JWT service initialized with issuer: {jwt_issuer}")
```

### **Step 6: Integrate JWT Signing**

In your document sealing endpoint:
```python
from src.jwt_service import get_jwt_service

@app.post("/api/your-seal-endpoint")
async def seal_document(data: YourDataModel):
    # ... your existing sealing logic ...
    
    # Create JWT signature
    jwt_service = get_jwt_service()
    jwt_token = jwt_service.sign_artifact(artifact_id, document_data)
    
    # Save JWT to database
    artifact.signature_jwt = jwt_token
    db.commit()
    
    return {
        "artifact_id": artifact_id,
        "signature_jwt": jwt_token,
        # ... other response data
    }
```

### **Step 7: Add Verification**

In your verification endpoint:
```python
@app.post("/api/verify")
async def verify_document(request: VerifyRequest):
    # ... your existing verification logic ...
    
    # Verify JWT if present
    jwt_result = {"verified": False, "error": "No JWT signature found"}
    if artifact.signature_jwt:
        jwt_service = get_jwt_service()
        jwt_result = jwt_service.verify_signature(artifact.signature_jwt)
    
    return {
        "is_valid": True,  # your existing validation
        "details": {
            # ... other details
            "jwt_signature": jwt_result
        }
    }
```

### **Step 8: Environment Configuration**

Add to your `.env`:
```env
# JWT Digital Signature Configuration
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=your-app-name
JWT_TTL_SECONDS=3600
```

### **Step 9: Health Check Integration**

Add JWT status to health endpoint:
```python
@app.get("/api/health")
async def health_check():
    services = {}
    
    # ... other service checks ...
    
    # JWT service check
    try:
        jwt_service = get_jwt_service()
        services["jwt"] = {
            "status": "up",
            "details": f"JWT service operational (issuer: {jwt_service.issuer})",
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

## 🧪 **Testing**

Create `tests/test_jwt_service.py`:
```python
import pytest
from src.jwt_service import JWTService

def test_jwt_signing_and_verification():
    jwt_service = JWTService(
        'jwt_private_key.pem',
        'jwt_public_key.pem', 
        'test-issuer'
    )
    
    # Test data
    artifact_id = "test-artifact-123"
    payload = {"test": "data", "number": 42}
    
    # Sign
    token = jwt_service.sign_artifact(artifact_id, payload)
    assert token is not None
    
    # Verify
    result = jwt_service.verify_signature(token)
    assert result['verified'] is True
    assert result['claims']['artifact_id'] == artifact_id
```

## 🎯 **Usage Examples**

After implementation, every document seal will automatically:
1. Create JWT signature
2. Store in database
3. Return in API response
4. Verify on subsequent requests

```bash
# Seal document (creates JWT automatically)
curl -X POST /api/your-seal-endpoint -d '{"data": "your document"}'

# Verify document (includes JWT verification)
curl -X POST /api/verify -d '{"etid": 12345, "hash": "abc..."}'
```

## 🎉 **You're Done!**

Your project now has:
- ✅ Automatic JWT signing on all documents
- ✅ Cryptographic verification with tamper detection  
- ✅ Database integration and persistence
- ✅ Production-ready error handling
- ✅ Complete API integration

**The same JWT implementation we built is now ready in your project!** 🔐🚀
