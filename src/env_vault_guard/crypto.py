import base64
import hashlib
import hmac
import os
import secrets
from typing import Tuple


class EnvCrypto:
    """Zero-dependency password-based encrypted secrets container for .env files."""

    ITERATIONS = 100_000

    @classmethod
    def _derive_keys(cls, passphrase: str, salt: bytes) -> Tuple[bytes, bytes]:
        key_material = hashlib.pbkdf2_hmac(
            "sha256", passphrase.encode("utf-8"), salt, cls.ITERATIONS, dklen=64
        )
        enc_key = key_material[:32]
        mac_key = key_material[32:]
        return enc_key, mac_key

    @classmethod
    def _keystream(cls, key: bytes, nonce: bytes, length: int) -> bytes:
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            block = hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    @classmethod
    def encrypt(cls, plaintext: str, passphrase: str) -> str:
        data = plaintext.encode("utf-8")
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(16)
        enc_key, mac_key = cls._derive_keys(passphrase, salt)

        keystream = cls._keystream(enc_key, nonce, len(data))
        ciphertext = bytes(a ^ b for a, b in zip(data, keystream))

        tag = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).digest()
        payload = salt + nonce + tag + ciphertext
        return base64.b64encode(payload).decode("utf-8")

    @classmethod
    def decrypt(cls, payload_b64: str, passphrase: str) -> str:
        try:
            payload = base64.b64decode(payload_b64.encode("utf-8"))
        except Exception as e:
            raise ValueError(f"Invalid base64 payload: {e}")

        if len(payload) < 64:
            raise ValueError("Invalid encrypted payload size")

        salt = payload[:16]
        nonce = payload[16:32]
        expected_tag = payload[32:64]
        ciphertext = payload[64:]

        enc_key, mac_key = cls._derive_keys(passphrase, salt)
        calculated_tag = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).digest()

        if not hmac.compare_digest(expected_tag, calculated_tag):
            raise ValueError("Decryption failed: Incorrect passphrase or tampered payload")

        keystream = cls._keystream(enc_key, nonce, len(ciphertext))
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, keystream))
        return plaintext.decode("utf-8")
