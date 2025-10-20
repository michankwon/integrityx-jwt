'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { 
  Loader2, 
  Settings, 
  Database, 
  Globe, 
  HardDrive, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Clock,
  Activity,
  Upload,
  Wifi
} from 'lucide-react';
import toast from 'react-hot-toast';

interface ServiceHealth {
  status: string;
  duration_ms: number;
  details?: string;
  error?: string;
}

interface HealthResponse {
  status: string;
  message: string;
  timestamp: string;
  total_duration_ms: number;
  services: {
    [key: string]: ServiceHealth;
  };
}

interface EnvironmentConfig {
  [key: string]: string;
}

interface ApiResponse<T = any> {
  ok: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export default function SettingsPage() {
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [envConfig, setEnvConfig] = useState<EnvironmentConfig>({});
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [testingPresign, setTestingPresign] = useState(false);
  const [testingWalacor, setTestingWalacor] = useState(false);
  const [presignResult, setPresignResult] = useState<any>(null);
  const [walacorResult, setWalacorResult] = useState<any>(null);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/health');
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      const apiResponse: ApiResponse<HealthResponse> = await response.json();
      
      if (!apiResponse.ok || !apiResponse.data) {
        throw new Error(apiResponse.error?.message || 'Health check failed');
      }
      
      setHealthData(apiResponse.data);
      setLastChecked(new Date());
      
      // Show detailed success message
      const totalDuration = apiResponse.data.total_duration_ms;
      const healthyServices = Object.values(apiResponse.data.services).filter(s => s.status === 'up' || s.status === 'healthy').length;
      const totalServices = Object.keys(apiResponse.data.services).length;
      
      toast.success(
        `Health check completed in ${formatDuration(totalDuration)} - ${healthyServices}/${totalServices} services healthy`,
        { duration: 4000 }
      );
    } catch (error) {
      console.error('Health check error:', error);
      toast.error('Failed to fetch health status');
    } finally {
      setLoading(false);
    }
  };

  const fetchEnvironmentConfig = async () => {
    try {
      const response = await fetch('/api/config');
      if (response.ok) {
        const apiResponse: ApiResponse<EnvironmentConfig> = await response.json();
        
        if (apiResponse.ok && apiResponse.data) {
          setEnvConfig(apiResponse.data);
        }
      }
    } catch (error) {
      console.error('Config fetch error:', error);
      // Continue without config data
    }
  };

  const testPresign = async () => {
    setTestingPresign(true);
    setPresignResult(null);
    
    try {
      const response = await fetch('/api/storage/s3/presign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: 'test-document.pdf',
          contentType: 'application/pdf',
          size: 1024
        })
      });

      const apiResponse: ApiResponse<any> = await response.json();
      
      if (apiResponse.ok && apiResponse.data) {
        setPresignResult({
          success: true,
          data: apiResponse.data,
          timestamp: new Date().toISOString()
        });
        toast.success('S3 presign test successful!');
      } else {
        setPresignResult({
          success: false,
          error: apiResponse.error?.message || 'Presign test failed',
          timestamp: new Date().toISOString()
        });
        toast.error('S3 presign test failed');
      }
    } catch (error) {
      setPresignResult({
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date().toISOString()
      });
      toast.error('S3 presign test failed');
    } finally {
      setTestingPresign(false);
    }
  };

  const testWalacor = async () => {
    setTestingWalacor(true);
    setWalacorResult(null);
    
    try {
      const response = await fetch('/api/walacor/ping');
      const apiResponse: ApiResponse<any> = await response.json();
      
      if (apiResponse.ok && apiResponse.data) {
        setWalacorResult({
          success: true,
          data: apiResponse.data,
          timestamp: new Date().toISOString()
        });
        toast.success(`Walacor ping successful! (${apiResponse.data.latency_ms}ms)`);
      } else {
        setWalacorResult({
          success: false,
          error: apiResponse.error?.message || 'Walacor ping failed',
          timestamp: new Date().toISOString()
        });
        toast.error('Walacor ping failed');
      }
    } catch (error) {
      setWalacorResult({
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date().toISOString()
      });
      toast.error('Walacor ping failed');
    } finally {
      setTestingWalacor(false);
    }
  };

  useEffect(() => {
    fetchEnvironmentConfig();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'down':
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return <Badge className="bg-green-100 text-green-800">Healthy</Badge>;
      case 'down':
      case 'unhealthy':
        return <Badge className="bg-red-100 text-red-800">Unhealthy</Badge>;
      case 'degraded':
        return <Badge className="bg-yellow-100 text-yellow-800">Degraded</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) {
      return `${ms.toFixed(1)}ms`;
    }
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getAlertClassName = (status: string) => {
    if (status === 'healthy') {
      return 'border-green-200 bg-green-50';
    }
    if (status === 'degraded') {
      return 'border-yellow-200 bg-yellow-50';
    }
    return 'border-red-200 bg-red-50';
  };

  const isSecretKey = (key: string) => {
    const secretPatterns = [
      'password', 'secret', 'key', 'token', 'auth', 'credential',
      'private', 'api_key', 'access_key', 'secret_key'
    ];
    return secretPatterns.some(pattern => 
      key.toLowerCase().includes(pattern)
    );
  };

  const maskSecretValue = (value: string) => {
    if (value.length <= 8) {
      return '*'.repeat(value.length);
    }
    return value.substring(0, 4) + '*'.repeat(value.length - 8) + value.substring(value.length - 4);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">System Settings</h1>
        <p className="text-muted-foreground">
          Monitor system health and view configuration settings.
        </p>
      </div>

      <div className="grid gap-6">
        {/* Health Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Health
            </CardTitle>
            <CardDescription>
              Real-time status of all system services
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {healthData && getStatusIcon(healthData.status)}
                <span className="font-medium">Overall Status</span>
                {healthData && getStatusBadge(healthData.status)}
              </div>
              <div className="flex items-center gap-2">
                {lastChecked && (
                  <div className="text-sm text-muted-foreground">
                    Last checked: {lastChecked.toLocaleTimeString()}
                  </div>
                )}
                <Button 
                  onClick={fetchHealth} 
                  disabled={loading}
                  className="min-w-[140px]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Checking...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Run Health Check
                    </>
                  )}
                </Button>
              </div>
            </div>

            {loading && !healthData && (
              <div className="text-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Running health check...</p>
              </div>
            )}

            {!loading && !healthData && (
              <div className="text-center py-8">
                <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-2">No health data available</p>
                <p className="text-sm text-muted-foreground">
                  Click "Run Health Check" to get system status
                </p>
              </div>
            )}

            {healthData && (
              <>
                <Alert className={getAlertClassName(healthData.status)}>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {healthData.message}
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">Last Checked</div>
                      <div className="text-sm font-medium">
                        {lastChecked ? lastChecked.toLocaleString() : 'Never'}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">Total Response Time</div>
                      <div className="text-sm font-medium">
                        {formatDuration(healthData.total_duration_ms)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                    <Settings className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">Server Timestamp</div>
                      <div className="text-sm font-medium">
                        {formatTimestamp(healthData.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="space-y-3">
                  <h4 className="font-medium">Service Details</h4>
                  {Object.entries(healthData.services).map(([serviceName, service]) => (
                    <div key={serviceName} className="p-4 border rounded-lg bg-card">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          {getStatusIcon(service.status)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <div className="font-medium capitalize">{serviceName.replace('_', ' ')}</div>
                              {getStatusBadge(service.status)}
                            </div>
                            {service.details && (
                              <div className="text-sm text-muted-foreground mb-1">{service.details}</div>
                            )}
                            {service.error && (
                              <div className="text-sm text-red-600 mb-1">{service.error}</div>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-1 text-sm font-medium text-muted-foreground mb-1">
                            <Activity className="h-3 w-3" />
                            {formatDuration(service.duration_ms)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Response time
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Environment Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Environment Configuration
            </CardTitle>
            <CardDescription>
              Non-sensitive environment variables and configuration settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(envConfig).length === 0 ? (
              <div className="text-center py-8">
                <Settings className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No configuration data available</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Configuration endpoint may not be implemented
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Only non-sensitive configuration values are displayed. Secret keys and passwords are masked for security.
                  </AlertDescription>
                </Alert>

                <div className="grid gap-3">
                  {Object.entries(envConfig).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        {key.includes('database') && <Database className="h-4 w-4 text-muted-foreground" />}
                        {key.includes('walacor') && <Globe className="h-4 w-4 text-muted-foreground" />}
                        {key.includes('s3') && <HardDrive className="h-4 w-4 text-muted-foreground" />}
                        <span className="font-medium font-mono">{key}</span>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                          {isSecretKey(key) ? maskSecretValue(value) : value}
                        </span>
                        {isSecretKey(key) && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            Masked
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Information */}
        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>
              General system and application information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="font-medium">Application</span>
                <p className="text-sm text-muted-foreground">Walacor Financial Integrity Platform</p>
              </div>
              <div>
                <span className="font-medium">Version</span>
                <p className="text-sm text-muted-foreground">1.0.0</p>
              </div>
              <div>
                <span className="font-medium">Environment</span>
                <p className="text-sm text-muted-foreground">
                  {process.env.NODE_ENV || 'development'}
                </p>
              </div>
              <div>
                <span className="font-medium">Last Health Check</span>
                <p className="text-sm text-muted-foreground">
                  {lastChecked ? lastChecked.toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Service Tests */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Service Tests
            </CardTitle>
            <CardDescription>
              Test connectivity and functionality of external services
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* S3 Presign Test */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Upload className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">S3 Presign Test</span>
                </div>
                <Button 
                  onClick={testPresign} 
                  disabled={testingPresign}
                  variant="outline"
                  size="sm"
                >
                  {testingPresign ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Test Presign
                    </>
                  )}
                </Button>
              </div>
              
              {presignResult && (
                <Alert className={presignResult.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
                  {presignResult.success ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                  <AlertDescription>
                    <div className="space-y-2">
                      <div className="font-medium">
                        {presignResult.success ? 'S3 Presign Test Successful' : 'S3 Presign Test Failed'}
                      </div>
                      {presignResult.success ? (
                        <div className="text-sm space-y-1">
                          <div>✅ Presigned URL generated successfully</div>
                          <div className="text-xs text-muted-foreground">
                            Tested at: {new Date(presignResult.timestamp).toLocaleString()}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm">
                          <div className="text-red-600">❌ {presignResult.error}</div>
                          <div className="text-xs text-muted-foreground">
                            Failed at: {new Date(presignResult.timestamp).toLocaleString()}
                          </div>
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>

            <Separator />

            {/* Walacor Ping Test */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Wifi className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">Walacor Ping Test</span>
                </div>
                <Button 
                  onClick={testWalacor} 
                  disabled={testingWalacor}
                  variant="outline"
                  size="sm"
                >
                  {testingWalacor ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Pinging...
                    </>
                  ) : (
                    <>
                      <Wifi className="h-4 w-4 mr-2" />
                      Test Walacor
                    </>
                  )}
                </Button>
              </div>
              
              {walacorResult && (
                <Alert className={walacorResult.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
                  {walacorResult.success ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                  <AlertDescription>
                    <div className="space-y-2">
                      <div className="font-medium">
                        {walacorResult.success ? 'Walacor Ping Successful' : 'Walacor Ping Failed'}
                      </div>
                      {walacorResult.success ? (
                        <div className="text-sm space-y-1">
                          <div>✅ Walacor service is responding</div>
                          <div className="flex items-center gap-2">
                            <Activity className="h-3 w-3" />
                            <span>Latency: {walacorResult.data.latency_ms}ms</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Tested at: {new Date(walacorResult.timestamp).toLocaleString()}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm">
                          <div className="text-red-600">❌ {walacorResult.error}</div>
                          <div className="text-xs text-muted-foreground">
                            Failed at: {new Date(walacorResult.timestamp).toLocaleString()}
                          </div>
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

