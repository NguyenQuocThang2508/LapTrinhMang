# 📋 PHÂN CÔNG CHI TIẾT - MỖI NGƯỜI 4+ COMMIT

## 🎯 MỤC TIÊU
Mỗi người trong nhóm 4 người sẽ có **ít nhất 4 commit** riêng biệt, mỗi commit là một task hoàn chỉnh.

---

## 👤 NGƯỜI 1: CLIENT & UI (Graphics & Visual Effects)

### **Commit 1: [FEAT] Thêm hiệu ứng particle khi player di chuyển**
**File:** `client/src/graphics.py`
**Mô tả:**
- Thêm class `ParticleSystem` để tạo hiệu ứng bụi/trail khi di chuyển
- Vẽ các hạt nhỏ phía sau player khi di chuyển
- Màu sắc thay đổi theo tốc độ

**Code gợi ý:**
```python
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color):
        # Thêm particle mới
        pass
    
    def update(self, dt):
        # Cập nhật và xóa particle cũ
        pass
    
    def draw(self, canvas):
        # Vẽ particles
        pass
```

**Branch:** `feature/particle-effects`

---

### **Commit 2: [FEAT] Thêm mini-map hiển thị vị trí players**
**File:** `client/src/graphics.py`
**Mô tả:**
- Vẽ mini-map góc trên bên phải màn hình
- Hiển thị vị trí tất cả players (màu khác nhau)
- Hiển thị obstacles và goal trên mini-map

**Code gợi ý:**
```python
def draw_minimap(self, players, obstacles, goal):
    # Vẽ mini-map ở góc trên phải
    # Scale toàn bộ map xuống nhỏ
    pass
```

**Branch:** `feature/minimap`

---

### **Commit 3: [FEAT] Thêm animation cho player (nhấp nháy khi spawn)**
**File:** `client/src/graphics.py`, `client/src/game.py`
**Mô tả:**
- Player nhấp nháy (fade in/out) khi mới spawn
- Animation kéo dài 2 giây
- Thêm thuộc tính `spawn_time` vào Player class

**Code gợi ý:**
```python
def draw_player(self, x, y, color, spawn_time=None):
    if spawn_time:
        elapsed = time.time() - spawn_time
        if elapsed < 2.0:
            alpha = int(255 * (elapsed / 2.0))
            # Vẽ với alpha thay đổi
    # Vẽ player bình thường
```

**Branch:** `feature/player-animation`

---

### **Commit 4: [FEAT] Thêm health bar cho mỗi player**
**File:** `client/src/graphics.py`
**Mô tả:**
- Vẽ thanh HP phía trên đầu player
- Màu xanh khi HP cao, đỏ khi HP thấp
- Hiển thị số HP dạng text

**Code gợi ý:**
```python
def draw_health_bar(self, x, y, hp, max_hp=100):
    # Vẽ background bar (màu đỏ)
    # Vẽ foreground bar (màu xanh) theo tỷ lệ hp/max_hp
    # Vẽ text hiển thị số HP
    pass
```

**Branch:** `feature/health-bar`

---

### **Commit 5 (Bonus): [STYLE] Cải thiện màu sắc và contrast**
**File:** `client/src/graphics.py`
**Mô tả:**
- Tối ưu màu sắc cho dễ nhìn
- Thêm shadow cho text
- Cải thiện contrast giữa player và background

**Branch:** `feature/color-improvement`

---

## 👤 NGƯỜI 2: SERVER & GAME LOGIC

### **Commit 1: [FEAT] Thêm hệ thống điểm số (score) cho players**
**File:** `server/src/game_logic.py`
**Mô tả:**
- Thêm thuộc tính `score` vào `ServerPlayer`
- Tăng điểm khi đạt goal (+10 điểm)
- Tăng điểm khi sống sót mỗi 10 giây (+1 điểm)
- Gửi score trong state message

**Code gợi ý:**
```python
@dataclass
class ServerPlayer:
    # ... existing fields ...
    score: int = 0
    last_score_time: float = 0.0

def update_scores(self, dt):
    # Tăng điểm theo thời gian
    pass
```

**Branch:** `feature/score-system`

---

### **Commit 2: [FEAT] Thêm hệ thống power-up (tăng tốc độ tạm thời)**
**File:** `server/src/game_logic.py`
**Mô tả:**
- Tạo power-up spawn ngẫu nhiên trên map
- Player chạm vào power-up → tăng tốc độ 1.5x trong 5 giây
- Power-up biến mất sau khi bị nhặt

**Code gợi ý:**
```python
@dataclass
class PowerUp:
    id: str
    x: float
    y: float
    type: str = "speed_boost"
    duration: float = 5.0

# Thêm vào GameLogic:
self.powerups = []
self.player_effects = {}  # {player_id: {"speed_boost": end_time}}
```

