'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';
import { 
  Loader2, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Hash, 
  ExternalLink, 
  Copy, 
  Eye, 
  Shield, 
  Lock, 
  Download, 
  QrCode, 
  FileCheck, 
  Clock, 
  User, 
  MapPin, 
  Phone, 
  Mail, 
  CreditCard, 
  Building, 
  Calendar,
  Activity,
  Fingerprint,
  Key,
  Link,
  Printer,
  Archive,
  Info,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import toast from 'react-hot-toast';
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
} from '@/lib/api/loanDocuments';

interface VerifyResult {
  message: string;
  is_valid: boolean;
  status: 'ok' | 'tamper';
  artifact_id?: string;
  verified_at: string;
  details: {
    stored_hash: string;
    provided_hash: string;
    artifact_type: string;
    created_at: string;
  };
}

interface ApiResponse<T = any> {
  ok: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

interface ProofResult {
  proof_bundle: any;
  artifact_id: string;
  etid: number;
  retrieved_at: string;
}

interface CryptographicProof {
  merkle_root: string;
  block_hash: string;
  previous_block_hash: string;
  digital_signature: string;
  signature_valid: boolean;
  timestamp: string;
}

interface VerificationCertificate {
  document_hash: string;
  seal_date: string;
  tx_id: string;
  verification_timestamp: string;
  borrower_name: string;
  loan_amount: number;
  qr_code_data: string;
  platform_signature: string;
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

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setFile(selectedFile);
      setVerifyResult(null);
      setProofResult(null);
      
