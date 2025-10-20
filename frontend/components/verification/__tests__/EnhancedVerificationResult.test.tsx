import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { EnhancedVerificationResult } from '../EnhancedVerificationResult';

const mockValidResult = {
  is_valid: true,
  message: 'Document verification successful',
  artifact_id: 'artifact_123',
  details: {
    created_at: '2024-01-15T10:30:00Z',
    hash: 'valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
    etid: 100001
  }
};

const mockTamperedResult = {
  is_valid: false,
  message: 'Document verification failed - tampering detected',
  artifact_id: 'artifact_456',
  details: {
    created_at: '2024-01-15T10:30:00Z',
    hash: 'original_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
    etid: 100001
  }
};

describe('EnhancedVerificationResult', () => {
  it('renders success message for valid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    expect(screen.getByText('Document Verification Successful')).toBeInTheDocument();
    expect(screen.getByText('Document verification successful')).toBeInTheDocument();
    expect(screen.getByText(/This document has been verified as authentic/)).toBeInTheDocument();
  });

  it('shows verification status grid for valid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    expect(screen.getByText('Hash Matches')).toBeInTheDocument();
    expect(screen.getByText('No Tampering')).toBeInTheDocument();
    expect(screen.getByText('Borrower Data Intact')).toBeInTheDocument();
  });

  it('renders failure message for tampered documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    expect(screen.getByText('Document Verification Failed')).toBeInTheDocument();
    expect(screen.getByText('Document verification failed - tampering detected')).toBeInTheDocument();
    expect(screen.getByText(/This document has been tampered with/)).toBeInTheDocument();
  });

  it('shows hash comparison for tampered documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    expect(screen.getByText('Original Hash (Blockchain)')).toBeInTheDocument();
    expect(screen.getByText('Current Hash (Tampered)')).toBeInTheDocument();
  });

  it('displays blockchain details for valid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    // Click on Blockchain Proof tab
    fireEvent.click(screen.getByText('Blockchain Proof'));

    expect(screen.getByText('Document Hash:')).toBeInTheDocument();
    expect(screen.getByText('Entity Type ID:')).toBeInTheDocument();
    expect(screen.getByText('Sealed Date:')).toBeInTheDocument();
    expect(screen.getByText('Verification Status:')).toBeInTheDocument();
  });

  it('shows document metadata for valid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    // Click on Document Metadata tab
    fireEvent.click(screen.getByText('Document Metadata'));

    expect(screen.getByText('Artifact ID:')).toBeInTheDocument();
    expect(screen.getByText('Created:')).toBeInTheDocument();
    expect(screen.getByText('Hash Algorithm:')).toBeInTheDocument();
  });

  it('displays verification timeline for valid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    // Click on Verification Timeline tab
    fireEvent.click(screen.getByText('Verification Timeline'));

    expect(screen.getByText('Document Sealed')).toBeInTheDocument();
    expect(screen.getByText('Hash Verification')).toBeInTheDocument();
  });

  it('provides download functionality', () => {
    render(
      <EnhancedVerificationResult 
        result={mockValidResult} 
        currentHash="valid_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
      />
    );

    expect(screen.getByText('Download Report')).toBeInTheDocument();
  });

  it('shows tamper analysis for invalid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        showTamperAnalysis={true}
      />
    );

    // The tamper analysis should be visible for tampered documents
    expect(screen.getByText('Tamper Detection Analysis')).toBeInTheDocument();
  });

  it('shows visual comparison for invalid documents', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        showVisualComparison={true}
      />
    );

    // The visual comparison should be visible for tampered documents
    expect(screen.getByText('Visual Document Comparison')).toBeInTheDocument();
  });

  it('hides tamper analysis when disabled', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        showTamperAnalysis={false}
      />
    );

    expect(screen.queryByText('Tamper Detection Analysis')).not.toBeInTheDocument();
  });

  it('hides visual comparison when disabled', () => {
    render(
      <EnhancedVerificationResult 
        result={mockTamperedResult} 
        currentHash="modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        showVisualComparison={false}
      />
    );

    expect(screen.queryByText('Visual Document Comparison')).not.toBeInTheDocument();
  });
});

