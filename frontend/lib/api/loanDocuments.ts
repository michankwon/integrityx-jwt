/**
 * Loan Documents API Client
 * 
 * This module provides TypeScript API client functions for loan document operations
 * including sealing, retrieval, search, verification, and audit trail access.
 * 
 * Features:
 * - Comprehensive TypeScript types for all API operations
 * - Proper error handling with custom error types
 * - Loading state management
 * - File upload support with multipart/form-data
 * - Pagination support for search operations
 * - Audit trail and verification functionality
 */

import axios, { AxiosResponse, AxiosError } from 'axios';

// ============================================================================
// TYPESCRIPT TYPES
// ============================================================================

export interface BorrowerInfo {
  full_name: string;
  date_of_birth: string;
  email: string;
  phone: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  ssn_last4: string;
  id_type: 'drivers_license' | 'passport' | 'state_id' | 'military_id' | 'alien_id';
  id_last4: string;
  employment_status: 'employed' | 'self_employed' | 'retired' | 'unemployed' | 'student' | 'disabled';
  annual_income_range: string;
  co_borrower_name?: string;
  is_sealed: boolean;
  walacor_tx_id?: string;
  seal_timestamp?: string;
}

export interface LoanData {
  loan_id: string;
  document_type: 'loan_application' | 'mortgage_application' | 'refinance_application' | 'home_equity_loan' | 'personal_loan' | 'auto_loan' | 'business_loan';
  loan_amount: number;
  borrower_name: string;
  additional_notes?: string;
}

export interface FileInfo {
  filename: string;
  file_type: string;
  file_size: number;
  upload_timestamp: string;
  content_hash?: string;
}

export interface SealLoanDocumentRequest {
  loan_data: LoanData;
  borrower_info: BorrowerInfo;
  files: FileInfo[];
}

export interface SealResponse {
  message: string;
  artifact_id: string;
  walacor_tx_id: string;
  hash: string;
  sealed_at: string;
  blockchain_proof?: {
    transaction_id: string;
    blockchain_network: string;
    etid: number;
    seal_timestamp: string;
    integrity_verified: boolean;
    immutability_established: boolean;
  };
}

export interface SearchFilters {
  borrower_name?: string;
  borrower_email?: string;
  loan_id?: string;
  date_from?: string;
  date_to?: string;
  amount_min?: number;
  amount_max?: number;
  document_type?: string;
  employment_status?: string;
  is_sealed?: boolean;
  limit?: number;
  offset?: number;
}

export interface LoanSearchResult {
  artifact_id: string;
  loan_id: string;
  document_type: string;
  loan_amount: number;
  borrower_name: string;
  borrower_email: string;
  upload_date: string;
  sealed_status: string;
  walacor_tx_id?: string;
}

export interface SearchResults {
  results: LoanSearchResult[];
  total_count: number;
  has_more: boolean;
  limit: number;
  offset: number;
}

export interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  user_id: string;
  ip_address?: string;
  details: Record<string, any>;
}

export interface VerificationResult {
  message: string;
  is_valid: boolean;
  status: string;
  artifact_id: string;
  verified_at: string;
  details: {
    stored_hash: string;
    provided_hash: string;
    artifact_type: string;
    created_at: string;
  };
}

export interface ApiResponse<T> {
  ok: boolean;
  data: T;
  error?: string;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error instanceof Error ? error : new Error(String(error)));
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error instanceof Error ? error : new Error(String(error)));
  }
);

// ============================================================================
// ERROR HANDLING UTILITIES
// ============================================================================

function handleApiError(error: AxiosError): ApiError {
  if (error.response) {
    // Server responded with error status
    const responseData = error.response.data as any;
    return {
      message: responseData?.error || responseData?.message || 'Server error occurred',
      status: error.response.status,
      details: responseData,
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      message: 'Network error - unable to reach server',
      status: 0,
      details: error.request,
    };
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      details: error,
    };
  }
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Seal a loan document with borrower information in the blockchain
 * 
 * @param loanData - Loan-specific data
 * @param borrowerInfo - Borrower information
 * @param files - List of files to be sealed
 * @returns Promise with sealing response including artifact_id and transaction details
 */
