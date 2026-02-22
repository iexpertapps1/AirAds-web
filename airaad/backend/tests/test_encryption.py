"""
Tests for core/encryption.py — AES-256-GCM encrypt/decrypt.
"""

import base64

import pytest
from django.test import override_settings

from core.encryption import EncryptionError, decrypt, encrypt

VALID_KEY = base64.b64encode(b"a" * 32).decode()


@pytest.mark.unit
class TestEncryption:
    """Unit tests for AES-256-GCM encryption utilities."""

    def test_encrypt_returns_bytes(self):
        """encrypt() returns bytes."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            result = encrypt("+923001234567")
        assert isinstance(result, bytes)

    def test_encrypt_decrypt_roundtrip(self):
        """decrypt(encrypt(x)) == x for any non-empty string."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            plaintext = "+923001234567"
            assert decrypt(encrypt(plaintext)) == plaintext

    def test_encrypt_empty_returns_empty_bytes(self):
        """encrypt('') returns b''."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            assert encrypt("") == b""

    def test_decrypt_empty_returns_empty_string(self):
        """decrypt(b'') returns ''."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            assert decrypt(b"") == ""

    def test_encrypt_produces_unique_ciphertext(self):
        """Two encryptions of the same plaintext produce different ciphertext (random IV)."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            ct1 = encrypt("+923001234567")
            ct2 = encrypt("+923001234567")
        assert ct1 != ct2

    def test_ciphertext_length_includes_iv(self):
        """Ciphertext is at least 12 bytes (IV) + 1 byte (data) + 16 bytes (GCM tag)."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            ct = encrypt("x")
        assert len(ct) >= 29  # 12 IV + 1 data + 16 GCM tag

    def test_invalid_key_raises_encryption_error(self):
        """Invalid ENCRYPTION_KEY raises EncryptionError."""
        with override_settings(ENCRYPTION_KEY="not-valid-base64!!!"):
            with pytest.raises(EncryptionError):
                encrypt("test")

    def test_wrong_length_key_raises_encryption_error(self):
        """Key that decodes to != 32 bytes raises EncryptionError."""
        short_key = base64.b64encode(b"short").decode()
        with override_settings(ENCRYPTION_KEY=short_key):
            with pytest.raises(EncryptionError):
                encrypt("test")

    def test_tampered_ciphertext_raises_encryption_error(self):
        """Tampered ciphertext raises EncryptionError on decrypt."""
        with override_settings(ENCRYPTION_KEY=VALID_KEY):
            ct = bytearray(encrypt("+923001234567"))
            ct[-1] ^= 0xFF  # flip last byte
            with pytest.raises(EncryptionError):
                decrypt(bytes(ct))
