/**
 * Tests for AttestationList component
 */

import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { AttestationList } from '@/components/attestations/AttestationList'

// Mock the toast module
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('AttestationList', () => {
  const mockAttestations = [
    {
      id: 1,
      artifactId: 'test-artifact-1',
      etid: 'ATTESTATION_ETID_001',
      kind: 'qc_check',
      issuedBy: 'quality_team',
      details: { score: 95, notes: 'High quality' },
      createdAt: '2024-01-01T10:00:00Z'
    },
    {
      id: 2,
      artifactId: 'test-artifact-1',
      etid: 'ATTESTATION_ETID_001',
      kind: 'kyc_passed',
      issuedBy: 'compliance_team',
      details: { verified: true, method: 'document_scan' },
      createdAt: '2024-01-01T11:00:00Z'
    }
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading state initially', () => {
    render(<AttestationList artifactId="test-artifact-1" />)
    
    expect(screen.getByText('Attestations')).toBeInTheDocument()
    expect(screen.getByText('Generating Pack...')).toBeInTheDocument()
  })

  it('renders attestations list when data is loaded', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: mockAttestations }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('qc_check')).toBeInTheDocument()
      expect(screen.getByText('kyc_passed')).toBeInTheDocument()
      expect(screen.getByText('quality_team')).toBeInTheDocument()
      expect(screen.getByText('compliance_team')).toBeInTheDocument()
    })

    expect(screen.getByText('2')).toBeInTheDocument() // Badge count
  })

  it('renders empty state when no attestations exist', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: [] }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('No attestations found')).toBeInTheDocument()
      expect(screen.getByText("This artifact doesn't have any attestations yet.")).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load attestations: Network error')).toBeInTheDocument()
      expect(screen.getByText('Try Again')).toBeInTheDocument()
    })
  })

  it('handles API error responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({
        ok: false,
        error: { message: 'Artifact not found' }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load attestations: Artifact not found')).toBeInTheDocument()
    })
  })

  it('expands and collapses attestation details', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: [mockAttestations[0]] }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('qc_check')).toBeInTheDocument()
    })

    // Click expand button
    const expandButton = screen.getByLabelText('Expand details')
    fireEvent.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText('Details')).toBeInTheDocument()
      expect(screen.getByText('Copy JSON')).toBeInTheDocument()
    })

    // Click collapse button
    const collapseButton = screen.getByLabelText('Collapse details')
    fireEvent.click(collapseButton)

    await waitFor(() => {
      expect(screen.queryByText('Details')).not.toBeInTheDocument()
    })
  })

  it('copies JSON details to clipboard', async () => {
    const mockWriteText = jest.fn()
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: mockWriteText },
      writable: true,
    })

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: [mockAttestations[0]] }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('qc_check')).toBeInTheDocument()
    })

    // Expand details
    const expandButton = screen.getByLabelText('Expand details')
    fireEvent.click(expandButton)

    await waitFor(() => {
      expect(screen.getByText('Copy JSON')).toBeInTheDocument()
    })

    // Click copy button
    const copyButton = screen.getByText('Copy JSON')
    fireEvent.click(copyButton)

    expect(mockWriteText).toHaveBeenCalledWith(
      JSON.stringify(mockAttestations[0].details, null, 2)
    )
  })

  it('refreshes data when refresh button is clicked', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          data: { attestations: [mockAttestations[0]] }
        })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          data: { attestations: mockAttestations }
        })
      } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('qc_check')).toBeInTheDocument()
    })

    // Click refresh button
    const refreshButton = screen.getByText('Refresh')
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(screen.getByText('kyc_passed')).toBeInTheDocument()
    })

    expect(mockFetch).toHaveBeenCalledTimes(2)
  })

  it('listens for attestation creation events', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: [] }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('No attestations found')).toBeInTheDocument()
    })

    // Dispatch attestation created event
    const event = new CustomEvent('attestationCreated', {
      detail: { artifactId: 'test-artifact-1' }
    })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2)
    })
  })

  it('ignores attestation creation events for different artifacts', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        data: { attestations: [] }
      })
    } as Response)

    render(<AttestationList artifactId="test-artifact-1" />)

    await waitFor(() => {
      expect(screen.getByText('No attestations found')).toBeInTheDocument()
    })

    // Dispatch event for different artifact
    const event = new CustomEvent('attestationCreated', {
      detail: { artifactId: 'different-artifact' }
    })
    window.dispatchEvent(event)

    // Should not trigger additional fetch
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })
})

