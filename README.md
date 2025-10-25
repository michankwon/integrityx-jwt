# 🔒 IntegrityX - Financial Document Integrity System

A comprehensive financial document integrity system that uses cryptographic hashing and blockchain technology to detect tampering and maintain complete audit trails.

## 🚀 Features

- **📤 Document Upload**: Secure document storage with cryptographic hashing
- **🔍 Integrity Verification**: Tampering detection using hash comparison
- **✍️ Digital Signatures**: JWT-based document signing for cryptographic proof of authenticity
- **🔗 Provenance Tracking**: Complete document lineage and relationship tracking
- **⏰ Time Machine**: View document states at any past timestamp
- **📊 Audit Trails**: Comprehensive logging and compliance reporting

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IntegrityX_Python
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Walacor credentials
   ```

4. **Initialize schemas** (first time only)
   ```bash
   python scripts/initialize_schemas.py
   ```

## 🎯 Running the Application

### Streamlit Web Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Command Line Tools

**Test Connection**
```bash
python test_connection.py
```

**Tampering Detection Demo**
```bash
python tests/test_tampering.py
```

**Provenance Chain Demo**
```bash
python tests/test_provenance.py
```

## 📋 Application Pages

### 📤 Upload Document
- Upload loan documents with metadata
- Automatic cryptographic hashing
- Secure storage with audit trails

### 🔍 Verify Integrity
- Verify document authenticity
- Detect tampering and modifications
- Compare current vs stored hashes

### 🔗 Provenance Chain
- View complete document lineage
- Track document relationships
- Analyze document lifecycle

### 📋 Attestations & Provenance
- Create and manage document attestations
- Link parent-child document relationships
- Visualize document lineage with interactive graphs
- Download comprehensive disclosure packs

## 🔧 Configuration

### Environment Variables (.env)
```env
# Walacor Instance Configuration
WALACOR_HOST=your-walacor-host
WALACOR_USERNAME=your-username
WALACOR_PASSWORD=your-password

# Application Settings
STORAGE_PATH=data/documents
TEMP_PATH=data/temp

# JWT Digital Signatures (REQUIRED)
JWT_PRIVATE_KEY_PATH=secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/jwt_public.pem
JWT_ISSUER=integrityx-demo
JWT_TTL_SECONDS=3600

# Security
SECRET_KEY=your-secret-key
SESSION_TIMEOUT_MINUTES=30

