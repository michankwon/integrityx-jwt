'use client'

import React, { useState, useEffect } from 'react'

interface SystemMetrics {
  timestamp: string
  overview: {
    total_documents: number
    total_attestations: number
    total_audit_events: number
    system_uptime: string
    last_updated: string
  }
  daily_stats: {
    documents_processed: number
    attestations_created: number
    verifications_completed: number
    disclosure_packs_generated: number
    date: string
  }
  weekly_stats: {
    documents_processed: number
    attestations_created: number
    verifications_completed: number
    disclosure_packs_generated: number
    week_start: string
    week_end: string
  }
  compliance_metrics: {
    compliance_score: number
    pending_reviews: number
    completed_reviews: number
    overdue_items: number
    regulatory_requirements_met: number
    total_requirements: number
  }
  performance_metrics: {
    average_processing_time: string
    throughput_per_hour: number
    error_rate: string
    system_availability: string
  }
  trends: {
    document_processing_trend: string
    attestation_volume_trend: string
    compliance_score_trend: string
    performance_trend: string
  }
}

interface AttestationAnalytics {
  timestamp: string
  attestation_types: Record<string, number>
  success_rates: Record<string, number>
  time_series: Array<{
    date: string
    attestations_created: number
    successful_attestations: number
    failed_attestations: number
  }>
  summary: {
    total_attestations: number
    average_success_rate: number
    most_common_type: string
  }
}

interface ComplianceDashboard {
  timestamp: string
  compliance_status: {
    overall_status: string
    last_audit_date: string
    next_audit_date: string
    compliance_score: number
    critical_issues: number
    warnings: number
  }
  regulatory_metrics: {
    regulations_covered: string[]
    compliance_by_regulation: Record<string, number>
    pending_requirements: number
    completed_requirements: number
  }
  audit_summary: {
    total_audit_events: number
    events_today: number
    events_this_week: number
    most_common_event_type: string
    last_audit_event: string
  }
  alerts: Array<{
    id: string
    type: string
    message: string
    severity: string
    created_at: string
  }>
}

interface PerformanceAnalytics {
  timestamp: string
  api_performance: {
    average_response_time: string
    requests_per_minute: number
    error_rate: string
    uptime: string
  }
  database_performance: {
    average_query_time: string
    connection_pool_usage: string
    cache_hit_rate: string
  }
  storage_metrics: {
    total_documents: number
    total_size: string
    average_document_size: string
  }
  system_resources: {
    cpu_usage: string
    memory_usage: string
    disk_usage: string
  }
}

