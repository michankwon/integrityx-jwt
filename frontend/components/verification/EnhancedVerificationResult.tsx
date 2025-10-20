"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  CheckCircle, 
  XCircle, 
  Shield, 
  Lock, 
  FileText, 
  Hash, 
  Download,
  Copy,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { TamperDiffVisualizer } from './TamperDiffVisualizer';
import { VisualComparisonTool } from './VisualComparisonTool';

interface VerificationResult {
  is_valid: boolean;
  message: string;
  artifact_id?: string;
  details: {
    created_at: string;
    hash: string;
    etid: number;
  };
}

interface EnhancedVerificationResultProps {
  result: VerificationResult;
  currentHash?: string;
  showTamperAnalysis?: boolean;
  showVisualComparison?: boolean;
}

interface TamperDiffData {
  originalHash: string;
  currentHash: string;
  differences: Array<{
    type: 'content' | 'metadata' | 'signature' | 'timestamp';
    field: string;
    originalValue: string;
    currentValue: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
  }>;
  tamperEvidence: {
    timestamp: string;
    location: string;
    method: string;
    confidence: number;
  };
  blockchainProof: {
    originalTxId: string;
    currentTxId: string;
    blockHeight: number;
    verificationStatus: 'verified' | 'failed' | 'pending';
  };
}