# JWT Digital Signatures
JWT_PRIVATE_KEY_PATH=keys/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=keys/jwt_public_key.pem
JWT_ISSUER=integrityx
```

## 📋 Attestations & Provenance

### Overview
The Attestations & Provenance system provides comprehensive document certification and relationship tracking capabilities. This system allows you to create attestations for documents, establish parent-child relationships between documents, and generate complete disclosure packs for regulatory compliance.

### Attestations

Attestations are certifications or validations that can be applied to documents, such as quality checks, KYC verification, policy compliance, etc.

#### Creating Attestations
```typescript
// Example attestation data
{
  "artifactId": "doc_12345",
  "etid": "ATTESTATION_ETID_001",
  "kind": "qc_check",
  "issuedBy": "quality_team",
  "details": {
    "score": 95,
    "notes": "High quality document",
    "checker": "automated_system",
    "timestamp": "2024-01-01T10:00:00Z"
  }
}
```

#### Common Attestation Types
- **qc_check**: Quality control verification
- **kyc_passed**: Know Your Customer verification
- **policy_ok**: Policy compliance check
- **audit_complete**: Audit completion certification
- **approval_granted**: Approval authorization
- **compliance_verified**: Compliance verification
- **risk_assessed**: Risk assessment completion

### Provenance Linking

Provenance links establish relationships between documents, enabling you to track document lineage and dependencies.

#### Creating Provenance Links
```typescript
// Example provenance link
{
  "parentArtifactId": "loan_application_123",
  "childArtifactId": "appraisal_456",
  "relation": "contains"
}
```

#### Relationship Types
- **contains**: Parent contains child document
- **derived_from**: Child derived from parent document
- **supersedes**: Child replaces parent document
- **references**: Child references parent document
- **validates**: Child validates parent document

### Disclosure Pack

A disclosure pack is a comprehensive ZIP file containing all relevant information about a document for regulatory compliance and audit purposes.

#### Contents of Disclosure Pack
The disclosure pack (`disclosure_[artifactId].zip`) contains:

1. **proof.json** - Walacor proof bundle with blockchain anchors and signatures
2. **artifact.json** - Complete artifact details and metadata
3. **attestations.json** - All attestations linked to the artifact
4. **audit_events.json** - Recent audit events and access logs
5. **manifest.json** - Package metadata and summary information

#### Example manifest.json
```json
{
  "disclosure_pack_version": "1.0",
  "generated_at": "2024-01-01T12:00:00Z",
  "artifact_id": "doc_12345",
  "artifact_hash": "sha256:abc123...",
  "artifact_etid": 100001,
  "created_at": "2024-01-01T10:00:00Z",
  "algorithm": "SHA-256",
  "app_version": "1.0.0",
  "total_attestations": 3,
  "total_events": 15,
  "walacor_tx_id": "tx_789012"
}
```

### API Endpoints

#### Attestations
- `POST /api/attestations` - Create new attestation
- `GET /api/attestations?artifactId={id}` - List attestations for artifact

#### Provenance
- `POST /api/provenance/link` - Create provenance link
- `GET /api/provenance/children?parentId={id}` - List child documents
- `GET /api/provenance/parents?childId={id}` - List parent documents

#### Disclosure Pack
- `GET /api/disclosure-pack?id={artifactId}` - Download disclosure pack

### Usage Examples

#### 1. Creating a Quality Check Attestation
```bash
curl -X POST /api/attestations \
  -H "Content-Type: application/json" \
  -d '{
    "artifactId": "loan_doc_123",
    "etid": "ATTESTATION_ETID_001",
    "kind": "qc_check",
    "issuedBy": "quality_team",
    "details": {
      "score": 95,
      "notes": "Document passed quality check",
      "checker": "automated_system"
    }
  }'
```

#### 2. Linking Documents
```bash
curl -X POST /api/provenance/link \
  -H "Content-Type: application/json" \
  -d '{
    "parentArtifactId": "loan_application_123",
    "childArtifactId": "appraisal_456",
    "relation": "contains"
  }'
```

#### 3. Downloading Disclosure Pack
```bash
curl -X GET /api/disclosure-pack?id=loan_doc_123 \
  -o disclosure_loan_doc_123.zip
```

### Frontend Components

#### AttestationList
Displays all attestations for a document with expandable details and copy functionality.

#### AttestationForm
Provides a form for creating new attestations with auto-fill examples based on attestation type.

#### LineageGraph
Visualizes document relationships with a hierarchical graph showing parents, current document, and children.

#### ProvenanceLinker
Allows users to create parent-child relationships between documents with relation type selection.

#### DisclosureButton
Downloads a comprehensive disclosure pack containing all document-related information.

## 🏗️ Architecture

### Core Components

- **DocumentHandler**: Cryptographic hashing and file management
- **WalacorIntegrityService**: Blockchain integration and data storage
- **DocumentVerifier**: Tampering detection and integrity verification
- **ProvenanceTracker**: Document relationship and lineage tracking
- **DocumentTimeMachine**: Temporal analysis and forensic capabilities

### Data Schemas

- **loan_documents** (ETId: 100001): Document metadata and hashes
- **document_provenance** (ETId: 100002): Document relationships
- **attestations** (ETId: 100003): Document attestations and signatures
- **audit_logs** (ETId: 100004): Complete audit trail

## 🧪 Testing

### Backend Tests (pytest)

Run the comprehensive backend test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_attestations.py -v
pytest tests/test_provenance.py -v
pytest tests/test_disclosure_pack.py -v

# Run with coverage
pytest --cov=backend tests/
```

