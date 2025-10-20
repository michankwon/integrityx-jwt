"use client"

import { useState, useCallback } from "react"
import { useErrorHandler } from "@/components/system/ErrorDrawer"

interface ApiResponse<T = any> {
  ok: boolean
  data?: T
  error?: {
    code: string
    message: string
    requestId?: string
    details?: Record<string, any>
  }
}

interface ApiErrorOptions {
  showAlert?: boolean
  showDrawer?: boolean
  onError?: (error: any) => void
  retryable?: boolean
}

export function useApiError(options: ApiErrorOptions = {}) {
  const {
    showAlert = true,
    showDrawer = false,
    onError,
    retryable = true
  } = options

  const errorHandler = useErrorHandler()
  const [isRetrying, setIsRetrying] = useState(false)

  const handleApiError = useCallback(async (
    response: Response | ApiResponse,
    context?: {
      endpoint?: string
      method?: string
      userId?: string
    }
  ) => {
    let errorData: any

    if (response instanceof Response) {
      // Handle fetch Response
      try {
        errorData = await response.json()
      } catch {
        errorData = {
          error: {
            code: 'PARSE_ERROR',
            message: 'Failed to parse error response',
            requestId: response.headers.get('x-request-id') || undefined
          }
        }
      }

      // Add response context
      errorData.statusCode = response.status
      errorData.endpoint = context?.endpoint
      errorData.method = context?.method
      errorData.userId = context?.userId
    } else {
      // Handle ApiResponse object
      errorData = response
      errorData.endpoint = context?.endpoint
      errorData.method = context?.method
      errorData.userId = context?.userId
    }

    // Check if response indicates an error
    if (!errorData.ok || errorData.error) {
      errorHandler.handleError(errorData)

      if (showAlert) {
        // Show compact alert
        errorHandler.showErrorDetails()
      }

      if (onError) {
        onError(errorData)
      }
    }
  }, [errorHandler, showAlert, onError])

  const handleRetry = useCallback(async (retryFn: () => Promise<any>) => {
    if (!retryable || isRetrying) return

    setIsRetrying(true)
    try {
      await retryFn()
      errorHandler.clearError()
    } catch {
      // Error will be handled by the retry function
    } finally {
      setIsRetrying(false)
    }
  }, [retryable, isRetrying, errorHandler])

  return {
    error: errorHandler.error,
    isDrawerOpen: errorHandler.isDrawerOpen,
    setIsDrawerOpen: errorHandler.setIsDrawerOpen,
    handleApiError,
    handleRetry,
    clearError: errorHandler.clearError,
    showErrorDetails: errorHandler.showErrorDetails,
    isRetrying
  }
}

// Hook for handling fetch errors specifically
export function useFetchError() {
  const apiError = useApiError()

  const fetchWithErrorHandling = useCallback(async (
    url: string,
    options: RequestInit = {},
    context?: {
      userId?: string
    }
  ) => {
    try {
      const response = await fetch(url, options)
      
      if (!response.ok) {
        await apiError.handleApiError(response, {
          endpoint: url,
          method: options.method || 'GET',
          userId: context?.userId
        })
        return null
      }

      const data = await response.json()
      
      if (!data.ok) {
        await apiError.handleApiError(data, {
          endpoint: url,
          method: options.method || 'GET',
          userId: context?.userId
        })
        return null
      }

      return data
    } catch (error) {
      await apiError.handleApiError({
        ok: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Network error occurred',
          requestId: undefined
        }
      }, {
        endpoint: url,
        method: options.method || 'GET',
        userId: context?.userId
      })
      return null
    }
  }, [apiError])

  return {
    ...apiError,
    fetchWithErrorHandling
  }
}
