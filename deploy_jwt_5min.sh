#!/bin/bash
# 🔐 JWT Digital Signature Quick Deploy Script - 5 MINUTE TOKENS
# This script sets up JWT implementation with enhanced security (5-minute token expiration)

set -e  # Exit on any error

echo "🔐 JWT Digital Signature Setup - 5 MINUTE TOKENS"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] && [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: No requirements.txt or pyproject.toml found. Are you in a Python project directory?"
    exit 1
fi

echo "✅ Python project detected"

# Step 1: Install dependencies
echo "📦 Installing JWT dependencies..."
if [ -f "requirements.txt" ]; then
    echo "cryptography>=41.0.0" >> requirements.txt
    echo "PyJWT>=2.8.0" >> requirements.txt
    pip install cryptography PyJWT
else
    echo "Please add 'cryptography>=41.0.0' and 'PyJWT>=2.8.0' to your dependencies"
fi

# Step 2: Create directories
echo "📁 Creating directory structure..."
mkdir -p src tests

# Step 3: Generate JWT keys
echo "🔑 Generating JWT keys..."
python3 << 'EOF'
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate private key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Serialize keys
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write to files
with open('jwt_private_key.pem', 'wb') as f: f.write(private_pem)
with open('jwt_public_key.pem', 'wb') as f: f.write(public_pem)

print("✅ JWT keys generated: jwt_private_key.pem, jwt_public_key.pem")
EOF

# Step 4: Create .env template with 5-minute expiration
echo "⚙️ Creating .env template with 5-minute token expiration..."
cat > .env.example << 'EOF'
# JWT Digital Signature Configuration - 5 MINUTE TOKENS
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=your-app-name
JWT_TTL_SECONDS=300

# 🔒 SECURITY NOTICE: 
# Tokens expire in 5 minutes (300 seconds) for enhanced security
# Perfect for high-security applications requiring short-lived tokens
# Copy this file to .env and configure your settings
EOF

# Step 5: Update .gitignore
echo "🔒 Updating .gitignore for security..."
cat >> .gitignore << 'EOF'

# JWT Keys (NEVER commit these!)
jwt_private_key.pem
jwt_public_key.pem
*.pem

# Environment files
.env
.env.local
EOF

echo ""
echo "🎉 JWT Setup Complete - 5 MINUTE TOKENS!"
echo "========================================"
echo ""
echo "⏰ TOKEN CONFIGURATION:"
echo "   • Token Lifetime: 5 minutes (300 seconds)"
echo "   • Enhanced Security: Short-lived tokens"
echo "   • Perfect for: Financial, legal, medical documents"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure"
echo "2. Copy jwt_service.py from your JWT repository"
echo "3. Add JWT integration to your main.py"
echo "4. Run database migration for signature_jwt column"
echo "5. Test token expiration after 5 minutes"
echo ""
echo "📚 See CLONE_AND_APPLY_JWT_GUIDE.md for detailed instructions"
echo "🔐 Your JWT keys are ready for high-security production use!"
