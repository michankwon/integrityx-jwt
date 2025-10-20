'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, FileText, CheckCircle, AlertCircle, Upload, Sparkles } from 'lucide-react'
import { toast } from '@/components/ui/toast'

interface ExtractedData {
  documentType: string
  loanId?: string
  borrowerName?: string
  propertyAddress?: string
  amount?: string
  rate?: string
  term?: string
  confidence: number
}

interface SmartUploadFormProps {
  onUpload: (formData: FormData) => Promise<void>
  isUploading: boolean
}

export default function SmartUploadForm({ onUpload, isUploading }: SmartUploadFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [formData, setFormData] = useState({
    loanId: '',
    documentType: '',
    borrowerName: '',
    propertyAddress: '',
    amount: '',
    rate: '',
    term: '',
    notes: ''
  })

  // Auto-populate form when data is extracted
  useEffect(() => {
    if (extractedData) {
      setFormData(prev => ({
        ...prev,
        loanId: extractedData.loanId || prev.loanId,
        documentType: extractedData.documentType || prev.documentType,
        borrowerName: extractedData.borrowerName || prev.borrowerName,
        propertyAddress: extractedData.propertyAddress || prev.propertyAddress,
        amount: extractedData.amount || prev.amount,
        rate: extractedData.rate || prev.rate,
        term: extractedData.term || prev.term
      }))
    }
  }, [extractedData])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0]
    if (selectedFile) {
      setFile(selectedFile)
      setExtractedData(null)
      
      // Start extraction process
      setIsExtracting(true)
      try {
        await extractDocumentData(selectedFile)
      } catch (error) {
        console.error('Extraction failed:', error)
        toast.error('Failed to extract document data')
      } finally {
        setIsExtracting(false)
      }
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const extractDocumentData = async (file: File) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch('http://localhost:8000/api/extract-document-data', {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        setExtractedData(result.data)
        toast.success('Document data extracted successfully!')
      } else {
        throw new Error('Extraction failed')
      }
    } catch (error) {
      console.error('Extraction error:', error)
      toast.error('Failed to extract document data')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      toast.error('Please select a file first')
      return
    }

    const uploadFormData = new FormData()
    uploadFormData.append('file', file)
    uploadFormData.append('loan_id', formData.loanId)
    uploadFormData.append('document_type', formData.documentType)
    uploadFormData.append('borrower_name', formData.borrowerName)
    uploadFormData.append('property_address', formData.propertyAddress)
    uploadFormData.append('amount', formData.amount)
    uploadFormData.append('rate', formData.rate)
    uploadFormData.append('term', formData.term)
    uploadFormData.append('notes', formData.notes)
    uploadFormData.append('created_by', 'user') // This should come from auth context

    await onUpload(uploadFormData)
  }

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'pdf':
        return '📄'
      case 'docx':
      case 'doc':
        return '📝'
      case 'xlsx':
      case 'xls':
        return '📊'
      case 'jpg':
      case 'jpeg':
      case 'png':
        return '🖼️'
      case 'json':
        return '📋'
      default:
        return '📁'
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Smart Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            Smart Document Upload
          </CardTitle>
          <CardDescription>
            Upload your document and let AI automatically extract key information
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* File Drop Zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            {isDragActive ? (
              <p className="text-lg">Drop the file here...</p>
            ) : (
              <div>
                <p className="text-lg mb-2">Drag & drop a document here, or click to select</p>
                <p className="text-sm text-gray-500">
                  Supports PDF, Word, Excel, JSON, images, and text files (max 50MB)
                </p>
              </div>
            )}
          </div>

          {/* Selected File */}
          {file && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getFileIcon(file.name)}</span>
                <div className="flex-1">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {isExtracting && (
                  <div className="flex items-center gap-2 text-blue-600">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Extracting data...</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Extracted Data Preview */}
          {extractedData && (
            <Alert className="mt-4">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p className="font-medium">Document data extracted successfully!</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">
                      Type: {extractedData.documentType}
                    </Badge>
                    {extractedData.loanId && (
                      <Badge variant="outline">
                        Loan ID: {extractedData.loanId}
                      </Badge>
                    )}
                    {extractedData.borrowerName && (
                      <Badge variant="outline">
                        Borrower: {extractedData.borrowerName}
                      </Badge>
                    )}
                    {extractedData.amount && (
                      <Badge variant="outline">
                        Amount: ${extractedData.amount}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    Confidence: {Math.round(extractedData.confidence * 100)}%
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Smart Form */}
      <Card>
        <CardHeader>
          <CardTitle>Document Information</CardTitle>
          <CardDescription>
            Review and edit the automatically extracted information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Loan ID */}
              <div className="space-y-2">
                <Label htmlFor="loanId">Loan ID *</Label>
                <Input
                  id="loanId"
                  value={formData.loanId}
                  onChange={(e) => setFormData(prev => ({ ...prev, loanId: e.target.value }))}
                  placeholder="e.g., LOAN_2024_001"
                  required
                />
              </div>

              {/* Document Type */}
              <div className="space-y-2">
                <Label htmlFor="documentType">Document Type *</Label>
                <Input
                  id="documentType"
                  value={formData.documentType}
                  onChange={(e) => setFormData(prev => ({ ...prev, documentType: e.target.value }))}
                  placeholder="e.g., loan_application"
                  required
                />
              </div>

              {/* Borrower Name */}
              <div className="space-y-2">
                <Label htmlFor="borrowerName">Borrower Name</Label>
                <Input
                  id="borrowerName"
                  value={formData.borrowerName}
                  onChange={(e) => setFormData(prev => ({ ...prev, borrowerName: e.target.value }))}
                  placeholder="e.g., John Smith"
                />
              </div>

              {/* Property Address */}
              <div className="space-y-2">
                <Label htmlFor="propertyAddress">Property Address</Label>
                <Input
                  id="propertyAddress"
                  value={formData.propertyAddress}
                  onChange={(e) => setFormData(prev => ({ ...prev, propertyAddress: e.target.value }))}
                  placeholder="e.g., 123 Main St, City, State"
                />
              </div>

              {/* Loan Amount */}
              <div className="space-y-2">
                <Label htmlFor="amount">Loan Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                  placeholder="e.g., 250000"
                />
              </div>

              {/* Interest Rate */}
              <div className="space-y-2">
                <Label htmlFor="rate">Interest Rate (%)</Label>
                <Input
                  id="rate"
                  type="number"
                  step="0.01"
                  value={formData.rate}
                  onChange={(e) => setFormData(prev => ({ ...prev, rate: e.target.value }))}
                  placeholder="e.g., 6.5"
                />
              </div>

              {/* Loan Term */}
              <div className="space-y-2">
                <Label htmlFor="term">Loan Term (months)</Label>
                <Input
                  id="term"
                  type="number"
                  value={formData.term}
                  onChange={(e) => setFormData(prev => ({ ...prev, term: e.target.value }))}
                  placeholder="e.g., 360"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Any additional information about this document..."
                rows={3}
              />
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={!file || isUploading}
                className="min-w-[120px]"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
