"""JSON-based protocol helpers for encoding/decoding messages."""
import json
from typing import Any, Dict

def encode(message: Dict[str, Any]) -> bytes:
    data = json.dumps(message).encode('utf-8')
    return len(data).to_bytes(4, 'big') + data

def decode(stream_bytes: bytes) -> Dict[str, Any]:
    # expects stream_bytes to be exactly the JSON payload (no length prefix)
    return json.loads(stream_bytes.decode('utf-8'))
