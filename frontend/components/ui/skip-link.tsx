"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { createSkipLink } from "@/lib/accessibility"

interface SkipLinkProps {
  href: string
  children: React.ReactNode
  className?: string
}

export function SkipLink({ href, children, className, ...props }: SkipLinkProps) {
  const skipLinkProps = createSkipLink(href)
  
  return (
    <a
      href={skipLinkProps.href}
      className={cn(skipLinkProps.className, className)}
      {...props}
    >
      {children}
    </a>
  )
}

// Predefined skip links for common destinations
export function SkipToMain() {
  return (
    <SkipLink href="#main-content">
      Skip to main content
    </SkipLink>
  )
}

export function SkipToNavigation() {
  return (
    <SkipLink href="#main-navigation">
      Skip to navigation
    </SkipLink>
  )
}

export function SkipToSearch() {
  return (
    <SkipLink href="#search">
      Skip to search
    </SkipLink>
  )
}

export function SkipToFooter() {
  return (
    <SkipLink href="#footer">
      Skip to footer
    </SkipLink>
  )
}

