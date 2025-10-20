'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { BarChart3, TrendingUp, Shield, FileText, Users, ArrowRight, AlertCircle, RefreshCw } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

interface AnalyticsData {
  financial_documents: {
    documents_sealed_today: number
    documents_sealed_this_month: number
    total_documents_sealed: number
    total_loan_value_sealed: number
    average_loan_amount: number
    sealing_success_rate: number
    blockchain_confirmation_rate: number
  }
  compliance_risk: {
    documents_compliant: number
    documents_pending_review: number
    overall_compliance_rate: number
    high_risk_documents: number
    medium_risk_documents: number
    low_risk_documents: number
    audit_trail_completeness: number
  }
  business_intelligence: {
    monthly_revenue: number
    revenue_per_document: number
    profit_margin: number
    customer_retention_rate: number
    customer_satisfaction_score: number
    growth_rate: string
  }
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      setError(null)
      setLoading(true)

      const [financialResponse, complianceResponse, businessResponse] = await Promise.all([
        fetch('http://localhost:8000/api/analytics/financial-documents', {
          headers: { 'Accept': 'application/json' },
          signal: AbortSignal.timeout(10000)
        }),
        fetch('http://localhost:8000/api/analytics/compliance-risk', {
          headers: { 'Accept': 'application/json' },
          signal: AbortSignal.timeout(10000)
        }),
        fetch('http://localhost:8000/api/analytics/business-intelligence', {
          headers: { 'Accept': 'application/json' },
          signal: AbortSignal.timeout(10000)
        })
      ])

      const [financialData, complianceData, businessData] = await Promise.all([
        financialResponse.json(),
        complianceResponse.json(),
        businessResponse.json()
      ])

      setAnalytics({
        financial_documents: {
          documents_sealed_today: financialData.data?.analytics?.document_processing?.documents_sealed_today || 0,
          documents_sealed_this_month: financialData.data?.analytics?.document_processing?.documents_sealed_this_month || 0,
          total_documents_sealed: financialData.data?.analytics?.document_processing?.total_documents_sealed || 0,
          total_loan_value_sealed: financialData.data?.analytics?.financial_metrics?.total_loan_value_sealed || 0,
          average_loan_amount: financialData.data?.analytics?.financial_metrics?.average_loan_amount || 0,
          sealing_success_rate: financialData.data?.analytics?.document_processing?.sealing_success_rate || 0,
          blockchain_confirmation_rate: financialData.data?.analytics?.blockchain_activity?.blockchain_confirmation_rate || 0
        },
        compliance_risk: {
          documents_compliant: complianceData.data?.analytics?.compliance_status?.documents_compliant || 0,
          documents_pending_review: complianceData.data?.analytics?.compliance_status?.documents_pending_review || 0,
          overall_compliance_rate: complianceData.data?.analytics?.compliance_status?.overall_compliance_rate || 0,
          high_risk_documents: complianceData.data?.analytics?.risk_assessment?.high_risk_documents || 0,
          medium_risk_documents: complianceData.data?.analytics?.risk_assessment?.medium_risk_documents || 0,
          low_risk_documents: complianceData.data?.analytics?.risk_assessment?.low_risk_documents || 0,
          audit_trail_completeness: complianceData.data?.analytics?.compliance_status?.audit_trail_completeness || 0
        },
        business_intelligence: {
          monthly_revenue: businessData.data?.analytics?.revenue_metrics?.monthly_revenue || 0,
          revenue_per_document: businessData.data?.analytics?.revenue_metrics?.revenue_per_document || 0,
          profit_margin: businessData.data?.analytics?.revenue_metrics?.profit_margin || 0,
          customer_retention_rate: businessData.data?.analytics?.customer_analytics?.customer_retention_rate || 0,
          customer_satisfaction_score: businessData.data?.analytics?.customer_analytics?.customer_satisfaction_score || 0,
          growth_rate: businessData.data?.analytics?.market_insights?.growth_rate || "0%"
        }
      })
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
      if (error instanceof Error) {
        if (error.name === 'TimeoutError') {
          setError('Request timed out. Please check your connection and try again.')
        } else if (error.message.includes('Failed to fetch')) {
          setError('Unable to connect to the server. Please ensure the backend is running.')
        } else {
          setError(error.message)
        }
      } else {
        setError('An unexpected error occurred while loading analytics.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
    fetchAnalytics()
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'documents', name: 'Document Processing', icon: FileText },
    { id: 'compliance', name: 'Compliance & Risk', icon: Shield },
    { id: 'business', name: 'Business Intelligence', icon: TrendingUp }
  ]

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        {/* Header Skeleton */}
        <div className="mb-8">
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-96" />
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

