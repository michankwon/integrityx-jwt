"use client"

import * as React from "react"
import { ErrorDrawer, useErrorHandler } from "./ErrorDrawer"

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

interface ErrorBoundaryProps {
  readonly children: React.ReactNode
  readonly fallback?: React.ComponentType<{ error: Error; resetError: () => void }>
  readonly onError?: (error: Error, errorInfo: React.ErrorInfo) => void
  readonly showErrorDrawer?: boolean
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo
    })

    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return <FallbackComponent error={this.state.error} resetError={this.resetError} />
      }

      return (
        <DefaultErrorFallback 
          error={this.state.error} 
          errorInfo={this.state.errorInfo}
          resetError={this.resetError}
          showErrorDrawer={this.props.showErrorDrawer}
        />
      )
    }

    return this.props.children
  }
}

interface DefaultErrorFallbackProps {
  error: Error
  errorInfo: React.ErrorInfo | null
  resetError: () => void
  showErrorDrawer?: boolean
}

function DefaultErrorFallback({ 
  error, 
  errorInfo, 
  resetError,
  showErrorDrawer = true 
}: DefaultErrorFallbackProps) {
  const errorHandler = useErrorHandler()

  React.useEffect(() => {
    if (showErrorDrawer) {
      const errorDetails = {
        code: 'REACT_ERROR',
        message: error.message,
        requestId: `error-${Date.now()}`,
        timestamp: new Date().toISOString(),
        details: {
          componentStack: errorInfo?.componentStack,
          stack: error.stack
        },
        stack: error.stack,
        userAgent: navigator.userAgent
      }
      
      errorHandler.handleError(errorDetails)
    }
  }, [error, errorInfo, errorHandler, showErrorDrawer])

  return (
    <div className="min-h-[200px] flex items-center justify-center p-6">
      <div className="text-center space-y-4 max-w-md">
        <div className="text-6xl">⚠️</div>
        <h2 className="text-xl font-semibold text-destructive">
          Something went wrong
        </h2>
        <p className="text-muted-foreground">
          An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
        </p>
        
        <div className="flex gap-2 justify-center">
          <button
            onClick={resetError}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 border border-input bg-background rounded-md hover:bg-accent transition-colors"
          >
            Refresh Page
          </button>
          {showErrorDrawer && (
            <button
              onClick={() => errorHandler.showErrorDetails()}
              className="px-4 py-2 border border-input bg-background rounded-md hover:bg-accent transition-colors"
            >
              Show Details
            </button>
          )}
        </div>

        {showErrorDrawer && errorHandler.error && (
          <ErrorDrawer
            error={errorHandler.error}
            isOpen={errorHandler.isDrawerOpen}
            onOpenChange={errorHandler.setIsDrawerOpen}
            onRetry={resetError}
          />
        )}
      </div>
    </div>
  )
}

// Hook for programmatic error handling
export function useErrorBoundary() {
  const [error, setError] = React.useState<Error | null>(null)

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  const captureError = React.useCallback((error: Error) => {
    setError(error)
  }, [])

  React.useEffect(() => {
    if (error) {
      throw error
    }
  }, [error])

  return {
    captureError,
    resetError
  }
}

// Higher-order component for error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  return function ErrorBoundaryWrappedComponent(props: P) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}
