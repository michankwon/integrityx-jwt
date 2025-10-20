# Auto-Fill Functionality Test Plan

## Overview

Test the automatic form filling functionality when users upload JSON files containing loan and borrower data. This feature should extract relevant information from the JSON file and populate the form fields automatically.

## Test Files

### 1. Test JSON File: `test-auto-fill.json`
- Contains structured loan and borrower data
- Includes all required fields for auto-filling
- Tests various field mappings and data extraction

### 2. Sample Files for Testing
- `sample-loan-document.json` - Complete loan document structure
- `sample-simple.json` - Financial statement (different structure)
- `test-auto-fill.json` - Custom test file with specific data

## Test Scenarios

### Scenario 1: Complete JSON Auto-Fill
**File:** `test-auto-fill.json`

**Expected Auto-Filled Fields:**
- ✅ Loan ID: "AUTO_FILL_TEST_001"
- ✅ Document Type: "loan_application"
- ✅ Loan Amount: 300000
- ✅ Borrower Name: "Jane Doe"
- ✅ Additional Notes: "Auto-fill test document for loan application"

**Borrower Information:**
- ✅ Full Name: "Jane Doe"
- ✅ Email: "jane.doe@example.com"
- ✅ Phone: "+1-555-9876"
- ✅ Date of Birth: "1990-05-20"
- ✅ Street Address: "456 Oak Street"
- ✅ City: "San Francisco"
- ✅ State: "CA"
- ✅ ZIP Code: "94102"
- ✅ Country: "US"
- ✅ SSN Last 4: "5678"
- ✅ ID Type: "passport"
- ✅ ID Last 4: "9012"
- ✅ Employment Status: "self_employed"
- ✅ Annual Income: 85000
- ✅ Co-Borrower Name: "John Doe"

### Scenario 2: Partial JSON Auto-Fill
**File:** `sample-simple.json` (Financial Statement)

**Expected Behavior:**
- ✅ Should attempt to extract any available loan-related data
- ✅ Should not error if fields are missing
- ✅ Should show appropriate success message with count of fields filled

### Scenario 3: Invalid JSON File
**File:** Invalid JSON or non-JSON file

**Expected Behavior:**
- ✅ Should show error message: "Failed to auto-fill form from JSON file. Please check file format."
- ✅ Should not crash the application
- ✅ Should continue with normal file upload process

## Test Steps

### 1. Navigate to Upload Page
```
http://localhost:3000/upload
```

### 2. Upload JSON File
1. Click "Choose File" or drag and drop
2. Select `test-auto-fill.json`
3. Observe the auto-fill process

### 3. Verify Auto-Fill Process
1. ✅ Check for "Auto-filling form..." indicator
2. ✅ Verify success toast: "✅ Auto-filled X fields from JSON file!"
3. ✅ Check that form fields are populated correctly
4. ✅ Verify that existing data is preserved (not overwritten)

### 4. Test Form Validation
1. ✅ Verify that auto-filled data passes validation
2. ✅ Check that required fields are marked correctly
3. ✅ Test that form can be submitted successfully

### 5. Test Different File Types
1. ✅ Upload PDF file - should not attempt auto-fill
2. ✅ Upload non-JSON file - should not attempt auto-fill
3. ✅ Upload invalid JSON - should show error message

## Expected UI Behavior

### 1. Visual Indicators
- ✅ "Auto-filling form..." spinner during processing
- ✅ Success toast with count of fields filled
- ✅ Error toast if auto-fill fails
- ✅ Form fields populated with extracted data

### 2. User Experience
- ✅ Auto-fill happens automatically on JSON file upload
- ✅ No manual intervention required
- ✅ Existing form data is preserved (not overwritten)
- ✅ User can still manually edit auto-filled fields

### 3. Error Handling
- ✅ Graceful handling of invalid JSON
- ✅ Clear error messages for users
- ✅ Application continues to work normally

## Success Criteria

1. ✅ JSON files automatically populate form fields
2. ✅ Auto-fill works with various JSON structures
3. ✅ Visual feedback during auto-fill process
4. ✅ Error handling for invalid files
5. ✅ Existing form data is preserved
6. ✅ Auto-filled data passes validation
7. ✅ Form can be submitted successfully after auto-fill

## Test Commands

### Start the Application
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Test Files Available
- `test-auto-fill.json` - Custom test file
- `sample-loan-document.json` - Complete loan document
- `sample-simple.json` - Financial statement

## Notes

- Auto-fill only works with JSON files
- PDF and other file types are ignored for auto-fill
- Auto-fill preserves existing form data (doesn't overwrite)
- User can manually edit any auto-filled fields
- Auto-fill happens immediately after file selection
- Success message shows count of fields that were filled

