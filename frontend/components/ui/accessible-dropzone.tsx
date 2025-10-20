"use client"

import * as React from "react"
import { useDropzone } from "react-dropzone"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Upload, FileText, AlertCircle } from "lucide-react"

interface AccessibleDropzoneProps {
  readonly onDrop: (acceptedFiles: File[]) => void
  readonly accept?: Record<string, string[]>
  readonly maxFiles?: number
  readonly maxSize?: number
  readonly disabled?: boolean
  readonly className?: string
  readonly description?: string
  readonly errorMessage?: string
  readonly id?: string
  readonly "aria-label"?: string
  readonly "aria-describedby"?: string
}

export function AccessibleDropzone({
  onDrop,
  accept,
  maxFiles = 1,
  maxSize,
  disabled = false,
  className,
  description = "Drag and drop files here, or click to select files",
  errorMessage,
  id,
  "aria-label": ariaLabel,
  "aria-describedby": ariaDescribedBy,
  ...props
}: AccessibleDropzoneProps) {
  const [isDragActive, setIsDragActive] = React.useState(false)
  const [keyboardFocused, setKeyboardFocused] = React.useState(false)
  const dropzoneRef = React.useRef<HTMLDivElement>(null)
  const descriptionId = React.useId()
  const errorId = React.useId()

  const {
    getRootProps,
    getInputProps,
    isDragReject,
    fileRejections,
    isDragAccept,
  } = useDropzone({
    onDrop,
    accept,
    maxFiles,
    maxSize,
    disabled,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    onDropAccepted: () => setIsDragActive(false),
    onDropRejected: () => setIsDragActive(false),
  })

  // Handle keyboard events
  const handleKeyDown = React.useCallback((event: React.KeyboardEvent) => {
    if (disabled) return

    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      // Trigger file input click
      const input = dropzoneRef.current?.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        input.click()
      }
    }
  }, [disabled])

  const handleFocus = React.useCallback(() => {
    setKeyboardFocused(true)
  }, [])

  const handleBlur = React.useCallback(() => {
    setKeyboardFocused(false)
  }, [])

  // Generate accessible description
  const accessibleDescription = React.useMemo(() => {
    const parts = [description]
    
    if (accept) {
      const acceptedTypes = Object.keys(accept).join(", ")
      parts.push(`Accepted file types: ${acceptedTypes}`)
    }
    
    if (maxSize) {
      const sizeInMB = Math.round(maxSize / (1024 * 1024))
      parts.push(`Maximum file size: ${sizeInMB}MB`)
    }
    
    if (maxFiles > 1) {
      parts.push(`Maximum ${maxFiles} files`)
    }
    
    return parts.join(". ")
  }, [description, accept, maxSize, maxFiles])

  // Get current state for styling
  const getStateClasses = () => {
    if (disabled) return "opacity-50 cursor-not-allowed"
    if (isDragReject || fileRejections.length > 0) return "border-red-500 bg-red-50"
    if (isDragAccept) return "border-green-500 bg-green-50"
    if (isDragActive) return "border-blue-500 bg-blue-50"
    if (keyboardFocused) return "ring-2 ring-ring ring-offset-2"
    return "border-gray-300 hover:border-gray-400"
  }

  const getIcon = () => {
    if (isDragReject || fileRejections.length > 0) {
      return <AlertCircle className="h-8 w-8 text-red-500" />
    }
    if (isDragAccept) {
      return <FileText className="h-8 w-8 text-green-500" />
    }
    return <Upload className="h-8 w-8 text-gray-400" />
  }

  const getStatusText = () => {
    if (isDragReject || fileRejections.length > 0) {
      return "File type not supported"
    }
    if (isDragAccept) {
      return "Drop files here"
    }
    if (isDragActive) {
      return "Drop files here"
    }
    return "Click to upload or drag and drop"
  }

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        ref={dropzoneRef}
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors focus:outline-none",
          getStateClasses(),
          className
        )}
        tabIndex={disabled ? -1 : 0}
        aria-label={ariaLabel || "File upload area"}
        aria-describedby={ariaDescribedBy || descriptionId}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}
      >
        <input
          {...getInputProps()}
          id={id}
          aria-describedby={ariaDescribedBy || descriptionId}
        />
        
        <div className="flex flex-col items-center space-y-2">
          {getIcon()}
          <div className="text-sm">
            <p className="font-medium text-gray-900">
              {getStatusText()}
            </p>
            <p 
              id={descriptionId}
              className="text-gray-500 mt-1"
            >
              {accessibleDescription}
            </p>
          </div>
        </div>
      </div>

      {/* Error messages */}
      {fileRejections.length > 0 && (
        <div 
          id={errorId}
          className="text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name}>
              <strong>{file.name}:</strong> {errors.map(e => e.message).join(", ")}
            </div>
          ))}
        </div>
      )}

      {/* Custom error message */}
      {errorMessage && (
        <div 
          className="text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          {errorMessage}
        </div>
      )}
    </div>
  )
}

