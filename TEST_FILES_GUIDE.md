# IntegrityX Test Files Guide

## 🧪 Available Test Files

### 1. **SIMPLE_TEST_FILE.json** ⭐ **RECOMMENDED FOR BASIC TESTING**
- **Purpose**: Basic functionality testing
- **Features**: Standard loan application with borrower information
- **Use Case**: First-time testing, basic upload verification
- **Size**: Small and simple
- **Fields**: All required fields for standard sealing

### 2. **QUANTUM_SAFE_TEST_FILE.json** 🔬 **FOR QUANTUM-SAFE TESTING**
- **Purpose**: Quantum-safe cryptography testing
- **Features**: Advanced security features, quantum-resistant algorithms
- **Use Case**: Testing quantum-safe mode, future-proof security
- **Size**: Medium complexity
- **Fields**: All required fields + quantum-safe metadata

### 3. **COMPREHENSIVE_TEST_FILE.json** 📋 **FOR COMPLETE TESTING**
- **Purpose**: Full system testing with all features
- **Features**: Complete loan application with KYC, compliance, audit trail
- **Use Case**: End-to-end testing, compliance verification
- **Size**: Large and comprehensive
- **Fields**: All possible fields and metadata

---

## 🚀 How to Test

### **Step 1: Start the System**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### **Step 2: Access Upload Page**
- Open browser: `http://localhost:3000/upload`
- You should see the upload page with all features

### **Step 3: Test Basic Upload (Recommended First)**
1. **Select File**: Choose `SIMPLE_TEST_FILE.json`
2. **Auto-fill**: Form should automatically populate with data
3. **Security Mode**: Choose "Standard Security" first
4. **Upload**: Click "Upload & Seal"
5. **Verify**: Check for success message and transaction ID

### **Step 4: Test Quantum-Safe Mode**
1. **Select File**: Choose `QUANTUM_SAFE_TEST_FILE.json`
2. **Security Mode**: Enable "🔬 Quantum-Safe Mode"
3. **Upload**: Click "Upload & Seal (Quantum-Safe)"
4. **Verify**: Check for quantum-safe features in success message

### **Step 5: Test Comprehensive Features**
1. **Select File**: Choose `COMPREHENSIVE_TEST_FILE.json`
2. **Review**: Check all auto-filled fields
3. **Security Mode**: Try different security levels
4. **Upload**: Test with maximum security
5. **Verify**: Check complete audit trail

---

## ✅ What to Look For

### **Successful Upload Indicators**
- ✅ **File Selected**: File name appears in upload area
- ✅ **Auto-fill**: Form fields populate automatically
- ✅ **Validation**: No red error messages
- ✅ **Upload Button**: Changes to "Upload & Seal" (not disabled)
- ✅ **Progress**: Loading spinner during upload
- ✅ **Success Modal**: Shows transaction ID and seal details
- ✅ **Transaction ID**: Format like `TX_1234567890_abcdef12`

### **Quantum-Safe Features**
- ✅ **Security Badges**: Purple badges showing quantum-safe features
- ✅ **Algorithms**: SHAKE256, BLAKE3, SHA3-512, Dilithium2
- ✅ **Security Level**: "hybrid" or "quantum_safe"
- ✅ **Future-Proof**: Protection against quantum computers

### **Error Indicators**
- ❌ **Red Fields**: Validation errors
- ❌ **Error Messages**: Specific error descriptions
- ❌ **Upload Failed**: Network or server errors
- ❌ **No Transaction ID**: Sealing failed

---

## 🔧 Troubleshooting

### **"File Not Selected"**
- Make sure you're selecting a `.json` file
- Check file is in the project root directory
- Try refreshing the page

### **"Auto-fill Not Working"**
- Check browser console for errors
- Verify JSON file format is valid
- Try a different test file

### **"Upload Failed"**
- Check backend is running (`python main.py`)
- Verify Walacor connection in health check
- Check browser network tab for API errors

### **"No Transaction ID"**
- Check backend logs for errors
- Verify `.env` file has correct Walacor credentials
- Try with "Standard Security" first

---

## 📊 Test Scenarios

### **Scenario 1: Basic Functionality**
1. Upload `SIMPLE_TEST_FILE.json`
2. Use Standard Security
3. Verify basic sealing works
4. Test document verification

### **Scenario 2: Quantum-Safe Security**
1. Upload `QUANTUM_SAFE_TEST_FILE.json`
2. Enable Quantum-Safe Mode
3. Verify quantum-resistant algorithms
4. Check future-proof security

### **Scenario 3: Complete System**
1. Upload `COMPREHENSIVE_TEST_FILE.json`
2. Test all security levels
3. Verify KYC data collection
4. Check audit trail generation

### **Scenario 4: Error Handling**
1. Try uploading invalid JSON
2. Test with missing required fields
3. Verify error messages are clear
4. Test network failure scenarios

---

## 🎯 Success Criteria

### **Basic Test Passes If:**
- ✅ File uploads successfully
- ✅ Transaction ID is generated
- ✅ Document appears in documents list
- ✅ Verification works correctly

### **Quantum-Safe Test Passes If:**
- ✅ Quantum-safe mode works
- ✅ Advanced algorithms are used
- ✅ Security badges display correctly
- ✅ Future-proof features are active

### **Comprehensive Test Passes If:**
- ✅ All fields auto-fill correctly
- ✅ Data sanitization works
- ✅ Encryption/decryption functions
- ✅ Complete audit trail is created

---

## 📝 Test Results Template

```
Test Date: ___________
Tester: ___________
Backend Version: ___________
Frontend Version: ___________

Basic Upload Test:
[ ] SIMPLE_TEST_FILE.json uploaded successfully
[ ] Transaction ID received: ___________
[ ] Document verification works
[ ] No errors in console

Quantum-Safe Test:
[ ] QUANTUM_SAFE_TEST_FILE.json uploaded successfully
[ ] Quantum-safe mode enabled
[ ] Security badges displayed
[ ] Advanced algorithms used: ___________

Comprehensive Test:
[ ] COMPREHENSIVE_TEST_FILE.json uploaded successfully
[ ] All fields auto-filled correctly
[ ] Data sanitization worked
[ ] Complete audit trail created

Issues Found:
- ___________
- ___________
- ___________

Overall Status: [ ] PASS [ ] FAIL
```

---

## 🆘 Getting Help

### **If Tests Fail:**
1. Check the troubleshooting section above
2. Review browser console for errors
3. Check backend logs in terminal
4. Verify all services are running
5. Test with the simplest file first

### **For Support:**
- Check `PROJECT_DOCUMENTATION.md` for technical details
- Review `SIMPLE_PROJECT_GUIDE.md` for non-technical help
- Check backend logs for detailed error messages
- Verify environment configuration

---

**Remember**: Start with `SIMPLE_TEST_FILE.json` for basic testing, then move to more complex files once basic functionality is confirmed! 🚀
