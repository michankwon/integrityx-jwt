'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Brain, TrendingUp, Shield, AlertTriangle, BarChart3 } from 'lucide-react'
import PredictiveAnalyticsDashboard from '@/components/PredictiveAnalyticsDashboard'

export default function PredictiveAnalyticsPage() {
  const [modelStats, setModelStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModelStatistics()
  }, [])

  const fetchModelStatistics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/predictive-analytics/model-statistics')
      if (response.ok) {
        const data = await response.json()
        if (data.ok && data.data) {
          setModelStats(data.data.model_statistics)
        }
      }
    } catch (error) {
      console.error('Failed to fetch model statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-8">
        <Link
          href="/analytics"
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Predictive Analytics</h1>
          <p className="text-gray-600 mt-1">
            AI-powered risk prediction, compliance forecasting, and performance optimization
          </p>
        </div>
      </div>

      {/* Model Statistics */}
      {modelStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Available Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {modelStats.models_available?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Shield className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Scalers</p>
                <p className="text-2xl font-bold text-gray-900">
                  {modelStats.scalers_available?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Model Path</p>
                <p className="text-sm font-medium text-gray-900 truncate">
                  {modelStats.model_path || 'models'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Last Updated</p>
                <p className="text-sm font-medium text-gray-900">
                  {modelStats.last_updated ? new Date(modelStats.last_updated).toLocaleDateString() : 'Unknown'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Available Models */}
      {modelStats?.models_available && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Available ML Models</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {modelStats.models_available.map((model: string) => (
              <div key={model} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="p-1 bg-green-100 rounded-full">
                    <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                  </div>
                  <span className="font-medium text-gray-900 capitalize">
                    {model.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Predictive Analytics Dashboard */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">ML Model Interface</h2>
          <p className="text-gray-600 mt-1">
            Test and interact with machine learning models for risk prediction and compliance forecasting
          </p>
        </div>
        <div className="p-6">
          <PredictiveAnalyticsDashboard />
        </div>
      </div>

      {/* Features Overview */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Risk Prediction</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Predict potential risks in documents using machine learning models trained on historical data.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Shield className="h-5 w-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Compliance Forecast</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Forecast compliance status and identify potential violations before they occur.
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Performance Prediction</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Predict future performance trends and optimize system resources accordingly.
          </p>
        </div>
      </div>
    </div>
  )
}
