"use client"

import * as React from "react"
import { Input, InputProps } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface AccessibleInputProps extends InputProps {
  label?: string
  description?: string
  error?: string
  required?: boolean
  "aria-describedby"?: string
  "aria-invalid"?: boolean
  "aria-required"?: boolean
}

const AccessibleInput = React.forwardRef<HTMLInputElement, AccessibleInputProps>(
  ({
    className,
    label,
    description,
    error,
    required = false,
    id,
    "aria-describedby": ariaDescribedBy,
    "aria-invalid": ariaInvalid,
    "aria-required": ariaRequired,
    ...props
  }, ref) => {
  const inputId = React.useId()
  const descriptionId = React.useId()
  const errorId = React.useId()
  
  const finalInputId = id || inputId

    const isInvalid = ariaInvalid || !!error
    const describedBy = React.useMemo(() => {
      const ids = []
      if (ariaDescribedBy) ids.push(ariaDescribedBy)
      if (description) ids.push(descriptionId)
      if (error) ids.push(errorId)
      return ids.length > 0 ? ids.join(' ') : undefined
    }, [ariaDescribedBy, description, error, descriptionId, errorId])

    return (
      <div className="space-y-2">
        {label && (
          <Label 
            htmlFor={finalInputId}
            className={cn(
              "text-sm font-medium",
              isInvalid && "text-destructive"
            )}
          >
            {label}
            {required && (
              <span className="text-destructive ml-1" aria-label="required">
                *
              </span>
            )}
          </Label>
        )}
        
        <Input
          ref={ref}
          id={finalInputId}
          className={cn(
            "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            isInvalid && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-describedby={describedBy}
          aria-invalid={isInvalid}
          aria-required={required || ariaRequired}
          {...props}
        />
        
        {description && !error && (
          <p 
            id={descriptionId}
            className="text-sm text-muted-foreground"
          >
            {description}
          </p>
        )}
        
        {error && (
          <p 
            id={errorId}
            className="text-sm text-destructive"
            role="alert"
            aria-live="polite"
          >
            {error}
          </p>
        )}
      </div>
    )
  }
)

AccessibleInput.displayName = "AccessibleInput"

export { AccessibleInput, type AccessibleInputProps }
