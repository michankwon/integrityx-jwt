"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import { GitBranch, ArrowUp, ArrowDown, AlertCircle, RefreshCw, Copy } from 'lucide-react'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface ProvenanceLink {
  id: number
  parentArtifactId: string
  childArtifactId: string
  relation: string
  createdAt: string
}

interface LineageGraphProps {
  readonly artifactId: string
  readonly className?: string
}

const RELATION_COLORS: Record<string, string> = {
  'contains': 'bg-blue-100 text-blue-800 border-blue-200',
  'derived_from': 'bg-green-100 text-green-800 border-green-200',
  'supersedes': 'bg-orange-100 text-orange-800 border-orange-200',
  'references': 'bg-purple-100 text-purple-800 border-purple-200',
  'validates': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'default': 'bg-gray-100 text-gray-800 border-gray-200'
}

const getRelationColor = (relation: string): string => {
  return RELATION_COLORS[relation] || RELATION_COLORS.default
}

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}

async function fetchParents(childId: string): Promise<ProvenanceLink[]> {
  const response = await fetch(`/api/provenance/parents?childId=${encodeURIComponent(childId)}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch parents: ${response.statusText}`)
  }
  
  const apiResponse = await response.json()
  
  if (!apiResponse.ok) {
    throw new Error(apiResponse.error?.message || 'Failed to fetch parents')
  }
  
  return apiResponse.data.parents || []
}

async function fetchChildren(parentId: string): Promise<ProvenanceLink[]> {
  const response = await fetch(`/api/provenance/children?parentId=${encodeURIComponent(parentId)}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch children: ${response.statusText}`)
  }
  
  const apiResponse = await response.json()
  
  if (!apiResponse.ok) {
    throw new Error(apiResponse.error?.message || 'Failed to fetch children')
  }
  
  return apiResponse.data.children || []
}

export function LineageGraph({ artifactId, className }: LineageGraphProps) {
  const [parents, setParents] = React.useState<ProvenanceLink[]>([])
  const [children, setChildren] = React.useState<ProvenanceLink[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState<Error | null>(null)
  
  const fetchLineageData = React.useCallback(async () => {
    if (!artifactId) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const [parentsData, childrenData] = await Promise.all([
        fetchParents(artifactId),
        fetchChildren(artifactId)
      ])
      
      setParents(parentsData)
      setChildren(childrenData)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch lineage data'))
    } finally {
      setIsLoading(false)
    }
  }, [artifactId])
  
  React.useEffect(() => {
    fetchLineageData()
  }, [fetchLineageData])
  
  // Listen for provenance link creation events to refresh the graph
  React.useEffect(() => {
    const handleProvenanceLinkCreated = (event: CustomEvent) => {
      if (event.detail?.artifactId === artifactId) {
        fetchLineageData()
      }
    }
    
    window.addEventListener('provenanceLinkCreated', handleProvenanceLinkCreated as EventListener)
    
    return () => {
      window.removeEventListener('provenanceLinkCreated', handleProvenanceLinkCreated as EventListener)
    }
  }, [artifactId, fetchLineageData])
  
  const copyToClipboard = React.useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast.success('Copied to clipboard')
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
      toast.error('Failed to copy to clipboard')
    }
  }, [])
  
  if (isLoading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Document Lineage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Parents skeleton */}
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <div className="space-y-2">
              {Array.from({ length: 2 }, (_, index) => (
                <div key={index} className="flex items-center gap-2 p-3 border rounded-lg">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-5 w-20" />
                </div>
              ))}
            </div>
          </div>
          
          {/* Current node skeleton */}
          <div className="flex justify-center">
            <div className="flex items-center gap-2 p-4 border-2 border-primary rounded-lg bg-primary/5">
              <Skeleton className="h-4 w-4" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
          
          {/* Children skeleton */}
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <div className="space-y-2">
              {Array.from({ length: 2 }, (_, index) => (
                <div key={index} className="flex items-center gap-2 p-3 border rounded-lg">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-5 w-20" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  if (error) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Document Lineage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">
              Failed to load lineage: {error.message}
            </span>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchLineageData}
            className="mt-2"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  const hasLineage = parents.length > 0 || children.length > 0
  
  if (!hasLineage) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Document Lineage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={GitBranch}
            title="No lineage data"
            description="This document doesn't have any parent or child relationships yet."
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
            <GitBranch className="h-5 w-5" />
            Document Lineage
            <Badge variant="secondary">
              {parents.length + children.length} links
            </Badge>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchLineageData}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Parents Section */}
        {parents.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <ArrowUp className="h-4 w-4" />
              Parents ({parents.length})
            </div>
            <div className="space-y-2">
              {parents.map((link) => (
                <div key={link.id} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-2 flex-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    <span className="font-mono text-sm">{link.parentArtifactId}</span>
                    <Badge className={getRelationColor(link.relation)}>
                      {link.relation}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{formatDate(link.createdAt)}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(link.parentArtifactId)}
                      className="h-6 w-6 p-0"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Current Node */}
        <div className="flex justify-center">
          <div className="flex items-center gap-2 p-4 border-2 border-primary rounded-lg bg-primary/5">
            <GitBranch className="h-4 w-4 text-primary" />
            <span className="font-mono text-sm font-medium">{artifactId}</span>
            <Badge variant="default">Current</Badge>
          </div>
        </div>
        
        {/* Children Section */}
        {children.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <ArrowDown className="h-4 w-4" />
              Children ({children.length})
            </div>
            <div className="space-y-2">
              {children.map((link) => (
                <div key={link.id} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-2 flex-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="font-mono text-sm">{link.childArtifactId}</span>
                    <Badge className={getRelationColor(link.relation)}>
                      {link.relation}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{formatDate(link.createdAt)}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(link.childArtifactId)}
                      className="h-6 w-6 p-0"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Legend */}
        <div className="pt-4 border-t">
          <div className="text-xs text-muted-foreground mb-2">Relation Types:</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(RELATION_COLORS).filter(([key]) => key !== 'default').map(([relation, colorClass]) => (
              <div key={relation} className="flex items-center gap-1">
                <Badge className={colorClass} variant="outline">
                  {relation}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
