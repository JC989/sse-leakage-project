import hashlib
import hmac
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12  # 12 bytes(96 bits) is the recommended nonce length for AES-GCM by NIST.


@dataclass(frozen=True)
class Keys:
    """Client keys derived from the master key."""

    token_key: bytes
    encryption_key: bytes


def generate_master_key() -> bytes:
    """Generate a random 32-byte master key for AES-256 encryption."""
    return os.urandom(32)


def derive_subkey(master_key: bytes, label: bytes) -> bytes:
    """Derive a 32-byte subkey for one purpose, named by label."""
    return hmac.new(master_key, label, hashlib.sha256).digest()


def derive_keys(master_key: bytes) -> Keys:
    """Split the master key into separate token and encryption keys."""
    return Keys(
        token_key=derive_subkey(master_key, b"token"),
        encryption_key=derive_subkey(master_key, b"encryption"),
    )


def make_token(token_key: bytes, keyword: str) -> bytes:
    """Return the 32-byte HMAC search token for an already-cleaned keyword."""
    return hmac.new(token_key, keyword.encode("utf-8"), hashlib.sha256).digest()


def encrypt(encryption_key: bytes, plaintext: bytes, associated_data: bytes) -> bytes:
    """Encrypt with AES-GCM under a fresh random nonce; returns nonce || ciphertext."""
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(encryption_key).encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext


def decrypt(encryption_key: bytes, blob: bytes, associated_data: bytes) -> bytes:
    """Reverse encrypt(). Raises InvalidTag if blob or associated_data was altered."""
    nonce, ciphertext = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    return AESGCM(encryption_key).decrypt(nonce, ciphertext, associated_data)
