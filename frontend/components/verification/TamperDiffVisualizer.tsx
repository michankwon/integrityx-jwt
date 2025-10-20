"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  AlertTriangle, 
  XCircle, 
  Eye, 
  EyeOff, 
  FileText, 
  Hash, 
  Shield,
  Download,
  Copy,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { toast } from 'react-hot-toast';

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

interface TamperDiffVisualizerProps {
  diffData: TamperDiffData;
  isVisible?: boolean;
  onToggleVisibility?: () => void;
}

const severityColors = {
  low: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  medium: 'bg-orange-100 text-orange-800 border-orange-200',
  high: 'bg-red-100 text-red-800 border-red-200',
  critical: 'bg-red-200 text-red-900 border-red-300'
};

const severityIcons = {
  low: <AlertTriangle className="h-4 w-4" />,
  medium: <AlertTriangle className="h-4 w-4" />,
  high: <XCircle className="h-4 w-4" />,
  critical: <XCircle className="h-4 w-4" />
};

export function TamperDiffVisualizer({ 
  diffData, 
  isVisible = true, 
  onToggleVisibility 
}: TamperDiffVisualizerProps) {
  const [expandedDifferences, setExpandedDifferences] = useState<Set<number>>(new Set());
  const [showRawData, setShowRawData] = useState(false);

  const toggleDifference = (index: number) => {
    const newExpanded = new Set(expandedDifferences);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedDifferences(newExpanded);
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard`);
  };

  const downloadDiffReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      tamperAnalysis: diffData,
      summary: {
        totalDifferences: diffData.differences.length,
        criticalIssues: diffData.differences.filter(d => d.severity === 'critical').length,
        highIssues: diffData.differences.filter(d => d.severity === 'high').length,
        mediumIssues: diffData.differences.filter(d => d.severity === 'medium').length,
        lowIssues: diffData.differences.filter(d => d.severity === 'low').length
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tamper-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Tamper analysis report downloaded');
  };

  if (!isVisible) {
    return (
      <Button
        variant="outline"
        onClick={onToggleVisibility}
        className="w-full border-red-200 text-red-600 hover:bg-red-50"
      >
        <Eye className="h-4 w-4 mr-2" />
        Show Tamper Analysis
      </Button>
    );
  }

  return (
    <Card className="border-red-200 bg-red-50/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-600" />
            <CardTitle className="text-red-800">Tamper Detection Analysis</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={downloadDiffReport}
              className="border-red-200 text-red-600 hover:bg-red-100"
            >
              <Download className="h-4 w-4 mr-1" />
              Download Report
            </Button>
            {onToggleVisibility && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleVisibility}
                className="text-red-600 hover:bg-red-100"
              >
                <EyeOff className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        <CardDescription className="text-red-700">
          Document integrity compromised. {diffData.differences.length} difference(s) detected.
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

        {/* Hash Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Hash className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">Original Hash (Blockchain)</span>
            </div>
            <div className="font-mono text-xs bg-gray-100 p-2 rounded break-all">
              {diffData.originalHash}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(diffData.originalHash, 'Original hash')}
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
              {diffData.currentHash}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(diffData.currentHash, 'Current hash')}
              className="mt-2 text-xs"
            >
              <Copy className="h-3 w-3 mr-1" />
              Copy
            </Button>
          </div>
        </div>

        {/* Detailed Differences */}
        <Tabs defaultValue="differences" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="differences">Differences ({diffData.differences.length})</TabsTrigger>
            <TabsTrigger value="evidence">Tamper Evidence</TabsTrigger>
            <TabsTrigger value="blockchain">Blockchain Proof</TabsTrigger>
          </TabsList>

          <TabsContent value="differences" className="space-y-3">
            {diffData.differences.map((diff, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${severityColors[diff.severity]}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {severityIcons[diff.severity]}
                    <span className="font-medium capitalize">{diff.field}</span>
                    <Badge variant="outline" className={severityColors[diff.severity]}>
                      {diff.severity}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleDifference(index)}
                    className="text-xs"
                  >
                    {expandedDifferences.has(index) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                
                <p className="text-sm mt-2 opacity-90">{diff.description}</p>
                
                {expandedDifferences.has(index) && (
                  <div className="mt-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium opacity-75">Original Value:</label>
                        <div className="font-mono text-xs bg-white/50 p-2 rounded mt-1 break-all">
                          {diff.originalValue}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-medium opacity-75">Current Value:</label>
                        <div className="font-mono text-xs bg-white/50 p-2 rounded mt-1 break-all">
                          {diff.currentValue}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </TabsContent>

          <TabsContent value="evidence" className="space-y-4">
            <div className="p-4 bg-white border border-red-200 rounded-lg">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Tamper Evidence
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="font-medium">Detection Time:</span>
                  <span>{new Date(diffData.tamperEvidence.timestamp).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Location:</span>
                  <span>{diffData.tamperEvidence.location}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Method:</span>
                  <span>{diffData.tamperEvidence.method}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Confidence:</span>
                  <Badge variant="outline" className="bg-red-100 text-red-800">
                    {Math.round(diffData.tamperEvidence.confidence * 100)}%
                  </Badge>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="blockchain" className="space-y-4">
            <div className="p-4 bg-white border border-red-200 rounded-lg">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Blockchain Verification
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="font-medium">Original TX ID:</span>
                  <span className="font-mono text-xs">{diffData.blockchainProof.originalTxId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Current TX ID:</span>
                  <span className="font-mono text-xs">{diffData.blockchainProof.currentTxId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Block Height:</span>
                  <span>{diffData.blockchainProof.blockHeight}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">Verification Status:</span>
                  <Badge 
                    variant="outline" 
                    className={
                      diffData.blockchainProof.verificationStatus === 'verified' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }
                  >
                    {diffData.blockchainProof.verificationStatus}
                  </Badge>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* Raw Data Toggle */}
        <div className="pt-4 border-t border-red-200">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRawData(!showRawData)}
            className="text-red-600 border-red-200 hover:bg-red-100"
          >
            {showRawData ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
            {showRawData ? 'Hide' : 'Show'} Raw Data
          </Button>
          
          {showRawData && (
            <div className="mt-3 p-3 bg-white border border-red-200 rounded-lg">
              <pre className="text-xs overflow-auto max-h-64">
                {JSON.stringify(diffData, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