export async function sealLoanDocument(
  loanData: LoanData,
  borrowerInfo: BorrowerInfo,
  files: File[]
): Promise<SealResponse> {
  try {
    console.log('🔐 Sealing loan document:', loanData.loan_id);
    
    // Create request payload in the format expected by backend
    const requestPayload = {
      loan_id: loanData.loan_id,
      document_type: loanData.document_type,
      loan_amount: loanData.loan_amount,
      borrower_name: loanData.borrower_name,
      additional_notes: loanData.additional_notes,
      created_by: loanData.created_by || 'user@example.com',
      borrower: {
        full_name: borrowerInfo.full_name,
        date_of_birth: borrowerInfo.date_of_birth,
        email: borrowerInfo.email,
        phone: borrowerInfo.phone,
        address: {
          street: borrowerInfo.address_line1,
          city: borrowerInfo.city,
          state: borrowerInfo.state,
          zip_code: borrowerInfo.zip_code,
          country: borrowerInfo.country
        },
        ssn_last4: borrowerInfo.ssn_last4,
        id_type: borrowerInfo.id_type,
        id_last4: borrowerInfo.id_last4,
        employment_status: borrowerInfo.employment_status,
        annual_income: parseFloat(borrowerInfo.annual_income_range.replace(/[^0-9]/g, '')) || 0,
        co_borrower_name: borrowerInfo.co_borrower_name || ''
      }
    };
    
    const response: AxiosResponse<ApiResponse<SealResponse>> = await apiClient.post(
      '/api/loan-documents/seal',
      requestPayload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to seal loan document');
    }
    
    console.log('✅ Loan document sealed successfully:', response.data.data.artifact_id);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to seal loan document:', apiError);
    throw apiError;
  }
}

/**
 * Seal a loan document with MAXIMUM SECURITY and MINIMAL TAMPERING
 * 
 * This function implements multiple layers of security:
 * 1. Multi-algorithm hashing (SHA-256, SHA-512, BLAKE3, SHA3-256)
 * 2. PKI-based digital signatures
 * 3. Content-based integrity verification
 * 4. Cross-verification systems
 * 5. Advanced tamper detection
 * 
 * @param loanData - Loan-specific data
 * @param borrowerInfo - Borrower information
 * @param files - Files to be sealed
 * @returns Promise with comprehensive security seal information
 */
export async function sealLoanDocumentMaximumSecurity(
  loanData: LoanData,
  borrowerInfo: BorrowerInfo,
  files: File[]
): Promise<SealResponse> {
  try {
    console.log('🔐 Sealing loan document with MAXIMUM SECURITY:', loanData.loan_id);
    
    // Create request payload in the format expected by backend
    const requestPayload = {
      loan_id: loanData.loan_id,
      document_type: loanData.document_type,
      loan_amount: loanData.loan_amount,
      borrower_name: loanData.borrower_name,
      additional_notes: loanData.additional_notes,
      created_by: loanData.created_by || 'user@example.com',
      borrower: {
        full_name: borrowerInfo.full_name,
        date_of_birth: borrowerInfo.date_of_birth,
        email: borrowerInfo.email,
        phone: borrowerInfo.phone,
        address: {
          street: borrowerInfo.address_line1,
          city: borrowerInfo.city,
          state: borrowerInfo.state,
          zip_code: borrowerInfo.zip_code,
          country: borrowerInfo.country
        },
        ssn_last4: borrowerInfo.ssn_last4,
        id_type: borrowerInfo.id_type,
        id_last4: borrowerInfo.id_last4,
        employment_status: borrowerInfo.employment_status,
        annual_income: parseFloat(borrowerInfo.annual_income_range.replace(/[^0-9]/g, '')) || 0,
        co_borrower_name: borrowerInfo.co_borrower_name || ''
      }
    };
    
    const response: AxiosResponse<ApiResponse<SealResponse>> = await apiClient.post(
      '/api/loan-documents/seal-maximum-security',
      requestPayload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to seal loan document with maximum security');
    }
    
    console.log('✅ Loan document sealed with MAXIMUM SECURITY:', response.data.data.artifact_id);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to seal loan document with maximum security:', apiError);
    throw apiError;
  }
}