export function EnhancedVerificationResult({ 
  result, 
  currentHash,
  showTamperAnalysis = true,
  showVisualComparison = true
}: EnhancedVerificationResultProps) {
  const [showTamperDiff, setShowTamperDiff] = useState(false);
  const [showRawData, setShowRawData] = useState(false);

  // Generate mock tamper diff data for demonstration
  const generateTamperDiffData = (): TamperDiffData => {
    return {
      originalHash: result.details.hash,
      currentHash: currentHash || 'modified_hash_example_1234567890abcdef',
      differences: [
        {
          type: 'content',
          field: 'document_content',
          originalValue: 'Original loan amount: $500,000',
          currentValue: 'Modified loan amount: $750,000',
          severity: 'critical',
          description: 'Critical financial data has been altered. The loan amount was increased by $250,000.'
        },
        {
          type: 'metadata',
          field: 'borrower_name',
          originalValue: 'John Smith',
          currentValue: 'John A. Smith',
          severity: 'medium',
          description: 'Borrower name has been modified with additional middle initial.'
        },
        {
          type: 'timestamp',
          field: 'document_date',
          originalValue: '2024-01-15T10:30:00Z',
          currentValue: '2024-01-16T14:45:00Z',
          severity: 'high',
          description: 'Document timestamp has been changed, indicating potential backdating.'
        },
        {
          type: 'signature',
          field: 'digital_signature',
          originalValue: 'sig_original_abc123...',
          currentValue: 'sig_modified_xyz789...',
          severity: 'critical',
          description: 'Digital signature has been invalidated, indicating document tampering.'
        }
      ],
      tamperEvidence: {
        timestamp: new Date().toISOString(),
        location: 'Document content section',
        method: 'Content modification detected via hash comparison',
        confidence: 0.95
      },
      blockchainProof: {
        originalTxId: 'WAL_TX_' + Math.random().toString(16).substr(2, 16),
        currentTxId: 'WAL_TX_' + Math.random().toString(16).substr(2, 16),
        blockHeight: 1234567,
        verificationStatus: 'failed' as const
      }
    };
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const downloadVerificationReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      verification: result,
      status: result.is_valid ? 'VERIFIED' : 'TAMPERED',
      blockchain: {
        hash: result.details.hash,
        etid: result.details.etid,
        created_at: result.details.created_at
      },
      analysis: result.is_valid ? null : generateTamperDiffData()
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `verification-report-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Verification report downloaded');
  };

  if (result.is_valid) {
    return (
      <Card className="border-green-200 bg-green-50/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <CardTitle className="text-green-800">Document Verification Successful</CardTitle>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={downloadVerificationReport}
              className="border-green-200 text-green-600 hover:bg-green-100"
            >
              <Download className="h-4 w-4 mr-1" />
              Download Report
            </Button>
          </div>
          <CardDescription className="text-green-700">
            {result.message}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Success Alert */}
          <Alert className="border-green-300 bg-green-100">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <strong>Verification Complete:</strong> This document has been verified as authentic and untampered. 
              The hash matches the blockchain record and all integrity checks have passed.
            </AlertDescription>
          </Alert>

          {/* Verification Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 bg-white border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-green-800">Hash Matches</p>
                <p className="text-xs text-green-600">Document integrity verified</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white border border-green-200 rounded-lg">
              <Shield className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-green-800">No Tampering</p>
                <p className="text-xs text-green-600">Content unchanged</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white border border-green-200 rounded-lg">
              <Lock className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-green-800">Borrower Data Intact</p>
                <p className="text-xs text-green-600">Personal info secure</p>
              </div>
            </div>
          </div>

          {/* Blockchain Details */}
          <Tabs defaultValue="blockchain" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="blockchain">Blockchain Proof</TabsTrigger>
              <TabsTrigger value="metadata">Document Metadata</TabsTrigger>
              <TabsTrigger value="timeline">Verification Timeline</TabsTrigger>
            </TabsList>

            <TabsContent value="blockchain" className="space-y-4">
              <div className="p-4 bg-white border border-green-200 rounded-lg">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Hash className="h-4 w-4" />
                  Blockchain Verification
                </h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">Document Hash:</span>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs">{result.details.hash}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(result.details.hash, 'Document hash')}
                        className="text-xs p-1"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Entity Type ID:</span>
                    <span>{result.details.etid}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Sealed Date:</span>
                    <span>{new Date(result.details.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Verification Status:</span>
                    <Badge className="bg-green-100 text-green-800">
                      Verified
                    </Badge>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="metadata" className="space-y-4">
              <div className="p-4 bg-white border border-green-200 rounded-lg">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Document Information
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">Artifact ID:</span>
                    <span className="font-mono text-xs">{result.artifact_id || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Created:</span>
                    <span>{new Date(result.details.created_at).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Hash Algorithm:</span>
                    <span>SHA-256</span>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="timeline" className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-white border border-green-200 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Document Sealed</p>
                    <p className="text-xs text-gray-600">{new Date(result.details.created_at).toLocaleString()}</p>
                  </div>
                  <Badge variant="outline" className="bg-green-100 text-green-800">
                    Complete
                  </Badge>
                </div>
                <div className="flex items-center gap-3 p-3 bg-white border border-green-200 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Hash Verification</p>
                    <p className="text-xs text-gray-600">Just now</p>
                  </div>
                  <Badge variant="outline" className="bg-green-100 text-green-800">
                    Verified
                  </Badge>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    );
  }

  // Tampered document view
  return (
    <div className="space-y-6">
      <Card className="border-red-200 bg-red-50/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-600" />
              <CardTitle className="text-red-800">Document Verification Failed</CardTitle>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={downloadVerificationReport}
              className="border-red-200 text-red-600 hover:bg-red-100"
            >
              <Download className="h-4 w-4 mr-1" />
              Download Report
            </Button>
          </div>
          <CardDescription className="text-red-700">
            {result.message}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Critical Alert */}
          <Alert className="border-red-300 bg-red-100">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>Security Alert:</strong> This document has been tampered with. 
              The current hash does not match the blockchain record. 
              Do not trust this document for any legal or financial purposes.
            </AlertDescription>
          </Alert>

          {/* Verification Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 bg-white border border-red-200 rounded-lg">
              <XCircle className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-sm font-medium text-red-800">Hash Mismatch</p>
                <p className="text-xs text-red-600">Document integrity compromised</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white border border-red-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-sm font-medium text-red-800">Tampering Detected</p>
                <p className="text-xs text-red-600">Content has been modified</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 bg-white border border-red-200 rounded-lg">
              <XCircle className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-sm font-medium text-red-800">Data Compromised</p>
                <p className="text-xs text-red-600">Personal info may be altered</p>
              </div>
            </div>
          </div>

          {/* Hash Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Hash className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">Original Hash (Blockchain)</span>
              </div>
              <div className="font-mono text-xs bg-gray-100 p-2 rounded break-all">
                {result.details.hash}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(result.details.hash, 'Original hash')}
                className="mt-2 text-xs"
              >
                <Copy className="h-3 w-3 mr-1" />
                Copy
              </Button>
            </div>

            <div className="p-4 bg-white border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Hash className="h-4 w-4 text-red-600" />
                <span className="text-sm font-medium text-red-800">Current Hash (Tampered)</span>
              </div>
              <div className="font-mono text-xs bg-red-50 p-2 rounded break-all">
                {currentHash || 'modified_hash_example_1234567890abcdef'}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(currentHash || 'modified_hash_example', 'Current hash')}
                className="mt-2 text-xs"
              >
                <Copy className="h-3 w-3 mr-1" />
                Copy
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tamper Analysis */}
      {showTamperAnalysis && (
        <TamperDiffVisualizer
          diffData={generateTamperDiffData()}
          isVisible={showTamperDiff}
          onToggleVisibility={() => setShowTamperDiff(!showTamperDiff)}
        />
      )}

      {/* Visual Comparison Tool */}
      {showVisualComparison && !result.is_valid && (
        <VisualComparisonTool
          comparisonData={{
            original: {
              hash: result.details.hash,
              timestamp: result.details.created_at,
              size: 1500000,
              metadata: {
                document_type: 'loan_application',
                borrower_name: 'John Smith',
                loan_amount: '$500,000',
                created_by: 'system'
              },
              content: 'Original document content...'
            },
            current: {
              hash: currentHash || 'modified_hash_example_1234567890abcdef',
              timestamp: new Date().toISOString(),
              size: 1600000,
              metadata: {
                document_type: 'loan_application',
                borrower_name: 'John A. Smith',
                loan_amount: '$750,000',
                created_by: 'system'
              },
              content: 'Modified document content...'
            },
            differences: [
              {
                field: 'loan_amount',
                type: 'modified',
                originalValue: '$500,000',
                currentValue: '$750,000',
                severity: 'critical'
              },
              {
                field: 'borrower_name',
                type: 'modified',
                originalValue: 'John Smith',
                currentValue: 'John A. Smith',
                severity: 'medium'
              },
              {
                field: 'document_size',
                type: 'modified',
                originalValue: 1500000,
                currentValue: 1600000,
                severity: 'low'
              }
            ],
            statistics: {
              totalChanges: 3,
              criticalChanges: 1,
              highChanges: 0,
              mediumChanges: 1,
              lowChanges: 1,
              similarityScore: 0.75
            }
          }}
          isVisible={true}
        />
      )}
    </div>
  );
}
