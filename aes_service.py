import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from config import AES_SECRET_KEY


def _load_key() -> bytes:
    if not AES_SECRET_KEY:
        raise ValueError("AES_SECRET_KEY is not configured.")

    try:
        key = base64.b64decode(AES_SECRET_KEY, validate=True)
    except Exception:
        key = AES_SECRET_KEY.encode("utf-8")

    if len(key) not in (16, 24, 32):
        raise ValueError("AES_SECRET_KEY must be 16, 24, or 32 bytes.")
    return key


def encrypt_text(data: str) -> str:
    key = _load_key()
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode("utf-8"))
    return base64.b64encode(nonce + tag + ciphertext).decode("utf-8")


def decrypt_text(encrypted_data: str) -> str:
    key = _load_key()
    raw_data = base64.b64decode(encrypted_data)
    nonce = raw_data[:12]
    tag = raw_data[12:28]
    ciphertext = raw_data[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8")


# Backward-compatible aliases for backend-only encrypted metadata.
encrypt_log = encrypt_text
decrypt_log = decrypt_text
