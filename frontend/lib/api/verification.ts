/**
 * Verification API Client
 * 
 * This module provides TypeScript API client functions for document verification operations.
 */

import axios, { AxiosResponse, AxiosError } from 'axios';

// ============================================================================
// TYPESCRIPT TYPES
// ============================================================================

export interface VerifyRequest {
  etid: number;
  payloadHash: string;
}

export interface VerifyResponse {
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

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// ERROR HANDLING
// ============================================================================

function handleApiError(error: AxiosError): Error {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.error || 'Server error occurred';
    return new Error(message);
  } else if (error.request) {
    // Request was made but no response received
    return new Error('Network error - please check your connection');
  } else {
    // Something else happened
    return new Error(error.message || 'An unexpected error occurred');
  }
}

// ============================================================================
// VERIFICATION FUNCTIONS
// ============================================================================

/**
 * Verify a document by hash and ETID
 * @param etid - Entity Type ID
 * @param payloadHash - SHA-256 hash of the document
 * @returns Promise with verification response
 */
export async function verifyDocument(
  etid: number,
  payloadHash: string
): Promise<VerifyResponse> {
  try {
    console.log("🔍 Verifying document:", { etid, hash: payloadHash.substring(0, 16) + "..." });
    
    const response: AxiosResponse<ApiResponse<VerifyResponse>> = await apiClient.post(
      "/api/verify",
      {
        etid,
        payloadHash
      }
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || "Failed to verify document");
    }
    
    console.log("✅ Document verification result:", response.data.data.status);
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error("❌ Failed to verify document:", apiError);
    throw apiError;
  }
}

/**
 * Check if a document is already sealed
 * @param hash - SHA-256 hash of the document
 * @param etid - Entity Type ID
 * @returns Promise with verification result or null if not found
 */
export async function checkIfAlreadySealed(
  hash: string,
  etid: number
): Promise<VerifyResponse | null> {
  try {
    const result = await verifyDocument(etid, hash);
    return result.is_valid ? result : null;
  } catch (error) {
    // If verification fails, document is not sealed
    return null;
  }
}

/**
 * Get borrower information for a specific artifact
 * @param artifactId - Artifact ID
 * @returns Promise with borrower information
 */
export async function getBorrowerInfo(artifactId: string): Promise<any> {
  try {
    console.log("🔍 Getting borrower info for artifact:", artifactId);
    
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.get(
      `/api/loan-documents/${artifactId}/borrower`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || "Failed to get borrower info");
    }
    
    console.log("✅ Borrower info retrieved successfully");
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error("❌ Failed to get borrower info:", apiError);
    throw apiError;
  }
}

/**
 * Get audit trail for a specific artifact
 * @param artifactId - Artifact ID
 * @returns Promise with audit trail information
 */
export async function getAuditTrail(artifactId: string): Promise<any> {
  try {
    console.log("🔍 Getting audit trail for artifact:", artifactId);
    
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.get(
      `/api/loan-documents/${artifactId}/audit-trail`
    );
    
    if (!response.data.ok) {
      throw new Error(response.data.error || "Failed to get audit trail");
    }
    
    console.log("✅ Audit trail retrieved successfully");
    return response.data.data;
    
  } catch (error) {
    const apiError = handleApiError(error as AxiosError);
    console.error("❌ Failed to get audit trail:", apiError);
    throw apiError;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  verifyDocument,
  checkIfAlreadySealed,
  getBorrowerInfo,
  getAuditTrail,
};
