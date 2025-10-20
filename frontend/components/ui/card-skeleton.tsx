"use client"

import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface CardSkeletonProps {
  showHeader?: boolean
  showDescription?: boolean
  contentLines?: number
  className?: string
}

export function CardSkeleton({ 
  showHeader = true, 
  showDescription = true,
  contentLines = 3,
  className 
}: CardSkeletonProps) {
  return (
    <Card className={className}>
      {showHeader && (
        <CardHeader>
          <CardTitle>
            <Skeleton className="h-6 w-3/4" />
          </CardTitle>
          {showDescription && (
            <CardDescription>
              <Skeleton className="h-4 w-1/2" />
            </CardDescription>
          )}
        </CardHeader>
      )}
      <CardContent>
        <div className="space-y-3">
          {Array.from({ length: contentLines }).map((_, index) => (
            <Skeleton 
              key={index} 
              className={`h-4 ${index === contentLines - 1 ? 'w-2/3' : 'w-full'}`} 
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface StatsCardSkeletonProps {
  showIcon?: boolean
  className?: string
}

export function StatsCardSkeleton({ showIcon = true, className }: StatsCardSkeletonProps) {
  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-2">
          {showIcon && <Skeleton className="h-4 w-4" />}
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-8 w-16" />
      </CardContent>
    </Card>
  )
}

interface EventCardSkeletonProps {
  showBadges?: boolean
  showPayload?: boolean
  className?: string
}

export function EventCardSkeleton({ 
  showBadges = true, 
  showPayload = true,
  className 
}: EventCardSkeletonProps) {
  return (
    <div className={`border rounded-lg p-4 space-y-3 ${className}`}>
      {/* Header with badges and timestamp */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {showBadges && (
            <>
              <Skeleton className="h-5 w-16 rounded-full" />
              <Skeleton className="h-5 w-20 rounded-full" />
            </>
          )}
        </div>
        <Skeleton className="h-4 w-32" />
      </div>
      
      {/* Event details grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="space-y-1">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-3 w-full" />
          </div>
        ))}
      </div>
      
      {/* Payload section */}
      {showPayload && (
        <div className="space-y-2">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-20 w-full rounded" />
        </div>
      )}
    </div>
  )
}

interface FilterCardSkeletonProps {
  showActiveFilters?: boolean
  className?: string
}

export function FilterCardSkeleton({ 
  showActiveFilters = true, 
  className 
}: FilterCardSkeletonProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5" />
            <Skeleton className="h-6 w-16" />
            <Skeleton className="h-5 w-12 rounded-full" />
          </div>
          <Skeleton className="h-8 w-20" />
        </div>
      </CardHeader>
      <CardContent>
        {/* Filter inputs grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-4">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-10 w-full" />
            </div>
          ))}
        </div>
        
        {/* Active filters section */}
        {showActiveFilters && (
          <div className="mb-4 p-3 bg-muted/50 rounded-lg">
            <Skeleton className="h-4 w-24 mb-2" />
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 3 }).map((_, index) => (
                <Skeleton key={index} className="h-6 w-20 rounded-full" />
              ))}
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-20" />
        </div>
      </CardContent>
    </Card>
  )
}