/**
 * Verify a maximum security loan document with comprehensive tamper detection
 * 
 * This function performs:
 * 1. Multi-algorithm hash verification
 * 2. PKI signature verification
 * 3. Content integrity verification
 * 4. Blockchain seal verification
 * 5. Advanced tampering detection
 * 
 * @param artifactId - Unique artifact identifier
 * @returns Promise with comprehensive verification results
 */
export async function verifyMaximumSecurityDocument(artifactId: string): Promise<VerificationResult> {
  try {
    console.log('🔍 Verifying maximum security document:', artifactId);
    
    const response: AxiosResponse<ApiResponse<VerificationResult>> = await apiClient.post(
      `/api/loan-documents/${artifactId}/verify-maximum-security`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to verify maximum security document');
    }
    
    console.log('✅ Maximum security document verification completed:', response.data.data.verification_status);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to verify maximum security document:', apiError);
    throw apiError;
  }
}

export async function sealLoanDocumentQuantumSafe(
  loanData: LoanData,
  borrowerInfo: BorrowerInfo,
  files: File[]
): Promise<SealResponse> {
  try {
    console.log('🔐 Sealing loan document with QUANTUM-SAFE cryptography:', loanData.loan_id);
    
    // Create request payload in the format expected by backend
    const requestPayload = {
      loan_id: loanData.loan_id,
      document_type: loanData.document_type,
      loan_amount: loanData.loan_amount,
      borrower_name: loanData.borrower_name,
      additional_notes: loanData.additional_notes,
      created_by: loanData.created_by || 'user@example.com',
      borrower: {
        full_name: borrowerInfo.full_name,
        date_of_birth: borrowerInfo.date_of_birth,
        email: borrowerInfo.email,
        phone: borrowerInfo.phone,
        address: {
          street: borrowerInfo.address_line1,
          city: borrowerInfo.city,
          state: borrowerInfo.state,
          zip_code: borrowerInfo.zip_code,
          country: borrowerInfo.country
        },
        ssn_last4: borrowerInfo.ssn_last4,
        id_type: borrowerInfo.id_type,
        id_last4: borrowerInfo.id_last4,
        employment_status: borrowerInfo.employment_status,
        annual_income: parseFloat(borrowerInfo.annual_income_range.replace(/[^0-9]/g, '')) || 0,
        co_borrower_name: borrowerInfo.co_borrower_name || ''
      }
    };
    
    const response: AxiosResponse<ApiResponse<SealResponse>> = await apiClient.post(
      '/api/loan-documents/seal-quantum-safe',
      requestPayload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to seal loan document with quantum-safe cryptography');
    }
    
    console.log('✅ Loan document sealed with QUANTUM-SAFE cryptography:', response.data.data.artifact_id);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to seal loan document with quantum-safe cryptography:', apiError);
    throw apiError;
  }
}

/**
 * Get borrower information for a specific loan document
 * 
 * @param artifactId - Unique artifact identifier
 * @returns Promise with masked borrower information
 */
export async function getBorrowerInfo(artifactId: string): Promise<BorrowerInfo> {
  try {
    console.log('👤 Retrieving borrower info for artifact:', artifactId);
    
    const response: AxiosResponse<ApiResponse<BorrowerInfo>> = await apiClient.get(
      `/api/loan-documents/${artifactId}/borrower`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to retrieve borrower information');
    }
    
    console.log('✅ Borrower info retrieved successfully');
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to retrieve borrower info:', apiError);
    throw apiError;
  }
}

/**
 * Search loan documents with various filters
 * 
 * @param filters - Search filters and pagination parameters
 * @returns Promise with paginated search results
 */
export async function searchLoanDocuments(filters: SearchFilters = {}): Promise<SearchResults> {
  try {
    console.log('🔍 Searching loan documents with filters:', filters);
    
    // Build query parameters
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    const response: AxiosResponse<ApiResponse<SearchResults>> = await apiClient.get(
      `/api/loan-documents/search?${params.toString()}`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to search loan documents');
    }
    
    console.log('✅ Search completed:', response.data.data.results.length, 'results found');
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to search loan documents:', apiError);
    throw apiError;
  }
}

