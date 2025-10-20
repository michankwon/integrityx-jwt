'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Download, 
  Eye, 
  Shield, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  XCircle,
  FileText,
  Calendar,
  TrendingUp,
  Activity,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-react';
import { simpleToast as toast } from '@/components/ui/simple-toast';
import { 
  searchLoanDocuments, 
  getBorrowerInfo, 
  getAuditTrail, 
  verifyLoanDocument,
  downloadLoanDocument,
  formatLoanAmount,
  formatDate,
  getStatusBadgeColor,
  type LoanSearchResult,
  type BorrowerInfo,
  type AuditEvent,
} from '@/lib/api/loanDocuments';

interface AdminStats {
  totalDocuments: number;
  documentsToday: number;
  pendingSeals: number;
  failedSeals: number;
  errorRate: number;
}

interface FilterState {
  search: string;
  dateFrom: string;
  dateTo: string;
  amountMin: string;
  amountMax: string;
  sealStatus: string;
}

interface PaginationState {
  page: number;
  limit: number;
  total: number;
}

export default function AdminLoanDocumentsPage() {
  // State management
  const [documents, setDocuments] = useState<LoanSearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [stats, setStats] = useState<AdminStats>({
    totalDocuments: 0,
    documentsToday: 0,
    pendingSeals: 0,
    failedSeals: 0,
    errorRate: 0
  });

  // Filter and pagination state
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    dateFrom: '',
    dateTo: '',
    amountMin: '',
    amountMax: '',
    sealStatus: ''
  });
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    limit: 50,
    total: 0
  });
  const [sortField, setSortField] = useState<string>('upload_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Modal states
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<LoanSearchResult | null>(null);
  const [borrowerInfo, setBorrowerInfo] = useState<BorrowerInfo | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditEvent[]>([]);

  // Loading states
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [loadingVerification, setLoadingVerification] = useState(false);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  // Auto-refresh state
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Load documents with current filters and pagination
  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true);
      
      const searchParams = {
        limit: pagination.limit,
        offset: (pagination.page - 1) * pagination.limit,
        ...(filters.search && { borrower_name: filters.search }),
        ...(filters.dateFrom && { date_from: filters.dateFrom }),
        ...(filters.dateTo && { date_to: filters.dateTo }),
        ...(filters.amountMin && { amount_min: parseInt(filters.amountMin) }),
        ...(filters.amountMax && { amount_max: parseInt(filters.amountMax) }),
        ...(filters.sealStatus && { is_sealed: filters.sealStatus === 'sealed' })
      };

      const response = await searchLoanDocuments(searchParams);
      
      setDocuments(response.results);
      setPagination(prev => ({ ...prev, total: response.total_count }));
      
      // Calculate stats
      const today = new Date().toISOString().split('T')[0];
      const documentsToday = response.results.filter(doc => 
        doc.upload_date.startsWith(today)
      ).length;
      
      const pendingSeals = response.results.filter(doc => 
        doc.sealed_status.toLowerCase().includes('pending')
      ).length;
      
      const failedSeals = response.results.filter(doc => 
        doc.sealed_status.toLowerCase().includes('failed')
      ).length;
      
      setStats({
        totalDocuments: response.total_count,
        documentsToday,
        pendingSeals,
        failedSeals,
        errorRate: response.total_count > 0 ? (failedSeals / response.total_count) * 100 : 0
      });

      setLastRefresh(new Date());
      
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [filters, pagination.page, pagination.limit]);

  // Auto-refresh effect
  useEffect(() => {
    loadDocuments();
    
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadDocuments();
      }, 30000); // 30 seconds
      
      return () => clearInterval(interval);
    }
  }, [loadDocuments, autoRefresh]);

  // Handle sort
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Handle document selection
  const selectDocument = (documentId: string) => {
    const newSelected = new Set(selectedDocuments);
    newSelected.add(documentId);
    setSelectedDocuments(newSelected);
  };

  const deselectDocument = (documentId: string) => {
    const newSelected = new Set(selectedDocuments);
    newSelected.delete(documentId);
    setSelectedDocuments(newSelected);
  };

  // Handle document selection change
  const handleSelectDocumentChange = (documentId: string, checked: boolean | string) => {
    if (typeof checked === 'boolean') {
      if (checked === true) {
        selectDocument(documentId);
      } else {
        deselectDocument(documentId);
      }
    }
  };

  // Handle select all
  const selectAllDocuments = () => {
    setSelectedDocuments(new Set(documents.map(doc => doc.artifact_id)));
  };

  const deselectAllDocuments = () => {
    setSelectedDocuments(new Set());
  };

  // Handle select all checkbox change
  const handleSelectAllChange = (checked: boolean | string) => {
    if (typeof checked === 'boolean') {
      if (checked === true) {
        selectAllDocuments();
      } else {
        deselectAllDocuments();
      }
    }
  };

  // View document details
  const handleViewDetails = async (document: LoanSearchResult) => {
    try {
      setLoadingDetails(true);
      setSelectedDocument(document);
      setShowDetailsModal(true);
      
      // Load borrower info
      const borrower = await getBorrowerInfo(document.artifact_id);
      setBorrowerInfo(borrower);
      
    } catch (error) {
      console.error('Failed to load document details:', error);
      toast.error('Failed to load document details.');
    } finally {
      setLoadingDetails(false);
    }
  };

  // View audit trail
  const handleViewAuditTrail = async (document: LoanSearchResult) => {
    try {
      setLoadingAudit(true);
      setSelectedDocument(document);
      setShowAuditModal(true);
      
      const audit = await getAuditTrail(document.artifact_id);
      setAuditTrail(audit);
      
    } catch (error) {
      console.error('Failed to load audit trail:', error);
      toast.error('Failed to load audit trail.');
    } finally {
      setLoadingAudit(false);
    }
  };

  // Verify document
  const handleVerifyDocument = async (document: LoanSearchResult) => {
    try {
      setLoadingVerification(true);
      
      // For now, we'll use a placeholder hash - in real implementation,
      // you'd get the actual hash from the document
      const result = await verifyLoanDocument(document.artifact_id, 'placeholder-hash');
      
      toast.success(`Document verification: ${result.status}`);
      
    } catch (error) {
      console.error('Failed to verify document:', error);
      toast.error('Failed to verify document.');
    } finally {
      setLoadingVerification(false);
    }
  };

  // Export document
  const handleExportDocument = async (document: LoanSearchResult) => {
    try {
      const blob = await downloadLoanDocument(document.artifact_id, 'json');
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `loan-document-${document.loan_id}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Document exported successfully');
      
    } catch (error) {
      console.error('Failed to export document:', error);
      toast.error('Failed to export document.');
    }
  };

  // Bulk actions
  const handleBulkExport = async () => {
    if (selectedDocuments.size === 0) {
      toast.error('Please select documents to export.');
      return;
    }

    try {
      setBulkActionLoading(true);
      
      // In a real implementation, you'd create a ZIP file with all documents
      toast.success(`Exporting ${selectedDocuments.size} documents...`);
      
      // Simulate bulk export
      setTimeout(() => {
        toast.success('Bulk export completed');
        setSelectedDocuments(new Set());
        setBulkActionLoading(false);
      }, 2000);
      
    } catch (error) {
      console.error('Failed to bulk export:', error);
      toast.error('Failed to bulk export documents.');
      setBulkActionLoading(false);
    }
  };

  // Export to CSV
  const handleExportCSV = () => {
    const csvContent = [
      ['Loan ID', 'Borrower Name', 'Loan Amount', 'Upload Date', 'Seal Status', 'Transaction ID'],
      ...documents.map(doc => [
        doc.loan_id,
        doc.borrower_name,
        doc.loan_amount.toString(),
        doc.upload_date,
        doc.sealed_status,
        doc.walacor_tx_id || 'N/A'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `loan-documents-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    toast.success('CSV exported successfully');
  };

  // Pagination helpers
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const canGoPrevious = pagination.page > 1;
  const canGoNext = pagination.page < totalPages;

  const goToPage = (page: number) => {
    setPagination(prev => ({ ...prev, page }));
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Loan Documents Admin</h1>
        <p className="text-gray-600">Manage and monitor sealed loan documents</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold">{stats.totalDocuments}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Today</p>
                <p className="text-2xl font-bold">{stats.documentsToday}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold">{stats.pendingSeals}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-2xl font-bold">{stats.failedSeals}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Error Rate</p>
                <p className="text-2xl font-bold">{stats.errorRate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Actions */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Documents</CardTitle>
              <CardDescription>
                Showing {documents.length} of {pagination.total} documents
                {lastRefresh && (
                  <span className="ml-2 text-xs text-gray-500">
                    Last updated: {lastRefresh.toLocaleTimeString()}
                  </span>
                )}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
              >
                <Activity className="h-4 w-4 mr-2" />
                {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
              </Button>
              <Button variant="outline" size="sm" onClick={loadDocuments}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-4">
            <div className="lg:col-span-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search by loan ID, borrower name..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="dateFrom">Date From</Label>
              <Input
                id="dateFrom"
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
              />
            </div>

            <div>
              <Label htmlFor="dateTo">Date To</Label>
              <Input
                id="dateTo"
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
              />
            </div>

            <div>
              <Label htmlFor="amountMin">Min Amount</Label>
              <Input
                id="amountMin"
                type="number"
                placeholder="0"
                value={filters.amountMin}
                onChange={(e) => setFilters(prev => ({ ...prev, amountMin: e.target.value }))}
              />
            </div>

            <div>
              <Label htmlFor="sealStatus">Status</Label>
              <Select
                value={filters.sealStatus}
                onValueChange={(value) => setFilters(prev => ({ ...prev, sealStatus: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All statuses</SelectItem>
                  <SelectItem value="sealed">Sealed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {selectedDocuments.size > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">
                    {selectedDocuments.size} selected
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleBulkExport}
                    disabled={bulkActionLoading}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export Selected
                  </Button>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={handleExportCSV}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={selectedDocuments.size === documents.length && documents.length > 0}
                    onCheckedChange={handleSelectAllChange}
                  />
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => handleSort('loan_id')}
                >
                  <div className="flex items-center gap-2">
                    Loan ID
                    {sortField === 'loan_id' && (
                      <span className="text-xs">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => handleSort('borrower_name')}
                >
                  <div className="flex items-center gap-2">
                    Borrower Name
                    {sortField === 'borrower_name' && (
                      <span className="text-xs">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => handleSort('loan_amount')}
                >
                  <div className="flex items-center gap-2">
                    Loan Amount
                    {sortField === 'loan_amount' && (
                      <span className="text-xs">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => handleSort('upload_date')}
                >
                  <div className="flex items-center gap-2">
                    Upload Date
                    {sortField === 'upload_date' && (
                      <span className="text-xs">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </TableHead>
                <TableHead>Seal Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(() => {
                if (loading) {
                  return (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">
                        <div className="flex items-center justify-center gap-2">
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          Loading documents...
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                }
                
                if (documents.length === 0) {
                  return (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        No documents found
                      </TableCell>
                    </TableRow>
                  );
                }
                
                return documents.map((document) => (
                  <TableRow key={document.artifact_id}>
                    <TableCell>
                      <Checkbox
                        checked={selectedDocuments.has(document.artifact_id)}
                        onCheckedChange={(checked) => handleSelectDocumentChange(document.artifact_id, checked)}
                      />
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {document.loan_id}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{document.borrower_name}</div>
                        <div className="text-sm text-gray-500">{document.borrower_email}</div>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">
                      {formatLoanAmount(document.loan_amount)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {formatDate(document.upload_date)}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={getStatusBadgeColor(document.sealed_status)}
                      >
                        {document.sealed_status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewDetails(document)}
                          disabled={loadingDetails}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewAuditTrail(document)}
                          disabled={loadingAudit}
                        >
                          <Activity className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleVerifyDocument(document)}
                          disabled={loadingVerification}
                        >
                          <Shield className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleExportDocument(document)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ));
              })()}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-600">
            Showing {((pagination.page - 1) * pagination.limit) + 1} to{' '}
            {Math.min(pagination.page * pagination.limit, pagination.total)} of{' '}
            {pagination.total} results
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(1)}
              disabled={!canGoPrevious}
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(pagination.page - 1)}
              disabled={!canGoPrevious}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm">
              Page {pagination.page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(pagination.page + 1)}
              disabled={!canGoNext}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => goToPage(totalPages)}
              disabled={!canGoNext}
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Document Details Modal */}
      <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Document Details</DialogTitle>
            <DialogDescription>
              Complete information for loan document {selectedDocument?.loan_id}
            </DialogDescription>
          </DialogHeader>
          
          {loadingDetails ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin mr-2" />
              Loading document details...
            </div>
          ) : (
            <Tabs defaultValue="loan" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="loan">Loan Information</TabsTrigger>
                <TabsTrigger value="borrower">Borrower Information</TabsTrigger>
              </TabsList>
              
              <TabsContent value="loan" className="space-y-4">
                {selectedDocument && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Loan ID</Label>
                      <p className="font-mono text-sm bg-gray-50 p-2 rounded">
                        {selectedDocument.loan_id}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Document Type</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {selectedDocument.document_type}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Loan Amount</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded font-medium">
                        {formatLoanAmount(selectedDocument.loan_amount)}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Upload Date</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {formatDate(selectedDocument.upload_date)}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Seal Status</Label>
                      <Badge 
                        variant="outline" 
                        className={getStatusBadgeColor(selectedDocument.sealed_status)}
                      >
                        {selectedDocument.sealed_status}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <Label>Transaction ID</Label>
                      <p className="font-mono text-sm bg-gray-50 p-2 rounded">
                        {selectedDocument.walacor_tx_id || 'N/A'}
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="borrower" className="space-y-4">
                {borrowerInfo ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Full Name</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.full_name}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Date of Birth</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.date_of_birth}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Email</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.email}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Phone</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.phone}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Address</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.address_line1}
                        {borrowerInfo.address_line2 && `, ${borrowerInfo.address_line2}`}
                        <br />
                        {borrowerInfo.city}, {borrowerInfo.state} {borrowerInfo.zip_code}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Employment Status</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.employment_status}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Annual Income Range</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.annual_income_range}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Co-borrower</Label>
                      <p className="text-sm bg-gray-50 p-2 rounded">
                        {borrowerInfo.co_borrower_name || 'N/A'}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No borrower information available
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailsModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Audit Trail Modal */}
      <Dialog open={showAuditModal} onOpenChange={setShowAuditModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Audit Trail</DialogTitle>
            <DialogDescription>
              Complete audit history for loan document {selectedDocument?.loan_id}
            </DialogDescription>
          </DialogHeader>
          
          {loadingAudit ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin mr-2" />
              Loading audit trail...
            </div>
          ) : (
            <div className="space-y-4">
              {auditTrail.map((event, index) => (
                <div key={event.event_id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
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
                        <p className="text-sm text-gray-600 mb-2">
                          {formatDate(event.timestamp)}
                        </p>
                        {event.details && (
                          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(event.details, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAuditModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