**Branch:** `feature/powerups`

---

### **Commit 3: [FEAT] Thêm hệ thống respawn với cooldown**
**File:** `server/src/game_logic.py`
**Mô tả:**
- Khi player chết, phải đợi 3 giây mới respawn
- Hiển thị countdown trên client
- Không thể di chuyển khi đang respawn

**Code gợi ý:**
```python
@dataclass
class ServerPlayer:
    # ... existing fields ...
    is_dead: bool = False
    respawn_time: float = 0.0

def check_respawn(self, player_id, current_time):
    # Kiểm tra và respawn nếu đủ thời gian
    pass
```

**Branch:** `feature/respawn-cooldown`

---

### **Commit 4: [FEAT] Thêm hệ thống leaderboard (top 3 players)**
**File:** `server/src/game_logic.py`, `server/src/server.py`
**Mô tả:**
- Tính toán top 3 players dựa trên score
- Gửi leaderboard trong state message mỗi 2 giây
- Hiển thị trên client

**Code gợi ý:**
```python
def get_leaderboard(self, top_n=3):
    sorted_players = sorted(
        self.players.values(),
        key=lambda p: p.score,
        reverse=True
    )
    return [
        {"id": p.id, "name": p.name, "score": p.score}
        for p in sorted_players[:top_n]
    ]
```

**Branch:** `feature/leaderboard`

---

### **Commit 5 (Bonus): [FIX] Cải thiện collision detection**
**File:** `server/src/game_logic.py`
**Mô tả:**
- Tối ưu thuật toán collision
- Thêm collision giữa players (không thể đi xuyên qua nhau)
- Fix bug collision với obstacles

**Branch:** `fix/collision-improvement`

---

## 👤 NGƯỜI 3: NETWORK & PROTOCOL

### **Commit 1: [FEAT] Thêm message compression để giảm bandwidth**
**File:** `shared/protocol.py`
**Mô tả:**
- Sử dụng gzip để nén message trước khi gửi
- Giảm kích thước message xuống 50-70%
- Tự động detect và decompress khi nhận

**Code gợi ý:**
```python
import gzip

def encode(message: Dict[str, Any], compress=True) -> bytes:
    data = json.dumps(message).encode('utf-8')
    if compress:
        data = gzip.compress(data)
    return len(data).to_bytes(4, 'big') + data

def decode(stream_bytes: bytes) -> Dict[str, Any]:
    # Thử decompress trước
    try:
        stream_bytes = gzip.decompress(stream_bytes)
    except:
        pass
    return json.loads(stream_bytes.decode('utf-8'))
```

**Branch:** `feature/message-compression`

---

### **Commit 2: [FEAT] Thêm heartbeat/ping system để detect disconnect**
**File:** `shared/protocol.py`, `server/src/server.py`, `client/src/client.py`
**Mô tả:**
- Client gửi ping mỗi 5 giây
- Server trả về pong
- Nếu không nhận ping trong 15 giây → disconnect player

**Code gợi ý:**
```python
# Trong protocol.py
PING_MESSAGE = {"type": "ping", "timestamp": time.time()}
PONG_MESSAGE = {"type": "pong", "timestamp": time.time()}

# Trong server: track last_ping_time cho mỗi client
# Trong client: gửi ping định kỳ
```

**Branch:** `feature/heartbeat-system`

---

### **Commit 3: [FEAT] Thêm message queuing để tránh mất packet**
**File:** `client/src/client.py`
**Mô tả:**
- Queue các message chưa gửi được
- Retry gửi lại nếu fail
- Đảm bảo message quan trọng (join, leave) luôn được gửi

**Code gợi ý:**
```python
class ClientNetwork:
    def __init__(self):
        self.message_queue = []
        self.important_messages = []  # join, leave
    
    def send(self, message, important=False):
        try:
            # Thử gửi
            pass
        except:
            # Thêm vào queue
            if important:
                self.important_messages.append(message)
            else:
                self.message_queue.append(message)
```

**Branch:** `feature/message-queue`

---

### **Commit 4: [FEAT] Thêm encryption cho message (optional)**
**File:** `shared/protocol.py`
**Mô tả:**
- Mã hóa message bằng XOR đơn giản (hoặc base64)
- Bảo vệ khỏi packet sniffing cơ bản
- Có thể bật/tắt encryption

**Code gợi ý:**
```python
import base64

def encode(message: Dict[str, Any], encrypt=False) -> bytes:
    data = json.dumps(message).encode('utf-8')
    if encrypt:
        # Simple XOR encryption với key
        key = b"game_key_2024"
        data = bytes(a ^ b for a, b in zip(data, key * len(data)))
    return len(data).to_bytes(4, 'big') + data
```

