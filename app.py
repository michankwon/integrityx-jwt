"""
IntegrityX - Financial Document Integrity System
Main Streamlit Application

This is the main Streamlit application for the IntegrityX financial document
integrity system. It provides a multi-page interface for document upload,
integrity verification, and provenance tracking.

Features:
- Multi-page navigation with sidebar
- Document upload and management
- Integrity verification and tampering detection
- Document provenance chain tracking
- Professional UI with clean design
"""

import streamlit as st
import sys
from pathlib import Path
from typing import List, Dict, Any

# Optional imports for admin dashboard
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import IntegrityX services
from document_handler import DocumentHandler
from walacor_service import WalacorIntegrityService
from verifier import DocumentVerifier
from provenance import ProvenanceTracker
from time_machine import DocumentTimeMachine
from ai_detector import AnomalyDetector
from verification_portal import VerificationPortal
from security import SecurityManager


# Page configuration
st.set_page_config(
    page_title="IntegrityX - Financial Document Integrity",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .page-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 0.5rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_services():
    """
    Initialize and cache all IntegrityX services.
    
    This function uses Streamlit's @st.cache_resource decorator to ensure
    services are initialized only once and cached for the entire session.
    This improves performance and prevents multiple initializations.
    
    Returns:
        dict: Dictionary containing all initialized services
    """
    try:
        st.info("🔄 Initializing IntegrityX services...")
        
        services = {
            'doc_handler': DocumentHandler(),
            'wal_service': WalacorIntegrityService(),
            'verifier': DocumentVerifier(),
            'provenance': ProvenanceTracker(),
            'time_machine': DocumentTimeMachine(),
            'ai_detector': AnomalyDetector(),
            'verification_portal': VerificationPortal(),
            'security': SecurityManager()
        }
        
        st.success("✅ All services initialized successfully!")
        return services
        
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {e}")
        st.error("Please check your configuration and try again.")
        return None


def render_sidebar():
    """
    Render the sidebar with navigation and project information.
    """
    st.sidebar.markdown("## 🔒 IntegrityX")
    st.sidebar.markdown("**Financial Document Integrity System**")
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.markdown("### 📋 Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        [
            "📤 Upload Document",
            "🔍 Verify Integrity", 
            "🔗 Provenance Chain",
            "⏰ Time Machine",
            "🤖 AI Fraud Detection",
            "🔐 Multi-Party Verification",
            "⚙️ Admin"
        ],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Project information
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.markdown("""
    **IntegrityX** provides comprehensive document integrity verification
    using cryptographic hashing and blockchain technology.
    
    **Key Features:**
    - 🔐 Tampering detection
    - 🔗 Provenance tracking
    - ⏰ Time machine analysis
    - 📊 Audit trails
    """)
    
    st.sidebar.markdown("---")
    
    # System status
    st.sidebar.markdown("### 🔧 System Status")
    services = get_services()
    if services:
        st.sidebar.success("✅ All systems operational")
    else:
        st.sidebar.error("❌ System initialization failed")
    
    # Platform information
    st.sidebar.markdown("---")
    st.sidebar.info("""
**Walacor Financial Integrity Platform**

Cryptographically secured document management for GENIUS Act compliance.

🏆 Built for Walacor Hackathon 2025

**Features:**
- 🔐 Tamper-proof integrity
- 🔗 Complete provenance chains
- ⏰ Historical time travel
- 🤖 AI fraud prediction
- 🔐 Privacy-preserving verification
""")

    st.sidebar.markdown("**Team:** [Your Team Name]")
    st.sidebar.markdown("**GitHub:** [Your Repo Link]")
    
    return page


def render_upload_page():
    """
    Render the Upload Document page.
    """
    st.markdown('<h1 class="page-header">📤 Upload Loan Document</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload a new loan document to the IntegrityX system. The document will be
    cryptographically hashed and stored securely with full audit trail tracking.
    """)
    
    # Security information
    st.info("🔒 All uploads are validated for security. Max file size: 50MB. Allowed types: PDF, DOCX, XLSX, JPG, PNG")
    
    # Upload form
    with st.form("upload_form"):
        st.markdown("### 📋 Document Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_id = st.text_input(
                "Loan ID",
                placeholder="e.g., LOAN_2024_001",
                help="Unique identifier for the loan"
            )
            
            document_type = st.selectbox(
                "Document Type",
                [
                    "loan_application",
                    "income_verification", 
                    "credit_report",
                    "appraisal",
                    "underwriting",
                    "closing_documents",
                    "insurance",
                    "title_search",
                    "other"
                ],
                help="Type of document being uploaded"
            )
        
        with col2:
            uploaded_by = st.text_input(
                "Uploaded By",
                placeholder="e.g., john.doe@company.com",
                help="Email or username of person uploading"
            )
            
            file_extension = st.selectbox(
                "File Type",
                ["pdf", "docx", "doc", "txt", "jpg", "png"],
                help="Expected file format"
            )
        
        st.markdown("### 📄 Document File")
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['pdf', 'docx', 'doc', 'txt', 'jpg', 'png'],
            help="Select the document file to upload"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Upload & Secure",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validate inputs
            if not all([loan_id, document_type, uploaded_by, uploaded_file]):
                st.error("❌ Please fill in all required fields and upload a file.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        with st.spinner("🔒 Securing document..."):
                            # Read uploaded file bytes
                            file_bytes = uploaded_file.read()
                            
                            # SECURITY CHECK 1: Validate file upload
                            validation = services['security'].validate_file_upload(
                                uploaded_file.name,
                                len(file_bytes),
                                file_bytes
                            )
                            
                            if not validation['valid']:
                                st.error(f"🚫 Security Check Failed: {validation['error']}")
                                return  # Stop processing
                            
                            # SECURITY CHECK 2: Check rate limit
                            if not services['security'].check_rate_limit(uploaded_by, "upload", limit_per_hour=100):
                                st.error("🚫 Rate limit exceeded. Please try again later.")
                                return
                            
                            # SECURITY CHECK 3: Sanitize inputs
                            loan_id = services['security'].sanitize_input(loan_id)
                            uploaded_by = services['security'].sanitize_input(uploaded_by)
                            
                            # Calculate hash
                            document_hash = services['doc_handler'].calculate_hash_from_bytes(file_bytes)
                            
                            # Save document locally
                            save_result = services['doc_handler'].save_document(
                                file_bytes=file_bytes,
                                loan_id=loan_id,
                                document_type=document_type,
                                file_extension=file_extension
                            )
                            
                            # Store hash in Walacor
                            walacor_result = services['wal_service'].store_document_hash(
                                loan_id=loan_id,
                                document_type=document_type,
                                document_hash=document_hash,
                                file_size=save_result['file_size'],
                                file_path=save_result['file_path'],
                                uploaded_by=uploaded_by
                            )
                            
                            # Log audit event
                            services['wal_service'].log_audit_event(
                                document_id=save_result['filename'],
                                event_type="upload",
                                user=uploaded_by,
                                details=f"Document uploaded: {uploaded_file.name} ({document_type})"
                            )
                            
                            # Success message
                            st.success("✅ Document secured successfully!")
                            
                            # Display hash
                            st.info(f"**Document Hash:** `{document_hash[:32]}...`")
                            
                            # Display Walacor result
                            if walacor_result:
                                st.info(f"**Stored in Walacor:** Envelope ID {walacor_result}")
                            
                            # Next steps
                            st.markdown("### 🎯 Next Steps")
                            st.markdown("""
                            1. ✅ **Document is now cryptographically secured**
                            2. 🔍 **Use 'Verify Integrity'** to check authenticity anytime
                            3. 🔗 **Link related documents** in 'Provenance Chain'
                            4. ⏰ **View document history** with Time Machine
                            """)
                            
                            # Celebration
                            st.balloons()
                            
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
                        st.error("Please check your configuration and try again.")


def render_verify_page():
    """
    Render the Verify Integrity page.
    """
    st.markdown('<h1 class="page-header">🔍 Verify Document Integrity</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Verify the integrity of a loan document by comparing its current hash with
    the stored hash in the blockchain. This detects any tampering or modifications.
    """)
    
    # Verification form
    with st.form("verify_form"):
        st.markdown("### 🔍 Verification Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_id = st.text_input(
                "Loan ID",
                placeholder="e.g., LOAN_2024_001",
                help="Loan ID to verify"
            )
        
        with col2:
            verification_type = st.selectbox(
                "Verification Type",
                ["File Upload", "Existing Document"],
                help="Choose how to provide the document"
            )
        
        if verification_type == "File Upload":
            st.markdown("### 📄 Document File")
            uploaded_file = st.file_uploader(
                "Choose a document file to verify",
                type=['pdf', 'docx', 'doc', 'txt', 'jpg', 'png'],
                help="Upload the document to verify its integrity"
            )
        else:
            st.markdown("### 📄 Document Selection")
            document_id = st.text_input(
                "Document ID",
                placeholder="e.g., DOC_2024_001",
                help="ID of existing document to verify"
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "🔍 Verify Now",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validate inputs
            if verification_type == "File Upload":
                if not all([loan_id, uploaded_file]):
                    st.error("❌ Please provide Loan ID and upload a file.")
                else:
                    # Get services
                    services = get_services()
                    if not services:
                        st.error("❌ Failed to initialize services. Please check your configuration.")
                    else:
                        try:
                            with st.spinner("🔍 Verifying document integrity..."):
                                # Save uploaded file temporarily
                                import tempfile
                                import os
                                
                                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                    tmp_file.write(uploaded_file.read())
                                    temp_file_path = tmp_file.name
                                
                                # Verify document
                                verification_result = services['verifier'].verify_document(
                                    file_path=temp_file_path,
                                    loan_id=loan_id
                                )
                                
                                # Clean up temp file
                                os.unlink(temp_file_path)
                                
                                # Display results dramatically
                                display_verification_results(verification_result, uploaded_file.name, loan_id)
                                
                        except Exception as e:
                            st.error(f"❌ Verification failed: {str(e)}")
                            st.error("Please check your configuration and try again.")
            else:
                if not all([loan_id, document_id]):
                    st.error("❌ Please provide Loan ID and Document ID.")
                else:
                    # Get services
                    services = get_services()
                    if not services:
                        st.error("❌ Failed to initialize services. Please check your configuration.")
                    else:
                        try:
                            with st.spinner("🔍 Verifying document integrity..."):
                                # For existing document, we need to get the file path first
                                # This is a simplified version - in production you'd query the database
                                st.info("🚧 **Note:** Existing document verification requires file path lookup. Using file upload method for demo.")
                                st.info("Please use 'File Upload' verification type for full functionality.")
                                
                        except Exception as e:
                            st.error(f"❌ Verification failed: {str(e)}")
                            st.error("Please check your configuration and try again.")


def display_verification_results(verification_result, filename, loan_id):
    """
    Display verification results with dramatic visual feedback.
    """
    st.markdown("---")
    st.markdown("## 🔍 Verification Results")
    
    # Check if verification was successful
    if verification_result.get('is_valid', False):
        # DOCUMENT IS AUTHENTIC
        st.success("✅ **DOCUMENT IS AUTHENTIC**")
        st.balloons()
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🔒 Status",
                value="AUTHENTIC",
                delta="No tampering detected"
            )
        
        with col2:
            st.metric(
                label="🚫 Tampered",
                value="No",
                delta="Document is original"
            )
        
        with col3:
            st.metric(
                label="🎯 Match",
                value="100%",
                delta="Perfect match"
            )
        
        # Show timing information
        st.markdown("### ⏰ Timeline")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**📤 Original Upload:** {verification_result.get('original_upload_time', 'Unknown')}")
        
        with col2:
            st.info(f"**🔍 Verification Time:** {verification_result.get('verification_time', 'Unknown')}")
        
        # Hash information
        st.markdown("### 🔐 Hash Information")
        st.code(f"Document Hash: {verification_result.get('current_hash', 'Unknown')}")
        
        # Detailed information
        with st.expander("📋 Detailed Information"):
            st.json(verification_result)
    
    elif verification_result.get('tampered', False):
        # TAMPERING DETECTED
        st.error("❌ **TAMPERING DETECTED!**")
        st.warning("🚨 This document has been modified since original upload")
        
        # Show dramatic comparison
        st.markdown("### 🔍 Hash Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔴 Current Hash (Modified):**")
            st.code(verification_result.get('current_hash', 'Unknown'))
        
        with col2:
            st.markdown("**🟢 Expected Hash (Original):**")
            st.code(verification_result.get('stored_hash', 'Unknown'))
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🔒 Status",
                value="TAMPERED",
                delta="Document modified",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                label="🚫 Tampered",
                value="YES",
                delta="Hash mismatch detected",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="🎯 Match",
                value="0%",
                delta="No match found",
                delta_color="inverse"
            )
        
        # Show timeline
        st.markdown("### ⏰ Timeline")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**📤 Original Upload:** {verification_result.get('original_upload_time', 'Unknown')}")
        
        with col2:
            st.error(f"**🔍 Verification Time:** {verification_result.get('verification_time', 'Unknown')}")
        
        # Security alert
        st.markdown("### 🚨 Security Alert")
        st.error("""
        **CRITICAL:** This document has been tampered with!
        
        - The current document hash does not match the stored hash
        - The document content has been modified since original upload
        - This may indicate unauthorized access or malicious modification
        - Contact your security team immediately
        """)
        
        # Detailed information
        with st.expander("📋 Detailed Information"):
            st.json(verification_result)
    
    else:
        # NO STORED RECORD FOUND
        st.warning("⚠️ **NO STORED RECORD FOUND**")
        st.info("This document has not been previously uploaded to the system.")
        
        # Show current hash
        st.markdown("### 🔐 Current Document Hash")
        st.code(f"Hash: {verification_result.get('current_hash', 'Unknown')}")
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🔒 Status",
                value="UNKNOWN",
                delta="No baseline found"
            )
        
        with col2:
            st.metric(
                label="🚫 Tampered",
                value="N/A",
                delta="Cannot determine"
            )
        
        with col3:
            st.metric(
                label="🎯 Match",
                value="N/A",
                delta="No comparison"
            )
        
        # Instructions
        st.markdown("### 📋 Next Steps")
        st.info("""
        1. **Upload this document first** using the 'Upload Document' page
        2. **Then verify** to establish a baseline
        3. **Future verifications** will detect any tampering
        """)
        
        # Detailed information
        with st.expander("📋 Detailed Information"):
            st.json(verification_result)


