/**
 * Tests for DisclosureButton component
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { DisclosureButton } from '@/components/proof/DisclosureButton'

// Mock the toast module
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('DisclosureButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders download button with correct text', () => {
    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    expect(screen.getByText('Download Disclosure Pack')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('is disabled when no artifact ID is provided', () => {
    render(<DisclosureButton artifactId="" />)
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('shows loading state during download', async () => {
    // Mock a slow response
    mockFetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          headers: new Headers({
            'content-type': 'application/zip',
            'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
          }),
          blob: () => Promise.resolve(new Blob(['test content']))
        } as Response), 100)
      )
    )

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    // Check loading state
    expect(screen.getByText('Generating Pack...')).toBeInTheDocument()
    expect(button).toBeDisabled()
    
    await waitFor(() => {
      expect(screen.queryByText('Generating Pack...')).not.toBeInTheDocument()
    })
  })

  it('shows success state after successful download', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Downloaded!')).toBeInTheDocument()
    })
    
    expect(mockToast.success).toHaveBeenCalledWith('Disclosure pack downloaded successfully!')
  })

  it('handles network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to download disclosure pack: Network error')).toBeInTheDocument()
    })
    
    expect(mockToast.error).toHaveBeenCalledWith('Failed to download disclosure pack: Network error')
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

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to download disclosure pack: Artifact not found')).toBeInTheDocument()
    })
  })

  it('handles non-ZIP response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/json'
      }),
      json: async () => ({ ok: true, data: {} })
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to download disclosure pack: Response is not a ZIP file')).toBeInTheDocument()
    })
  })

  it('extracts filename from Content-Disposition header', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="custom_disclosure_pack.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Downloaded!')).toBeInTheDocument()
    })
    
    // Check that document.createElement was called with correct download attribute
    expect(document.createElement).toHaveBeenCalledWith('a')
  })

  it('uses default filename when Content-Disposition is missing', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Downloaded!')).toBeInTheDocument()
    })
  })

  it('creates and triggers download link', async () => {
    const mockClick = jest.fn()
    const mockAppendChild = jest.fn()
    const mockRemoveChild = jest.fn()
    
    const mockElement = {
      href: '',
      download: '',
      style: { display: '' },
      click: mockClick,
    }
    
    ;(document.createElement as jest.Mock).mockReturnValue(mockElement)
    ;(document.body.appendChild as jest.Mock).mockImplementation(mockAppendChild)
    ;(document.body.removeChild as jest.Mock).mockImplementation(mockRemoveChild)

    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(document.createElement).toHaveBeenCalledWith('a')
      expect(mockElement.download).toBe('disclosure_test-artifact-1.zip')
      expect(mockAppendChild).toHaveBeenCalledWith(mockElement)
      expect(mockClick).toHaveBeenCalled()
      expect(mockRemoveChild).toHaveBeenCalledWith(mockElement)
    })
  })

  it('cleans up object URL after download', async () => {
    const mockRevokeObjectURL = jest.fn()
    global.URL.revokeObjectURL = mockRevokeObjectURL

    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('mock-url')
    })
  })

  it('resets success state after timeout', async () => {
    jest.useFakeTimers()

    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Downloaded!')).toBeInTheDocument()
    })
    
    // Fast-forward time
    jest.advanceTimersByTime(2000)
    
    await waitFor(() => {
      expect(screen.queryByText('Downloaded!')).not.toBeInTheDocument()
      expect(screen.getByText('Download Disclosure Pack')).toBeInTheDocument()
    })
    
    jest.useRealTimers()
  })

  it('shows help text', () => {
    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    expect(screen.getByText(/Downloads a ZIP file containing proof, artifact details, attestations, audit events, and manifest/)).toBeInTheDocument()
  })

  it('handles clipboard errors gracefully', async () => {
    // Mock clipboard error
    const mockWriteText = jest.fn().mockRejectedValue(new Error('Clipboard error'))
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: mockWriteText },
      writable: true,
    })

    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename="disclosure_test-artifact-1.zip"'
      }),
      blob: () => Promise.resolve(new Blob(['test content']))
    } as Response)

    render(<DisclosureButton artifactId="test-artifact-1" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    // Should still complete successfully despite clipboard error
    await waitFor(() => {
      expect(screen.getByText('Downloaded!')).toBeInTheDocument()
    })
  })
})
