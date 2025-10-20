"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Sheet, 
  SheetContent, 
  SheetDescription, 
  SheetHeader, 
  SheetTitle
} from "@/components/ui/sheet"
import { 
  AlertCircle, 
  Copy, 
  ExternalLink, 
  RefreshCw, 
  Bug, 
  Clock, 
  User,
  Code,
  MessageSquare,
  FileText
} from "lucide-react"
import { cn } from "@/lib/utils"
import toast from "react-hot-toast"

interface ErrorDetails {
  code: string
  message: string
  requestId?: string
  timestamp?: string
  endpoint?: string
  method?: string
  statusCode?: number
  details?: Record<string, any>
  stack?: string
  userAgent?: string
  userId?: string
}

interface ErrorDrawerProps {
  readonly error: ErrorDetails
  readonly isOpen: boolean
  readonly onOpenChange: (open: boolean) => void
  readonly onRetry?: () => void
  readonly className?: string
}

interface ErrorAlertProps {
  readonly error: ErrorDetails
  readonly onShowDetails: () => void
  readonly onRetry?: () => void
  readonly compact?: boolean
  readonly className?: string
}

export function ErrorDrawer({ 
  error, 
  isOpen, 
  onOpenChange, 
  onRetry,
  className 
}: ErrorDrawerProps) {
  const copyToClipboard = React.useCallback(async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast.success(`${label} copied to clipboard`)
    } catch {
      toast.error('Failed to copy to clipboard')
    }
  }, [])

  const formatTimestamp = React.useCallback((timestamp?: string) => {
    if (!timestamp) return 'Unknown'
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }, [])

  const getErrorSeverity = React.useCallback((code: string) => {
    if (code.includes('NETWORK') || code.includes('TIMEOUT')) return 'warning'
    if (code.includes('AUTH') || code.includes('PERMISSION')) return 'error'
    if (code.includes('VALIDATION') || code.includes('FORMAT')) return 'info'
    return 'error'
  }, [])

  const getErrorIcon = React.useCallback((code: string) => {
    if (code.includes('NETWORK') || code.includes('TIMEOUT')) return RefreshCw
    if (code.includes('AUTH') || code.includes('PERMISSION')) return User
    if (code.includes('VALIDATION') || code.includes('FORMAT')) return FileText
    return Bug
  }, [])

  const Icon = getErrorIcon(error.code)

  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className={cn("w-[400px] sm:w-[540px]", className)}>
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-destructive" />
            Error Details
          </SheetTitle>
          <SheetDescription>
            Detailed information about the error that occurred
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)] pr-4">
          <div className="space-y-6 mt-6">
            {/* Error Summary */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  Error Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Error Code:</span>
                  <Badge variant="destructive" className="font-mono">
                    {error.code}
                  </Badge>
                </div>
                
                <div>
                  <span className="text-sm font-medium">Message:</span>
                  <p className="text-sm text-muted-foreground mt-1">
                    {error.message}
                  </p>
                </div>

                {error.requestId && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Request ID:</span>
                    <div className="flex items-center gap-2">
                      <code className="text-xs bg-muted px-2 py-1 rounded">
                        {error.requestId}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(error.requestId!, 'Request ID')}
                        className="h-6 w-6 p-0"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Request Information */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Request Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {error.endpoint && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Endpoint:</span>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {error.method} {error.endpoint}
                    </code>
                  </div>
                )}

                {error.statusCode && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Status Code:</span>
                    <Badge 
                      variant={error.statusCode >= 500 ? "destructive" : "secondary"}
                      className="font-mono"
                    >
                      {error.statusCode}
                    </Badge>
                  </div>
                )}

                {error.timestamp && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Timestamp:</span>
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        {formatTimestamp(error.timestamp)}
                      </span>
                    </div>
                  </div>
                )}

                {error.userId && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">User ID:</span>
                    <div className="flex items-center gap-2">
                      <User className="h-3 w-3 text-muted-foreground" />
                      <code className="text-xs bg-muted px-2 py-1 rounded">
                        {error.userId}
                      </code>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Additional Details */}
            {error.details && Object.keys(error.details).length > 0 && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    Additional Details
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Object.entries(error.details).map(([key, value]) => (
                      <div key={key} className="flex items-start justify-between">
                        <span className="text-sm font-medium capitalize">
                          {key.replace(/([A-Z])/g, ' $1').trim()}:
                        </span>
                        <div className="text-right max-w-[200px]">
                          <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                            {typeof value === 'object' 
                              ? JSON.stringify(value, null, 2)
                              : String(value)
                            }
                          </code>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Stack Trace */}
            {error.stack && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Bug className="h-5 w-5" />
                    Stack Trace
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32 w-full">
                    <pre className="text-xs bg-muted p-3 rounded font-mono whitespace-pre-wrap">
                      {error.stack}
                    </pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* User Agent */}
            {error.userAgent && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Browser Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <code className="text-xs bg-muted p-2 rounded block break-all">
                    {error.userAgent}
                  </code>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              {onRetry && (
                <Button onClick={onRetry} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              )}
              <Button 
                variant="outline" 
                onClick={() => copyToClipboard(JSON.stringify(error, null, 2), 'Error details')}
                className="flex-1"
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy All
              </Button>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}

export function ErrorAlert({ 
  error, 
  onShowDetails, 
  onRetry,
  compact = false,
  className 
}: ErrorAlertProps) {
  const getErrorIcon = React.useCallback((code: string) => {
    if (code.includes('NETWORK') || code.includes('TIMEOUT')) return RefreshCw
    if (code.includes('AUTH') || code.includes('PERMISSION')) return User
    if (code.includes('VALIDATION') || code.includes('FORMAT')) return FileText
    return AlertCircle
  }, [])

  const Icon = getErrorIcon(error.code)

  if (compact) {
    return (
      <Alert className={cn("border-destructive/50 bg-destructive/10", className)}>
        <Icon className="h-4 w-4 text-destructive" />
        <AlertDescription className="flex items-center justify-between">
          <span className="text-destructive">
            {error.message}
          </span>
          <div className="flex items-center gap-2">
            {error.requestId && (
              <code className="text-xs bg-destructive/20 px-2 py-1 rounded">
                {error.requestId.slice(0, 8)}...
              </code>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onShowDetails}
              className="h-6 px-2 text-xs"
            >
              Details
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <Alert className={cn("border-destructive/50 bg-destructive/10", className)}>
      <Icon className="h-4 w-4 text-destructive" />
      <AlertDescription>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-medium text-destructive">
              {error.code}
            </span>
            {error.requestId && (
              <code className="text-xs bg-destructive/20 px-2 py-1 rounded">
                {error.requestId}
              </code>
            )}
          </div>
          <p className="text-destructive">
            {error.message}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onShowDetails}
              className="h-8"
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              View Details
            </Button>
            {onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="h-8"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            )}
          </div>
        </div>
      </AlertDescription>
    </Alert>
  )
}

// Hook for managing error state
export function useErrorHandler() {
  const [error, setError] = React.useState<ErrorDetails | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(false)

  const handleError = React.useCallback((errorResponse: any) => {
    const errorDetails: ErrorDetails = {
      code: errorResponse.error?.code || 'UNKNOWN_ERROR',
      message: errorResponse.error?.message || 'An unknown error occurred',
      requestId: errorResponse.error?.requestId || errorResponse.requestId,
      timestamp: new Date().toISOString(),
      endpoint: errorResponse.endpoint,
      method: errorResponse.method,
      statusCode: errorResponse.statusCode,
      details: errorResponse.error?.details,
      stack: errorResponse.stack,
      userAgent: navigator.userAgent,
      userId: errorResponse.userId
    }
    
    setError(errorDetails)
  }, [])

  const clearError = React.useCallback(() => {
    setError(null)
    setIsDrawerOpen(false)
  }, [])

  const showErrorDetails = React.useCallback(() => {
    setIsDrawerOpen(true)
  }, [])

  return {
    error,
    isDrawerOpen,
    setIsDrawerOpen,
    handleError,
    clearError,
    showErrorDetails
  }
}

// Higher-order component for error handling
export function withErrorHandler<P extends object>(
  Component: React.ComponentType<P>
) {
  return function ErrorHandledComponent(props: P) {
    const errorHandler = useErrorHandler()

    return (
      <>
        <Component {...props} />
        {errorHandler.error && (
          <>
            <ErrorAlert
              error={errorHandler.error}
              onShowDetails={errorHandler.showErrorDetails}
              compact={true}
              className="fixed bottom-4 right-4 z-50 max-w-md"
            />
            <ErrorDrawer
              error={errorHandler.error}
              isOpen={errorHandler.isDrawerOpen}
              onOpenChange={errorHandler.setIsDrawerOpen}
              onRetry={errorHandler.clearError}
            />
          </>
        )}
      </>
    )
  }
}