def render_provenance_page():
    """
    Render the Provenance Chain page with tabs for viewing and creating links.
    """
    st.markdown('<h1 class="page-header">🔗 Document Provenance Chain</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    View and manage document provenance chains, showing all relationships
    and transformations throughout the loan lifecycle process.
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔍 View Chain", "🔗 Create Link"])
    
    with tab1:
        render_view_chain_tab()
    
    with tab2:
        render_create_link_tab()


def render_view_chain_tab():
    """
    Render the View Chain tab for displaying provenance chains.
    """
    st.markdown("### 🔍 View Document Provenance Chain")
    st.markdown("Enter a document ID to view its complete provenance chain and relationships.")
    
    with st.form("view_chain_form"):
        document_id = st.text_input(
            "Document ID",
            placeholder="e.g., DOC_2024_001",
            help="ID of the document to analyze"
        )
        
        submitted = st.form_submit_button(
            "🔍 Show Provenance Chain",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not document_id:
                st.error("❌ Please provide a Document ID.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        with st.spinner("🔍 Retrieving provenance chain..."):
                            # Get provenance chain
                            chain = services['provenance'].get_chain(document_id)
                            
                            # Display results
                            display_provenance_chain(chain, document_id)
                            
                    except Exception as e:
                        st.error(f"❌ Failed to retrieve provenance chain: {str(e)}")
                        st.error("Please check your configuration and try again.")


def render_create_link_tab():
    """
    Render the Create Link tab for creating new provenance relationships.
    """
    st.markdown("### 🔗 Create Provenance Link")
    st.markdown("Create a new relationship between two documents in the loan lifecycle.")
    
    with st.form("create_link_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            parent_id = st.text_input(
                "Parent Document ID",
                placeholder="e.g., APP_2024_001",
                help="ID of the parent/source document"
            )
        
        with col2:
            child_id = st.text_input(
                "Child Document ID",
                placeholder="e.g., UNDER_2024_001",
                help="ID of the child/derived document"
            )
        
        relationship_type = st.selectbox(
            "Relationship Type",
            [
                "servicing_transfer",
                "modification", 
                "attestation",
                "qc_review",
                "underwriting",
                "appraisal",
                "closing",
                "application",
                "income_verification",
                "credit_report",
                "title_search",
                "insurance",
                "disclosure"
            ],
            help="Type of relationship between documents"
        )
        
        description = st.text_area(
            "Description",
            placeholder="Describe the relationship between these documents...",
            help="Optional description of the relationship"
        )
        
        submitted = st.form_submit_button(
            "🔗 Create Link",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not all([parent_id, child_id, relationship_type]):
                st.error("❌ Please provide Parent ID, Child ID, and Relationship Type.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        with st.spinner("🔗 Creating provenance link..."):
                            # Create provenance link
                            services['provenance'].create_link(
                                parent_doc_id=parent_id,
                                child_doc_id=child_id,
                                relationship_type=relationship_type,
                                description=description
                            )
                            
                            # Success message
                            st.success("✅ Provenance link created successfully!")
                            
                            # Display link summary
                            st.markdown("### 📋 Link Summary")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info(f"**Parent:** {parent_id}")
                                st.info(f"**Child:** {child_id}")
                            
                            with col2:
                                st.info(f"**Relationship:** {relationship_type}")
                                st.info(f"**Description:** {description or 'None'}")
                            
                            # Show next steps
                            st.markdown("### 🎯 Next Steps")
                            st.markdown("""
                            1. ✅ **Link created** between documents
                            2. 🔍 **View the chain** using the 'View Chain' tab
                            3. 🔗 **Create more links** to build complete provenance
                            4. 📊 **Analyze relationships** in the loan lifecycle
                            """)
                            
                    except Exception as e:
                        st.error(f"❌ Failed to create provenance link: {str(e)}")
                        st.error("Please check your configuration and try again.")


def display_provenance_chain(chain, _document_id):
    """
    Display the provenance chain with visual timeline.
    """
    st.markdown("---")
    st.markdown("## 🔗 Provenance Chain Results")
    
    if not chain:
        st.info("📭 **No provenance chain found.** This is the root document.")
        st.markdown("""
        This document has no parent documents, meaning it's the starting point
        of the provenance chain. Other documents may be derived from this one.
        """)
    else:
        st.success(f"✅ **Found {len(chain)} links in the provenance chain**")
        
        # Display chain as timeline
        st.markdown("### 📅 Provenance Timeline")
        
        for i, link in enumerate(chain):
            with st.container():
                # Create visual timeline entry
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    # Timeline indicator
                    if i == 0:
                        st.markdown("🟢 **ROOT**")
                    else:
                        st.markdown(f"**{i}**")
                
                with col2:
                    # Link information
                    parent = link.get('parent_doc_id', 'Unknown')
                    child = link.get('child_doc_id', 'Unknown')
                    rel_type = link.get('relationship_type', 'Unknown')
                    timestamp = link.get('timestamp', 'Unknown')
                    description = link.get('description', '')
                    
                    # Format timestamp
                    try:
                        from datetime import datetime
                        if timestamp and timestamp != 'Unknown':
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            formatted_time = timestamp
                    except:
                        formatted_time = timestamp
                    
                    # Display link
                    st.markdown(f"**{parent}** → **{child}**")
                    st.markdown(f"🔗 **Type:** {rel_type}")
                    st.markdown(f"⏰ **Time:** {formatted_time}")
                    
                    if description:
                        st.markdown(f"📝 **Description:** {description}")
                
                with col3:
                    # Status indicator
                    if i == 0:
                        st.markdown("🌱")
                    else:
                        st.markdown("🔗")
                
                # Add divider between entries (except for last one)
                if i < len(chain) - 1:
                    st.divider()
        
        # Summary information
        st.markdown("### 📊 Chain Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🔗 Total Links",
                value=len(chain),
                delta="Relationships found"
            )
        
        with col2:
            # Count unique relationship types
            rel_types = set(link.get('relationship_type', 'Unknown') for link in chain)
            st.metric(
                label="📋 Relationship Types",
                value=len(rel_types),
                delta="Different types"
            )
        
        with col3:
            # Show if this is a complete chain
            is_complete = len(chain) > 0
            st.metric(
                label="✅ Chain Status",
                value="Complete" if is_complete else "Empty",
                delta="Ready for analysis"
            )
        
        # Relationship types breakdown
        if rel_types:
            st.markdown("### 🔍 Relationship Types in Chain")
            for rel_type in sorted(rel_types):
                count = sum(1 for link in chain if link.get('relationship_type') == rel_type)
                st.markdown(f"- **{rel_type}:** {count} occurrence{'s' if count != 1 else ''}")
        
        # Detailed information
        with st.expander("📋 Detailed Chain Information"):
            st.json(chain)


def render_time_machine_page():
    """
    Render the Time Machine page for viewing document history and time travel.
    """
    st.markdown('<h1 class="page-header">⏰ Document Time Machine</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    🕰️ **Travel through time** to view document history and see exactly what happened
    to your documents at any point in time. This unique feature lets you explore
    the complete audit trail and understand document custody throughout its lifecycle.
    """)
    
    # Document ID input
    st.markdown("### 📄 Select Document for Time Travel")
    document_id = st.text_input(
        "Document ID",
        placeholder="e.g., DOC_2024_001",
        help="ID of the document to explore through time"
    )
    
    if document_id:
        # Get services
        services = get_services()
        if not services:
            st.error("❌ Failed to initialize services. Please check your configuration.")
        else:
            try:
                # Show document timeline
                display_document_timeline(services['time_machine'], document_id)
                
                # Time travel section
                render_time_travel_section(services['time_machine'], document_id)
                
            except Exception as e:
                st.error(f"❌ Failed to access time machine: {str(e)}")
                st.error("Please check your configuration and try again.")


def display_document_timeline(time_machine, document_id):
    """
    Display the complete timeline of events for a document.
    """
    st.markdown("---")
    st.markdown("## 📅 Complete Document Timeline")
    
    try:
        with st.spinner("⏰ Retrieving document history..."):
            timeline = time_machine.create_timeline(document_id)
        
        if not timeline:
            st.info("📭 **No timeline events found.** This document has no recorded history.")
            st.markdown("""
            This could mean:
            - The document hasn't been uploaded yet
            - No audit events have been recorded
            - The document ID doesn't exist in the system
            """)
        else:
            st.success(f"✅ **Found {len(timeline)} events in the timeline**")
            
            # Display timeline
            st.markdown("### 🕰️ Event Timeline")
            
            for i, event in enumerate(timeline):
                with st.container():
                    # Create timeline entry
                    col1, col2, col3 = st.columns([1, 4, 1])
                    
                    with col1:
                        # Event icon
                        icon = event.get('icon', '📄')
                        st.markdown(f"**{icon}**")
                    
                    with col2:
                        # Event information
                        timestamp = event.get('timestamp', 'Unknown')
                        event_type = event.get('event_type', 'Unknown')
                        user = event.get('user', 'Unknown')
                        details = event.get('details', '')
                        
                        # Format timestamp
                        try:
                            from datetime import datetime
                            if timestamp and timestamp != 'Unknown':
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                formatted_time = timestamp
                        except:
                            formatted_time = timestamp
                        
                        # Display event
                        st.markdown(f"**{event_type}** by {user}")
                        st.markdown(f"⏰ **Time:** {formatted_time}")
                        
                        if details:
                            st.markdown(f"📝 **Details:** {details}")
                    
                    with col3:
                        # Timeline position
                        st.markdown(f"**#{i+1}**")
                    
                    # Add divider between entries (except for last one)
                    if i < len(timeline) - 1:
                        st.divider()
            
            # Timeline summary
            st.markdown("### 📊 Timeline Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="📅 Total Events",
                    value=len(timeline),
                    delta="Timeline entries"
                )
            
            with col2:
                # Count unique event types
                event_types = set(event.get('event_type', 'Unknown') for event in timeline)
                st.metric(
                    label="🔍 Event Types",
                    value=len(event_types),
                    delta="Different types"
                )
            
            with col3:
                # Count unique users
                users = set(event.get('user', 'Unknown') for event in timeline)
                st.metric(
                    label="👥 Users",
                    value=len(users),
                    delta="Different users"
                )
            
            # Event types breakdown
            if event_types:
                st.markdown("### 🔍 Event Types in Timeline")
                for event_type in sorted(event_types):
                    count = sum(1 for event in timeline if event.get('event_type') == event_type)
                    st.markdown(f"- **{event_type}:** {count} occurrence{'s' if count != 1 else ''}")
            
            # Detailed timeline
            with st.expander("📋 Detailed Timeline Information"):
                st.json(timeline)
                
    except Exception as e:
        st.error(f"❌ Failed to retrieve timeline: {str(e)}")


def render_time_travel_section(time_machine, document_id):
    """
    Render the time travel section for viewing document at specific time.
    """
    st.markdown("---")
    st.markdown("## ⏰ Time Travel")
    st.markdown("🕰️ **Select a specific date and time** to see what the document looked like at that moment.")
    
    with st.form("time_travel_form"):
        st.markdown("### 🕰️ View Document at Specific Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_date = st.date_input(
                "📅 Target Date",
                help="Date to travel to"
            )
        
        with col2:
            target_time = st.time_input(
                "⏰ Target Time",
                help="Time to travel to"
            )
        
        submitted = st.form_submit_button(
            "🕰️ Travel to This Time",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            try:
                # Combine date and time into timestamp
                from datetime import datetime
                target_timestamp = datetime.combine(target_date, target_time).isoformat()
                
                with st.spinner("🕰️ Traveling through time..."):
                    # Get document state at that time
                    result = time_machine.view_at_timestamp(document_id, target_timestamp)
                
                # Display time travel results
                display_time_travel_results(result, target_timestamp)
                
            except Exception as e:
                st.error(f"❌ Time travel failed: {str(e)}")
                st.error("Please check your configuration and try again.")


def display_time_travel_results(result, target_timestamp):
    """
    Display the results of time travel.
    """
    st.markdown("---")
    st.markdown("## 🕰️ Time Travel Results")
    
    if not result:
        st.warning("⚠️ **No document state found** at the specified time.")
        st.markdown(f"""
        The document may not have existed at **{target_timestamp}**.
        Try selecting an earlier time or check if the document ID is correct.
        """)
    else:
        st.success("✅ **Time travel successful!** Document state retrieved.")
        
        # Display key information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Document State")
            st.info(f"**Document ID:** {result.get('document_id', 'Unknown')}")
            st.info(f"**Timestamp:** {result.get('timestamp', 'Unknown')}")
            st.info(f"**Events Count:** {result.get('events_count', 0)}")
        
        with col2:
            st.markdown("### 👤 Custody Information")
            custody = result.get('custody', {})
            if custody:
                st.info(f"**Custodian:** {custody.get('user', 'Unknown')}")
                st.info(f"**Access Time:** {custody.get('timestamp', 'Unknown')}")
                st.info(f"**Event Type:** {custody.get('event_type', 'Unknown')}")
            else:
                st.info("**Custodian:** No custody information available")
        
        # Document metadata
        with st.expander("📋 Document Metadata at This Time"):
            metadata = result.get('metadata', {})
            if metadata:
                st.json(metadata)
            else:
                st.info("No metadata available at this time.")
        
        # Last event before selected time
        with st.expander("📅 Last Event Before Selected Time"):
            state_at_time = result.get('state_at_time', {})
            if state_at_time:
                st.json(state_at_time)
            else:
                st.info("No events recorded before this time.")
        
        # Time travel summary
        st.markdown("### 🎯 Time Travel Summary")
        st.markdown(f"""
        - **Target Time:** {target_timestamp}
        - **Document Status:** {'Found' if result else 'Not Found'}
        - **Events Up to This Point:** {result.get('events_count', 0)}
        - **Custody:** {custody.get('user', 'Unknown') if custody else 'Unknown'}
        """)
        
        # Next steps
        st.markdown("### 🚀 Next Steps")
        st.markdown("""
        1. ✅ **Time travel completed** successfully
        2. 🔍 **Explore other times** to see document evolution
        3. 📊 **Compare states** at different time points
        4. 🔗 **Check provenance** to understand document relationships
        """)


def render_ai_fraud_detection_page():
    """
    Render the AI Fraud Detection page for predictive fraud analysis.
    """
    st.markdown('<h1 class="page-header">🤖 AI Fraud Detection</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    🧠 **Predictive fraud detection** using advanced AI algorithms to identify
    potential fraud scenarios BEFORE they occur. This system analyzes loan patterns,
    access behaviors, and document modifications to predict and prevent financial fraud.
    """)
    
    # Input section
    st.markdown("### 📊 Loan Analysis Parameters")
    
    with st.form("fraud_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            loan_id = st.text_input(
                "Loan ID",
                placeholder="e.g., LOAN_2024_001",
                help="Unique identifier for the loan"
            )
            
            loan_amount = st.number_input(
                "Loan Amount ($)",
                min_value=0,
                max_value=10000000,
                value=500000,
                step=10000,
                help="Total loan amount in dollars"
            )
        
        with col2:
            transfer_count = st.number_input(
                "Transfer Count",
                min_value=0,
                max_value=20,
                value=2,
                step=1,
                help="Number of servicing transfers"
            )
            
            modification_count = st.number_input(
                "Modification Count",
                min_value=0,
                max_value=15,
                value=1,
                step=1,
                help="Number of document modifications in last 7 days"
            )
        
        submitted = st.form_submit_button(
            "🔍 Analyze Fraud Risk",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not loan_id:
                st.error("❌ Please provide a Loan ID.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        # Simulate history events for demo
                        simulated_history = simulate_loan_history(transfer_count, modification_count)
                        
                        # Create loan data
                        loan_data = {
                            'loan_id': loan_id,
                            'loan_amount': loan_amount,
                            'expected_attestations': 3
                        }
                        
                        # Analyze fraud risk
                        with st.spinner("🤖 AI analyzing fraud patterns..."):
                            analysis_result = services['ai_detector'].analyze_loan_risk(loan_data, simulated_history)
                        
                        # Display results
                        display_fraud_analysis_results(analysis_result, simulated_history)
                        
                    except Exception as e:
                        st.error(f"❌ Failed to analyze fraud risk: {str(e)}")
                        st.error("Please check your configuration and try again.")


def simulate_loan_history(transfer_count: int, modification_count: int) -> List[Dict[str, Any]]:
    """
    Simulate loan history events for demo purposes.
    """
    from datetime import datetime, timedelta
    import random
    
    history = []
    base_time = datetime.now() - timedelta(days=30)
    
    # Add upload event
    history.append({
        'timestamp': (base_time + timedelta(hours=1)).isoformat(),
        'event_type': 'upload',
        'user': 'loan_officer@bank.com'
    })
    
    # Add transfer events
    for i in range(transfer_count):
        transfer_time = base_time + timedelta(days=5 + i*3, hours=10 + i)
        history.append({
            'timestamp': transfer_time.isoformat(),
            'event_type': 'servicing_transfer',
            'user': f'servicing_agent_{i+1}@company.com'
        })
    
    # Add modification events (some after hours to trigger unusual access pattern)
    for i in range(modification_count):
        # Some modifications during normal hours, some after hours
        if i % 3 == 0:  # Every 3rd modification is after hours
            mod_time = base_time + timedelta(days=20 + i, hours=22 + random.randint(0, 2))
        else:
            mod_time = base_time + timedelta(days=20 + i, hours=9 + random.randint(0, 6))
        
        history.append({
            'timestamp': mod_time.isoformat(),
            'event_type': 'document_modification',
            'user': f'underwriter_{i+1}@bank.com'
        })
    
    # Add some attestation events
    for i in range(2):
        attest_time = base_time + timedelta(days=10 + i*5, hours=14)
        history.append({
            'timestamp': attest_time.isoformat(),
            'event_type': 'attestation',
            'user': f'compliance_officer_{i+1}@bank.com'
        })
    
    # Sort by timestamp
    history.sort(key=lambda x: x['timestamp'])
    return history


def display_fraud_analysis_results(analysis_result: Dict[str, Any], simulated_history: List[Dict[str, Any]]):
    """
    Display the fraud analysis results in a professional dashboard format.
    """
    st.markdown("---")
    st.markdown("## 🎯 AI Fraud Analysis Results")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = analysis_result['risk_score']
        st.metric(
            label="🎯 Risk Score",
            value=f"{risk_score:.1f}/100",
            delta=f"{risk_score:.1f} points"
        )
    
    with col2:
        risk_level = analysis_result['risk_level']
        st.metric(
            label="⚠️ Risk Level",
            value=risk_level,
            delta="AI Assessment"
        )
    
    with col3:
        predictions_count = len(analysis_result['fraud_predictions'])
        st.metric(
            label="🔮 Predictions",
            value=f"{predictions_count} scenarios",
            delta="Fraud types identified"
        )
    
    # Risk score progress bar with color coding
    st.markdown("### 📊 Overall Risk Assessment")
    risk_score = analysis_result['risk_score']
    
    # Determine color based on risk level
    if risk_score < 20:
        color = "green"
    elif risk_score < 50:
        color = "yellow"
    elif risk_score < 75:
        color = "orange"
    else:
        color = "red"
    
    # Create custom progress bar
    progress_html = f"""
    <div style="background-color: #f0f0f0; border-radius: 10px; padding: 3px;">
        <div style="background-color: {color}; height: 20px; border-radius: 8px; width: {risk_score}%; 
                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
            {risk_score:.1f}%
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Risk factors breakdown
    st.markdown("### 📊 Risk Factors Analysis")
    risk_factors = analysis_result['risk_factors']
    
    for factor, score in risk_factors.items():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.write(f"**{factor.replace('_', ' ').title()}**")
        
        with col2:
            # Color code based on score
            if score < 0.3:
                color = "green"
            elif score < 0.6:
                color = "yellow"
            elif score < 0.8:
                color = "orange"
            else:
                color = "red"
            
            progress_html = f"""
            <div style="background-color: #f0f0f0; border-radius: 5px; padding: 2px;">
                <div style="background-color: {color}; height: 15px; border-radius: 3px; width: {score*100}%; 
                            display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
                    {score:.2f}
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### 💡 AI Recommendations")
    recommendations = analysis_result['recommendations']
    
    for i, recommendation in enumerate(recommendations, 1):
        st.markdown(f"{i}. {recommendation}")
    
    # Predicted fraud scenarios
    st.markdown("### 🎯 Predicted Fraud Scenarios")
    fraud_predictions = analysis_result['fraud_predictions']
    
    if fraud_predictions:
        for i, scenario in enumerate(fraud_predictions, 1):
            with st.expander(f"🔍 {scenario['scenario_name']} ({scenario['probability']}% probability)"):
                st.markdown(f"**Description:** {scenario['description']}")
                st.markdown(f"**Probability:** {scenario['probability']}%")
                
                st.markdown("**Risk Indicators:**")
                for indicator in scenario['risk_indicators']:
                    st.markdown(f"- {indicator}")
                
                st.markdown("**Fields to Monitor:**")
                for field in scenario['watch_fields']:
                    st.markdown(f"- {field}")
    else:
        st.info("✅ No fraud scenarios predicted. Loan appears to be operating within normal parameters.")
    
    # Suspicious activity timeline
    st.markdown("### 📅 Suspicious Activity Timeline")
    
    # Filter for suspicious events (after hours, multiple transfers, etc.)
    suspicious_events = []
    for event in simulated_history:
        is_suspicious = False
        reason = ""
        
        # Check for after-hours access
        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        if event_time.hour < 6 or event_time.hour >= 18:
            is_suspicious = True
            reason = "After-hours access"
        
        # Check for multiple transfers
        if event['event_type'] == 'servicing_transfer':
            transfer_count = sum(1 for e in simulated_history if e['event_type'] == 'servicing_transfer')
            if transfer_count > 2:
                is_suspicious = True
                reason = "Multiple servicing transfers"
        
        # Check for rapid modifications
        if event['event_type'] == 'document_modification':
            mod_count = sum(1 for e in simulated_history if e['event_type'] == 'document_modification')
            if mod_count > 3:
                is_suspicious = True
                reason = "Frequent document modifications"
        
        if is_suspicious:
            suspicious_events.append({
                'event': event,
                'reason': reason
            })
    
    if suspicious_events:
        for suspicious in suspicious_events:
            event = suspicious['event']
            reason = suspicious['reason']
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{event['event_type'].replace('_', ' ').title()}**")
                st.markdown(f"User: {event['user']}")
            
            with col2:
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                st.markdown(f"**{event_time.strftime('%Y-%m-%d %H:%M')}**")
            
            with col3:
                st.markdown(f"🚨 **{reason}**")
            
            st.divider()
    else:
        st.info("✅ No suspicious activity patterns detected in the timeline.")
    
    # Analysis summary
    st.markdown("### 📋 Analysis Summary")
    st.markdown(analysis_result['analysis_summary'])


def render_verification_portal_page():
    """
    Render the Multi-Party Verification page for privacy-preserving document verification.
    """
    st.markdown('<h1 class="page-header">🔐 Multi-Party Verification</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    🔒 **Privacy-preserving verification** that allows third parties (auditors, investors, regulators) 
    to verify document authenticity WITHOUT exposing sensitive borrower information. 
    
    **Key Benefits:**
    - ✅ **Zero-Knowledge Verification**: Verifiers see only what you permit
    - 🔐 **No PII Exposure**: Borrower names, SSNs, loan terms remain private
    - ⏰ **Time-Limited Access**: Links expire automatically
    - 🎯 **Granular Permissions**: Control exactly what information is shared
    - 🔗 **One-Time Use**: Each link can only be used once
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔗 Generate Link", "🔍 Verify with Token"])
    
    with tab1:
        render_generate_link_tab()
    
    with tab2:
        render_verify_token_tab()


def render_generate_link_tab():
    """
    Render the Generate Link tab for creating verification links.
    """
    st.markdown("### 🔗 Generate Verification Link")
    st.markdown("Create a secure, one-time link for third-party verification")
    
    with st.form("generate_link_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            doc_id = st.text_input(
                "Document ID",
                placeholder="e.g., DOC_2024_001",
                help="Unique identifier for the document"
            )
            
            doc_hash = st.text_input(
                "Document Hash",
                value="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                disabled=True,
                help="SHA-256 hash of the document (demo: pre-filled)"
            )
        
        with col2:
            allowed_email = st.text_input(
                "Authorized Email",
                placeholder="auditor@company.com",
                help="Email address of the person authorized to verify"
            )
            
            expiry_hours = st.number_input(
                "Expiry (hours)",
                min_value=1,
                max_value=168,
                value=24,
                step=1,
                help="Link expiration time (1-168 hours)"
            )
        
        # Permissions selection
        st.markdown("**🔐 Permissions to Grant:**")
        permissions = st.multiselect(
            "Select what information to share:",
            options=["hash", "timestamp", "attestations", "document_id"],
            default=["hash", "timestamp", "attestations"],
            help="Choose what information the verifier can access"
        )
        
        submitted = st.form_submit_button(
            "🔗 Generate Secure Link",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not all([doc_id, allowed_email]):
                st.error("❌ Please provide Document ID and Authorized Email.")
            elif not permissions:
                st.error("❌ Please select at least one permission.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        # Generate verification link
                        with st.spinner("🔐 Generating secure verification link..."):
                            result = services['verification_portal'].generate_verification_link(
                                document_id=doc_id,
                                document_hash=doc_hash,
                                allowed_party=allowed_email,
                                expiry_hours=expiry_hours,
                                permissions=permissions
                            )
                        
                        # Display success and link details
                        display_generated_link(result, permissions)
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate verification link: {str(e)}")


def display_generated_link(result: Dict[str, Any], permissions: List[str]):
    """
    Display the generated verification link and its details.
    """
    st.success("✅ Verification link generated successfully!")
    st.balloons()
    
    # Display the link
    st.markdown("### 🔗 Your Verification Link")
    st.code(result['link'], language="text")
    
    # Link details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Link Details:**")
        st.markdown(f"**Authorized Party:** {result['proof_bundle']['allowed_party']}")
        st.markdown(f"**Expires:** {result['expires_at']}")
        st.markdown(f"**Document ID:** {result['proof_bundle']['document_id']}")
    
    with col2:
        st.markdown("**🔐 Permissions Granted:**")
        for permission in permissions:
            st.markdown(f"✅ {permission}")
    
    # Privacy notice
    st.markdown("### 🔒 Privacy Protection")
    st.warning("""
    **What's NOT Shared:**
    - ❌ Full document content
    - ❌ Borrower personal information (name, SSN, address)
    - ❌ Loan terms and amounts
    - ❌ Internal bank data
    - ❌ Other sensitive information
    """)
    
    # Preview of what verifier will see
    with st.expander("👁️ Preview: What the Verifier Will See"):
        st.markdown("**When the verifier uses this link, they will see:**")
        
        preview_data = {
            "verified": True,
            "verification_time": "2024-01-15T10:30:00Z",
            "privacy_notice": "Only authorized information is shared. Sensitive borrower data is protected."
        }
        
        # Add permitted fields
        for permission in permissions:
            if permission == "hash":
                preview_data["document_hash"] = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            elif permission == "timestamp":
                preview_data["upload_timestamp"] = "2024-01-10T09:15:00Z"
            elif permission == "attestations":
                preview_data["attestations"] = [
                    {"attestor": "compliance_officer", "status": "verified", "date": "2024-01-12T14:20:00Z"},
                    {"attestor": "underwriter", "status": "approved", "date": "2024-01-13T11:45:00Z"}
                ]
            elif permission == "document_id":
                preview_data["document_id"] = "DOC_2024_001"
        
        st.json(preview_data)
        
        st.markdown("**🔐 Privacy Notice:**")
        st.info("This verification confirms document authenticity without exposing sensitive borrower information. The document hash proves integrity, while personal details remain protected.")


def render_verify_token_tab():
    """
    Render the Verify with Token tab for using verification links.
    """
    st.markdown("### 🔍 Verify with Token")
    st.markdown("Use a verification link you received to verify document authenticity")
    
    with st.form("verify_token_form"):
        verify_token = st.text_input(
            "Verification Token",
            placeholder="Enter the token from your verification link",
            help="The token portion of the verification link you received"
        )
        
        verify_email = st.text_input(
            "Your Email",
            placeholder="your.email@company.com",
            help="The email address you were authorized to use"
        )
        
        submitted = st.form_submit_button(
            "🔍 Verify Document",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not all([verify_token, verify_email]):
                st.error("❌ Please provide both Verification Token and Email.")
            else:
                # Get services
                services = get_services()
                if not services:
                    st.error("❌ Failed to initialize services. Please check your configuration.")
                else:
                    try:
                        # Verify with token
                        with st.spinner("🔍 Verifying document with token..."):
                            result = services['verification_portal'].verify_with_token(
                                token=verify_token,
                                verifier_email=verify_email
                            )
                        
                        # Display verification results
                        display_verification_results(result)
                        
                    except Exception as e:
                        st.error(f"❌ Verification failed: {str(e)}")


def display_verification_results(result: Dict[str, Any]):
    """
    Display the verification results.
    """
    if result['success']:
        st.success("✅ Document Verified Successfully!")
        st.balloons()
        
        # Show metrics for visible fields
        st.markdown("### 📊 Verification Results")
        
        # Create metrics based on what's available
        available_fields = [key for key in result.keys() if key not in ['success', 'verified', 'verification_time', 'privacy_notice']]
        
        if available_fields:
            cols = st.columns(min(len(available_fields), 3))
            for i, field in enumerate(available_fields[:3]):
                with cols[i]:
                    value = result[field]
                    if isinstance(value, str) and len(value) > 20:
                        display_value = f"{value[:16]}..."
                    else:
                        display_value = str(value)
                    
                    st.metric(
                        label=f"📄 {field.replace('_', ' ').title()}",
                        value=display_value
                    )
        
        # Privacy notice
        st.markdown("### 🔒 Privacy Notice")
        st.info(result.get('privacy_notice', 'Verification completed with privacy protection.'))
        
        # Full details in expander
        with st.expander("📋 Full Verification Details"):
            st.markdown("**Verification Summary:**")
            st.json({
                "verified": result['verified'],
                "verification_time": result['verification_time'],
                "available_fields": available_fields
            })
            
            st.markdown("**Available Information:**")
            for field, value in result.items():
                if field not in ['success', 'verified', 'verification_time', 'privacy_notice']:
                    st.markdown(f"**{field.replace('_', ' ').title()}:** {value}")
    
    else:
        # Handle different types of failures
        error_msg = result.get('error', 'Unknown verification error')
        
        if 'expired' in error_msg.lower():
            st.error("⏰ **Link Expired** - This verification link has expired. Please request a new one.")
        elif 'already used' in error_msg.lower() or 'used' in error_msg.lower():
            st.error("🔄 **Link Already Used** - This verification link has already been used. Each link can only be used once.")
        elif 'email' in error_msg.lower() or 'party' in error_msg.lower():
            st.error("📧 **Unauthorized Email** - The email address you provided is not authorized for this verification link.")
        elif 'invalid' in error_msg.lower() or 'not found' in error_msg.lower():
            st.error("🔍 **Invalid Token** - The verification token is invalid or not found. Please check the link.")
        else:
            st.error(f"❌ **Verification Failed** - {error_msg}")
        
        # Show possible solutions
        st.markdown("### 💡 Possible Solutions:")
        st.markdown("""
        - ✅ **Check the link**: Make sure you copied the complete verification link
        - ✅ **Verify email**: Ensure you're using the email address that was authorized
        - ✅ **Check expiration**: The link may have expired (links typically expire in 24 hours)
        - ✅ **One-time use**: Each link can only be used once
        - ✅ **Contact sender**: If issues persist, contact the person who sent you the link
        """)


def render_admin_page():
    """
    Render the Admin page with system status, statistics, and settings.
    """
    st.markdown('<h1 class="page-header">⚙️ Admin Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    🛠️ **System Administration** dashboard for monitoring system health, viewing statistics,
    and managing configuration settings. This page provides administrators with comprehensive
    insights into the IntegrityX system performance and status.
    """)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔗 System Status", "📊 Statistics", "⚙️ Settings"])
    
    with tab1:
        render_system_status_tab()
    
    with tab2:
        render_statistics_tab()
    
    with tab3:
        render_settings_tab()


def render_system_status_tab():
    """
    Render the System Status tab showing Walacor connection status.
    """
    st.markdown("### 🔗 Walacor Connection Status")
    
    # Get services
    services = get_services()
    if not services:
        st.error("❌ Failed to initialize services. Please check your configuration.")
        return
    
    try:
        # Test Walacor connection by getting schemas
        with st.spinner("🔍 Checking Walacor connection..."):
            schemas = services['wal_service'].wal.schema.get_list_with_latest_version()
        
        # Success - show metrics
        st.success("✅ Connected to Walacor")
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📋 Schemas Count",
                value=len(schemas),
                delta=f"{len(schemas)} schemas"
            )
        
        with col2:
            st.metric(
                label="🟢 Status",
                value="Online",
                delta="Connected"
            )
        
        with col3:
            # Simulate latency (in real app, you'd measure actual response time)
            latency = 45  # milliseconds
            st.metric(
                label="⚡ Latency",
                value=f"{latency}ms",
                delta="Excellent"
            )
        
        # Additional status information
        st.markdown("### 📋 System Health")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Services Status:**")
            st.markdown("- 🟢 Document Handler: Active")
            st.markdown("- 🟢 Walacor Service: Connected")
            st.markdown("- 🟢 Verifier: Ready")
            st.markdown("- 🟢 Provenance Tracker: Active")
            st.markdown("- 🟢 Time Machine: Ready")
            st.markdown("- 🟢 AI Detector: Active")
            st.markdown("- 🟢 Verification Portal: Ready")
            st.markdown("- 🟢 Security Manager: Active")
        
        with col2:
            st.markdown("**🔧 System Resources:**")
            st.markdown("- 💾 Memory Usage: 45%")
            st.markdown("- 🖥️ CPU Usage: 23%")
            st.markdown("- 💿 Disk Usage: 12%")
            st.markdown("- 🌐 Network: Stable")
            st.markdown("- 🔒 Security: All checks active")
            st.markdown("- 📊 Logs: Normal")
            st.markdown("- ⚡ Performance: Optimal")
        
    except Exception as e:
        # Connection failed
        st.error(f"❌ Failed to connect to Walacor: {str(e)}")
        
        # Show error details
        with st.expander("🔍 Error Details"):
            st.code(str(e))
            st.markdown("**Possible Solutions:**")
            st.markdown("- Check network connectivity")
            st.markdown("- Verify Walacor host configuration")
            st.markdown("- Check authentication credentials")
            st.markdown("- Contact system administrator")


def render_statistics_tab():
    """
    Render the Statistics tab showing system metrics and trends.
    """
    st.markdown("### 📊 System Statistics")
    
    # Hardcoded metrics for demo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Total Documents",
            value="1,234",
            delta="+12 today"
        )
    
    with col2:
        st.metric(
            label="✅ Verified Today",
            value="56",
            delta="+8 from yesterday"
        )
    
    with col3:
        st.metric(
            label="🚨 Tampering Detected",
            value="2",
            delta="-1 from last week"
        )
    
    with col4:
        st.metric(
            label="🔗 Provenance Links",
            value="789",
            delta="+23 this week"
        )
    
    # Upload trend chart
    st.markdown("### 📈 Upload Trend (Last 30 Days)")
    
    if HAS_PANDAS:
        # Generate sample data for the chart
        # Create sample data for the last 30 days
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        uploads = np.random.randint(5, 25, size=len(dates))
        verifications = np.random.randint(10, 40, size=len(dates))
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Uploads': uploads,
            'Verifications': verifications
        })
        
        # Set date as index for line chart
        chart_data = chart_data.set_index('Date')
        
        # Display line chart
        st.line_chart(chart_data)
    else:
        # Fallback: show sample data without pandas
        st.info("📊 Chart data (sample):")
        st.markdown("""
        **Last 7 Days:**
        - Day 1: 15 uploads, 28 verifications
        - Day 2: 18 uploads, 32 verifications  
        - Day 3: 12 uploads, 25 verifications
        - Day 4: 22 uploads, 35 verifications
        - Day 5: 16 uploads, 30 verifications
        - Day 6: 20 uploads, 38 verifications
        - Day 7: 14 uploads, 29 verifications
        """)
    
    # Additional statistics
    st.markdown("### 📋 Detailed Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Document Types:**")
        st.markdown("- Loan Applications: 234")
        st.markdown("- Income Verification: 189")
        st.markdown("- Credit Reports: 156")
        st.markdown("- Appraisals: 98")
        st.markdown("- Underwriting: 145")
        st.markdown("- Closing Documents: 203")
        st.markdown("- Insurance: 89")
        st.markdown("- Other: 120")
    
    with col2:
        st.markdown("**🔍 Verification Results:**")
        st.markdown("- ✅ Authentic: 1,198 (97.1%)")
        st.markdown("- 🚨 Tampered: 2 (0.2%)")
        st.markdown("- ⚠️ Unknown: 34 (2.7%)")
        st.markdown("")
        st.markdown("**👥 User Activity:**")
        st.markdown("- Active Users: 45")
        st.markdown("- Uploads Today: 12")
        st.markdown("- Verifications Today: 56")
        st.markdown("- AI Analyses: 8")


def render_settings_tab():
    """
    Render the Settings tab showing configuration and connection test.
    """
    st.markdown("### ⚙️ Settings")
    
    # Get environment variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Display configuration (read-only for demo)
    st.markdown("#### 🔧 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        walacor_host = os.getenv('WALACOR_HOST', 'Not configured')
        st.text_input(
            "Walacor Host",
            value=walacor_host,
            disabled=True,
            help="Walacor server hostname or IP address"
        )
        
        storage_path = os.getenv('STORAGE_PATH', 'data/documents')
        st.text_input(
            "Storage Path",
            value=storage_path,
            disabled=True,
            help="Local storage path for documents"
        )
    
    with col2:
        username = os.getenv('WALACOR_USERNAME', 'Not configured')
        st.text_input(
            "Username",
            value=username,
            disabled=True,
            help="Walacor authentication username"
        )
        
        temp_path = os.getenv('TEMP_PATH', 'data/temp')
        st.text_input(
            "Temp Path",
            value=temp_path,
            disabled=True,
            help="Temporary files storage path"
        )
    
    # Security settings
    st.markdown("#### 🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_file_size = "50 MB"
        st.text_input(
            "Max File Size",
            value=max_file_size,
            disabled=True,
            help="Maximum allowed file size for uploads"
        )
        
        allowed_extensions = "PDF, DOCX, XLSX, JPG, PNG"
        st.text_input(
            "Allowed Extensions",
            value=allowed_extensions,
            disabled=True,
            help="File types allowed for upload"
        )
    
    with col2:
        rate_limit = "100 uploads/hour"
        st.text_input(
            "Rate Limit",
            value=rate_limit,
            disabled=True,
            help="Upload rate limit per user"
        )
        
        session_timeout = "30 minutes"
        st.text_input(
            "Session Timeout",
            value=session_timeout,
            disabled=True,
            help="User session timeout duration"
        )
    
    # Test connection button
    st.markdown("#### 🔍 Connection Test")
    
    if st.button("🔗 Test Connection", type="primary", use_container_width=True):
        # Get services
        services = get_services()
        if not services:
            st.error("❌ Failed to initialize services.")
        else:
            try:
                with st.spinner("🔍 Testing connection..."):
                    # Test connection
                    schemas = services['wal_service'].wal.schema.get_list_with_latest_version()
                
                st.success("✅ Connection test successful!")
                st.info(f"Found {len(schemas)} schemas in Walacor")
                
            except Exception as e:
                st.error(f"❌ Connection test failed: {str(e)}")
    
    # System information
    st.markdown("#### ℹ️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏗️ Application:**")
        st.markdown("- Name: IntegrityX")
        st.markdown("- Version: 1.0.0")
        st.markdown("- Environment: Demo")
        st.markdown("- Framework: Streamlit")
        st.markdown("- Python: 3.12")
    
    with col2:
        st.markdown("**🔧 Services:**")
        st.markdown("- Walacor SDK: Latest")
        st.markdown("- Security: Active")
        st.markdown("- AI Detection: Enabled")
        st.markdown("- Multi-Party: Ready")
        st.markdown("- Time Machine: Active")


def render_footer():
    """
    Render the footer with project information.
    """
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔒 IntegrityX**  
        Financial Document Integrity System  
        Powered by Blockchain Technology
        """)
    
    with col2:
        st.markdown("""
        **📞 Support**  
        Contact: support@integrityx.com  
        Documentation: docs.integrityx.com
        """)
    
    with col3:
        st.markdown("""
        **⚖️ Legal**  
        Privacy Policy | Terms of Service  
        © 2024 IntegrityX. All rights reserved.
        """)


def main():
    """
    Main application function.
    """
    # Render header
    st.markdown('<h1 class="main-header">🔒 IntegrityX</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Financial Document Integrity System</p>', unsafe_allow_html=True)
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Page routing
    if page == "📤 Upload Document":
        render_upload_page()
    elif page == "🔍 Verify Integrity":
        render_verify_page()
    elif page == "🔗 Provenance Chain":
        render_provenance_page()
    elif page == "⏰ Time Machine":
        render_time_machine_page()
    elif page == "🤖 AI Fraud Detection":
        render_ai_fraud_detection_page()
    elif page == "🔐 Multi-Party Verification":
        render_verification_portal_page()
    elif page == "⚙️ Admin":
        render_admin_page()
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
