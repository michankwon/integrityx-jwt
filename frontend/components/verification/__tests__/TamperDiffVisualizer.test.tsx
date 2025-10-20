import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TamperDiffVisualizer } from '../TamperDiffVisualizer';

const mockTamperDiffData = {
  originalHash: 'original_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
  currentHash: 'modified_hash_1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
  differences: [
    {
      type: 'content' as const,
      field: 'loan_amount',
      originalValue: '$500,000',
      currentValue: '$750,000',
      severity: 'critical' as const,
      description: 'Critical financial data has been altered. The loan amount was increased by $250,000.'
    },
    {
      type: 'metadata' as const,
      field: 'borrower_name',
      originalValue: 'John Smith',
      currentValue: 'John A. Smith',
      severity: 'medium' as const,
      description: 'Borrower name has been modified with additional middle initial.'
    }
  ],
  tamperEvidence: {
    timestamp: new Date().toISOString(),
    location: 'Document content section',
    method: 'Content modification detected via hash comparison',
    confidence: 0.95
  },
  blockchainProof: {
    originalTxId: 'WAL_TX_1234567890abcdef',
    currentTxId: 'WAL_TX_abcdef1234567890',
    blockHeight: 1234567,
    verificationStatus: 'failed' as const
  }
};

describe('TamperDiffVisualizer', () => {
  it('renders tamper detection analysis when visible', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    expect(screen.getByText('Tamper Detection Analysis')).toBeInTheDocument();
    expect(screen.getByText('Document integrity compromised. 2 difference(s) detected.')).toBeInTheDocument();
  });

  it('shows security alert for tampered documents', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    expect(screen.getByText(/Security Alert:/)).toBeInTheDocument();
    expect(screen.getByText(/This document has been tampered with/)).toBeInTheDocument();
  });

  it('displays hash comparison', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    expect(screen.getByText('Original Hash (Blockchain)')).toBeInTheDocument();
    expect(screen.getByText('Current Hash (Tampered)')).toBeInTheDocument();
    expect(screen.getByText(mockTamperDiffData.originalHash)).toBeInTheDocument();
    expect(screen.getByText(mockTamperDiffData.currentHash)).toBeInTheDocument();
  });

  it('shows differences with severity levels', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    expect(screen.getByText('loan_amount')).toBeInTheDocument();
    expect(screen.getByText('borrower_name')).toBeInTheDocument();
    expect(screen.getByText('critical')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
  });

  it('allows expanding difference details', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    const expandButtons = screen.getAllByRole('button', { name: /expand/i });
    expect(expandButtons).toHaveLength(2);

    fireEvent.click(expandButtons[0]);
    
    expect(screen.getByText('Original Value:')).toBeInTheDocument();
    expect(screen.getByText('Current Value:')).toBeInTheDocument();
  });

  it('shows tamper evidence details', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    // Click on Tamper Evidence tab
    fireEvent.click(screen.getByText('Tamper Evidence'));

    expect(screen.getByText('Detection Time:')).toBeInTheDocument();
    expect(screen.getByText('Location:')).toBeInTheDocument();
    expect(screen.getByText('Method:')).toBeInTheDocument();
    expect(screen.getByText('Confidence:')).toBeInTheDocument();
  });

  it('shows blockchain proof details', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    // Click on Blockchain Proof tab
    fireEvent.click(screen.getByText('Blockchain Proof'));

    expect(screen.getByText('Original TX ID:')).toBeInTheDocument();
    expect(screen.getByText('Current TX ID:')).toBeInTheDocument();
    expect(screen.getByText('Block Height:')).toBeInTheDocument();
    expect(screen.getByText('Verification Status:')).toBeInTheDocument();
  });

  it('provides download report functionality', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={true} 
      />
    );

    expect(screen.getByText('Download Report')).toBeInTheDocument();
  });

  it('shows toggle button when not visible', () => {
    render(
      <TamperDiffVisualizer 
        diffData={mockTamperDiffData} 
        isVisible={false} 
      />
    );

    expect(screen.getByText('Show Tamper Analysis')).toBeInTheDocument();
    expect(screen.queryByText('Tamper Detection Analysis')).not.toBeInTheDocument();
  });
});

