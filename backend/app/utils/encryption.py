"""Encryption utilities for sensitive data"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from app.config import settings


def get_encryption_key() -> bytes:
    """Get or generate encryption key"""
    encryption_key = settings.ENCRYPTION_KEY.encode()
    
    # Derive a 32-byte key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'ai_life_admin_salt',  # In production, use a random salt per user
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(encryption_key))
    return key


def encrypt_token(token: str) -> str:
    """Encrypt a token"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token"""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_token.encode())
    return decrypted.decode()
