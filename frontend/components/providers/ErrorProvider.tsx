"use client"

import * as React from "react"
import { ErrorDrawer, ErrorAlert, useErrorHandler } from "@/components/system/ErrorDrawer"

interface ErrorContextType {
  showError: (error: any) => void
  clearError: () => void
  showErrorDetails: () => void
  error: any
  isDrawerOpen: boolean
}

const ErrorContext = React.createContext<ErrorContextType | null>(null)

interface ErrorProviderProps {
  readonly children: React.ReactNode
}

export function ErrorProvider({ children }: ErrorProviderProps) {
  const errorHandler = useErrorHandler()

  const showError = React.useCallback((errorResponse: any) => {
    const errorDetails = {
      code: errorResponse.error?.code || errorResponse.code || 'UNKNOWN_ERROR',
      message: errorResponse.error?.message || errorResponse.message || 'An unknown error occurred',
      requestId: errorResponse.error?.requestId || errorResponse.requestId,
      timestamp: new Date().toISOString(),
      endpoint: errorResponse.endpoint,
      method: errorResponse.method,
      statusCode: errorResponse.statusCode,
      details: errorResponse.error?.details || errorResponse.details,
      stack: errorResponse.stack,
      userAgent: navigator.userAgent,
      userId: errorResponse.userId
    }
    
    errorHandler.handleError(errorDetails)
  }, [errorHandler])

  const contextValue = React.useMemo(() => ({
    showError,
    clearError: errorHandler.clearError,
    showErrorDetails: errorHandler.showErrorDetails,
    error: errorHandler.error,
    isDrawerOpen: errorHandler.isDrawerOpen
  }), [showError, errorHandler])

  return (
    <ErrorContext.Provider value={contextValue}>
      {children}
      
      {/* Global Error Alert */}
      {errorHandler.error && (
        <div className="fixed bottom-4 right-4 z-50 max-w-md">
          <ErrorAlert
            error={errorHandler.error}
            onShowDetails={errorHandler.showErrorDetails}
            compact={true}
          />
        </div>
      )}
      
      {/* Global Error Drawer */}
      {errorHandler.error && (
        <ErrorDrawer
          error={errorHandler.error}
          isOpen={errorHandler.isDrawerOpen}
          onOpenChange={errorHandler.setIsDrawerOpen}
          onRetry={errorHandler.clearError}
        />
      )}
    </ErrorContext.Provider>
  )
}

export function useError() {
  const context = React.useContext(ErrorContext)
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider')
  }
  return context
}

// Hook for handling API responses with automatic error handling
export function useApiResponse() {
  const { showError } = useError()

  const handleResponse = React.useCallback((response: any) => {
    if (!response.ok) {
      showError(response)
      return false
    }
    return true
  }, [showError])

  return { handleResponse }
}