#### Test Coverage
- **Attestations**: Create, list, validation, and error handling
- **Provenance**: Link creation, idempotency, parent/child relationships
- **Disclosure Pack**: ZIP generation, content validation, error scenarios

### Frontend Tests (Jest + React Testing Library)

```bash
# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run frontend tests
npm test

# Run specific component tests
npm test AttestationList
npm test AttestationForm
npm test DisclosureButton
```

#### Test Coverage
- **AttestationList**: Renders rows, details expansion, error handling
- **AttestationForm**: Form submission, validation, API integration
- **DisclosureButton**: Download functionality, error handling, loading states

### Integration Tests

```bash
# Test API endpoints
python tests/test_attestations.py
python tests/test_provenance.py
python tests/test_disclosure_pack.py

# Test frontend components
npm test
```

### Manual Testing

Use the provided HTML test files for manual API testing:

```bash
# Open in browser
open frontend/test_attestations.html
open frontend/test_provenance.html
open frontend/test_disclosure_pack.html
```

## 📊 Demo Scenarios

### Tampering Detection
1. Create original document with hash
2. Modify document content
3. Verify integrity - tampering detected!

### Provenance Chain
1. Upload loan application
2. Link to appraisal
3. Link to underwriting
4. Link to closing
5. View complete chain

### Time Machine
1. View document at any past timestamp
2. Analyze custody chain
3. Forensic investigation capabilities

## 🔒 Security Features

- **Cryptographic Hashing**: SHA-256 for document integrity
- **Digital Signatures**: RSA-2048 JWT signatures with canonical JSON for tamper-proof verification
- **Blockchain Storage**: Immutable audit trails
- **Access Control**: User authentication and authorization
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: Secure data transmission and storage

### 🔐 JWT Digital Signatures

IntegrityX includes built-in JWT (JSON Web Token) digital signature capabilities that provide cryptographic proof of document authenticity and tamper detection.

#### Key Features
- **RS256 Algorithm**: RSA signatures with SHA-256 hashing
- **2048-bit RSA Keys**: Industry-standard key strength
- **Canonical JSON**: Consistent payload representation for signing
- **Automatic Integration**: Documents are automatically signed during sealing
- **Tamper Detection**: Any modification to signed documents is immediately detected

#### Setup Requirements
1. **Generate RSA Key Pair**:
   ```bash
   cd backend
   python generate_jwt_keys.py
   ```

2. **Configure Environment Variables**:
   ```env
   JWT_PRIVATE_KEY_PATH=keys/jwt_private_key.pem
   JWT_PUBLIC_KEY_PATH=keys/jwt_public_key.pem
   JWT_ISSUER=integrityx
   ```

#### Operational Considerations
- **Key Security**: Store private keys securely with restricted access
- **Key Rotation**: Rotate keys periodically (recommended: annually)
- **Backup Strategy**: Maintain secure backups of both public and private keys
- **Token Expiration**: Default 1-hour expiration for signed tokens
- **Verification**: Signatures are verified during document integrity checks

#### API Integration
- **Seal Endpoint**: `/api/seal` automatically generates JWT signatures
- **Verify Endpoint**: `/api/verify` includes JWT verification in response
- **Response Format**: JWT data returned in `signature_jwt` field

## 📈 Performance

- **Efficient Hashing**: Chunk-based processing for large files
- **Cached Services**: Streamlit service caching for performance
- **Optimized Queries**: Indexed database operations
- **Scalable Architecture**: Designed for high-volume processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@integrityx.com
- Documentation: docs.integrityx.com
- Issues: GitHub Issues

---

**🔒 IntegrityX** - Ensuring Financial Document Integrity Through Technology



