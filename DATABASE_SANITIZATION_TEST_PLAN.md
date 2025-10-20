# Database Sanitization Test Plan

## Overview

Test the comprehensive data sanitization functionality that ensures all form fields are database-friendly by removing special characters, preventing SQL injection, and normalizing data formats for seamless database insertion.

## Sanitization Features Implemented

### 1. **Text Sanitization**
- Removes dangerous characters: `<>'"&`
- Keeps only alphanumeric, spaces, hyphens, periods, commas, parentheses
- Normalizes multiple spaces to single space
- Limits length to 255 characters

### 2. **Email Sanitization**
- Converts to lowercase
- Keeps only valid email characters: `a-z0-9@._-`
- Limits length to 100 characters

### 3. **Phone Sanitization**
- Keeps only digits, `+`, `-`, `(`, `)`, and spaces
- Normalizes spaces
- Limits length to 20 characters

### 4. **Numeric Sanitization**
- Keeps only digits and decimal point
- Prevents multiple decimal points
- Adds leading zero if starts with decimal
- Limits length to 15 characters

### 5. **Date Sanitization**
- Keeps only digits and hyphens
- Limits to 10 characters (YYYY-MM-DD format)

### 6. **SSN/ID Sanitization**
- Extracts only digits
- Takes last 4 digits for SSN
- Limits to 4 digits for ID numbers

### 7. **Address Sanitization**
- Removes dangerous characters
- Keeps alphanumeric, spaces, hyphens, periods, commas, hash
- Normalizes spaces
- Limits length to 100 characters

### 8. **City Sanitization**
- Keeps only letters, spaces, and hyphens
- Normalizes spaces
- Limits length to 50 characters

### 9. **State/Country Sanitization**
- Keeps only letters
- Converts to uppercase
- Limits to 2 characters

### 10. **ZIP Code Sanitization**
- Keeps only digits and hyphens
- Limits to 10 characters

### 11. **Enum Value Sanitization**
- Maps to valid enum values for:
  - Employment status
  - Government ID type
  - Document type

### 12. **Notes Sanitization**
- Removes dangerous characters
- Keeps alphanumeric, spaces, basic punctuation
- Normalizes spaces
- Limits length to 1000 characters

## Test Files

### 1. **Test File with Malicious Content: `test-sanitization.json`**
Contains:
- XSS attempts: `<script>alert('xss')</script>`
- SQL injection attempts: `'; DROP TABLE users; --`
- Special characters: `<>'"&`
- Invalid data formats
- Oversized inputs

### 2. **Sample Files for Testing**
- `test-auto-fill.json` - Clean data for comparison
- `sample-loan-document.json` - Standard loan document
- `test-sanitization.json` - Malicious content for testing

## Test Scenarios

### Scenario 1: XSS Prevention
**Input:** `"John Doe <script>alert('xss')</script>"`
**Expected Output:** `"John Doe"`
**Test:** Verify XSS scripts are completely removed

### Scenario 2: SQL Injection Prevention
**Input:** `"'; DROP TABLE users; --"`
**Expected Output:** `""`
**Test:** Verify SQL injection attempts are neutralized

### Scenario 3: Special Character Removal
**Input:** `"Test & Associates <>&\"'"`
**Expected Output:** `"Test  Associates"`
**Test:** Verify dangerous characters are removed

### Scenario 4: Email Normalization
**Input:** `"JOHN.DOE@EXAMPLE.COM<script>alert('xss')</script>"`
**Expected Output:** `"john.doe@example.com"`
**Test:** Verify email is normalized and XSS removed

### Scenario 5: Phone Number Cleaning
**Input:** `"+1-555-123-4567<script>alert('xss')</script>"`
**Expected Output:** `"+1-555-123-4567"`
**Test:** Verify phone format is preserved, XSS removed

### Scenario 6: Date Format Validation
**Input:** `"1990-05-20<script>alert('xss')</script>"`
**Expected Output:** `"1990-05-20"`
**Test:** Verify date format is preserved, XSS removed

### Scenario 7: SSN Last 4 Extraction
**Input:** `"***-**-1234<script>alert('xss')</script>"`
**Expected Output:** `"1234"`
**Test:** Verify only last 4 digits are extracted

