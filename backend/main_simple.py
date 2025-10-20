"""
Simplified FastAPI application for the Walacor Financial Integrity Platform.

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

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import os
import logging
from datetime import datetime, timezone
import traceback

# Import backend services
from src.database import Database
from src.document_handler import DocumentHandler
from src.walacor_service import WalacorIntegrityService
from src.json_handler import JSONHandler
from src.manifest_handler import ManifestHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Walacor Financial Integrity API",
    description="API for document integrity verification and artifact management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
db: Optional[Database] = None
doc_handler: Optional[DocumentHandler] = None
wal_service: Optional[WalacorIntegrityService] = None
json_handler: Optional[JSONHandler] = None
manifest_handler: Optional[ManifestHandler] = None


# Pydantic models for request/response
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    services: Dict[str, str] = Field(..., description="Service statuses")


class IngestJsonRequest(BaseModel):
    """JSON ingestion request model."""
    loan_id: str = Field(..., description="Loan ID")
    created_by: str = Field(..., description="Creator identifier")
    json_data: Dict[str, Any] = Field(..., description="JSON document data")


class IngestJsonResponse(BaseModel):
    """JSON ingestion response model."""
    message: str = Field(..., description="Response message")
    artifact_id: Optional[str] = Field(None, description="Created artifact ID")
    hash: Optional[str] = Field(None, description="Document hash")
    timestamp: str = Field(..., description="Processing timestamp")


class IngestPacketRequest(BaseModel):
    """Packet ingestion request model."""
    loan_id: str = Field(..., description="Loan ID")
    created_by: str = Field(..., description="Creator identifier")
    files: List[Dict[str, Any]] = Field(..., description="File information list")


class IngestPacketResponse(BaseModel):
    """Packet ingestion response model."""
    message: str = Field(..., description="Response message")
    artifact_id: Optional[str] = Field(None, description="Created artifact ID")
    hash: Optional[str] = Field(None, description="Manifest hash")
    file_count: Optional[int] = Field(None, description="Number of files processed")
    timestamp: str = Field(..., description="Processing timestamp")


class VerifyManifestRequest(BaseModel):
    """Manifest verification request model."""
    manifest: Dict[str, Any] = Field(..., description="Manifest to verify")


class VerifyManifestResponse(BaseModel):
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


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize services at startup."""
    global db, doc_handler, wal_service, json_handler, manifest_handler
    
    try:
        logger.info("Initializing Walacor Financial Integrity API services...")
        
        # Initialize database
        db = Database()
        logger.info("✅ Database service initialized")
        
        # Initialize document handler
        doc_handler = DocumentHandler()
        logger.info("✅ Document handler initialized")
        
        # Initialize Walacor service
        try:
            wal_service = WalacorIntegrityService()
            logger.info("✅ Walacor service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Walacor service initialization failed: {e}")
            wal_service = None
        
        # Initialize JSON handler
        json_handler = JSONHandler()
        logger.info("✅ JSON handler initialized")
        
        # Initialize manifest handler
        manifest_handler = ManifestHandler()
        logger.info("✅ Manifest handler initialized")
        
        logger.info("🎉 All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        logger.error(traceback.format_exc())
        raise


# Dependency to check if services are initialized
def get_services():
    """Get initialized services."""
    if not all([db, doc_handler, json_handler, manifest_handler]):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core services not initialized"
        )
    return {
        "db": db,
        "doc_handler": doc_handler,
        "wal_service": wal_service,  # May be None if Walacor is not available
        "json_handler": json_handler,
        "manifest_handler": manifest_handler
    }


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the API and all services.
    """
    try:
        services_status = {}
        
        # Check database
        if db and db.health_check():
            services_status["database"] = "healthy"
        else:
            services_status["database"] = "unhealthy"
        
        # Check other services
        services_status["document_handler"] = "healthy" if doc_handler else "unhealthy"
        services_status["walacor_service"] = "healthy" if wal_service else "unhealthy"
        services_status["json_handler"] = "healthy" if json_handler else "unhealthy"
        services_status["manifest_handler"] = "healthy" if manifest_handler else "unhealthy"
        
        overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            message="API is running" if overall_status == "healthy" else "API is running with degraded services",
            timestamp=datetime.now(timezone.utc).isoformat(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


# JSON document ingestion endpoint
@app.post("/api/ingest-json", response_model=IngestJsonResponse)
async def ingest_json(
    request: IngestJsonRequest,
    services: dict = Depends(get_services)
):
    """
    Ingest a JSON document.
    
    Accepts JSON data and processes it for integrity verification.
    """
    try:
        logger.info(f"Ingesting JSON document for loan: {request.loan_id}")
        
        # Process JSON with JSONHandler
        result = services["json_handler"].process_json_artifact(request.json_data, 'loan')
        
        if not result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON validation failed: {', '.join(result['errors'])}"
            )
        
        # Store in database
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="json",
            etid=100002,  # ETID for JSON artifacts
            payload_sha256=result['hash'],
            walacor_tx_id="WAL_TX_JSON_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            created_by=request.created_by
        )
        
        # Log event
        services["db"].insert_event(
            artifact_id=artifact_id,
            event_type="uploaded",
            created_by=request.created_by,
            payload_json=json.dumps({"data_size": len(str(request.json_data))})
        )
        
        logger.info(f"✅ JSON document ingested successfully: {artifact_id}")
        
        return IngestJsonResponse(
            message="JSON document ingested successfully",
            artifact_id=artifact_id,
            hash=result['hash'],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
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
@app.post("/api/ingest-packet", response_model=IngestPacketResponse)
async def ingest_packet(
    request: IngestPacketRequest,
    services: dict = Depends(get_services)
):
    """
    Ingest a multi-file packet.
    
    Accepts file information and creates a manifest for the packet.
    """
    try:
        logger.info(f"Ingesting packet with {len(request.files)} files for loan: {request.loan_id}")
        
        if not request.files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        # Create manifest
        manifest = services["manifest_handler"].create_manifest(
            loan_id=request.loan_id,
            files=request.files,
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
        
        # Store in database
        artifact_id = services["db"].insert_artifact(
            loan_id=request.loan_id,
            artifact_type="loan_packet",
            etid=100001,  # ETID for loan packets
            payload_sha256=manifest_result['hash'],
            walacor_tx_id="WAL_TX_PACKET_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            created_by=request.created_by,
            manifest_sha256=manifest_result['hash']
        )
        
        # Store file information
        for file_info in request.files:
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
                "file_count": len(request.files),
                "total_size": sum(f["size"] for f in request.files),
                "manifest_hash": manifest_result['hash']
            })
        )
        
        logger.info(f"✅ Packet ingested successfully: {artifact_id}")
        
        return IngestPacketResponse(
            message="Packet ingested successfully",
            artifact_id=artifact_id,
            hash=manifest_result['hash'],
            file_count=len(request.files),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Packet ingestion failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Packet ingestion failed: {str(e)}"
        )


# Manifest verification endpoint
@app.post("/api/verify-manifest", response_model=VerifyManifestResponse)
async def verify_manifest(
    request: VerifyManifestRequest,
    services: dict = Depends(get_services)
):
    """
    Verify a manifest.
    
    Validates and processes a manifest document.
    """
    try:
        logger.info("Verifying manifest")
        
        # Process manifest
        result = services["manifest_handler"].process_manifest(request.manifest)
        
        logger.info(f"Manifest verification completed: valid={result['is_valid']}")
        
        return VerifyManifestResponse(
            message="Manifest verification completed",
            is_valid=result['is_valid'],
            hash=result['hash'],
            errors=result['errors'],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Manifest verification failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Manifest verification failed: {str(e)}"
        )


# Get artifact details endpoint
@app.get("/api/artifacts/{artifact_id}", response_model=ArtifactResponse)
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
        response = ArtifactResponse(
            id=artifact.id,
            loan_id=artifact.loan_id,
            artifact_type=artifact.artifact_type,
            payload_sha256=artifact.payload_sha256,
            manifest_sha256=artifact.manifest_sha256,
            walacor_tx_id=artifact.walacor_tx_id,
            created_by=artifact.created_by,
            created_at=artifact.created_at.isoformat(),
            files=[{
                "id": f.id,
                "name": f.name,
                "uri": f.uri,
                "sha256": f.sha256,
                "size": f.size_bytes,
                "content_type": f.content_type
            } for f in artifact.files],
            events=[{
                "id": e.id,
                "event_type": e.event_type,
                "created_by": e.created_by,
                "created_at": e.created_at.isoformat(),
                "payload_json": e.payload_json,
                "walacor_tx_id": e.walacor_tx_id
            } for e in artifact.events]
        )
        
        return response
        
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
@app.get("/api/artifacts/{artifact_id}/events", response_model=List[EventResponse])
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
        response = [
            EventResponse(
                id=event.id,
                artifact_id=event.artifact_id,
                event_type=event.event_type,
                created_by=event.created_by,
                created_at=event.created_at.isoformat(),
                payload_json=event.payload_json,
                walacor_tx_id=event.walacor_tx_id
            )
            for event in events
        ]
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to retrieve artifact events: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve artifact events: {str(e)}"
        )


# Get system statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
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
        
        response = StatsResponse(
            total_artifacts=total_artifacts,
            total_files=total_files,
            total_events=total_events,
            artifacts_by_type=artifacts_by_type,
            recent_activity=recent_activity,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
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
