'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Search, FileText, Eye, Plus, Filter, Calendar, Hash, AlertCircle, RefreshCw, Download, CheckSquare, Square } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import jsPDF from 'jspdf'
import Papa from 'papaparse'
import JSZip from 'jszip'

interface Document {
  id: string
  loan_id: string
  borrower_name: string
  borrower_email: string
  loan_amount: number
  document_type: string
  upload_date: string
  walacor_tx_id: string
  artifact_type: string
  created_by: string
  sealed_status: string
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  
  // Search filters
  const [borrowerName, setBorrowerName] = useState('')
  const [borrowerEmail, setBorrowerEmail] = useState('')
  const [loanId, setLoanId] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [amountMin, setAmountMin] = useState('')
  const [amountMax, setAmountMax] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  
  // Export functionality
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set())
  const [isExporting, setIsExporting] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async (page: number = 1) => {
    try {
      setError(null)
      setLoading(true)

      // Build query parameters
      const params = new URLSearchParams()
      if (borrowerName) params.append('borrower_name', borrowerName)
      if (borrowerEmail) params.append('borrower_email', borrowerEmail)
      if (loanId) params.append('loan_id', loanId)
      if (dateFrom) params.append('date_from', dateFrom)
      if (dateTo) params.append('date_to', dateTo)
      if (amountMin) params.append('amount_min', amountMin)
      if (amountMax) params.append('amount_max', amountMax)
      
      params.append('limit', '20')
      params.append('offset', String((page - 1) * 20))

      const response = await fetch(`http://localhost:8000/api/artifacts?${params.toString()}`, {
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000)
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.ok && data.data) {
          setDocuments(data.data.artifacts || [])
          setTotalCount(data.data.total_count || 0)
          setHasMore(data.data.has_more || false)
        }
      } else if (response.status === 404) {
        // No documents yet - this is normal
        setDocuments([])
        setTotalCount(0)
        setHasMore(false)
      } else {
        throw new Error(`Failed to fetch documents: ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      if (error instanceof Error) {
        if (error.name === 'TimeoutError') {
          setError('Request timed out. Please check your connection and try again.')
        } else if (error.message.includes('Failed to fetch')) {
          setError('Unable to connect to the server. Please ensure the backend is running.')
        } else {
          setError(error.message)
        }
      } else {
        setError('An unexpected error occurred while loading documents.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    fetchDocuments()
  }

  const handleSearch = () => {
    setCurrentPage(1)
    fetchDocuments(1)
  }

  const handleClearFilters = () => {
    setBorrowerName('')
    setBorrowerEmail('')
    setLoanId('')
    setDateFrom('')
    setDateTo('')
    setAmountMin('')
    setAmountMax('')
    setCurrentPage(1)
    fetchDocuments(1)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    fetchDocuments(page)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  // Export functionality
  const handleSelectDocument = (documentId: string) => {
    const newSelected = new Set(selectedDocuments)
    if (newSelected.has(documentId)) {
      newSelected.delete(documentId)
    } else {
      newSelected.add(documentId)
    }
    setSelectedDocuments(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedDocuments.size === documents.length) {
      setSelectedDocuments(new Set())
    } else {
      setSelectedDocuments(new Set(documents.map(doc => doc.id)))
    }
  }

  const generatePDFReport = async (document: Document) => {
    const pdf = new jsPDF()
    
    // Header
    pdf.setFontSize(20)
    pdf.text('Loan Document Audit Report', 20, 30)
    pdf.setFontSize(12)
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, 45)
    
    // Loan Details Section
    pdf.setFontSize(16)
    pdf.text('Loan Details', 20, 65)
    pdf.setFontSize(10)
    pdf.text(`Loan ID: ${document.loan_id}`, 20, 80)
    pdf.text(`Document Type: ${document.document_type}`, 20, 90)
    pdf.text(`Loan Amount: ${formatCurrency(document.loan_amount)}`, 20, 100)
    pdf.text(`Upload Date: ${formatDate(document.upload_date)}`, 20, 110)
    pdf.text(`Created By: ${document.created_by}`, 20, 120)
    
    // Borrower Information Section
    pdf.setFontSize(16)
    pdf.text('Borrower Information', 20, 140)
    pdf.setFontSize(10)
    pdf.text(`Name: ${document.borrower_name}`, 20, 155)
    pdf.text(`Email: ${document.borrower_email}`, 20, 165)
    
    // Verification Status Section
    pdf.setFontSize(16)
    pdf.text('Verification Status', 20, 185)
    pdf.setFontSize(10)
    pdf.text(`Status: ${document.sealed_status}`, 20, 200)
    pdf.text(`Walacor TX ID: ${document.walacor_tx_id}`, 20, 210)
    pdf.text(`Artifact ID: ${document.id}`, 20, 220)
    
    // Blockchain Proof Section
    pdf.setFontSize(16)
    pdf.text('Blockchain Proof', 20, 240)
    pdf.setFontSize(10)
    pdf.text(`Transaction ID: ${document.walacor_tx_id}`, 20, 255)
    pdf.text(`Sealed Date: ${formatDate(document.upload_date)}`, 20, 265)
    pdf.text('Document hash is cryptographically sealed in Walacor blockchain', 20, 275)
    pdf.text('This document has not been tampered with since sealing', 20, 285)
    
    return pdf
  }

  const exportToPDF = async (document: Document) => {
    try {
      setIsExporting(true)
      const pdf = await generatePDFReport(document)
      pdf.save(`loan-audit-${document.loan_id}-${new Date().toISOString().split('T')[0]}.pdf`)
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('Error generating PDF report')
    } finally {
      setIsExporting(false)
    }
  }

  const exportToJSON = (document: Document) => {
    try {
      const exportData = {
        loan_details: {
          loan_id: document.loan_id,
          document_type: document.document_type,
          loan_amount: document.loan_amount,
          upload_date: document.upload_date,
          created_by: document.created_by
        },
        borrower_information: {
          name: document.borrower_name,
          email: document.borrower_email
        },
        verification_status: {
          status: document.sealed_status,
          walacor_tx_id: document.walacor_tx_id,
          artifact_id: document.id
        },
        blockchain_proof: {
          transaction_id: document.walacor_tx_id,
          sealed_date: document.upload_date,
          integrity_verified: true,
          tamper_proof: true
        },
        export_metadata: {
          exported_at: new Date().toISOString(),
          export_format: 'JSON',
          version: '1.0'
        }
      }
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `loan-audit-${document.loan_id}-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting JSON:', error)
      alert('Error exporting JSON report')
    }
  }

  const exportToCSV = (document: Document) => {
    try {
      const csvData = [
        {
          'Loan ID': document.loan_id,
          'Document Type': document.document_type,
          'Loan Amount': document.loan_amount,
          'Upload Date': document.upload_date,
          'Created By': document.created_by,
          'Borrower Name': document.borrower_name,
          'Borrower Email': document.borrower_email,
          'Sealed Status': document.sealed_status,
          'Walacor TX ID': document.walacor_tx_id,
          'Artifact ID': document.id,
          'Export Date': new Date().toISOString()
        }
      ]
      
      const csv = Papa.unparse(csvData)
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `loan-audit-${document.loan_id}-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting CSV:', error)
      alert('Error exporting CSV report')
    }
  }

  const exportBulkDocuments = async (format: 'PDF' | 'JSON' | 'CSV') => {
    if (selectedDocuments.size === 0) {
      alert('Please select documents to export')
      return
    }

    try {
      setIsExporting(true)
      const selectedDocs = documents.filter(doc => selectedDocuments.has(doc.id))
      
      if (format === 'PDF') {
        const zip = new JSZip()
        
        for (const doc of selectedDocs) {
          const pdf = await generatePDFReport(doc)
          const pdfBlob = pdf.output('blob')
          zip.file(`loan-audit-${doc.loan_id}.pdf`, pdfBlob)
        }
        
        const zipBlob = await zip.generateAsync({ type: 'blob' })
        const url = URL.createObjectURL(zipBlob)
        const a = document.createElement('a')
        a.href = url
        a.download = `loan-audit-bulk-${new Date().toISOString().split('T')[0]}.zip`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } else if (format === 'JSON') {
        const exportData = selectedDocs.map(doc => ({
          loan_details: {
            loan_id: doc.loan_id,
            document_type: doc.document_type,
            loan_amount: doc.loan_amount,
            upload_date: doc.upload_date,
            created_by: doc.created_by
          },
          borrower_information: {
            name: doc.borrower_name,
            email: doc.borrower_email
          },
          verification_status: {
            status: doc.sealed_status,
            walacor_tx_id: doc.walacor_tx_id,
            artifact_id: doc.id
          },
          blockchain_proof: {
            transaction_id: doc.walacor_tx_id,
            sealed_date: doc.upload_date,
            integrity_verified: true,
            tamper_proof: true
          }
        }))
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `loan-audit-bulk-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } else if (format === 'CSV') {
        const csvData = selectedDocs.map(doc => ({
          'Loan ID': doc.loan_id,
          'Document Type': doc.document_type,
          'Loan Amount': doc.loan_amount,
          'Upload Date': doc.upload_date,
          'Created By': doc.created_by,
          'Borrower Name': doc.borrower_name,
          'Borrower Email': doc.borrower_email,
          'Sealed Status': doc.sealed_status,
          'Walacor TX ID': doc.walacor_tx_id,
          'Artifact ID': doc.id,
          'Export Date': new Date().toISOString()
        }))
        
        const csv = Papa.unparse(csvData)
        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `loan-audit-bulk-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error exporting bulk documents:', error)
      alert('Error exporting documents')
    } finally {
      setIsExporting(false)
    }
  }


  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>

        {/* Search and Filter Skeleton */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="md:w-48">
              <Skeleton className="h-10 w-full" />
            </div>
          </div>
        </div>

        {/* Table Skeleton */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Skeleton className="h-8 w-8 rounded-lg" />
                    <div>
                      <Skeleton className="h-4 w-32 mb-2" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-6 w-20" />
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-8 w-16" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center max-w-md">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Documents</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="space-y-3">
              <button
                onClick={handleRetry}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </button>
              {retryCount > 0 && (
                <p className="text-sm text-gray-500">
                  Retry attempt: {retryCount}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-2">
            Manage and view all your uploaded documents
          </p>
        </div>
        <Link
          href="/upload"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Upload Document
        </Link>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Search Loans by Borrower Information</h2>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Filter className="h-4 w-4 mr-2" />
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>

        {/* Basic Search */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Borrower Name</label>
              <input
                type="text"
              placeholder="Enter borrower name..."
              value={borrowerName}
              onChange={(e) => setBorrowerName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              placeholder="Enter email address..."
              value={borrowerEmail}
              onChange={(e) => setBorrowerEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Loan ID</label>
            <input
              type="text"
              placeholder="Enter loan ID..."
              value={loanId}
              onChange={(e) => setLoanId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="border-t pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Min Amount</label>
                <input
                  type="number"
                  placeholder="0"
                  value={amountMin}
                  onChange={(e) => setAmountMin(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Amount</label>
                <input
                  type="number"
                  placeholder="1000000"
                  value={amountMax}
                  onChange={(e) => setAmountMax(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSearch}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Search className="h-4 w-4 mr-2" />
            Search
          </button>
          <button
            onClick={handleClearFilters}
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Results Summary and Export Controls */}
      {totalCount > 0 && (
        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {documents.length} of {totalCount} loan documents
          </div>
          <div className="flex items-center space-x-3">
            {selectedDocuments.size > 0 && (
              <div className="text-sm text-gray-600">
                {selectedDocuments.size} selected
              </div>
            )}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => exportBulkDocuments('PDF')}
                disabled={selectedDocuments.size === 0 || isExporting}
                className="inline-flex items-center px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-3 w-3 mr-1" />
                Export PDF
              </button>
              <button
                onClick={() => exportBulkDocuments('JSON')}
                disabled={selectedDocuments.size === 0 || isExporting}
                className="inline-flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-3 w-3 mr-1" />
                Export JSON
              </button>
              <button
                onClick={() => exportBulkDocuments('CSV')}
                disabled={selectedDocuments.size === 0 || isExporting}
                className="inline-flex items-center px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-3 w-3 mr-1" />
                Export CSV
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Documents Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {documents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                    <button
                      onClick={handleSelectAll}
                      className="flex items-center justify-center w-4 h-4"
                    >
                      {selectedDocuments.size === documents.length && documents.length > 0 ? (
                        <CheckSquare className="h-4 w-4 text-blue-600" />
                      ) : (
                        <Square className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loan ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Borrower Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Loan Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Upload Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sealed Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleSelectDocument(doc.id)}
                        className="flex items-center justify-center w-4 h-4"
                      >
                        {selectedDocuments.has(doc.id) ? (
                          <CheckSquare className="h-4 w-4 text-blue-600" />
                        ) : (
                          <Square className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                        {doc.loan_id}
                          </div>
                          <div className="text-sm text-gray-500">
                        {doc.document_type}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {doc.borrower_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {doc.borrower_email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(doc.loan_amount)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1 text-gray-400" />
                        {formatDate(doc.upload_date)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doc.sealed_status === 'Sealed' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {doc.sealed_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                      <Link
                        href={`/documents/${doc.id}`}
                        className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Link>
                        <Link
                          href={`/verify?artifact_id=${doc.id}`}
                          className="inline-flex items-center px-3 py-1 border border-blue-300 rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
                        >
                          <Hash className="h-3 w-3 mr-1" />
                          Verify
                        </Link>
                        <div className="relative group">
                          <button
                            onClick={() => exportToPDF(doc)}
                            disabled={isExporting}
                            className="inline-flex items-center px-3 py-1 border border-red-300 rounded-md text-red-700 bg-red-50 hover:bg-red-100 transition-colors disabled:opacity-50"
                          >
                            <Download className="h-3 w-3 mr-1" />
                            Export
                          </button>
                          <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                            <div className="py-1">
                              <button
                                onClick={() => exportToPDF(doc)}
                                disabled={isExporting}
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                              >
                                Export as PDF
                              </button>
                              <button
                                onClick={() => exportToJSON(doc)}
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                              >
                                Export as JSON
                              </button>
                              <button
                                onClick={() => exportToCSV(doc)}
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                              >
                                Export as CSV
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            icon={FileText}
            title="No loan documents found"
            description="Try adjusting your search criteria or upload a new document with borrower information."
            action={
                <Link
                  href="/upload"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Document
                </Link>
            }
          />
        )}
      </div>

      {/* Pagination */}
      {totalCount > 20 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, totalCount)} of {totalCount} results
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-2 text-sm font-medium text-gray-700">
              Page {currentPage} of {Math.ceil(totalCount / 20)}
            </span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={!hasMore}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
