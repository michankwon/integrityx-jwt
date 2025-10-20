/**
 * Data Sanitization Utilities for Database-Friendly Input
 * 
 * These functions ensure all form data is clean and safe for database insertion
 * by removing special characters, normalizing formats, and preventing SQL injection.
 */

/**
 * Sanitize text input - removes special characters except basic punctuation
 */
export function sanitizeText(input: string): string {
  if (!input) return '';
  
  return input
    .trim() // Remove leading/trailing whitespace
    .replace(/[<>'"&]/g, '') // Remove potentially dangerous characters
    .replace(/[^\w\s\-.,()]/g, '') // Keep only alphanumeric, spaces, hyphens, periods, commas, parentheses
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .substring(0, 255); // Limit length to prevent database issues
}

/**
 * Sanitize email - keeps only valid email characters
 */
export function sanitizeEmail(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9@._-]/g, '') // Keep only valid email characters
    .substring(0, 100); // Reasonable email length limit
}

/**
 * Sanitize phone number - keeps only digits, +, -, (, ), and spaces
 */
export function sanitizePhone(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[^\d+\-() ]/g, '') // Keep only digits and phone formatting characters
    .replace(/\s+/g, ' ') // Normalize spaces
    .substring(0, 20); // Reasonable phone length limit
}

/**
 * Sanitize numeric input - keeps only digits and decimal point
 */
export function sanitizeNumber(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[^\d.]/g, '') // Keep only digits and decimal point
    .replace(/\.{2,}/g, '.') // Replace multiple decimal points with single
    .replace(/^\./, '0.') // Add leading zero if starts with decimal
    .substring(0, 15); // Reasonable number length limit
}

/**
 * Sanitize input with digits and hyphens - keeps only digits and hyphens
 */
export function sanitizeDigitsAndHyphens(input: string, maxLength: number = 10): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[^\d-]/g, '') // Keep only digits and hyphens
    .substring(0, maxLength); // Length limit
}

/**
 * Sanitize date - keeps only valid date characters (YYYY-MM-DD format)
 */
export function sanitizeDate(input: string): string {
  return sanitizeDigitsAndHyphens(input, 10);
}

/**
 * Sanitize numeric input with specific length - keeps only digits
 */
export function sanitizeNumeric(input: string, maxLength: number = 4): string {
  if (!input) return '';
  
  const digits = input.replace(/\D/g, ''); // Extract only digits
  return digits.substring(0, maxLength); // Take specified length
}

/**
 * Sanitize SSN/ID number - keeps only last 4 digits
 */
export function sanitizeSSNLast4(input: string): string {
  if (!input) return '';
  
  const digits = input.replace(/\D/g, ''); // Extract only digits
  return digits.substring(digits.length - 4); // Take last 4 digits
}

/**
 * Sanitize ZIP code - keeps only digits and hyphens
 */
export function sanitizeZipCode(input: string): string {
  return sanitizeDigitsAndHyphens(input, 10);
}

/**
 * Sanitize address - removes special characters but keeps basic formatting
 */
export function sanitizeAddress(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[<>'"&]/g, '') // Remove potentially dangerous characters
    .replace(/[^\w\s\-.,#]/g, '') // Keep alphanumeric, spaces, hyphens, periods, commas, hash
    .replace(/\s+/g, ' ') // Normalize spaces
    .substring(0, 100); // Address length limit
}

/**
 * Sanitize city name - keeps only letters, spaces, and hyphens
 */
export function sanitizeCity(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[^a-zA-Z\s-]/g, '') // Keep only letters, spaces, and hyphens
    .replace(/\s+/g, ' ') // Normalize spaces
    .substring(0, 50); // City name length limit
}

/**
 * Sanitize code (state/country) - keeps only letters and converts to uppercase
 */
export function sanitizeCode(input: string, maxLength: number = 2): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[^a-zA-Z]/g, '') // Keep only letters
    .toUpperCase()
    .substring(0, maxLength); // Code length limit
}

/**
 * Sanitize state - keeps only letters and converts to uppercase
 */
export function sanitizeState(input: string): string {
  return sanitizeCode(input, 2);
}

/**
 * Sanitize country - keeps only letters and converts to uppercase
 */
export function sanitizeCountry(input: string): string {
  return sanitizeCode(input, 2);
}

/**
 * Sanitize employment status - maps to valid enum values
 */
export function sanitizeEmploymentStatus(input: string): string {
  if (!input) return 'employed';
  
  const validStatuses = [
    'employed',
    'self_employed', 
    'unemployed',
    'retired',
    'student',
    'other'
  ];
  
  const normalized = input.toLowerCase().trim();
  return validStatuses.includes(normalized) ? normalized : 'employed';
}

