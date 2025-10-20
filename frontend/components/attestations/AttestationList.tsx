"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import { ChevronDown, ChevronRight, User, Calendar, FileText, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Attestation {
  id: number
  artifactId: string
  etid: string
  kind: string
  issuedBy: string
  details: Record<string, any>
  createdAt: string
}

interface AttestationListProps {
  readonly artifactId: string
  readonly className?: string
}

const ATTESTATION_KIND_COLORS: Record<string, string> = {
  'qc_check': 'bg-blue-100 text-blue-800 border-blue-200',
  'kyc_passed': 'bg-green-100 text-green-800 border-green-200',
  'policy_ok': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'audit_complete': 'bg-purple-100 text-purple-800 border-purple-200',
  'approval_granted': 'bg-orange-100 text-orange-800 border-orange-200',
  'compliance_verified': 'bg-indigo-100 text-indigo-800 border-indigo-200',
  'risk_assessed': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'default': 'bg-gray-100 text-gray-800 border-gray-200'
}

const getKindColor = (kind: string): string => {
  return ATTESTATION_KIND_COLORS[kind] || ATTESTATION_KIND_COLORS.default
}

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return dateString
  }
}

const formatJsonDetails = (details: Record<string, any>): string => {
  try {
    return JSON.stringify(details, null, 2)
  } catch {
    return JSON.stringify(details, null, 2)
  }
}

async function fetchAttestations(artifactId: string): Promise<Attestation[]> {
  const response = await fetch(`/api/attestations?artifactId=${encodeURIComponent(artifactId)}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch attestations: ${response.statusText}`)
  }
  
  const apiResponse = await response.json()
  
  if (!apiResponse.ok) {
    throw new Error(apiResponse.error?.message || 'Failed to fetch attestations')
  }
  
  return apiResponse.data.attestations || []
}

export function AttestationList({ artifactId, className }: AttestationListProps) {
  const [expandedItems, setExpandedItems] = React.useState<Set<number>>(new Set())
  const [attestations, setAttestations] = React.useState<Attestation[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState<Error | null>(null)
  
  const fetchAttestationsData = React.useCallback(async () => {
    if (!artifactId) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await fetchAttestations(artifactId)
      setAttestations(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch attestations'))
    } finally {
      setIsLoading(false)
    }
  }, [artifactId])
  
  React.useEffect(() => {
    fetchAttestationsData()
  }, [fetchAttestationsData])
  
  // Listen for attestation creation events to refresh the list
  React.useEffect(() => {
    const handleAttestationCreated = (event: CustomEvent) => {
      if (event.detail?.artifactId === artifactId) {
        fetchAttestationsData()
      }
    }
    
    window.addEventListener('attestationCreated', handleAttestationCreated as EventListener)
    
    return () => {
      window.removeEventListener('attestationCreated', handleAttestationCreated as EventListener)
    }
  }, [artifactId, fetchAttestationsData])
  
  const toggleExpanded = React.useCallback((id: number) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }, [])
  
  const copyToClipboard = React.useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }, [])
  
  if (isLoading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Attestations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }, (_, index) => (
            <div key={index} className="border rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-5 w-20" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <Skeleton className="h-4 w-24" />
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  <Skeleton className="h-4 w-20" />
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }
  
  if (error) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Attestations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">
              Failed to load attestations: {error instanceof Error ? error.message : 'Unknown error'}
            </span>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchAttestationsData}
            className="mt-2"
          >
            Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  if (!attestations || attestations.length === 0) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Attestations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={FileText}
            title="No attestations found"
            description="This artifact doesn't have any attestations yet."
            className="py-8"
          />
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Attestations
            <Badge variant="secondary">{attestations.length}</Badge>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchAttestationsData}
          >
            Refresh
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {attestations.map((attestation) => {
          const isExpanded = expandedItems.has(attestation.id)
          
          return (
            <Collapsible key={attestation.id}>
              <div className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className={getKindColor(attestation.kind)}>
                      {attestation.kind}
                    </Badge>
                    <span className="text-sm font-medium">ETID: {attestation.etid}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {formatDate(attestation.createdAt)}
                    </span>
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleExpanded(attestation.id)}
                        className="h-6 w-6 p-0"
                        aria-label={isExpanded ? "Collapse details" : "Expand details"}
                      >
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </Button>
                    </CollapsibleTrigger>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    <span>{attestation.issuedBy}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    <span>ID: {attestation.id}</span>
                  </div>
                </div>
                
                <CollapsibleContent className="space-y-3">
                  <div className="border-t pt-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium">Details</h4>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(formatJsonDetails(attestation.details))}
                      >
                        Copy JSON
                      </Button>
                    </div>
                    <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                      {formatJsonDetails(attestation.details)}
                    </pre>
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>
          )
        })}
      </CardContent>
    </Card>
  )
}
