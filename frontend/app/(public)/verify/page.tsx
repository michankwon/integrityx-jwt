"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  FileText, 
  Hash, 
  CheckCircle, 
  AlertTriangle, 
  Loader2, 
  Eye, 
  Copy,
  ExternalLink,
  Shield,
  Lock,
  Clock,
  Users,
  Activity,
  Key,
  FileCheck,
  Archive,
  Download,
  Fingerprint,
  User,
  Info
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useSearchParams } from 'next/navigation';
import ProofViewer from '@/components/proof/ProofViewer';
import { DisclosureButton } from '@/components/proof/DisclosureButton';
import { VerifyResultSkeleton, ProofResultSkeleton } from '@/components/ui/verify-result-skeleton';
import { EmptyState, NoResultsEmptyState } from '@/components/ui/empty-state';
import { AttestationList } from '@/components/attestations/AttestationList';
import { AttestationForm } from '@/components/attestations/AttestationForm';
import { LineageGraph } from '@/components/provenance/LineageGraph';
import { ProvenanceLinker } from '@/components/provenance/ProvenanceLinker';
import { EnhancedVerificationResult } from '@/components/verification/EnhancedVerificationResult';
import { 
  getBorrowerInfo, 
  getAuditTrail, 
  type BorrowerInfo, 
  type AuditEvent 
} from '@/lib/api/verification';

// Types
interface VerifyResult {
  is_valid: boolean;
  message: string;
  artifact_id?: string;
  details: {
    created_at: string;
    hash: string;
    etid: number;
  };
}

interface ProofResult {
  proof_bundle: any;
  verification_status: string;
  blockchain_anchors: any[];
}

interface ApiResponse<T> {
  ok: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
  };
}

interface CryptographicProof {
  merkle_root: string;
  block_hash: string;
  previous_block_hash: string;
  digital_signature: string;
}

interface VerificationCertificate {
  certificate_id: string;
  issued_at: string;
  expires_at: string;
  issuer: string;
  document_hash: string;
  verification_status: string;
}

interface DocumentVerificationStatus {
  hashMatches: boolean;
  noTampering: boolean;
  borrowerDataIntact: boolean;
  sealedDateTime: string;
  walacorTxId: string;
  overallStatus: 'verified' | 'tampered' | 'pending';
}

