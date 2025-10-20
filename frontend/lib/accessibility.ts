/**
 * Accessibility utilities for focus management, ARIA attributes, and keyboard navigation
 */

import { useEffect, useRef, useCallback, useState } from "react"

// Focus management utilities
export function useFocusManagement() {
  const focusableElementsRef = useRef<HTMLElement[]>([])
  const previousActiveElementRef = useRef<Element | null>(null)

  const setFocusableElements = useCallback((container: HTMLElement | null) => {
    if (!container) {
      focusableElementsRef.current = []
      return
    }

    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ].join(', ')

    focusableElementsRef.current = Array.from(
      container.querySelectorAll(focusableSelectors)
    ) as HTMLElement[]
  }, [])

  const trapFocus = useCallback((event: KeyboardEvent) => {
    if (event.key !== 'Tab' || focusableElementsRef.current.length === 0) {
      return
    }

    const firstElement = focusableElementsRef.current[0]
    const lastElement = focusableElementsRef.current[focusableElementsRef.current.length - 1]

    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      }
    } else if (document.activeElement === lastElement) {
      event.preventDefault()
      firstElement.focus()
    }
  }, [])

  const restoreFocus = useCallback(() => {
    if (previousActiveElementRef.current instanceof HTMLElement) {
      previousActiveElementRef.current.focus()
    }
  }, [])

  const saveFocus = useCallback(() => {
    previousActiveElementRef.current = document.activeElement
  }, [])

  return {
    setFocusableElements,
    trapFocus,
    restoreFocus,
    saveFocus
  }
}

// ARIA utilities
export function generateAriaId(prefix: string = 'aria'): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 11)}`
}

export function createAriaDescribedBy(...ids: (string | undefined)[]): string {
  return ids.filter(Boolean).join(' ')
}

// Keyboard navigation utilities
export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End'
} as const

export function isActivationKey(key: string): boolean {
  return key === KEYBOARD_KEYS.ENTER || key === KEYBOARD_KEYS.SPACE
}

export function isNavigationKey(key: string): boolean {
  return [
    KEYBOARD_KEYS.ARROW_UP,
    KEYBOARD_KEYS.ARROW_DOWN,
    KEYBOARD_KEYS.ARROW_LEFT,
    KEYBOARD_KEYS.ARROW_RIGHT,
    KEYBOARD_KEYS.HOME,
    KEYBOARD_KEYS.END
  ].includes(key as any)
}

// Screen reader utilities
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div')
  announcement.setAttribute('aria-live', priority)
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message

  document.body.appendChild(announcement)

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

// Focus ring utilities
export function addFocusRing(element: HTMLElement) {
  element.classList.add('focus-visible:ring-2', 'focus-visible:ring-ring', 'focus-visible:ring-offset-2')
}

export function removeFocusRing(element: HTMLElement) {
  element.classList.remove('focus-visible:ring-2', 'focus-visible:ring-ring', 'focus-visible:ring-offset-2')
}

// High contrast mode detection
export function useHighContrastMode() {
  const [isHighContrast, setIsHighContrast] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    setIsHighContrast(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return isHighContrast
}

// Reduced motion detection
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersReducedMotion
}

// Color scheme detection
export function useColorScheme() {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark' | 'no-preference'>('no-preference')

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    setColorScheme(mediaQuery.matches ? 'dark' : 'light')

    const handleChange = (e: MediaQueryListEvent) => {
      setColorScheme(e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return colorScheme
}

// Form validation accessibility
export function createValidationMessage(fieldId: string, message: string): string {
  const messageId = `${fieldId}-error`
  return messageId
}

export function getValidationAriaAttributes(
  fieldId: string, 
  isValid: boolean, 
  errorMessage?: string
) {
  const messageId = `${fieldId}-error`
  
  return {
    'aria-invalid': !isValid,
    'aria-describedby': errorMessage ? messageId : undefined
  }
}

// Skip link utilities
export function createSkipLink(targetId: string, label: string = 'Skip to main content') {
  return {
    href: `#${targetId}`,
    className: 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md',
    children: label
  }
}

// Landmark utilities
export const LANDMARK_ROLES = {
  BANNER: 'banner',
  COMPLEMENTARY: 'complementary',
  CONTENTINFO: 'contentinfo',
  FORM: 'form',
  MAIN: 'main',
  NAVIGATION: 'navigation',
  REGION: 'region',
  SEARCH: 'search'
} as const

export function createLandmarkProps(role: keyof typeof LANDMARK_ROLES, label?: string) {
  return {
    role: LANDMARK_ROLES[role],
    'aria-label': label
  }
}

// Live region utilities
export const LIVE_REGION_PRIORITIES = {
  POLITE: 'polite',
  ASSERTIVE: 'assertive',
  OFF: 'off'
} as const

export function createLiveRegionProps(priority: keyof typeof LIVE_REGION_PRIORITIES = 'POLITE') {
  return {
    'aria-live': LIVE_REGION_PRIORITIES[priority],
    'aria-atomic': 'true'
  }
}

