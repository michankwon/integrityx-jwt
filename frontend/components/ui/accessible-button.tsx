"use client"

import * as React from "react"
import { Button, ButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { isActivationKey } from "@/lib/accessibility"

interface AccessibleButtonProps extends ButtonProps {
  "aria-describedby"?: string
  "aria-expanded"?: boolean
  "aria-haspopup"?: boolean | "menu" | "listbox" | "tree" | "grid" | "dialog"
  "aria-controls"?: string
  "aria-pressed"?: boolean
  "aria-current"?: boolean | "page" | "step" | "location" | "date" | "time"
  loading?: boolean
  loadingText?: string
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
}

const AccessibleButton = React.forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  ({
    className,
    children,
    disabled,
    loading = false,
    loadingText,
    icon,
    iconPosition = "left",
    "aria-describedby": ariaDescribedBy,
    "aria-expanded": ariaExpanded,
    "aria-haspopup": ariaHaspopup,
    "aria-controls": ariaControls,
    "aria-pressed": ariaPressed,
    "aria-current": ariaCurrent,
    onKeyDown,
    ...props
  }, ref) => {
    const [isKeyboardFocused, setIsKeyboardFocused] = React.useState(false)

    const handleKeyDown = React.useCallback((event: React.KeyboardEvent<HTMLButtonElement>) => {
      // Handle activation keys
      if (isActivationKey(event.key) && !disabled && !loading) {
        // Let the default behavior handle the activation
        return
      }

      // Call custom onKeyDown if provided
      if (onKeyDown) {
        onKeyDown(event)
      }
    }, [disabled, loading, onKeyDown])

    const handleFocus = React.useCallback(() => {
      setIsKeyboardFocused(true)
    }, [])

    const handleBlur = React.useCallback(() => {
      setIsKeyboardFocused(false)
    }, [])

    const isDisabled = disabled || loading

    const buttonContent = React.useMemo(() => {
      if (loading) {
        return (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent mr-2" />
            {loadingText || "Loading..."}
          </>
        )
      }

      if (icon && iconPosition === "left") {
        return (
          <>
            {icon}
            {children}
          </>
        )
      }

      if (icon && iconPosition === "right") {
        return (
          <>
            {children}
            {icon}
          </>
        )
      }

      return children
    }, [loading, loadingText, icon, iconPosition, children])

    return (
      <Button
        ref={ref}
        className={cn(
          "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          isKeyboardFocused && "ring-2 ring-ring ring-offset-2",
          className
        )}
        disabled={isDisabled}
        aria-describedby={ariaDescribedBy}
        aria-expanded={ariaExpanded}
        aria-haspopup={ariaHaspopup}
        aria-controls={ariaControls}
        aria-pressed={ariaPressed}
        aria-current={ariaCurrent}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}
      >
        {buttonContent}
      </Button>
    )
  }
)

AccessibleButton.displayName = "AccessibleButton"

export { AccessibleButton, type AccessibleButtonProps }

