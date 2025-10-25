"""
Simplified Pydantic schemas for loan document API request/response validation.

This module defines comprehensive Pydantic models for validating loan document
API requests and responses, including borrower information, loan data, and
search parameters. All models include proper validation rules and field constraints.

Features:
- Comprehensive field validation with custom validators
- Phone number format validation (regex-based)
- SSN and ID number format validation
- Email validation using regex
- Date validation with age restrictions
- Enum validation for standardized values
- Masked response models for privacy protection
- Search parameter validation with pagination
"""

import re
from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

# Constants for validation patterns
NAME_PATTERN = r'^[a-zA-Z\s\'-\.]+$'
WALACOR_TX_ID_DESCRIPTION = "Walacor transaction ID"


class EmploymentStatus(str, Enum):
    """Employment status enumeration."""
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    DISABLED = "disabled"


class IDType(str, Enum):
    """Government ID type enumeration."""
    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    STATE_ID = "state_id"
    MILITARY_ID = "military_id"
    ALIEN_ID = "alien_id"


class DocumentType(str, Enum):
    """Loan document type enumeration."""
    LOAN_APPLICATION = "loan_application"
    MORTGAGE_APPLICATION = "mortgage_application"
    REFINANCE_APPLICATION = "refinance_application"
    HOME_EQUITY_LOAN = "home_equity_loan"
    PERSONAL_LOAN = "personal_loan"
    AUTO_LOAN = "auto_loan"
    BUSINESS_LOAN = "business_loan"


class FileInfo(BaseModel):
    """File information model."""
    filename: str = Field(..., min_length=1, max_length=255, description="Name of the file")
    file_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=0, le=100_000_000, description="File size in bytes (max 100MB)")
    upload_timestamp: str = Field(..., description="ISO timestamp when file was uploaded")
    content_hash: Optional[str] = Field(None, description="SHA-256 hash of file content")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename doesn't contain dangerous characters."""
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Filename contains invalid characters')
        return v


class BorrowerInfoRequest(BaseModel):
    """Borrower information request model with comprehensive validation."""
    
    # Personal Information
    full_name: str = Field(..., min_length=2, max_length=255, description="Full legal name of the borrower")
    date_of_birth: date = Field(..., description="Date of birth (must be 18+ years old)")
    email: str = Field(..., description="Valid email address")
    phone: str = Field(..., description="Phone number in international format")
    
    # Address Information
    address_line1: str = Field(..., min_length=1, max_length=255, description="Primary street address")
    address_line2: Optional[str] = Field(None, max_length=255, description="Secondary address line")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    zip_code: str = Field(..., description="ZIP code (5 or 9 digits)")
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    
    # Identity Information
    ssn_last4: str = Field(..., description="Last 4 digits of Social Security Number")
    id_type: IDType = Field(..., description="Type of government-issued ID")
    id_last4: str = Field(..., description="Last 4 digits of government ID number")
    
    # Financial Information
    employment_status: EmploymentStatus = Field(..., description="Current employment status")
    annual_income: int = Field(..., ge=0, le=10_000_000, description="Annual income in USD (0-10,000,000)")
    co_borrower_name: Optional[str] = Field(None, max_length=255, description="Name of co-borrower if applicable")
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v):
        """Validate borrower is at least 18 years old."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Borrower must be at least 18 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format using regex."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format using regex."""
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        clean_phone = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not re.match(phone_pattern, clean_phone):
            raise ValueError('Invalid phone number format')
        return v
    
    @field_validator('state')
    @classmethod
    def validate_state_code(cls, v):
        """Validate US state code."""
        us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
        }
        if v.upper() not in us_states:
            raise ValueError('Invalid state code')
        return v.upper()
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v):
        """Validate ZIP code format (5 or 9 digits)."""
        clean_zip = re.sub(r'[\s-]', '', v)
        if not re.match(r'^\d{5}(\d{4})?$', clean_zip):
            raise ValueError('ZIP code must be 5 or 9 digits')
        return clean_zip
    
    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v):
        """Validate ISO 3166-1 alpha-2 country code."""
        valid_countries = {
            'US', 'CA', 'MX', 'GB', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE',
            'CH', 'AT', 'SE', 'NO', 'DK', 'FI', 'PL', 'CZ', 'HU', 'SK',
            'SI', 'HR', 'BG', 'RO', 'GR', 'CY', 'MT', 'IE', 'PT', 'LU',
            'EE', 'LV', 'LT', 'JP', 'KR', 'CN', 'IN', 'AU', 'NZ', 'BR',
            'AR', 'CL', 'CO', 'PE', 'VE', 'UY', 'PY', 'BO', 'EC', 'GY',
            'SR', 'FK', 'ZA', 'EG', 'NG', 'KE', 'GH', 'MA', 'TN', 'DZ',
            'LY', 'SD', 'ET', 'UG', 'TZ', 'ZW', 'BW', 'NA', 'ZM', 'MW',
            'MZ', 'MG', 'MU', 'SC', 'KM', 'DJ', 'SO', 'ER', 'SS', 'CF',
            'CM', 'GQ', 'GA', 'CG', 'CD', 'AO', 'BI', 'RW', 'SL',
            'LR', 'CI', 'GN', 'GW', 'GM', 'SN', 'ML', 'BF', 'NE'
        }
        if v.upper() not in valid_countries:
            raise ValueError('Invalid country code')
        return v.upper()
    
    @field_validator('ssn_last4')
    @classmethod
    def validate_ssn_last4(cls, v):
        """Validate SSN last 4 digits."""
        if not re.match(r'^\d{4}$', v):
            raise ValueError('SSN last 4 digits must be exactly 4 digits')
        return v
    
    @field_validator('id_last4')
    @classmethod
    def validate_id_last4(cls, v):
        """Validate ID last 4 digits."""
        if not re.match(r'^\d{4}$', v):
            raise ValueError('ID last 4 digits must be exactly 4 digits')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name format."""
        if not re.match(NAME_PATTERN, v):
            raise ValueError('Full name contains invalid characters')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Validate city name format."""
        if not re.match(NAME_PATTERN, v):
            raise ValueError('City name contains invalid characters')
        return v.strip()


