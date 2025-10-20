"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Hash, 
  Eye, 
  EyeOff, 
  Download, 
  Copy, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  BarChart3
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ComparisonData {
  original: {
    hash: string;
    timestamp: string;
    size: number;
    metadata: Record<string, any>;
    content: string;
  };
  current: {
    hash: string;
    timestamp: string;
    size: number;
    metadata: Record<string, any>;
    content: string;
  };
  differences: Array<{
    field: string;
    type: 'added' | 'removed' | 'modified';
    originalValue: any;
    currentValue: any;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  statistics: {
    totalChanges: number;
    criticalChanges: number;
    highChanges: number;
    mediumChanges: number;
    lowChanges: number;
    similarityScore: number;
  };
}

interface VisualComparisonToolProps {
  comparisonData: ComparisonData;
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

const changeTypeColors = {
  added: 'bg-green-100 text-green-800 border-green-200',
  removed: 'bg-red-100 text-red-800 border-red-200',
  modified: 'bg-orange-100 text-orange-800 border-orange-200'
};

export function VisualComparisonTool({ 
  comparisonData, 
  isVisible = true, 
  onToggleVisibility 
}: VisualComparisonToolProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showRawData, setShowRawData] = useState(false);
  const [expandedDifferences, setExpandedDifferences] = useState<Set<number>>(new Set());

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

  const downloadComparisonReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      comparison: comparisonData,
      summary: {
        totalChanges: comparisonData.statistics.totalChanges,
        criticalIssues: comparisonData.statistics.criticalChanges,
        highIssues: comparisonData.statistics.highChanges,
        mediumIssues: comparisonData.statistics.mediumChanges,
        lowIssues: comparisonData.statistics.lowChanges,
        similarityScore: comparisonData.statistics.similarityScore
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `document-comparison-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Comparison report downloaded');
  };

  if (!isVisible) {
    return (
      <Button
        variant="outline"
        onClick={onToggleVisibility}
        className="w-full border-blue-200 text-blue-600 hover:bg-blue-50"
      >
        <Eye className="h-4 w-4 mr-2" />
        Show Visual Comparison
      </Button>
    );
  }

  return (
    <Card className="border-blue-200 bg-blue-50/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-blue-800">Visual Document Comparison</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={downloadComparisonReport}
              className="border-blue-200 text-blue-600 hover:bg-blue-100"
            >
              <Download className="h-4 w-4 mr-1" />
              Download Report
            </Button>
            {onToggleVisibility && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleVisibility}
                className="text-blue-600 hover:bg-blue-100"
              >
                <EyeOff className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
        <CardDescription className="text-blue-700">
          Side-by-side comparison of original vs current document with {comparisonData.differences.length} difference(s) detected.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Statistics Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-white border border-blue-200 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{comparisonData.statistics.totalChanges}</div>
            <div className="text-sm text-blue-800">Total Changes</div>
          </div>
          <div className="p-4 bg-white border border-red-200 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">{comparisonData.statistics.criticalChanges}</div>
            <div className="text-sm text-red-800">Critical</div>
          </div>
          <div className="p-4 bg-white border border-orange-200 rounded-lg text-center">
            <div className="text-2xl font-bold text-orange-600">{comparisonData.statistics.highChanges}</div>
            <div className="text-sm text-orange-800">High</div>
          </div>
          <div className="p-4 bg-white border border-green-200 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{Math.round(comparisonData.statistics.similarityScore * 100)}%</div>
            <div className="text-sm text-green-800">Similarity</div>
          </div>
        </div>

        {/* Similarity Score Visualization */}
        <div className="p-4 bg-white border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Document Similarity Score</span>
            <span className="text-sm font-bold">{Math.round(comparisonData.statistics.similarityScore * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                comparisonData.statistics.similarityScore > 0.8 ? 'bg-green-500' :
                comparisonData.statistics.similarityScore > 0.6 ? 'bg-yellow-500' :
                comparisonData.statistics.similarityScore > 0.4 ? 'bg-orange-500' : 'bg-red-500'
              }`}
              style={{ width: `${comparisonData.statistics.similarityScore * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Detailed Comparison */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="hashes">Hash Comparison</TabsTrigger>
            <TabsTrigger value="differences">Differences</TabsTrigger>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Original Document */}
              <div className="p-4 bg-white border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="font-medium text-green-800">Original Document</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">Size:</span>
                    <span>{comparisonData.original.size.toLocaleString()} bytes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Timestamp:</span>
                    <span>{new Date(comparisonData.original.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Hash:</span>
                    <span className="font-mono text-xs">{comparisonData.original.hash.substring(0, 16)}...</span>
                  </div>
                </div>
              </div>

              {/* Current Document */}
              <div className="p-4 bg-white border border-red-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <span className="font-medium text-red-800">Current Document</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">Size:</span>
                    <span>{comparisonData.current.size.toLocaleString()} bytes</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Timestamp:</span>
                    <span>{new Date(comparisonData.current.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Hash:</span>
                    <span className="font-mono text-xs">{comparisonData.current.hash.substring(0, 16)}...</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Change Summary */}
            <div className="p-4 bg-white border border-blue-200 rounded-lg">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Change Summary
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-lg font-bold text-red-600">{comparisonData.statistics.criticalChanges}</div>
                  <div className="text-xs text-red-800">Critical</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-orange-600">{comparisonData.statistics.highChanges}</div>
                  <div className="text-xs text-orange-800">High</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-yellow-600">{comparisonData.statistics.mediumChanges}</div>
                  <div className="text-xs text-yellow-800">Medium</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">{comparisonData.statistics.lowChanges}</div>
                  <div className="text-xs text-green-800">Low</div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="hashes" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-white border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">Original Hash</span>
                </div>
                <div className="font-mono text-xs bg-gray-100 p-2 rounded break-all">
                  {comparisonData.original.hash}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(comparisonData.original.hash, 'Original hash')}
                  className="mt-2 text-xs"
                >
                  <Copy className="h-3 w-3 mr-1" />
                  Copy
                </Button>
              </div>

              <div className="p-4 bg-white border border-red-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="h-4 w-4 text-red-600" />
                  <span className="text-sm font-medium text-red-800">Current Hash</span>
                </div>
                <div className="font-mono text-xs bg-red-50 p-2 rounded break-all">
                  {comparisonData.current.hash}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(comparisonData.current.hash, 'Current hash')}
                  className="mt-2 text-xs"
                >
                  <Copy className="h-3 w-3 mr-1" />
                  Copy
                </Button>
              </div>
            </div>

            {/* Hash Comparison Visualization */}
            <div className="p-4 bg-white border border-blue-200 rounded-lg">
              <h4 className="font-medium mb-3">Hash Comparison</h4>
              <div className="space-y-2">
                {Array.from({ length: 8 }, (_, i) => {
                  const originalChunk = comparisonData.original.hash.substring(i * 8, (i + 1) * 8);
                  const currentChunk = comparisonData.current.hash.substring(i * 8, (i + 1) * 8);
                  const isDifferent = originalChunk !== currentChunk;
                  
                  return (
                    <div key={i} className="flex items-center gap-2 text-xs font-mono">
                      <span className="w-8 text-gray-500">{i * 8 + 1}-{(i + 1) * 8}</span>
                      <div className={`flex-1 p-1 rounded ${isDifferent ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {originalChunk}
                      </div>
                      <div className={`flex-1 p-1 rounded ${isDifferent ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                        {currentChunk}
                      </div>
                      <div className="w-4 text-center">
                        {isDifferent ? <XCircle className="h-3 w-3 text-red-600" /> : <CheckCircle className="h-3 w-3 text-green-600" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="differences" className="space-y-3">
            {comparisonData.differences.map((diff, index) => (
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
                    <Badge variant="outline" className={changeTypeColors[diff.type]}>
                      {diff.type}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleDifference(index)}
                    className="text-xs"
                  >
                    {expandedDifferences.has(index) ? 'Collapse' : 'Expand'}
                  </Button>
                </div>
                
                {expandedDifferences.has(index) && (
                  <div className="mt-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium opacity-75">Original Value:</label>
                        <div className="font-mono text-xs bg-white/50 p-2 rounded mt-1 break-all">
                          {typeof diff.originalValue === 'object' 
                            ? JSON.stringify(diff.originalValue, null, 2)
                            : String(diff.originalValue)
                          }
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-medium opacity-75">Current Value:</label>
                        <div className="font-mono text-xs bg-white/50 p-2 rounded mt-1 break-all">
                          {typeof diff.currentValue === 'object' 
                            ? JSON.stringify(diff.currentValue, null, 2)
                            : String(diff.currentValue)
                          }
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </TabsContent>

          <TabsContent value="metadata" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-white border border-green-200 rounded-lg">
                <h4 className="font-medium mb-3 text-green-800">Original Metadata</h4>
                <div className="space-y-2 text-sm">
                  {Object.entries(comparisonData.original.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="font-medium">{key}:</span>
                      <span className="font-mono text-xs">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-white border border-red-200 rounded-lg">
                <h4 className="font-medium mb-3 text-red-800">Current Metadata</h4>
                <div className="space-y-2 text-sm">
                  {Object.entries(comparisonData.current.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="font-medium">{key}:</span>
                      <span className="font-mono text-xs">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* Raw Data Toggle */}
        <div className="pt-4 border-t border-blue-200">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRawData(!showRawData)}
            className="text-blue-600 border-blue-200 hover:bg-blue-100"
          >
            {showRawData ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
            {showRawData ? 'Hide' : 'Show'} Raw Data
          </Button>
          
          {showRawData && (
            <div className="mt-3 p-3 bg-white border border-blue-200 rounded-lg">
              <pre className="text-xs overflow-auto max-h-64">
                {JSON.stringify(comparisonData, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
