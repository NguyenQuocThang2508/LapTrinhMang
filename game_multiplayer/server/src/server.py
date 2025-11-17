"""Simple TCP server scaffold for the multiplayer game.
This is a minimal, single-threaded accept loop that reads length-prefixed JSON messages.
For production, replace with asyncio or a threaded model.
"""
import socket
import threading
import json
import time
from server.src.config import SERVER_IP, SERVER_PORT
from server.src.game_logic import GameLogic
from shared.constants import GAME_WIDTH, GAME_HEIGHT

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, on_message):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.on_message = on_message
        self.running = True
        self.player_id = None  # ID của player này

    def run(self):
        try:
            while self.running:
                raw_len = self._recv_n(4)
                if not raw_len:
                    break
                length = int.from_bytes(raw_len, 'big')
                data = self._recv_n(length)
                if not data:
                    break
                msg = json.loads(data.decode('utf-8'))
                self.on_message(self, msg)
        finally:
            try:
                self.conn.close()
            except Exception:
                pass

    def _recv_n(self, n):
        buf = b''
        while len(buf) < n:
            chunk = self.conn.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def send(self, message: dict):
        try:
            data = json.dumps(message).encode('utf-8')
            length = len(data).to_bytes(4, 'big')
            self.conn.sendall(length + data)
            # Đảm bảo dữ liệu được gửi ngay
            self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception as e:
            print(f"ERROR sending message to {self.addr}: {e}", flush=True)
            raise

