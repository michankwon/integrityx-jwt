'use client'

import React, { useState, useEffect } from 'react'

interface RiskPrediction {
  document_id: string
  risk_score: number
  risk_level: string
  confidence: number
  factors: string[]
  recommendations: string[]
  predicted_at: string
}

interface ComplianceForecast {
  document_id: string
  compliance_probability: number
  forecast_status: string
  confidence: number
  risk_factors: string[]
  recommendations: string[]
  forecasted_at: string
}

interface PerformancePrediction {
  metric_name: string
  current_value: number
  predicted_value: number
  trend: string
  confidence: number
  recommendations: string[]
  predicted_at: string
}

interface TrendAnalysis {
  metric_name: string
  trend: string
  change_percentage: number
  confidence: number
  recommendations: string[]
  data_points: number
  analyzed_at: string
}

interface ModelStatistics {
  models_available: string[]
  scalers_available: string[]
  model_path: string
  models_loaded: Record<string, {
    type: string
    fitted: boolean
  }>
  last_updated: string
}

const PredictiveAnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('risk-prediction')
  const [loading, setLoading] = useState(false)
  const [modelStats, setModelStats] = useState<ModelStatistics | null>(null)
  const [riskPrediction, setRiskPrediction] = useState<RiskPrediction | null>(null)
  const [complianceForecast, setComplianceForecast] = useState<ComplianceForecast | null>(null)
  const [performancePrediction, setPerformancePrediction] = useState<PerformancePrediction | null>(null)
  const [trendAnalysis, setTrendAnalysis] = useState<TrendAnalysis | null>(null)

  const API_BASE = 'http://localhost:8000/api'

  useEffect(() => {
    loadModelStatistics()
  }, [])

  const loadModelStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/predictive-analytics/model-statistics`)
      const data = await response.json()
      if (data.ok) {
        setModelStats(data.data.model_statistics)
      }
    } catch (error) {
      console.error('Failed to load model statistics:', error)
    }
  }

  const testRiskPrediction = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/predictive-analytics/risk-prediction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: 'demo_doc_001',
          document_data: {
            file_size: 1500000,
            content_length: 8000,
            created_at: new Date().toISOString(),
            payload_sha256: 'demo_hash_123',
            attestations: [],
            provenance_links: [],
            events: []
          }
        })
      })
      const data = await response.json()
      if (data.ok) {
        setRiskPrediction(data.data.risk_prediction)
      }
    } catch (error) {
      console.error('Failed to predict risk:', error)
    } finally {
      setLoading(false)
    }
  }

  const testComplianceForecast = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/predictive-analytics/compliance-forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: 'compliance_demo_002',
          document_data: {
            file_size: 800000,
            content_length: 4000,
            created_at: new Date().toISOString(),
            payload_sha256: 'compliance_hash_456',
            attestations: [
              { status: 'verified', type: 'integrity' },
              { status: 'verified', type: 'compliance' }
            ],
            provenance_links: [
              { relationship_type: 'derived_from' }
            ],
            events: [
              { event_type: 'verification' },
              { event_type: 'attestation' },
              { event_type: 'compliance_check' }
            ]
          }
        })
      })
      const data = await response.json()
      if (data.ok) {
        setComplianceForecast(data.data.compliance_forecast)
      }
    } catch (error) {
      console.error('Failed to forecast compliance:', error)
    } finally {
      setLoading(false)
    }
  }

  const testPerformancePrediction = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/predictive-analytics/performance-prediction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric_name: 'api_response_time',
          historical_data: [120, 115, 125, 110, 118, 130, 105, 112, 108, 115]
        })
      })
      const data = await response.json()
      if (data.ok) {
        setPerformancePrediction(data.data.performance_prediction)
      }
    } catch (error) {
      console.error('Failed to predict performance:', error)
    } finally {
      setLoading(false)
    }
  }

  const testTrendAnalysis = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/predictive-analytics/trend-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric_name: 'document_processing_rate',
          time_series_data: [
            { timestamp: '2025-10-01T00:00:00Z', value: 100 },
            { timestamp: '2025-10-02T00:00:00Z', value: 105 },
            { timestamp: '2025-10-03T00:00:00Z', value: 110 },
            { timestamp: '2025-10-04T00:00:00Z', value: 115 },
            { timestamp: '2025-10-05T00:00:00Z', value: 120 },
            { timestamp: '2025-10-06T00:00:00Z', value: 125 },
            { timestamp: '2025-10-07T00:00:00Z', value: 130 }
          ]
        })
      })
      const data = await response.json()
      if (data.ok) {
        setTrendAnalysis(data.data.trend_analysis)
      }
    } catch (error) {
      console.error('Failed to analyze trends:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-green-600 bg-green-100'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100'
      case 'HIGH': return 'text-orange-600 bg-orange-100'
      case 'CRITICAL': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getComplianceStatusColor = (status: string) => {
    switch (status) {
      case 'PASS': return 'text-green-600 bg-green-100'
      case 'REVIEW_REQUIRED': return 'text-yellow-600 bg-yellow-100'
      case 'FAIL': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'INCREASING': return 'text-green-600'
      case 'DECREASING': return 'text-red-600'
      case 'STABLE': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🔮 Predictive Analytics & ML Dashboard
        </h1>
        <p className="text-gray-600">
          Advanced machine learning models for risk prediction, compliance forecasting, and performance optimization.
        </p>
      </div>

      {/* Model Statistics */}
      {modelStats && (
        <div className="card mb-6">
          <h2 className="card-title">🤖 ML Model Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800">Available Models</h3>
              <p className="text-2xl font-bold text-blue-600">{modelStats.models_available.length}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800">Scalers</h3>
              <p className="text-2xl font-bold text-green-600">{modelStats.scalers_available.length}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800">Model Path</h3>
              <p className="text-sm text-purple-600">{modelStats.model_path}</p>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <h3 className="font-semibold text-orange-800">Last Updated</h3>
              <p className="text-sm text-orange-600">
                {new Date(modelStats.last_updated).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'risk-prediction', label: 'Risk Prediction', icon: '⚠️' },
          { id: 'compliance-forecast', label: 'Compliance Forecast', icon: '📋' },
          { id: 'performance-prediction', label: 'Performance Prediction', icon: '📊' },
          { id: 'trend-analysis', label: 'Trend Analysis', icon: '📈' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Risk Prediction Tab */}
        {activeTab === 'risk-prediction' && (
          <div className="card">
            <h2 className="card-title">⚠️ Document Risk Prediction</h2>
            <p className="text-gray-600 mb-4">
              Predict potential risks in documents using machine learning models.
            </p>
            <button
              onClick={testRiskPrediction}
              disabled={loading}
              className="button mb-4"
            >
              {loading ? 'Analyzing...' : 'Test Risk Prediction'}
            </button>
            
            {riskPrediction && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Risk Level</h3>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(riskPrediction.risk_level)}`}>
                      {riskPrediction.risk_level}
                    </span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Risk Score</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {(riskPrediction.risk_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Confidence</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {(riskPrediction.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">Risk Factors</h3>
                    <ul className="space-y-1">
                      {riskPrediction.factors.map((factor, index) => (
                        <li key={index} className="text-sm text-gray-600">• {factor}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">Recommendations</h3>
                    <ul className="space-y-1">
                      {riskPrediction.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-600">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Compliance Forecast Tab */}
        {activeTab === 'compliance-forecast' && (
          <div className="card">
            <h2 className="card-title">📋 Compliance Forecast</h2>
            <p className="text-gray-600 mb-4">
              Predict whether documents will pass compliance checks.
            </p>
            <button
              onClick={testComplianceForecast}
              disabled={loading}
              className="button mb-4"
            >
              {loading ? 'Forecasting...' : 'Test Compliance Forecast'}
            </button>
            
            {complianceForecast && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Forecast Status</h3>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getComplianceStatusColor(complianceForecast.forecast_status)}`}>
                      {complianceForecast.forecast_status}
                    </span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Compliance Probability</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {(complianceForecast.compliance_probability * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Confidence</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {(complianceForecast.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">Risk Factors</h3>
                    <ul className="space-y-1">
                      {complianceForecast.risk_factors.map((factor, index) => (
                        <li key={index} className="text-sm text-gray-600">• {factor}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">Recommendations</h3>
                    <ul className="space-y-1">
                      {complianceForecast.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-600">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Performance Prediction Tab */}
        {activeTab === 'performance-prediction' && (
          <div className="card">
            <h2 className="card-title">📊 Performance Prediction</h2>
            <p className="text-gray-600 mb-4">
              Predict future performance trends and optimization opportunities.
            </p>
            <button
              onClick={testPerformancePrediction}
              disabled={loading}
              className="button mb-4"
            >
              {loading ? 'Predicting...' : 'Test Performance Prediction'}
            </button>
            
            {performancePrediction && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Current Value</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {performancePrediction.current_value.toFixed(1)}ms
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Predicted Value</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {performancePrediction.predicted_value.toFixed(1)}ms
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Trend</h3>
                    <span className={`text-lg font-bold ${getTrendColor(performancePrediction.trend)}`}>
                      {performancePrediction.trend}
                    </span>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">Recommendations</h3>
                  <ul className="space-y-1">
                    {performancePrediction.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600">• {rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Trend Analysis Tab */}
        {activeTab === 'trend-analysis' && (
          <div className="card">
            <h2 className="card-title">📈 Trend Analysis</h2>
            <p className="text-gray-600 mb-4">
              Analyze time series data to identify trends and patterns.
            </p>
            <button
              onClick={testTrendAnalysis}
              disabled={loading}
              className="button mb-4"
            >
              {loading ? 'Analyzing...' : 'Test Trend Analysis'}
            </button>
            
            {trendAnalysis && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Trend</h3>
                    <span className={`text-lg font-bold ${getTrendColor(trendAnalysis.trend)}`}>
                      {trendAnalysis.trend}
                    </span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Change</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {trendAnalysis.change_percentage > 0 ? '+' : ''}{trendAnalysis.change_percentage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-800">Data Points</h3>
                    <p className="text-2xl font-bold text-gray-900">
                      {trendAnalysis.data_points}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">Recommendations</h3>
                  <ul className="space-y-1">
                    {trendAnalysis.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600">• {rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictiveAnalyticsDashboard

