'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Calendar, 
  Shield, 
  Download, 
  Link as LinkIcon, 
  Copy,
  CheckCircle,
  AlertCircle,
  Clock,
  User,
  RefreshCw
} from 'lucide-react'
import { toast } from '@/components/ui/toast'
import { Skeleton } from '@/components/ui/skeleton'

interface Document {
  id: string
  filename: string
  hash: string
  created_at: string
  artifact_type: string
  loan_id?: string
  walacor_tx_id?: string
  created_by?: string
  blockchain_seal?: string
  local_metadata?: any
}

interface Attestation {
  id: string
  artifact_id: string
  attestation_type: string
  attestation_data: any
  created_at: string
  created_by: string
}

interface AuditEvent {
  id: string
  artifact_id: string
  event_type: string
  created_at: string
  created_by: string
  payload_json?: string
}

export default function DocumentDetailPage() {
  const params = useParams()
  const documentId = params.id as string

  const [document, setDocument] = useState<Document | null>(null)
  const [attestations, setAttestations] = useState<Attestation[]>([])
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [copiedHash, setCopiedHash] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  // Utility functions for masking sensitive data
  const maskEmail = (email: string): string => {
    if (!email || !email.includes('@')) return email
    const [local, domain] = email.split('@')
    if (local.length <= 2) return email
    return `${local[0]}***@${domain}`
  }

  const maskPhone = (phone: string): string => {
    if (!phone) return phone
    const digits = phone.replace(/\D/g, '')
    if (digits.length < 4) return phone
    const last4 = digits.slice(-4)
    return `***-***-${last4}`
  }

  const maskSSN = (ssn: string): string => {
    if (!ssn) return ssn
    if (ssn.length < 4) return ssn
    const last4 = ssn.slice(-4)
    return `****-**-${last4}`
  }

  const getIncomeRange = (income: number): string => {
    if (income < 25000) return 'Under $25,000'
    if (income < 50000) return '$25,000 - $49,999'
    if (income < 75000) return '$50,000 - $74,999'
    if (income < 100000) return '$75,000 - $99,999'
    if (income < 150000) return '$100,000 - $149,999'
    if (income < 200000) return '$150,000 - $199,999'
    return '$200,000+'
  }


  useEffect(() => {
    if (documentId) {
      fetchDocumentDetails()
    }
  }, [documentId])

  const fetchDocumentDetails = async () => {
    try {
      setError(null)
      setLoading(true)

      // Fetch document details
      const docResponse = await fetch(`http://localhost:8000/api/artifacts/${documentId}`, {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      
      if (docResponse.ok) {
        const docData = await docResponse.json()
        if (docData.ok && docData.data) {
          setDocument(docData.data)
        }
      } else if (docResponse.status === 404) {
        setError('Document not found')
        return
      } else {
        throw new Error(`Failed to fetch document: ${docResponse.status}`)
      }

      // Fetch attestations
      const attResponse = await fetch(`http://localhost:8000/api/attestations?artifactId=${documentId}`, {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      if (attResponse.ok) {
        const attData = await attResponse.json()
        if (attData.ok && attData.data) {
          setAttestations(attData.data.attestations || [])
        }
      }

      // Fetch borrower info (masked)
      const borrowerResponse = await fetch(`http://localhost:8000/api/loan-documents/${documentId}/borrower`, {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      if (borrowerResponse.ok) {
        const borrowerData = await borrowerResponse.json()
        if (borrowerData.ok && borrowerData.data) {
          setBorrower(borrowerData.data)
        }
      }

      // Fetch audit events
      const auditResponse = await fetch(`http://localhost:8000/api/loan-documents/${documentId}/audit-trail`, {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      if (auditResponse.ok) {
        const auditData = await auditResponse.json()
        if (auditData.ok && auditData.data) {
          setAuditEvents(auditData.data.events || [])
        }
      }
    } catch (error) {
      console.error('Failed to fetch document details:', error)
      if (error instanceof Error) {
        if (error.name === 'TimeoutError') {
          setError('Request timed out. Please check your connection and try again.')
        } else if (error.message.includes('Failed to fetch')) {
          setError('Unable to connect to the server. Please ensure the backend is running.')
        } else {
          setError(error.message)
        }
      } else {
        setError('An unexpected error occurred while loading document details.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    fetchDocumentDetails()
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      if (type === 'hash') {
        setCopiedHash(true)
        setTimeout(() => setCopiedHash(false), 2000)
      }
      toast.success(`${type} copied to clipboard`)
    } catch (error) {
      toast.error('Failed to copy to clipboard')
    }
  }

  const handleCreateAttestation = async () => {
    setActionLoading('attestation')
    try {
      const response = await fetch('http://localhost:8000/api/attestations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          artifactId: documentId,
          etid: '100001',
          kind: 'compliance',
          issuedBy: 'user@example.com',
          details: {
            verified: true,
            compliance_standard: 'ISO 27001',
            verified_by: 'system',
            notes: 'Document integrity verified'
          }
        })
      })

      if (response.ok) {
        toast.success('Attestation created successfully')
        fetchDocumentDetails() // Refresh data
      } else {
        toast.error('Failed to create attestation')
      }
    } catch (error) {
      toast.error('Failed to create attestation')
    } finally {
      setActionLoading(null)
    }
  }

  const handleGenerateDisclosurePack = async () => {
    setActionLoading('disclosure')
    try {
      const response = await fetch(`http://localhost:8000/api/disclosure-pack?artifact_id=${documentId}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `disclosure-pack-${documentId}.zip`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('Disclosure pack downloaded')
      } else {
        toast.error('Failed to generate disclosure pack')
      }
    } catch (error) {
      toast.error('Failed to generate disclosure pack')
    } finally {
      setActionLoading(null)
    }
  }

  const handleGenerateVerificationLink = async () => {
    setActionLoading('verification')
    try {
      const response = await fetch('http://localhost:8000/api/verification/generate-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documentId: documentId,
          documentHash: document?.hash,
          allowedParty: 'verifier@example.com',
          permissions: ['hash', 'timestamp', 'attestations'],
          expiresInHours: 24
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.ok && data.data) {
          const link = data.data.verification_link.verificationUrl
          await copyToClipboard(link, 'verification link')
        }
      } else {
        toast.error('Failed to generate verification link')
      }
    } catch (error) {
      toast.error('Failed to generate verification link')
    } finally {
      setActionLoading(null)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Header Skeleton */}
        <div className="flex items-center space-x-4 mb-8">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div>
            <Skeleton className="h-8 w-64 mb-2" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Skeleton */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <div>
                  <Skeleton className="h-4 w-16 mb-2" />
                  <Skeleton className="h-6 w-20" />
                </div>
                <div>
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <div>
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-20 mb-4" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-24 mb-4" />
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                    <Skeleton className="h-16 w-full" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar Skeleton */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-20 mb-4" />
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-4 w-12" />
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-24 mb-4" />
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-start space-x-3">
                    <Skeleton className="h-6 w-6 rounded-full" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-24 mb-1" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                  </div>
                ))}
              </div>
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
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Document</h2>
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
              <Link
                href="/documents"
                className="block text-blue-600 hover:text-blue-700 text-sm"
              >
                ← Back to Documents
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Not Found</h2>
          <p className="text-gray-600 mb-6">The document you're looking for doesn't exist or has been removed.</p>
          <Link
            href="/documents"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Link
            href="/documents"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {document.filename || `Document ${document.id}`}
            </h1>
            <p className="text-gray-600 mt-1">Document ID: {document.id}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Document Information */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Loan ID</label>
                <div className="p-2 bg-gray-50 rounded border text-sm">
                  {document.loan_id || 'Not provided'}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
                <div className="p-2 bg-gray-50 rounded border text-sm">
                  {document.local_metadata?.comprehensive_document?.document_type || document.artifact_type || 'Unknown'}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Loan Amount</label>
                <div className="p-2 bg-gray-50 rounded border text-sm">
                  {document.local_metadata?.comprehensive_document?.loan_amount 
                    ? `$${document.local_metadata.comprehensive_document.loan_amount.toLocaleString()}`
                    : 'Not provided'
                  }
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Upload Date</label>
                <div className="flex items-center text-sm text-gray-900">
                  <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                  {new Date(document.created_at).toLocaleString()}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Hash</label>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 p-2 bg-gray-50 rounded border font-mono text-sm">
                    {document.payload_sha256}
                  </div>
                  <button
                    onClick={() => copyToClipboard(document.payload_sha256, 'hash')}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                  >
                    {copiedHash ? <CheckCircle className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Created By</label>
                <div className="flex items-center text-sm text-gray-900">
                  <User className="h-4 w-4 mr-2 text-gray-400" />
                  {document.created_by || 'System'}
                </div>
              </div>
            </div>
          </div>

          {/* Borrower Information (From Sealed Record) */}
          {borrower && (
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Borrower Information (From Sealed Record)</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.full_name}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.date_of_birth}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.email}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.phone}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.address?.city && borrower.address?.state 
                      ? `${borrower.address.city}, ${borrower.address.state}`
                      : 'Not provided'
                    }
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">SSN</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.ssn_last4 ? `****-**-${borrower.ssn_last4}` : 'Not provided'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Employment Status</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.employment_status || 'Not provided'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Annual Income Range</label>
                  <div className="p-2 bg-gray-50 rounded border text-sm">
                    {borrower.annual_income_range || 'Not provided'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Verification Status */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification Status</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-900">Document hash matches blockchain record</span>
              </div>
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-900">Data has not been tampered with</span>
              </div>
              <div className="flex items-center space-x-3">
                <Clock className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-gray-900">
                  Sealed on: {new Date(document.created_at).toLocaleString()}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <Shield className="h-5 w-5 text-purple-600" />
                <span className="text-sm text-gray-900">
                  Walacor TX ID: {document.walacor_tx_id}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={handleCreateAttestation}
                disabled={actionLoading === 'attestation'}
                className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <Shield className="h-5 w-5 mr-2 text-green-600" />
                <span>Create Attestation</span>
              </button>
              <button
                onClick={handleGenerateDisclosurePack}
                disabled={actionLoading === 'disclosure'}
                className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <Download className="h-5 w-5 mr-2 text-blue-600" />
                <span>Generate Disclosure Pack</span>
              </button>
              <button
                onClick={handleGenerateVerificationLink}
                disabled={actionLoading === 'verification'}
                className="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <LinkIcon className="h-5 w-5 mr-2 text-purple-600" />
                <span>Generate Verification Link</span>
              </button>
            </div>
          </div>

          {/* Attestations */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Attestations</h2>
            {attestations.length > 0 ? (
              <div className="space-y-4">
                {attestations.map((att) => (
                  <div key={att.id} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{att.attestation_type}</span>
                      <span className="text-sm text-gray-500">
                        {new Date(att.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      <pre className="whitespace-pre-wrap">{JSON.stringify(att.attestation_data, null, 2)}</pre>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No attestations yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Info */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Info</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status</span>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Verified
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Attestations</span>
                <span className="text-sm font-medium text-gray-900">{attestations.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Audit Events</span>
                <span className="text-sm font-medium text-gray-900">{auditEvents.length}</span>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            {auditEvents.length > 0 ? (
              <div className="space-y-3">
                {auditEvents.slice(0, 5).map((event) => (
                  <div key={event.id} className="flex items-start space-x-3">
                    <div className="p-1 bg-blue-100 rounded-full">
                      <Clock className="h-3 w-3 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{event.event_type}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(event.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4">
                <Clock className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
