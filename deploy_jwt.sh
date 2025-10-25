#!/bin/bash
# 🔐 JWT Digital Signature Quick Deploy Script
# This script sets up the complete JWT implementation on any FastAPI project

set -e  # Exit on any error

echo "🔐 JWT Digital Signature Implementation Setup"
echo "============================================="

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
mkdir -p src tests alembic/versions

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

# Step 4: Create .env template
echo "⚙️ Creating .env template..."
cat > .env.example << 'EOF'
# JWT Digital Signature Configuration
JWT_PRIVATE_KEY_PATH=jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=jwt_public_key.pem
JWT_ISSUER=your-app-name
JWT_TTL_SECONDS=3600

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
echo "🎉 JWT Setup Complete!"
echo "======================"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure"
echo "2. Copy jwt_service.py from the JWT implementation guide"
echo "3. Add JWT integration to your main.py"
echo "4. Run database migration for signature_jwt column"
echo ""
echo "📚 See JWT_IMPLEMENTATION_GUIDE.md for detailed instructions"
echo "🔐 Your JWT keys are ready for production use!"
