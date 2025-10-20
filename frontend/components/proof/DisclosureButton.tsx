"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Download, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface DisclosureButtonProps {
  readonly artifactId: string
  readonly className?: string
  readonly variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive'
  readonly size?: 'default' | 'sm' | 'lg' | 'icon'
}

async function downloadDisclosurePack(artifactId: string): Promise<void> {
  const response = await fetch(`/api/disclosure-pack?id=${encodeURIComponent(artifactId)}`)
  
  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`)
  }
  
  // Check if it's a ZIP file
  const contentType = response.headers.get('content-type')
  if (!contentType?.includes('application/zip')) {
    throw new Error('Response is not a ZIP file')
  }
  
  // Get the filename from Content-Disposition header or use default
  const contentDisposition = response.headers.get('content-disposition')
  let filename = `disclosure_${artifactId}.zip`
  
  if (contentDisposition) {
    const filenameRegex = /filename="([^"]+)"/
    const filenameMatch = filenameRegex.exec(contentDisposition)
    if (filenameMatch) {
      filename = filenameMatch[1]
    }
  }
  
  // Create blob and download
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  
  // Create temporary download link
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.style.display = 'none'
  
  // Add to DOM, click, and remove
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  
  // Clean up
  window.URL.revokeObjectURL(url)
}

export function DisclosureButton({ 
  artifactId, 
  className, 
  variant = 'outline',
  size = 'default'
}: DisclosureButtonProps) {
  const [isDownloading, setIsDownloading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState(false)
  
  const handleDownload = async () => {
    if (!artifactId) {
      toast.error('No artifact ID available for disclosure pack')
      return
    }
    
    setIsDownloading(true)
    setError(null)
    setSuccess(false)
    
    try {
      await downloadDisclosurePack(artifactId)
      setSuccess(true)
      toast.success('Disclosure pack downloaded successfully!')
      
      // Reset success state after a short delay
      setTimeout(() => setSuccess(false), 2000)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to download disclosure pack'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsDownloading(false)
    }
  }
  
  return (
    <div className={cn("space-y-2", className)}>
      <Button
        onClick={handleDownload}
        disabled={isDownloading || !artifactId}
        variant={variant}
        size={size}
        className="w-full"
      >
        {(() => {
          if (isDownloading) {
            return (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Pack...
              </>
            )
          }
          
          if (success) {
            return (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Downloaded!
              </>
            )
          }
          
          return (
            <>
              <Download className="h-4 w-4 mr-2" />
              Download Disclosure Pack
            </>
          )
        })()}
      </Button>
      
      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      )}
      
      {/* Help Text */}
      <div className="text-xs text-muted-foreground">
        Downloads a ZIP file containing proof, artifact details, attestations, audit events, and manifest.
      </div>
    </div>
  )
}
