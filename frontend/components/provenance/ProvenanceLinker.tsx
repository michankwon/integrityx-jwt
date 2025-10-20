"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Plus, AlertCircle, Loader2, Link, ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'react-hot-toast'

interface ProvenanceLinkerProps {
  readonly artifactId: string
  readonly className?: string
}

interface ProvenanceLink {
  id: number
  parentArtifactId: string
  childArtifactId: string
  relation: string
  createdAt: string
}

const RELATION_TYPES = [
  { value: 'contains', label: 'Contains', description: 'Parent contains child' },
  { value: 'derived_from', label: 'Derived From', description: 'Child derived from parent' },
  { value: 'supersedes', label: 'Supersedes', description: 'Child replaces parent' },
  { value: 'references', label: 'References', description: 'Child references parent' },
  { value: 'validates', label: 'Validates', description: 'Child validates parent' }
]

async function createProvenanceLink(data: {
  parentArtifactId: string
  childArtifactId: string
  relation: string
}): Promise<ProvenanceLink> {
  const response = await fetch('/api/provenance/link', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`)
  }
  
  const apiResponse = await response.json()
  
  if (!apiResponse.ok) {
    throw new Error(apiResponse.error?.message || 'Failed to create provenance link')
  }
  
  return apiResponse.data
}

export function ProvenanceLinker({ artifactId, className }: ProvenanceLinkerProps) {
  const [activeTab, setActiveTab] = React.useState<'child' | 'parent'>('child')
  const [childArtifactId, setChildArtifactId] = React.useState('')
  const [parentArtifactId, setParentArtifactId] = React.useState('')
  const [relation, setRelation] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  
  // Load last-linked IDs from URL params
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const lastChildId = urlParams.get('lastChildId')
    const lastParentId = urlParams.get('lastParentId')
    
    if (lastChildId) setChildArtifactId(lastChildId)
    if (lastParentId) setParentArtifactId(lastParentId)
  }, [])
  
  const validateArtifactId = (id: string): boolean => {
    return id.trim().length > 0
  }
  
  const updateUrlParams = (childId?: string, parentId?: string) => {
    const url = new URL(window.location.href)
    if (childId) url.searchParams.set('lastChildId', childId)
    if (parentId) url.searchParams.set('lastParentId', parentId)
    window.history.replaceState({}, '', url.toString())
  }
  
  const handleAddChild = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateArtifactId(childArtifactId)) {
      setError('Please enter a valid child artifact ID')
      return
    }
    
    if (!relation) {
      setError('Please select a relation type')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      await createProvenanceLink({
        parentArtifactId: artifactId,
        childArtifactId: childArtifactId.trim(),
        relation
      })
      
      toast.success('Child link created successfully!')
      updateUrlParams(childArtifactId.trim())
      
      // Reset form
      setChildArtifactId('')
      setRelation('')
      
      // Trigger refresh of lineage graph
      window.dispatchEvent(new CustomEvent('provenanceLinkCreated', { 
        detail: { artifactId, type: 'child' } 
      }))
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create child link'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleAddParent = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateArtifactId(parentArtifactId)) {
      setError('Please enter a valid parent artifact ID')
      return
    }
    
    if (!relation) {
      setError('Please select a relation type')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      await createProvenanceLink({
        parentArtifactId: parentArtifactId.trim(),
        childArtifactId: artifactId,
        relation
      })
      
      toast.success('Parent link created successfully!')
      updateUrlParams(undefined, parentArtifactId.trim())
      
      // Reset form
      setParentArtifactId('')
      setRelation('')
      
      // Trigger refresh of lineage graph
      window.dispatchEvent(new CustomEvent('provenanceLinkCreated', { 
        detail: { artifactId, type: 'parent' } 
      }))
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create parent link'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Link className="h-5 w-5" />
          Provenance Linking
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'child' | 'parent')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="child" className="flex items-center gap-2">
              <ArrowDown className="h-4 w-4" />
              Add Child
            </TabsTrigger>
            <TabsTrigger value="parent" className="flex items-center gap-2">
              <ArrowUp className="h-4 w-4" />
              Add Parent
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="child" className="space-y-4 mt-4">
            <div className="text-sm text-muted-foreground">
              Link a child artifact that is related to the current artifact ({artifactId})
            </div>
            
            <form onSubmit={handleAddChild} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="childArtifactId">Child Artifact ID *</Label>
                <Input
                  id="childArtifactId"
                  value={childArtifactId}
                  onChange={(e) => setChildArtifactId(e.target.value)}
                  placeholder="Enter child artifact ID"
                  className={cn(error && !validateArtifactId(childArtifactId) && "border-destructive")}
                />
                <p className="text-xs text-muted-foreground">
                  The artifact that will be linked as a child
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="childRelation">Relation Type *</Label>
                <Select value={relation} onValueChange={setRelation}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select relation type" />
                  </SelectTrigger>
                  <SelectContent>
                    {RELATION_TYPES.map((rel) => (
                      <SelectItem key={rel.value} value={rel.value}>
                        <div>
                          <div className="font-medium">{rel.label}</div>
                          <div className="text-xs text-muted-foreground">{rel.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  How the child relates to the current artifact
                </p>
              </div>
              
              <Button
                type="submit"
                disabled={isSubmitting || !childArtifactId.trim() || !relation}
                className="w-full"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating Link...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Child Link
                  </>
                )}
              </Button>
            </form>
          </TabsContent>
          
          <TabsContent value="parent" className="space-y-4 mt-4">
            <div className="text-sm text-muted-foreground">
              Link a parent artifact that the current artifact ({artifactId}) is related to
            </div>
            
            <form onSubmit={handleAddParent} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="parentArtifactId">Parent Artifact ID *</Label>
                <Input
                  id="parentArtifactId"
                  value={parentArtifactId}
                  onChange={(e) => setParentArtifactId(e.target.value)}
                  placeholder="Enter parent artifact ID"
                  className={cn(error && !validateArtifactId(parentArtifactId) && "border-destructive")}
                />
                <p className="text-xs text-muted-foreground">
                  The artifact that will be linked as a parent
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="parentRelation">Relation Type *</Label>
                <Select value={relation} onValueChange={setRelation}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select relation type" />
                  </SelectTrigger>
                  <SelectContent>
                    {RELATION_TYPES.map((rel) => (
                      <SelectItem key={rel.value} value={rel.value}>
                        <div>
                          <div className="font-medium">{rel.label}</div>
                          <div className="text-xs text-muted-foreground">{rel.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  How the current artifact relates to the parent
                </p>
              </div>
              
              <Button
                type="submit"
                disabled={isSubmitting || !parentArtifactId.trim() || !relation}
                className="w-full"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating Link...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Parent Link
                  </>
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
        
        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
