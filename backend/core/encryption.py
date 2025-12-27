from cryptography.fernet import Fernet

from core.config import settings


def get_cipher() -> Fernet:
    """Get Fernet cipher instance using the configured encryption key."""
    return Fernet(settings.token_encryption_key.encode())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token using Fernet symmetric encryption."""
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(plaintext.encode())
    return encrypted_bytes.decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a token using Fernet symmetric encryption."""
    cipher = get_cipher()
    decrypted_bytes = cipher.decrypt(ciphertext.encode())
    return decrypted_bytes.decode()
