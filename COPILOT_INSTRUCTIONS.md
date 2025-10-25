# 🚀 COPY-PASTE JWT IMPLEMENTATION FOR COPILOT

**Instructions for GitHub Copilot:** Please help me implement JWT digital signatures with 5-minute token expiration on this repository. Follow these exact steps:

## Step 1: Setup Dependencies
```bash
# Add to requirements.txt
echo "cryptography>=41.0.0" >> requirements.txt
echo "PyJWT>=2.8.0" >> requirements.txt
pip install cryptography PyJWT
```

## Step 2: Generate JWT Keys
Create `generate_jwt_keys.py`:
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_jwt_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open('jwt_private_key.pem', 'wb') as f: f.write(private_pem)
    with open('jwt_public_key.pem', 'wb') as f: f.write(public_pem)
    print("✅ JWT keys generated!")

if __name__ == "__main__": generate_jwt_keys()
```

Run: `python generate_jwt_keys.py`

## Step 3: Create JWT Service
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
    def __init__(self, private_key_path: str, public_key_path: str, issuer: str, ttl_seconds: int = 300):
        self.issuer = issuer
        self.ttl_seconds = ttl_seconds
        self.private_key = self._load_private_key(private_key_path)
        self.public_key = self._load_public_key(public_key_path)
        logger.info(f"✅ JWT service initialized with {ttl_seconds/60} minute expiration")
    
    def sign_artifact(self, artifact_id: str, payload_data: dict) -> str:
        try:
            now = datetime.now(timezone.utc)
            canonical_payload = json.dumps(payload_data, sort_keys=True, separators=(',', ':'))
            
            claims = {
                'iss': self.issuer,
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(seconds=self.ttl_seconds)).timestamp()),
                'artifact_id': artifact_id,
                'payload': canonical_payload
            }
            
            token = jwt.encode(claims, self.private_key, algorithm='RS256')
            logger.info(f"✅ JWT signature created for {artifact_id[:8]}... (expires in {self.ttl_seconds/60} min)")
            return token
        except Exception as e:
            logger.error(f"❌ Failed to sign artifact {artifact_id}: {str(e)}")
            raise
    
    def verify_signature(self, token: str) -> Dict[str, Any]:
        try:
            claims = jwt.decode(token, self.public_key, algorithms=['RS256'])
            logger.info(f"✅ JWT signature verified for {claims.get('artifact_id', 'unknown')[:8]}...")
            
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
            return {'verified': False, 'error': 'JWT signature expired (5-minute limit)', 'claims': None}
        except jwt.InvalidTokenError as e:
            return {'verified': False, 'error': f'Invalid JWT: {str(e)}', 'claims': None}
        except Exception as e:
            return {'verified': False, 'error': f'Verification failed: {str(e)}', 'claims': None}
    
    def _load_private_key(self, path: str):
        with open(path, 'rb') as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    
    def _load_public_key(self, path: str):
        with open(path, 'rb') as f:
            return serialization.load_pem_public_key(f.read())

jwt_service: Optional[JWTService] = None

def get_jwt_service() -> JWTService:
    global jwt_service
    if jwt_service is None:
        raise RuntimeError("JWT service not initialized")
    return jwt_service

def initialize_jwt_service(private_key_path: str, public_key_path: str, issuer: str, ttl_seconds: int = 300):
    global jwt_service
    jwt_service = JWTService(private_key_path, public_key_path, issuer, ttl_seconds)
```

## Step 4: Environment Configuration
Create `.env`:
```env
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=your-app-name
JWT_TTL_SECONDS=300
```

## Step 5: Update .gitignore
Add to `.gitignore`:
```
# JWT Keys - NEVER commit
*.pem
jwt_private_key.pem
jwt_public_key.pem
.env
```

## Step 6: Database Migration (if using Alembic)
```bash
alembic revision -m "add_jwt_signature_column"
```
Edit migration:
```python
def upgrade() -> None:
    op.add_column('your_table', sa.Column('signature_jwt', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('your_table', 'signature_jwt')
```

## Step 7: Initialize in Main App
Add to your `main.py`:
```python
from src.jwt_service import initialize_jwt_service, get_jwt_service
import os

@app.on_event("startup")
async def startup_event():
    # Initialize JWT with 5-minute expiration
    initialize_jwt_service(
        os.getenv('JWT_PRIVATE_KEY_PATH', 'jwt_private_key.pem'),
        os.getenv('JWT_PUBLIC_KEY_PATH', 'jwt_public_key.pem'),
        os.getenv('JWT_ISSUER', 'your-app'),
        int(os.getenv('JWT_TTL_SECONDS', '300'))  # 5 minutes
    )
    print("✅ JWT service ready with 5-minute tokens")
```

## Step 8: Add JWT Signing to Endpoints
```python
@app.post("/your-endpoint")  # Replace with actual endpoint
async def create_item(data: YourModel):
    # Your existing logic...
    
    # Add JWT signing
    jwt_service = get_jwt_service()
    jwt_token = jwt_service.sign_artifact(item_id, item_data_dict)
    
    # Save to database
    item.signature_jwt = jwt_token  # Add this field to your model
    db.commit()
    
    return {"id": item_id, "signature_jwt": jwt_token, "expires_in_minutes": 5}
```

## Step 9: Add JWT Verification
```python
@app.post("/verify")  # Replace with actual endpoint
async def verify_item(request: VerifyModel):
    # Your existing verification...
    
    # Add JWT verification
    jwt_result = {"verified": False, "error": "No JWT signature"}
    if item.signature_jwt:
        jwt_service = get_jwt_service()
        jwt_result = jwt_service.verify_signature(item.signature_jwt)
    
    return {
        "is_valid": your_existing_validation,
        "jwt_signature": jwt_result,
        "token_lifetime_minutes": 5
    }
```

## Step 10: Test Commands
```bash
# Test creation (should create JWT)
curl -X POST "http://localhost:8000/your-endpoint" -H "Content-Type: application/json" -d '{"test": "data"}'

# Test verification (should verify JWT)
curl -X POST "http://localhost:8000/verify" -H "Content-Type: application/json" -d '{"id": "test-id"}'

# Test expiration (wait 6 minutes, then verify - should fail)
sleep 360 && curl -X POST "http://localhost:8000/verify" -H "Content-Type: application/json" -d '{"id": "test-id"}'
```

---

**Copilot Instructions:** 
1. Adapt the endpoint names and data models to match this repository's structure
2. Add the JWT signature column to the appropriate database table/model
3. Integrate JWT signing into existing document/data creation endpoints
4. Add JWT verification to existing verification/retrieval endpoints
5. Ensure 5-minute token expiration is working (JWT_TTL_SECONDS=300)
6. Test that tokens expire after exactly 5 minutes

**Expected Result:** Every document/item created gets a JWT signature that expires in 5 minutes, providing ultra-secure cryptographic proof of authenticity with short-lived tokens.
