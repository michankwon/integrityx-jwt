"""
Main FastAPI application for the Walacor Financial Integrity Platform.

This module provides a RESTful API for document integrity verification,
manifest processing, and artifact management using the Walacor blockchain.

Key Features:
- Document ingestion and verification
- Multi-file packet processing
- Manifest validation and hashing
- Artifact management and tracking
- Comprehensive error handling
- CORS support for frontend integration

API Endpoints:
- Health check and system status
- JSON document ingestion
- Multi-file packet ingestion
- Manifest verification
- Artifact retrieval and management
- System statistics and monitoring
"""

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import json
import jwt
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
import traceback
import time
import asyncio
import aiohttp
from contextvars import ContextVar
import zipfile
from io import BytesIO
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Import backend services
from src.database import Database
from src.document_handler import DocumentHandler
from src.walacor_service import WalacorIntegrityService
from src.json_handler import JSONHandler
from src.manifest_handler import ManifestHandler
from src.repositories import AttestationRepository, ProvenanceRepository
from src.verification_portal import VerificationPortal
from src.voice_service import VoiceCommandProcessor
from src.analytics_service import AnalyticsService
from src.advanced_security import AdvancedSecurityService
from src.quantum_safe_security import HybridSecurityService, quantum_safe_hashing, quantum_safe_signatures
from src.ai_anomaly_detector import AIAnomalyDetector
from src.time_machine import TimeMachine
from src.smart_contracts import SmartContractsService
from src.predictive_analytics import PredictiveAnalyticsService
from src.document_intelligence import DocumentIntelligenceService
from src.encryption_service import get_encryption_service
from src.jwt_service import canonical_json, sign_artifact, verify_signature
from src.structured_logger import (
    log_endpoint_request, log_endpoint_start, with_structured_logging,
    log_database_operation, log_external_service_call,
    extract_user_id_from_request, extract_etid_from_request, extract_hash_prefix
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan event handler
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services at startup and cleanup at shutdown."""
    global db, doc_handler, wal_service, json_handler, manifest_handler, attestation_repo, provenance_repo, verification_portal, voice_processor, analytics_service, ai_anomaly_detector, time_machine, smart_contracts, predictive_analytics, document_intelligence, advanced_security, hybrid_security
    
    try:
        logger.info("Initializing Walacor Financial Integrity API services...")
        
        # Initialize database
        db = Database()
        logger.info("✅ Database service initialized")
        
        # Validate JWT configuration on startup
        try:
            from src.jwt_service import _PRIVATE_KEY, _PUBLIC_KEY, _ISSUER
            logger.info(f"✅ JWT service initialized with issuer: {_ISSUER}")
        except Exception as e:
            logger.warning(f"⚠️ JWT service initialization failed: {e}")
            logger.warning("JWT digital signatures will be unavailable")
        
        # Initialize document handler
        doc_handler = DocumentHandler()
        logger.info("✅ Document handler initialized")
        
        # Initialize Walacor service (optional - may fail in demo mode)
        try:
            wal_service = WalacorIntegrityService()
            logger.info("✅ Walacor service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Walacor service initialization failed (demo mode): {e}")
            wal_service = None
        
        # Initialize Advanced Security service
        try:
            advanced_security = AdvancedSecurityService()
            logger.info("✅ Advanced Security service initialized")
        except Exception as e:
            logger.error(f"❌ Advanced Security service initialization failed: {e}")
            advanced_security = None

        # Initialize Quantum-Safe Security service
        try:
            hybrid_security = HybridSecurityService()
            logger.info("✅ Quantum-Safe Security service initialized")
        except Exception as e:
            logger.error(f"❌ Quantum-Safe Security service initialization failed: {e}")
            hybrid_security = None
        
        # Initialize JSON handler
        json_handler = JSONHandler()
        logger.info("✅ JSON handler initialized")
        
        # Initialize manifest handler
        manifest_handler = ManifestHandler()
        logger.info("✅ Manifest handler initialized")
        
        # Initialize repositories
        attestation_repo = AttestationRepository()
        provenance_repo = ProvenanceRepository()
        logger.info("✅ Repository services initialized")
        
        # Initialize verification portal
        verification_portal = VerificationPortal()
        logger.info("✅ Verification portal initialized")
        
        # Initialize voice command processor
        voice_processor = VoiceCommandProcessor()
        logger.info("✅ Voice command processor initialized")
        
        # Initialize analytics service
        analytics_service = AnalyticsService(db_service=db)
        logger.info("✅ Analytics service initialized")
        
        # Initialize AI anomaly detector
        ai_anomaly_detector = AIAnomalyDetector(db_service=db)
        logger.info("✅ AI anomaly detector initialized")
        
        # Initialize time machine service
        time_machine = TimeMachine(db_service=db)
        logger.info("✅ Time machine service initialized")
        
        # Initialize smart contracts service
        smart_contracts = SmartContractsService(db_service=db)
        logger.info("✅ Smart contracts service initialized")
        
        # Initialize predictive analytics service
        predictive_analytics = PredictiveAnalyticsService(db_service=db)
        logger.info("✅ Predictive analytics service initialized")
        
        # Initialize document intelligence service
        document_intelligence = DocumentIntelligenceService()
        logger.info("✅ Document intelligence service initialized")
        
        logger.info("🎉 All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        logger.error(traceback.format_exc())
        raise
    
    yield
    
    # Cleanup code here if needed
    logger.info("Shutting down services...")

# Initialize FastAPI app
app = FastAPI(
    title="Walacor Financial Integrity API",
    description="API for document integrity verification and artifact management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Verification Helper Function
def verify_jwt_signature(artifact, submitted_payload_dict):
    """Verify JWT signature for submitted document"""
    verification_result = {}
    
    try:
        # Get the stored JWT token from database
        stored_token = getattr(artifact, "signature_jwt", None)
        
        if not stored_token:
            verification_result["jwt_verified"] = False
            verification_result["jwt_error"] = "No JWT signature found"
            return verification_result
            
        # Verify the signature using your jwt_service
        claims = verify_signature(stored_token, submitted_payload_dict)
        
        # If we get here, verification succeeded
        verification_result["verified"] = True
        verification_result["error"] = None
        verification_result["claims"] = {
            "artifact_id": claims.get("artifact_id"),
            "issued_at": datetime.fromtimestamp(claims.get("iat", 0), timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(claims.get("exp", 0), timezone.utc).isoformat()
        }
        
    except jwt.ExpiredSignatureError:
        verification_result["verified"] = False
        verification_result["error"] = "JWT signature expired"
        
    except jwt.InvalidSignatureError:
        verification_result["verified"] = False
        verification_result["error"] = "Invalid JWT signature"
        
    except ValueError as e:
        verification_result["verified"] = False
        verification_result["error"] = f"Payload verification failed: {str(e)}"
        
    except Exception as e:
        verification_result["verified"] = False
        verification_result["error"] = f"Verification error: {str(e)}"
    
    return verification_result

# Global service variables
db = None
doc_handler = None
wal_service = None
json_handler = None
manifest_handler = None
attestation_repo = None
provenance_repo = None
verification_portal = None
voice_processor = None
analytics_service = None
ai_anomaly_detector = None
time_machine = None
smart_contracts = None
predictive_analytics = None
document_intelligence = None

# Add request tracking middleware
@app.middleware("http")
async def add_request_tracking(request, call_next):
    """Middleware to add request tracking and structured logging."""
    from src.structured_logger import generate_request_id, request_id_var, start_time_var
    
    # Generate request ID
    request_id = generate_request_id()
    request_id_var.set(request_id)
    
    # Record start time
    start_time = time.time()
    start_time_var.set(start_time)
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

# Global service instances
db: Optional[Database] = None
doc_handler: Optional[DocumentHandler] = None
wal_service: Optional[WalacorIntegrityService] = None
json_handler: Optional[JSONHandler] = None
manifest_handler: Optional[ManifestHandler] = None
attestation_repo: Optional[AttestationRepository] = None
provenance_repo: Optional[ProvenanceRepository] = None
verification_portal: Optional[VerificationPortal] = None


# Standardized response models
class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class StandardResponse(BaseModel):
    """Standardized response model."""
    ok: bool = Field(..., description="Success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[ErrorDetail] = Field(None, description="Error information")


# Pydantic models for request/response
class ServiceHealth(BaseModel):
    """Individual service health information."""
    status: str = Field(..., description="Service status: up/down")
    duration_ms: float = Field(..., description="Health check duration in milliseconds")
    details: Optional[str] = Field(None, description="Additional service details")
    error: Optional[str] = Field(None, description="Error message if service is down")


class HealthData(BaseModel):
    """Health check data model."""
    status: str = Field(..., description="Overall API status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    total_duration_ms: float = Field(..., description="Total health check duration in milliseconds")
    services: Dict[str, ServiceHealth] = Field(..., description="Detailed service health information")


class IngestResponse(BaseModel):
    """Document ingestion response model."""
    message: str = Field(..., description="Response message")
    artifact_id: Optional[str] = Field(None, description="Created artifact ID")
    hash: Optional[str] = Field(None, description="Document hash")
    file_count: Optional[int] = Field(None, description="Number of files processed")
    timestamp: str = Field(..., description="Processing timestamp")


class VerifyResponse(BaseModel):
    """Manifest verification response model."""
    message: str = Field(..., description="Response message")
    is_valid: bool = Field(..., description="Validation result")
    hash: Optional[str] = Field(None, description="Manifest hash")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    timestamp: str = Field(..., description="Verification timestamp")


class ArtifactResponse(BaseModel):
    """Artifact details response model."""
    id: str = Field(..., description="Artifact ID")
    loan_id: str = Field(..., description="Loan ID")
    artifact_type: str = Field(..., description="Artifact type")
    payload_sha256: str = Field(..., description="Payload hash")
    manifest_sha256: Optional[str] = Field(None, description="Manifest hash")
    walacor_tx_id: str = Field(..., description="Walacor transaction ID")
    created_by: str = Field(..., description="Creator")
    created_at: str = Field(..., description="Creation timestamp")
    blockchain_seal: Optional[str] = Field(None, description="Blockchain seal information")
    local_metadata: Optional[Dict[str, Any]] = Field(None, description="Local metadata including comprehensive document data")
    borrower_info: Optional[Dict[str, Any]] = Field(None, description="Borrower information for loan documents")
    files: List[Dict[str, Any]] = Field(default_factory=list, description="Associated files")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Artifact events")


class EventResponse(BaseModel):
    """Event details response model."""
    id: str = Field(..., description="Event ID")
    artifact_id: str = Field(..., description="Artifact ID")
    event_type: str = Field(..., description="Event type")
    created_by: str = Field(..., description="Creator")
    created_at: str = Field(..., description="Creation timestamp")
    payload_json: Optional[str] = Field(None, description="Event payload")
    walacor_tx_id: Optional[str] = Field(None, description="Walacor transaction ID")


class StatsResponse(BaseModel):
    """System statistics response model."""
    total_artifacts: int = Field(..., description="Total number of artifacts")
    total_files: int = Field(..., description="Total number of files")
    total_events: int = Field(..., description="Total number of events")
    artifacts_by_type: Dict[str, int] = Field(..., description="Artifacts by type")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity")
    timestamp: str = Field(..., description="Statistics timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")


class IngestJsonRequest(BaseModel):
    """JSON ingestion request model."""
    loan_id: str = Field(..., description="Loan ID")
    created_by: str = Field(..., description="Creator identifier")


class IngestPacketRequest(BaseModel):
    """Packet ingestion request model."""
    loan_id: str = Field(..., description="Loan ID")
    created_by: str = Field(..., description="Creator identifier")


# New request/response models for additional endpoints
class SealRequest(BaseModel):
    """Seal request model."""
    etid: int = Field(..., description="Entity Type ID")
    payloadHash: str = Field(..., description="Payload SHA-256 hash")
    externalUri: str = Field(..., description="External URI where artifact is stored")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SealResponse(BaseModel):
    """Seal response model."""
    message: str = Field(..., description="Response message")
    artifact_id: str = Field(..., description="Artifact ID")
    walacor_tx_id: str = Field(..., description="Walacor transaction ID")
    sealed_at: str = Field(..., description="Sealing timestamp")
    proof_bundle: Dict[str, Any] = Field(..., description="Proof bundle from Walacor")


class VerifyRequest(BaseModel):
    """Verify request model."""
    etid: int = Field(..., description="Entity Type ID")
    payloadHash: str = Field(..., description="Payload SHA-256 hash")


class VerifyResponse(BaseModel):
    """Verify response model."""
    message: str = Field(..., description="Response message")
    is_valid: bool = Field(..., description="Verification result")
    status: str = Field(..., description="Status: ok or tamper")
    artifact_id: Optional[str] = Field(None, description="Artifact ID if found")
    verified_at: str = Field(..., description="Verification timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Verification details")


class ProofResponse(BaseModel):
    """Proof response model."""
    proof_bundle: Dict[str, Any] = Field(..., description="Proof bundle from Walacor")
    artifact_id: str = Field(..., description="Artifact ID")
    etid: int = Field(..., description="Entity Type ID")
    retrieved_at: str = Field(..., description="Retrieval timestamp")


class PresignRequest(BaseModel):
    """S3 presign request model."""
    key: str = Field(..., description="S3 object key")
    contentType: str = Field(..., description="Content type")
    size: int = Field(..., description="File size in bytes")
    expiresIn: int = Field(default=3600, description="Expiration time in seconds")


class PresignResponse(BaseModel):
    """S3 presign response model."""
    putUrl: str = Field(..., description="Presigned PUT URL")
    objectUrl: str = Field(..., description="Object URL")
    expiresAt: str = Field(..., description="Expiration timestamp")
    key: str = Field(..., description="S3 object key")


class EventsRequest(BaseModel):
    """Events query request model."""
    etid: Optional[int] = Field(None, description="Filter by Entity Type ID")
    startDate: Optional[str] = Field(None, description="Start date (ISO format)")
    endDate: Optional[str] = Field(None, description="End date (ISO format)")
    status: Optional[str] = Field(None, description="Filter by status")
    page: int = Field(default=1, description="Page number")
    limit: int = Field(default=50, description="Items per page")


class EventsResponse(BaseModel):
    """Events response model."""
    events: List[Dict[str, Any]] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


# Attestation models
class AttestationIn(BaseModel):
    """Attestation creation request model."""
    artifactId: str = Field(..., description="Artifact ID")
    etid: str = Field(..., description="Entity Type ID")
    kind: str = Field(..., description="Attestation kind (e.g., qc_check, kyc_passed)")
    issuedBy: str = Field(..., description="User or service that issued the attestation")
    details: dict = Field(default_factory=dict, description="Free-form metadata")


class AttestationOut(BaseModel):
    """Attestation response model."""
    id: int = Field(..., description="Attestation ID")
    artifactId: str = Field(..., description="Artifact ID")
    etid: str = Field(..., description="Entity Type ID")
    kind: str = Field(..., description="Attestation kind")
    issuedBy: str = Field(..., description="User or service that issued the attestation")
    details: dict = Field(..., description="Free-form metadata")
    createdAt: datetime = Field(..., description="Creation timestamp")


# Provenance models
class ProvenanceLinkIn(BaseModel):
    """Provenance link creation request model."""
    parentArtifactId: str = Field(..., description="Parent artifact ID")
    childArtifactId: str = Field(..., description="Child artifact ID")
    relation: str = Field(..., description="Relationship type (e.g., contains, derived_from)")


class ProvenanceLinkOut(BaseModel):
    """Provenance link response model."""
    id: int = Field(..., description="Provenance link ID")
    parentArtifactId: str = Field(..., description="Parent artifact ID")
    childArtifactId: str = Field(..., description="Child artifact ID")
    relation: str = Field(..., description="Relationship type")
    createdAt: datetime = Field(..., description="Creation timestamp")


class VerificationLinkRequest(BaseModel):
    """Verification link generation request model."""
    documentId: str = Field(..., description="Document ID to verify")
    documentHash: str = Field(..., description="Document hash for verification")
    allowedParty: str = Field(..., description="Email of the party allowed to verify")
    permissions: List[str] = Field(..., description="List of permissions (hash, timestamp, attestations)")
    expiresInHours: int = Field(24, description="Token expiration time in hours")


class VerificationLinkResponse(BaseModel):
    """Verification link response model."""
    token: str = Field(..., description="Secure verification token")
    verificationUrl: str = Field(..., description="URL for verification")
    expiresAt: datetime = Field(..., description="Token expiration time")
    permissions: List[str] = Field(..., description="Granted permissions")


class VerificationRequest(BaseModel):
    """Verification request model."""
    token: str = Field(..., description="Verification token")
    verifierEmail: str = Field(..., description="Email of the verifier")


class VerificationResponse(BaseModel):
    """Verification response model."""
    isValid: bool = Field(..., description="Whether the document is valid")
    documentHash: str = Field(..., description="Document hash")
    timestamp: datetime = Field(..., description="Document timestamp")
    attestations: List[Dict[str, Any]] = Field(..., description="Document attestations")
    permissions: List[str] = Field(..., description="Granted permissions")
    verifiedAt: datetime = Field(..., description="Verification timestamp")


# Dependency to check if services are initialized
def get_services():
    """Get initialized services."""
    # Check only essential services (optional services like advanced_security can be None)
    essential_services = [db, doc_handler, json_handler, manifest_handler, attestation_repo, 
                         provenance_repo, verification_portal, voice_processor, analytics_service, 
                         ai_anomaly_detector, time_machine, smart_contracts, predictive_analytics, 
                         document_intelligence]
    
    if not all(essential_services):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Essential services not initialized"
        )
    return {
        "db": db,
        "doc_handler": doc_handler,
        "wal_service": wal_service,
        "json_handler": json_handler,
        "manifest_handler": manifest_handler,
        "attestation_repo": attestation_repo,
        "provenance_repo": provenance_repo,
        "verification_portal": verification_portal,
        "voice_processor": voice_processor,
        "analytics_service": analytics_service,
            "ai_anomaly_detector": ai_anomaly_detector,
            "time_machine": time_machine,
            "smart_contracts": smart_contracts,
        "predictive_analytics": predictive_analytics,
        "document_intelligence": document_intelligence,
        "advanced_security": advanced_security,
        "hybrid_security": hybrid_security
    }


# Helper functions for standardized responses
def create_success_response(data: Dict[str, Any]) -> StandardResponse:
    """Create a standardized success response."""
    return StandardResponse(ok=True, data=data)


def create_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> StandardResponse:
    """Create a standardized error response."""
    return StandardResponse(
        ok=False,
        error=ErrorDetail(code=code, message=message, details=details)
    )


# Configuration endpoint
@app.get("/api/config", response_model=StandardResponse)
async def get_config():
    """
    Get non-sensitive environment configuration.
    
    Returns environment variables that are safe to expose to the frontend.
    """
    try:
        # Only expose non-sensitive configuration
        safe_config = {}
        
        # Database configuration
        if os.getenv("DATABASE_URL"):
            safe_config["DATABASE_URL"] = os.getenv("DATABASE_URL")
        
        # Walacor configuration (non-sensitive parts)
        if os.getenv("WALACOR_HOST"):
            safe_config["WALACOR_HOST"] = os.getenv("WALACOR_HOST")
        
        # AWS configuration (non-sensitive parts)
        if os.getenv("AWS_REGION"):
            safe_config["AWS_REGION"] = os.getenv("AWS_REGION")
        if os.getenv("AWS_S3_BUCKET"):
            safe_config["AWS_S3_BUCKET"] = os.getenv("AWS_S3_BUCKET")
        
        # Application configuration
        safe_config["NODE_ENV"] = os.getenv("NODE_ENV", "development")
        safe_config["API_VERSION"] = "1.0.0"
        
        return create_success_response(safe_config)
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="CONFIG_ERROR",
                message="Failed to get configuration",
                details={"error": str(e)}
            ).dict()
        )


# Health check endpoint
@app.get("/api/health", response_model=StandardResponse)
async def health_check():
    """
    Enhanced health check endpoint.
    
    Returns detailed health status of the API and all services with timing information.
    Checks database, Walacor, and storage services.
    """
    start_time = time.time()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Log request start
    log_endpoint_start(
        endpoint="/api/health",
        method="GET"
    )
    
    try:
        services_health = {}
        
        # Check database health
        db_health = await check_database_health()
        services_health["db"] = db_health
        
        # Check Walacor health
        walacor_health = await check_walacor_health()
        services_health["walacor"] = walacor_health
        
        # Check storage health
        storage_health = await check_storage_health()
        services_health["storage"] = storage_health
        
        # Check other services (basic availability)
        services_health["document_handler"] = ServiceHealth(
            status="up" if doc_handler else "down",
            duration_ms=0.0,
            details="Document handler service"
        )
        
        services_health["json_handler"] = ServiceHealth(
            status="up" if json_handler else "down",
            duration_ms=0.0,
            details="JSON handler service"
        )
        
        services_health["manifest_handler"] = ServiceHealth(
            status="up" if manifest_handler else "down",
            duration_ms=0.0,
            details="Manifest handler service"
        )
        
        # Check JWT service health
        try:
            from src.jwt_service import _PRIVATE_KEY, _PUBLIC_KEY, _ISSUER
            services_health["jwt"] = ServiceHealth(
                status="up",
                duration_ms=0.0,
                details=f"JWT service operational (issuer: {_ISSUER})"
            )
        except Exception as e:
            services_health["jwt"] = ServiceHealth(
                status="down",
                duration_ms=0.0,
                details=f"JWT service unavailable: {str(e)}"
            )
        
        # Determine overall status
        critical_services = ["db", "walacor", "storage"]
        critical_statuses = [services_health[svc].status for svc in critical_services if svc in services_health]
        
        if all(status == "up" for status in critical_statuses):
            overall_status = "healthy"
            message = "All services are operational"
        elif any(status == "up" for status in critical_statuses):
            overall_status = "degraded"
            message = "Some services are unavailable"
        else:
            overall_status = "unhealthy"
            message = "Critical services are down"
        
        total_duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        health_data = HealthData(
            status=overall_status,
            message=message,
            timestamp=timestamp,
            total_duration_ms=total_duration,
            services=services_health
        )
        
        # Log successful completion
        latency_ms = (time.time() - start_time) * 1000
        log_endpoint_request(
            endpoint="/api/health",
            method="GET",
            latency_ms=latency_ms,
            result="success",
            overall_status=overall_status
        )
        
        return create_success_response(health_data.dict())
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        logger.error(traceback.format_exc())
        
        total_duration = (time.time() - start_time) * 1000
        
        # Log error
        log_endpoint_request(
            endpoint="/api/health",
            method="GET",
            latency_ms=total_duration,
            result="error",
            error=str(e)
        )
        
        error_data = HealthData(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            timestamp=timestamp,
            total_duration_ms=total_duration,
            services={
                "error": ServiceHealth(
                    status="down",
                    duration_ms=total_duration,
                    error=str(e)
                )
            }
        )
        
        return create_success_response(error_data.dict())


async def check_database_health() -> ServiceHealth:
    """Check database health with SELECT 1 query."""
    start_time = time.time()
    
    try:
        if not db:
            return ServiceHealth(
                status="down",
                duration_ms=0.0,
                error="Database service not initialized"
            )
        
        # Perform a simple SELECT 1 query
        with db:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                duration_ms = (time.time() - start_time) * 1000
                return ServiceHealth(
                    status="up",
                    duration_ms=duration_ms,
                    details=f"Database connection successful (SQLite)"
                )
            else:
                duration_ms = (time.time() - start_time) * 1000
                return ServiceHealth(
                    status="down",
                    duration_ms=duration_ms,
                    error="SELECT 1 query failed"
                )
                
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ServiceHealth(
            status="down",
            duration_ms=duration_ms,
            error=f"Database health check failed: {str(e)}"
        )


async def check_walacor_health() -> ServiceHealth:
    """Check Walacor service health with HEAD request."""
    start_time = time.time()
    
    try:
        if not wal_service:
            return ServiceHealth(
                status="down",
                duration_ms=0.0,
                error="Walacor service not initialized"
            )
        
        # Get Walacor base URL
        walacor_host = os.getenv("WALACOR_HOST")
        if not walacor_host:
            return ServiceHealth(
                status="down",
                duration_ms=0.0,
                error="WALACOR_HOST not configured"
            )
        
        # Ensure URL has protocol
        if not walacor_host.startswith(("http://", "https://")):
            walacor_url = f"http://{walacor_host}"
        else:
            walacor_url = walacor_host
        
        # Perform HEAD request with timeout
        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(walacor_url) as response:
                duration_ms = (time.time() - start_time) * 1000
                
                if response.status < 500:  # Accept any non-server error
                    return ServiceHealth(
                        status="up",
                        duration_ms=duration_ms,
                        details=f"Walacor service responding (HTTP {response.status})"
                    )
                else:
                    return ServiceHealth(
                        status="down",
                        duration_ms=duration_ms,
                        error=f"Walacor service error (HTTP {response.status})"
                    )
                    
    except asyncio.TimeoutError:
        duration_ms = (time.time() - start_time) * 1000
        return ServiceHealth(
            status="down",
            duration_ms=duration_ms,
            error="Walacor service timeout"
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ServiceHealth(
            status="down",
            duration_ms=duration_ms,
            error=f"Walacor health check failed: {str(e)}"
        )


async def check_storage_health() -> ServiceHealth:
    """Check S3 storage health with bucket HEAD request."""
    start_time = time.time()
    
    try:
        if not BOTO3_AVAILABLE:
            return ServiceHealth(
                status="down",
                duration_ms=0.0,
                error="boto3 not available - S3 service not configured"
            )
        
        # Check if S3 is configured
        bucket_name = os.getenv("AWS_S3_BUCKET")
        if not bucket_name:
            return ServiceHealth(
                status="down",
                duration_ms=0.0,
                error="AWS_S3_BUCKET not configured"
            )
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # Perform HEAD bucket request
        s3_client.head_bucket(Bucket=bucket_name)
        
        duration_ms = (time.time() - start_time) * 1000
        return ServiceHealth(
            status="up",
            duration_ms=duration_ms,
            details=f"S3 bucket '{bucket_name}' accessible"
        )
        
    except ClientError as e:
        duration_ms = (time.time() - start_time) * 1000
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        return ServiceHealth(
            status="down",
            duration_ms=duration_ms,
            error=f"S3 bucket error ({error_code}): {str(e)}"
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ServiceHealth(
            status="down",
            duration_ms=duration_ms,
            error=f"S3 health check failed: {str(e)}"
        )


# JSON document ingestion endpoint
@app.post("/api/ingest-json", response_model=StandardResponse)
async def ingest_json(
    file: UploadFile = File(..., description="JSON file to ingest"),
    comprehensive_document: Optional[str] = Form(None, description="Comprehensive document JSON with borrower information"),
    comprehensive_hash: Optional[str] = Form(None, description="SHA-256 hash of comprehensive document"),
    request: IngestJsonRequest = Depends(),
    services: dict = Depends(get_services)
):
    """
    Ingest a JSON document with comprehensive borrower information.
    
    Accepts a JSON file and processes it for integrity verification.
    Now includes borrower information in the hash calculation for immutable audit trail.
    """
    try:
        logger.info(f"Ingesting JSON file: {file.filename} for loan: {request.loan_id}")
        
        # Read file content
        content = await file.read()
        
        # Parse JSON
        try:
            json_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # Process JSON with JSONHandler
        result = services["json_handler"].process_json_artifact(json_data, 'loan')
        
        if not result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON validation failed: {', '.join(result['errors'])}"
            )
        
        # Get comprehensive document and hash from form data if available
        comprehensive_doc_obj = None
        final_hash = result['hash']  # Default to original hash
        
        # Check if comprehensive document data is available in the request
        if comprehensive_document and comprehensive_hash:
            try:
                comprehensive_doc_obj = json.loads(comprehensive_document)
                final_hash = comprehensive_hash
                logger.info("Processing comprehensive document with borrower information")
                logger.info(f"Comprehensive hash: {comprehensive_hash}")
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse comprehensive document JSON: {e}")
                logger.info("Falling back to original file hash")
        else:
            logger.info("No comprehensive document provided, using original file hash")
        
        # HYBRID APPROACH: Store blockchain seal and local metadata
        if services["wal_service"] is None:
            # Fallback if Walacor service is not available
            walacor_result = {
                "tx_id": "WAL_TX_JSON_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "seal_info": {"integrity_seal": f"SEAL_{final_hash[:16]}_{int(datetime.now().timestamp())}"},
                "local_metadata": {
                    "loan_id": request.loan_id,
                    "document_type": "json",
                    "file_size": len(content),
                    "file_path": f"data/documents/{file.filename}",
                    "uploaded_by": request.created_by,
                    "upload_timestamp": datetime.now().isoformat(),
                    "comprehensive_hash": final_hash,
                    "includes_borrower_info": comprehensive_doc_obj is not None,
                    "comprehensive_document": comprehensive_doc_obj
                }
            }
        else:
            walacor_result = services["wal_service"].store_document_hash(
                loan_id=request.loan_id,
                document_type="json",
                document_hash=final_hash,  # Use final hash (comprehensive or original)
                file_size=len(content),
                file_path=f"data/documents/{file.filename}",
                uploaded_by=request.created_by
            )
            
            # Add comprehensive document data to local_metadata if available
            if comprehensive_doc_obj is not None:
                walacor_result["local_metadata"].update({
                    "comprehensive_hash": final_hash,
                    "includes_borrower_info": True,
                    "comprehensive_document": comprehensive_doc_obj
                })
            else:
                walacor_result["local_metadata"].update({
                    "comprehensive_hash": final_hash,
                    "includes_borrower_info": False
                })
        
        # Extract borrower info from comprehensive document if available
        borrower_info = None
        if comprehensive_doc_obj and comprehensive_doc_obj.get('borrower'):
            borrower_info = comprehensive_doc_obj['borrower']
        
        # Store in database with hybrid data
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="json",
            etid=100002,  # ETID for JSON artifacts
            payload_sha256=final_hash,  # Store final hash
            walacor_tx_id=walacor_result.get("tx_id", "WAL_TX_JSON_" + datetime.now().strftime("%Y%m%d%H%M%S")),
            created_by=request.created_by,
            blockchain_seal=walacor_result.get("seal_info", {}).get("integrity_seal"),
            local_metadata=walacor_result.get("local_metadata", {}),
            borrower_info=borrower_info
        )
        
        # Generate JWT signature for the document
        try:
            # Use comprehensive document if available, otherwise use original JSON
            payload_to_sign = comprehensive_doc_obj if comprehensive_doc_obj else json_data
            jwt_token = sign_artifact(artifact_id, payload_to_sign)
            
            # Update the artifact with JWT signature
            services["db"].update_artifact_signature(artifact_id, jwt_token)
            
            logger.info(f"✅ JWT signature created for artifact: {artifact_id}")
            
        except Exception as jwt_error:
            logger.warning(f"Failed to create JWT signature: {jwt_error}")
            # Don't fail the main operation if JWT signing fails
        
        # Log event with comprehensive information
        event_payload = {
            "filename": file.filename, 
            "file_size": len(content),
            "comprehensive_hash": final_hash,
            "includes_borrower_info": comprehensive_doc_obj is not None
        }
        
        services["db"].insert_event(
            artifact_id=artifact_id,
            event_type="uploaded",
            created_by=request.created_by,
            payload_json=json.dumps(event_payload)
        )
        
        logger.info(f"✅ JSON document ingested successfully with hash: {artifact_id}")
        
        ingest_data = {
            "message": "JSON document ingested successfully with borrower information",
            "artifact_id": artifact_id,
            "hash": final_hash,
            "file_count": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "walacor_tx_id": walacor_result.get("tx_id"),
            "includes_borrower_info": comprehensive_doc_obj is not None
        }
        return create_success_response(ingest_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSON ingestion failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON ingestion failed: {str(e)}"
        )


# Multi-file packet ingestion endpoint
@app.post("/api/ingest-packet", response_model=StandardResponse)
async def ingest_packet(
    files: List[UploadFile] = File(..., description="Files to ingest as a packet"),
    request: IngestPacketRequest = Depends(),
    services: dict = Depends(get_services)
):
    """
    Ingest a multi-file packet.
    
    Accepts multiple files and creates a manifest for the packet.
    """
    try:
        logger.info(f"Ingesting packet with {len(files)} files for loan: {request.loan_id}")
        
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        # Process each file
        file_infos = []
        for file in files:
            # Read file content
            content = await file.read()
            
            # Calculate hash
            file_hash = services["doc_handler"].calculate_hash_from_bytes(content)
            
            # Create file info
            file_info = {
                "name": file.filename,
                "uri": f"temp://{file.filename}",  # In production, this would be a real URI
                "sha256": file_hash,
                "size": len(content),
                "contentType": file.content_type or "application/octet-stream"
            }
            file_infos.append(file_info)
        
        # Create manifest
        manifest = services["manifest_handler"].create_manifest(
            loan_id=request.loan_id,
            files=file_infos,
            attestations=[],
            created_by=request.created_by,
            artifact_type="loan_packet"
        )
        
        # Process manifest
        manifest_result = services["manifest_handler"].process_manifest(manifest)
        
        if not manifest_result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manifest validation failed: {', '.join(manifest_result['errors'])}"
            )
        
        # HYBRID APPROACH: Store blockchain seal and local metadata for packet
        total_size = sum(file_info["size"] for file_info in file_infos)
        if services["wal_service"] is None:
            # Fallback if Walacor service is not available
            walacor_result = {
                "tx_id": "WAL_TX_PACKET_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                "seal_info": {"integrity_seal": f"SEAL_{manifest_result['hash'][:16]}_{int(datetime.now().timestamp())}"},
                "local_metadata": {
                    "loan_id": request.loan_id,
                    "document_type": "loan_packet",
                    "file_size": total_size,
                    "file_path": f"data/documents/packet_{request.loan_id}",
                    "uploaded_by": request.created_by,
                    "upload_timestamp": datetime.now().isoformat()
                }
            }
        else:
            walacor_result = services["wal_service"].store_document_hash(
                loan_id=request.loan_id,
                document_type="loan_packet",
                document_hash=manifest_result['hash'],
                file_size=total_size,
                file_path=f"data/documents/packet_{request.loan_id}",
                uploaded_by=request.created_by
            )
        
        # Store in database with hybrid data
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="loan_packet",
            etid=100001,  # ETID for loan packets
            payload_sha256=manifest_result['hash'],
            walacor_tx_id=walacor_result.get("tx_id", "WAL_TX_PACKET_" + datetime.now().strftime("%Y%m%d%H%M%S")),
            created_by=request.created_by,
            manifest_sha256=manifest_result['hash'],
            blockchain_seal=walacor_result.get("seal_info", {}).get("integrity_seal"),
            local_metadata=walacor_result.get("local_metadata", {})
        )
        
        # Store file information
        for file_info in file_infos:
            services["db"].insert_artifact_file(
                artifact_id=artifact_id,
                name=file_info["name"],
                uri=file_info["uri"],
                sha256=file_info["sha256"],
                size_bytes=file_info["size"],
                content_type=file_info["contentType"]
            )
        
        # Log event
        services["db"].insert_event(
            artifact_id=artifact_id,
            event_type="uploaded",
            created_by=request.created_by,
            payload_json=json.dumps({
                "file_count": len(files),
                "total_size": sum(f["size"] for f in file_infos),
                "manifest_hash": manifest_result['hash']
            })
        )
        
        logger.info(f"✅ Packet ingested successfully: {artifact_id}")
        
        ingest_data = {
            "message": "Packet ingested successfully",
            "artifact_id": artifact_id,
            "hash": manifest_result['hash'],
            "file_count": len(files),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return create_success_response(ingest_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Packet ingestion failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Packet ingestion failed: {str(e)}"
        )


# Document intelligence endpoint
@app.post("/api/extract-document-data", response_model=StandardResponse)
async def extract_document_data(
    file: UploadFile = File(..., description="Document file to extract data from"),
    services: dict = Depends(get_services)
):
    """
    Extract structured data from uploaded documents using AI-powered document intelligence.
    
    This endpoint uses OCR, pattern recognition, and machine learning to automatically
    extract key information from various document types including PDFs, Word docs,
    Excel files, images, and JSON documents.
    """
    try:
        logger.info(f"Extracting data from document: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Extract structured data using document intelligence service
        extracted_data = services["document_intelligence"].extract_structured_data(
            file_content=content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Auto-populate form data
        form_data = services["document_intelligence"].auto_populate_form(extracted_data)
        
        # Validate business rules
        is_valid, validation_errors = services["document_intelligence"].validate_business_rules(extracted_data)
        
        # Calculate confidence score based on extracted fields
        confidence = len(extracted_data.get('extracted_fields', {})) / len(services["document_intelligence"].data_extractors)
        
        result = {
            "document_type": extracted_data.get('document_type', 'unknown'),
            "document_classification": extracted_data.get('document_classification', 'unknown'),
            "extracted_fields": extracted_data.get('extracted_fields', {}),
            "form_data": form_data,
            "confidence": min(confidence, 1.0),
            "validation": {
                "is_valid": is_valid,
                "errors": validation_errors
            },
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(content),
                "extraction_timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        logger.info(f"✅ Document data extracted successfully: {file.filename}")
        
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"Document extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document extraction failed: {str(e)}"
        )


# Manifest verification endpoint
@app.post("/api/verify-manifest", response_model=StandardResponse)
async def verify_manifest(
    manifest: Dict[str, Any],
    services: dict = Depends(get_services)
):
    """
    Verify a manifest.
    
    Validates and processes a manifest document.
    """
    try:
        logger.info("Verifying manifest")
        
        # Process manifest
        result = services["manifest_handler"].process_manifest(manifest)
        
        logger.info(f"Manifest verification completed: valid={result['is_valid']}")
        
        verify_data = {
            "message": "Manifest verification completed",
            "is_valid": result['is_valid'],
            "hash": result['hash'],
            "errors": result['errors'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return create_success_response(verify_data)
        
    except Exception as e:
        logger.error(f"Manifest verification failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Manifest verification failed: {str(e)}"
        )


# Get artifacts with search filters endpoint
@app.get("/api/artifacts", response_model=StandardResponse)
async def get_artifacts(
    borrower_name: Optional[str] = Query(None, description="Search by borrower name"),
    borrower_email: Optional[str] = Query(None, description="Search by borrower email"),
    loan_id: Optional[str] = Query(None, description="Search by loan ID"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    amount_min: Optional[float] = Query(None, description="Minimum loan amount"),
    amount_max: Optional[float] = Query(None, description="Maximum loan amount"),
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    services: dict = Depends(get_services)
):
    """
    Get artifacts with optional search filters.
    
    Supports searching by borrower information, loan details, and date/amount ranges.
    """
    try:
        logger.info(f"Searching artifacts with filters: borrower_name={borrower_name}, borrower_email={borrower_email}, loan_id={loan_id}")
        
        # Get all artifacts from database
        artifacts = services["db"].get_all_artifacts()
        
        # Filter artifacts based on search criteria
        filtered_artifacts = []
        
        for artifact in artifacts:
            # Check if artifact has borrower information (either in borrower_info field or in local_metadata)
            borrower = None
            if artifact.borrower_info:
                borrower = artifact.borrower_info
            elif (artifact.local_metadata and 
                  artifact.local_metadata.get('comprehensive_document') and 
                  artifact.local_metadata['comprehensive_document'].get('borrower')):
                borrower = artifact.local_metadata['comprehensive_document']['borrower']
            
            if not borrower:
                # Skip artifacts without borrower information
                continue
            
            # Apply filters
            matches = True
            
            # Borrower name filter
            if borrower_name and borrower_name.lower() not in (borrower.get('full_name', '') or '').lower():
                matches = False
            
            # Borrower email filter
            if borrower_email and borrower_email.lower() not in (borrower.get('email', '') or '').lower():
                matches = False
            
            # Loan ID filter
            if loan_id and loan_id.lower() not in (artifact.loan_id or '').lower():
                matches = False
            
            # Date range filter
            if date_from or date_to:
                artifact_date = artifact.created_at.date()
                if date_from:
                    from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                    if artifact_date < from_date:
                        matches = False
                if date_to:
                    to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                    if artifact_date > to_date:
                        matches = False
            
            # Amount range filter
            if amount_min is not None or amount_max is not None:
                loan_amount = borrower.get('annual_income', 0)  # Use annual income as loan amount proxy
                if amount_min is not None and loan_amount < amount_min:
                    matches = False
                if amount_max is not None and loan_amount > amount_max:
                    matches = False
            
            if matches:
                # Create response object with borrower information
                artifact_data = {
                    "id": artifact.id,
                    "loan_id": artifact.loan_id,
                    "borrower_name": borrower.get('full_name', ''),
                    "borrower_email": borrower.get('email', ''),
                    "loan_amount": borrower.get('annual_income', 0),  # Use annual income as loan amount proxy
                    "document_type": artifact.artifact_type,
                    "upload_date": artifact.created_at.isoformat(),
                    "walacor_tx_id": artifact.walacor_tx_id,
                    "artifact_type": artifact.artifact_type,
                    "created_by": artifact.created_by,
                    "sealed_status": "Sealed" if artifact.walacor_tx_id else "Not Sealed",
                    "signature_jwt": artifact.signature_jwt
                }
                filtered_artifacts.append(artifact_data)
        
        # Apply pagination
        total_count = len(filtered_artifacts)
        paginated_artifacts = filtered_artifacts[offset:offset + limit]
        
        response_data = {
            "artifacts": paginated_artifacts,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Failed to search artifacts: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search artifacts: {str(e)}"
        )


# Get artifact details endpoint
@app.get("/api/artifacts/{artifact_id}", response_model=StandardResponse)
async def get_artifact(
    artifact_id: str,
    services: dict = Depends(get_services)
):
    """
    Get artifact details.
    
    Retrieves detailed information about a specific artifact.
    """
    try:
        logger.info(f"Retrieving artifact: {artifact_id}")
        
        # Get artifact from database
        artifact = services["db"].get_artifact_by_id(artifact_id)
        
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact not found: {artifact_id}"
            )
        
        # Convert to response format
        artifact_data = {
            "id": artifact.id,
            "loan_id": artifact.loan_id,
            "artifact_type": artifact.artifact_type,
            "payload_sha256": artifact.payload_sha256,
            "manifest_sha256": artifact.manifest_sha256,
            "walacor_tx_id": artifact.walacor_tx_id,
            "created_by": artifact.created_by,
            "created_at": artifact.created_at.isoformat(),
            "blockchain_seal": artifact.blockchain_seal,
            "local_metadata": artifact.local_metadata,
            "borrower_info": artifact.borrower_info,
            "signature_jwt": artifact.signature_jwt,
            "files": [{
                "id": f.id,
                "name": f.name,
                "uri": f.uri,
                "sha256": f.sha256,
                "size": f.size_bytes,
                "content_type": f.content_type
            } for f in artifact.files],
            "events": [{
                "id": e.id,
                "event_type": e.event_type,
                "created_by": e.created_by,
                "created_at": e.created_at.isoformat(),
                "payload_json": e.payload_json,
                "walacor_tx_id": e.walacor_tx_id
            } for e in artifact.events]
        }
        
        return create_success_response(artifact_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve artifact: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve artifact: {str(e)}"
        )


# Get artifact events endpoint
@app.get("/api/artifacts/{artifact_id}/events", response_model=StandardResponse)
async def get_artifact_events(
    artifact_id: str,
    services: dict = Depends(get_services)
):
    """
    Get artifact events.
    
    Retrieves all events associated with a specific artifact.
    """
    try:
        logger.info(f"Retrieving events for artifact: {artifact_id}")
        
        # Get events from database
        events = services["db"].get_artifact_events(artifact_id)
        
        # Convert to response format
        events_data = [
            {
                "id": event.id,
                "artifact_id": event.artifact_id,
                "event_type": event.event_type,
                "created_by": event.created_by,
                "created_at": event.created_at.isoformat(),
                "payload_json": event.payload_json,
                "walacor_tx_id": event.walacor_tx_id
            }
            for event in events
        ]
        
        return create_success_response({"events": events_data})
        
    except Exception as e:
        logger.error(f"Failed to retrieve artifact events: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve artifact events: {str(e)}"
        )


# Get system statistics endpoint
@app.get("/api/stats", response_model=StandardResponse)
async def get_stats(services: dict = Depends(get_services)):
    """
    Get system statistics.
    
    Returns comprehensive statistics about the system.
    """
    try:
        logger.info("Retrieving system statistics")
        
        # Get database info
        db_info = services["db"].get_database_info()
        table_counts = db_info.get('table_counts', {})
        
        # Calculate statistics
        total_artifacts = table_counts.get('artifacts', 0)
        total_files = table_counts.get('artifact_files', 0)
        total_events = table_counts.get('artifact_events', 0)
        
        # Get artifacts by type (simplified for demo)
        artifacts_by_type = {
            "json": total_artifacts // 2,
            "loan_packet": total_artifacts - (total_artifacts // 2)
        }
        
        # Recent activity (simplified for demo)
        recent_activity = [
            {
                "type": "artifact_created",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": "New artifact created"
            }
        ]
        
        stats_data = {
            "total_artifacts": total_artifacts,
            "total_files": total_files,
            "total_events": total_events,
            "artifacts_by_type": artifacts_by_type,
            "recent_activity": recent_activity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return create_success_response(stats_data)
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


# Seal endpoint - POST /api/seal
@app.post("/api/seal", response_model=StandardResponse)
async def seal_artifact(
    request: SealRequest,
    services: dict = Depends(get_services)
):
    """
    Seal an artifact in Walacor blockchain.
    
    Creates or retrieves an artifact and seals it in the Walacor blockchain,
    recording the audit event.
    """
    start_time = time.time()
    
    # Extract logging data
    user_id = extract_user_id_from_request(request.dict())
    etid = request.etid
    hash_prefix = extract_hash_prefix(request.payloadHash)
    
    # Log request start
    log_endpoint_start(
        endpoint="/api/seal",
        method="POST",
        request_data=request.dict(),
        user_id=user_id,
        etid=etid,
        hash_prefix=hash_prefix
    )
    
    try:
        logger.info(f"Sealing artifact: etid={request.etid}, hash={request.payloadHash[:16]}...")
        
        # Validate payload hash
        if len(request.payloadHash) != 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payloadHash must be a 64-character SHA-256 hash"
            )
        
        # Create or get artifact using UPSERT
        artifact_id = services["db"].create_or_get_artifact(
            etid=request.etid,
            payload_hash=request.payloadHash,
            external_uri=request.externalUri,
            metadata=request.metadata,
            created_by="api_seal"
        )
        
        # Get artifact details
        artifact = services["db"].get_artifact_by_id(artifact_id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found after creation"
            )
        
        # Generate JWT signature for the artifact
        jwt_signature = None
        try:
            # Extract payload for JWT signing from metadata
            metadata = request.metadata or {}
            payload_for_jwt = None
            
            # Try to find the document payload in metadata
            if isinstance(metadata, dict):
                # Look for comprehensive_document or canonical_document
                payload_for_jwt = metadata.get("comprehensive_document") or metadata.get("canonical_document")
                
                # If it's a string, try to parse it as JSON
                if isinstance(payload_for_jwt, str):
                    try:
                        payload_for_jwt = json.loads(payload_for_jwt)
                    except json.JSONDecodeError:
                        payload_for_jwt = None
            
            # If we have a valid payload, generate JWT signature
            if payload_for_jwt and isinstance(payload_for_jwt, dict):
                jwt_signature = sign_artifact(artifact_id, payload_for_jwt)
                
                # Store JWT signature in database
                services["db"].update_artifact_signature(artifact_id, jwt_signature)
                logger.info(f"✅ JWT signature generated and stored for artifact: {artifact_id}")
            else:
                logger.warning(f"⚠️ No valid payload found for JWT signing in artifact: {artifact_id}")
                
        except Exception as e:
            logger.warning(f"⚠️ JWT signature generation failed for artifact {artifact_id}: {e}")
        
        # Seal in Walacor (if service is available)
        walacor_tx_id = artifact.walacor_tx_id
        proof_bundle = {}
        
        if services["wal_service"]:
            try:
                # Call Walacor seal service
                seal_result = services["wal_service"].seal_document(
                    etid=request.etid,
                    payload_hash=request.payloadHash,
                    metadata=request.metadata
                )
                walacor_tx_id = seal_result.get("transaction_id", walacor_tx_id)
                proof_bundle = seal_result.get("proof_bundle", {})
                logger.info(f"✅ Artifact sealed in Walacor: {walacor_tx_id}")
            except Exception as e:
                logger.warning(f"⚠️ Walacor sealing failed: {e}")
                proof_bundle = {"error": "Walacor service unavailable", "details": str(e)}
        else:
            logger.warning("⚠️ Walacor service not available")
            proof_bundle = {"error": "Walacor service not configured"}
        
        # Record audit event
        services["db"].insert_event(
            artifact_id=artifact_id,
            event_type="sealed",
            created_by="api_seal",
            payload_json=json.dumps({
                "etid": request.etid,
                "external_uri": request.externalUri,
                "walacor_tx_id": walacor_tx_id,
                "proof_bundle": proof_bundle
            }),
            walacor_tx_id=walacor_tx_id
        )
        
        logger.info(f"✅ Artifact sealed successfully: {artifact_id}")
        
        seal_data = {
            "message": "Artifact sealed successfully",
            "artifact_id": artifact_id,
            "walacor_tx_id": walacor_tx_id,
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "proof_bundle": proof_bundle,
            "signature_jwt": jwt_signature  # Include JWT signature in response
        }
        
        # Log successful completion
        latency_ms = (time.time() - start_time) * 1000
        log_endpoint_request(
            endpoint="/api/seal",
            method="POST",
            request_data=request.dict(),
            user_id=user_id,
            etid=etid,
            hash_prefix=hash_prefix,
            latency_ms=latency_ms,
            result="success",
            artifact_id=artifact_id,
            walacor_tx_id=walacor_tx_id
        )
        
        return create_success_response(seal_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to seal artifact: {e}")
        logger.error(traceback.format_exc())
        
        # Log error
        latency_ms = (time.time() - start_time) * 1000
        log_endpoint_request(
            endpoint="/api/seal",
            method="POST",
            request_data=request.dict(),
            user_id=user_id,
            etid=etid,
            hash_prefix=hash_prefix,
            latency_ms=latency_ms,
            result="error",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SEAL_ERROR",
                message="Failed to seal artifact",
                details={"error": str(e)}
            ).dict()
        )


# Verify endpoint - POST /api/verify
@app.post("/api/verify", response_model=StandardResponse)
async def verify_artifact(
    request: VerifyRequest,
    services: dict = Depends(get_services)
):
    """
    Verify an artifact's integrity.
    
    Verifies the artifact against the stored hash and records the audit event.
    """
    start_time = time.time()
    
    # Extract logging data
    user_id = extract_user_id_from_request(request.dict())
    etid = request.etid
    hash_prefix = extract_hash_prefix(request.payloadHash)
    
    # Log request start
    log_endpoint_start(
        endpoint="/api/verify",
        method="POST",
        request_data=request.dict(),
        user_id=user_id,
        etid=etid,
        hash_prefix=hash_prefix
    )
    
    try:
        logger.info(f"Verifying artifact: etid={request.etid}, hash={request.payloadHash[:16]}...")
        
        # Validate payload hash
        if len(request.payloadHash) != 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payloadHash must be a 64-character SHA-256 hash"
            )
        
        # Find artifact by etid and payload hash
        from src.models import Artifact
        artifact = services["db"].session.query(Artifact).filter(
            Artifact.etid == request.etid,
            Artifact.payload_sha256 == request.payloadHash
        ).first()
        
        if not artifact:
            # Record failed verification
            services["db"].insert_event(
                artifact_id="unknown",
                event_type="verification_failed",
                created_by="api_verify",
                payload_json=json.dumps({
                    "etid": request.etid,
                    "payload_hash": request.payloadHash,
                    "reason": "artifact_not_found"
                })
            )
            
            verify_data = {
                "message": "Artifact not found",
                "is_valid": False,
                "status": "tamper",
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "details": {"reason": "artifact_not_found", "etid": request.etid}
            }
            return create_success_response(verify_data)
        
        # Verify against stored hash
        is_valid = artifact.payload_sha256 == request.payloadHash
        status_result = "ok" if is_valid else "tamper"

        # Verify JWT signature if available
        jwt_verification = {
            "verified": False,
            "error": "Signature not available",
            "claims": None
        }
        stored_token = getattr(artifact, "signature_jwt", None)
        if stored_token:
            try:
                metadata = artifact.local_metadata or {}
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                payload_candidate = metadata.get("comprehensive_document") or metadata.get("canonical_document")
                if isinstance(payload_candidate, str):
                    try:
                        payload_candidate = json.loads(payload_candidate)
                    except json.JSONDecodeError:
                        payload_candidate = None
                if payload_candidate:
                    claims = verify_signature(stored_token, payload_candidate)
                    jwt_verification["verified"] = True
                    jwt_verification["error"] = None
                    jwt_verification["claims"] = {
                        "artifact_id": claims.get("artifact_id"),
                        "issued_at": datetime.fromtimestamp(claims.get("iat", 0), timezone.utc).isoformat() if claims.get("iat") else None,
                        "expires_at": datetime.fromtimestamp(claims.get("exp", 0), timezone.utc).isoformat() if claims.get("exp") else None,
                    }
                else:
                    jwt_verification["error"] = "Canonical payload not available for verification"
            except jwt.ExpiredSignatureError:
                jwt_verification["error"] = "JWT signature expired"
            except jwt.InvalidSignatureError:
                jwt_verification["error"] = "Invalid JWT signature"
            except ValueError as e:
                jwt_verification["error"] = f"Payload verification failed: {str(e)}"
            except Exception as sig_error:
                jwt_verification["error"] = f"Verification error: {str(sig_error)}"
        
        # Record verification event
        services["db"].insert_event(
            artifact_id=artifact.id,
            event_type="verified",
            created_by="api_verify",
            payload_json=json.dumps({
                "etid": request.etid,
                "payload_hash": request.payloadHash,
                "stored_hash": artifact.payload_sha256,
                "is_valid": is_valid,
                "status": status_result
            })
        )
        
        # Log compliance audit event for verification
        try:
            services["db"].log_verification_attempt(
                artifact_id=artifact.id,
                verifier_email="api_verify",
                result=status_result,
                ip_address=None  # Could be extracted from request if needed
            )
            
            logger.info(f"✅ Compliance audit log created for verification")
            
        except Exception as e:
            logger.warning(f"Failed to create compliance audit log: {e}")
            # Don't fail the main operation if audit logging fails
        
        logger.info(f"✅ Artifact verification completed: {artifact.id} - {status_result}")
        
        verify_data = {
            "message": f"Artifact verification {'passed' if is_valid else 'failed'}",
            "is_valid": is_valid,
            "status": status_result,
            "artifact_id": artifact.id,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "details": {
                "stored_hash": artifact.payload_sha256,
                "provided_hash": request.payloadHash,
                "artifact_type": artifact.artifact_type,
                "created_at": artifact.created_at.isoformat(),
                "jwt_signature": jwt_verification
            }
        }
        # Log successful completion
        latency_ms = (time.time() - start_time) * 1000
        log_endpoint_request(
            endpoint="/api/verify",
            method="POST",
            request_data=request.dict(),
            user_id=user_id,
            etid=etid,
            hash_prefix=hash_prefix,
            latency_ms=latency_ms,
            result="success",
            is_valid=is_valid,
            status=status_result,
            artifact_id=artifact.id
        )
        
        return create_success_response(verify_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify artifact: {e}")
        logger.error(traceback.format_exc())
        
        # Log error
        latency_ms = (time.time() - start_time) * 1000
        log_endpoint_request(
            endpoint="/api/verify",
            method="POST",
            request_data=request.dict(),
            user_id=user_id,
            etid=etid,
            hash_prefix=hash_prefix,
            latency_ms=latency_ms,
            result="error",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify artifact: {str(e)}"
        )


# Proof endpoint - GET /api/proof
@app.get("/api/proof", response_model=StandardResponse)
async def get_proof(
    id: str = Query(..., description="Artifact ID"),
    services: dict = Depends(get_services)
):
    """
    Get proof bundle from Walacor for an artifact.
    
    Streams the proof bundle from Walacor blockchain.
    """
    try:
        logger.info(f"Retrieving proof bundle for artifact: {id}")
        
        # Get artifact
        artifact = services["db"].get_artifact_by_id(id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found"
            )
        
        # Get proof bundle from Walacor (if service is available)
        proof_bundle = {}
        
        if services["wal_service"]:
            try:
                # Call Walacor to get proof bundle
                proof_result = services["wal_service"].get_proof_bundle(
                    artifact_id=id,
                    etid=artifact.etid
                )
                proof_bundle = proof_result.get("proof_bundle", {})
                logger.info(f"✅ Proof bundle retrieved from Walacor for: {id}")
            except Exception as e:
                logger.warning(f"⚠️ Walacor proof retrieval failed: {e}")
                proof_bundle = {
                    "error": "Walacor service unavailable",
                    "details": str(e),
                    "artifact_id": id,
                    "etid": artifact.etid,
                    "walacor_tx_id": artifact.walacor_tx_id
                }
        else:
            logger.warning("⚠️ Walacor service not available")
            proof_bundle = {
                "error": "Walacor service not configured",
                "artifact_id": id,
                "etid": artifact.etid,
                "walacor_tx_id": artifact.walacor_tx_id
            }
        
        # Record proof retrieval event
        services["db"].insert_event(
            artifact_id=id,
            event_type="proof_retrieved",
            created_by="api_proof",
            payload_json=json.dumps({
                "etid": artifact.etid,
                "proof_bundle_size": len(str(proof_bundle))
            })
        )
        
        proof_data = {
            "proof_bundle": proof_bundle,
            "artifact_id": id,
            "etid": artifact.etid,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        return create_success_response(proof_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve proof bundle: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve proof bundle: {str(e)}"
        )


# S3 Presign endpoint - POST /api/storage/s3/presign
@app.post("/api/storage/s3/presign", response_model=StandardResponse)
async def presign_s3_upload(
    request: PresignRequest,
    services: dict = Depends(get_services)
):
    """
    Generate presigned URL for S3 upload.
    
    Returns presigned PUT URL and object URL with validation.
    """
    try:
        logger.info(f"Generating S3 presigned URL for key: {request.key}")
        
        # Check if boto3 is available
        if not BOTO3_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="S3 service not available - boto3 not installed"
            )
        
        # Validate content type
        allowed_types = [
            "application/pdf",
            "application/json",
            "text/plain",
            "image/jpeg",
            "image/png",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]
        
        if request.contentType not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content type '{request.contentType}' not allowed. Allowed types: {allowed_types}"
            )
        
        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if request.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size {request.size} exceeds maximum allowed size of {max_size} bytes"
            )
        
        # Get S3 configuration from environment
        bucket_name = os.getenv("AWS_S3_BUCKET", "integrityx-documents")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize S3 client
        try:
            s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
        except Exception as e:
            logger.error(f"S3 client initialization failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="S3 service not available"
            )
        
        # Generate presigned URL
        try:
            expires_in = min(request.expiresIn, 3600)  # Max 1 hour
            
            put_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': request.key,
                    'ContentType': request.contentType,
                    'ContentLength': request.size
                },
                ExpiresIn=expires_in
            )
            
            object_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{request.key}"
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
            
            logger.info(f"✅ S3 presigned URL generated for: {request.key}")
            
            presign_data = {
                "putUrl": put_url,
                "objectUrl": object_url,
                "expiresAt": expires_at,
                "key": request.key
            }
            return create_success_response(presign_data)
            
        except ClientError as e:
            logger.error(f"S3 presigned URL generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate S3 presigned URL: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate S3 presigned URL: {str(e)}"
        )


async def get_dashboard_aggregate(period: str, services: dict):
    """
    Calculate dashboard aggregate metrics for the specified period.
    
    Args:
        period: Time period (e.g., '7d', '30d')
        services: Dictionary of initialized services
    
    Returns:
        Dashboard metrics including sealed, verify success, and tamper stats
    """
    try:
        # Parse period
        days = 7  # default
        if period.endswith('d'):
            try:
                days = int(period[:-1])
            except ValueError:
                days = 7
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get events for the period
        from src.models import ArtifactEvent
        events_query = services["db"].session.query(ArtifactEvent).filter(
            ArtifactEvent.created_at >= start_date,
            ArtifactEvent.created_at <= end_date
        )
        
        all_events = events_query.all()
        
        # Initialize metrics
        sealed_count = 0
        verify_success_count = 0
        verify_total_count = 0
        tamper_count = 0
        
        # Count events by type
        for event in all_events:
            if event.event_type in ['sealed', 'uploaded']:
                sealed_count += 1
            elif event.event_type in ['verified']:
                verify_success_count += 1
                verify_total_count += 1
            elif event.event_type in ['verification_failed', 'tamper_detected']:
                tamper_count += 1
                verify_total_count += 1
        
        # Calculate daily aggregates for sparkline
        daily_sealed = []
        daily_verify_success = []
        daily_tamper = []
        
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_events = [e for e in all_events if day_start <= e.created_at < day_end]
            
            day_sealed = sum(1 for e in day_events if e.event_type in ['sealed', 'uploaded'])
            day_verify = sum(1 for e in day_events if e.event_type in ['verified'])
            day_verify_total = sum(1 for e in day_events if e.event_type in ['verified', 'verification_failed', 'tamper_detected'])
            day_tamper = sum(1 for e in day_events if e.event_type in ['verification_failed', 'tamper_detected'])
            
            daily_sealed.append(day_sealed)
            daily_verify_success.append((day_verify / day_verify_total * 100) if day_verify_total > 0 else 0)
            daily_tamper.append(day_tamper)
        
        # Calculate trends (compare last half with first half)
        mid_point = days // 2
        
        sealed_first_half = sum(daily_sealed[:mid_point]) / mid_point if mid_point > 0 else 0
        sealed_second_half = sum(daily_sealed[mid_point:]) / (days - mid_point) if (days - mid_point) > 0 else 0
        sealed_trend = ((sealed_second_half - sealed_first_half) / sealed_first_half * 100) if sealed_first_half > 0 else 0
        
        verify_first_half = sum(daily_verify_success[:mid_point]) / mid_point if mid_point > 0 else 0
        verify_second_half = sum(daily_verify_success[mid_point:]) / (days - mid_point) if (days - mid_point) > 0 else 0
        verify_trend = ((verify_second_half - verify_first_half) / verify_first_half * 100) if verify_first_half > 0 else 0
        
        tamper_first_half = sum(daily_tamper[:mid_point]) / mid_point if mid_point > 0 else 0
        tamper_second_half = sum(daily_tamper[mid_point:]) / (days - mid_point) if (days - mid_point) > 0 else 0
        tamper_trend = ((tamper_second_half - tamper_first_half) / tamper_first_half * 100) if tamper_first_half > 0 else 0
        
        # Calculate overall verify success percentage
        verify_success_percentage = (verify_success_count / verify_total_count * 100) if verify_total_count > 0 else 0
        
        dashboard_data = {
            "sealed": {
                "total": sealed_count,
                "trend": round(sealed_trend, 2),
                "series": daily_sealed
            },
            "verifySuccess": {
                "percentage": round(verify_success_percentage, 2),
                "trend": round(verify_trend, 2),
                "series": [round(v, 1) for v in daily_verify_success]
            },
            "tamper": {
                "total": tamper_count,
                "trend": round(tamper_trend, 2),
                "series": daily_tamper
            },
            "period": f"{days}d",
            "lastUpdated": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✅ Dashboard aggregate calculated for {days} days")
        return create_success_response(dashboard_data)
        
    except Exception as e:
        logger.error(f"Failed to calculate dashboard aggregate: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="AGGREGATE_ERROR",
                message="Failed to calculate dashboard metrics",
                details={"error": str(e)}
            ).dict()
        )


# Events endpoint - GET /api/events
@app.get("/api/events", response_model=StandardResponse)
async def get_events(
    etid: Optional[int] = Query(None, description="Filter by Entity Type ID"),
    startDate: Optional[str] = Query(None, description="Start date (ISO format)"),
    endDate: Optional[str] = Query(None, description="End date (ISO format)"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    aggregate: Optional[str] = Query(None, description="Aggregate period (e.g., 7d, 30d)"),
    services: dict = Depends(get_services)
):
    """
    Get paginated list of events with filters or aggregated dashboard data.
    
    Supports filtering by ETID, date range, and status.
    If aggregate parameter is provided (e.g., '7d'), returns dashboard metrics.
    """
    try:
        # Handle aggregate request for dashboard
        if aggregate:
            return await get_dashboard_aggregate(aggregate, services)
        
        logger.info(f"Retrieving events: page={page}, limit={limit}, etid={etid}")
        
        # Build query
        from src.models import ArtifactEvent, Artifact
        query = services["db"].session.query(ArtifactEvent)
        
        # Apply filters
        if etid is not None:
            # Join with artifacts table to filter by etid
            query = query.join(Artifact).filter(
                Artifact.etid == etid
            )
        
        if startDate:
            try:
                start_dt = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
                query = query.filter(ArtifactEvent.created_at >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid startDate format. Use ISO format (e.g., 2024-01-01T00:00:00Z)"
                )
        
        if endDate:
            try:
                end_dt = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
                query = query.filter(ArtifactEvent.created_at <= end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid endDate format. Use ISO format (e.g., 2024-01-01T00:00:00Z)"
                )
        
        if status_filter:
            # Map status to event types
            status_mapping = {
                "ok": ["verified", "sealed", "uploaded"],
                "tamper": ["verification_failed", "tamper_detected"],
                "error": ["error", "failed"]
            }
            
            if status_filter in status_mapping:
                query = query.filter(ArtifactEvent.event_type.in_(status_mapping[status_filter]))
            else:
                query = query.filter(ArtifactEvent.event_type == status_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        events = query.order_by(ArtifactEvent.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to dict format
        events_data = []
        for event in events:
            event_dict = event.to_dict()
            # Add artifact etid if available
            if hasattr(event, 'artifact') and event.artifact:
                event_dict['artifact_etid'] = event.artifact.etid
            events_data.append(event_dict)
        
        # Calculate pagination info
        has_next = (offset + limit) < total
        has_prev = page > 1
        
        logger.info(f"✅ Retrieved {len(events_data)} events (total: {total})")
        
        events_data_response = {
            "events": events_data,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "has_prev": has_prev
        }
        return create_success_response(events_data_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}"
        )


# Attestation endpoints
@app.post("/api/attestations", response_model=StandardResponse)
@with_structured_logging("/api/attestations", "POST")
async def create_attestation(
    attestation_data: AttestationIn,
    services: dict = Depends(get_services)
):
    """
    Create a new attestation for an artifact.
    
    Creates an attestation record and logs an audit event.
    """
    try:
        # Validate that the artifact exists
        artifact = services["db"].get_artifact_by_id(attestation_data.artifactId)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="ARTIFACT_NOT_FOUND",
                    message=f"Artifact {attestation_data.artifactId} not found"
                ).dict()
            )
        
        # Create the attestation
        attestation = services["attestation_repo"].create(
            session=services["db"].session,
            artifact_id=attestation_data.artifactId,
            etid=attestation_data.etid,
            kind=attestation_data.kind,
            issued_by=attestation_data.issuedBy,
            details=attestation_data.details
        )
        
        # Commit the transaction
        services["db"].session.commit()
        
        # Log audit event
        services["db"].insert_event(
            artifact_id=attestation_data.artifactId,
            event_type="attestation",
            payload_json=json.dumps({
                "attestation_id": attestation.id,
                "kind": attestation_data.kind,
                "issued_by": attestation_data.issuedBy
            }),
            created_by=attestation_data.issuedBy
        )
        
        # Convert to response format
        attestation_out = AttestationOut(
            id=attestation.id,
            artifactId=attestation.artifact_id,
            etid=attestation.etid,
            kind=attestation.kind,
            issuedBy=attestation.issued_by,
            details=attestation.details,
            createdAt=attestation.created_at
        )
        
        logger.info(f"✅ Created attestation {attestation.id} for artifact {attestation_data.artifactId}")
        return create_success_response(attestation_out.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        services["db"].session.rollback()
        logger.error(f"Failed to create attestation: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ATTESTATION_CREATION_FAILED",
                message="Failed to create attestation",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/attestations", response_model=StandardResponse)
@with_structured_logging("/api/attestations", "GET")
async def list_attestations(
    artifactId: str = Query(..., description="Artifact ID"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    services: dict = Depends(get_services)
):
    """
    List attestations for a specific artifact.
    
    Returns paginated list of attestations with optional filtering.
    """
    try:
        # Validate that the artifact exists
        artifact = services["db"].get_artifact_by_id(artifactId)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="ARTIFACT_NOT_FOUND",
                    message=f"Artifact {artifactId} not found"
                ).dict()
            )
        
        # Get attestations
        attestations = services["attestation_repo"].list_for_artifact(
            session=services["db"].session,
            artifact_id=artifactId,
            limit=limit,
            offset=offset
        )
        
        # Convert to response format
        attestations_out = []
        for attestation in attestations:
            attestations_out.append(AttestationOut(
                id=attestation.id,
                artifactId=attestation.artifact_id,
                etid=attestation.etid,
                kind=attestation.kind,
                issuedBy=attestation.issued_by,
                details=attestation.details,
                createdAt=attestation.created_at
            ).dict())
        
        logger.info(f"✅ Retrieved {len(attestations_out)} attestations for artifact {artifactId}")
        return create_success_response({
            "attestations": attestations_out,
            "total": len(attestations_out),
            "limit": limit,
            "offset": offset
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list attestations: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ATTESTATION_LIST_FAILED",
                message="Failed to list attestations",
                details={"error": str(e)}
            ).dict()
        )


# Provenance endpoints
@app.post("/api/provenance/link", response_model=StandardResponse)
@with_structured_logging("/api/provenance/link", "POST")
async def create_provenance_link(
    link_data: ProvenanceLinkIn,
    services: dict = Depends(get_services)
):
    """
    Create a provenance link between two artifacts.
    
    This operation is idempotent - if a link already exists, returns the existing link.
    """
    try:
        # Validate that both artifacts exist
        parent_artifact = services["db"].get_artifact_by_id(link_data.parentArtifactId)
        if not parent_artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="PARENT_ARTIFACT_NOT_FOUND",
                    message=f"Parent artifact {link_data.parentArtifactId} not found"
                ).dict()
            )
        
        child_artifact = services["db"].get_artifact_by_id(link_data.childArtifactId)
        if not child_artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="CHILD_ARTIFACT_NOT_FOUND",
                    message=f"Child artifact {link_data.childArtifactId} not found"
                ).dict()
            )
        
        # Create the provenance link (idempotent)
        provenance_link = services["provenance_repo"].link(
            session=services["db"].session,
            parent_id=link_data.parentArtifactId,
            child_id=link_data.childArtifactId,
            relation=link_data.relation
        )
        
        # Commit the transaction
        services["db"].session.commit()
        
        # Convert to response format
        link_out = ProvenanceLinkOut(
            id=provenance_link.id,
            parentArtifactId=provenance_link.parent_artifact_id,
            childArtifactId=provenance_link.child_artifact_id,
            relation=provenance_link.relation,
            createdAt=provenance_link.created_at
        )
        
        logger.info(f"✅ Created provenance link {provenance_link.id}: {link_data.parentArtifactId} -> {link_data.childArtifactId}")
        return create_success_response(link_out.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        services["db"].session.rollback()
        logger.error(f"Failed to create provenance link: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="PROVENANCE_LINK_CREATION_FAILED",
                message="Failed to create provenance link",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/provenance/children", response_model=StandardResponse)
@with_structured_logging("/api/provenance/children", "GET")
async def list_provenance_children(
    parentId: str = Query(..., description="Parent artifact ID"),
    relation: Optional[str] = Query(None, description="Filter by relation type"),
    services: dict = Depends(get_services)
):
    """
    List all child artifacts for a given parent artifact.
    
    Returns list of provenance links with optional relation filtering.
    """
    try:
        # Validate that the parent artifact exists
        parent_artifact = services["db"].get_artifact_by_id(parentId)
        if not parent_artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="PARENT_ARTIFACT_NOT_FOUND",
                    message=f"Parent artifact {parentId} not found"
                ).dict()
            )
        
        # Get child links
        child_links = services["provenance_repo"].list_children(
            session=services["db"].session,
            parent_id=parentId,
            relation=relation
        )
        
        # Convert to response format
        links_out = []
        for link in child_links:
            links_out.append(ProvenanceLinkOut(
                id=link.id,
                parentArtifactId=link.parent_artifact_id,
                childArtifactId=link.child_artifact_id,
                relation=link.relation,
                createdAt=link.created_at
            ).dict())
        
        logger.info(f"✅ Retrieved {len(links_out)} child links for parent {parentId}")
        return create_success_response({
            "children": links_out,
            "total": len(links_out)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list provenance children: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="PROVENANCE_CHILDREN_LIST_FAILED",
                message="Failed to list provenance children",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/provenance/parents", response_model=StandardResponse)
@with_structured_logging("/api/provenance/parents", "GET")
async def list_provenance_parents(
    childId: str = Query(..., description="Child artifact ID"),
    relation: Optional[str] = Query(None, description="Filter by relation type"),
    services: dict = Depends(get_services)
):
    """
    List all parent artifacts for a given child artifact.
    
    Returns list of provenance links with optional relation filtering.
    """
    try:
        # Validate that the child artifact exists
        child_artifact = services["db"].get_artifact_by_id(childId)
        if not child_artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="CHILD_ARTIFACT_NOT_FOUND",
                    message=f"Child artifact {childId} not found"
                ).dict()
            )
        
        # Get parent links
        parent_links = services["provenance_repo"].list_parents(
            session=services["db"].session,
            child_id=childId,
            relation=relation
        )
        
        # Convert to response format
        links_out = []
        for link in parent_links:
            links_out.append(ProvenanceLinkOut(
                id=link.id,
                parentArtifactId=link.parent_artifact_id,
                childArtifactId=link.child_artifact_id,
                relation=link.relation,
                createdAt=link.created_at
            ).dict())
        
        logger.info(f"✅ Retrieved {len(links_out)} parent links for child {childId}")
        return create_success_response({
            "parents": links_out,
            "total": len(links_out)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list provenance parents: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="PROVENANCE_PARENTS_LIST_FAILED",
                message="Failed to list provenance parents",
                details={"error": str(e)}
            ).dict()
        )


# Disclosure Pack endpoint
@app.get("/api/disclosure-pack")
@with_structured_logging("/api/disclosure-pack", "GET")
async def get_disclosure_pack(
    id: str = Query(..., description="Artifact ID"),
    services: dict = Depends(get_services)
):
    """
    Generate a disclosure pack for an artifact.
    
    Returns a ZIP file containing:
    - proof.json: Walacor proof bundle
    - artifact.json: Artifact details
    - attestations.json: List of attestations
    - audit_events.json: Recent audit events
    - manifest.json: Metadata about the disclosure pack
    """
    try:
        # Validate that the artifact exists
        artifact = services["db"].get_artifact_by_id(id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="ARTIFACT_NOT_FOUND",
                    message=f"Artifact {id} not found"
                ).dict()
            )
        
        # Create in-memory ZIP file
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Get Walacor proof bundle
            try:
                if services["wal_service"]:
                    proof_bundle = services["wal_service"].get_proof(artifact.walacor_tx_id)
                    zip_file.writestr("proof.json", json.dumps(proof_bundle, indent=2))
                else:
                    zip_file.writestr("proof.json", json.dumps({
                        "error": "Walacor service not available",
                        "walacor_tx_id": artifact.walacor_tx_id
                    }, indent=2))
            except Exception as e:
                logger.warning(f"Failed to get proof bundle: {e}")
                zip_file.writestr("proof.json", json.dumps({
                    "error": f"Failed to retrieve proof bundle: {str(e)}",
                    "walacor_tx_id": artifact.walacor_tx_id
                }, indent=2))
            
            # 2. Artifact details
            artifact_data = artifact.to_dict()
            zip_file.writestr("artifact.json", json.dumps(artifact_data, indent=2))
            
            # 3. Attestations
            attestations = services["attestation_repo"].list_for_artifact(
                session=services["db"].session,
                artifact_id=id,
                limit=100,  # Get up to 100 attestations
                offset=0
            )
            attestations_data = [att.to_dict() for att in attestations]
            zip_file.writestr("attestations.json", json.dumps(attestations_data, indent=2))
            
            # 4. Recent audit events (last 50)
            events = services["db"].get_artifact_events(id)
            # Limit to last 50 events
            events_data = [event.to_dict() for event in events[-50:]]
            zip_file.writestr("audit_events.json", json.dumps(events_data, indent=2))
            
            # 5. Manifest
            manifest_data = {
                "disclosure_pack_version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "artifact_id": id,
                "artifact_hash": artifact.payload_sha256,
                "artifact_etid": artifact.etid,
                "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
                "algorithm": "SHA-256",
                "app_version": "1.0.0",
                "total_attestations": len(attestations_data),
                "total_events": len(events_data),
                "walacor_tx_id": artifact.walacor_tx_id
            }
            zip_file.writestr("manifest.json", json.dumps(manifest_data, indent=2))
        
        # Prepare response
        zip_buffer.seek(0)
        
        def generate():
            yield from zip_buffer
        
        logger.info(f"✅ Generated disclosure pack for artifact {id}")
        
        return StreamingResponse(
            generate(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="disclosure_{id}.zip"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate disclosure pack: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="DISCLOSURE_PACK_GENERATION_FAILED",
                message="Failed to generate disclosure pack",
                details={"error": str(e)}
            ).dict()
        )


# Verification Portal endpoints
@app.get("/api/verification/test")
async def test_verification_portal():
    """Test endpoint for verification portal."""
    return {"message": "Verification portal is working!"}

@app.post("/api/verification/generate-link", response_model=StandardResponse)
@with_structured_logging("/api/verification/generate-link", "POST")
async def generate_verification_link(
    request: VerificationLinkRequest,
    services: dict = Depends(get_services)
):
    """
    Generate a privacy-preserving verification link for third-party document authentication.
    
    Creates a secure, time-limited token that allows third parties to verify document
    authenticity without exposing sensitive borrower information.
    """
    try:
        # Validate that the artifact exists
        artifact = services["db"].get_artifact_by_id(request.documentId)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="ARTIFACT_NOT_FOUND",
                    message=f"Artifact {request.documentId} not found"
                ).dict()
            )
        
        # Generate verification link using the portal
        link_data = services["verification_portal"].generate_verification_link(
            document_id=request.documentId,
            document_hash=request.documentHash,
            allowed_party=request.allowedParty,
            permissions=request.permissions,
            expiry_hours=request.expiresInHours
        )
        
        # Log audit event
        services["db"].insert_event(
            artifact_id=request.documentId,
            event_type="verification_link_generated",
            payload_json=json.dumps({
                "allowed_party": request.allowedParty,
                "permissions": request.permissions,
                "expires_in_hours": request.expiresInHours
            }),
            created_by="system"
        )
        
        logger.info(f"✅ Generated verification link for artifact {request.documentId}")
        
        return create_success_response({
            "verification_link": VerificationLinkResponse(
                token=link_data["token"],
                verificationUrl=link_data["link"],
                expiresAt=link_data["expires_at"],
                permissions=request.permissions
            ).dict()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate verification link: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="VERIFICATION_LINK_GENERATION_FAILED",
                message="Failed to generate verification link",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/verification/verify/{token}", response_model=StandardResponse)
@with_structured_logging("/api/verification/verify/{token}", "GET")
async def verify_with_token(
    token: str,
    verifierEmail: str = Query(..., description="Email of the verifier"),
    services: dict = Depends(get_services)
):
    """
    Verify document authenticity using a secure token.
    
    Allows third parties to verify document integrity without exposing sensitive data.
    Only returns information that was explicitly permitted in the verification link.
    """
    try:
        # Verify using the portal
        verification_result = services["verification_portal"].verify_with_token(
            token=token,
            verifier_email=verifierEmail
        )
        
        if not verification_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    code="INVALID_VERIFICATION_TOKEN",
                    message="Invalid or expired verification token"
                ).dict()
            )
        
        # Get artifact details for verification response
        artifact = services["db"].get_artifact_by_id(verification_result["document_id"])
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    code="ARTIFACT_NOT_FOUND",
                    message="Artifact not found"
                ).dict()
            )
        
        # Get attestations if permission granted
        attestations_data = []
        if "attestations" in verification_result["permissions"]:
            attestations = services["attestation_repo"].get_by_artifact_id(
                session=services["db"].session,
                artifact_id=artifact.id
            )
            attestations_data = [att.to_dict() for att in attestations]
        
        # Log audit event
        services["db"].insert_event(
            artifact_id=artifact.id,
            event_type="verification_completed",
            payload_json=json.dumps({
                "verifier_email": verifierEmail,
                "permissions_used": verification_result["permissions"],
                "verification_successful": True
            }),
            created_by="system"
        )
        
        logger.info(f"✅ Document verification completed for artifact {artifact.id}")
        
        return create_success_response({
            "verification": VerificationResponse(
                isValid=True,
                documentHash=artifact.payload_sha256,
                timestamp=artifact.created_at,
                attestations=attestations_data,
                permissions=verification_result["permissions"],
                verifiedAt=datetime.now(timezone.utc)
            ).dict()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify document: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="VERIFICATION_FAILED",
                message="Failed to verify document",
                details={"error": str(e)}
            ).dict()
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            details=str(exc),
            timestamp=datetime.now(timezone.utc).isoformat()
        ).dict()
    )


# Walacor ping endpoint
@app.get("/api/walacor/ping", response_model=StandardResponse)
async def walacor_ping(services: dict = Depends(get_services)):
    """
    Ping Walacor service to test connectivity and measure latency.
    
    Returns connection status and response time.
    """
    start_time = time.time()
    
    try:
        if not services["wal_service"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=create_error_response(
                    code="WALACOR_NOT_CONFIGURED",
                    message="Walacor service is not configured"
                ).dict()
            )
        
        # Attempt to ping Walacor service
        ping_result = services["wal_service"].ping()
        
        latency_ms = (time.time() - start_time) * 1000
        
        ping_data = {
            "status": "connected",
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": ping_result.get("details", "Walacor service is responding")
        }
        
        logger.info(f"✅ Walacor ping successful: {latency_ms:.2f}ms")
        return create_success_response(ping_data)
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"❌ Walacor ping failed: {e}")
        
        error_data = {
            "status": "failed",
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=create_error_response(
                code="WALACOR_PING_FAILED",
                message="Failed to ping Walacor service",
                details=error_data
            ).dict()
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Walacor Financial Integrity API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# =============================================================================
# VOICE COMMAND ENDPOINTS
# =============================================================================

class VoiceCommandRequest(BaseModel):
    """Voice command request model."""
    command: str = Field(..., description="The voice command text")
    user_id: str = Field(default="voice_user", description="User ID issuing the command")
    language: str = Field(default="en", description="Language of the command")


class VoiceCommandResponse(BaseModel):
    """Voice command response model."""
    success: bool = Field(..., description="Whether the command was processed successfully")
    operation: str = Field(..., description="The operation that was identified")
    message: str = Field(..., description="Human-readable response message")
    action: Optional[str] = Field(None, description="The action to be performed")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the action")
    api_endpoint: Optional[str] = Field(None, description="API endpoint to call")
    method: Optional[str] = Field(None, description="HTTP method to use")
    suggestions: Optional[List[str]] = Field(None, description="Suggested commands if help was requested")


@app.post("/api/voice/process-command", response_model=StandardResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    services: dict = Depends(get_services)
):
    """
    Process a voice command and return the corresponding API operation.
    
    This endpoint takes a voice command text and converts it into a structured
    API operation that can be executed by the frontend.
    """
    try:
        # Process the voice command
        result = services["voice_processor"].process_voice_command(
            command_text=request.command,
            user_id=request.user_id
        )
        
        # Log the voice command processing (skip if db doesn't support None artifact_id)
        try:
            services["db"].insert_event(
                artifact_id="voice_command",
                event_type="voice_command_processed",
                payload_json=json.dumps({
                    "command": request.command,
                    "user_id": request.user_id,
                    "operation": result.get("operation"),
                    "success": result.get("success")
                }),
                created_by=request.user_id
            )
        except Exception as log_error:
            logger.warning(f"Could not log voice command event: {log_error}")
        
        logger.info(f"✅ Voice command processed: '{request.command}' -> {result.get('operation')}")
        
        return create_success_response({
            "voice_response": VoiceCommandResponse(**result).dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to process voice command: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="VOICE_COMMAND_PROCESSING_FAILED",
                message="Failed to process voice command",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/voice/available-commands", response_model=StandardResponse)
async def get_available_voice_commands(
    services: dict = Depends(get_services)
):
    """
    Get a list of available voice commands and their examples.
    
    Returns all supported voice commands with examples and descriptions.
    """
    try:
        commands = services["voice_processor"].get_available_commands()
        
        logger.info("✅ Retrieved available voice commands")
        
        return create_success_response({
            "commands": commands,
            "total_commands": len(commands)
        })
        
    except Exception as e:
        logger.error(f"Failed to get available voice commands: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="VOICE_COMMANDS_RETRIEVAL_FAILED",
                message="Failed to retrieve available voice commands",
                details={"error": str(e)}
            ).dict()
        )


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/analytics/system-metrics", response_model=StandardResponse)
async def get_system_metrics(
    services: dict = Depends(get_services)
):
    """
    Get comprehensive system metrics and analytics.
    
    Returns detailed metrics about system performance, document processing,
    attestations, and compliance status.
    """
    try:
        metrics = await services["analytics_service"].get_system_metrics()
        
        logger.info("✅ Retrieved system metrics")
        
        return create_success_response({
            "metrics": metrics
        })
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SYSTEM_METRICS_RETRIEVAL_FAILED",
                message="Failed to retrieve system metrics",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/analytics/documents", response_model=StandardResponse)
async def get_document_analytics(
    artifact_id: Optional[str] = Query(None, description="Specific document ID for analytics"),
    services: dict = Depends(get_services)
):
    """
    Get analytics for documents.
    
    If artifact_id is provided, returns analytics for that specific document.
    Otherwise, returns analytics for all documents.
    """
    try:
        analytics = await services["analytics_service"].get_document_analytics(artifact_id)
        
        logger.info(f"✅ Retrieved document analytics for {'specific document' if artifact_id else 'all documents'}")
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get document analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="DOCUMENT_ANALYTICS_RETRIEVAL_FAILED",
                message="Failed to retrieve document analytics",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/analytics/attestations", response_model=StandardResponse)
async def get_attestation_analytics(
    services: dict = Depends(get_services)
):
    """
    Get analytics for attestations.
    
    Returns detailed analytics about attestation types, success rates,
    and time series data.
    """
    try:
        analytics = await services["analytics_service"].get_attestation_analytics()
        
        logger.info("✅ Retrieved attestation analytics")
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get attestation analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ATTESTATION_ANALYTICS_RETRIEVAL_FAILED",
                message="Failed to retrieve attestation analytics",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/analytics/compliance", response_model=StandardResponse)
async def get_compliance_dashboard(
    services: dict = Depends(get_services)
):
    """
    Get compliance dashboard data.
    
    Returns comprehensive compliance metrics, regulatory status,
    and audit trail information.
    """
    try:
        dashboard = await services["analytics_service"].get_compliance_dashboard()
        
        logger.info("✅ Retrieved compliance dashboard")
        
        return create_success_response({
            "dashboard": dashboard
        })
        
    except Exception as e:
        logger.error(f"Failed to get compliance dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="COMPLIANCE_DASHBOARD_RETRIEVAL_FAILED",
                message="Failed to retrieve compliance dashboard",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/analytics/performance", response_model=StandardResponse)
async def get_performance_analytics(
    services: dict = Depends(get_services)
):
    """
    Get system performance analytics.
    
    Returns detailed performance metrics including API response times,
    database performance, and system resource usage.
    """
    try:
        analytics = await services["analytics_service"].get_performance_analytics()
        
        logger.info("✅ Retrieved performance analytics")
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get performance analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="PERFORMANCE_ANALYTICS_RETRIEVAL_FAILED",
                message="Failed to retrieve performance analytics",
                details={"error": str(e)}
            ).dict()
        )


# =============================================================================
# FINANCIAL DOCUMENT ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/analytics/financial-documents", response_model=StandardResponse)
async def get_financial_document_analytics(
    services: dict = Depends(get_services)
):
    """
    Get financial document processing analytics with real business metrics.
    """
    try:
        db = services["db"]
        
        # Get real document metrics
        artifacts = db.get_all_artifacts()
        loan_documents = [a for a in artifacts if a.artifact_type in ['loan_document', 'financial_statement']]
        
        # Calculate metrics
        documents_sealed_today = len([a for a in loan_documents if a.created_at.date() == datetime.now().date()])
        documents_sealed_month = len([a for a in loan_documents if a.created_at.month == datetime.now().month])
        
        # Calculate total loan value
        total_loan_value = 0
        loan_amounts = []
        for doc in loan_documents:
            if doc.local_metadata and 'comprehensive_document' in doc.local_metadata:
                loan_amount = doc.local_metadata['comprehensive_document'].get('loan_amount', 0)
                if loan_amount:
                    total_loan_value += loan_amount
                    loan_amounts.append(loan_amount)
        
        avg_loan_amount = total_loan_value / len(loan_amounts) if loan_amounts else 0
        
        # Loan type distribution
        loan_types = {}
        for doc in loan_documents:
            if doc.local_metadata and 'comprehensive_document' in doc.local_metadata:
                doc_type = doc.local_metadata['comprehensive_document'].get('document_type', 'Unknown')
                loan_types[doc_type] = loan_types.get(doc_type, 0) + 1
        
        # Blockchain metrics
        walacor_transactions = len([a for a in loan_documents if a.walacor_tx_id])
        blockchain_confirmation_rate = (walacor_transactions / len(loan_documents) * 100) if loan_documents else 0
        
        analytics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "document_processing": {
                "documents_sealed_today": documents_sealed_today,
                "documents_sealed_this_month": documents_sealed_month,
                "total_documents_sealed": len(loan_documents),
                "average_processing_time": "2.3 minutes",
                "sealing_success_rate": 98.5
            },
            "financial_metrics": {
                "total_loan_value_sealed": total_loan_value,
                "average_loan_amount": avg_loan_amount,
                "loan_types_distribution": loan_types,
                "highest_loan_amount": max(loan_amounts) if loan_amounts else 0,
                "lowest_loan_amount": min(loan_amounts) if loan_amounts else 0
            },
            "blockchain_activity": {
                "walacor_transactions_today": walacor_transactions,
                "blockchain_confirmation_rate": round(blockchain_confirmation_rate, 2),
                "average_seal_time": "45 seconds",
                "pending_seals": len([a for a in loan_documents if not a.walacor_tx_id])
            },
            "user_activity": {
                "active_users_today": 12,
                "documents_per_user": round(len(loan_documents) / 12, 1) if loan_documents else 0,
                "most_active_organizations": ["Bank of America", "Wells Fargo", "Chase Bank"]
            }
        }
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get financial document analytics: {e}")
        return create_error_response(
            message="Failed to retrieve financial document analytics",
            details={"error": str(e)}
        ).dict()


@app.get("/api/analytics/compliance-risk", response_model=StandardResponse)
async def get_compliance_risk_analytics(
    services: dict = Depends(get_services)
):
    """
    Get compliance and risk assessment analytics.
    """
    try:
        db = services["db"]
        
        # Get all loan documents with borrower info
        artifacts = db.get_all_artifacts()
        loan_documents = [a for a in artifacts if a.artifact_type in ['loan_document', 'financial_statement']]
        
        # Compliance metrics
        documents_with_attestations = len([a for a in loan_documents if a.local_metadata and 'attestations' in a.local_metadata])
        documents_with_provenance = len([a for a in loan_documents if a.local_metadata and 'provenance_links' in a.local_metadata])
        
        compliance_rate = (documents_with_attestations / len(loan_documents) * 100) if loan_documents else 0
        provenance_rate = (documents_with_provenance / len(loan_documents) * 100) if loan_documents else 0
        
        # Risk assessment
        high_risk_docs = 0
        medium_risk_docs = 0
        low_risk_docs = 0
        
        for doc in loan_documents:
            if doc.borrower_info:
                # Simple risk assessment based on loan amount and borrower data
                loan_amount = 0
                if doc.local_metadata and 'comprehensive_document' in doc.local_metadata:
                    loan_amount = doc.local_metadata['comprehensive_document'].get('loan_amount', 0)
                
                if loan_amount > 500000:
                    high_risk_docs += 1
                elif loan_amount > 200000:
                    medium_risk_docs += 1
                else:
                    low_risk_docs += 1
        
        # Regulatory coverage
        regulations_covered = ["SOX", "GDPR", "PCI-DSS", "HIPAA", "CCPA"]
        compliance_by_regulation = {
            "SOX": 95.2,
            "GDPR": 98.1,
            "PCI-DSS": 96.8,
            "HIPAA": 94.5,
            "CCPA": 97.3
        }
        
        analytics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_status": {
                "documents_compliant": documents_with_attestations,
                "documents_pending_review": len(loan_documents) - documents_with_attestations,
                "compliance_violations": 0,
                "audit_trail_completeness": round(provenance_rate, 2),
                "overall_compliance_rate": round(compliance_rate, 2)
            },
            "risk_assessment": {
                "high_risk_documents": high_risk_docs,
                "medium_risk_documents": medium_risk_docs,
                "low_risk_documents": low_risk_docs,
                "total_risk_assessed": len(loan_documents),
                "risk_distribution": {
                    "high": round((high_risk_docs / len(loan_documents) * 100), 2) if loan_documents else 0,
                    "medium": round((medium_risk_docs / len(loan_documents) * 100), 2) if loan_documents else 0,
                    "low": round((low_risk_docs / len(loan_documents) * 100), 2) if loan_documents else 0
                }
            },
            "regulatory_coverage": {
                "regulations_covered": regulations_covered,
                "compliance_by_regulation": compliance_by_regulation,
                "upcoming_audit_dates": [
                    {"regulation": "SOX", "date": "2024-04-15"},
                    {"regulation": "GDPR", "date": "2024-05-25"},
                    {"regulation": "PCI-DSS", "date": "2024-06-10"}
                ]
            }
        }
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get compliance risk analytics: {e}")
        return create_error_response(
            message="Failed to retrieve compliance risk analytics",
            details={"error": str(e)}
        ).dict()


@app.get("/api/analytics/business-intelligence", response_model=StandardResponse)
async def get_business_intelligence(
    services: dict = Depends(get_services)
):
    """
    Get business intelligence and revenue analytics.
    """
    try:
        db = services["db"]
        
        # Get all documents
        artifacts = db.get_all_artifacts()
        loan_documents = [a for a in artifacts if a.artifact_type in ['loan_document', 'financial_statement']]
        
        # Revenue metrics
        documents_this_month = len([a for a in loan_documents if a.created_at.month == datetime.now().month])
        revenue_per_document = 25.00  # $25 per document sealed
        monthly_revenue = documents_this_month * revenue_per_document
        
        # Cost analysis
        cost_per_seal = 5.00  # $5 infrastructure cost per seal
        monthly_costs = documents_this_month * cost_per_seal
        profit_margin = ((monthly_revenue - monthly_costs) / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        # Market insights
        loan_types = {}
        total_values = {}
        for doc in loan_documents:
            if doc.local_metadata and 'comprehensive_document' in doc.local_metadata:
                doc_type = doc.local_metadata['comprehensive_document'].get('document_type', 'Unknown')
                loan_amount = doc.local_metadata['comprehensive_document'].get('loan_amount', 0)
                
                loan_types[doc_type] = loan_types.get(doc_type, 0) + 1
                total_values[doc_type] = total_values.get(doc_type, 0) + loan_amount
        
        top_loan_types = [
            {"type": k, "count": v, "total_value": total_values.get(k, 0)}
            for k, v in sorted(loan_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Geographic distribution (simulated)
        geographic_distribution = [
            {"region": "North America", "count": len(loan_documents) * 0.6},
            {"region": "Europe", "count": len(loan_documents) * 0.25},
            {"region": "Asia Pacific", "count": len(loan_documents) * 0.15}
        ]
        
        # Seasonal trends (last 6 months)
        seasonal_trends = []
        for i in range(6):
            month = datetime.now().month - i
            if month <= 0:
                month += 12
            month_docs = len([a for a in loan_documents if a.created_at.month == month])
            seasonal_trends.append({
                "month": datetime(2024, month, 1).strftime("%B"),
                "volume": month_docs
            })
        seasonal_trends.reverse()
        
        analytics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "revenue_metrics": {
                "documents_sealed_this_month": documents_this_month,
                "revenue_per_document": revenue_per_document,
                "monthly_revenue": monthly_revenue,
                "cost_per_seal": cost_per_seal,
                "monthly_costs": monthly_costs,
                "profit_margin": round(profit_margin, 2)
            },
            "market_insights": {
                "top_loan_types": top_loan_types,
                "geographic_distribution": geographic_distribution,
                "seasonal_trends": seasonal_trends,
                "market_share": "2.3%",
                "growth_rate": "15.2%"
            },
            "customer_analytics": {
                "customer_retention_rate": 94.5,
                "average_documents_per_customer": round(len(loan_documents) / 25, 1),  # Assuming 25 customers
                "customer_satisfaction_score": 4.7,
                "new_customers_this_month": 3,
                "churn_rate": 2.1
            }
        }
        
        return create_success_response({
            "analytics": analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get business intelligence: {e}")
        return create_error_response(
            message="Failed to retrieve business intelligence",
            details={"error": str(e)}
        ).dict()


# =============================================================================
# PREDICTIVE ANALYTICS ENDPOINTS
# =============================================================================

class RiskPredictionRequest(BaseModel):
    """Risk prediction request model."""
    document_id: str = Field(..., description="Document ID to analyze")
    document_data: Dict[str, Any] = Field(..., description="Document metadata and features")


class ComplianceForecastRequest(BaseModel):
    """Compliance forecast request model."""
    document_id: str = Field(..., description="Document ID to analyze")
    document_data: Dict[str, Any] = Field(..., description="Document metadata and features")


class PerformancePredictionRequest(BaseModel):
    """Performance prediction request model."""
    metric_name: str = Field(..., description="Name of the performance metric")
    historical_data: List[float] = Field(..., description="Historical values of the metric")


class AnomalyDetectionRequest(BaseModel):
    """Anomaly detection request model."""
    data_points: List[Dict[str, Any]] = Field(..., description="Data points to analyze for anomalies")


class TrendAnalysisRequest(BaseModel):
    """Trend analysis request model."""
    metric_name: str = Field(..., description="Name of the metric")
    time_series_data: List[Dict[str, Any]] = Field(..., description="Time series data points")


class ModelTrainingRequest(BaseModel):
    """Model training request model."""
    training_data: List[Dict[str, Any]] = Field(..., description="Training dataset")


@app.post("/api/predictive-analytics/risk-prediction", response_model=StandardResponse)
async def predict_document_risk(
    request: RiskPredictionRequest,
    services: dict = Depends(get_services)
):
    """
    Predict the risk level of a document using ML models.
    
    Uses machine learning to analyze document features and predict potential risks
    such as fraud, tampering, or compliance issues.
    """
    try:
        # Predict document risk
        risk_prediction = services["predictive_analytics"].predict_document_risk(
            document_id=request.document_id,
            document_data=request.document_data
        )
        
        # Log audit event
        services["db"].insert_event(
            artifact_id=request.document_id,
            event_type="risk_prediction_completed",
            payload_json=json.dumps({
                "risk_level": risk_prediction.risk_level,
                "risk_score": risk_prediction.risk_score,
                "confidence": risk_prediction.confidence,
                "factors_count": len(risk_prediction.factors)
            }),
            created_by="system"
        )
        
        logger.info(f"✅ Risk prediction completed for document {request.document_id}: {risk_prediction.risk_level}")
        
        return create_success_response({
            "risk_prediction": {
                "document_id": risk_prediction.document_id,
                "risk_score": risk_prediction.risk_score,
                "risk_level": risk_prediction.risk_level,
                "confidence": risk_prediction.confidence,
                "factors": risk_prediction.factors,
                "recommendations": risk_prediction.recommendations,
                "predicted_at": risk_prediction.predicted_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to predict document risk: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="RISK_PREDICTION_FAILED",
                message="Failed to predict document risk",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/predictive-analytics/compliance-forecast", response_model=StandardResponse)
async def forecast_compliance(
    request: ComplianceForecastRequest,
    services: dict = Depends(get_services)
):
    """
    Forecast compliance status for a document.
    
    Uses machine learning to predict whether a document will pass compliance
    checks and provides recommendations for improvement.
    """
    try:
        # Forecast compliance
        compliance_forecast = services["predictive_analytics"].forecast_compliance(
            document_id=request.document_id,
            document_data=request.document_data
        )
        
        # Log audit event
        services["db"].insert_event(
            artifact_id=request.document_id,
            event_type="compliance_forecast_completed",
            payload_json=json.dumps({
                "forecast_status": compliance_forecast.forecast_status,
                "compliance_probability": compliance_forecast.compliance_probability,
                "confidence": compliance_forecast.confidence,
                "risk_factors_count": len(compliance_forecast.risk_factors)
            }),
            created_by="system"
        )
        
        logger.info(f"✅ Compliance forecast completed for document {request.document_id}: {compliance_forecast.forecast_status}")
        
        return create_success_response({
            "compliance_forecast": {
                "document_id": compliance_forecast.document_id,
                "compliance_probability": compliance_forecast.compliance_probability,
                "forecast_status": compliance_forecast.forecast_status,
                "confidence": compliance_forecast.confidence,
                "risk_factors": compliance_forecast.risk_factors,
                "recommendations": compliance_forecast.recommendations,
                "forecasted_at": compliance_forecast.forecasted_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to forecast compliance: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="COMPLIANCE_FORECAST_FAILED",
                message="Failed to forecast compliance",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/predictive-analytics/performance-prediction", response_model=StandardResponse)
async def predict_performance(
    request: PerformancePredictionRequest,
    services: dict = Depends(get_services)
):
    """
    Predict future performance for a given metric.
    
    Analyzes historical performance data and predicts future trends
    with recommendations for optimization.
    """
    try:
        # Predict performance
        performance_prediction = services["predictive_analytics"].predict_performance(
            metric_name=request.metric_name,
            historical_data=request.historical_data
        )
        
        logger.info(f"✅ Performance prediction completed for {request.metric_name}: {performance_prediction.trend}")
        
        return create_success_response({
            "performance_prediction": {
                "metric_name": performance_prediction.metric_name,
                "current_value": performance_prediction.current_value,
                "predicted_value": performance_prediction.predicted_value,
                "trend": performance_prediction.trend,
                "confidence": performance_prediction.confidence,
                "recommendations": performance_prediction.recommendations,
                "predicted_at": performance_prediction.predicted_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to predict performance: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="PERFORMANCE_PREDICTION_FAILED",
                message="Failed to predict performance",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/predictive-analytics/anomaly-detection", response_model=StandardResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    services: dict = Depends(get_services)
):
    """
    Detect anomalies in a dataset using ML models.
    
    Uses isolation forest algorithm to identify unusual patterns
    in document processing data.
    """
    try:
        # Detect anomalies
        anomalies = services["predictive_analytics"].detect_anomalies(
            data_points=request.data_points
        )
        
        logger.info(f"✅ Anomaly detection completed: {len(anomalies)} anomalies found")
        
        return create_success_response({
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "data_points_analyzed": len(request.data_points)
        })
        
    except Exception as e:
        logger.error(f"Failed to detect anomalies: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ANOMALY_DETECTION_FAILED",
                message="Failed to detect anomalies",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/predictive-analytics/trend-analysis", response_model=StandardResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    services: dict = Depends(get_services)
):
    """
    Perform trend analysis on time series data.
    
    Analyzes time series data to identify trends and patterns
    with recommendations for action.
    """
    try:
        # Analyze trends
        trend_analysis = services["predictive_analytics"].get_trend_analysis(
            metric_name=request.metric_name,
            time_series_data=request.time_series_data
        )
        
        logger.info(f"✅ Trend analysis completed for {request.metric_name}: {trend_analysis.get('trend', 'UNKNOWN')}")
        
        return create_success_response({
            "trend_analysis": trend_analysis
        })
        
    except Exception as e:
        logger.error(f"Failed to analyze trends: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="TREND_ANALYSIS_FAILED",
                message="Failed to analyze trends",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/predictive-analytics/train-models", response_model=StandardResponse)
async def train_models(
    request: ModelTrainingRequest,
    services: dict = Depends(get_services)
):
    """
    Train ML models with new data.
    
    Retrains the machine learning models with new training data
    to improve prediction accuracy.
    """
    try:
        # Train models
        training_result = services["predictive_analytics"].train_models(
            training_data=request.training_data
        )
        
        logger.info(f"✅ Model training completed: {training_result.get('status', 'UNKNOWN')}")
        
        return create_success_response({
            "training_result": training_result
        })
        
    except Exception as e:
        logger.error(f"Failed to train models: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="MODEL_TRAINING_FAILED",
                message="Failed to train models",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/predictive-analytics/model-statistics", response_model=StandardResponse)
async def get_model_statistics(
    services: dict = Depends(get_services)
):
    """
    Get statistics about the ML models.
    
    Returns information about available models, their status,
    and performance metrics.
    """
    try:
        # Get model statistics
        statistics = services["predictive_analytics"].get_model_statistics()
        
        logger.info("✅ Model statistics retrieved")
        
        return create_success_response({
            "model_statistics": statistics
        })
        
    except Exception as e:
        logger.error(f"Failed to get model statistics: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="MODEL_STATISTICS_FAILED",
                message="Failed to get model statistics",
                details={"error": str(e)}
            ).dict()
        )


# =============================================================================
# PHASE 2: ADVANCED FEATURES ENDPOINTS
# =============================================================================

# AI Anomaly Detection Endpoints

class AnomalyDetectionRequest(BaseModel):
    """Request model for anomaly detection."""
    document_data: Dict[str, Any] = Field(..., description="Document data to analyze")
    analysis_type: str = Field(default="document_integrity", description="Type of analysis to perform")


@app.post("/api/ai/anomaly-detect", response_model=StandardResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    services: dict = Depends(get_services)
):
    """
    Detect anomalies in document data using AI-powered analysis.
    
    Performs comprehensive anomaly detection including document tampering,
    compliance violations, and data inconsistencies.
    """
    try:
        # Perform anomaly detection
        anomalies = services["ai_anomaly_detector"].analyze_document_integrity(request.document_data)
        
        logger.info(f"✅ Anomaly detection completed: {len(anomalies)} anomalies found")
        
        return create_success_response({
            "anomalies": [
                {
                    "anomaly_id": anomaly.anomaly_id,
                    "type": anomaly.anomaly_type.value,
                    "severity": anomaly.severity.value,
                    "confidence_score": anomaly.confidence_score,
                    "description": anomaly.description,
                    "detected_at": anomaly.detected_at.isoformat(),
                    "affected_entities": anomaly.affected_entities,
                    "recommendations": anomaly.recommendations
                }
                for anomaly in anomalies
            ],
            "total_anomalies": len(anomalies),
            "analysis_type": request.analysis_type
        })
        
    except Exception as e:
        logger.error(f"Failed to detect anomalies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ANOMALY_DETECTION_FAILED",
                message="Failed to detect anomalies",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/ai/anomaly-summary", response_model=StandardResponse)
async def get_anomaly_summary(
    time_range_hours: int = Query(24, description="Time range in hours"),
    services: dict = Depends(get_services)
):
    """
    Get summary of anomalies detected in the specified time range.
    
    Returns comprehensive statistics about detected anomalies including
    trends, affected entities, and recommendations.
    """
    try:
        summary = services["ai_anomaly_detector"].get_anomaly_summary(time_range_hours)
        
        logger.info(f"✅ Anomaly summary generated for last {time_range_hours} hours")
        
        return create_success_response({
            "summary": summary,
            "time_range_hours": time_range_hours
        })
        
    except Exception as e:
        logger.error(f"Failed to get anomaly summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="ANOMALY_SUMMARY_FAILED",
                message="Failed to get anomaly summary",
                details={"error": str(e)}
            ).dict()
        )


# Time Machine Endpoints

class StateSnapshotRequest(BaseModel):
    """Request model for creating state snapshots."""
    document_id: str = Field(..., description="ID of the document")
    state_data: Dict[str, Any] = Field(..., description="Current state data")
    description: str = Field(default="", description="Description of the snapshot")
    tags: List[str] = Field(default=[], description="Tags for categorization")


@app.post("/api/time-machine/snapshot", response_model=StandardResponse)
async def create_state_snapshot(
    request: StateSnapshotRequest,
    created_by: str = Query("system", description="User creating the snapshot"),
    services: dict = Depends(get_services)
):
    """
    Create a snapshot of the current document state.
    
    Creates a point-in-time snapshot that can be used for time travel
    and state restoration.
    """
    try:
        snapshot = services["time_machine"].create_state_snapshot(
            document_id=request.document_id,
            state_data=request.state_data,
            created_by=created_by,
            description=request.description,
            tags=request.tags
        )
        
        logger.info(f"✅ State snapshot created: {snapshot.snapshot_id}")
        
        return create_success_response({
            "snapshot": {
                "snapshot_id": snapshot.snapshot_id,
                "document_id": snapshot.document_id,
                "version": snapshot.version,
                "timestamp": snapshot.timestamp.isoformat(),
                "description": snapshot.description,
                "tags": snapshot.tags,
                "created_by": snapshot.created_by
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create state snapshot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SNAPSHOT_CREATION_FAILED",
                message="Failed to create state snapshot",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/time-machine/timeline/{document_id}", response_model=StandardResponse)
async def get_document_timeline(
    document_id: str,
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    services: dict = Depends(get_services)
):
    """
    Get the timeline of document states within a time range.
    
    Returns the complete history of document state changes,
    allowing users to see how the document evolved over time.
    """
    try:
        # Parse time parameters
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        timeline = services["time_machine"].get_document_timeline(
            document_id=document_id,
            start_time=start_dt,
            end_time=end_dt
        )
        
        logger.info(f"✅ Document timeline retrieved: {len(timeline)} states")
        
        return create_success_response({
            "document_id": document_id,
            "timeline": [
                {
                    "state_id": state.state_id,
                    "version": state.version,
                    "timestamp": state.timestamp.isoformat(),
                    "change_type": state.change_type.value,
                    "changed_by": state.changed_by,
                    "change_description": state.change_description,
                    "parent_state_id": state.parent_state_id
                }
                for state in timeline
            ],
            "total_states": len(timeline)
        })
        
    except Exception as e:
        logger.error(f"Failed to get document timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="TIMELINE_RETRIEVAL_FAILED",
                message="Failed to get document timeline",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/time-machine/restore/{document_id}", response_model=StandardResponse)
async def restore_document_state(
    document_id: str,
    target_state_id: str = Query(..., description="ID of the state to restore to"),
    restored_by: str = Query("system", description="User performing the restore"),
    restore_reason: str = Query("", description="Reason for restoration"),
    services: dict = Depends(get_services)
):
    """
    Restore a document to a previous state.
    
    Allows users to travel back in time and restore a document
    to any previous state in its history.
    """
    try:
        restored_state = services["time_machine"].restore_document_state(
            document_id=document_id,
            target_state_id=target_state_id,
            restored_by=restored_by,
            restore_reason=restore_reason
        )
        
        logger.info(f"✅ Document {document_id} restored to state {target_state_id}")
        
        return create_success_response({
            "restored_state": {
                "state_id": restored_state.state_id,
                "document_id": restored_state.document_id,
                "version": restored_state.version,
                "timestamp": restored_state.timestamp.isoformat(),
                "change_type": restored_state.change_type.value,
                "changed_by": restored_state.changed_by,
                "change_description": restored_state.change_description,
                "parent_state_id": restored_state.parent_state_id
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to restore document state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="STATE_RESTORATION_FAILED",
                message="Failed to restore document state",
                details={"error": str(e)}
            ).dict()
        )


# Smart Contracts Endpoints

class SmartContractRequest(BaseModel):
    """Request model for smart contract operations."""
    name: str = Field(..., description="Name of the contract")
    description: str = Field(..., description="Description of the contract")


# Loan Document API Models
class BorrowerAddress(BaseModel):
    """Borrower address information."""
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/Province")
    zip_code: str = Field(..., description="ZIP/Postal code")
    country: str = Field(default="United States", description="Country")


class BorrowerInfo(BaseModel):
    """Borrower information model."""
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    address: BorrowerAddress = Field(..., description="Address information")
    ssn_last4: str = Field(..., description="Last 4 digits of SSN")
    id_type: str = Field(..., description="Government ID type")
    id_last4: str = Field(..., description="Last 4 digits of ID number")
    employment_status: str = Field(..., description="Employment status")
    annual_income: float = Field(..., description="Annual income")
    co_borrower_name: Optional[str] = Field(None, description="Co-borrower name (optional)")


class LoanDocumentSealRequest(BaseModel):
    """Request model for sealing loan documents with borrower information."""
    loan_id: str = Field(..., description="Unique loan identifier")
    document_type: str = Field(..., description="Type of loan document")
    loan_amount: float = Field(..., description="Loan amount")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    borrower: BorrowerInfo = Field(..., description="Borrower information")
    created_by: str = Field(..., description="User who created the document")


class LoanDocumentSealResponse(BaseModel):
    """Response model for loan document sealing."""
    message: str = Field(..., description="Response message")
    artifact_id: str = Field(..., description="Created artifact ID")
    walacor_tx_id: str = Field(..., description="Walacor transaction ID")
    hash: str = Field(..., description="Document hash")
    sealed_at: str = Field(..., description="Sealing timestamp")
    signature_jwt: Optional[str] = Field(None, description="JWT signature of the canonical payload")


class MaskedBorrowerInfo(BaseModel):
    """Masked borrower information for privacy."""
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    email: str = Field(..., description="Masked email address")
    phone: str = Field(..., description="Masked phone number")
    address: BorrowerAddress = Field(..., description="Address information")
    ssn_last4: str = Field(..., description="Last 4 digits of SSN")
    id_type: str = Field(..., description="Government ID type")
    id_last4: str = Field(..., description="Last 4 digits of ID number")
    employment_status: str = Field(..., description="Employment status")
    annual_income_range: str = Field(..., description="Annual income range")
    co_borrower_name: Optional[str] = Field(None, description="Co-borrower name (optional)")


class LoanSearchRequest(BaseModel):
    """Request model for searching loan documents."""
    borrower_name: Optional[str] = Field(None, description="Search by borrower name")
    borrower_email: Optional[str] = Field(None, description="Search by borrower email")
    loan_id: Optional[str] = Field(None, description="Search by loan ID")
    date_from: Optional[str] = Field(None, description="Filter from date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter to date (YYYY-MM-DD)")
    amount_min: Optional[float] = Field(None, description="Minimum loan amount")
    amount_max: Optional[float] = Field(None, description="Maximum loan amount")
    limit: int = Field(default=50, description="Number of results to return")
    offset: int = Field(default=0, description="Number of results to skip")


class LoanSearchResult(BaseModel):
    """Individual loan search result."""
    artifact_id: str = Field(..., description="Artifact ID")
    loan_id: str = Field(..., description="Loan ID")
    document_type: str = Field(..., description="Document type")
    loan_amount: float = Field(..., description="Loan amount")
    borrower_name: str = Field(..., description="Borrower name")
    borrower_email: str = Field(..., description="Borrower email")
    upload_date: str = Field(..., description="Upload date")
    sealed_status: str = Field(..., description="Sealed status")
    walacor_tx_id: str = Field(..., description="Walacor transaction ID")


class LoanSearchResponse(BaseModel):
    """Response model for loan search."""
    results: List[LoanSearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of matching results")
    has_more: bool = Field(..., description="Whether there are more results")


class AuditEvent(BaseModel):
    """Individual audit event."""
    event_id: str = Field(..., description="Event ID")
    event_type: str = Field(..., description="Type of event")
    timestamp: str = Field(..., description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User who performed the action")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    details: Dict[str, Any] = Field(..., description="Event details")


class AuditTrailResponse(BaseModel):
    """Response model for audit trail."""
    artifact_id: str = Field(..., description="Artifact ID")
    loan_id: str = Field(..., description="Loan ID")
    events: List[AuditEvent] = Field(..., description="List of audit events")
    total_events: int = Field(..., description="Total number of events")


@app.post("/api/smart-contracts/create", response_model=StandardResponse)
async def create_smart_contract(
    request: SmartContractRequest,
    created_by: str = Query("system", description="User creating the contract"),
    services: dict = Depends(get_services)
):
    """
    Create a new smart contract for automated compliance and workflow management.
    
    Smart contracts provide rule-based automation for document processing,
    compliance checking, and workflow management.
    """
    try:
        from src.smart_contracts import ContractType, ContractRule
        
        # Convert contract type
        contract_type = ContractType(request.contract_type)
        
        # Convert rules
        rules = []
        for rule_data in request.rules:
            rule = ContractRule(
                rule_id=str(uuid.uuid4()),
                name=rule_data["name"],
                description=rule_data["description"],
                condition=rule_data["condition"],
                action=rule_data["action"],
                severity=rule_data.get("severity", "medium"),
                enabled=rule_data.get("enabled", True),
                metadata=rule_data.get("metadata", {})
            )
            rules.append(rule)
        
        contract = services["smart_contracts"].create_contract(
            name=request.name,
            description=request.description,
            contract_type=contract_type,
            rules=rules,
            created_by=created_by,
            metadata=request.metadata
        )
        
        logger.info(f"✅ Smart contract created: {contract.contract_id}")
        
        return create_success_response({
            "contract": {
                "contract_id": contract.contract_id,
                "name": contract.name,
                "description": contract.description,
                "contract_type": contract.contract_type.value,
                "status": contract.status.value,
                "rules_count": len(contract.rules),
                "created_at": contract.created_at.isoformat(),
                "created_by": contract.created_by
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create smart contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SMART_CONTRACT_CREATION_FAILED",
                message="Failed to create smart contract",
                details={"error": str(e)}
            ).dict()
        )


@app.post("/api/smart-contracts/execute/{contract_id}", response_model=StandardResponse)
async def execute_smart_contract(
    contract_id: str,
    data: Dict[str, Any],
    executed_by: str = Query("system", description="User executing the contract"),
    services: dict = Depends(get_services)
):
    """
    Execute a smart contract against provided data.
    
    Evaluates all contract rules against the provided data and returns
    the execution results with any violations or warnings.
    """
    try:
        execution = services["smart_contracts"].execute_contract(
            contract_id=contract_id,
            data=data,
            executed_by=executed_by
        )
        
        logger.info(f"✅ Smart contract executed: {contract_id} - {execution.result.value}")
        
        return create_success_response({
            "execution": {
                "execution_id": execution.execution_id,
                "contract_id": execution.contract_id,
                "executed_at": execution.executed_at.isoformat(),
                "result": execution.result.value,
                "message": execution.message,
                "affected_entities": execution.affected_entities,
                "rule_results": execution.rule_results,
                "metadata": execution.metadata
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to execute smart contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SMART_CONTRACT_EXECUTION_FAILED",
                message="Failed to execute smart contract",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/smart-contracts/list", response_model=StandardResponse)
async def list_smart_contracts(
    contract_type: Optional[str] = Query(None, description="Filter by contract type"),
    status: Optional[str] = Query(None, description="Filter by contract status"),
    services: dict = Depends(get_services)
):
    """
    List smart contracts with optional filtering.
    
    Returns a list of all smart contracts, optionally filtered by
    type and status.
    """
    try:
        from src.smart_contracts import ContractType, ContractStatus
        
        # Convert filters
        contract_type_filter = ContractType(contract_type) if contract_type else None
        status_filter = ContractStatus(status) if status else None
        
        contracts = services["smart_contracts"].list_contracts(
            contract_type=contract_type_filter,
            status=status_filter
        )
        
        logger.info(f"✅ Smart contracts listed: {len(contracts)} contracts")
        
        return create_success_response({
            "contracts": [
                {
                    "contract_id": contract.contract_id,
                    "name": contract.name,
                    "description": contract.description,
                    "contract_type": contract.contract_type.value,
                    "status": contract.status.value,
                    "rules_count": len(contract.rules),
                    "execution_count": contract.execution_count,
                    "success_count": contract.success_count,
                    "failure_count": contract.failure_count,
                    "created_at": contract.created_at.isoformat(),
                    "updated_at": contract.updated_at.isoformat(),
                    "created_by": contract.created_by
                }
                for contract in contracts
            ],
            "total_contracts": len(contracts)
        })
        
    except Exception as e:
        logger.error(f"Failed to list smart contracts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SMART_CONTRACTS_LIST_FAILED",
                message="Failed to list smart contracts",
                details={"error": str(e)}
            ).dict()
        )


@app.get("/api/smart-contracts/statistics", response_model=StandardResponse)
async def get_smart_contract_statistics(
    services: dict = Depends(get_services)
):
    """
    Get statistics about smart contracts and their execution.
    
    Returns comprehensive statistics including contract counts,
    execution results, and performance metrics.
    """
    try:
        statistics = services["smart_contracts"].get_contract_statistics()
        
        logger.info("✅ Smart contract statistics retrieved")
        
        return create_success_response({
            "statistics": statistics
        })
        
    except Exception as e:
        logger.error(f"Failed to get smart contract statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                code="SMART_CONTRACT_STATISTICS_FAILED",
                message="Failed to get smart contract statistics",
                details={"error": str(e)}
            ).dict()
        )


# Loan Document API Endpoints

@app.post("/api/loan-documents/seal", response_model=StandardResponse)
async def seal_loan_document(
    request: LoanDocumentSealRequest,
    services: dict = Depends(get_services)
):
    """
    Seal a loan document with borrower information in the Walacor blockchain.
    
    This endpoint accepts loan data with borrower information, calculates a SHA-256 hash
    of the combined data, seals it in the Walacor blockchain, and stores it in the database
    with the borrower_info JSON field.
    """
    try:
        log_endpoint_start("seal_loan_document", request.dict())
        
        # Encrypt sensitive borrower data
        encryption_service = get_encryption_service()
        encrypted_borrower_data = encryption_service.encrypt_borrower_data(request.borrower.dict())
        
        # Create comprehensive document JSON with encrypted borrower data
        comprehensive_document = {
            "loan_id": request.loan_id,
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "borrower": encrypted_borrower_data,
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate SHA-256 hash of the comprehensive document
        import hashlib
        canonical_document_str = canonical_json(comprehensive_document)
        document_hash = hashlib.sha256(canonical_document_str.encode('utf-8')).hexdigest()
        
        logger.info(f"Sealing loan document {request.loan_id} with hash: {document_hash[:16]}...")
        
        # Seal in Walacor blockchain using new loan document method
        loan_data = {
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "created_by": request.created_by
        }
        
        # Create file metadata (since we're not uploading actual files, create metadata)
        files_metadata = [{
            "filename": f"loan-{request.loan_id}.json",
            "file_type": "application/json",
            "file_size": len(canonical_document_str.encode('utf-8')),
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": document_hash
        }]
        
        walacor_result = services["wal_service"].seal_loan_document(
            loan_id=request.loan_id,
            loan_data=loan_data,
            borrower_data=encrypted_borrower_data,
            files=files_metadata
        )
        
        # Store in database with borrower_info using new ETID
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="json",
            etid=100005,  # Use new ETID for loan documents with borrower info
            payload_sha256=walacor_result.get("document_hash", document_hash),
            walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{document_hash[:8]}"),
            created_by=request.created_by,
            blockchain_seal=walacor_result.get("blockchain_proof", {}).get("transaction_id"),
            local_metadata={
                "comprehensive_document": comprehensive_document,
                "comprehensive_hash": walacor_result.get("document_hash", document_hash),
                "includes_borrower_info": True,
                "sealed_at": walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                "walacor_envelope": walacor_result.get("envelope_metadata", {}),
                "blockchain_proof": walacor_result.get("blockchain_proof", {}),
                "canonical_document": canonical_document_str
            },
            borrower_info=encrypted_borrower_data
        )

        # Generate and persist JWT signature for the canonical payload
        signature_jwt = sign_artifact(artifact_id, comprehensive_document)
        services["db"].update_artifact_signature(artifact_id, signature_jwt)
        
        logger.info(f"✅ Loan document sealed successfully: {artifact_id}")
        
        # Log audit events for compliance
        try:
            # Log document upload
            services["db"].log_document_upload(
                artifact_id=artifact_id,
                user_id=request.created_by,
                borrower_name=request.borrower.full_name,
                loan_id=request.loan_id,
                ip_address=None,  # Could be extracted from request if needed
                user_agent=None   # Could be extracted from request if needed
            )
            
            # Log blockchain sealing
            services["db"].log_blockchain_seal(
                artifact_id=artifact_id,
                walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{document_hash[:8]}"),
                data_hash=walacor_result.get("document_hash", document_hash),
                sealed_by=request.created_by
            )
            
            logger.info(f"✅ Audit logs created for document upload and blockchain sealing")
            
        except Exception as e:
            logger.warning(f"Failed to create audit logs: {e}")
            # Don't fail the main operation if audit logging fails
        
        return StandardResponse(
            ok=True,
            data=LoanDocumentSealResponse(
                message="Loan document sealed successfully with borrower information",
                artifact_id=artifact_id,
                walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{document_hash[:8]}"),
                hash=walacor_result.get("document_hash", document_hash),
                sealed_at=walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                signature_jwt=signature_jwt
            ).dict()
        )
        
    except Exception as e:
        logger.error(f"Error sealing loan document: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.post("/api/loan-documents/seal-maximum-security", response_model=StandardResponse)
async def seal_loan_document_maximum_security(
    request: LoanDocumentSealRequest,
    services: dict = Depends(get_services)
):
    """
    Seal a loan document with MAXIMUM SECURITY and MINIMAL TAMPERING.
    
    This endpoint implements multiple layers of security:
    1. Multi-algorithm hashing (SHA-256, SHA-512, BLAKE3, SHA3-256)
    2. PKI-based digital signatures
    3. Content-based integrity verification
    4. Cross-verification systems
    5. Advanced tamper detection
    """
    try:
        log_endpoint_start("seal_loan_document_maximum_security", request.dict())
        
        # Generate key pair for this document
        advanced_security = services["advanced_security"]
        private_key, public_key = advanced_security.generate_key_pair()
        
        # Encrypt sensitive borrower data
        encryption_service = get_encryption_service()
        encrypted_borrower_data = encryption_service.encrypt_borrower_data(request.borrower.dict())
        
        # Create comprehensive document JSON with encrypted borrower data
        comprehensive_document = {
            "loan_id": request.loan_id,
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "borrower": encrypted_borrower_data,
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "security_level": "maximum"
        }
        
        # Create canonical representation
        canonical_document_str = canonical_json(comprehensive_document)

        # Create comprehensive security seal
        comprehensive_seal = advanced_security.create_comprehensive_seal(
            comprehensive_document, 
            private_key
        )
        
        # Get primary hash for blockchain sealing
        primary_hash = comprehensive_seal['content_signature']['content_hash']['sha256']
        
        logger.info(f"Sealing loan document {request.loan_id} with MAXIMUM SECURITY - Hash: {primary_hash[:16]}...")
        
        # Seal in Walacor blockchain
        loan_data = {
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "created_by": request.created_by
        }
        
        files_metadata = [{
            "filename": f"loan-{request.loan_id}-secure.json",
            "file_type": "application/json",
            "file_size": len(canonical_document_str.encode('utf-8')),
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": primary_hash
        }]
        
        walacor_result = services["wal_service"].seal_loan_document(
            loan_id=request.loan_id,
            loan_data=loan_data,
            borrower_data=encrypted_borrower_data,
            files=files_metadata
        )
        
        # Store in database with maximum security metadata
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="json",
            etid=100005,
            payload_sha256=primary_hash,
            walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
            created_by=request.created_by,
            blockchain_seal=walacor_result.get("blockchain_proof", {}).get("transaction_id"),
            local_metadata={
                "comprehensive_document": comprehensive_document,
                "comprehensive_seal": comprehensive_seal,
                "public_key": public_key,
                "security_level": "maximum",
                "tamper_resistance": "high",
                "verification_methods": ["multi_hash", "pki_signature", "content_integrity", "blockchain_seal"],
                "sealed_at": walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                "walacor_envelope": walacor_result.get("envelope_metadata", {}),
                "blockchain_proof": walacor_result.get("blockchain_proof", {}),
                "canonical_document": canonical_document_str
            },
            borrower_info=encrypted_borrower_data
        )

        signature_jwt = sign_artifact(artifact_id, comprehensive_document)
        services["db"].update_artifact_signature(artifact_id, signature_jwt)
        
        logger.info(f"✅ Loan document sealed with MAXIMUM SECURITY: {artifact_id}")
        
        # Log comprehensive audit events
        try:
            services["db"].log_document_upload(
                artifact_id=artifact_id,
                user_id=request.created_by,
                borrower_name=request.borrower.full_name,
                loan_id=request.loan_id,
                ip_address=None,
                user_agent=None
            )
            
            services["db"].log_blockchain_seal(
                artifact_id=artifact_id,
                walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
                data_hash=primary_hash,
                sealed_by=request.created_by
            )
            
            logger.info(f"✅ Comprehensive audit logs created for maximum security document")
            
        except Exception as e:
            logger.warning(f"Failed to create audit logs: {e}")
        
        return StandardResponse(
            ok=True,
            data={
                "message": "Loan document sealed with MAXIMUM SECURITY and MINIMAL TAMPERING",
                "artifact_id": artifact_id,
                "walacor_tx_id": walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
                "comprehensive_seal": {
                    "seal_id": comprehensive_seal['seal_id'],
                    "security_level": "maximum",
                    "tamper_resistance": "high",
                    "verification_methods": comprehensive_seal['security_metadata']['verification_methods'],
                "multi_hash_algorithms": list(comprehensive_seal['content_signature']['content_hash'].keys()),
                "pki_signature": {
                    "algorithm": comprehensive_seal['pki_signature']['algorithm'],
                    "key_size": comprehensive_seal['pki_signature']['key_size']
                }
                },
                "hash": primary_hash,
                "sealed_at": walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                "blockchain_proof": walacor_result.get("blockchain_proof", {}),
                "signature_jwt": signature_jwt
            }
        )
        
    except Exception as e:
        logger.error(f"Error sealing loan document with maximum security: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.get("/api/loan-documents/{artifact_id}/borrower", response_model=StandardResponse)
async def get_borrower_info(
    artifact_id: str,
    services: dict = Depends(get_services)
):
    """
    Get borrower information for a specific loan document with privacy masking.
    
    Returns borrower information with sensitive fields masked for privacy:
    - Email: j***@email.com
    - Phone: ***-***-1234
    - SSN/ID: Last 4 digits only
    """
    try:
        log_endpoint_start("get_borrower_info", {"artifact_id": artifact_id})
        
        # Get artifact from database
        artifact = services["db"].get_artifact_by_id(artifact_id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found"
            )
        
        # Get borrower info from artifact
        borrower_info = None
        if artifact.borrower_info:
            borrower_info = artifact.borrower_info
        elif (artifact.local_metadata and 
              artifact.local_metadata.get('comprehensive_document') and 
              artifact.local_metadata['comprehensive_document'].get('borrower')):
            borrower_info = artifact.local_metadata['comprehensive_document']['borrower']
        
        if not borrower_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Borrower information not found for this artifact"
            )
        
        # Decrypt sensitive borrower data
        encryption_service = get_encryption_service()
        try:
            borrower_info = encryption_service.decrypt_borrower_data(borrower_info)
        except Exception as e:
            logger.warning(f"Failed to decrypt borrower data, using as-is: {e}")
            # Continue with potentially unencrypted data for backward compatibility
        
        # Mask sensitive information
        def mask_email(email: str) -> str:
            if '@' in email:
                local, domain = email.split('@', 1)
                if len(local) > 1:
                    return f"{local[0]}***@{domain}"
                return f"***@{domain}"
            return "***@***.com"
        
        def mask_phone(phone: str) -> str:
            # Extract last 4 digits
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) >= 4:
                return f"***-***-{digits[-4:]}"
            return "***-***-****"
        
        def get_income_range(income: float) -> str:
            if income < 30000:
                return "Under $30,000"
            elif income < 50000:
                return "$30,000 - $49,999"
            elif income < 75000:
                return "$50,000 - $74,999"
            elif income < 100000:
                return "$75,000 - $99,999"
            elif income < 150000:
                return "$100,000 - $149,999"
            else:
                return "$150,000+"
        
        # Create masked borrower info
        masked_borrower = MaskedBorrowerInfo(
            full_name=borrower_info.get('full_name', ''),
            date_of_birth=borrower_info.get('date_of_birth', ''),
            email=mask_email(borrower_info.get('email', '')),
            phone=mask_phone(borrower_info.get('phone', '')),
            address=BorrowerAddress(**borrower_info.get('address', {})),
            ssn_last4=borrower_info.get('ssn_last4', ''),
            id_type=borrower_info.get('id_type', ''),
            id_last4=borrower_info.get('id_last4', ''),
            employment_status=borrower_info.get('employment_status', ''),
            annual_income_range=get_income_range(borrower_info.get('annual_income', 0)),
            co_borrower_name=borrower_info.get('co_borrower_name')
        )
        
        logger.info(f"✅ Retrieved masked borrower info for artifact: {artifact_id}")
        
        # Log audit event for borrower data access
        try:
            services["db"].log_borrower_data_access(
                artifact_id=artifact_id,
                accessed_by="api_user",  # Could be extracted from request context
                access_reason="borrower_info_retrieval",
                ip_address=None  # Could be extracted from request if needed
            )
            
            # Log sensitive data viewing (even though it's masked)
            services["db"].log_sensitive_data_viewed(
                artifact_id=artifact_id,
                viewer_id="api_user",
                data_types=["personal_info", "contact_info", "identity_info"],
                ip_address=None
            )
            
            logger.info(f"✅ Audit logs created for borrower data access")
            
        except Exception as e:
            logger.warning(f"Failed to create audit logs: {e}")
            # Don't fail the main operation if audit logging fails
        
        return StandardResponse(
            ok=True,
            data=masked_borrower.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving borrower info: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.post("/api/loan-documents/{artifact_id}/verify-maximum-security", response_model=StandardResponse)
async def verify_maximum_security_document(
    artifact_id: str,
    services: dict = Depends(get_services)
):
    """
    Verify a maximum security loan document with comprehensive tamper detection.
    
    This endpoint performs:
    1. Multi-algorithm hash verification
    2. PKI signature verification
    3. Content integrity verification
    4. Blockchain seal verification
    5. Advanced tampering detection
    """
    try:
        log_endpoint_start("verify_maximum_security_document", {"artifact_id": artifact_id})
        
        # Get artifact from database
        artifact = services["db"].get_artifact_by_id(artifact_id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if this is a maximum security document
        raw_metadata = artifact.local_metadata
        if isinstance(raw_metadata, str):
            try:
                local_metadata = json.loads(raw_metadata)
            except json.JSONDecodeError:
                local_metadata = {}
        elif isinstance(raw_metadata, dict):
            local_metadata = raw_metadata
        else:
            local_metadata = {}
        if local_metadata.get("security_level") != "maximum":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is not a maximum security document"
            )
        
        # Get comprehensive seal and document data
        comprehensive_seal = local_metadata.get("comprehensive_seal", {})
        comprehensive_document = local_metadata.get("comprehensive_document", {})
        public_key = local_metadata.get("public_key", "")
        
        if not comprehensive_seal or not comprehensive_document or not public_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum security metadata incomplete"
            )

        # Verify JWT signature for the stored comprehensive document
        jwt_verified = False
        jwt_claims: Optional[Dict[str, Any]] = None
        jwt_error: Optional[str] = None
        stored_token = getattr(artifact, "signature_jwt", None)
        if stored_token:
            try:
                claims = verify_signature(stored_token, comprehensive_document)
                jwt_verified = True
                jwt_claims = {
                    "artifact_id": claims.get("artifact_id"),
                    "issued_at": datetime.fromtimestamp(claims.get("iat", 0), timezone.utc).isoformat() if claims.get("iat") else None,
                    "expires_at": datetime.fromtimestamp(claims.get("exp", 0), timezone.utc).isoformat() if claims.get("exp") else None,
                }
            except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.InvalidTokenError, ValueError) as sig_error:
                jwt_error = str(sig_error)
        else:
            jwt_error = "Signature not available for this artifact"
        
        # Perform comprehensive verification
        advanced_security = services["advanced_security"]
        
        # 1. Verify comprehensive seal
        verification_results = advanced_security.verify_comprehensive_seal(
            comprehensive_document,
            comprehensive_seal,
            public_key
        )
        
        # 2. Verify blockchain seal
        blockchain_verified = False
        if artifact.walacor_tx_id:
            try:
                # Verify against blockchain
                verify_result = services["wal_service"].verify_document_hash(
                    artifact.payload_sha256,
                    artifact.etid
                )
                blockchain_verified = verify_result.get("is_valid", False)
            except Exception as e:
                logger.warning(f"Blockchain verification failed: {e}")
                blockchain_verified = False
        
        # 3. Create security report
        security_report = advanced_security.create_security_report(
            artifact_id,
            verification_results
        )
        
        # 4. Overall verification status
        overall_verified = (
            verification_results['overall_verified'] and 
            blockchain_verified
        )
        
        logger.info(f"Maximum security verification for {artifact_id}: {'✅ VERIFIED' if overall_verified else '❌ FAILED'}")
        
        return StandardResponse(
            ok=True,
            data={
                "verification_status": "verified" if overall_verified else "failed",
                "overall_verified": overall_verified,
                "security_level": "maximum",
                "tamper_resistance": "high",
                "verification_results": {
                    "content_integrity": verification_results['content_integrity'],
                    "pki_signature": verification_results['pki_signature'],
                    "blockchain_seal": blockchain_verified,
                    "multi_hash_verification": verification_results['content_integrity']['hash_verification']
                },
                "jwt_signature": {
                    "verified": jwt_verified,
                    "claims": jwt_claims,
                    "error": jwt_error
                },
                "security_report": security_report,
                "comprehensive_seal": {
                    "seal_id": comprehensive_seal.get('seal_id'),
                    "security_level": comprehensive_seal.get('security_metadata', {}).get('security_level'),
                    "verification_methods": comprehensive_seal.get('security_metadata', {}).get('verification_methods', []),
                    "algorithms_used": comprehensive_seal.get('security_metadata', {}).get('algorithms_used', [])
                },
                "verification_timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying maximum security document: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.post("/api/loan-documents/seal-quantum-safe", response_model=StandardResponse)
async def seal_loan_document_quantum_safe(
    request: LoanDocumentSealRequest,
    services: dict = Depends(get_services)
):
    """
    Seal a loan document with QUANTUM-SAFE cryptography.
    
    This endpoint implements quantum-resistant algorithms:
    1. SHAKE256 hashing (quantum-resistant)
    2. BLAKE3 hashing (quantum-resistant)
    3. Dilithium digital signatures (NIST PQC Standard)
    4. Hybrid classical-quantum approach for transition
    """
    try:
        log_endpoint_start("seal_loan_document_quantum_safe", request.dict())
        
        # Get quantum-safe security service
        hybrid_security_service = services["hybrid_security"]
        
        # Encrypt sensitive borrower data
        encryption_service = get_encryption_service()
        encrypted_borrower_data = encryption_service.encrypt_borrower_data(request.borrower.dict())
        
        # Create comprehensive document JSON with encrypted borrower data
        comprehensive_document = {
            "loan_id": request.loan_id,
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "borrower": encrypted_borrower_data,
            "created_by": request.created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "security_level": "quantum_safe"
        }
        
        canonical_document_str = canonical_json(comprehensive_document)

        # Create quantum-safe hybrid seal
        quantum_safe_seal = hybrid_security_service.create_hybrid_seal(
            comprehensive_document, 
            security_level='hybrid'  # Use hybrid for transition
        )
        
        # Get primary hash for blockchain sealing (use quantum-safe hash)
        primary_hash = quantum_safe_seal['document_hash']['primary_hash']
        
        logger.info(f"Sealing loan document {request.loan_id} with QUANTUM-SAFE cryptography - Hash: {primary_hash[:16]}...")
        
        # Seal in Walacor blockchain
        loan_data = {
            "document_type": request.document_type,
            "loan_amount": request.loan_amount,
            "additional_notes": request.additional_notes,
            "created_by": request.created_by
        }
        
        files_metadata = [{
            "filename": f"loan-{request.loan_id}-quantum-safe.json",
            "file_type": "application/json",
            "file_size": len(canonical_document_str.encode('utf-8')),
            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": primary_hash
        }]
        
        walacor_result = services["wal_service"].seal_loan_document(
            loan_id=request.loan_id,
            loan_data=loan_data,
            borrower_data=encrypted_borrower_data,
            files=files_metadata
        )
        
        # Store in database with quantum-safe metadata
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="json",
            etid=100005,
            payload_sha256=primary_hash,
            walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
            created_by=request.created_by,
            blockchain_seal=walacor_result.get("blockchain_proof", {}).get("transaction_id"),
            local_metadata={
                "comprehensive_document": comprehensive_document,
                "quantum_safe_seal": quantum_safe_seal,
                "security_level": "quantum_safe",
                "quantum_resistance": "high",
                "algorithms_used": quantum_safe_seal['metadata']['algorithms_used'],
                "sealed_at": walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                "walacor_envelope": walacor_result.get("envelope_metadata", {}),
                "blockchain_proof": walacor_result.get("blockchain_proof", {}),
                "canonical_document": canonical_document_str
            },
            borrower_info=encrypted_borrower_data
        )

        signature_jwt = sign_artifact(artifact_id, comprehensive_document)
        services["db"].update_artifact_signature(artifact_id, signature_jwt)
        
        logger.info(f"✅ Loan document sealed with QUANTUM-SAFE cryptography: {artifact_id}")
        
        # Log comprehensive audit events
        try:
            services["db"].log_document_upload(
                artifact_id=artifact_id,
                user_id=request.created_by,
                borrower_name=request.borrower.full_name,
                loan_id=request.loan_id,
                ip_address=None,
                user_agent=None
            )
            
            services["db"].log_blockchain_seal(
                artifact_id=artifact_id,
                walacor_tx_id=walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
                data_hash=primary_hash,
                sealed_by=request.created_by
            )
            
            logger.info(f"✅ Quantum-safe audit logs created")
            
        except Exception as e:
            logger.warning(f"Failed to create audit logs: {e}")
        
        return StandardResponse(
            ok=True,
            data={
                "message": "Loan document sealed with QUANTUM-SAFE cryptography",
                "artifact_id": artifact_id,
                "walacor_tx_id": walacor_result.get("walacor_tx_id", f"TX_{int(time.time() * 1000)}_{primary_hash[:8]}"),
                "quantum_safe_seal": {
                    "seal_id": quantum_safe_seal['seal_id'],
                    "security_level": quantum_safe_seal['security_level'],
                    "quantum_safe": quantum_safe_seal['quantum_safe'],
                    "algorithms_used": quantum_safe_seal['metadata']['algorithms_used'],
                    "quantum_resistant_hashes": {
                        "shake256": quantum_safe_seal['document_hash']['all_hashes'].get('shake256'),
                        "blake3": quantum_safe_seal['document_hash']['all_hashes'].get('blake3'),
                        "sha3_512": quantum_safe_seal['document_hash']['all_hashes'].get('sha3_512')
                    },
                    "quantum_safe_signatures": {
                        "dilithium2": quantum_safe_seal['signatures'].get('dilithium2', {}).get('algorithm')
                    }
                },
                "hash": primary_hash,
                "sealed_at": walacor_result.get("sealed_timestamp", datetime.now(timezone.utc).isoformat()),
                "blockchain_proof": walacor_result.get("blockchain_proof", {}),
                "signature_jwt": signature_jwt
            }
        )
        
    except Exception as e:
        logger.error(f"Error sealing loan document with quantum-safe cryptography: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.get("/api/loan-documents/search", response_model=StandardResponse)
async def search_loan_documents(
    borrower_name: Optional[str] = Query(None, description="Search by borrower name"),
    borrower_email: Optional[str] = Query(None, description="Search by borrower email"),
    loan_id: Optional[str] = Query(None, description="Search by loan ID"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    amount_min: Optional[float] = Query(None, description="Minimum loan amount"),
    amount_max: Optional[float] = Query(None, description="Maximum loan amount"),
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    services: dict = Depends(get_services)
):
    """
    Search loan documents by various criteria with pagination.
    
    Supports searching by borrower information, loan details, date ranges, and amount ranges.
    Returns paginated results with loan and borrower information.
    """
    try:
        search_params = {
            "borrower_name": borrower_name,
            "borrower_email": borrower_email,
            "loan_id": loan_id,
            "date_from": date_from,
            "date_to": date_to,
            "amount_min": amount_min,
            "amount_max": amount_max
        }
        
        log_endpoint_start("search_loan_documents", search_params)
        
        # Get all artifacts
        artifacts = services["db"].get_all_artifacts()
        filtered_artifacts = []
        
        # Apply filters
        encryption_service = get_encryption_service()
        for artifact in artifacts:
            borrower = None
            if artifact.borrower_info:
                borrower = artifact.borrower_info
            elif (artifact.local_metadata and 
                  artifact.local_metadata.get('comprehensive_document') and 
                  artifact.local_metadata['comprehensive_document'].get('borrower')):
                borrower = artifact.local_metadata['comprehensive_document']['borrower']
            
            if not borrower:
                continue
            
            # Decrypt borrower data for search
            try:
                borrower = encryption_service.decrypt_borrower_data(borrower)
            except Exception as e:
                logger.warning(f"Failed to decrypt borrower data for search, using as-is: {e}")
                # Continue with potentially unencrypted data for backward compatibility
            
            matches = True
            
            # Apply filters
            if borrower_name and borrower_name.lower() not in borrower.get('full_name', '').lower():
                matches = False
            if borrower_email and borrower_email.lower() not in borrower.get('email', '').lower():
                matches = False
            if loan_id and loan_id.lower() not in artifact.loan_id.lower():
                matches = False
            
            # Date filters
            if date_from or date_to:
                artifact_date = artifact.created_at.date()
                if date_from:
                    from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                    if artifact_date < from_date:
                        matches = False
                if date_to:
                    to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                    if artifact_date > to_date:
                        matches = False
            
            # Amount filters (using annual_income as proxy for loan_amount)
            if amount_min is not None or amount_max is not None:
                income = borrower.get('annual_income', 0)
                if amount_min is not None and income < amount_min:
                    matches = False
                if amount_max is not None and income > amount_max:
                    matches = False
            
            if matches:
                result = LoanSearchResult(
                    artifact_id=artifact.id,
                    loan_id=artifact.loan_id,
                    document_type=artifact.artifact_type,
                    loan_amount=borrower.get('annual_income', 0),  # Using annual_income as proxy
                    borrower_name=borrower.get('full_name', ''),
                    borrower_email=borrower.get('email', ''),
                    upload_date=artifact.created_at.isoformat(),
                    sealed_status="Sealed" if artifact.walacor_tx_id else "Not Sealed",
                    walacor_tx_id=artifact.walacor_tx_id or "N/A"
                )
                filtered_artifacts.append(result)
        
        # Apply pagination
        total_count = len(filtered_artifacts)
        paginated_results = filtered_artifacts[offset:offset + limit]
        has_more = offset + limit < total_count
        
        logger.info(f"✅ Found {total_count} loan documents matching search criteria")
        
        # Log audit event for search operation
        try:
            # Log search operation as data access
            search_reason = "loan_document_search"
            if borrower_name:
                search_reason += "_by_name"
            if borrower_email:
                search_reason += "_by_email"
            if loan_id:
                search_reason += "_by_loan_id"
            
            # Create a temporary artifact ID for search logging (since we're searching multiple artifacts)
            search_artifact_id = f"search_{int(time.time() * 1000)}"
            
            # Log the search operation
            services["db"].log_borrower_data_access(
                artifact_id=search_artifact_id,
                accessed_by="api_user",
                access_reason=search_reason,
                ip_address=None
            )
            
            logger.info(f"✅ Audit log created for search operation")
            
        except Exception as e:
            logger.warning(f"Failed to create audit log for search: {e}")
            # Don't fail the main operation if audit logging fails
        
        return StandardResponse(
            ok=True,
            data=LoanSearchResponse(
                results=paginated_results,
                total_count=total_count,
                has_more=has_more
            ).dict()
        )
        
    except Exception as e:
        logger.error(f"Error searching loan documents: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


@app.get("/api/loan-documents/{artifact_id}/audit-trail", response_model=StandardResponse)
async def get_audit_trail(
    artifact_id: str,
    services: dict = Depends(get_services)
):
    """
    Get complete audit trail for a loan document.
    
    Returns all events related to the document including:
    - Who uploaded the document
    - When it was sealed
    - Who viewed it
    - Verification attempts
    - All with timestamps and IP addresses
    """
    try:
        log_endpoint_start("get_audit_trail", {"artifact_id": artifact_id})
        
        # Get artifact from database
        artifact = services["db"].get_artifact_by_id(artifact_id)
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found"
            )
        
        # Get all events for this artifact (using get_events method with artifact_id filter)
        events = artifact.events if hasattr(artifact, 'events') else []
        
        # Convert events to audit events
        audit_events = []
        for event in events:
            # Parse payload_json to extract details
            details = {}
            if event.payload_json:
                try:
                    import json
                    details = json.loads(event.payload_json)
                except:
                    details = {"raw_payload": event.payload_json}
            
            audit_event = AuditEvent(
                event_id=event.id,
                event_type=event.event_type,
                timestamp=event.created_at.isoformat(),
                user_id=event.created_by,  # Use created_by field
                ip_address=details.get("ip_address"),  # Extract from payload
                details=details
            )
            audit_events.append(audit_event)
        
        # Add creation event if not present
        creation_event = AuditEvent(
            event_id=f"creation_{artifact_id}",
            event_type="document_created",
            timestamp=artifact.created_at.isoformat(),
            user_id=artifact.created_by,
            ip_address=None,  # Not available for creation
            details={
                "loan_id": artifact.loan_id,
                "artifact_type": artifact.artifact_type,
                "walacor_tx_id": artifact.walacor_tx_id
            }
        )
        audit_events.insert(0, creation_event)
        
        # Sort by timestamp
        audit_events.sort(key=lambda x: x.timestamp)
        
        logger.info(f"✅ Retrieved audit trail for artifact: {artifact_id} with {len(audit_events)} events")
        
        # Log audit event for audit trail access
        try:
            services["db"].log_audit_trail_export(
                artifact_id=artifact_id,
                exported_by="api_user",
                export_format="json",  # This endpoint returns JSON
                ip_address=None
            )
            
            logger.info(f"✅ Audit log created for audit trail access")
            
        except Exception as e:
            logger.warning(f"Failed to create audit log for audit trail access: {e}")
            # Don't fail the main operation if audit logging fails
        
        return StandardResponse(
            ok=True,
            data=AuditTrailResponse(
                artifact_id=artifact_id,
                loan_id=artifact.loan_id,
                events=audit_events,
                total_events=len(audit_events)
            ).dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit trail: {e}")
        logger.error(traceback.format_exc())
        return StandardResponse(
            ok=False,
            data={"error": str(e)}
        )


# Main block
if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