class LoanDataRequest(BaseModel):
    """Loan data request model."""
    
    loan_id: str = Field(..., min_length=1, max_length=100, description="Unique loan identifier")
    document_type: DocumentType = Field(..., description="Type of loan document")
    loan_amount: int = Field(..., ge=1, le=50_000_000, description="Loan amount in USD (1-50,000,000)")
    borrower_name: str = Field(..., min_length=2, max_length=255, description="Primary borrower's name")
    additional_notes: Optional[str] = Field(None, max_length=2000, description="Additional notes or comments")
    
    @field_validator('loan_id')
    @classmethod
    def validate_loan_id(cls, v):
        """Validate loan ID format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Loan ID can only contain alphanumeric characters, dashes, and underscores')
        return v
    
    @field_validator('borrower_name')
    @classmethod
    def validate_borrower_name(cls, v):
        """Validate borrower name format."""
        if not re.match(NAME_PATTERN, v):
            raise ValueError('Borrower name contains invalid characters')
        return v.strip()


class SealLoanDocumentRequest(BaseModel):
    """Complete loan document sealing request."""
    
    loan_data: LoanDataRequest = Field(..., description="Loan-specific data")
    borrower_info: BorrowerInfoRequest = Field(..., description="Borrower information")
    files: List[FileInfo] = Field(..., min_length=1, max_length=10, description="List of files to be sealed (1-10 files)")
    
    @model_validator(mode='after')
    def validate_borrower_name_consistency(self):
        """Ensure borrower name in loan_data matches full_name in borrower_info."""
        if self.loan_data.borrower_name.lower() != self.borrower_info.full_name.lower():
            raise ValueError('Borrower name in loan_data must match full_name in borrower_info')
        return self


class BorrowerInfoResponse(BaseModel):
    """Borrower information response model with masked sensitive data."""
    
    # Personal Information (masked)
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: date = Field(..., description="Date of birth")
    email: str = Field(..., description="Masked email address (e.g., j***@email.com)")
    phone: str = Field(..., description="Masked phone number (e.g., ***-***-1234)")
    
    # Address Information
    address_line1: str = Field(..., description="Primary street address")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="Two-letter state code")
    zip_code: str = Field(..., description="ZIP code")
    country: str = Field(..., description="Country code")
    
    # Identity Information (masked)
    ssn_last4: str = Field(..., description="Masked SSN (e.g., ****-**-1234)")
    id_type: IDType = Field(..., description="Type of government-issued ID")
    id_last4: str = Field(..., description="Masked ID number (e.g., ****-****-1234)")
    
    # Financial Information
    employment_status: EmploymentStatus = Field(..., description="Employment status")
    annual_income_range: str = Field(..., description="Income range (e.g., $75,000 - $99,999)")
    co_borrower_name: Optional[str] = Field(None, description="Co-borrower name")
    
    # Sealing Information
    is_sealed: bool = Field(..., description="Whether document is sealed in blockchain")
    walacor_tx_id: Optional[str] = Field(None, description=WALACOR_TX_ID_DESCRIPTION)
    seal_timestamp: Optional[str] = Field(None, description="ISO timestamp when sealed")


class SearchLoansRequest(BaseModel):
    """Search loans request model with query parameters."""
    
    # Search Filters
    borrower_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Search by borrower name")
    borrower_email: Optional[str] = Field(None, description="Search by borrower email")
    loan_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Search by exact loan ID")
    
    # Date Range Filters
    date_from: Optional[date] = Field(None, description="Filter from date (YYYY-MM-DD)")
    date_to: Optional[date] = Field(None, description="Filter to date (YYYY-MM-DD)")
    
    # Amount Range Filters
    amount_min: Optional[int] = Field(None, ge=0, le=50_000_000, description="Minimum loan amount")
    amount_max: Optional[int] = Field(None, ge=0, le=50_000_000, description="Maximum loan amount")
    
    # Pagination
    limit: int = Field(50, ge=1, le=1000, description="Number of results to return (1-1000)")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    
    # Additional Filters
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    employment_status: Optional[EmploymentStatus] = Field(None, description="Filter by employment status")
    is_sealed: Optional[bool] = Field(None, description="Filter by sealing status")
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range is logical."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError('date_from cannot be after date_to')
        return self
    
    @model_validator(mode='after')
    def validate_amount_range(self):
        """Validate amount range is logical."""
        if self.amount_min and self.amount_max and self.amount_min > self.amount_max:
            raise ValueError('amount_min cannot be greater than amount_max')
        return self


class LoanSearchResult(BaseModel):
    """Individual loan search result."""
    
    artifact_id: str = Field(..., description="Unique artifact identifier")
    loan_id: str = Field(..., description="Loan identifier")
    document_type: str = Field(..., description="Type of loan document")
    loan_amount: int = Field(..., description="Loan amount in USD")
    borrower_name: str = Field(..., description="Primary borrower name")
    borrower_email: str = Field(..., description="Masked borrower email")
    upload_date: str = Field(..., description="ISO timestamp when uploaded")
    sealed_status: str = Field(..., description="Sealing status")
    walacor_tx_id: Optional[str] = Field(None, description=WALACOR_TX_ID_DESCRIPTION)


class LoanSearchResponse(BaseModel):
    """Loan search response with pagination."""
    
    results: List[LoanSearchResult] = Field(..., description="List of matching loans")
    total_count: int = Field(..., ge=0, description="Total number of matching loans")
    has_more: bool = Field(..., description="Whether there are more results")
    limit: int = Field(..., description="Number of results returned")
    offset: int = Field(..., description="Number of results skipped")


class LoanDocumentSealResponse(BaseModel):
    """Response model for loan document sealing."""
    
    message: str = Field(..., description="Success message")
    artifact_id: str = Field(..., description="Unique artifact identifier")
    walacor_tx_id: str = Field(..., description=WALACOR_TX_ID_DESCRIPTION)
    hash: str = Field(..., description="SHA-256 hash of sealed document")
    sealed_at: str = Field(..., description="ISO timestamp when sealed")
    blockchain_proof: Optional[Dict[str, Any]] = Field(None, description="Blockchain proof data")
    signature_jwt: Optional[str] = Field(None, description="JWT signature of the canonical payload")


# Utility functions for data masking
def mask_email(email: str) -> str:
    """Mask email address for privacy."""
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 1:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number for privacy."""
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 4:
        return '***-***-' + digits[-4:]
    else:
        return '***-***-****'


def mask_ssn(ssn_last4: str) -> str:
    """Mask SSN for privacy."""
    return f"****-**-{ssn_last4}"


def mask_id(id_last4: str) -> str:
    """Mask ID number for privacy."""
    return f"****-****-{id_last4}"


def get_income_range(annual_income: int) -> str:
    """Convert annual income to range for privacy."""
    if annual_income < 25000:
        return "Under $25,000"
    elif annual_income < 50000:
        return "$25,000 - $49,999"
    elif annual_income < 75000:
        return "$50,000 - $74,999"
    elif annual_income < 100000:
        return "$75,000 - $99,999"
    elif annual_income < 150000:
        return "$100,000 - $149,999"
    elif annual_income < 200000:
        return "$150,000 - $199,999"
    elif annual_income < 300000:
        return "$200,000 - $299,999"
    elif annual_income < 500000:
        return "$300,000 - $499,999"
    else:
        return "$500,000+"
