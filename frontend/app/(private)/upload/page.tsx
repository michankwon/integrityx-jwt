'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AccessibleDropzone } from '@/components/ui/accessible-dropzone';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Loader2, Upload, FileText, CheckCircle, ExternalLink, Hash, Shield, ArrowLeft, ChevronDown, ChevronUp, User, HelpCircle, AlertCircle, X, RefreshCw, Mail, Download } from 'lucide-react';
import { simpleToast as toast } from '@/components/ui/simple-toast';
import { sealLoanDocument, sealLoanDocumentMaximumSecurity, sealLoanDocumentQuantumSafe, type LoanData, type BorrowerInfo } from '@/lib/api/loanDocuments';
import { 
  sanitizeText, 
  sanitizeEmail, 
  sanitizePhone, 
  sanitizeNumber, 
  sanitizeDate, 
  sanitizeSSNLast4, 
  sanitizeZipCode, 
  sanitizeAddress, 
  sanitizeCity, 
  sanitizeState, 
  sanitizeCountry, 
  sanitizeEmploymentStatus, 
  sanitizeGovernmentIdType, 
  sanitizeDocumentType, 
  sanitizeNotes,
  sanitizeFormData
} from '@/utils/dataSanitization';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface UploadResult {
  artifactId: string;
  walacorTxId: string;
  sealedAt: string;
  proofBundle: any;
}

interface VerifyResult {
  is_valid: boolean;
  status: string;
  artifact_id: string;
  verified_at: string;
  details: {
    stored_hash: string;
    provided_hash: string;
    artifact_type: string;
    created_at: string;
  };
}

interface ApiResponse<T = any> {
  ok: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

interface KYCData {
  // Personal Information
  fullLegalName: string;
  dateOfBirth: string;
  phoneNumber: string;
  emailAddress: string;
  
  // Address Information
  streetAddress1: string;
  streetAddress2: string;
  city: string;
  stateProvince: string;
  postalZipCode: string;
  country: string;
  
  // Identification Information
  citizenshipCountry: string;
  identificationType: string;
  identificationNumber: string;
  idIssuingCountry: string;
  
  // Financial Information
  sourceOfFunds: string;
  purposeOfLoan: string;
  expectedMonthlyTransactionVolume: number;
  expectedNumberOfMonthlyTransactions: number;
  
  // Compliance Screening
  isPEP: string;
  pepDetails: string;
  
  // Document Uploads
  governmentIdFile: File | null;
  proofOfAddressFile: File | null;
}

interface KYCErrors {
  [key: string]: string;
}

interface ValidationError {
  field: string;
  message: string;
}

interface UploadError {
  type: 'validation' | 'network' | 'server' | 'walacor' | 'file' | 'unknown';
  message: string;
  details?: any;
  retryable?: boolean;
}

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: UploadError | null;
  validationErrors: ValidationError[];
  canRetry: boolean;
  savedData: any;
}


