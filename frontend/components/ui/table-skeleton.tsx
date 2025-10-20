"use client"

import { Skeleton } from "@/components/ui/skeleton"

interface TableSkeletonProps {
  readonly rows?: number
  readonly columns?: number
  readonly showHeader?: boolean
  readonly className?: string
}

export function TableSkeleton({ 
  rows = 5, 
  columns = 4, 
  showHeader = true,
  className 
}: TableSkeletonProps) {
  return (
    <div className={className}>
      {showHeader && (
        <div className="flex gap-4 mb-4">
          {Array.from({ length: columns }, (_, index) => (
            <Skeleton key={`header-${index}`} className="h-4 flex-1" />
          ))}
        </div>
      )}
      
      <div className="space-y-3">
        {Array.from({ length: rows }, (_, rowIndex) => (
          <div key={`row-${rowIndex}`} className="flex gap-4">
            {Array.from({ length: columns }, (_, colIndex) => (
              <Skeleton 
                key={`cell-${rowIndex}-${colIndex}`} 
                className="h-4 flex-1" 
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

interface TableRowSkeletonProps {
  readonly columns?: number
  readonly className?: string
}

export function TableRowSkeleton({ columns = 4, className }: TableRowSkeletonProps) {
  return (
    <div className={`flex gap-4 ${className}`}>
      {Array.from({ length: columns }, (_, index) => (
        <Skeleton key={index} className="h-4 flex-1" />
      ))}
    </div>
  )
}

interface TableHeaderSkeletonProps {
  readonly columns?: number
  readonly className?: string
}

export function TableHeaderSkeleton({ columns = 4, className }: TableHeaderSkeletonProps) {
  return (
    <div className={`flex gap-4 mb-4 ${className}`}>
      {Array.from({ length: columns }, (_, index) => (
        <Skeleton key={index} className="h-4 flex-1" />
      ))}
    </div>
  )
}
