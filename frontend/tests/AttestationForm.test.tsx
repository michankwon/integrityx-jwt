/**
 * Tests for AttestationForm component
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AttestationForm } from '@/components/attestations/AttestationForm'

// Mock the toast module
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('AttestationForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders collapsed form initially', () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    expect(screen.getByText('Add Attestation')).toBeInTheDocument()
    expect(screen.queryByText('Add New Attestation')).not.toBeInTheDocument()
  })

  it('expands form when Add Attestation is clicked', () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    expect(screen.getByText('Add New Attestation')).toBeInTheDocument()
    expect(screen.getByText('Attestation Kind *')).toBeInTheDocument()
    expect(screen.getByText('Issued By *')).toBeInTheDocument()
    expect(screen.getByText('Details (JSON) *')).toBeInTheDocument()
  })

  it('collapses form when Cancel is clicked', () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    expect(screen.getByText('Add New Attestation')).toBeInTheDocument()
    
    // Collapse form
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    
    expect(screen.queryByText('Add New Attestation')).not.toBeInTheDocument()
    expect(screen.getByText('Add Attestation')).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Try to submit without filling fields
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Attestation kind is required')).toBeInTheDocument()
      expect(screen.getByText('Issued by is required')).toBeInTheDocument()
      expect(screen.getByText('Details are required')).toBeInTheDocument()
    })
  })

  it('validates JSON format in details field', async () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in valid data but invalid JSON
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: 'invalid json' } })
    
    // Try to submit
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Details must be valid JSON')).toBeInTheDocument()
    })
  })

  it('submits form successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { id: 1, kind: 'qc_check' }
      })
    } as Response)

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: '{"score": 95, "notes": "test"}' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/attestations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          artifactId: 'test-artifact-1',
          etid: 'ATTESTATION_ETID_001',
          kind: 'qc_check',
          issuedBy: 'test_user',
          details: { score: 95, notes: 'test' }
        })
      })
    })
    
    expect(mockToast.success).toHaveBeenCalledWith('Attestation created successfully!')
  })

  it('handles API errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: '{"score": 95}' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to create attestation: Network error')).toBeInTheDocument()
    })
    
    expect(mockToast.error).toHaveBeenCalledWith('Failed to create attestation: Network error')
  })

  it('handles API error responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({
        ok: false,
        error: { message: 'Invalid data' }
      })
    } as Response)

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: '{"score": 95}' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to create attestation: Invalid data')).toBeInTheDocument()
    })
  })

  it('auto-fills example details based on kind selection', async () => {
    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Select KYC kind
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'kyc_passed' } })
    
    // Check that details are auto-filled
    const detailsTextarea = screen.getByDisplayValue(/verification_method/)
    expect(detailsTextarea).toHaveValue(
      JSON.stringify({
        verification_method: "document_scan",
        confidence_level: "high",
        documents_verified: ["passport", "utility_bill"],
        timestamp: expect.any(String)
      }, null, 2)
    )
  })

  it('dispatches attestation created event on success', async () => {
    const mockDispatchEvent = jest.fn()
    global.dispatchEvent = mockDispatchEvent

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { id: 1, kind: 'qc_check' }
      })
    } as Response)

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: '{"score": 95}' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockDispatchEvent).toHaveBeenCalledWith(
        new CustomEvent('attestationCreated', { detail: { artifactId: 'test-artifact-1' } })
      )
    })
  })

  it('shows loading state during submission', async () => {
    // Mock a slow response
    mockFetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({ ok: true, data: { id: 1 } })
        } as Response), 100)
      )
    )

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    const detailsTextarea = screen.getByDisplayValue(/score.*95/)
    fireEvent.change(detailsTextarea, { target: { value: '{"score": 95}' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    // Check loading state
    expect(screen.getByText('Creating...')).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
    
    await waitFor(() => {
      expect(screen.queryByText('Creating...')).not.toBeInTheDocument()
    })
  })

  it('resets form after successful submission', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { id: 1, kind: 'qc_check' }
      })
    } as Response)

    render(<AttestationForm artifactId="test-artifact-1" />)
    
    // Expand form
    const addButton = screen.getByText('Add Attestation')
    fireEvent.click(addButton)
    
    // Fill in form data
    const kindSelect = screen.getByDisplayValue('')
    fireEvent.change(kindSelect, { target: { value: 'qc_check' } })
    
    const issuedByInput = screen.getByDisplayValue('current_user')
    fireEvent.change(issuedByInput, { target: { value: 'test_user' } })
    
    // Submit form
    const submitButton = screen.getByText('Create Attestation')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      // Form should be collapsed after success
      expect(screen.queryByText('Add New Attestation')).not.toBeInTheDocument()
      expect(screen.getByText('Add Attestation')).toBeInTheDocument()
    })
  })
})
