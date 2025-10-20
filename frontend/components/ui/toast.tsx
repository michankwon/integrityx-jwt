'use client'

import { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle, Loader2 } from 'lucide-react'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

interface ToastProps {
  toast: Toast
  onRemove: (id: string) => void
}

export function ToastComponent({ toast, onRemove }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setIsVisible(true), 10)

    // Auto remove (skip for loading toasts with duration: 0)
    const duration = toast.duration || 5000
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => onRemove(toast.id), 300)
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [toast.id, toast.duration, onRemove])

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case 'info':
        return toast.duration === 0 ? 
          <Loader2 className="h-5 w-5 text-blue-600 animate-spin" /> : 
          <Info className="h-5 w-5 text-blue-600" />
    }
  }

  const getBackgroundColor = () => {
    switch (toast.type) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'info':
        return 'bg-blue-50 border-blue-200'
    }
  }

  return (
    <div
      className={`
        fixed top-4 right-4 z-50 max-w-sm w-full
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      `}
    >
      <div className={`
        p-4 rounded-lg border shadow-lg
        ${getBackgroundColor()}
      `}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div className="ml-3 flex-1">
            <h4 className="text-sm font-medium text-gray-900">
              {toast.title}
            </h4>
            {toast.message && (
              <p className="mt-1 text-sm text-gray-600">
                {toast.message}
              </p>
            )}
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={() => {
                setIsVisible(false)
                setTimeout(() => onRemove(toast.id), 300)
              }}
              className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Toast Manager
class ToastManager {
  private toasts: Toast[] = []
  private listeners: ((toasts: Toast[]) => void)[] = []

  constructor() {
    // Bind methods to ensure proper 'this' context
    this.subscribe = this.subscribe.bind(this)
    this.add = this.add.bind(this)
    this.remove = this.remove.bind(this)
    this.success = this.success.bind(this)
    this.error = this.error.bind(this)
    this.warning = this.warning.bind(this)
    this.info = this.info.bind(this)
    this.loading = this.loading.bind(this)
    this.notify = this.notify.bind(this)
  }

  subscribe(listener: (toasts: Toast[]) => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  private notify() {
    this.listeners.forEach(listener => listener([...this.toasts]))
  }

  add(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast: Toast = { ...toast, id }
    this.toasts.push(newToast)
    this.notify()
    return id
  }

  remove(id: string) {
    this.toasts = this.toasts.filter(toast => toast.id !== id)
    this.notify()
  }

  success(title: string, message?: string, duration?: number, id?: string) {
    if (id) {
      // Update existing toast
      const existingIndex = this.toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        this.toasts[existingIndex] = { id, type: 'success', title, message, duration }
        this.notify()
        return id
      }
    }
    return this.add({ type: 'success', title, message, duration })
  }

  error(title: string, message?: string, duration?: number, id?: string) {
    if (id) {
      // Update existing toast
      const existingIndex = this.toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        this.toasts[existingIndex] = { id, type: 'error', title, message, duration }
        this.notify()
        return id
      }
    }
    return this.add({ type: 'error', title, message, duration })
  }

  warning(title: string, message?: string, duration?: number, id?: string) {
    if (id) {
      // Update existing toast
      const existingIndex = this.toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        this.toasts[existingIndex] = { id, type: 'warning', title, message, duration }
        this.notify()
        return id
      }
    }
    return this.add({ type: 'warning', title, message, duration })
  }

  info(title: string, message?: string, duration?: number, id?: string) {
    if (id) {
      // Update existing toast
      const existingIndex = this.toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        this.toasts[existingIndex] = { id, type: 'info', title, message, duration }
        this.notify()
        return id
      }
    }
    return this.add({ type: 'info', title, message, duration })
  }

  loading(title: string, message?: string, id?: string) {
    if (id) {
      // Update existing toast
      const existingIndex = this.toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        this.toasts[existingIndex] = { id, type: 'info', title, message, duration: 0 }
        this.notify()
        return id
      }
    }
    return this.add({ type: 'info', title, message, duration: 0 })
  }
}

// Create singleton instance
const toastManager = new ToastManager()
export const toast = toastManager

// Toast Container Component
export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => {
    return toast.subscribe(setToasts)
  }, [])

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toastItem => (
        <ToastComponent
          key={toastItem.id}
          toast={toastItem}
          onRemove={toast.remove}
        />
      ))}
    </div>
  )
}