### Scenario 8: Address Cleaning
**Input:** `"123 Main Street <>&\"'"`
**Expected Output:** `"123 Main Street"`
**Test:** Verify address is cleaned but readable

### Scenario 9: State/Country Code Normalization
**Input:** `"ny<script>alert('xss')</script>"`
**Expected Output:** `"NY"`
**Test:** Verify state code is normalized to uppercase

### Scenario 10: ZIP Code Cleaning
**Input:** `"10001<script>alert('xss')</script>"`
**Expected Output:** `"10001"`
**Test:** Verify ZIP code is cleaned

### Scenario 11: Enum Value Mapping
**Input:** `"EMPLOYED<script>alert('xss')</script>"`
**Expected Output:** `"employed"`
**Test:** Verify enum values are mapped correctly

### Scenario 12: Notes Sanitization
**Input:** `"Test notes <>&\"' <script>alert('xss')</script>"`
**Expected Output:** `"Test notes"`
**Test:** Verify notes are cleaned but readable

## Test Steps

### 1. **Upload Malicious JSON File**
1. Navigate to `http://localhost:3000/upload`
2. Upload `test-sanitization.json`
3. Observe auto-fill process

### 2. **Verify Sanitization**
1. ✅ Check that XSS scripts are removed
2. ✅ Verify special characters are cleaned
3. ✅ Confirm data formats are normalized
4. ✅ Ensure length limits are enforced
5. ✅ Validate enum values are mapped correctly

### 3. **Test Manual Input**
1. ✅ Type malicious content in form fields
2. ✅ Verify real-time sanitization
3. ✅ Check that dangerous characters are removed
4. ✅ Confirm data is normalized on input

### 4. **Test Form Submission**
1. ✅ Submit form with sanitized data
2. ✅ Verify backend receives clean data
3. ✅ Check database insertion succeeds
4. ✅ Confirm no SQL injection occurs

### 5. **Test Data Retrieval**
1. ✅ Retrieve stored data
2. ✅ Verify data is clean and safe
3. ✅ Check that sanitization is preserved
4. ✅ Confirm no XSS in displayed data

## Expected Results

### 1. **Security**
- ✅ No XSS vulnerabilities
- ✅ No SQL injection risks
- ✅ No dangerous characters in database
- ✅ All inputs are sanitized

### 2. **Data Integrity**
- ✅ Valid data formats preserved
- ✅ Length limits enforced
- ✅ Enum values mapped correctly
- ✅ Readable data maintained

### 3. **User Experience**
- ✅ Real-time sanitization feedback
- ✅ Clear error messages
- ✅ Form validation works
- ✅ Auto-fill functions correctly

### 4. **Database Compatibility**
- ✅ All fields are database-friendly
- ✅ No special characters cause issues
- ✅ Data insertion is seamless
- ✅ No encoding problems

## Test Commands

### Start the Application
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Test Files Available
- `test-sanitization.json` - Malicious content for testing
- `test-auto-fill.json` - Clean data for comparison
- `sample-loan-document.json` - Standard loan document

## Success Criteria

1. ✅ **XSS Prevention**: All script tags and dangerous HTML removed
2. ✅ **SQL Injection Prevention**: All SQL injection attempts neutralized
3. ✅ **Special Character Removal**: Dangerous characters removed
4. ✅ **Data Normalization**: Formats standardized (email lowercase, state uppercase)
5. ✅ **Length Limits**: All fields respect maximum length limits
6. ✅ **Enum Mapping**: Invalid enum values mapped to defaults
7. ✅ **Real-time Sanitization**: Input sanitized as user types
8. ✅ **Auto-fill Sanitization**: JSON data sanitized during auto-fill
9. ✅ **Form Submission**: Clean data sent to backend
10. ✅ **Database Insertion**: All data inserts successfully without errors

## Notes

- Sanitization happens at multiple levels:
  - Real-time input sanitization
  - Auto-fill sanitization
  - Pre-submission sanitization
  - Backend validation (additional layer)
- All sanitization preserves data readability while ensuring security
- Length limits prevent database overflow issues
- Enum mapping ensures data consistency
- The system is designed to be fail-safe: if sanitization fails, the field is cleared rather than allowing dangerous content