class GameServer:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.clients = []  # Tất cả clients (mọi phòng)
        # Quản lý nhiều phòng: mỗi phòng có logic, danh sách client, counter id
        # rooms[room_id] = { 'logic': GameLogic, 'clients': [ClientHandler], 'counter': int }
        self.rooms = {}
        self.last_broadcast = time.time()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        
        # Thread để broadcast state định kỳ
        broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        broadcast_thread.start()
        
        try:
            while True:
                conn, addr = self.sock.accept()
                print(f"Accepted connection from {addr}", flush=True)
                handler = ClientHandler(conn, addr, self.on_message)
                self.clients.append(handler)
                handler.start()
                print(f"Started handler thread for {addr}", flush=True)
        except KeyboardInterrupt:
            print("Server shutting down")
        finally:
            if self.sock:
                self.sock.close()
    
    def _broadcast_loop(self):
        """Broadcast game state định kỳ cho tất cả clients."""
        while True:
            try:
                time.sleep(0.1)  # 10 FPS
                current_time = time.time()
                # Cập nhật power-ups cho tất cả rooms
                for room in self.rooms.values():
                    room['logic'].update_powerups(current_time)
                    # Cập nhật speed boost cho players
                    for player in room['logic'].players.values():
                        if current_time >= getattr(player, 'speed_boost_end_time', 0):
                            player.speed_boost = 1.0
                self.broadcast_state()
            except Exception as e:
                print(f"Lỗi broadcast: {e}")
    
    def broadcast_state(self):
        """Gửi game state cho từng phòng tới đúng clients của phòng đó."""
        dead_clients = []
        for room_id, room in list(self.rooms.items()):
            # Chỉ broadcast nếu có ít nhất 1 player
            if not room['logic'].players:
                continue
            logic: GameLogic = room['logic']
            state = {
                "type": "state",
                "players": {},
                "obstacles": logic.get_obstacles_dict(),
                "powerups": logic.get_powerups_dict(),
                "goal": logic.get_goal_dict(),
                "level": logic.level_index
            }
            for pid, player in logic.players.items():
                state["players"][pid] = {
                    "name": getattr(player, "name", ""),
                    "x": player.x,
                    "y": player.y,
                    "hp": player.hp,
                    "score": getattr(player, "score", 0),
                    "speed_boost": getattr(player, "speed_boost", 1.0),
                    "is_dead": getattr(player, "is_dead", False)
                }
            # Thêm leaderboard vào state
            leaderboard = logic.get_leaderboard(3)
            state["leaderboard"] = [
                {"id": pid, "name": name, "score": score}
                for pid, name, score in leaderboard
            ]
            # Gửi cho các client trong phòng - CHỈ gửi cho clients đã có player_id
            for client in list(room['clients']):
                try:
                    if client.player_id and client.player_id in logic.players:
                        client.send(state)
                except Exception:
                    dead_clients.append((room_id, client))
        # Xóa dead clients và xử lý leave
        for room_id, client in dead_clients:
            if room_id in self.rooms and client in self.rooms[room_id]['clients']:
                self.rooms[room_id]['clients'].remove(client)
                if client.player_id:
                    self._handle_leave(client)

    def on_message(self, handler, message):
        print(f"Received from {handler.addr}: {message}", flush=True)
        msg_type = message.get('type')
        
        if msg_type == 'join':
            try:
                # Client muốn join game vào một phòng
                room_id = message.get('room') or 'default'
                print(f"Processing join for room: {room_id}", flush=True)
                if room_id not in self.rooms:
                    self.rooms[room_id] = {
                        'logic': GameLogic(),
                        'clients': [],
                        'counter': 1
                    }
                    print(f"Created new room: {room_id}", flush=True)
                room = self.rooms[room_id]
                if handler not in room['clients']:
                    room['clients'].append(handler)
                handler.room_id = room_id

                handler.player_id = f"player_{room['counter']}"
                room['counter'] += 1
                join_name = message.get('name') or ""
                print(f"Adding player {handler.player_id} with name '{join_name}' to room {room_id}", flush=True)
                room['logic'].add_player(handler.player_id, name=join_name)

                # Gửi confirm cho client (kèm room)
                response = {
                    "type": "joined",
                    "id": handler.player_id,
                    "room": room_id
                }
                print(f"Sending joined response: {response}", flush=True)
                handler.send(response)
                print(f"Joined response sent successfully to {handler.addr}", flush=True)
            except Exception as e:
                print(f"ERROR in join handler: {e}", flush=True)
                import traceback
                traceback.print_exc()

            # Broadcast join cho các clients khác trong cùng phòng
            self._broadcast_player_event("join", handler.player_id, room_id, exclude_handler=handler)
            
        elif msg_type == 'move':
            # Client di chuyển
            player_id = message.get('id')
            x = message.get('x')
            y = message.get('y')
            room_id = getattr(handler, 'room_id', 'default')
            room = self.rooms.get(room_id)
            if not room:
                return
            logic = room['logic']

            if player_id in logic.players:
                # Clamp vào biên an toàn
                new_x = max(0, min(GAME_WIDTH, x))
                new_y = max(0, min(GAME_HEIGHT, y))

                # Kiểm tra player có thể di chuyển không (đã hết cooldown respawn chưa)
                player = logic.players[player_id]
                current_time = time.time()
                if player.is_dead:
                    if logic.can_respawn(player_id, current_time):
                        logic.respawn_player(player_id)
                        self._send_to(handler, {"type": "respawned", "id": player_id})
                    else:
                        # Vẫn trong cooldown, không cho di chuyển
                        return
                
                # Nếu chạm obstacle => chết: reset và thông báo riêng cho client
                # Sử dụng collision detection với prediction để tránh đi xuyên qua
                old_x, old_y = player.x, player.y
                if logic.check_collision_with_obstacles_prediction(old_x, old_y, new_x, new_y):
                    logic.reset_player(player_id, current_time)
                    remaining_cooldown = player.respawn_time - current_time
                    self._send_to(handler, {
                        "type": "dead", 
                        "id": player_id,
                        "respawn_cooldown": remaining_cooldown
                    })
                else:
                    # Cập nhật vị trí
                    player = logic.players[player_id]
                    player.x = new_x
                    player.y = new_y
                    
                    # Kiểm tra nhặt power-up
                    collected_powerup = logic.check_powerup_collection(player.x, player.y)
                    if collected_powerup:
                        if collected_powerup.type == "speed":
                            current_time = time.time()
                            player.speed_boost = 2.0  # Tăng tốc gấp đôi
                            player.speed_boost_end_time = current_time + collected_powerup.duration
                            # Thông báo cho client
                            self._send_to(handler, {
                                "type": "powerup_collected",
                                "powerup_type": "speed",
                                "duration": collected_powerup.duration
                            })
                    
                    # Kiểm tra tới đích để qua màn
                    if logic.check_goal_reached(player.x, player.y):
                        logic.advance_level(player_id)
                        # Broadcast sự kiện level mới
                        self._broadcast_room(room_id, {
                            "type": "level",
                            "level": logic.level_index,
                            "obstacles": logic.get_obstacles_dict(),
                            "goal": logic.get_goal_dict(),
                            "player_id": player_id,
                            "score": logic.players[player_id].score
                        })
                
        elif msg_type == 'leave':
            # Client rời game
            self._handle_leave(handler)
    
    def _handle_leave(self, handler):
        """Xử lý khi client leave."""
        if handler.player_id:
            room_id = getattr(handler, 'room_id', None)
            if room_id and room_id in self.rooms:
                logic = self.rooms[room_id]['logic']
                logic.remove_player(handler.player_id)
                if handler in self.rooms[room_id]['clients']:
                    self.rooms[room_id]['clients'].remove(handler)
                self._broadcast_player_event("leave", handler.player_id, room_id)
                print(f"Player {handler.player_id} left the game (room {room_id})")
    
    def _broadcast_player_event(self, event_type, player_id, room_id, exclude_handler=None):
        """Broadcast join/leave event cho các clients trong cùng phòng."""
        room = self.rooms.get(room_id)
        if not room:
            return
        for client in list(room['clients']):
            try:
                if client != exclude_handler:
                    client.send({
                        "type": event_type,
                        "id": player_id
                    })
            except Exception:
                pass

    def _send_to(self, handler, message: dict):
        try:
            handler.send(message)
        except Exception:
            pass

    def _broadcast_room(self, room_id: str, message: dict):
        room = self.rooms.get(room_id)
        if not room:
            return
        dead = []
        for c in list(room['clients']):
            try:
                c.send(message)
            except Exception:
                dead.append(c)
        for c in dead:
            if c in room['clients']:
                room['clients'].remove(c)

if __name__ == '__main__':
    gs = GameServer()
    gs.start()