export default function AnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'attestations' | 'compliance' | 'performance'>('overview')
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [attestationAnalytics, setAttestationAnalytics] = useState<AttestationAnalytics | null>(null)
  const [complianceDashboard, setComplianceDashboard] = useState<ComplianceDashboard | null>(null)
  const [performanceAnalytics, setPerformanceAnalytics] = useState<PerformanceAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalyticsData()
  }, [])

  const loadAnalyticsData = async () => {
    setLoading(true)
    setError(null)

    try {
      const [systemResponse, attestationResponse, complianceResponse, performanceResponse] = await Promise.all([
        fetch('http://localhost:8000/api/analytics/system-metrics'),
        fetch('http://localhost:8000/api/analytics/attestations'),
        fetch('http://localhost:8000/api/analytics/compliance'),
        fetch('http://localhost:8000/api/analytics/performance')
      ])

      const [systemData, attestationData, complianceData, performanceData] = await Promise.all([
        systemResponse.json(),
        attestationResponse.json(),
        complianceResponse.json(),
        performanceResponse.json()
      ])

      if (systemData.ok) setSystemMetrics(systemData.data.metrics)
      if (attestationData.ok) setAttestationAnalytics(attestationData.data.analytics)
      if (complianceData.ok) setComplianceDashboard(complianceData.data.dashboard)
      if (performanceData.ok) setPerformanceAnalytics(performanceData.data.analytics)

    } catch (err) {
      setError(`Failed to load analytics data: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return '📈'
      case 'decreasing': return '📉'
      case 'stable': return '➡️'
      case 'improving': return '📈'
      default: return '➡️'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant': return '#28a745'
      case 'warning': return '#ffc107'
      case 'critical': return '#dc3545'
      default: return '#6c757d'
    }
  }

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading">
          <h3>📊 Loading Analytics...</h3>
          <p>Please wait while we fetch your analytics data.</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="analytics-dashboard">
        <div className="error">
          <h3>❌ Error Loading Analytics</h3>
          <p>{error}</p>
          <button onClick={loadAnalyticsData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2>📊 Analytics Dashboard</h2>
        <button onClick={loadAnalyticsData} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`tab ${activeTab === 'attestations' ? 'active' : ''}`}
          onClick={() => setActiveTab('attestations')}
        >
          ✅ Attestations
        </button>
        <button 
          className={`tab ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => setActiveTab('compliance')}
        >
          🛡️ Compliance
        </button>
        <button 
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          ⚡ Performance
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && systemMetrics && (
          <div className="overview-tab">
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>📄 Documents</h3>
                <div className="metric-value">{systemMetrics.overview.total_documents.toLocaleString()}</div>
                <div className="metric-trend">
                  {getTrendIcon(systemMetrics.trends.document_processing_trend)} 
                  {systemMetrics.trends.document_processing_trend}
                </div>
              </div>

              <div className="metric-card">
                <h3>✅ Attestations</h3>
                <div className="metric-value">{systemMetrics.overview.total_attestations.toLocaleString()}</div>
                <div className="metric-trend">
                  {getTrendIcon(systemMetrics.trends.attestation_volume_trend)} 
                  {systemMetrics.trends.attestation_volume_trend}
                </div>
              </div>

              <div className="metric-card">
                <h3>📋 Audit Events</h3>
                <div className="metric-value">{systemMetrics.overview.total_audit_events.toLocaleString()}</div>
                <div className="metric-subtitle">Total tracked events</div>
              </div>

              <div className="metric-card">
                <h3>🛡️ Compliance Score</h3>
                <div className="metric-value">{systemMetrics.compliance_metrics.compliance_score}%</div>
                <div className="metric-trend">
                  {getTrendIcon(systemMetrics.trends.compliance_score_trend)} 
                  {systemMetrics.trends.compliance_score_trend}
                </div>
              </div>

              <div className="metric-card">
                <h3>⚡ System Uptime</h3>
                <div className="metric-value">{systemMetrics.overview.system_uptime}</div>
                <div className="metric-subtitle">Availability</div>
              </div>

              <div className="metric-card">
                <h3>🔄 Performance</h3>
                <div className="metric-value">{systemMetrics.performance_metrics.average_processing_time}</div>
                <div className="metric-trend">
                  {getTrendIcon(systemMetrics.trends.performance_trend)} 
                  {systemMetrics.trends.performance_trend}
                </div>
              </div>
            </div>

            <div className="stats-section">
              <div className="stats-card">
                <h3>📅 Today's Activity</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Documents Processed:</span>
                    <span className="stat-value">{systemMetrics.daily_stats.documents_processed}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Attestations Created:</span>
                    <span className="stat-value">{systemMetrics.daily_stats.attestations_created}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Verifications Completed:</span>
                    <span className="stat-value">{systemMetrics.daily_stats.verifications_completed}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Disclosure Packs Generated:</span>
                    <span className="stat-value">{systemMetrics.daily_stats.disclosure_packs_generated}</span>
                  </div>
                </div>
              </div>

              <div className="stats-card">
                <h3>📊 This Week's Summary</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Documents Processed:</span>
                    <span className="stat-value">{systemMetrics.weekly_stats.documents_processed}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Attestations Created:</span>
                    <span className="stat-value">{systemMetrics.weekly_stats.attestations_created}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Verifications Completed:</span>
                    <span className="stat-value">{systemMetrics.weekly_stats.verifications_completed}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Disclosure Packs Generated:</span>
                    <span className="stat-value">{systemMetrics.weekly_stats.disclosure_packs_generated}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'attestations' && attestationAnalytics && (
          <div className="attestations-tab">
            <div className="attestation-summary">
              <div className="summary-card">
                <h3>📊 Attestation Summary</h3>
                <div className="summary-stats">
                  <div className="summary-item">
                    <span className="summary-label">Total Attestations:</span>
                    <span className="summary-value">{attestationAnalytics.summary.total_attestations}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Average Success Rate:</span>
                    <span className="summary-value">{attestationAnalytics.summary.average_success_rate.toFixed(1)}%</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Most Common Type:</span>
                    <span className="summary-value">{attestationAnalytics.summary.most_common_type.replace('_', ' ')}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="attestation-types">
              <h3>📋 Attestation Types Distribution</h3>
              <div className="types-grid">
                {Object.entries(attestationAnalytics.attestation_types).map(([type, count]) => (
                  <div key={type} className="type-card">
                    <h4>{type.replace('_', ' ')}</h4>
                    <div className="type-count">{count}</div>
                    <div className="type-success-rate">
                      Success: {attestationAnalytics.success_rates[type]}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="time-series">
              <h3>📈 Attestation Trends (Last 7 Days)</h3>
              <div className="time-series-chart">
                {attestationAnalytics.time_series.map((day, index) => (
                  <div key={index} className="time-series-item">
                    <div className="date">{day.date}</div>
                    <div className="chart-bar">
                      <div 
                        className="bar successful" 
                        style={{ height: `${(day.successful_attestations / 25) * 100}%` }}
                        title={`Successful: ${day.successful_attestations}`}
                      ></div>
                      <div 
                        className="bar failed" 
                        style={{ height: `${(day.failed_attestations / 25) * 100}%` }}
                        title={`Failed: ${day.failed_attestations}`}
                      ></div>
                    </div>
                    <div className="total">{day.attestations_created}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'compliance' && complianceDashboard && (
          <div className="compliance-tab">
            <div className="compliance-status">
              <div className="status-card">
                <h3>🛡️ Compliance Status</h3>
                <div className="status-overview">
                  <div className="status-item">
                    <span className="status-label">Overall Status:</span>
                    <span 
                      className="status-value"
                      style={{ color: getStatusColor(complianceDashboard.compliance_status.overall_status) }}
                    >
                      {complianceDashboard.compliance_status.overall_status.toUpperCase()}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Compliance Score:</span>
                    <span className="status-value">{complianceDashboard.compliance_status.compliance_score}%</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Critical Issues:</span>
                    <span className="status-value">{complianceDashboard.compliance_status.critical_issues}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Warnings:</span>
                    <span className="status-value">{complianceDashboard.compliance_status.warnings}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="regulatory-metrics">
              <h3>📋 Regulatory Compliance</h3>
              <div className="regulations-grid">
                {Object.entries(complianceDashboard.regulatory_metrics.compliance_by_regulation).map(([regulation, score]) => (
                  <div key={regulation} className="regulation-card">
                    <h4>{regulation}</h4>
                    <div className="compliance-score">{score}%</div>
                    <div className="compliance-bar">
                      <div 
                        className="compliance-fill" 
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="audit-summary">
              <h3>📊 Audit Trail Summary</h3>
              <div className="audit-stats">
                <div className="audit-item">
                  <span className="audit-label">Total Events:</span>
                  <span className="audit-value">{complianceDashboard.audit_summary.total_audit_events.toLocaleString()}</span>
                </div>
                <div className="audit-item">
                  <span className="audit-label">Events Today:</span>
                  <span className="audit-value">{complianceDashboard.audit_summary.events_today}</span>
                </div>
                <div className="audit-item">
                  <span className="audit-label">Events This Week:</span>
                  <span className="audit-value">{complianceDashboard.audit_summary.events_this_week}</span>
                </div>
                <div className="audit-item">
                  <span className="audit-label">Most Common Event:</span>
                  <span className="audit-value">{complianceDashboard.audit_summary.most_common_event_type}</span>
                </div>
              </div>
            </div>

            {complianceDashboard.alerts.length > 0 && (
              <div className="compliance-alerts">
                <h3>🚨 Compliance Alerts</h3>
                <div className="alerts-list">
                  {complianceDashboard.alerts.map((alert) => (
                    <div key={alert.id} className={`alert alert-${alert.severity}`}>
                      <div className="alert-header">
                        <span className="alert-type">{alert.type.toUpperCase()}</span>
                        <span className="alert-severity">{alert.severity}</span>
                      </div>
                      <div className="alert-message">{alert.message}</div>
                      <div className="alert-time">{new Date(alert.created_at).toLocaleString()}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'performance' && performanceAnalytics && (
          <div className="performance-tab">
            <div className="performance-metrics">
              <div className="metric-section">
                <h3>🌐 API Performance</h3>
                <div className="performance-grid">
                  <div className="perf-item">
                    <span className="perf-label">Average Response Time:</span>
                    <span className="perf-value">{performanceAnalytics.api_performance.average_response_time}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Requests per Minute:</span>
                    <span className="perf-value">{performanceAnalytics.api_performance.requests_per_minute}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Error Rate:</span>
                    <span className="perf-value">{performanceAnalytics.api_performance.error_rate}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Uptime:</span>
                    <span className="perf-value">{performanceAnalytics.api_performance.uptime}</span>
                  </div>
                </div>
              </div>

              <div className="metric-section">
                <h3>🗄️ Database Performance</h3>
                <div className="performance-grid">
                  <div className="perf-item">
                    <span className="perf-label">Average Query Time:</span>
                    <span className="perf-value">{performanceAnalytics.database_performance.average_query_time}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Connection Pool Usage:</span>
                    <span className="perf-value">{performanceAnalytics.database_performance.connection_pool_usage}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Cache Hit Rate:</span>
                    <span className="perf-value">{performanceAnalytics.database_performance.cache_hit_rate}</span>
                  </div>
                </div>
              </div>

              <div className="metric-section">
                <h3>💾 Storage Metrics</h3>
                <div className="performance-grid">
                  <div className="perf-item">
                    <span className="perf-label">Total Documents:</span>
                    <span className="perf-value">{performanceAnalytics.storage_metrics.total_documents.toLocaleString()}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Total Size:</span>
                    <span className="perf-value">{performanceAnalytics.storage_metrics.total_size}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Average Document Size:</span>
                    <span className="perf-value">{performanceAnalytics.storage_metrics.average_document_size}</span>
                  </div>
                </div>
              </div>

              <div className="metric-section">
                <h3>🖥️ System Resources</h3>
                <div className="performance-grid">
                  <div className="perf-item">
                    <span className="perf-label">CPU Usage:</span>
                    <span className="perf-value">{performanceAnalytics.system_resources.cpu_usage}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Memory Usage:</span>
                    <span className="perf-value">{performanceAnalytics.system_resources.memory_usage}</span>
                  </div>
                  <div className="perf-item">
                    <span className="perf-label">Disk Usage:</span>
                    <span className="perf-value">{performanceAnalytics.system_resources.disk_usage}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .analytics-dashboard {
          background: #ffffff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          background: #f8f9fa;
          border-bottom: 1px solid #dee2e6;
        }

        .dashboard-header h2 {
          margin: 0;
          color: #495057;
        }

        .refresh-button {
          background: #007bff;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .refresh-button:hover {
          background: #0056b3;
        }

        .dashboard-tabs {
          display: flex;
          background: #e9ecef;
          border-bottom: 1px solid #dee2e6;
        }

        .tab {
          background: none;
          border: none;
          padding: 12px 20px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #6c757d;
          border-bottom: 3px solid transparent;
          transition: all 0.2s;
        }

        .tab:hover {
          background: #dee2e6;
          color: #495057;
        }

        .tab.active {
          background: #ffffff;
          color: #007bff;
          border-bottom-color: #007bff;
        }

        .dashboard-content {
          padding: 20px;
        }

        .loading, .error {
          text-align: center;
          padding: 40px;
        }

        .loading h3, .error h3 {
          color: #495057;
          margin-bottom: 10px;
        }

        .retry-button {
          background: #dc3545;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 15px;
        }

        .retry-button:hover {
          background: #c82333;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .metric-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
        }

        .metric-card h3 {
          margin: 0 0 10px 0;
          color: #495057;
          font-size: 14px;
        }

        .metric-value {
          font-size: 24px;
          font-weight: bold;
          color: #007bff;
          margin-bottom: 5px;
        }

        .metric-trend {
          font-size: 12px;
          color: #6c757d;
        }

        .metric-subtitle {
          font-size: 12px;
          color: #6c757d;
        }

        .stats-section {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .stats-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
        }

        .stats-card h3 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .stats-grid {
          display: grid;
          gap: 10px;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #e9ecef;
        }

        .stat-item:last-child {
          border-bottom: none;
        }

        .stat-label {
          color: #6c757d;
          font-size: 14px;
        }

        .stat-value {
          font-weight: bold;
          color: #495057;
        }

        .attestation-summary {
          margin-bottom: 30px;
        }

        .summary-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
        }

        .summary-card h3 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .summary-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .summary-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .summary-label {
          color: #6c757d;
          font-size: 14px;
        }

        .summary-value {
          font-weight: bold;
          color: #495057;
        }

        .attestation-types {
          margin-bottom: 30px;
        }

        .attestation-types h3 {
          color: #495057;
          margin-bottom: 15px;
        }

        .types-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .type-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 15px;
          text-align: center;
        }

        .type-card h4 {
          margin: 0 0 10px 0;
          color: #495057;
          text-transform: capitalize;
        }

        .type-count {
          font-size: 20px;
          font-weight: bold;
          color: #007bff;
          margin-bottom: 5px;
        }

        .type-success-rate {
          font-size: 12px;
          color: #28a745;
        }

        .time-series {
          margin-bottom: 30px;
        }

        .time-series h3 {
          color: #495057;
          margin-bottom: 15px;
        }

        .time-series-chart {
          display: flex;
          align-items: end;
          gap: 10px;
          height: 200px;
          padding: 20px;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
        }

        .time-series-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex: 1;
        }

        .date {
          font-size: 12px;
          color: #6c757d;
          margin-bottom: 10px;
        }

        .chart-bar {
          display: flex;
          align-items: end;
          height: 120px;
          gap: 2px;
        }

        .bar {
          width: 20px;
          border-radius: 2px 2px 0 0;
        }

        .bar.successful {
          background: #28a745;
        }

        .bar.failed {
          background: #dc3545;
        }

        .total {
          font-size: 12px;
          font-weight: bold;
          color: #495057;
          margin-top: 5px;
        }

        .compliance-status {
          margin-bottom: 30px;
        }

        .status-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
        }

        .status-card h3 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .status-overview {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .status-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .status-label {
          color: #6c757d;
          font-size: 14px;
        }

        .status-value {
          font-weight: bold;
          font-size: 16px;
        }

        .regulatory-metrics {
          margin-bottom: 30px;
        }

        .regulatory-metrics h3 {
          color: #495057;
          margin-bottom: 15px;
        }

        .regulations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .regulation-card {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 15px;
          text-align: center;
        }

        .regulation-card h4 {
          margin: 0 0 10px 0;
          color: #495057;
        }

        .compliance-score {
          font-size: 20px;
          font-weight: bold;
          color: #007bff;
          margin-bottom: 10px;
        }

        .compliance-bar {
          height: 8px;
          background: #e9ecef;
          border-radius: 4px;
          overflow: hidden;
        }

        .compliance-fill {
          height: 100%;
          background: #28a745;
          transition: width 0.3s ease;
        }

        .audit-summary {
          margin-bottom: 30px;
        }

        .audit-summary h3 {
          color: #495057;
          margin-bottom: 15px;
        }

        .audit-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .audit-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
        }

        .audit-label {
          color: #6c757d;
          font-size: 14px;
        }

        .audit-value {
          font-weight: bold;
          color: #495057;
        }

        .compliance-alerts {
          margin-bottom: 30px;
        }

        .compliance-alerts h3 {
          color: #495057;
          margin-bottom: 15px;
        }

        .alerts-list {
          display: grid;
          gap: 10px;
        }

        .alert {
          border: 1px solid;
          border-radius: 4px;
          padding: 15px;
        }

        .alert-warning {
          background: #fff3cd;
          border-color: #ffeaa7;
        }

        .alert-info {
          background: #d1ecf1;
          border-color: #bee5eb;
        }

        .alert-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 5px;
        }

        .alert-type {
          font-weight: bold;
          font-size: 12px;
        }

        .alert-severity {
          font-size: 12px;
          padding: 2px 6px;
          border-radius: 3px;
          background: #6c757d;
          color: white;
        }

        .alert-message {
          color: #495057;
          margin-bottom: 5px;
        }

        .alert-time {
          font-size: 12px;
          color: #6c757d;
        }

        .performance-metrics {
          display: grid;
          gap: 30px;
        }

        .metric-section {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
        }

        .metric-section h3 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .performance-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
        }

        .perf-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #ffffff;
          border: 1px solid #e9ecef;
          border-radius: 4px;
        }

        .perf-label {
          color: #6c757d;
          font-size: 14px;
        }

        .perf-value {
          font-weight: bold;
          color: #495057;
        }
      `}</style>
    </div>
  )
}
