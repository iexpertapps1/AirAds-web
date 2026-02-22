"""
AirAd Backend — AES-256-GCM Encryption Utilities (R2)

All phone numbers at rest are encrypted using AES-256-GCM with a random
96-bit IV prepended to the ciphertext. The key is loaded from
settings.ENCRYPTION_KEY (32-byte base64-encoded string).

Never use this module with a hardcoded key. Never store plaintext phone numbers.
"""

import base64
import logging
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""


def _get_key() -> bytes:
    """Decode the AES-256-GCM key from settings.

    Returns:
        32-byte key as raw bytes.

    Raises:
        EncryptionError: If ENCRYPTION_KEY is missing or not valid base64.
    """
    try:
        key = base64.b64decode(settings.ENCRYPTION_KEY)
    except Exception as e:
        raise EncryptionError(f"Invalid ENCRYPTION_KEY — must be base64-encoded 32 bytes: {e}") from e

    if len(key) != 32:
        raise EncryptionError(
            f"ENCRYPTION_KEY must decode to exactly 32 bytes, got {len(key)}"
        )
    return key


def encrypt(plaintext: str) -> bytes:
    """Encrypt a plaintext string using AES-256-GCM with a random IV.

    A fresh 96-bit (12-byte) IV is generated for every call — IVs are
    never reused. The IV is prepended to the ciphertext so that decrypt()
    can extract it without additional storage.

    Empty string input returns empty bytes without error (soft-delete
    and null-phone scenarios).

    Args:
        plaintext: The string to encrypt (e.g. a phone number).

    Returns:
        IV (12 bytes) + ciphertext + GCM tag as raw bytes.
        Returns b"" if plaintext is empty.

    Raises:
        EncryptionError: If the key is invalid or encryption fails.

    Example:
        >>> ciphertext = encrypt("+923001234567")
        >>> len(ciphertext) > 12
        True
    """
    if not plaintext:
        return b""

    try:
        key = _get_key()
        aesgcm = AESGCM(key)
        iv = os.urandom(12)  # 96-bit random IV — never reuse
        ciphertext = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
        return iv + ciphertext  # prepend IV for decryption
    except EncryptionError:
        raise
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}") from e


def decrypt(ciphertext: bytes) -> str:
    """Decrypt AES-256-GCM ciphertext produced by encrypt().

    Extracts the 12-byte IV from the head of the ciphertext, then
    decrypts the remainder.

    Args:
        ciphertext: Raw bytes produced by encrypt() — IV + ciphertext + tag.
            Pass b"" to receive "" (mirrors encrypt() empty-string behaviour).

    Returns:
        Decrypted plaintext string.
        Returns "" if ciphertext is empty.

    Raises:
        EncryptionError: If decryption fails (wrong key, tampered data, etc.).

    Example:
        >>> original = "+923001234567"
        >>> decrypt(encrypt(original)) == original
        True
    """
    if not ciphertext:
        return ""

    try:
        key = _get_key()
        aesgcm = AESGCM(key)
        iv, data = ciphertext[:12], ciphertext[12:]
        return aesgcm.decrypt(iv, data, None).decode("utf-8")
    except EncryptionError:
        raise
    except Exception as e:
        raise EncryptionError(f"Decryption failed: {e}") from e
