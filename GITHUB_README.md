# IntegrityX - JWT Digital Signature Platform

🔐 **Complete JWT Digital Signature Implementation** - A blockchain-based document integrity platform with enterprise-grade JWT cryptographic signatures.

## 🎯 **What This Repository Contains**

This is a **complete implementation** of JWT digital signatures on top of the IntegrityX blockchain document platform, featuring:

### ✅ **JWT Digital Signatures**
- **RS256 Algorithm** with 2048-bit RSA keys
- **Automatic Document Signing** on all seal operations
- **Cryptographic Verification** with tamper detection
- **Dual-Layer Security**: Blockchain + JWT signatures

### ✅ **Production Features**
- **Database Integration** with signature storage
- **Health Monitoring** with JWT service status
- **Comprehensive Error Handling** and logging
- **Complete API Documentation**

### ✅ **Frontend Integration**
- **Seamless User Experience** - transparent JWT signing
- **All Documents Automatically Signed** through frontend
- **Real-time Verification** and status display

## 🚀 **Quick Start**

1. **Clone and Setup:**
   ```bash
   git clone <your-repo-url>
   cd integrityx-jwt
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Generate JWT Keys:**
   ```bash
   python generate_jwt_keys.py
   ```

4. **Run Database Migration:**
   ```bash
   alembic upgrade head
   ```

5. **Start Backend:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Start Frontend:**
   ```bash
   npm install
   npm run dev
   ```

## 🔧 **Environment Configuration**

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# JWT Digital Signature Configuration
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=integrityx-demo
JWT_TTL_SECONDS=3600
```

## 📚 **API Endpoints**

### Document Sealing (with JWT)
```bash
POST /api/loan-documents/seal
# Automatically creates JWT signature
```

### Verification (includes JWT)
```bash
POST /api/verify
# Verifies both blockchain and JWT signature
```

### Health Check
```bash
GET /api/health
# Shows JWT service status
```

## 🧪 **Testing JWT Implementation**

```bash
# Run JWT service tests
cd backend
python -m pytest tests/test_jwt_service.py -v

# Test complete verification workflow
python -m pytest tests/test_verification_integration.py -v
```

## 🏗️ **Architecture**

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite with Alembic migrations
- **JWT**: RS256 algorithm with secure key management
- **Frontend**: Next.js with TypeScript
- **Blockchain**: Walacor integration with local simulation

## 📖 **Documentation**

- See `PROJECT_DOCUMENTATION.md` for complete technical documentation
- See `backend/src/jwt_service.py` for JWT implementation details
- See `tests/` directory for comprehensive test examples

## 🔐 **Security Features**

- **2048-bit RSA Keys** for maximum security
- **Canonical JSON Signing** for consistency
- **Tamper Detection** via signature verification
- **Time-bounded Tokens** with expiration
- **Secure Key Storage** and management

## 🎯 **Use Cases**

Perfect for:
- Document integrity verification
- Loan document authentication
- Compliance and audit trails
- Legal document certification
- Financial record protection

---

**Ready to use JWT digital signatures in your own project? Clone and start building!** 🚀