/**
 * Sanitize government ID type - maps to valid enum values
 */
export function sanitizeGovernmentIdType(input: string): string {
  if (!input) return 'drivers_license';
  
  const validTypes = [
    'drivers_license',
    'passport',
    'state_id',
    'military_id',
    'other'
  ];
  
  const normalized = input.toLowerCase().trim();
  return validTypes.includes(normalized) ? normalized : 'drivers_license';
}

/**
 * Sanitize document type - maps to valid enum values
 */
export function sanitizeDocumentType(input: string): string {
  if (!input) return 'loan_application';
  
  const validTypes = [
    'loan_application',
    'promissory_note',
    'mortgage_agreement',
    'financial_statement',
    'tax_return',
    'bank_statement',
    'other'
  ];
  
  const normalized = input.toLowerCase().trim().replace(/[^a-z_]/g, '');
  return validTypes.includes(normalized) ? normalized : 'loan_application';
}

/**
 * Sanitize notes/comments - removes dangerous characters but keeps basic formatting
 */
export function sanitizeNotes(input: string): string {
  if (!input) return '';
  
  return input
    .trim()
    .replace(/[<>'"&]/g, '') // Remove potentially dangerous characters
    .replace(/[^\w\s\-.,!?()]/g, '') // Keep alphanumeric, spaces, basic punctuation
    .replace(/\s+/g, ' ') // Normalize spaces
    .substring(0, 1000); // Notes length limit
}

/**
 * Comprehensive sanitization for loan data object
 */
export function sanitizeLoanData(data: any): any {
  return {
    loanId: sanitizeText(data.loanId || ''),
    documentType: sanitizeDocumentType(data.documentType || ''),
    loanAmount: sanitizeNumber(data.loanAmount?.toString() || '0'),
    borrowerName: sanitizeText(data.borrowerName || ''),
    additionalNotes: sanitizeNotes(data.additionalNotes || ''),
    createdBy: sanitizeEmail(data.createdBy || '')
  };
}

/**
 * Comprehensive sanitization for borrower data object
 */
export function sanitizeBorrowerData(data: any): any {
  return {
    fullName: sanitizeText(data.fullName || ''),
    dateOfBirth: sanitizeDate(data.dateOfBirth || ''),
    email: sanitizeEmail(data.email || ''),
    phone: sanitizePhone(data.phone || ''),
    streetAddress: sanitizeAddress(data.streetAddress || ''),
    city: sanitizeCity(data.city || ''),
    state: sanitizeState(data.state || ''),
    zipCode: sanitizeZipCode(data.zipCode || ''),
    country: sanitizeCountry(data.country || 'US'),
    ssnLast4: sanitizeSSNLast4(data.ssnLast4 || ''),
    governmentIdType: sanitizeGovernmentIdType(data.governmentIdType || ''),
    idNumberLast4: sanitizeSSNLast4(data.idNumberLast4 || ''),
    employmentStatus: sanitizeEmploymentStatus(data.employmentStatus || ''),
    annualIncome: sanitizeNumber(data.annualIncome?.toString() || '0'),
    coBorrowerName: sanitizeText(data.coBorrowerName || '')
  };
}

/**
 * Validate and sanitize all form data before submission
 */
export function sanitizeFormData(loanData: any, borrowerData: any): {
  loanData: any;
  borrowerData: any;
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  // Sanitize loan data
  const sanitizedLoanData = sanitizeLoanData(loanData);
  
  // Sanitize borrower data
  const sanitizedBorrowerData = sanitizeBorrowerData(borrowerData);
  
  // Validate required fields
  if (!sanitizedLoanData.loanId) {
    errors.push('Loan ID is required');
  }
  
  if (!sanitizedBorrowerData.fullName) {
    errors.push('Borrower full name is required');
  }
  
  if (!sanitizedBorrowerData.email) {
    errors.push('Borrower email is required');
  }
  
  if (!sanitizedBorrowerData.phone) {
    errors.push('Borrower phone is required');
  }
  
  if (!sanitizedBorrowerData.dateOfBirth) {
    errors.push('Borrower date of birth is required');
  }
  
  if (!sanitizedBorrowerData.ssnLast4 || sanitizedBorrowerData.ssnLast4.length !== 4) {
    errors.push('SSN last 4 digits is required and must be exactly 4 digits');
  }
  
  if (!sanitizedBorrowerData.annualIncome || parseFloat(sanitizedBorrowerData.annualIncome) <= 0) {
    errors.push('Annual income is required and must be greater than 0');
  }
  
  return {
    loanData: sanitizedLoanData,
    borrowerData: sanitizedBorrowerData,
    isValid: errors.length === 0,
    errors
  };
}
