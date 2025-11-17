"""Simple network client placeholder.
This is a minimal, synchronous TCP client used as a scaffold.
Replace with a real async or threaded client as needed.
"""
import socket
import sys
from shared import protocol

class ClientNetwork:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self, timeout=5):
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(10.0)  # Set timeout để tránh block vô hạn

    def send(self, message: dict):
        framed = protocol.encode(message)
        self.sock.sendall(framed)

    def receive(self):
        try:
            # read 4-byte length prefix
            raw_len = self.sock.recv(4)
            if not raw_len or len(raw_len) < 4:
                return None
            length = int.from_bytes(raw_len, 'big')
            payload = b''
            while len(payload) < length:
                chunk = self.sock.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk
            if len(payload) < length:
                return None
            # Dữ liệu đã được nén + mã hóa ở tầng protocol
            return protocol.decode(payload)
        except socket.timeout:
            print("[CLIENT] Receive timeout")
            return None
        except Exception as e:
            print(f"[CLIENT] Receive error: {e}")
            return None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