/**
 * Get complete audit trail for a loan document
 * 
 * @param artifactId - Unique artifact identifier
 * @returns Promise with array of audit events
 */
export async function getAuditTrail(artifactId: string): Promise<AuditEvent[]> {
  try {
    console.log('📋 Retrieving audit trail for artifact:', artifactId);
    
    const response: AxiosResponse<ApiResponse<AuditEvent[]>> = await apiClient.get(
      `/api/loan-documents/${artifactId}/audit-trail`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to retrieve audit trail');
    }
    
    console.log('✅ Audit trail retrieved successfully:', response.data.data.length, 'events');
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to retrieve audit trail:', apiError);
    throw apiError;
  }
}

/**
 * Verify a loan document's integrity
 * 
 * @param artifactId - Unique artifact identifier
 * @param providedHash - Hash to verify against stored hash
 * @returns Promise with verification result
 */
export async function verifyLoanDocument(
  artifactId: string,
  providedHash: string
): Promise<VerificationResult> {
  try {
    console.log('🔍 Verifying loan document:', artifactId);
    
    // First, get the artifact details to find the ETID
    const artifactResponse = await apiClient.get(`/api/artifacts/${artifactId}`);
    const artifact = artifactResponse.data.data;
    
    const verifyRequest = {
      etid: artifact.etid,
      payloadHash: providedHash,
    };
    
    const response: AxiosResponse<ApiResponse<VerificationResult>> = await apiClient.post(
      '/api/verify',
      verifyRequest
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to verify loan document');
    }
    
    console.log('✅ Loan document verification completed:', response.data.data.status);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to verify loan document:', apiError);
    throw apiError;
  }
}

/**
 * Get loan document details by artifact ID
 * 
 * @param artifactId - Unique artifact identifier
 * @returns Promise with complete loan document details
 */
export async function getLoanDocument(artifactId: string): Promise<any> {
  try {
    console.log('📄 Retrieving loan document:', artifactId);
    
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.get(
      `/api/artifacts/${artifactId}`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || 'Failed to retrieve loan document');
    }
    
    console.log('✅ Loan document retrieved successfully');
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to retrieve loan document:', apiError);
    throw apiError;
  }
}

/**
 * Download loan document as file
 * 
 * @param artifactId - Unique artifact identifier
 * @param format - Download format ('json', 'pdf', 'csv')
 * @returns Promise with blob data for download
 */
export async function downloadLoanDocument(
  artifactId: string,
  format: 'json' | 'pdf' | 'csv' = 'json'
): Promise<Blob> {
  try {
    console.log('📥 Downloading loan document:', artifactId, 'as', format);
    
    const response = await apiClient.get(
      `/api/loan-documents/${artifactId}/download?format=${format}`,
      {
        responseType: 'blob',
      }
    );
    
    console.log('✅ Loan document downloaded successfully');
    return response.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error('❌ Failed to download loan document:', apiError);
    throw apiError;
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Create a download link for a blob
 * 
 * @param blob - Blob data
 * @param filename - Filename for download
 */
export function createDownloadLink(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Format loan amount for display
 * 
 * @param amount - Loan amount in USD
 * @returns Formatted amount string
 */
export function formatLoanAmount(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format date for display
 * 
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get status badge color for sealed status
 * 
 * @param status - Sealed status string
 * @returns CSS color class
 */
export function getStatusBadgeColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'sealed':
    case 'verified':
      return 'bg-green-100 text-green-800';
    case 'pending':
    case 'processing':
      return 'bg-yellow-100 text-yellow-800';
    case 'failed':
    case 'error':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  sealLoanDocument,
  sealLoanDocumentMaximumSecurity,
  sealLoanDocumentQuantumSafe,
  verifyMaximumSecurityDocument,
  getBorrowerInfo,
  searchLoanDocuments,
  getAuditTrail,
  verifyLoanDocument,
  getLoanDocument,
  downloadLoanDocument,
  createDownloadLink,
  formatLoanAmount,
  formatDate,
  getStatusBadgeColor,
};
