'use client'

import { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle, Loader2 } from 'lucide-react'

export interface SimpleToast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

interface SimpleToastProps {
  toast: SimpleToast
  onRemove: (id: string) => void
}

export function SimpleToastComponent({ toast, onRemove }: SimpleToastProps) {
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

// Simple Toast Manager using global state
let toasts: SimpleToast[] = []
let listeners: ((toasts: SimpleToast[]) => void)[] = []

function notify() {
  listeners.forEach(listener => listener([...toasts]))
}

function addToast(toast: Omit<SimpleToast, 'id'>) {
  const id = Math.random().toString(36).substr(2, 9)
  const newToast: SimpleToast = { ...toast, id }
  toasts.push(newToast)
  notify()
  return id
}

function removeToast(id: string) {
  toasts = toasts.filter(toast => toast.id !== id)
  notify()
}

function subscribe(listener: (toasts: SimpleToast[]) => void) {
  listeners.push(listener)
  return () => {
    listeners = listeners.filter(l => l !== listener)
  }
}

// Simple toast API
export const simpleToast = {
  success: (title: string, message?: string, duration?: number, id?: string) => {
    if (id) {
      const existingIndex = toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        toasts[existingIndex] = { id, type: 'success', title, message, duration }
        notify()
        return id
      }
    }
    return addToast({ type: 'success', title, message, duration })
  },

  error: (title: string, message?: string, duration?: number, id?: string) => {
    if (id) {
      const existingIndex = toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        toasts[existingIndex] = { id, type: 'error', title, message, duration }
        notify()
        return id
      }
    }
    return addToast({ type: 'error', title, message, duration })
  },

  warning: (title: string, message?: string, duration?: number, id?: string) => {
    if (id) {
      const existingIndex = toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        toasts[existingIndex] = { id, type: 'warning', title, message, duration }
        notify()
        return id
      }
    }
    return addToast({ type: 'warning', title, message, duration })
  },

  info: (title: string, message?: string, duration?: number, id?: string) => {
    if (id) {
      const existingIndex = toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        toasts[existingIndex] = { id, type: 'info', title, message, duration }
        notify()
        return id
      }
    }
    return addToast({ type: 'info', title, message, duration })
  },

  loading: (title: string, message?: string, id?: string) => {
    if (id) {
      const existingIndex = toasts.findIndex(t => t.id === id)
      if (existingIndex !== -1) {
        toasts[existingIndex] = { id, type: 'info', title, message, duration: 0 }
        notify()
        return id
      }
    }
    return addToast({ type: 'info', title, message, duration: 0 })
  },

  remove: removeToast
}

// Simple Toast Container Component
export function SimpleToastContainer() {
  const [toastList, setToastList] = useState<SimpleToast[]>([])

  useEffect(() => {
    return subscribe(setToastList)
  }, [])

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toastList.map(toastItem => (
        <SimpleToastComponent
          key={toastItem.id}
          toast={toastItem}
          onRemove={removeToast}
        />
      ))}
    </div>
  )
}
