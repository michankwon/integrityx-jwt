'use client'

import { useUser } from '@clerk/nextjs'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Upload, FileText, BarChart3, Plus, Eye, TrendingUp, Shield, Clock, AlertCircle, RefreshCw } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { EmptyState } from '@/components/ui/empty-state'

interface Document {
  id: string
  filename: string
  hash: string
  created_at: string
  artifact_type: string
}

interface Stats {
  total_documents: number
  total_attestations: number
  recent_activity: number
  compliance_score: number
}

export default function Dashboard() {
  const { user, isLoaded } = useUser()
  const [documents, setDocuments] = useState<Document[]>([])
  const [stats, setStats] = useState<Stats>({
    total_documents: 0,
    total_attestations: 0,
    recent_activity: 0,
    compliance_score: 94.5
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    if (isLoaded) {
      fetchDashboardData()
    }
  }, [isLoaded])

  const fetchDashboardData = async () => {
    try {
      setError(null)
      setLoading(true)

      // Fetch recent documents
      const docsResponse = await fetch('http://localhost:8000/api/artifacts?limit=5', {
        headers: {
          'Accept': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(10000)
      })
      
      if (docsResponse.ok) {
        const docsData = await docsResponse.json()
        if (docsData.ok && docsData.data) {
          setDocuments(docsData.data.artifacts || [])
        }
      } else if (docsResponse.status === 404) {
        // No documents yet - this is normal
        setDocuments([])
      } else {
        throw new Error(`Failed to fetch documents: ${docsResponse.status}`)
      }

      // Fetch stats (mock for now - would come from analytics API)
      setStats({
        total_documents: documents.length,
        total_attestations: 0,
        recent_activity: 12,
        compliance_score: 94.5
      })
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      if (error instanceof Error) {
        if (error.name === 'TimeoutError') {
          setError('Request timed out. Please check your connection and try again.')
        } else if (error.message.includes('Failed to fetch')) {
          setError('Unable to connect to the server. Please ensure the backend is running.')
        } else {
          setError(error.message)
        }
      } else {
        setError('An unexpected error occurred while loading dashboard data.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    fetchDashboardData()
  }

  if (!isLoaded) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-gray-600">Loading your dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Header Skeleton */}
        <div className="mb-8">
          <Skeleton className="h-8 w-1/3 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>

        {/* Stats Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <Skeleton className="h-10 w-10 rounded-lg mr-4" />
                <div className="flex-1">
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-6 w-12" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Content Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                    <Skeleton className="h-8 w-8 rounded-lg" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-2" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                    <Skeleton className="h-6 w-12" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div>
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <Skeleton className="h-6 w-24 mb-4" />
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center p-4 border border-gray-200 rounded-lg">
                    <Skeleton className="h-8 w-8 rounded-lg mr-3" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-24 mb-1" />
                      <Skeleton className="h-3 w-16" />
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
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h2>
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
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
        </h1>
        <p className="text-gray-600">
          Manage your document integrity and compliance from your dashboard.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Documents</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_documents}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Attestations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_attestations}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Activity</p>
              <p className="text-2xl font-bold text-gray-900">{stats.recent_activity}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Compliance Score</p>
              <p className="text-2xl font-bold text-gray-900">{stats.compliance_score}%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Documents */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
                <Link 
                  href="/documents"
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  View all
                </Link>
              </div>
            </div>
            <div className="p-6">
              {documents.length > 0 ? (
                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gray-100 rounded-lg">
                          <FileText className="h-4 w-4 text-gray-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{doc.filename || `Document ${doc.id}`}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(doc.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <Link
                        href={`/documents/${doc.id}`}
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        View
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={FileText}
                  title="No documents yet"
                  description="Upload your first document to get started with document integrity verification."
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
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
            </div>
            <div className="p-6 space-y-4">
              <Link
                href="/upload"
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Upload className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Upload Document</p>
                  <p className="text-sm text-gray-500">Seal a new document</p>
                </div>
              </Link>

              <Link
                href="/documents"
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Eye className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">View Documents</p>
                  <p className="text-sm text-gray-500">Manage your documents</p>
                </div>
              </Link>

              <Link
                href="/analytics"
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="p-2 bg-purple-100 rounded-lg mr-3">
                  <BarChart3 className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Analytics</p>
                  <p className="text-sm text-gray-500">View system metrics</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
