#!/usr/bin/env python3
"""
Generate RSA key pair for JWT signing.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_jwt_keys():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Create secrets directory
    os.makedirs('secrets', exist_ok=True)
    
    # Write private key
    with open('secrets/jwt_private.pem', 'wb') as f:
        f.write(private_pem)
    
    # Write public key
    with open('secrets/jwt_public.pem', 'wb') as f:
        f.write(public_pem)
    
    print("✅ JWT keys generated successfully!")
    print("Private key: secrets/jwt_private.pem")
    print("Public key: secrets/jwt_public.pem")

if __name__ == "__main__":
    generate_jwt_keys()
