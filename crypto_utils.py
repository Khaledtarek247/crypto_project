"""
crypto_utils.py
───────────────
Core cryptography functions for the CryptoLab project.
Uses PyCryptodome (Crypto) for all cryptographic operations.

Algorithms implemented:
  • AES (CBC, CFB, OFB, CTR, GCM) — 128 / 192 / 256-bit keys
  • DES (CBC, CFB, OFB)            — 56-bit effective key (64-bit with parity)

Enhancements over v1:
  • AES-GCM authenticated encryption (encrypt_aes_gcm / decrypt_aes_gcm)
  • Timing-safe byte comparison in verify_files (hmac.compare_digest)
  • key_fingerprint() — short SHA-256 digest for key display
  • compute_sha256()  — hash helper for integrity display
"""

import os
import json
import hmac
import base64
import hashlib
from Crypto.Cipher import AES, DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# ─────────────────────────────────────────────────────────────────────────────
# Key generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_aes_key(key_bits: int = 256) -> bytes:
    """Generate a random AES key of the specified bit length (128, 192, or 256)."""
    if key_bits not in (128, 192, 256):
        raise ValueError("AES key size must be 128, 192, or 256 bits.")
    return get_random_bytes(key_bits // 8)


def generate_des_key() -> bytes:
    """Generate a random 8-byte (64-bit / 56 effective bits) DES key."""
    return get_random_bytes(8)


# ─────────────────────────────────────────────────────────────────────────────
# AES encrypt / decrypt  (CBC, CFB, OFB, CTR)
# ─────────────────────────────────────────────────────────────────────────────

def encrypt_aes(data: bytes, key: bytes, mode_str: str = "CBC") -> tuple[bytes, dict]:
    """
    Encrypt *data* with AES using the given mode.

    Returns
    -------
    ciphertext : bytes
    metadata   : dict  — contains mode, iv/nonce (hex-encoded) needed for decryption
    """
    mode_str = mode_str.upper()
    meta: dict = {"algo": "AES", "mode": mode_str}

    if mode_str == "CBC":
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data, AES.block_size))
        meta["iv"] = iv.hex()

    elif mode_str == "CFB":
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        ct = cipher.encrypt(data)
        meta["iv"] = iv.hex()

    elif mode_str == "OFB":
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_OFB, iv)
        ct = cipher.encrypt(data)
        meta["iv"] = iv.hex()

    elif mode_str == "CTR":
        cipher = AES.new(key, AES.MODE_CTR)
        ct = cipher.encrypt(data)
        meta["nonce"] = cipher.nonce.hex()

    else:
        raise ValueError(f"Unsupported AES mode: {mode_str}")

    return ct, meta


def decrypt_aes(ciphertext: bytes, key: bytes, meta: dict) -> bytes:
    """Decrypt AES ciphertext using stored metadata (mode + iv/nonce)."""
    mode_str = meta["mode"].upper()

    if mode_str == "CBC":
        iv = bytes.fromhex(meta["iv"])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size)

    elif mode_str == "CFB":
        iv = bytes.fromhex(meta["iv"])
        cipher = AES.new(key, AES.MODE_CFB, iv)
        return cipher.decrypt(ciphertext)

    elif mode_str == "OFB":
        iv = bytes.fromhex(meta["iv"])
        cipher = AES.new(key, AES.MODE_OFB, iv)
        return cipher.decrypt(ciphertext)

    elif mode_str == "CTR":
        nonce = bytes.fromhex(meta["nonce"])
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext)

    else:
        raise ValueError(f"Unsupported AES mode: {mode_str}")


# ─────────────────────────────────────────────────────────────────────────────
# AES-GCM  (Authenticated Encryption with Associated Data)
# ─────────────────────────────────────────────────────────────────────────────

def encrypt_aes_gcm(data: bytes, key: bytes, aad: bytes = b"") -> tuple[bytes, dict]:
    """
    Encrypt *data* with AES-256-GCM, an authenticated encryption mode.

    AES-GCM provides both *confidentiality* (the ciphertext is encrypted)
    and *integrity / authenticity* (the 16-byte tag proves the ciphertext
    was not tampered with and was produced by someone who holds *key*).

    Parameters
    ----------
    data : bytes   — plaintext to encrypt
    key  : bytes   — 16 / 24 / 32-byte AES key
    aad  : bytes   — optional Additional Authenticated Data (authenticated
                     but NOT encrypted; e.g. header or context string)

    Returns
    -------
    ciphertext : bytes  — encrypted payload (same length as *data*)
    metadata   : dict   {
        "algo"  : "AES-GCM",
        "mode"  : "GCM",
        "nonce" : hex str (96-bit / 12 bytes — GCM standard),
        "tag"   : hex str (128-bit authentication tag),
        "aad"   : hex str (may be empty),
    }
    """
    nonce = get_random_bytes(12)          # 96-bit nonce is the GCM standard
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    ct, tag = cipher.encrypt_and_digest(data)
    return ct, {
        "algo":  "AES-GCM",
        "mode":  "GCM",
        "nonce": nonce.hex(),
        "tag":   tag.hex(),
        "aad":   aad.hex(),
    }