export default function VerifyPage() {
  const searchParams = useSearchParams();
  const [file, setFile] = useState<File | null>(null);
  const [fileHash, setFileHash] = useState('');
  const [etid, setEtid] = useState('100001');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [proofResult, setProofResult] = useState<ProofResult | null>(null);
  const [isLoadingProof, setIsLoadingProof] = useState(false);
  const [isProofViewerOpen, setIsProofViewerOpen] = useState(false);
  const [proofData, setProofData] = useState<any>(null);
  const viewProofButtonRef = useRef<HTMLButtonElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Enhanced verification state
  const [borrowerInfo, setBorrowerInfo] = useState<BorrowerInfo | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditEvent[]>([]);
  const [cryptographicProof, setCryptographicProof] = useState<CryptographicProof | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<DocumentVerificationStatus | null>(null);
  const [certificate, setCertificate] = useState<VerificationCertificate | null>(null);
  const [isLoadingBorrowerInfo, setIsLoadingBorrowerInfo] = useState(false);
  const [isLoadingAuditTrail, setIsLoadingAuditTrail] = useState(false);
  const [isVerifyingSignature, setIsVerifyingSignature] = useState(false);
  const [isGeneratingCertificate, setIsGeneratingCertificate] = useState(false);
  const [isDownloadingProofBundle, setIsDownloadingProofBundle] = useState(false);
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [showCryptographicProof, setShowCryptographicProof] = useState(false);

  // Check for hash in URL params
  useEffect(() => {
    const hashFromUrl = searchParams.get('hash');
    if (hashFromUrl) {
      setFileHash(hashFromUrl);
    }
  }, [searchParams]);

  // Calculate file hash on client side
  const calculateFileHash = async (file: File): Promise<string> => {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      try {
        const hash = await calculateFileHash(selectedFile);
        setFileHash(hash);
        toast.success('File hash calculated successfully');
      } catch (error) {
        console.error('Hash calculation error:', error);
      }
    }
  };

  const handleVerify = async () => {
    if (!fileHash) {
      toast.error('Please provide a file hash');
      return;
    }

    setIsVerifying(true);
    setVerifyResult(null);
    setProofResult(null);

    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          etid: parseInt(etid),
          payloadHash: fileHash
        })
      });

      if (!response.ok) {
        throw new Error('Verification request failed');
      }

      const apiResponse: ApiResponse<VerifyResult> = await response.json();
      
      if (!apiResponse.ok || !apiResponse.data) {
        throw new Error(apiResponse.error?.message || 'Verification request failed');
      }

      const result = apiResponse.data;
      setVerifyResult(result);
      
      // Set verification status
      const status: DocumentVerificationStatus = {
        hashMatches: result.is_valid,
        noTampering: result.is_valid,
        borrowerDataIntact: result.is_valid,
        sealedDateTime: result.details.created_at,
        walacorTxId: 'TX_' + Math.random().toString(16).substr(2, 16), // Mock TX ID
        overallStatus: result.is_valid ? 'verified' : 'tampered'
      };
      setVerificationStatus(status);
      
      if (result.is_valid) {
        toast.success('Document verification successful!');
        
        // Load additional data for verified documents
        if (result.artifact_id) {
          loadBorrowerInfo(result.artifact_id);
          loadAuditTrail(result.artifact_id);
        }
      } else {
        toast.error('Document verification failed - tampering detected!');
      }

    } catch (error) {
      console.error('Verification error:', error);
      toast.error(`Verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleGetProof = async () => {
    if (!verifyResult?.artifact_id) {
      toast.error('No artifact ID available');
      return;
    }

    setIsLoadingProof(true);
    try {
      const response = await fetch(`/api/proof?artifactId=${verifyResult.artifact_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch proof');
      }
      const data = await response.json();
      setProofResult(data);
      toast.success('Proof retrieved successfully');
    } catch (error) {
      console.error('Proof retrieval error:', error);
      toast.error('Failed to retrieve proof');
    } finally {
      setIsLoadingProof(false);
    }
  };

  const handleViewProof = () => {
    if (proofResult) {
      setProofData(proofResult);
      setIsProofViewerOpen(true);
    }
  };

  const loadBorrowerInfo = async (artifactId: string) => {
    setIsLoadingBorrowerInfo(true);
    try {
      const info = await getBorrowerInfo(artifactId);
      setBorrowerInfo(info);
    } catch (error) {
      console.error('Failed to load borrower info:', error);
    } finally {
      setIsLoadingBorrowerInfo(false);
    }
  };

  const loadAuditTrail = async (artifactId: string) => {
    setIsLoadingAuditTrail(true);
    try {
      const trail = await getAuditTrail(artifactId);
      setAuditTrail(trail);
    } catch (error) {
      console.error('Failed to load audit trail:', error);
    } finally {
      setIsLoadingAuditTrail(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const maskSensitiveData = (data: string, type: string): string => {
    if (!data) return 'N/A';
    
    switch (type) {
      case 'email':
        const [username, domain] = data.split('@');
        return `${username.substring(0, 2)}***@${domain}`;
      case 'phone':
        return data.replace(/(\d{3})\d{3}(\d{4})/, '$1***$2');
      default:
        return data;
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">Document Verification</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Verify the integrity and authenticity of your financial documents using blockchain technology.
            Upload a file or provide a hash to check against our immutable records.
          </p>
        </div>

        {/* Verification Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Verification Input
            </CardTitle>
            <CardDescription>
              Provide either a file upload or document hash for verification
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div className="space-y-2">
              <Label htmlFor="file-upload">Upload Document</Label>
              <div className="flex items-center gap-4">
                <Input
                  ref={fileInputRef}
                  id="file-upload"
                  type="file"
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx,.txt,.json"
                  className="flex-1"
                />
                {file && (
                  <Badge variant="outline" className="text-green-600 border-green-200">
                    <FileText className="h-3 w-3 mr-1" />
                    {file.name}
                  </Badge>
                )}
              </div>
            </div>

            {/* Hash Input */}
            <div className="space-y-2">
              <Label htmlFor="hash-input">Or Enter Document Hash</Label>
              <div className="flex gap-2">
                <Input
                  id="hash-input"
                  type="text"
                  placeholder="Enter SHA-256 hash (64 characters)"
                  value={fileHash}
                  onChange={(e) => setFileHash(e.target.value)}
                  className="flex-1 font-mono text-sm"
                />
                {fileHash && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => copyToClipboard(fileHash)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>

            {/* ETID Selection */}
            <div className="space-y-2">
              <Label htmlFor="etid-select">Entity Type ID</Label>
              <Select value={etid} onValueChange={setEtid}>
                <SelectTrigger>
                  <SelectValue placeholder="Select ETID" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="100001">Loan Documents (100001)</SelectItem>
                  <SelectItem value="100002">Document Provenance (100002)</SelectItem>
                  <SelectItem value="100003">Attestations (100003)</SelectItem>
                  <SelectItem value="100004">Audit Logs (100004)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Verify Button */}
            <Button 
              onClick={handleVerify} 
              disabled={!fileHash || isVerifying}
              className="w-full"
              size="lg"
            >
              {isVerifying ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Verifying Document...
                </>
              ) : (
                <>
                  <Shield className="h-4 w-4 mr-2" />
                  Verify Document
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Enhanced Verification Result */}
        {isVerifying ? (
          <VerifyResultSkeleton />
        ) : verifyResult ? (
          <EnhancedVerificationResult 
            result={verifyResult} 
            currentHash={fileHash}
            showTamperAnalysis={true}
            showVisualComparison={true}
          />
        ) : null}

        {/* Attestations Section - Only show for valid documents with artifact ID */}
        {verifyResult?.is_valid && verifyResult?.artifact_id && (
          <>
            <AttestationList artifactId={verifyResult.artifact_id} />
            <AttestationForm artifactId={verifyResult.artifact_id} currentUser="current_user" />
          </>
        )}

        {/* Provenance Section - Only show for valid documents with artifact ID */}
        {verifyResult?.is_valid && verifyResult?.artifact_id && (
          <>
            <LineageGraph artifactId={verifyResult.artifact_id} />
            <ProvenanceLinker artifactId={verifyResult.artifact_id} />
          </>
        )}

        {/* Proof Result */}
        {isLoadingProof ? (
          <ProofResultSkeleton />
        ) : proofResult ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Proof Bundle
              </CardTitle>
              <CardDescription>
                Cryptographic proof of document integrity
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Proof bundle retrieved successfully. Click "View Proof" to see detailed verification data.
                </AlertDescription>
              </Alert>
              <div className="flex gap-2">
                <Button onClick={handleViewProof}>
                  <Eye className="h-4 w-4 mr-2" />
                  View Proof
                </Button>
                <DisclosureButton artifactId={verifyResult?.artifact_id || ''} />
              </div>
            </CardContent>
          </Card>
        ) : null}

        {/* Proof Viewer Modal */}
        <ProofViewer
          isOpen={isProofViewerOpen}
          onClose={() => setIsProofViewerOpen(false)}
          proofData={proofData}
        />
      </div>
    </div>
  );
}