**Branch:** `feature/message-encryption`

---

### **Commit 5 (Bonus): [FEAT] Thêm rate limiting để chống spam**
**File:** `server/src/server.py`
**Mô tả:**
- Giới hạn số message mỗi giây từ mỗi client
- Block client nếu spam quá nhiều
- Log các client bị block

**Branch:** `feature/rate-limiting`

---

## 👤 NGƯỜI 4: TESTING & DOCUMENTATION

### **Commit 1: [TEST] Thêm unit test cho game logic**
**File:** `tests/test_game_logic.py`
**Mô tả:**
- Test thêm player
- Test collision detection
- Test goal reached
- Test level advancement

**Code gợi ý:**
```python
def test_add_player():
    logic = GameLogic()
    logic.add_player("p1", "Player1")
    assert "p1" in logic.players
    assert logic.players["p1"].name == "Player1"

def test_collision_detection():
    logic = GameLogic()
    # Tạo obstacle
    # Test collision
    assert logic.check_collision_with_obstacles(100, 100) == True
```

**Branch:** `feature/game-logic-tests`

---

### **Commit 2: [TEST] Thêm integration test cho client-server**
**File:** `tests/test_integration.py` (tạo mới)
**Mô tả:**
- Test kết nối client-server
- Test gửi/nhận message
- Test multiple clients
- Test disconnect/reconnect

**Code gợi ý:**
```python
def test_client_server_connection():
    # Start server thread
    # Connect client
    # Send message
    # Verify response
    pass
```

**Branch:** `feature/integration-tests`

---

### **Commit 3: [DOC] Cập nhật README với hướng dẫn đầy đủ**
**File:** `README.md`
**Mô tả:**
- Thêm phần Architecture
- Thêm phần API Documentation
- Thêm phần Troubleshooting
- Thêm screenshots/GIF demo

**Branch:** `feature/readme-update`

---

### **Commit 4: [DOC] Tạo file API documentation**
**File:** `docs/API.md` (tạo mới thư mục docs/)
**Mô tả:**
- Document tất cả message types
- Document protocol format
- Document server endpoints
- Ví dụ code cho mỗi message type

**Code gợi ý:**
```markdown
# API Documentation

## Message Types

### Join Message
```json
{
  "type": "join",
  "name": "Player1",
  "room": "default"
}
```
...
```

**Branch:** `feature/api-documentation`

---

### **Commit 5 (Bonus): [FIX] Fix các bug nhỏ và cải thiện error handling**
**File:** Nhiều file
**Mô tả:**
- Thêm try-catch cho các hàm quan trọng
- Thêm logging
- Fix các lỗi nhỏ phát hiện được
- Cải thiện error messages

**Branch:** `fix/error-handling`

---

## 📊 TỔNG KẾT

| Người | Số Commit | Branch Chính | Tính năng chính |
|-------|-----------|--------------|-----------------|
| Người 1 | 4-5 | `feature/client-ui` | Graphics, Effects, UI |
| Người 2 | 4-5 | `feature/server-logic` | Game Logic, Score, Powerups |
| Người 3 | 4-5 | `feature/network` | Protocol, Network |
| Người 4 | 4-5 | `feature/testing` | Tests, Documentation |

**Tổng: 16-20 commits từ 4 người**

---

## 🚀 QUY TRÌNH LÀM VIỆC

### **Bước 1: Mỗi người tạo branch riêng**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/tên-tính-năng-của-bạn
```

### **Bước 2: Làm từng commit một**
- Làm xong task 1 → commit
- Làm xong task 2 → commit
- ...

### **Bước 3: Push và tạo PR**
```bash
git push origin feature/tên-branch
# Tạo Pull Request trên GitHub/GitLab
```

### **Bước 4: Review và merge**
- Người khác review code
- Sửa theo comment
- Merge vào develop

---

## ⚠️ LƯU Ý

1. **Mỗi commit phải hoàn chỉnh** - code chạy được, không có lỗi
2. **Test trước khi commit** - chạy game để đảm bảo không break
3. **Commit message rõ ràng** - theo format `[FEAT] Mô tả`
4. **Không conflict** - pull thường xuyên từ develop
5. **Giao tiếp** - thông báo khi sửa file chung

---

## 📞 HỖ TRỢ

Nếu gặp khó khăn với task nào:
1. Đọc code hiện tại để hiểu cấu trúc
2. Hỏi trong nhóm
3. Google/Stack Overflow
4. Xem tài liệu pygame, Python

**Chúc nhóm hoàn thành tốt! 🎮**

