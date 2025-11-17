from shared.protocol import encode, decode


def test_protocol_roundtrip():
    msg = {'type':'ping', 'payload':{'x':1}}
    encoded = encode(msg)
    # strip length prefix for decode helper
    payload = encoded[4:]
    decoded = decode(payload)
    assert decoded == msg