        {/* Tabs and Content Skeleton */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="border-b border-gray-200 p-6">
            <div className="flex space-x-8">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-6 w-20" />
              ))}
            </div>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-4">
                <Skeleton className="h-6 w-32" />
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Skeleton className="h-5 w-5" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                    <Skeleton className="h-6 w-8" />
                  </div>
                ))}
              </div>
              <div className="space-y-4">
                <Skeleton className="h-6 w-32" />
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Skeleton className="h-5 w-5" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                    <Skeleton className="h-6 w-8" />
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
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Analytics</h2>
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Document Analytics</h1>
        <p className="text-gray-600">
          Monitor document processing, compliance, and business performance metrics
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Documents Sealed Today</p>
              <p className="text-2xl font-bold text-gray-900">{analytics?.financial_documents.documents_sealed_today || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Compliance Rate</p>
              <p className="text-2xl font-bold text-gray-900">{analytics?.compliance_risk.overall_compliance_rate || 0}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Loan Value</p>
              <p className="text-2xl font-bold text-gray-900">${(analytics?.financial_documents.total_loan_value_sealed || 0).toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">${analytics?.business_intelligence.monthly_revenue || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Processing</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">Documents Sealed Today</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      {analytics?.financial_documents.documents_sealed_today || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Shield className="h-5 w-5 text-green-600" />
                      <span className="font-medium">Sealing Success Rate</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      {analytics?.financial_documents.sealing_success_rate || 0}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <TrendingUp className="h-5 w-5 text-purple-600" />
                      <span className="font-medium">Blockchain Confirmation</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      {analytics?.financial_documents.blockchain_confirmation_rate || 0}%
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Metrics</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">Total Loan Value</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      ${(analytics?.financial_documents.total_loan_value_sealed || 0).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Shield className="h-5 w-5 text-green-600" />
                      <span className="font-medium">Average Loan Amount</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      ${(analytics?.financial_documents.average_loan_amount || 0).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Users className="h-5 w-5 text-purple-600" />
                      <span className="font-medium">Total Documents Sealed</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">
                      {analytics?.financial_documents.total_documents_sealed || 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Document Processing</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Documents Sealed This Month</span>
                    <span className="text-sm font-medium">{analytics?.financial_documents.documents_sealed_this_month || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Sealing Success Rate</span>
                    <span className="text-sm font-medium">{analytics?.financial_documents.sealing_success_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Average Processing Time</span>
                    <span className="text-sm font-medium">2.3 minutes</span>
                  </div>
                </div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Blockchain Activity</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Blockchain Confirmation Rate</span>
                    <span className="text-sm font-medium">{analytics?.financial_documents.blockchain_confirmation_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Average Seal Time</span>
                    <span className="text-sm font-medium">45 seconds</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Documents Sealed</span>
                    <span className="text-sm font-medium">{analytics?.financial_documents.total_documents_sealed || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'compliance' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Compliance Status</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Overall Compliance Rate</span>
                    <span className="text-sm font-medium">{analytics?.compliance_risk.overall_compliance_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Documents Compliant</span>
                    <span className="text-sm font-medium">{analytics?.compliance_risk.documents_compliant || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Pending Review</span>
                    <span className="text-sm font-medium">{analytics?.compliance_risk.documents_pending_review || 0}</span>
                  </div>
                </div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Risk Assessment</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">High Risk Documents</span>
                    <span className="text-sm font-medium text-red-600">{analytics?.compliance_risk.high_risk_documents || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Medium Risk Documents</span>
                    <span className="text-sm font-medium text-yellow-600">{analytics?.compliance_risk.medium_risk_documents || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Low Risk Documents</span>
                    <span className="text-sm font-medium text-green-600">{analytics?.compliance_risk.low_risk_documents || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'business' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Revenue Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Monthly Revenue</span>
                    <span className="text-sm font-medium">${analytics?.business_intelligence.monthly_revenue || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Revenue Per Document</span>
                    <span className="text-sm font-medium">${analytics?.business_intelligence.revenue_per_document || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Profit Margin</span>
                    <span className="text-sm font-medium">{analytics?.business_intelligence.profit_margin || 0}%</span>
                  </div>
                </div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Customer Analytics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Retention Rate</span>
                    <span className="text-sm font-medium">{analytics?.business_intelligence.customer_retention_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Satisfaction Score</span>
                    <span className="text-sm font-medium">{analytics?.business_intelligence.customer_satisfaction_score || 0}/5.0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Growth Rate</span>
                    <span className="text-sm font-medium">{analytics?.business_intelligence.growth_rate || "0%"}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Business Intelligence Tools */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Business Intelligence Tools</h3>
            <p className="text-gray-600 mt-1">
              Advanced risk assessment, compliance forecasting, and loan performance analytics
            </p>
          </div>
          <Link
            href="/analytics/predictive"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <span>View BI Tools</span>
            <ArrowRight className="h-4 w-4 ml-2" />
          </Link>
        </div>
      </div>
    </div>
  )
}