// Alternative button-style dropzone for more compact layouts
interface AccessibleDropzoneButtonProps {
  readonly onDrop: (acceptedFiles: File[]) => void
  readonly accept?: Record<string, string[]>
  readonly maxFiles?: number
  readonly maxSize?: number
  readonly disabled?: boolean
  readonly className?: string
  readonly children?: React.ReactNode
  readonly "aria-label"?: string
  readonly "aria-describedby"?: string
}

export function AccessibleDropzoneButton({
  onDrop,
  accept,
  maxFiles = 1,
  maxSize,
  disabled = false,
  className,
  children,
  "aria-label": ariaLabel,
  "aria-describedby": ariaDescribedBy,
  ...props
}: AccessibleDropzoneButtonProps) {
  const [isDragActive, setIsDragActive] = React.useState(false)
  const dropzoneRef = React.useRef<HTMLDivElement>(null)
  const descriptionId = React.useId()

  const {
    getRootProps,
    getInputProps,
    isDragReject,
    fileRejections,
    isDragAccept,
  } = useDropzone({
    onDrop,
    accept,
    maxFiles,
    maxSize,
    disabled,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    onDropAccepted: () => setIsDragActive(false),
    onDropRejected: () => setIsDragActive(false),
  })

  // Handle keyboard events
  const handleKeyDown = React.useCallback((event: React.KeyboardEvent) => {
    if (disabled) return

    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      // Trigger file input click
      const input = dropzoneRef.current?.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        input.click()
      }
    }
  }, [disabled])

  // Generate accessible description
  const accessibleDescription = React.useMemo(() => {
    const parts = []
    
    if (accept) {
      const acceptedTypes = Object.keys(accept).join(", ")
      parts.push(`Accepted: ${acceptedTypes}`)
    }
    
    if (maxSize) {
      const sizeInMB = Math.round(maxSize / (1024 * 1024))
      parts.push(`Max size: ${sizeInMB}MB`)
    }
    
    return parts.join(", ")
  }, [accept, maxSize])

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        ref={dropzoneRef}
        className={cn(
          "inline-flex items-center justify-center",
          className
        )}
        tabIndex={disabled ? -1 : 0}
        aria-label={ariaLabel || "Upload files"}
        aria-describedby={ariaDescribedBy || descriptionId}
        onKeyDown={handleKeyDown}
        {...props}
      >
        <input
          {...getInputProps()}
          aria-describedby={ariaDescribedBy || descriptionId}
        />
        
        <Button
          variant="outline"
          disabled={disabled}
          className={cn(
            isDragActive && "bg-accent",
            isDragAccept && "border-green-500 bg-green-50",
            isDragReject && "border-red-500 bg-red-50"
          )}
        >
          {children || (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Upload Files
            </>
          )}
        </Button>
      </div>

      {/* Hidden description for screen readers */}
      <div 
        id={descriptionId}
        className="sr-only"
      >
        {accessibleDescription}
      </div>

      {/* Error messages */}
      {fileRejections.length > 0 && (
        <div 
          className="text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name}>
              <strong>{file.name}:</strong> {errors.map(e => e.message).join(", ")}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