def decrypt_aes_gcm(ciphertext: bytes, key: bytes, meta: dict) -> bytes:
    """
    Decrypt AES-GCM ciphertext and *verify* the authentication tag.

    Raises
    ------
    ValueError  — if the tag verification fails (tampered ciphertext / wrong key).
    """
    nonce = bytes.fromhex(meta["nonce"])
    tag   = bytes.fromhex(meta["tag"])
    aad   = bytes.fromhex(meta.get("aad", ""))

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    if aad:
        cipher.update(aad)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as exc:
        raise ValueError(
            "GCM tag verification FAILED — ciphertext may have been tampered with."
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# DES encrypt / decrypt
# ─────────────────────────────────────────────────────────────────────────────

def encrypt_des(data: bytes, key: bytes, mode_str: str = "CBC") -> tuple[bytes, dict]:
    """
    Encrypt *data* with DES using the given mode.

    Note: DES is included for *educational comparison only*.
    Its 56-bit key space is considered insecure for real-world use.
    """
    mode_str = mode_str.upper()
    meta: dict = {"algo": "DES", "mode": mode_str}

    if mode_str == "CBC":
        iv = get_random_bytes(DES.block_size)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(data, DES.block_size))
        meta["iv"] = iv.hex()

    elif mode_str == "CFB":
        iv = get_random_bytes(DES.block_size)
        cipher = DES.new(key, DES.MODE_CFB, iv)
        ct = cipher.encrypt(data)
        meta["iv"] = iv.hex()

    elif mode_str == "OFB":
        iv = get_random_bytes(DES.block_size)
        cipher = DES.new(key, DES.MODE_OFB, iv)
        ct = cipher.encrypt(data)
        meta["iv"] = iv.hex()

    else:
        raise ValueError(f"Unsupported DES mode: {mode_str}")

    return ct, meta


def decrypt_des(ciphertext: bytes, key: bytes, meta: dict) -> bytes:
    """Decrypt DES ciphertext using stored metadata."""
    mode_str = meta["mode"].upper()
    iv = bytes.fromhex(meta["iv"])

    if mode_str == "CBC":
        cipher = DES.new(key, DES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), DES.block_size)

    elif mode_str == "CFB":
        cipher = DES.new(key, DES.MODE_CFB, iv)
        return cipher.decrypt(ciphertext)

    elif mode_str == "OFB":
        cipher = DES.new(key, DES.MODE_OFB, iv)
        return cipher.decrypt(ciphertext)

    else:
        raise ValueError(f"Unsupported DES mode: {mode_str}")


# ─────────────────────────────────────────────────────────────────────────────
# Metadata persistence helpers
# ─────────────────────────────────────────────────────────────────────────────

def save_metadata(meta: dict, path: str) -> None:
    """Save encryption metadata (IV, mode, algo) to a JSON file."""
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)


def load_metadata(path: str) -> dict:
    """Load encryption metadata from a JSON file."""
    with open(path) as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Verification & hashing helpers
# ─────────────────────────────────────────────────────────────────────────────

def verify_files(original: bytes, decrypted: bytes) -> bool:
    """
    Return True if *original* and *decrypted* are byte-identical.

    Uses hmac.compare_digest for timing-safe comparison, preventing
    timing side-channel attacks that could leak information about
    partial matches.
    """
    if len(original) != len(decrypted):
        return False
    return hmac.compare_digest(original, decrypted)


def compute_sha256(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def key_fingerprint(key: bytes, length: int = 16) -> str:
    """
    Return a short human-readable fingerprint of a key.

    Computes SHA-256 of the key and returns the first *length* hex
    characters in colon-separated pairs (e.g. ``A3:F1:2C:…``).
    Useful for displaying key identity without exposing the raw key.
    """
    digest = hashlib.sha256(key).hexdigest().upper()[:length]
    return ":".join(digest[i:i+2] for i in range(0, len(digest), 2))