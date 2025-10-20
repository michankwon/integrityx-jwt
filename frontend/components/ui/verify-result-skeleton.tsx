"use client"

import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface VerifyResultSkeletonProps {
  showAlert?: boolean
  showDetails?: boolean
  showActions?: boolean
  className?: string
}

export function VerifyResultSkeleton({ 
  showAlert = true, 
  showDetails = true,
  showActions = true,
  className 
}: VerifyResultSkeletonProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-6 w-48" />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Alert section */}
        {showAlert && (
          <Alert>
            <Skeleton className="h-4 w-4" />
            <AlertDescription>
              <Skeleton className="h-4 w-64" />
            </AlertDescription>
          </Alert>
        )}
        
        {/* Status and timestamp grid */}
        {showDetails && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-16" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        )}
        
        {/* Artifact ID section */}
        {showDetails && (
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <div className="flex gap-2">
              <Skeleton className="h-8 flex-1" />
              <Skeleton className="h-8 w-8" />
            </div>
          </div>
        )}
        
        {/* Hash comparison grid */}
        {showDetails && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-full" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-8 w-full" />
            </div>
          </div>
        )}
        
        {/* Additional details grid */}
        {showDetails && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-24" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        {showActions && (
          <div className="flex gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-28" />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface ProofResultSkeletonProps {
  showDetails?: boolean
  showRawData?: boolean
  className?: string
}

export function ProofResultSkeleton({ 
  showDetails = true, 
  showRawData = true,
  className 
}: ProofResultSkeletonProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-6 w-40" />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Proof details grid */}
        {showDetails && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-8 w-full" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-16" />
            </div>
          </div>
        )}
        
        {/* Raw data section */}
        {showRawData && (
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-32 w-full rounded" />
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-32" />
        </div>
      </CardContent>
    </Card>
  )
}

interface UploadResultSkeletonProps {
  showSuccess?: boolean
  showDetails?: boolean
  showActions?: boolean
  className?: string
}

export function UploadResultSkeleton({ 
  showSuccess = true, 
  showDetails = true,
  showActions = true,
  className 
}: UploadResultSkeletonProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-6 w-40" />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Success alert */}
        {showSuccess && (
          <Alert>
            <Skeleton className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-64" />
              </div>
            </AlertDescription>
          </Alert>
        )}
        
        {/* Upload details */}
        {showDetails && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-32" />
            </div>
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-28" />
            </div>
            <div className="flex items-center justify-between">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-36" />
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        {showActions && (
          <div className="flex gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-28" />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

