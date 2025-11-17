"""Protocol helpers for encoding/decoding messages.

Features:
- JSON serialisation
- Optional gzip compression
- Optional lightweight XOR-based "encryption" (for demo/assignment only)
- 4-byte big-endian length prefix framing
"""

import json
import gzip
from typing import Any, Dict

# NOTE: Đây KHÔNG phải mã hóa an toàn, chỉ phục vụ mục đích bài tập.
_SECRET_KEY = b"ltm_simple_key"


def _xor_bytes(data: bytes, key: bytes = _SECRET_KEY) -> bytes:
    """Lightweight XOR cipher – do NOT use in real production."""
    if not key:
        return data
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def encode(message: Dict[str, Any], *, compress: bool = True, encrypt: bool = True) -> bytes:
    """Encode message dict -> framed bytes (length prefix + payload)."""
    # JSON
    payload = json.dumps(message).encode("utf-8")

    # Gzip compression (tùy chọn)
    if compress:
        payload = gzip.compress(payload)

    # XOR "encryption" (tùy chọn)
    if encrypt:
        payload = _xor_bytes(payload)

    # 4 byte length prefix
    return len(payload).to_bytes(4, "big") + payload


def decode(framed_bytes: bytes, *, compress: bool = True, encrypt: bool = True) -> Dict[str, Any]:
    """Decode framed bytes (không gồm length prefix) -> message dict."""
    payload = framed_bytes

    # Giải mã XOR (nếu có)
    if encrypt:
        payload = _xor_bytes(payload)

    # Giải nén gzip (nếu có)
    if compress:
        payload = gzip.decompress(payload)

    return json.loads(payload.decode("utf-8"))

