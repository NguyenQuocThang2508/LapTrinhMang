"""Minimal multiplayer TCP server compatible with the client.

Protocol: 4-byte big-endian length prefix + JSON payload (utf-8).
Messages from client:
- {"type":"join", "name": str}
- {"type":"move", "id": str, "x": float, "y": float}
- {"type":"leave", "id": str}
- {"type":"checkin", "coins": int}            # optional, no-op
- {"type":"quiz_claim", "coins": int}          # optional, no-op

Server sends:
- {"type":"joined", "id": str}
- {"type":"state", "players": {id: {x,y,hp,name}}, "obstacles": {oid:{x,y,width,height}}, "goal": {x,y,width,height}|null, "level": int}
- {"type":"join", "id": str}
- {"type":"leave", "id": str}
- {"type":"level", "level": int, "obstacles": {}, "goal": null}
"""

import json
import socket
import threading
import time
import uuid
from typing import Dict, Any

HOST = '0.0.0.0'
PORT = 5000


def send_message(sock: socket.socket, message: Dict[str, Any]):
    data = json.dumps(message).encode('utf-8')
    length = len(data).to_bytes(4, 'big')
    sock.sendall(length + data)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError('socket closed')
        buf += chunk
    return buf


def receive_message(sock: socket.socket) -> Dict[str, Any]:
    raw_len = recv_exact(sock, 4)
    length = int.from_bytes(raw_len, 'big')
    payload = recv_exact(sock, length)
    return json.loads(payload.decode('utf-8'))


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[str, socket.socket] = {}
        self.players: Dict[str, Dict[str, Any]] = {}
        self.level = 1
        self.obstacles: Dict[str, Dict[str, Any]] = {}
        self.goal: Dict[str, Any] | None = None
        self.lock = threading.Lock()
        self.running = True
        self._build_level(self.level)

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Server listening on {self.host}:{self.port}")
        threading.Thread(target=self._broadcast_loop, daemon=True).start()
        # Tạo luồng tăng level demo mỗi 30 giây
        threading.Thread(target=self._level_timer_loop, daemon=True).start()
        try:
            while self.running:
                conn, addr = self.sock.accept()
                print(f"New connection from {addr}")
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
        finally:
            self.sock.close()

    def _level_timer_loop(self):
        while self.running:
            time.sleep(30)
            try:
                self.next_level()
            except Exception:
                pass

    def _broadcast_loop(self):
        # Periodically send state to all clients
        while self.running:
            time.sleep(0.05)  # ~20 Hz
            with self.lock:
                if not self.clients:
                    continue
                state = {
                    'type': 'state',
                    'players': self.players,
                    'obstacles': self.obstacles,
                    'goal': self.goal,
                    'level': self.level,
                }
                dead_ids = []
                for pid, csock in self.clients.items():
                    try:
                        send_message(csock, state)
                    except Exception:
                        dead_ids.append(pid)
                for pid in dead_ids:
                    self._disconnect(pid)

    def _handle_client(self, conn: socket.socket):
        player_id = None
        try:
            # Expect a join message first
            join_msg = receive_message(conn)
            if join_msg.get('type') != 'join':
                raise ConnectionError('Expected join message')
            player_id = str(uuid.uuid4())[:8]
            name = join_msg.get('name') or ''
            with self.lock:
                self.clients[player_id] = conn
                self.players[player_id] = {'x': 400.0, 'y': 300.0, 'hp': 100, 'name': name}
            # Ack join
            send_message(conn, {'type': 'joined', 'id': player_id})
            # Gửi level hiện tại cho client mới
            with self.lock:
                send_message(conn, {
                    'type': 'level',
                    'level': self.level,
                    'obstacles': self.obstacles,
                    'goal': self.goal,
                })
            self._broadcast({'type': 'join', 'id': player_id})

            # Handle subsequent messages
            while True:
                msg = receive_message(conn)
                mtype = msg.get('type')
                if mtype == 'move':
                    x = float(msg.get('x', 0.0))
                    y = float(msg.get('y', 0.0))
                    with self.lock:
                        if player_id in self.players:
                            self.players[player_id]['x'] = max(0.0, min(800.0, x))
                            self.players[player_id]['y'] = max(0.0, min(600.0, y))
                elif mtype == 'leave':
                    break
                elif mtype == 'goal':
                    print(f"[SERVER] GOAL REACHED BY {player_id}, switching to next level...")
                    with self.lock:
                        self.next_level()
                elif mtype in ('checkin', 'quiz_claim'):
                    # Optional: could persist coins or validate here
                    pass
                else:
                    # ignore unknown
                    pass
        except Exception as e:
            # print(e)
            pass
        finally:
            if player_id:
                self._disconnect(player_id)

    def _broadcast(self, message: Dict[str, Any]):
        with self.lock:
            dead_ids = []
            for pid, csock in self.clients.items():
                try:
                    send_message(csock, message)
                except Exception:
                    dead_ids.append(pid)
            for pid in dead_ids:
                self._disconnect(pid)

    def _disconnect(self, player_id: str):
        with self.lock:
            csock = self.clients.pop(player_id, None)
            if csock:
                try:
                    csock.close()
                except Exception:
                    pass
            if player_id in self.players:
                del self.players[player_id]
        # notify others
        self._broadcast({'type': 'leave', 'id': player_id})

    # ---------- Level building ----------
    def _build_level(self, level: int):
        # Tạo chướng ngại vật và goal mẫu theo level
        obs: Dict[str, Dict[str, Any]] = {}
        if level % 2 == 1:
            # Level lẻ: hành lang dọc
            for i in range(5):
                obs[f'o{i}'] = {'x': 150 + i * 100, 'y': 200, 'width': 60, 'height': 40}
            goal = {'x': 740, 'y': 520, 'width': 40, 'height': 40}
        else:
            # Level chẵn: bức tường ngang
            for i in range(6):
                obs[f'o{i}'] = {'x': 100 + i * 110, 'y': 320, 'width': 50, 'height': 50}
            goal = {'x': 60, 'y': 60, 'width': 40, 'height': 40}
        self.obstacles = obs
        self.goal = goal

    def next_level(self):
        with self.lock:
            self.level += 1
            self._build_level(self.level)
            self._broadcast({'type': 'level', 'level': self.level, 'obstacles': self.obstacles, 'goal': self.goal})


if __name__ == '__main__':
    Server(HOST, PORT).start()


