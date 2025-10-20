"use client"

import * as React from "react"
import { createPortal } from "react-dom"
import { cn } from "@/lib/utils"
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ToastProps {
  id: string
  title?: string
  description?: string
  type?: "success" | "error" | "warning" | "info"
  duration?: number
  onClose: (id: string) => void
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

const toastVariants = {
  success: {
    icon: CheckCircle,
    className: "border-green-200 bg-green-50 text-green-800",
    iconClassName: "text-green-600"
  },
  error: {
    icon: AlertCircle,
    className: "border-red-200 bg-red-50 text-red-800",
    iconClassName: "text-red-600"
  },
  warning: {
    icon: AlertTriangle,
    className: "border-yellow-200 bg-yellow-50 text-yellow-800",
    iconClassName: "text-yellow-600"
  },
  info: {
    icon: Info,
    className: "border-blue-200 bg-blue-50 text-blue-800",
    iconClassName: "text-blue-600"
  }
}

export function AccessibleToast({
  id,
  title,
  description,
  type = "info",
  duration = 5000,
  onClose,
  action,
  className
}: ToastProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const [isRemoving, setIsRemoving] = React.useState(false)
  const toastRef = React.useRef<HTMLDivElement>(null)
  const timeoutRef = React.useRef<NodeJS.Timeout>()

  const variant = toastVariants[type]
  const Icon = variant.icon

  // Auto-dismiss timer
  React.useEffect(() => {
    if (duration > 0) {
      timeoutRef.current = setTimeout(() => {
        handleClose()
      }, duration)
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [duration])

  // Show toast with animation
  React.useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  const handleClose = React.useCallback(() => {
    setIsRemoving(true)
    setTimeout(() => {
      onClose(id)
    }, 300) // Match animation duration
  }, [id, onClose])

  const handleKeyDown = React.useCallback((event: React.KeyboardEvent) => {
    if (event.key === "Escape") {
      handleClose()
    }
  }, [handleClose])

  // Focus management
  React.useEffect(() => {
    if (isVisible && toastRef.current) {
      toastRef.current.focus()
    }
  }, [isVisible])

  const toastContent = (
    <div
      ref={toastRef}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      tabIndex={-1}
      className={cn(
        "pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border shadow-lg transition-all duration-300 ease-in-out",
        variant.className,
        isVisible && !isRemoving ? "translate-x-0 opacity-100" : "translate-x-full opacity-0",
        className
      )}
      onKeyDown={handleKeyDown as any}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <Icon className={cn("h-5 w-5", variant.iconClassName)} aria-hidden="true" />
          </div>
          <div className="ml-3 w-0 flex-1">
            {title && (
              <p className="text-sm font-medium" id={`toast-title-${id}`}>
                {title}
              </p>
            )}
            {description && (
              <p 
                className={cn(
                  "text-sm",
                  title ? "mt-1" : ""
                )}
                id={`toast-description-${id}`}
              >
                {description}
              </p>
            )}
            {action && (
              <div className="mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={action.onClick}
                  className="text-xs"
                >
                  {action.label}
                </Button>
              </div>
            )}
          </div>
          <div className="ml-4 flex flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="h-6 w-6 p-0"
              aria-label="Close notification"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  return createPortal(toastContent, document.body)
}

// Toast container component
interface ToastContainerProps {
  readonly toasts: ToastProps[]
  readonly position?: "top-right" | "top-left" | "bottom-right" | "bottom-left" | "top-center" | "bottom-center"
  readonly className?: string
}

export function ToastContainer({ 
  toasts, 
  position = "top-right",
  className 
}: ToastContainerProps) {
  const positionClasses = {
    "top-right": "top-4 right-4",
    "top-left": "top-4 left-4",
    "bottom-right": "bottom-4 right-4",
    "bottom-left": "bottom-4 left-4",
    "top-center": "top-4 left-1/2 transform -translate-x-1/2",
    "bottom-center": "bottom-4 left-1/2 transform -translate-x-1/2"
  }

  return (
    <div
      className={cn(
        "fixed z-50 flex flex-col space-y-2 pointer-events-none",
        positionClasses[position],
        className
      )}
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <AccessibleToast key={toast.id} {...toast} />
      ))}
    </div>
  )
}

// Toast hook for managing toasts
interface Toast {
  id: string
  title?: string
  description?: string
  type?: "success" | "error" | "warning" | "info"
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

export function useAccessibleToast() {
  const [toasts, setToasts] = React.useState<Toast[]>([])

  const addToast = React.useCallback((toast: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substring(2, 11)
    const newToast = { ...toast, id }
    
    setToasts(prev => [...prev, newToast])
    
    return id
  }, [])

  const removeToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const clearAllToasts = React.useCallback(() => {
    setToasts([])
  }, [])

  // Convenience methods
  const toast = React.useMemo(() => ({
    success: (title: string, description?: string, options?: Partial<Toast>) => 
      addToast({ title, description, type: "success", ...options }),
    error: (title: string, description?: string, options?: Partial<Toast>) => 
      addToast({ title, description, type: "error", ...options }),
    warning: (title: string, description?: string, options?: Partial<Toast>) => 
      addToast({ title, description, type: "warning", ...options }),
    info: (title: string, description?: string, options?: Partial<Toast>) => 
      addToast({ title, description, type: "info", ...options }),
    custom: (toast: Omit<Toast, "id">) => addToast(toast)
  }), [addToast])

  return {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    toast
  }
}

// Toast provider component
interface ToastProviderProps {
  readonly children: React.ReactNode
  readonly position?: "top-right" | "top-left" | "bottom-right" | "bottom-left" | "top-center" | "bottom-center"
}

const ToastContext = React.createContext<ReturnType<typeof useAccessibleToast> | null>(null)

export function ToastProvider({ children, position = "top-right" }: ToastProviderProps) {
  const toastHook = useAccessibleToast()

  return (
    <ToastContext.Provider value={toastHook}>
      {children}
      <ToastContainer toasts={toastHook.toasts} position={position} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}