export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileHash, setFileHash] = useState<string>('');
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [metadata, setMetadata] = useState('');
  const [etid, setEtid] = useState('100002');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Enhanced error handling state
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    validationErrors: [],
    canRetry: false,
    savedData: null
  });
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [showValidationSummary, setShowValidationSummary] = useState(false);
  const [maximumSecurityMode, setMaximumSecurityMode] = useState(false); // Default to standard security
  const [quantumSafeMode, setQuantumSafeMode] = useState(false); // Quantum-safe mode
  const [isAutoFilling, setIsAutoFilling] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0);

  // Individual form field states for better reactivity
  const [formData, setFormData] = useState({
    loanId: '',
    documentType: 'loan_application',
    loanAmount: '',
    borrowerName: '',
    additionalNotes: '',
    borrowerFullName: '',
    borrowerDateOfBirth: '',
    borrowerEmail: '',
    borrowerPhone: '',
    borrowerStreetAddress: '',
    borrowerCity: '',
    borrowerState: '',
    borrowerZipCode: '',
    borrowerCountry: 'US',
    borrowerSSNLast4: '',
    borrowerGovernmentIdType: 'drivers_license',
    borrowerIdNumberLast4: '',
    borrowerEmploymentStatus: 'employed',
    borrowerAnnualIncome: '',
    borrowerCoBorrowerName: ''
  });

  // Debug: Log formData changes
  useEffect(() => {
    console.log('📊 formData state changed:', formData);
  }, [formData]);

  // Helper function to get current metadata values
  const getMetadataValue = (key: string): string => {
    try {
      const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};
      return currentMeta[key] || '';
    } catch (error) {
      console.error('Error parsing metadata:', error);
      return '';
    }
  };


  // KYC State
  const [kycData, setKycData] = useState<KYCData>({
    fullLegalName: '',
    dateOfBirth: '',
    phoneNumber: '',
    emailAddress: '',
    streetAddress1: '',
    streetAddress2: '',
    city: '',
    stateProvince: '',
    postalZipCode: '',
    country: 'US',
    citizenshipCountry: 'US',
    identificationType: '',
    identificationNumber: '',
    idIssuingCountry: 'US',
    sourceOfFunds: '',
    purposeOfLoan: '',
    expectedMonthlyTransactionVolume: 0,
    expectedNumberOfMonthlyTransactions: 0,
    isPEP: '',
    pepDetails: '',
    governmentIdFile: null,
    proofOfAddressFile: null,
  });
  const [kycErrors, setKycErrors] = useState<KYCErrors>({});
  const [isKycExpanded, setIsKycExpanded] = useState(false);
  const [isSavingKyc, setIsSavingKyc] = useState(false);
  const [kycSaved, setKycSaved] = useState(false);
  const [privacyNoticeDismissed, setPrivacyNoticeDismissed] = useState(false);
  const [borrowerErrors, setBorrowerErrors] = useState<Record<string, string>>({});

  // Check localStorage for privacy notice dismissal on component mount
  useEffect(() => {
    const dismissed = localStorage.getItem('privacy-notice-dismissed');
    if (dismissed === 'true') {
      setPrivacyNoticeDismissed(true);
    }
  }, []);

  // Handle privacy notice dismissal
  const handleDismissPrivacyNotice = () => {
    setPrivacyNoticeDismissed(true);
    localStorage.setItem('privacy-notice-dismissed', 'true');
  };

  // Borrower field validation
  const validateBorrowerField = (field: string, value: string): string => {
    switch (field) {
      case 'borrowerFullName':
        if (!value.trim()) return 'Full name is required';
        if (value.trim().length < 2) return 'Full name must be at least 2 characters';
        return '';
      
      case 'borrowerDateOfBirth':
        if (!value) return 'Date of birth is required';
        const birthDate = new Date(value);
        const today = new Date();
        if (isNaN(birthDate.getTime())) return 'Please enter a valid date';
        if (birthDate > today) return 'Date of birth cannot be in the future';
        return '';
      
      case 'borrowerEmail':
        if (!value.trim()) return 'Email address is required';
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) return 'Please enter a valid email address';
        return '';
      
      case 'borrowerPhone':
        if (!value.trim()) return 'Phone number is required';
        // Accept any phone format (US or international)
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) return 'Please enter a valid phone number';
        return '';
      
      case 'borrowerSSNLast4':
        if (!value.trim()) return 'SSN last 4 digits is required';
        if (!/^\d{4}$/.test(value)) return 'SSN must be exactly 4 digits';
        return '';
      
      case 'borrowerIdNumberLast4':
        if (!value.trim()) return 'ID number last 4 digits is required';
        if (!/^\d{4}$/.test(value)) return 'ID number must be exactly 4 digits';
        return '';
      
      case 'borrowerAnnualIncome':
        if (!value.trim()) return 'Annual income is required';
        const income = parseFloat(value);
        if (isNaN(income) || income <= 0) return 'Annual income must be a positive number';
        return '';
      
      case 'borrowerStreetAddress':
        if (!value.trim()) return 'Street address is required';
        return '';
      
      case 'borrowerCity':
        if (!value.trim()) return 'City is required';
        return '';
      
      case 'borrowerState':
        if (!value.trim()) return 'State is required';
        return '';
      
      case 'borrowerZipCode':
        if (!value.trim()) return 'ZIP code is required';
        return '';
      
      case 'borrowerCountry':
        if (!value.trim()) return 'Country is required';
        return '';
      
      case 'borrowerEmploymentStatus':
        if (!value.trim()) return 'Employment status is required';
        return '';
      
      default:
        return '';
    }
  };

  // Handle borrower field changes with validation and sanitization
  const handleBorrowerFieldChange = (field: string, value: string) => {
    // Sanitize the input based on field type
    let sanitizedValue = value;
    
    switch (field) {
      case 'borrowerFullName':
      case 'borrowerCoBorrowerName':
        sanitizedValue = sanitizeText(value);
        break;
      case 'borrowerEmail':
        sanitizedValue = sanitizeEmail(value);
        break;
      case 'borrowerPhone':
        sanitizedValue = sanitizePhone(value);
        break;
      case 'borrowerDateOfBirth':
        sanitizedValue = sanitizeDate(value);
        break;
      case 'borrowerStreetAddress':
        sanitizedValue = sanitizeAddress(value);
        break;
      case 'borrowerCity':
        sanitizedValue = sanitizeCity(value);
        break;
      case 'borrowerState':
        sanitizedValue = sanitizeState(value);
        break;
      case 'borrowerZipCode':
        sanitizedValue = sanitizeZipCode(value);
        break;
      case 'borrowerCountry':
        sanitizedValue = sanitizeCountry(value);
        break;
      case 'borrowerSSNLast4':
      case 'borrowerIdNumberLast4':
        sanitizedValue = sanitizeSSNLast4(value);
        break;
      case 'borrowerGovernmentIdType':
        sanitizedValue = sanitizeGovernmentIdType(value);
        break;
      case 'borrowerEmploymentStatus':
        sanitizedValue = sanitizeEmploymentStatus(value);
        break;
      case 'borrowerAnnualIncome':
        sanitizedValue = sanitizeNumber(value);
        break;
      default:
        sanitizedValue = sanitizeText(value);
    }
    
    const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};
    const updatedMeta = { ...currentMeta, [field]: sanitizedValue };
    setMetadata(JSON.stringify(updatedMeta, null, 2));
    
    // Validate the sanitized field
    const error = validateBorrowerField(field, sanitizedValue);
    setBorrowerErrors(prev => ({
      ...prev,
      [field]: error
    }));
  };

  // Auto-fill form data from JSON file
  const autoFillFromJSON = async (file: File): Promise<void> => {
    try {
      console.log('🚀 autoFillFromJSON function called with file:', file.name);
      setIsAutoFilling(true);
      const text = await file.text();
      console.log('📄 File text content:', text.substring(0, 200) + '...');
      const jsonData = JSON.parse(text);
      
      console.log('📄 Auto-filling form from JSON:', jsonData);
      
      // Extract loan information
      const loanId = jsonData.loan_id || jsonData.loanId || '';
      const documentType = jsonData.document_type || jsonData.documentType || 'loan_application';
      const loanAmount = jsonData.loan_amount || jsonData.loanAmount || 0;
      const borrowerName = jsonData.borrower_name || jsonData.borrowerName || '';
      const additionalNotes = jsonData.additional_notes || jsonData.additionalNotes || '';
      
      // Extract borrower information
      const borrower = jsonData.borrower || {};
      const fullName = borrower.full_name || borrower.fullName || '';
      const email = borrower.email || '';
      const phone = borrower.phone || '';
      const dateOfBirth = borrower.date_of_birth || borrower.dateOfBirth || '';
      
      // Extract address information
      const address = borrower.address || {};
      const streetAddress = address.street || address.street_address || '';
      const city = address.city || '';
      const state = address.state || '';
      const zipCode = address.zip_code || address.zipCode || '';
      const country = address.country || 'US';
      
      // Extract identity information
      const ssnLast4 = borrower.ssn_last4 || borrower.ssnLast4 || '';
      const idType = borrower.id_type || borrower.idType || 'drivers_license';
      const idLast4 = borrower.id_last4 || borrower.idLast4 || '';
      
      // Extract financial information
      const employmentStatus = borrower.employment_status || borrower.employmentStatus || 'employed';
      const annualIncome = borrower.annual_income || borrower.annualIncome || 0;
      const coBorrowerName = borrower.co_borrower_name || borrower.coBorrowerName || '';
      
      console.log('📄 Extracted loan data:', { loanId, documentType, loanAmount, borrowerName, additionalNotes });
      console.log('📄 Extracted borrower data:', { fullName, email, phone, dateOfBirth, streetAddress, city, state, zipCode, country, ssnLast4, idType, idLast4, employmentStatus, annualIncome, coBorrowerName });
      
      // Create updated metadata object with sanitized data
      const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};
      const updatedMeta = {
        ...currentMeta,
        // Loan information (sanitized)
        loanId: sanitizeText(loanId || currentMeta.loanId),
        documentType: sanitizeDocumentType(documentType || currentMeta.documentType),
        loanAmount: sanitizeNumber((loanAmount || currentMeta.loanAmount)?.toString()),
        borrowerName: sanitizeText(borrowerName || currentMeta.borrowerName),
        additionalNotes: sanitizeNotes(additionalNotes || currentMeta.additionalNotes),
        
        // Borrower information (sanitized)
        borrowerFullName: sanitizeText(fullName || currentMeta.borrowerFullName),
        borrowerEmail: sanitizeEmail(email || currentMeta.borrowerEmail),
        borrowerPhone: sanitizePhone(phone || currentMeta.borrowerPhone),
        borrowerDateOfBirth: sanitizeDate(dateOfBirth || currentMeta.borrowerDateOfBirth),
        borrowerStreetAddress: sanitizeAddress(streetAddress || currentMeta.borrowerStreetAddress),
        borrowerCity: sanitizeCity(city || currentMeta.borrowerCity),
        borrowerState: sanitizeState(state || currentMeta.borrowerState),
        borrowerZipCode: sanitizeZipCode(zipCode || currentMeta.borrowerZipCode),
        borrowerCountry: sanitizeCountry(country || currentMeta.borrowerCountry),
        borrowerSSNLast4: sanitizeSSNLast4(ssnLast4 || currentMeta.borrowerSSNLast4),
        borrowerGovernmentIdType: sanitizeGovernmentIdType(idType || currentMeta.borrowerGovernmentIdType),
        borrowerIdNumberLast4: sanitizeSSNLast4(idLast4 || currentMeta.borrowerIdNumberLast4),
        borrowerEmploymentStatus: sanitizeEmploymentStatus(employmentStatus || currentMeta.borrowerEmploymentStatus),
        borrowerAnnualIncome: sanitizeNumber((annualIncome || currentMeta.borrowerAnnualIncome)?.toString()),
        borrowerCoBorrowerName: sanitizeText(coBorrowerName || currentMeta.borrowerCoBorrowerName)
      };
      
      // Update both metadata state and form data state
      console.log('🔄 Updating metadata and formData with:', updatedMeta);
      setMetadata(JSON.stringify(updatedMeta, null, 2));
      setFormData(updatedMeta);
      console.log('✅ formData state updated');
      
      // Also update KYC data state
      setKycData({
        fullLegalName: updatedMeta.borrowerFullName || '',
        dateOfBirth: updatedMeta.borrowerDateOfBirth || '',
        phoneNumber: updatedMeta.borrowerPhone || '',
        emailAddress: updatedMeta.borrowerEmail || '',
        streetAddress1: updatedMeta.borrowerStreetAddress || '',
        streetAddress2: '',
        city: updatedMeta.borrowerCity || '',
        stateProvince: updatedMeta.borrowerState || '',
        postalZipCode: updatedMeta.borrowerZipCode || '',
        country: updatedMeta.borrowerCountry || 'US',
        citizenshipCountry: updatedMeta.borrowerCountry || 'US',
        identificationType: updatedMeta.borrowerGovernmentIdType || 'drivers_license',
        identificationNumber: updatedMeta.borrowerIdNumberLast4 || '',
        idIssuingCountry: updatedMeta.borrowerCountry || 'US',
        sourceOfFunds: 'Employment Income',
        purposeOfLoan: updatedMeta.additionalNotes || '',
        expectedMonthlyTransactionVolume: '',
        expectedNumberOfMonthlyTransactions: '',
        isPep: false,
        pepDetails: '',
        governmentIdFile: null,
        proofOfAddressFile: null
      });
      
                  console.log('✅ KYC data state updated');
      
      // Force a re-render by updating a dummy state
      setForceUpdate(prev => prev + 1);
      
      // Show success message with count of fields filled
      const filledFields = Object.values(updatedMeta).filter(value => 
        value && value !== '' && value !== 0
      ).length;
      
      console.log('📄 Updated metadata:', updatedMeta);
      console.log('📄 Updated formData:', updatedMeta);
      console.log('📄 Filled fields count:', filledFields);
      
      toast.success(`✅ Auto-filled ${filledFields} fields from JSON file!`);
      
    } catch (error) {
      console.error('Error auto-filling from JSON:', error);
      toast.error('Failed to auto-fill form from JSON file. Please check file format.');
    } finally {
      setIsAutoFilling(false);
    }
  };

  // Calculate file hash on client side
  const calculateFileHash = async (file: File): Promise<string> => {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  // Create comprehensive document object for sealing
  const createComprehensiveDocument = (): any => {
    const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};
    
    // Extract loan information
    const loanData = {
      loan_id: currentMeta.loanId || `loan-${Date.now()}`,
      document_type: currentMeta.documentType || 'unknown',
      loan_amount: currentMeta.loanAmount || 0,
      borrower_name: currentMeta.borrowerName || '',
      notes: currentMeta.notes || '',
      etid: etid
    };

    // Extract borrower information
    const borrowerData = {
      full_name: currentMeta.borrowerFullName || '',
      dob: currentMeta.borrowerDateOfBirth || '',
      email: currentMeta.borrowerEmail || '',
      phone: currentMeta.borrowerPhone || '',
      address: {
        street: currentMeta.borrowerStreetAddress || '',
        city: currentMeta.borrowerCity || '',
        state: currentMeta.borrowerState || '',
        zip_code: currentMeta.borrowerZipCode || '',
        country: currentMeta.borrowerCountry || 'US'
      },
      ssn_last4: currentMeta.borrowerSSNLast4 || '',
      id_type: currentMeta.borrowerGovernmentIdType || '',
      id_last4: currentMeta.borrowerIdNumberLast4 || '',
      employment_status: currentMeta.borrowerEmploymentStatus || '',
      annual_income: currentMeta.borrowerAnnualIncome || 0,
      co_borrower_name: currentMeta.borrowerCoBorrowerName || ''
    };

    // Create comprehensive document object
    const comprehensiveDocument = {
      ...loanData,
      borrower: borrowerData,
      uploaded_files: file ? [{
        filename: file.name,
        file_type: file.type,
        file_size: file.size,
        file_hash: fileHash
      }] : [],
      metadata: {
        source: 'frontend_upload',
        timestamp: new Date().toISOString(),
        version: '1.0'
      }
    };

    return comprehensiveDocument;
  };

  // Calculate comprehensive hash including borrower information
  const calculateComprehensiveHash = async (): Promise<string> => {
    const comprehensiveDoc = createComprehensiveDocument();
    const jsonString = JSON.stringify(comprehensiveDoc, null, 2);
    const encoder = new TextEncoder();
    const data = encoder.encode(jsonString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  // Check if document is already sealed
  const checkIfAlreadySealed = async (hash: string, etid: string): Promise<VerifyResult | null> => {
    try {
      const response = await fetch('http://localhost:8000/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          etid: parseInt(etid),
          payloadHash: hash
        })
      });

      if (!response.ok) {
        // If verification fails (document not found), return null
        return null;
      }

      const apiResponse: ApiResponse<VerifyResult> = await response.json();
      
      if (apiResponse.ok && apiResponse.data) {
        return apiResponse.data;
      }
      
      return null;
    } catch (error) {
      console.error('Verification check error:', error);
      return null;
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    alert('onDrop function called with files: ' + acceptedFiles.length);
    console.log('Files dropped:', acceptedFiles);
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      alert('File selected: ' + selectedFile.name + ', Type: ' + selectedFile.type);
      console.log('Selected file:', selectedFile.name, selectedFile.type, selectedFile.size);
      setFile(selectedFile);
      setUploadResult(null);
      setVerifyResult(null);
      
      // Calculate hash
      try {
        const hash = await calculateFileHash(selectedFile);
        setFileHash(hash);
        console.log('File hash calculated:', hash);
        toast.success('File hash calculated successfully');
        
        // Auto-fill form data from JSON file if it's a JSON file
        if (selectedFile.type === 'application/json' || selectedFile.name.endsWith('.json')) {
          console.log('🔍 JSON file detected, calling autoFillFromJSON...');
          await autoFillFromJSON(selectedFile);
        } else {
          console.log('🔍 Not a JSON file, skipping auto-fill. File type:', selectedFile.type, 'File name:', selectedFile.name);
        }
        
        // Check if document is already sealed
        setIsVerifying(true);
        const existingVerify = await checkIfAlreadySealed(hash, etid);
        setIsVerifying(false);
        
        if (existingVerify && existingVerify.is_valid) {
          setVerifyResult(existingVerify);
          toast.success('Document already sealed!');
        }
      } catch (error) {
        toast.error('Failed to calculate file hash');
        console.error('Hash calculation error:', error);
      }
    }
  }, [etid]);

  // File acceptance configuration
  const fileAccept = {
    'application/pdf': ['.pdf'],
    'application/json': ['.json'],
    'text/plain': ['.txt'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    alert('handleFileSelect function called!');
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      alert('File selected: ' + selectedFile.name + ', Type: ' + selectedFile.type);
      setFile(selectedFile);
      setUploadResult(null);
      setVerifyResult(null);
      
      // Calculate hash
      try {
        const hash = await calculateFileHash(selectedFile);
        setFileHash(hash);
        toast.success('File hash calculated successfully');
        
        // Auto-fill form data from JSON file if it's a JSON file
        if (selectedFile.type === 'application/json' || selectedFile.name.endsWith('.json')) {
          console.log('🔍 JSON file detected, calling autoFillFromJSON...');
          await autoFillFromJSON(selectedFile);
        } else {
          console.log('🔍 Not a JSON file, skipping auto-fill. File type:', selectedFile.type, 'File name:', selectedFile.name);
        }
        
        // Check if document is already sealed
        setIsVerifying(true);
        const existingVerify = await checkIfAlreadySealed(hash, etid);
        setIsVerifying(false);
        
        if (existingVerify && existingVerify.is_valid) {
          setVerifyResult(existingVerify);
          toast.success('Document already sealed!');
        }
      } catch (error) {
        toast.error('Failed to calculate file hash');
        console.error('Hash calculation error:', error);
      }
    }
  };


  const handleUpload = async () => {
    console.log('Upload button clicked');
    
    // Clear previous errors
    setUploadState(prev => ({ ...prev, error: null, validationErrors: [] }));
    
    // Validate form first
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setUploadState(prev => ({ 
        ...prev, 
        validationErrors,
        error: {
          type: 'validation',
          message: `Please fix ${validationErrors.length} error${validationErrors.length > 1 ? 's' : ''} before submitting`,
          retryable: false
        }
      }));
      setShowValidationSummary(true);
      return;
    }

    if (!file || !fileHash) {
      console.log('No file or hash available');
      toast.error('Please select a file first');
      return;
    }

    console.log('Starting upload for file:', file.name);
    
    // Save form data before upload
    saveFormData();
    
    // Update upload state
    setUploadState(prev => ({
      ...prev,
      isUploading: true,
      progress: 0,
      error: null,
      canRetry: false
    }));
    
    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Get raw metadata and sanitize it
      const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};
      
      // Prepare raw data for sanitization
      const rawLoanData = {
        loanId: currentMeta.loanId || `loan-${Date.now()}`,
        documentType: currentMeta.documentType || 'loan_application',
        loanAmount: currentMeta.loanAmount || 0,
        borrowerName: currentMeta.borrowerFullName || currentMeta.borrowerName || '',
        additionalNotes: currentMeta.notes || '',
        createdBy: 'user@example.com' // TODO: Get from auth context
      };

      const rawBorrowerData = {
        fullName: currentMeta.borrowerFullName || '',
        dateOfBirth: currentMeta.borrowerDateOfBirth || '',
        email: currentMeta.borrowerEmail || '',
        phone: currentMeta.borrowerPhone || '',
        streetAddress: currentMeta.borrowerStreetAddress || '',
        city: currentMeta.borrowerCity || '',
        state: currentMeta.borrowerState || '',
        zipCode: currentMeta.borrowerZipCode || '',
        country: currentMeta.borrowerCountry || 'US',
        ssnLast4: currentMeta.borrowerSSNLast4 || '',
        governmentIdType: currentMeta.borrowerGovernmentIdType || 'drivers_license',
        idNumberLast4: currentMeta.borrowerIdNumberLast4 || '',
        employmentStatus: currentMeta.borrowerEmploymentStatus || 'employed',
        annualIncome: currentMeta.borrowerAnnualIncome || 0,
        coBorrowerName: currentMeta.borrowerCoBorrowerName || ''
      };

      // Sanitize all form data
      const sanitizedData = sanitizeFormData(rawLoanData, rawBorrowerData);
      
      if (!sanitizedData.isValid) {
        toast.error(`Validation errors: ${sanitizedData.errors.join(', ')}`);
        return;
      }

      // Create final loan data object
      const loanData: LoanData = {
        loan_id: sanitizedData.loanData.loanId,
        document_type: sanitizedData.loanData.documentType,
        loan_amount: parseFloat(sanitizedData.loanData.loanAmount),
        borrower_name: sanitizedData.loanData.borrowerName,
        additional_notes: sanitizedData.loanData.additionalNotes,
        created_by: sanitizedData.loanData.createdBy
      };

      // Create final borrower data object
      const borrowerInfo: BorrowerInfo = {
        full_name: sanitizedData.borrowerData.fullName,
        date_of_birth: sanitizedData.borrowerData.dateOfBirth,
        email: sanitizedData.borrowerData.email,
        phone: sanitizedData.borrowerData.phone,
        address_line1: sanitizedData.borrowerData.streetAddress,
        address_line2: currentMeta.borrowerStreetAddress2 || '', // Keep as is for now
        city: sanitizedData.borrowerData.city,
        state: sanitizedData.borrowerData.state,
        zip_code: sanitizedData.borrowerData.zipCode,
        country: sanitizedData.borrowerData.country,
        ssn_last4: sanitizedData.borrowerData.ssnLast4,
        id_type: sanitizedData.borrowerData.governmentIdType,
        id_last4: sanitizedData.borrowerData.idNumberLast4,
        employment_status: sanitizedData.borrowerData.employmentStatus,
        annual_income_range: sanitizedData.borrowerData.annualIncome,
        co_borrower_name: sanitizedData.borrowerData.coBorrowerName,
        is_sealed: false,
        walacor_tx_id: '',
        seal_timestamp: ''
      };

      console.log('Loan data:', loanData);
      console.log('Borrower info:', borrowerInfo);

      toast.loading('Sealing loan document with borrower information...');

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadState(prev => {
          const newProgress = Math.min(prev.progress + 10, 90);
          return { ...prev, progress: newProgress };
        });
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

        // Use the appropriate API client based on security mode
        let sealResponse;
        if (quantumSafeMode) {
          sealResponse = await sealLoanDocumentQuantumSafe(loanData, borrowerInfo, [file]);
        } else if (maximumSecurityMode) {
          sealResponse = await sealLoanDocumentMaximumSecurity(loanData, borrowerInfo, [file]);
        } else {
          sealResponse = await sealLoanDocument(loanData, borrowerInfo, [file]);
        }
      
      clearInterval(progressInterval);
      
      console.log('Seal response:', sealResponse);

      // Complete progress
      setUploadState(prev => ({ ...prev, progress: 100 }));
      setUploadProgress(100);

      // Create UploadResult for compatibility with existing UI
      const uploadResult: UploadResult = {
        artifactId: sealResponse.artifact_id,
        walacorTxId: sealResponse.walacor_tx_id,
        sealedAt: sealResponse.sealed_at,
        proofBundle: sealResponse.blockchain_proof || {}
      };

      setUploadResult(uploadResult);
      
      // Clear saved data on success
      clearSavedData();
      
      // Show success modal with confetti effect
      setShowSuccessModal(true);
      toast.success('Loan document sealed successfully with borrower information!');

    } catch (error) {
      console.error('Upload error:', error);
      
      const uploadError = handleError(error, 'sealLoanDocument');
      
      setUploadState(prev => ({
        ...prev,
        error: uploadError,
        canRetry: uploadError.retryable || false
      }));
      
      // Show error modal for serious errors
      if (uploadError.type === 'server' || uploadError.type === 'network') {
        setShowErrorModal(true);
      }
      
      toast.error(uploadError.message);
      
    } finally {
      setUploadState(prev => ({ ...prev, isUploading: false }));
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Retry upload function
  const handleRetry = async () => {
    setUploadState(prev => ({ ...prev, error: null, canRetry: false }));
    await handleUpload();
  };

  // Helper function to get income range
  const getIncomeRange = (annualIncome: number): string => {
    if (annualIncome < 25000) return "Under $25,000";
    if (annualIncome < 50000) return "$25,000 - $49,999";
    if (annualIncome < 75000) return "$50,000 - $74,999";
    if (annualIncome < 100000) return "$75,000 - $99,999";
    if (annualIncome < 150000) return "$100,000 - $149,999";
    if (annualIncome < 200000) return "$150,000 - $199,999";
    if (annualIncome < 300000) return "$200,000 - $299,999";
    if (annualIncome < 500000) return "$300,000 - $499,999";
    return "$500,000+";
  };

  // Enhanced validation function
  const validateForm = (): ValidationError[] => {
    const errors: ValidationError[] = [];
    const currentMeta = metadata ? JSON.parse(metadata || '{}') : {};

    // File validation
    if (!file) {
      errors.push({ field: 'file', message: 'Please select a file to upload' });
    } else if (file.size > 50 * 1024 * 1024) { // 50MB limit
      errors.push({ field: 'file', message: 'File size must be less than 50MB' });
    }

    // Loan data validation
    if (!currentMeta.loanId?.trim()) {
      errors.push({ field: 'loanId', message: 'Loan ID is required' });
    }
    if (!currentMeta.loanAmount || currentMeta.loanAmount <= 0) {
      errors.push({ field: 'loanAmount', message: 'Valid loan amount is required' });
    }
    if (!currentMeta.borrowerFullName?.trim()) {
      errors.push({ field: 'borrowerFullName', message: 'Borrower full name is required' });
    }

    // Borrower information validation
    if (!currentMeta.borrowerEmail?.trim()) {
      errors.push({ field: 'borrowerEmail', message: 'Email address is required' });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(currentMeta.borrowerEmail)) {
      errors.push({ field: 'borrowerEmail', message: 'Please enter a valid email address' });
    }

    if (!currentMeta.borrowerPhone?.trim()) {
      errors.push({ field: 'borrowerPhone', message: 'Phone number is required' });
    }

    if (!currentMeta.borrowerDateOfBirth?.trim()) {
      errors.push({ field: 'borrowerDateOfBirth', message: 'Date of birth is required' });
      } else {
      const dob = new Date(currentMeta.borrowerDateOfBirth);
      const today = new Date();
      const age = today.getFullYear() - dob.getFullYear();
      if (age < 18) {
        errors.push({ field: 'borrowerDateOfBirth', message: 'Borrower must be at least 18 years old' });
      }
    }

    if (!currentMeta.borrowerStreetAddress?.trim()) {
      errors.push({ field: 'borrowerStreetAddress', message: 'Street address is required' });
    }

    if (!currentMeta.borrowerCity?.trim()) {
      errors.push({ field: 'borrowerCity', message: 'City is required' });
    }

    if (!currentMeta.borrowerState?.trim()) {
      errors.push({ field: 'borrowerState', message: 'State is required' });
    }

    if (!currentMeta.borrowerZipCode?.trim()) {
      errors.push({ field: 'borrowerZipCode', message: 'ZIP code is required' });
    }

    if (!currentMeta.borrowerSSNLast4?.trim()) {
      errors.push({ field: 'borrowerSSNLast4', message: 'SSN last 4 digits are required' });
    } else if (!/^\d{4}$/.test(currentMeta.borrowerSSNLast4)) {
      errors.push({ field: 'borrowerSSNLast4', message: 'SSN last 4 digits must be exactly 4 numbers' });
    }

    if (!currentMeta.borrowerAnnualIncome || currentMeta.borrowerAnnualIncome <= 0) {
      errors.push({ field: 'borrowerAnnualIncome', message: 'Valid annual income is required' });
    }

    return errors;
  };

  // Error handling utilities
  const handleError = (error: any, context: string = 'upload'): UploadError => {
    console.error(`Error in ${context}:`, error);

    if (error.name === 'NetworkError' || error.message?.includes('fetch')) {
      return {
        type: 'network',
        message: 'Network error. Please check your connection and try again.',
        details: error,
        retryable: true
      };
    }

    if (error.response?.status >= 500) {
      return {
        type: 'server',
        message: 'Something went wrong on our end. Please try again or contact support.',
        details: error.response?.data,
        retryable: true
      };
    }

    if (error.response?.status === 400) {
      return {
        type: 'validation',
        message: error.response?.data?.error || 'Please check your input and try again.',
        details: error.response?.data,
        retryable: false
      };
    }

    if (error.message?.includes('walacor') || error.message?.includes('blockchain')) {
      return {
        type: 'walacor',
        message: 'Blockchain sealing failed. Document saved locally with pending seal status.',
        details: error,
        retryable: true
      };
    }

    return {
      type: 'unknown',
      message: error.message || 'An unexpected error occurred. Please try again.',
      details: error,
      retryable: true
    };
  };

  // Save form data to localStorage
  const saveFormData = () => {
    const formData = {
      file: file ? { name: file.name, size: file.size, type: file.type } : null,
      metadata,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('uploadFormData', JSON.stringify(formData));
  };

  // Load form data from localStorage
  const loadFormData = () => {
    const saved = localStorage.getItem('uploadFormData');
    if (saved) {
      try {
        const formData = JSON.parse(saved);
        setMetadata(formData.metadata || '');
        return formData;
      } catch (e) {
        console.error('Failed to load saved form data:', e);
      }
    }
    return null;
  };

  // Clear saved form data
  const clearSavedData = () => {
    localStorage.removeItem('uploadFormData');
  };

  // Get field error message
  const getFieldError = (fieldName: string): string => {
    const error = uploadState.validationErrors.find(e => e.field === fieldName);
    return error ? error.message : '';
  };

  // Check if field has error
  const hasFieldError = (fieldName: string): boolean => {
    return uploadState.validationErrors.some(e => e.field === fieldName);
  };

  const handleReset = () => {
    setFile(null);
    setFileHash('');
    setUploadResult(null);
    setVerifyResult(null);
    setMetadata('');
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // KYC Functions
  const validateKYC = (): boolean => {
    const errors: KYCErrors = {};
    
    // Personal Information validation
    if (!kycData.fullLegalName.trim()) errors.fullLegalName = 'Full legal name is required';
    if (!kycData.dateOfBirth) errors.dateOfBirth = 'Date of birth is required';
    if (kycData.dateOfBirth) {
      const birthDate = new Date(kycData.dateOfBirth);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18) errors.dateOfBirth = 'Must be 18 years or older';
    }
    if (!kycData.phoneNumber.trim()) errors.phoneNumber = 'Phone number is required';
    if (kycData.phoneNumber && !/^\+1-\d{3}-\d{3}-\d{4}$/.test(kycData.phoneNumber)) {
      errors.phoneNumber = 'Phone number must be in format +1-XXX-XXX-XXXX';
    }
    if (!kycData.emailAddress.trim()) errors.emailAddress = 'Email address is required';
    if (kycData.emailAddress && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(kycData.emailAddress)) {
      errors.emailAddress = 'Please enter a valid email address';
    }
    
    // Address Information validation
    if (!kycData.streetAddress1.trim()) errors.streetAddress1 = 'Street address is required';
    if (!kycData.city.trim()) errors.city = 'City is required';
    if (!kycData.stateProvince) errors.stateProvince = 'State/Province is required';
    if (!kycData.postalZipCode.trim()) errors.postalZipCode = 'Postal/ZIP code is required';
    if (!kycData.country) errors.country = 'Country is required';
    
    // Identification Information validation
    if (!kycData.citizenshipCountry) errors.citizenshipCountry = 'Citizenship country is required';
    if (!kycData.identificationType) errors.identificationType = 'Identification type is required';
    if (!kycData.identificationNumber.trim()) errors.identificationNumber = 'Identification number is required';
    if (!kycData.idIssuingCountry) errors.idIssuingCountry = 'ID issuing country is required';
    
    // Financial Information validation
    if (!kycData.sourceOfFunds) errors.sourceOfFunds = 'Source of funds is required';
    if (!kycData.purposeOfLoan.trim()) errors.purposeOfLoan = 'Purpose of loan is required';
    if (kycData.purposeOfLoan.trim().length < 20) errors.purposeOfLoan = 'Purpose must be at least 20 characters';
    if (!kycData.expectedMonthlyTransactionVolume || kycData.expectedMonthlyTransactionVolume <= 0) {
      errors.expectedMonthlyTransactionVolume = 'Expected monthly transaction volume is required';
    }
    if (!kycData.expectedNumberOfMonthlyTransactions || kycData.expectedNumberOfMonthlyTransactions <= 0) {
      errors.expectedNumberOfMonthlyTransactions = 'Expected number of monthly transactions is required';
    }
    
    // Compliance Screening validation
    if (!kycData.isPEP) errors.isPEP = 'Please indicate if you are a Politically Exposed Person';
    if (kycData.isPEP === 'Yes' && !kycData.pepDetails.trim()) {
      errors.pepDetails = 'Please provide details about your PEP status';
    }
    
    // Document Upload validation
    if (!kycData.governmentIdFile) errors.governmentIdFile = 'Government-issued ID upload is required';
    
    setKycErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleKycFieldChange = (field: keyof KYCData, value: any) => {
    // Sanitize the input based on field type
    let sanitizedValue = value;
    
    if (typeof value === 'string') {
      switch (field) {
        case 'fullLegalName':
        case 'streetAddress1':
        case 'streetAddress2':
        case 'city':
        case 'purposeOfLoan':
        case 'pepDetails':
          sanitizedValue = sanitizeText(value);
          break;
        case 'emailAddress':
          sanitizedValue = sanitizeEmail(value);
          break;
        case 'phoneNumber':
          sanitizedValue = sanitizePhone(value);
          break;
        case 'dateOfBirth':
          sanitizedValue = sanitizeDate(value);
          break;
        case 'postalZipCode':
          sanitizedValue = sanitizeZipCode(value);
          break;
        case 'identificationNumber':
          sanitizedValue = sanitizeSSNLast4(value);
          break;
        case 'expectedMonthlyTransactionVolume':
        case 'expectedNumberOfMonthlyTransactions':
          sanitizedValue = sanitizeNumber(value.toString());
          break;
        default:
          sanitizedValue = sanitizeText(value);
      }
    }
    
    setKycData(prev => ({ ...prev, [field]: sanitizedValue }));
    // Clear error when user starts typing
    if (kycErrors[field]) {
      setKycErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSaveKyc = async () => {
    if (!validateKYC()) {
      toast.error('Please fix all validation errors before saving');
      return;
    }

    setIsSavingKyc(true);
    try {
      // Create FormData for file uploads
      const formData = new FormData();
      
      // Add all KYC data
      Object.entries(kycData).forEach(([key, value]) => {
        if (value instanceof File) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      });

      // For now, we'll simulate the API call since the endpoint doesn't exist yet
      // In a real implementation, this would call: POST /api/kyc/users/{user_id}/submit
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      setKycSaved(true);
      toast.success('KYC information saved successfully!');
    } catch (error) {
      console.error('KYC save error:', error);
      toast.error('Failed to save KYC information');
    } finally {
      setIsSavingKyc(false);
    }
  };

  // Helper function to check if KYC is complete (currently unused but available for future use)
  // const isKycComplete = () => {
  //   return Object.values(kycData).every(value => 
  //     value !== null && value !== undefined && value !== '' && 
  //     (typeof value !== 'number' || value > 0)
  //   );
  // };

  // US States data
  const usStates = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];

  const countries = ['US', 'CA', 'MX', 'GB', 'FR', 'DE', 'IT', 'ES', 'AU', 'JP', 'CN', 'IN', 'BR', 'AR', 'CL', 'CO', 'PE', 'VE', 'Other'];

  // Load saved form data on component mount
  useEffect(() => {
    const savedData = loadFormData();
    if (savedData) {
      toast.info('Previous form data restored from local storage');
    }
  }, []);

  return (
    <>
      {/* Validation Summary Modal */}
      <Dialog open={showValidationSummary} onOpenChange={setShowValidationSummary}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              Validation Errors
            </DialogTitle>
            <DialogDescription>
              Please fix the following errors before submitting your document:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {uploadState.validationErrors.map((error, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-red-800 capitalize">
                    {error.field.replace(/([A-Z])/g, ' $1').trim()}
                  </p>
                  <p className="text-sm text-red-600">{error.message}</p>
                </div>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowValidationSummary(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Error Modal */}
      <Dialog open={showErrorModal} onOpenChange={setShowErrorModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              Upload Error
            </DialogTitle>
            <DialogDescription>
              {uploadState.error?.message}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {uploadState.error?.details && (
              <div className="p-3 bg-gray-50 border rounded-lg">
                <p className="text-sm font-medium mb-2">Technical Details:</p>
                <pre className="text-xs text-gray-600 overflow-auto max-h-32">
                  {JSON.stringify(uploadState.error.details, null, 2)}
                </pre>
              </div>
            )}
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Your form data has been saved locally. You can retry the upload or contact support if the problem persists.
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setShowErrorModal(false)}>
              Close
            </Button>
            {uploadState.canRetry && (
              <Button onClick={handleRetry} className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4" />
                Retry Upload
              </Button>
            )}
            <Button variant="outline" onClick={() => {
              const errorDetails = {
                error: uploadState.error,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
              };
              const mailtoLink = `mailto:support@example.com?subject=Upload Error Report&body=${encodeURIComponent(JSON.stringify(errorDetails, null, 2))}`;
              window.open(mailtoLink);
            }} className="flex items-center gap-2">
              <Mail className="h-4 w-4" />
              Contact Support
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Success Modal */}
      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
                              <DialogTitle className="flex items-center gap-2">
                                <CheckCircle className="h-5 w-5 text-green-500" />
                                {quantumSafeMode ? 'Document Sealed with Quantum-Safe Cryptography!' : 
                                 maximumSecurityMode ? 'Document Sealed with Maximum Security!' : 'Document Sealed Successfully!'}
                              </DialogTitle>
                              <DialogDescription>
                                {quantumSafeMode 
                                  ? 'Your loan document has been sealed with QUANTUM-SAFE CRYPTOGRAPHY, providing protection against future quantum computing attacks.'
                                  : maximumSecurityMode 
                                  ? 'Your loan document has been sealed with MAXIMUM SECURITY and MINIMAL TAMPERING in the blockchain with comprehensive protection.'
                                  : 'Your loan document has been successfully sealed in the blockchain with borrower information.'
                                }
                              </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {uploadResult && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">Artifact ID</p>
                    <p className="text-sm text-green-600 font-mono">{uploadResult.artifactId}</p>
                  </div>
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm font-medium text-green-800">Transaction ID</p>
                    <p className="text-sm text-green-600 font-mono">{uploadResult.walacorTxId}</p>
                  </div>
                </div>
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm font-medium text-blue-800">Sealed At</p>
                  <p className="text-sm text-blue-600">{new Date(uploadResult.sealedAt).toLocaleString()}</p>
                </div>
                            {uploadResult.proofBundle && (
                              <div className="p-3 bg-gray-50 border rounded-lg">
                                <p className="text-sm font-medium mb-2">Blockchain Proof</p>
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className="text-xs">
                                    {uploadResult.proofBundle.blockchain_network || 'walacor'}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    ETID: {uploadResult.proofBundle.etid}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    {uploadResult.proofBundle.integrity_verified ? 'Verified' : 'Pending'}
                                  </Badge>
                                </div>
                              </div>
                            )}
                      {quantumSafeMode && uploadResult.quantum_safe_seal && (
                        <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                          <p className="text-sm font-medium mb-2 text-purple-800">🔬 Quantum-Safe Features</p>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge variant="outline" className="text-xs bg-purple-100 text-purple-800">
                                🛡️ Quantum-Resistant
                              </Badge>
                              <Badge variant="outline" className="text-xs bg-blue-100 text-blue-800">
                                🔒 Post-Quantum Secure
                              </Badge>
                              <Badge variant="outline" className="text-xs bg-yellow-100 text-yellow-800">
                                ⚡ SHA3-512 Protected
                              </Badge>
                              <Badge variant="outline" className="text-xs bg-green-100 text-green-800">
                                ⭐ Future-Proof Security
                              </Badge>
                              <Badge variant="outline" className="text-xs bg-indigo-100 text-indigo-800">
                                ✅ NIST PQC Compliant
                              </Badge>
                            </div>
                            <div className="text-xs text-purple-700">
                              <p><strong>Quantum-Resistant Hashes:</strong> {Object.keys(uploadResult.quantum_safe_seal.quantum_resistant_hashes || {}).join(', ')}</p>
                              <p><strong>Quantum-Safe Signatures:</strong> {Object.keys(uploadResult.quantum_safe_seal.quantum_safe_signatures || {}).join(', ')}</p>
                              <p><strong>Algorithms Used:</strong> {uploadResult.quantum_safe_seal.algorithms_used?.join(', ')}</p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {maximumSecurityMode && uploadResult.comprehensive_seal && (
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <p className="text-sm font-medium mb-2 text-blue-800">Maximum Security Features</p>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs bg-blue-100 text-blue-800">
                                {uploadResult.comprehensive_seal.security_level}
                              </Badge>
                              <Badge variant="outline" className="text-xs bg-green-100 text-green-800">
                                {uploadResult.comprehensive_seal.tamper_resistance}
                              </Badge>
                            </div>
                            <div className="text-xs text-blue-700">
                              <p><strong>Multi-Hash Algorithms:</strong> {uploadResult.comprehensive_seal.multi_hash_algorithms?.join(', ')}</p>
                              <p><strong>PKI Signature:</strong> {uploadResult.comprehensive_seal.pki_signature?.algorithm} ({uploadResult.comprehensive_seal.pki_signature?.key_size} bits)</p>
                              <p><strong>Verification Methods:</strong> {uploadResult.comprehensive_seal.verification_methods?.join(', ')}</p>
                            </div>
                          </div>
                        </div>
                      )}
              </div>
            )}
          </div>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setShowSuccessModal(false)}>
              Close
            </Button>
            <Button variant="outline" onClick={() => {
              setShowSuccessModal(false);
              handleReset();
            }}>
              Upload Another
            </Button>
            {uploadResult && (
              <Button onClick={() => {
                window.location.href = `/documents/${uploadResult.artifactId}`;
              }} className="flex items-center gap-2">
                <ExternalLink className="h-4 w-4" />
                View Document
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Main Upload Page */}
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <Link
            href="/dashboard"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold mb-2">Document Upload & Seal</h1>
            <p className="text-muted-foreground">
              Upload documents and seal them in the Walacor blockchain for immutable integrity verification.
            </p>
          </div>
        </div>
        
        {/* Progress Indicator */}
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span className="text-sm font-medium">KYC:</span>
            <span className={`text-sm ${kycSaved ? 'text-green-600' : 'text-orange-600'}`}>
              {kycSaved ? 'Complete ✓' : 'Incomplete'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            <span className="text-sm font-medium">Document:</span>
            <span className={`text-sm ${uploadResult ? 'text-green-600' : 'text-orange-600'}`}>
              {uploadResult ? 'Sealed ✓' : 'Pending'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              File Upload
            </CardTitle>
            <CardDescription>
              Drag and drop a file or click to select. Maximum file size: 50MB
              <br />
              <span className="text-blue-600 font-medium">💡 Tip:</span> Upload a JSON file with loan data to automatically fill the form fields below!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <AccessibleDropzone
              onDrop={onDrop}
              accept={fileAccept}
              maxFiles={1}
              maxSize={50 * 1024 * 1024} // 50MB
              description="Drag and drop a file here, or click to select. Supported formats: PDF, JSON, TXT, JPG, PNG, DOCX, XLSX"
              aria-label="File upload area for document sealing"
              id="file-upload-dropzone"
            />

            {file && (
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span className="font-medium">{file.name}</span>
                    <span className="text-sm text-muted-foreground">
                      ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                    {isAutoFilling && (
                      <div className="flex items-center space-x-1 text-sm text-blue-600">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span>Auto-filling form...</span>
                      </div>
                    )}
                  </div>
                </div>

                {fileHash && (
                  <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                    <Hash className="h-4 w-4" />
                    <span className="text-sm font-mono break-all">{fileHash}</span>
                  </div>
                )}

                {isVerifying && (
                  <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    <span className="text-sm text-blue-800">Checking if document is already sealed...</span>
                  </div>
                )}

                {verifyResult && verifyResult.is_valid && (
                  <Alert className="border-green-200 bg-green-50">
                    <Shield className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                      <div className="space-y-2">
                        <div className="font-medium">Document Already Sealed!</div>
                        <div className="text-sm">
                          This document was already sealed on{' '}
                          <span className="font-medium">
                            {new Date(verifyResult.details.created_at).toLocaleString()}
                          </span>
                        </div>
                        <div className="flex gap-2 mt-3">
                          <Button asChild size="sm">
                            <a href={`http://localhost:8000/api/verify?hash=${fileHash}`} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-3 w-3 mr-1" />
                              View Proof
                            </a>
                          </Button>
                          <Button asChild variant="outline" size="sm">
                            <a href={`http://localhost:8000/api/proof?id=${verifyResult.artifact_id}`} target="_blank" rel="noopener noreferrer">
                              <Shield className="h-3 w-3 mr-1" />
                              Download Proof Bundle
                            </a>
                          </Button>
                        </div>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

                {isUploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading...</span>
                      <span>{uploadProgress.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Borrower KYC Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Borrower KYC Information (GENIUS ACT 2025 Required)
                </CardTitle>
                <CardDescription>
                  Complete your Know Your Customer information as required by GENIUS ACT 2025
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsKycExpanded(!isKycExpanded)}
              >
                {isKycExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                {isKycExpanded ? 'Collapse' : 'Expand'}
              </Button>
            </div>
          </CardHeader>
          {isKycExpanded && (
            <CardContent className="space-y-6">
              <TooltipProvider>
                {/* Personal Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Personal Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="fullLegalName" className="flex items-center gap-1">
                        Full Legal Name <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Enter your full legal name as it appears on official documents</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="fullLegalName"
                        value={kycData.fullLegalName}
                        onChange={(e) => handleKycFieldChange('fullLegalName', e.target.value)}
                        placeholder="John Doe"
                        className={kycErrors.fullLegalName ? 'border-red-500' : ''}
                      />
                      {kycErrors.fullLegalName && <p className="text-sm text-red-500">{kycErrors.fullLegalName}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="dateOfBirth" className="flex items-center gap-1">
                        Date of Birth <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Must be 18 years or older</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="dateOfBirth"
                        type="date"
                        value={kycData.dateOfBirth}
                        onChange={(e) => handleKycFieldChange('dateOfBirth', e.target.value)}
                        className={kycErrors.dateOfBirth ? 'border-red-500' : ''}
                      />
                      {kycErrors.dateOfBirth && <p className="text-sm text-red-500">{kycErrors.dateOfBirth}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="phoneNumber" className="flex items-center gap-1">
                        Phone Number <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Format: +1-XXX-XXX-XXXX</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="phoneNumber"
                        value={kycData.phoneNumber}
                        onChange={(e) => handleKycFieldChange('phoneNumber', e.target.value)}
                        placeholder="+1-555-123-4567"
                        className={kycErrors.phoneNumber ? 'border-red-500' : ''}
                      />
                      {kycErrors.phoneNumber && <p className="text-sm text-red-500">{kycErrors.phoneNumber}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="emailAddress" className="flex items-center gap-1">
                        Email Address <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Enter a valid email address</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="emailAddress"
                        type="email"
                        value={kycData.emailAddress}
                        onChange={(e) => handleKycFieldChange('emailAddress', e.target.value)}
                        placeholder="john.doe@example.com"
                        className={kycErrors.emailAddress ? 'border-red-500' : ''}
                      />
                      {kycErrors.emailAddress && <p className="text-sm text-red-500">{kycErrors.emailAddress}</p>}
                    </div>
                  </div>
                </div>

                {/* Address Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Address Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="streetAddress1" className="flex items-center gap-1">
                        Street Address Line 1 <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="streetAddress1"
                        value={kycData.streetAddress1}
                        onChange={(e) => handleKycFieldChange('streetAddress1', e.target.value)}
                        placeholder="123 Main Street"
                        className={kycErrors.streetAddress1 ? 'border-red-500' : ''}
                      />
                      {kycErrors.streetAddress1 && <p className="text-sm text-red-500">{kycErrors.streetAddress1}</p>}
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="streetAddress2">Street Address Line 2</Label>
                      <Input
                        id="streetAddress2"
                        value={kycData.streetAddress2}
                        onChange={(e) => handleKycFieldChange('streetAddress2', e.target.value)}
                        placeholder="Apt 4B, Suite 200"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="city" className="flex items-center gap-1">
                        City <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="city"
                        value={kycData.city}
                        onChange={(e) => handleKycFieldChange('city', e.target.value)}
                        placeholder="New York"
                        className={kycErrors.city ? 'border-red-500' : ''}
                      />
                      {kycErrors.city && <p className="text-sm text-red-500">{kycErrors.city}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="stateProvince" className="flex items-center gap-1">
                        State/Province <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.stateProvince} onValueChange={(value) => handleKycFieldChange('stateProvince', value)}>
                        <SelectTrigger className={kycErrors.stateProvince ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select state" />
                        </SelectTrigger>
                        <SelectContent>
                          {usStates.map((state) => (
                            <SelectItem key={state} value={state}>{state}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {kycErrors.stateProvince && <p className="text-sm text-red-500">{kycErrors.stateProvince}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="postalZipCode" className="flex items-center gap-1">
                        Postal/ZIP Code <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="postalZipCode"
                        value={kycData.postalZipCode}
                        onChange={(e) => handleKycFieldChange('postalZipCode', e.target.value)}
                        placeholder="10001"
                        className={kycErrors.postalZipCode ? 'border-red-500' : ''}
                      />
                      {kycErrors.postalZipCode && <p className="text-sm text-red-500">{kycErrors.postalZipCode}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="country" className="flex items-center gap-1">
                        Country <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.country} onValueChange={(value) => handleKycFieldChange('country', value)}>
                        <SelectTrigger className={kycErrors.country ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select country" />
                        </SelectTrigger>
                        <SelectContent>
                          {countries.map((country) => (
                            <SelectItem key={country} value={country}>{country}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {kycErrors.country && <p className="text-sm text-red-500">{kycErrors.country}</p>}
                    </div>
                  </div>
                </div>

                {/* Identification Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Identification Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="citizenshipCountry" className="flex items-center gap-1">
                        Citizenship Country <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.citizenshipCountry} onValueChange={(value) => handleKycFieldChange('citizenshipCountry', value)}>
                        <SelectTrigger className={kycErrors.citizenshipCountry ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select country" />
                        </SelectTrigger>
                        <SelectContent>
                          {countries.map((country) => (
                            <SelectItem key={country} value={country}>{country}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {kycErrors.citizenshipCountry && <p className="text-sm text-red-500">{kycErrors.citizenshipCountry}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="identificationType" className="flex items-center gap-1">
                        Identification Type <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.identificationType} onValueChange={(value) => handleKycFieldChange('identificationType', value)}>
                        <SelectTrigger className={kycErrors.identificationType ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select ID type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="SSN">SSN</SelectItem>
                          <SelectItem value="TIN">TIN</SelectItem>
                          <SelectItem value="Passport">Passport</SelectItem>
                          <SelectItem value="Driver's License">Driver's License</SelectItem>
                          <SelectItem value="Alien ID">Alien ID</SelectItem>
                        </SelectContent>
                      </Select>
                      {kycErrors.identificationType && <p className="text-sm text-red-500">{kycErrors.identificationType}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="identificationNumber" className="flex items-center gap-1">
                        Identification Number <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>This will be masked after typing for security</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="identificationNumber"
                        type="password"
                        value={kycData.identificationNumber}
                        onChange={(e) => handleKycFieldChange('identificationNumber', e.target.value)}
                        placeholder="Enter ID number"
                        className={kycErrors.identificationNumber ? 'border-red-500' : ''}
                      />
                      {kycErrors.identificationNumber && <p className="text-sm text-red-500">{kycErrors.identificationNumber}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="idIssuingCountry" className="flex items-center gap-1">
                        ID Issuing Country <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.idIssuingCountry} onValueChange={(value) => handleKycFieldChange('idIssuingCountry', value)}>
                        <SelectTrigger className={kycErrors.idIssuingCountry ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select country" />
                        </SelectTrigger>
                        <SelectContent>
                          {countries.map((country) => (
                            <SelectItem key={country} value={country}>{country}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {kycErrors.idIssuingCountry && <p className="text-sm text-red-500">{kycErrors.idIssuingCountry}</p>}
                    </div>
                  </div>
                </div>

                {/* Financial Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Financial Information (GENIUS ACT Required)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="sourceOfFunds" className="flex items-center gap-1">
                        Source of Funds <span className="text-red-500">*</span>
                      </Label>
                      <Select value={kycData.sourceOfFunds} onValueChange={(value) => handleKycFieldChange('sourceOfFunds', value)}>
                        <SelectTrigger className={kycErrors.sourceOfFunds ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select source" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Employment Income">Employment Income</SelectItem>
                          <SelectItem value="Business Income">Business Income</SelectItem>
                          <SelectItem value="Investment Returns">Investment Returns</SelectItem>
                          <SelectItem value="Inheritance">Inheritance</SelectItem>
                          <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                      {kycErrors.sourceOfFunds && <p className="text-sm text-red-500">{kycErrors.sourceOfFunds}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="expectedMonthlyTransactionVolume" className="flex items-center gap-1">
                        Expected Monthly Transaction Volume (USD) <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="expectedMonthlyTransactionVolume"
                        type="number"
                        value={kycData.expectedMonthlyTransactionVolume || ''}
                        onChange={(e) => handleKycFieldChange('expectedMonthlyTransactionVolume', Number(e.target.value))}
                        placeholder="50000"
                        className={kycErrors.expectedMonthlyTransactionVolume ? 'border-red-500' : ''}
                      />
                      {kycErrors.expectedMonthlyTransactionVolume && <p className="text-sm text-red-500">{kycErrors.expectedMonthlyTransactionVolume}</p>}
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="purposeOfLoan" className="flex items-center gap-1">
                        Purpose of Loan <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Minimum 20 characters required</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Textarea
                        id="purposeOfLoan"
                        value={kycData.purposeOfLoan}
                        onChange={(e) => handleKycFieldChange('purposeOfLoan', e.target.value)}
                        placeholder="Please provide a detailed explanation of how you intend to use the loan funds..."
                        rows={3}
                        className={kycErrors.purposeOfLoan ? 'border-red-500' : ''}
                      />
                      {kycErrors.purposeOfLoan && <p className="text-sm text-red-500">{kycErrors.purposeOfLoan}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="expectedNumberOfMonthlyTransactions" className="flex items-center gap-1">
                        Expected Number of Monthly Transactions <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="expectedNumberOfMonthlyTransactions"
                        type="number"
                        value={kycData.expectedNumberOfMonthlyTransactions || ''}
                        onChange={(e) => handleKycFieldChange('expectedNumberOfMonthlyTransactions', Number(e.target.value))}
                        placeholder="10"
                        className={kycErrors.expectedNumberOfMonthlyTransactions ? 'border-red-500' : ''}
                      />
                      {kycErrors.expectedNumberOfMonthlyTransactions && <p className="text-sm text-red-500">{kycErrors.expectedNumberOfMonthlyTransactions}</p>}
                    </div>
                  </div>
                </div>

                {/* Compliance Screening */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Compliance Screening</h3>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label className="flex items-center gap-1">
                        Are you a Politically Exposed Person (PEP)? <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>A PEP is someone who holds a prominent public position or has close associations with such individuals</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <RadioGroup value={kycData.isPEP} onValueChange={(value) => handleKycFieldChange('isPEP', value)}>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="No" id="pep-no" />
                          <Label htmlFor="pep-no">No</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="Yes" id="pep-yes" />
                          <Label htmlFor="pep-yes">Yes</Label>
                        </div>
                      </RadioGroup>
                      {kycErrors.isPEP && <p className="text-sm text-red-500">{kycErrors.isPEP}</p>}
                    </div>

                    {kycData.isPEP === 'Yes' && (
                      <div className="space-y-2">
                        <Label htmlFor="pepDetails" className="flex items-center gap-1">
                          Please provide details <span className="text-red-500">*</span>
                        </Label>
                        <Textarea
                          id="pepDetails"
                          value={kycData.pepDetails}
                          onChange={(e) => handleKycFieldChange('pepDetails', e.target.value)}
                          placeholder="Please provide details about your PEP status..."
                          rows={3}
                          className={kycErrors.pepDetails ? 'border-red-500' : ''}
                        />
                        {kycErrors.pepDetails && <p className="text-sm text-red-500">{kycErrors.pepDetails}</p>}
                      </div>
                    )}
                  </div>
                </div>

                {/* Identity Document Upload */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Identity Document Upload</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="governmentIdFile" className="flex items-center gap-1">
                        Upload Government-Issued ID <span className="text-red-500">*</span>
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Passport, driver's license, or national ID</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="governmentIdFile"
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={(e) => handleKycFieldChange('governmentIdFile', e.target.files?.[0] || null)}
                        className={kycErrors.governmentIdFile ? 'border-red-500' : ''}
                      />
                      {kycErrors.governmentIdFile && <p className="text-sm text-red-500">{kycErrors.governmentIdFile}</p>}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="proofOfAddressFile">
                        Upload Proof of Address
                        <Tooltip>
                          <TooltipTrigger>
                            <HelpCircle className="h-3 w-3 text-gray-400" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Utility bill or bank statement (optional)</p>
                          </TooltipContent>
                        </Tooltip>
                      </Label>
                      <Input
                        id="proofOfAddressFile"
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={(e) => handleKycFieldChange('proofOfAddressFile', e.target.files?.[0] || null)}
                      />
                    </div>
                  </div>
                </div>

                {/* Save KYC Button */}
                <div className="flex justify-end pt-4 border-t">
                  <Button
                    onClick={handleSaveKyc}
                    disabled={isSavingKyc}
                    className="min-w-[150px]"
                  >
                    {isSavingKyc ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      'Save KYC Data'
                    )}
                  </Button>
                </div>
              </TooltipProvider>
            </CardContent>
          )}
        </Card>

        {/* Loan Information */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Information</CardTitle>
            <CardDescription>
              Provide loan details and document context (optional)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4" key={`loan-info-${forceUpdate}`}>
              <div className="space-y-2">
                <Label htmlFor="loanId">Loan ID</Label>
                <Input
                  id="loanId"
                  value={formData.loanId}
                  onChange={(e) => {
                    console.log('🔍 Loan ID field changed to:', e.target.value);
                    setFormData(prev => ({ ...prev, loanId: e.target.value }));
                    const currentMeta = JSON.parse(metadata || '{}')
                    setMetadata(JSON.stringify({ ...currentMeta, loanId: e.target.value }, null, 2))
                  }}
                  placeholder="e.g., LOAN_2024_001"
                />
                <p className="text-xs text-muted-foreground">
                  Unique identifier for the loan
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="documentType">Document Type</Label>
                <select
                  id="documentType"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.documentType}
                  onChange={(e) => {
                    setFormData(prev => ({ ...prev, documentType: e.target.value }));
                    const currentMeta = JSON.parse(metadata || '{}')
                    setMetadata(JSON.stringify({ ...currentMeta, documentType: e.target.value }, null, 2))
                  }}
                >
                  <option value="">Select document type</option>
                  <option value="loan_application">Loan Application</option>
                  <option value="credit_report">Credit Report</option>
                  <option value="property_appraisal">Property Appraisal</option>
                  <option value="income_verification">Income Verification</option>
                  <option value="bank_statements">Bank Statements</option>
                  <option value="tax_returns">Tax Returns</option>
                  <option value="employment_verification">Employment Verification</option>
                  <option value="underwriting_decision">Underwriting Decision</option>
                  <option value="closing_disclosure">Closing Disclosure</option>
                  <option value="title_insurance">Title Insurance</option>
                  <option value="homeowners_insurance">Homeowners Insurance</option>
                  <option value="flood_certificate">Flood Certificate</option>
                  <option value="compliance_document">Compliance Document</option>
                  <option value="other">Other</option>
                </select>
                <p className="text-xs text-muted-foreground">
                  Type of document being uploaded
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="borrowerName">Borrower Name</Label>
                <Input
                  id="borrowerName"
                  value={formData.borrowerName}
                  onChange={(e) => {
                    setFormData(prev => ({ ...prev, borrowerName: e.target.value }));
                    const currentMeta = JSON.parse(metadata || '{}')
                    setMetadata(JSON.stringify({ ...currentMeta, borrowerName: e.target.value }, null, 2))
                  }}
                  placeholder="e.g., John Smith"
                />
                <p className="text-xs text-muted-foreground">
                  Primary borrower's full name
                </p>
              </div>
              </div>

            {/* Privacy Notice Banner */}
            {!privacyNoticeDismissed && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 relative">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-blue-800">
                      <span className="font-medium">ℹ️ Identity Information</span> - We collect minimal borrower identity data solely for creating an immutable audit trail. This data is cryptographically sealed in the blockchain but is not used for lending decisions or identity verification. Sensitive data (SSN, ID numbers) are collected in truncated format (last 4 digits only).
                    </p>
                  </div>
                  <button
                    onClick={handleDismissPrivacyNotice}
                    className="flex-shrink-0 text-blue-400 hover:text-blue-600 transition-colors"
                    aria-label="Dismiss privacy notice"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            {/* Borrower Information (For Audit Trail) */}
            <div className="space-y-4 pt-4 border-t">
              <div>
                <h3 className="text-lg font-semibold">Borrower Information (For Audit Trail)</h3>
                <p className="text-sm text-muted-foreground">
                  Essential borrower identity fields that will be sealed in the blockchain
                </p>
              </div>

              {/* Basic Identity */}
              <div className="space-y-4">
                <h4 className="text-md font-medium">Basic Identity</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="borrowerFullName" className="flex items-center gap-1">
                      Full Name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerFullName"
                      value={formData.borrowerFullName}
                      onChange={(e) => {
                        setFormData(prev => ({ ...prev, borrowerFullName: e.target.value }));
                        handleBorrowerFieldChange('borrowerFullName', e.target.value);
                      }}
                      placeholder="Primary borrower's legal name"
                      className={hasFieldError('borrowerFullName') ? 'border-red-500' : ''}
                    />
                    {getFieldError('borrowerFullName') && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {getFieldError('borrowerFullName')}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerDateOfBirth" className="flex items-center gap-1">
                      Date of Birth <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerDateOfBirth"
                      type="date"
                      value={formData.borrowerDateOfBirth}
                      onChange={(e) => handleBorrowerFieldChange('borrowerDateOfBirth', e.target.value)}
                      className={borrowerErrors.borrowerDateOfBirth ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerDateOfBirth && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerDateOfBirth}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerEmail" className="flex items-center gap-1">
                      Email Address <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerEmail"
                      type="email"
                      value={formData.borrowerEmail}
                      onChange={(e) => handleBorrowerFieldChange('borrowerEmail', e.target.value)}
                      placeholder="borrower@example.com"
                      className={hasFieldError('borrowerEmail') ? 'border-red-500' : ''}
                    />
                    {getFieldError('borrowerEmail') && (
                      <p className="text-sm text-red-500 flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {getFieldError('borrowerEmail')}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerPhone" className="flex items-center gap-1">
                      Phone Number <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerPhone"
                      type="tel"
                      value={formData.borrowerPhone}
                      onChange={(e) => handleBorrowerFieldChange('borrowerPhone', e.target.value)}
                      placeholder="+1-555-123-4567"
                      className={borrowerErrors.borrowerPhone ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerPhone && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerPhone}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Address */}
              <div className="space-y-4">
                <h4 className="text-md font-medium">Address</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="borrowerStreetAddress" className="flex items-center gap-1">
                      Street Address <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerStreetAddress"
                      value={formData.borrowerStreetAddress}
                      onChange={(e) => handleBorrowerFieldChange('borrowerStreetAddress', e.target.value)}
                      placeholder="123 Main Street"
                      className={borrowerErrors.borrowerStreetAddress ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerStreetAddress && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerStreetAddress}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerCity" className="flex items-center gap-1">
                      City <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerCity"
                      value={formData.borrowerCity}
                      onChange={(e) => handleBorrowerFieldChange('borrowerCity', e.target.value)}
                      placeholder="Anytown"
                      className={borrowerErrors.borrowerCity ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerCity && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerCity}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerState" className="flex items-center gap-1">
                      State <span className="text-red-500">*</span>
                    </Label>
                    <Select
                      value={formData.borrowerState}
                      onValueChange={(value) => handleBorrowerFieldChange('borrowerState', value)}
                    >
                      <SelectTrigger className={borrowerErrors.borrowerState ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="AL">Alabama</SelectItem>
                        <SelectItem value="AK">Alaska</SelectItem>
                        <SelectItem value="AZ">Arizona</SelectItem>
                        <SelectItem value="AR">Arkansas</SelectItem>
                        <SelectItem value="CA">California</SelectItem>
                        <SelectItem value="CO">Colorado</SelectItem>
                        <SelectItem value="CT">Connecticut</SelectItem>
                        <SelectItem value="DE">Delaware</SelectItem>
                        <SelectItem value="FL">Florida</SelectItem>
                        <SelectItem value="GA">Georgia</SelectItem>
                        <SelectItem value="HI">Hawaii</SelectItem>
                        <SelectItem value="ID">Idaho</SelectItem>
                        <SelectItem value="IL">Illinois</SelectItem>
                        <SelectItem value="IN">Indiana</SelectItem>
                        <SelectItem value="IA">Iowa</SelectItem>
                        <SelectItem value="KS">Kansas</SelectItem>
                        <SelectItem value="KY">Kentucky</SelectItem>
                        <SelectItem value="LA">Louisiana</SelectItem>
                        <SelectItem value="ME">Maine</SelectItem>
                        <SelectItem value="MD">Maryland</SelectItem>
                        <SelectItem value="MA">Massachusetts</SelectItem>
                        <SelectItem value="MI">Michigan</SelectItem>
                        <SelectItem value="MN">Minnesota</SelectItem>
                        <SelectItem value="MS">Mississippi</SelectItem>
                        <SelectItem value="MO">Missouri</SelectItem>
                        <SelectItem value="MT">Montana</SelectItem>
                        <SelectItem value="NE">Nebraska</SelectItem>
                        <SelectItem value="NV">Nevada</SelectItem>
                        <SelectItem value="NH">New Hampshire</SelectItem>
                        <SelectItem value="NJ">New Jersey</SelectItem>
                        <SelectItem value="NM">New Mexico</SelectItem>
                        <SelectItem value="NY">New York</SelectItem>
                        <SelectItem value="NC">North Carolina</SelectItem>
                        <SelectItem value="ND">North Dakota</SelectItem>
                        <SelectItem value="OH">Ohio</SelectItem>
                        <SelectItem value="OK">Oklahoma</SelectItem>
                        <SelectItem value="OR">Oregon</SelectItem>
                        <SelectItem value="PA">Pennsylvania</SelectItem>
                        <SelectItem value="RI">Rhode Island</SelectItem>
                        <SelectItem value="SC">South Carolina</SelectItem>
                        <SelectItem value="SD">South Dakota</SelectItem>
                        <SelectItem value="TN">Tennessee</SelectItem>
                        <SelectItem value="TX">Texas</SelectItem>
                        <SelectItem value="UT">Utah</SelectItem>
                        <SelectItem value="VT">Vermont</SelectItem>
                        <SelectItem value="VA">Virginia</SelectItem>
                        <SelectItem value="WA">Washington</SelectItem>
                        <SelectItem value="WV">West Virginia</SelectItem>
                        <SelectItem value="WI">Wisconsin</SelectItem>
                        <SelectItem value="WY">Wyoming</SelectItem>
                        <SelectItem value="DC">District of Columbia</SelectItem>
                      </SelectContent>
                    </Select>
                    {borrowerErrors.borrowerState && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerState}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerZipCode" className="flex items-center gap-1">
                      ZIP Code <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerZipCode"
                      value={formData.borrowerZipCode}
                      onChange={(e) => handleBorrowerFieldChange('borrowerZipCode', e.target.value)}
                      placeholder="12345"
                      className={borrowerErrors.borrowerZipCode ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerZipCode && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerZipCode}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerCountry" className="flex items-center gap-1">
                      Country <span className="text-red-500">*</span>
                    </Label>
                    <Select
                      value={formData.borrowerCountry}
                      onValueChange={(value) => handleBorrowerFieldChange('borrowerCountry', value)}
                    >
                      <SelectTrigger className={borrowerErrors.borrowerCountry ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select country" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="US">United States</SelectItem>
                        <SelectItem value="CA">Canada</SelectItem>
                        <SelectItem value="MX">Mexico</SelectItem>
                        <SelectItem value="GB">United Kingdom</SelectItem>
                        <SelectItem value="DE">Germany</SelectItem>
                        <SelectItem value="FR">France</SelectItem>
                        <SelectItem value="IT">Italy</SelectItem>
                        <SelectItem value="ES">Spain</SelectItem>
                        <SelectItem value="AU">Australia</SelectItem>
                        <SelectItem value="JP">Japan</SelectItem>
                        <SelectItem value="CN">China</SelectItem>
                        <SelectItem value="IN">India</SelectItem>
                        <SelectItem value="BR">Brazil</SelectItem>
                        <SelectItem value="AR">Argentina</SelectItem>
                        <SelectItem value="OTHER">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    {borrowerErrors.borrowerCountry && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerCountry}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Identity Reference */}
              <div className="space-y-4">
                <h4 className="text-md font-medium">Identity Reference</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="borrowerSSNLast4" className="flex items-center gap-1">
                      Social Security Number (Last 4 digits only) <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerSSNLast4"
                      type="text"
                      maxLength={4}
                      value={formData.borrowerSSNLast4}
                      onChange={(e) => handleBorrowerFieldChange('borrowerSSNLast4', e.target.value)}
                      placeholder="1234"
                      className={borrowerErrors.borrowerSSNLast4 ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerSSNLast4 && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerSSNLast4}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerGovernmentIdType">Government ID Type</Label>
                    <Select
                      value={formData.borrowerGovernmentIdType}
                      onValueChange={(value) => {
                        const currentMeta = JSON.parse(metadata || '{}')
                        setMetadata(JSON.stringify({ ...currentMeta, borrowerGovernmentIdType: value }, null, 2))
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select ID type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="driver_license">Driver's License</SelectItem>
                        <SelectItem value="passport">Passport</SelectItem>
                        <SelectItem value="state_id">State ID</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerIdNumberLast4">ID Number (Last 4 digits only)</Label>
                    <Input
                      id="borrowerIdNumberLast4"
                      type="text"
                      maxLength={4}
                      value={formData.borrowerIdNumberLast4}
                      onChange={(e) => handleBorrowerFieldChange('borrowerIdNumberLast4', e.target.value)}
                      placeholder="1234"
                      className={borrowerErrors.borrowerIdNumberLast4 ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerIdNumberLast4 && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerIdNumberLast4}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Loan-Specific */}
              <div className="space-y-4">
                <h4 className="text-md font-medium">Loan-Specific</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="borrowerEmploymentStatus" className="flex items-center gap-1">
                      Employment Status <span className="text-red-500">*</span>
                    </Label>
                    <Select
                      value={formData.borrowerEmploymentStatus}
                      onValueChange={(value) => handleBorrowerFieldChange('borrowerEmploymentStatus', value)}
                    >
                      <SelectTrigger className={borrowerErrors.borrowerEmploymentStatus ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select employment status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="employed">Employed</SelectItem>
                        <SelectItem value="self_employed">Self-Employed</SelectItem>
                        <SelectItem value="retired">Retired</SelectItem>
                        <SelectItem value="unemployed">Unemployed</SelectItem>
                      </SelectContent>
                    </Select>
                    {borrowerErrors.borrowerEmploymentStatus && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerEmploymentStatus}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerAnnualIncome" className="flex items-center gap-1">
                      Annual Income <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="borrowerAnnualIncome"
                      type="number"
                      value={formData.borrowerAnnualIncome}
                      onChange={(e) => handleBorrowerFieldChange('borrowerAnnualIncome', e.target.value)}
                      placeholder="75000"
                      className={borrowerErrors.borrowerAnnualIncome ? 'border-red-500' : ''}
                    />
                    {borrowerErrors.borrowerAnnualIncome && (
                      <p className="text-sm text-red-500">{borrowerErrors.borrowerAnnualIncome}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="borrowerCoBorrowerName">Co-Borrower Name</Label>
                    <Input
                      id="borrowerCoBorrowerName"
                      value={formData.borrowerCoBorrowerName}
                      onChange={(e) => {
                        const currentMeta = JSON.parse(metadata || '{}')
                        setMetadata(JSON.stringify({ ...currentMeta, borrowerCoBorrowerName: e.target.value }, null, 2))
                      }}
                      placeholder="Jane Smith (optional)"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              <div className="space-y-2">
                <Label htmlFor="loanAmount">Loan Amount</Label>
                <Input
                  id="loanAmount"
                  type="number"
                  value={formData.loanAmount}
                  onChange={(e) => {
                    setFormData(prev => ({ ...prev, loanAmount: e.target.value }));
                    const currentMeta = JSON.parse(metadata || '{}')
                    setMetadata(JSON.stringify({ ...currentMeta, loanAmount: e.target.value }, null, 2))
                  }}
                  placeholder="e.g., 250000"
                />
                <p className="text-xs text-muted-foreground">
                  Loan amount in USD
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                value={formData.additionalNotes}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, additionalNotes: e.target.value }));
                  const currentMeta = JSON.parse(metadata || '{}')
                  setMetadata(JSON.stringify({ ...currentMeta, notes: e.target.value }, null, 2))
                }}
                placeholder="Any additional information about this document..."
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                Optional notes or comments about the document
              </p>
            </div>

            {/* Advanced Options (Collapsible) */}
            <details className="group">
              <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                Advanced Options
              </summary>
              <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                <div className="space-y-2">
                  <Label htmlFor="etid">Entity Type ID (ETID)</Label>
                  <Input
                    id="etid"
                    value={etid}
                    onChange={(e) => setEtid(e.target.value)}
                    placeholder="100001"
                  />
                  <p className="text-xs text-muted-foreground">
                    100001 for loan packets, 100002 for JSON documents. Leave as default unless you know what you're doing.
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="rawMetadata">Raw Metadata (JSON)</Label>
                  <Textarea
                    id="rawMetadata"
                    value={metadata}
                    onChange={(e) => setMetadata(e.target.value)}
                    placeholder='{"source": "api", "department": "finance"}'
                    rows={3}
                  />
                  <p className="text-xs text-muted-foreground">
                    Advanced: Raw JSON metadata for technical users
                  </p>
                </div>
              </div>
            </details>
          </CardContent>
        </Card>

        {/* Upload Result */}
        {uploadResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                Document Sealed Successfully
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Artifact ID</Label>
                  <p className="text-sm font-mono bg-muted p-2 rounded">{uploadResult.artifactId}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Walacor Transaction ID</Label>
                  <p className="text-sm font-mono bg-muted p-2 rounded">{uploadResult.walacorTxId}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Document Hash</Label>
                  <p className="text-sm font-mono bg-muted p-2 rounded break-all">{fileHash}</p>
                </div>
              <div>
                <Label className="text-sm font-medium">Sealed At</Label>
                <p className="text-sm">{new Date(uploadResult.sealedAt).toLocaleString()}</p>
                </div>
              </div>

              {uploadResult.proofBundle && (
                <div>
                  <Label className="text-sm font-medium">Proof Bundle</Label>
                  <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32">
                    {JSON.stringify(uploadResult.proofBundle, null, 2)}
                  </pre>
                </div>
              )}

              <div className="flex gap-2">
                <Button asChild>
                  <a href={`http://localhost:8000/api/artifacts/${uploadResult.artifactId}`} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Artifact Details
                  </a>
                </Button>
                <Button variant="outline" onClick={handleReset}>
                  Upload Another
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {uploadState.error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-700">
              <div className="flex items-center justify-between">
                <span>{uploadState.error.message}</span>
                {uploadState.canRetry && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRetry}
                    className="ml-4 border-red-300 text-red-700 hover:bg-red-100"
                  >
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Retry
                  </Button>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Progress Indicator */}
        {uploadState.isUploading && (
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Uploading and Sealing Document...</span>
                  <span className="text-sm text-gray-500">{uploadState.progress}%</span>
                </div>
                <Progress value={uploadState.progress} className="w-full" />
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  <span>Processing borrower information and sealing in blockchain...</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* File Size Warning */}
        {file && file.size > 10 * 1024 * 1024 && (
          <Alert className="border-yellow-200 bg-yellow-50">
            <AlertCircle className="h-4 w-4 text-yellow-500" />
            <AlertDescription className="text-yellow-700">
              Large file detected ({Math.round(file.size / 1024 / 1024)}MB). Upload may take longer than usual.
            </AlertDescription>
          </Alert>
        )}

            {/* Security Configuration */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" /> Security Configuration
                </CardTitle>
                <CardDescription>
                  Choose the security level for document sealing.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="quantumSafe"
                      checked={quantumSafeMode}
                      onChange={(e) => {
                        setQuantumSafeMode(e.target.checked);
                        if (e.target.checked) {
                          setMaximumSecurityMode(false); // Disable maximum security when quantum-safe is enabled
                        }
                      }}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <Label htmlFor="quantumSafe" className="text-sm font-medium">
                      🔬 Quantum-Safe Mode (Future-Proof)
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="maximumSecurity"
                      checked={maximumSecurityMode}
                      onChange={(e) => {
                        setMaximumSecurityMode(e.target.checked);
                        if (e.target.checked) {
                          setQuantumSafeMode(false); // Disable quantum-safe when maximum security is enabled
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <Label htmlFor="maximumSecurity" className="text-sm font-medium">
                      Maximum Security Mode (Recommended)
                    </Label>
                  </div>
                  
                  <div className="text-sm text-gray-600 space-y-2">
                    {quantumSafeMode && (
                      <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <p className="font-medium text-purple-800 mb-2">🔬 Quantum-Safe Security includes:</p>
                        <ul className="list-disc list-inside space-y-1 ml-4 text-purple-700">
                          <li>SHAKE256 hashing (quantum-resistant)</li>
                          <li>BLAKE3 hashing (quantum-resistant)</li>
                          <li>Dilithium digital signatures (NIST PQC Standard)</li>
                          <li>Hybrid classical-quantum approach</li>
                          <li>Protection against future quantum attacks</li>
                          <li>Blockchain sealing for immutability</li>
                        </ul>
                        <div className="flex items-center gap-1 flex-wrap mt-2">
                          <Badge variant="outline" className="text-xs bg-purple-100 text-purple-800">
                            🛡️ Quantum-Resistant
                          </Badge>
                          <Badge variant="outline" className="text-xs bg-blue-100 text-blue-800">
                            🔒 Post-Quantum Secure
                          </Badge>
                          <Badge variant="outline" className="text-xs bg-yellow-100 text-yellow-800">
                            ⚡ SHA3-512 Protected
                          </Badge>
                          <Badge variant="outline" className="text-xs bg-green-100 text-green-800">
                            ⭐ Future-Proof Security
                          </Badge>
                          <Badge variant="outline" className="text-xs bg-indigo-100 text-indigo-800">
                            ✅ NIST PQC Compliant
                          </Badge>
                        </div>
                        <p className="text-xs text-purple-600 mt-2">
                          This provides protection against future quantum computing attacks while maintaining current security.
                        </p>
                      </div>
                    )}
                    
                    {maximumSecurityMode && (
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="font-medium text-blue-800 mb-2">Maximum Security includes:</p>
                        <ul className="list-disc list-inside space-y-1 ml-4 text-blue-700">
                          <li>Multi-algorithm hashing (SHA-256, SHA-512, BLAKE3, SHA3-256)</li>
                          <li>PKI-based digital signatures</li>
                          <li>Content-based integrity verification</li>
                          <li>Cross-verification systems</li>
                          <li>Advanced tamper detection</li>
                          <li>Blockchain sealing for immutability</li>
                        </ul>
                        <p className="text-xs text-blue-600 mt-2">
                          This provides the highest level of current security and minimal tampering risk for your loan documents.
                        </p>
                      </div>
                    )}
                    
                    {!quantumSafeMode && !maximumSecurityMode && (
                      <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                        <p className="font-medium text-gray-800 mb-2">Standard Security includes:</p>
                        <ul className="list-disc list-inside space-y-1 ml-4 text-gray-700">
                          <li>SHA-256 hashing</li>
                          <li>Basic digital signatures</li>
                          <li>Blockchain sealing for immutability</li>
                        </ul>
                        <p className="text-xs text-gray-600 mt-2">
                          Standard security suitable for most loan documents.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleUpload}
            disabled={isUploading || !file || !fileHash || isVerifying || uploadResult || (verifyResult && verifyResult.is_valid)}
            className="flex-1"
          >
                {isUploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {quantumSafeMode ? 'Sealing with Quantum-Safe Cryptography...' : 
                     maximumSecurityMode ? 'Sealing with Maximum Security...' : 'Sealing Document...'}
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    {!file ? 'Select File to Upload' : 
                     quantumSafeMode ? 'Upload & Seal (Quantum-Safe)' : 
                     maximumSecurityMode ? 'Upload & Seal (Maximum Security)' : 'Upload & Seal'}
                  </>
                )}
          </Button>
          {file && !uploadResult && !verifyResult && (
            <Button variant="outline" onClick={handleReset}>
              Reset
            </Button>
          )}
        </div>

        {/* Action Buttons for Already Sealed Documents */}
        {file && verifyResult && verifyResult.is_valid && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset} className="flex-1">
              Upload Different File
            </Button>
            <Button asChild>
              <a href={`http://localhost:8000/api/verify?hash=${fileHash}`} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                View Verification
              </a>
            </Button>
          </div>
        )}
      </div>
    </div>
    </>
  );
}

