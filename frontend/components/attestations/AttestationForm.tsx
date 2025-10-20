"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Plus, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'react-hot-toast'

interface AttestationFormProps {
  readonly artifactId: string
  readonly currentUser?: string
  readonly className?: string
}

interface AttestationFormData {
  kind: string
  issuedBy: string
  details: string
}

const COMMON_ATTESTATION_KINDS = [
  { value: 'qc_check', label: 'Quality Check' },
  { value: 'kyc_passed', label: 'KYC Verification' },
  { value: 'policy_ok', label: 'Policy Compliance' },
  { value: 'audit_complete', label: 'Audit Complete' },
  { value: 'approval_granted', label: 'Approval Granted' },
  { value: 'compliance_verified', label: 'Compliance Verified' },
  { value: 'risk_assessed', label: 'Risk Assessment' },
  { value: 'custom', label: 'Custom' }
]

const EXAMPLE_JSON = {
  score: 95,
  notes: "Quality check passed with high confidence",
  checker: "automated_system",
  timestamp: new Date().toISOString()
}

async function createAttestation(data: {
  artifactId: string
  kind: string
  issuedBy: string
  details: Record<string, any>
}): Promise<any> {
  const response = await fetch('/api/attestations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      artifactId: data.artifactId,
      etid: 'ATTESTATION_ETID_001', // Default ETID
      kind: data.kind,
      issuedBy: data.issuedBy,
      details: data.details
    })
  })
  
  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`)
  }
  
  const apiResponse = await response.json()
  
  if (!apiResponse.ok) {
    throw new Error(apiResponse.error?.message || 'Failed to create attestation')
  }
  
  return apiResponse.data
}

export function AttestationForm({ artifactId, currentUser = 'current_user', className }: AttestationFormProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)
  const [formData, setFormData] = React.useState<AttestationFormData>({
    kind: '',
    issuedBy: currentUser,
    details: JSON.stringify(EXAMPLE_JSON, null, 2)
  })
  const [errors, setErrors] = React.useState<Partial<AttestationFormData>>({})
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [apiError, setApiError] = React.useState<string | null>(null)
  
  const validateForm = (): boolean => {
    const newErrors: Partial<AttestationFormData> = {}
    
    if (!formData.kind.trim()) {
      newErrors.kind = 'Attestation kind is required'
    }
    
    if (!formData.issuedBy.trim()) {
      newErrors.issuedBy = 'Issued by is required'
    }
    
    if (!formData.details.trim()) {
      newErrors.details = 'Details are required'
    } else {
      try {
        JSON.parse(formData.details)
      } catch {
        newErrors.details = 'Details must be valid JSON'
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setIsSubmitting(true)
    setApiError(null)
    
    try {
      const parsedDetails = JSON.parse(formData.details)
      await createAttestation({
        artifactId,
        kind: formData.kind,
        issuedBy: formData.issuedBy,
        details: parsedDetails
      })
      
      toast.success('Attestation created successfully!')
      setFormData({
        kind: '',
        issuedBy: currentUser,
        details: JSON.stringify(EXAMPLE_JSON, null, 2)
      })
      setErrors({})
      setIsExpanded(false)
      
      // Trigger a refresh of the attestation list by dispatching a custom event
      window.dispatchEvent(new CustomEvent('attestationCreated', { detail: { artifactId } }))
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create attestation'
      setApiError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleKindChange = (value: string) => {
    setFormData(prev => ({ ...prev, kind: value }))
    
    // Auto-fill example details based on kind
    let exampleDetails = {}
    if (value === 'qc_check') {
      exampleDetails = {
        score: 95,
        notes: "Quality check passed with high confidence",
        checker: "automated_system",
        timestamp: new Date().toISOString()
      }
    } else if (value === 'kyc_passed') {
      exampleDetails = {
        verification_method: "document_scan",
        confidence_level: "high",
        documents_verified: ["passport", "utility_bill"],
        timestamp: new Date().toISOString()
      }
    } else if (value === 'policy_ok') {
      exampleDetails = {
        policy_version: "v2.1",
        compliance_score: 100,
        checked_by: "policy_engine",
        timestamp: new Date().toISOString()
      }
    } else if (value === 'custom') {
      exampleDetails = {
        custom_field: "custom_value",
        notes: "Custom attestation details",
        timestamp: new Date().toISOString()
      }
    }
    
    if (Object.keys(exampleDetails).length > 0) {
      setFormData(prev => ({ 
        ...prev, 
        details: JSON.stringify(exampleDetails, null, 2) 
      }))
    }
  }
  
  if (!isExpanded) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="p-6">
          <Button
            onClick={() => setIsExpanded(true)}
            className="w-full"
            variant="outline"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Attestation
          </Button>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5" />
          Add New Attestation
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Kind Selection */}
          <div className="space-y-2">
            <Label htmlFor="kind">Attestation Kind *</Label>
            <Select onValueChange={handleKindChange} value={formData.kind}>
              <SelectTrigger>
                <SelectValue placeholder="Select attestation kind" />
              </SelectTrigger>
              <SelectContent>
                {COMMON_ATTESTATION_KINDS.map((kind) => (
                  <SelectItem key={kind.value} value={kind.value}>
                    {kind.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.kind && (
              <p className="text-sm text-destructive">{errors.kind}</p>
            )}
          </div>
          
          {/* Issued By */}
          <div className="space-y-2">
            <Label htmlFor="issuedBy">Issued By *</Label>
            <Input
              id="issuedBy"
              value={formData.issuedBy}
              onChange={(e) => setFormData(prev => ({ ...prev, issuedBy: e.target.value }))}
              placeholder="Enter issuer name or ID"
              className={cn(errors.issuedBy && "border-destructive")}
            />
            {errors.issuedBy && (
              <p className="text-sm text-destructive">{errors.issuedBy}</p>
            )}
          </div>
          
          {/* Details JSON */}
          <div className="space-y-2">
            <Label htmlFor="details">Details (JSON) *</Label>
            <Textarea
              id="details"
              value={formData.details}
              onChange={(e) => setFormData(prev => ({ ...prev, details: e.target.value }))}
              placeholder="Enter JSON details..."
              rows={8}
              className={cn(
                "font-mono text-sm",
                errors.details && "border-destructive"
              )}
            />
            {errors.details && (
              <p className="text-sm text-destructive">{errors.details}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Enter valid JSON for attestation details. The system will auto-fill examples based on the selected kind.
            </p>
          </div>
          
          {/* API Error Display */}
          {apiError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {apiError}
              </AlertDescription>
            </Alert>
          )}
          
          {/* Form Actions */}
          <div className="flex gap-2 pt-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Create Attestation
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsExpanded(false)
                setFormData({
                  kind: '',
                  issuedBy: currentUser,
                  details: JSON.stringify(EXAMPLE_JSON, null, 2)
                })
                setErrors({})
                setApiError(null)
              }}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