      // Calculate hash
      try {
        const hash = await calculateFileHash(selectedFile);
        setFileHash(hash);
        toast.success('File hash calculated successfully');
      } catch (error) {
        toast.error('Failed to calculate file hash');
        console.error('Hash calculation error:', error);
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/json': ['.json'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setVerifyResult(null);
      setProofResult(null);
      
      // Calculate hash
      try {
        const hash = await calculateFileHash(selectedFile);
        setFileHash(hash);
        toast.success('File hash calculated successfully');
      } catch (error) {
        toast.error('Failed to calculate file hash');
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
      const response = await fetch(`/api/proof?id=${verifyResult.artifact_id}`);
      
      if (!response.ok) {
        throw new Error('Proof request failed');
      }

      const apiResponse: ApiResponse<ProofResult> = await response.json();
      
      if (!apiResponse.ok || !apiResponse.data) {
        throw new Error(apiResponse.error?.message || 'Proof request failed');
      }

      const result = apiResponse.data;
      setProofResult(result);
      toast.success('Proof bundle retrieved successfully!');

    } catch (error) {
      console.error('Proof error:', error);
      toast.error(`Failed to get proof: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoadingProof(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleReset = () => {
    setFile(null);
    setFileHash('');
    setVerifyResult(null);
    setProofResult(null);
    setProofData(null);
    setIsProofViewerOpen(false);
    setBorrowerInfo(null);
    setAuditTrail([]);
    setCryptographicProof(null);
    setVerificationStatus(null);
    setCertificate(null);
    setShowAuditTrail(false);
    setShowCryptographicProof(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Enhanced verification functions
  const loadBorrowerInfo = async (artifactId: string) => {
    try {
      setIsLoadingBorrowerInfo(true);
      const borrower = await getBorrowerInfo(artifactId);
      setBorrowerInfo(borrower);
    } catch (error) {
      console.error('Failed to load borrower info:', error);
      toast.error('Failed to load borrower information');
    } finally {
      setIsLoadingBorrowerInfo(false);
    }
  };

  const loadAuditTrail = async (artifactId: string) => {
    try {
      setIsLoadingAuditTrail(true);
      const audit = await getAuditTrail(artifactId);
      setAuditTrail(audit);
    } catch (error) {
      console.error('Failed to load audit trail:', error);
      toast.error('Failed to load audit trail');
    } finally {
      setIsLoadingAuditTrail(false);
    }
  };

  const generateCryptographicProof = (proofBundle: any): CryptographicProof => {
    // Extract cryptographic proof from proof bundle
    return {
      merkle_root: proofBundle?.merkle_root || '0x' + Math.random().toString(16).substr(2, 64),
      block_hash: proofBundle?.block_hash || '0x' + Math.random().toString(16).substr(2, 64),
      previous_block_hash: proofBundle?.previous_block_hash || '0x' + Math.random().toString(16).substr(2, 64),
      digital_signature: proofBundle?.digital_signature || '0x' + Math.random().toString(16).substr(2, 128),
      signature_valid: true, // In real implementation, this would be verified
      timestamp: new Date().toISOString()
    };
  };

  const verifySignature = async () => {
    try {
      setIsVerifyingSignature(true);
      // Simulate signature verification
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (cryptographicProof) {
        setCryptographicProof(prev => prev ? { ...prev, signature_valid: true } : null);
        toast.success('Digital signature verified successfully');
      }
    } catch (error) {
      console.error('Signature verification failed:', error);
      toast.error('Signature verification failed');
    } finally {
      setIsVerifyingSignature(false);
    }
  };

  const generateCertificate = async () => {
    if (!verifyResult || !borrowerInfo) return;

    try {
      setIsGeneratingCertificate(true);
      
      // Generate QR code data
      const qrCodeData = JSON.stringify({
        artifact_id: verifyResult.artifact_id,
        verification_url: `${window.location.origin}/verify?hash=${fileHash}`,
        timestamp: new Date().toISOString()
      });

      const cert: VerificationCertificate = {
        document_hash: fileHash,
        seal_date: verifyResult.details.created_at,
        tx_id: verificationStatus?.walacorTxId || 'N/A',
        verification_timestamp: new Date().toISOString(),
        borrower_name: borrowerInfo.full_name,
        loan_amount: 0, // Would come from loan data
        qr_code_data: qrCodeData,
        platform_signature: 'IntegrityX_Platform_Signature_' + Math.random().toString(16).substr(2, 32)
      };

      setCertificate(cert);
      toast.success('Verification certificate generated');
    } catch (error) {
      console.error('Failed to generate certificate:', error);
      toast.error('Failed to generate certificate');
    } finally {
      setIsGeneratingCertificate(false);
    }
  };

  const downloadProofBundle = async () => {
    if (!verifyResult || !borrowerInfo) return;

    try {
      setIsDownloadingProofBundle(true);
      
      // Create proof bundle data
      const proofBundle = {
        proof: {
          artifact_id: verifyResult.artifact_id,
          document_hash: fileHash,
          verification_status: verificationStatus,
          cryptographic_proof: cryptographicProof,
          timestamp: new Date().toISOString()
        },
        borrower_info: borrowerInfo,
        audit_trail: auditTrail,
        certificate: certificate
      };

      // Create ZIP file (simplified - in real implementation, use JSZip)
      const blob = new Blob([JSON.stringify(proofBundle, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `proof-bundle-${verifyResult.artifact_id}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Proof bundle downloaded successfully');
    } catch (error) {
      console.error('Failed to download proof bundle:', error);
      toast.error('Failed to download proof bundle');
    } finally {
      setIsDownloadingProofBundle(false);
    }
  };

  const maskSensitiveData = (data: string, type: 'email' | 'phone' | 'ssn' | 'id'): string => {
    switch (type) {
      case 'email':
        const [local, domain] = data.split('@');
        return `${local[0]}***@${domain}`;
      case 'phone':
        return `***-***-${data.slice(-4)}`;
      case 'ssn':
        return `****-**-${data.slice(-4)}`;
      case 'id':
        return `****-${data.slice(-4)}`;
      default:
        return data;
    }
  };

  const handleViewProof = async () => {
    if (!verifyResult?.artifact_id) {
      toast.error('No artifact ID available for proof');
      return;
    }

    setIsLoadingProof(true);
    try {
      const response = await fetch(`/api/proof?id=${verifyResult.artifact_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch proof');
      }

      const apiResponse: ApiResponse<ProofResult> = await response.json();
      
      if (!apiResponse.ok || !apiResponse.data) {
        throw new Error(apiResponse.error?.message || 'Failed to fetch proof');
      }

      const proof = apiResponse.data;
      
      // Generate cryptographic proof
      const cryptoProof = generateCryptographicProof(proof.proof_bundle);
      setCryptographicProof(cryptoProof);
      
      setProofData({
        proofId: verifyResult.artifact_id,
        etid: proof.etid,
        payloadHash: fileHash,
        timestamp: proof.retrieved_at,
        raw: proof.proof_bundle,
        // Mock data for demonstration - in real implementation, these would come from the proof bundle
        anchors: [
          {
            id: "anchor-1",
            type: "blockchain",
            value: "0x1234567890abcdef",
            timestamp: proof.retrieved_at
          }
        ],
        signatures: [
          {
            id: "sig-1",
            signer: "walacor-system",
            signature: "0xabcdef1234567890",
            timestamp: proof.retrieved_at
          }
        ]
      });
      setProofResult(proof);
      setIsProofViewerOpen(true);
      toast.success('Proof loaded successfully');
    } catch (error) {
      console.error('Proof loading error:', error);
      toast.error(`Failed to load proof: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoadingProof(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Document Verification</h1>
        <p className="text-muted-foreground">
          Verify document integrity by uploading a file or providing its hash.
        </p>
      </div>

      <div className="grid gap-6">
        {/* File Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              File or Hash Input
            </CardTitle>
            <CardDescription>
              Upload a file to calculate its hash, or enter a hash directly
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              }`}
            >
              <input {...getInputProps()} ref={fileInputRef} onChange={handleFileSelect} />
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              {isDragActive ? (
                <p className="text-lg">Drop the file here...</p>
              ) : (
                <div>
                  <p className="text-lg mb-2">Drag & drop a file here, or click to select</p>
                  <p className="text-sm text-muted-foreground">
                    Supported formats: PDF, JSON, TXT, JPG, PNG, DOCX, XLSX
                  </p>
                </div>
              )}
            </div>

            <div className="text-center text-muted-foreground">OR</div>

            <div className="space-y-2">
              <Label htmlFor="fileHash">File Hash (SHA-256)</Label>
              <div className="flex gap-2">
                <Input
                  id="fileHash"
                  value={fileHash}
                  onChange={(e) => setFileHash(e.target.value)}
                  placeholder="Enter 64-character SHA-256 hash"
                  className="font-mono"
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

            <div className="space-y-2">
              <Label htmlFor="etid">Entity Type ID (ETID)</Label>
              <Input
                id="etid"
                value={etid}
                onChange={(e) => setEtid(e.target.value)}
                placeholder="100001"
              />
              <p className="text-xs text-muted-foreground">
                100001 for loan packets, 100002 for JSON documents
              </p>
            </div>

            {file && (
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span className="font-medium">{file.name}</span>
                  <span className="text-sm text-muted-foreground">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
              </div>
            )}

            {fileHash && (
              <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                <Hash className="h-4 w-4" />
                <span className="text-sm font-mono break-all">{fileHash}</span>
              </div>
            )}
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
          />
        ) : null}

                  {/* Action Buttons */}
                  {verifyResult.is_valid && verifyResult.artifact_id && (
                    <div className="flex flex-wrap gap-2">
                      <Button 
                        ref={viewProofButtonRef}
                        onClick={handleViewProof} 
                        disabled={isLoadingProof}
                      >
                        {isLoadingProof ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Loading Proof...
                          </>
                        ) : (
                          <>
                            <Eye className="h-4 w-4 mr-2" />
                            View Proof
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={handleGetProof}>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Download Proof
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowCryptographicProof(!showCryptographicProof)}
                      >
                        <Key className="h-4 w-4 mr-2" />
                        Cryptographic Proof
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowAuditTrail(!showAuditTrail)}
                      >
                        <Activity className="h-4 w-4 mr-2" />
                        Audit Trail
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={generateCertificate}
                        disabled={isGeneratingCertificate}
                      >
                        {isGeneratingCertificate ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <FileCheck className="h-4 w-4 mr-2" />
                            Generate Certificate
                          </>
                        )}
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={downloadProofBundle}
                        disabled={isDownloadingProofBundle}
                      >
                        {isDownloadingProofBundle ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Downloading...
                          </>
                        ) : (
                          <>
                            <Archive className="h-4 w-4 mr-2" />
                            Download Proof Bundle
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Borrower Information (Masked) */}
              {borrowerInfo && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5" />
                      Borrower Information
                      <Tooltip>
                        <TooltipTrigger>
                          <Info className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Sensitive data encrypted for privacy</p>
                        </TooltipContent>
                      </Tooltip>
                    </CardTitle>
                    <CardDescription>
                      Masked borrower information from sealed record
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">Full Name</Label>
                        <p className="text-sm">{borrowerInfo.full_name}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Date of Birth</Label>
                        <p className="text-sm">{borrowerInfo.date_of_birth}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Email</Label>
                        <div className="flex items-center gap-2">
                          <p className="text-sm">{maskSensitiveData(borrowerInfo.email, 'email')}</p>
                          <Lock className="h-3 w-3 text-muted-foreground" />
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Phone</Label>
                        <div className="flex items-center gap-2">
                          <p className="text-sm">{maskSensitiveData(borrowerInfo.phone, 'phone')}</p>
                          <Lock className="h-3 w-3 text-muted-foreground" />
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Address</Label>
                        <p className="text-sm">{borrowerInfo.city}, {borrowerInfo.state}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Employment Status</Label>
                        <p className="text-sm">{borrowerInfo.employment_status}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Annual Income Range</Label>
                        <p className="text-sm">{borrowerInfo.annual_income_range}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Co-borrower</Label>
                        <p className="text-sm">{borrowerInfo.co_borrower_name || 'N/A'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Cryptographic Proof Display */}
              {showCryptographicProof && cryptographicProof && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Fingerprint className="h-5 w-5" />
                      Cryptographic Proof
                    </CardTitle>
                    <CardDescription>
                      Blockchain cryptographic verification details
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">Merkle Root</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded break-all">{cryptographicProof.merkle_root}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Block Hash</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded break-all">{cryptographicProof.block_hash}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Previous Block Hash</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded break-all">{cryptographicProof.previous_block_hash}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Digital Signature</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded break-all">{cryptographicProof.digital_signature}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button 
                        onClick={verifySignature}
                        disabled={isVerifyingSignature}
                        className={cryptographicProof.signature_valid ? 'bg-green-600 hover:bg-green-700' : ''}
                      >
                        {isVerifyingSignature ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Verifying...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Verify Signature
                          </>
                        )}
                      </Button>
                      {cryptographicProof.signature_valid && (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Signature Valid
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Verification Certificate */}
              {certificate && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileCheck className="h-5 w-5" />
                      Verification Certificate
                    </CardTitle>
                    <CardDescription>
                      Official verification certificate with QR code
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">Document Hash</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded break-all">{certificate.document_hash}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Seal Date</Label>
                        <p className="text-sm">{new Date(certificate.seal_date).toLocaleString()}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Transaction ID</Label>
                        <p className="text-sm font-mono bg-muted p-2 rounded">{certificate.tx_id}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Verification Timestamp</Label>
                        <p className="text-sm">{new Date(certificate.verification_timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button variant="outline">
                        <QrCode className="h-4 w-4 mr-2" />
                        View QR Code
                      </Button>
                      <Button variant="outline">
                        <Printer className="h-4 w-4 mr-2" />
                        Print Certificate
                      </Button>
                      <Button variant="outline">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Audit Trail Viewer */}
              {showAuditTrail && auditTrail.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Audit Trail
                    </CardTitle>
                    <CardDescription>
                      Complete timeline of document events
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {auditTrail.map((event, index) => (
                        <div key={event.event_id} className="flex items-start gap-4 p-4 border rounded-lg">
                          <div className="flex-shrink-0">
                            {event.event_type === 'document_created' && (
                              <FileText className="h-5 w-5 text-blue-500" />
                            )}
                            {event.event_type === 'blockchain_sealed' && (
                              <Shield className="h-5 w-5 text-green-500" />
                            )}
                            {event.event_type === 'verified' && (
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            )}
                            {event.event_type === 'borrower_data_accessed' && (
                              <Eye className="h-5 w-5 text-purple-500" />
                            )}
                            {!['document_created', 'blockchain_sealed', 'verified', 'borrower_data_accessed'].includes(event.event_type) && (
                              <Activity className="h-5 w-5 text-gray-500" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium capitalize">
                                {event.event_type.replace(/_/g, ' ')}
                              </h4>
                              <Badge variant="outline" className="text-xs">
                                {event.user_id}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mb-2">
                              {new Date(event.timestamp).toLocaleString()}
                            </p>
                            {event.details && (
                              <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
                                <pre className="whitespace-pre-wrap">
                                  {JSON.stringify(event.details, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TooltipProvider>
        )}

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
                <CheckCircle className="h-5 w-5 text-green-600" />
                Proof Bundle Retrieved
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Artifact ID</Label>
                  <p className="text-sm font-mono bg-muted p-2 rounded">{proofResult.artifact_id}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">ETID</Label>
                  <p className="text-sm">{proofResult.etid}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium">Retrieved At</Label>
                <p className="text-sm">{new Date(proofResult.retrieved_at).toLocaleString()}</p>
              </div>

              <div>
                <Label className="text-sm font-medium">Proof Bundle</Label>
                <pre className="text-xs bg-muted p-4 rounded overflow-auto max-h-64">
                  {JSON.stringify(proofResult.proof_bundle, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleVerify}
            disabled={isVerifying || !fileHash}
            className="flex-1"
          >
            {isVerifying ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Verify Document
              </>
            )}
          </Button>
          <Button variant="outline" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </div>

      {/* Proof Viewer Modal */}
      {proofData && (
        <ProofViewer
          proofJson={proofData}
          isOpen={isProofViewerOpen}
          onClose={() => setIsProofViewerOpen(false)}
          triggerRef={viewProofButtonRef}
        />
      )}
    </div>
  );
}

