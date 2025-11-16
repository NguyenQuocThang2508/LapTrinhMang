# 🎨 HƯỚNG DẪN CHI TIẾT CHO NGƯỜI 1 - 5 COMMITS

## 📋 TỔNG QUAN

Bạn sẽ làm **5 commits** để cải thiện Client & UI:
1. Particle effects khi di chuyển
2. Mini-map
3. Player spawn animation
4. Health bar
5. Cải thiện màu sắc

---

## 🚀 BƯỚC 0: SETUP BAN ĐẦU

```bash
# 1. Chuyển về develop và pull code mới nhất
git checkout develop
git pull origin develop

# 2. Tạo branch mới cho bạn
git checkout -b feature/client-ui-improvements

# 3. Kiểm tra bạn đang ở đúng branch
git branch
# Phải thấy dấu * ở feature/client-ui-improvements
```

---

## ✅ COMMIT 1: [FEAT] Thêm hiệu ứng particle khi player di chuyển

### **Mục tiêu:**
Tạo hiệu ứng bụi/trail phía sau player khi di chuyển

### **File cần sửa:**
- `client/src/graphics.py`

### **Các bước:**

**Bước 1:** Mở file `client/src/graphics.py`

**Bước 2:** Thêm class ParticleSystem vào cuối file (trước dòng cuối):

```python
class Particle:
    """Một hạt particle đơn lẻ."""
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=0.5):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 255

    def update(self, dt):
        """Cập nhật vị trí và alpha của particle."""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        # Alpha giảm dần theo thời gian
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))

    def is_alive(self):
        """Kiểm tra particle còn sống không."""
        return self.lifetime > 0


class ParticleSystem:
    """Hệ thống quản lý particles."""
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color=(200, 200, 200), velocity_x=0, velocity_y=0):
        """Thêm một particle mới."""
        import random
        # Thêm một chút randomness
        vx = velocity_x + random.uniform(-20, 20)
        vy = velocity_y + random.uniform(-20, 20)
        lifetime = random.uniform(0.3, 0.6)
        self.particles.append(Particle(x, y, color, vx, vy, lifetime))

    def update(self, dt):
        """Cập nhật tất cả particles."""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, canvas, sx, sy):
        """Vẽ tất cả particles lên canvas."""
        if not pygame:
            return
        for particle in self.particles:
            # Scale coordinates
            vx = int(particle.x * sx)
            vy = int(particle.y * sy)
            # Tạo màu với alpha
            color_with_alpha = (*particle.color, particle.alpha)
            # Vẽ particle nhỏ (2-3 pixels)
            pygame.draw.circle(canvas, particle.color[:3], (vx, vy), max(1, int(2 * sy)))
```

**Bước 3:** Thêm ParticleSystem vào GameRenderer class:

Trong `__init__` của GameRenderer, thêm:
```python
        # Particle system
        self.particle_system = ParticleSystem()
```

**Bước 4:** Thêm method để vẽ particles trong GameRenderer:

```python
    def draw_particles(self):
        """Vẽ particles lên canvas."""
        if pygame:
            self.particle_system.draw(self.canvas, self._sx, self._sy)
```

**Bước 5:** Cập nhật method `present()` để vẽ particles trước khi scale:

```python
    def present(self):
        if pygame:
            # Vẽ particles trước khi scale
            self.draw_particles()
            # Scale low-res canvas to screen with nearest-neighbor
            scaled = pygame.transform.scale(self.canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled, (0, 0))
            # Optional scanline overlay for CRT feel
            self._draw_scanlines(self.screen)
            pygame.display.flip()
```

**Bước 6:** Cập nhật `client/main.py` để sử dụng particles:

Tìm phần game loop (khoảng dòng 446), trong vòng lặp `while running:`, thêm:

```python
            # Update particles
            renderer.particle_system.update(dt)
```

Tìm phần di chuyển player (khoảng dòng 615), sau khi player di chuyển, thêm:

```python
                    if dx != 0 or dy != 0:
                        # Thêm particles khi di chuyển
                        if audio_enabled and sounds.get('footstep') and footstep_cooldown >= footstep_interval:
                            try: sounds['footstep'].play()
                            except Exception: pass
                            footstep_cooldown = 0.0
                        # Thêm particles
                        player = game_state.players[my_player_id]
                        # Tính velocity từ hướng di chuyển
                        vel_x = dx / dt if dt > 0 else 0
                        vel_y = dy / dt if dt > 0 else 0
                        # Thêm 3-5 particles
                        for _ in range(3):
                            renderer.particle_system.add_particle(
                                player.x, player.y,
                                color=(150, 150, 150),
                                velocity_x=-vel_x * 0.3,
                                velocity_y=-vel_y * 0.3
                            )
```

**Bước 7:** Test và commit:

```bash
# Test game
python -m server.main  # Terminal 1
python -m client.main  # Terminal 2

# Nếu chạy được, commit
git add client/src/graphics.py client/main.py
git commit -m "[FEAT] Thêm hiệu ứng particle khi player di chuyển"
git push origin feature/client-ui-improvements
```

---

## ✅ COMMIT 2: [FEAT] Thêm mini-map hiển thị vị trí players

### **Mục tiêu:**
Vẽ mini-map góc trên bên phải màn hình

### **File cần sửa:**
- `client/src/graphics.py`

### **Các bước:**

**Bước 1:** Thêm method `draw_minimap` vào GameRenderer:

```python
    def draw_minimap(self, players, obstacles, goal, my_player_id=None):
        """Vẽ mini-map ở góc trên bên phải."""
        if not pygame:
            return
        
        # Kích thước mini-map
        map_width = 120
        map_height = 90
        map_x = SCREEN_WIDTH - map_width - 10
        map_y = 10
        
        # Tạo surface cho mini-map
        minimap_surface = pygame.Surface((map_width, map_height))
        minimap_surface.fill((20, 20, 30))  # Nền tối
        
        # Scale factor để fit toàn bộ map vào mini-map
        scale_x = map_width / SCREEN_WIDTH
        scale_y = map_height / SCREEN_HEIGHT
        
        # Vẽ obstacles (màu nâu nhạt)
        for obs_id, obstacle in obstacles.items():
            obs_x = int(obstacle.x * scale_x)
            obs_y = int(obstacle.y * scale_y)
            obs_w = max(1, int(obstacle.width * scale_x))
            obs_h = max(1, int(obstacle.height * scale_y))
            pygame.draw.rect(minimap_surface, (100, 50, 30), (obs_x, obs_y, obs_w, obs_h))
        
        # Vẽ goal (màu xanh)
        if goal:
            goal_x = int(goal.get('x', 0) * scale_x)
            goal_y = int(goal.get('y', 0) * scale_y)
            goal_w = max(2, int(goal.get('width', 40) * scale_x))
            goal_h = max(2, int(goal.get('height', 40) * scale_y))
            pygame.draw.rect(minimap_surface, (0, 220, 100), (goal_x, goal_y, goal_w, goal_h))
        
        # Vẽ players
        for pid, player in players.items():
            px = int(player.x * scale_x)
            py = int(player.y * scale_y)
            # Màu khác nhau cho player của mình
            if my_player_id and pid == my_player_id:
                color = (0, 255, 0)  # Xanh lá cho mình
            else:
                color = (255, 0, 0)  # Đỏ cho người khác
            pygame.draw.circle(minimap_surface, color, (px, py), 2)
        
        # Vẽ viền cho mini-map
        pygame.draw.rect(minimap_surface, (100, 100, 100), (0, 0, map_width, map_height), 2)
        
        # Blit mini-map lên screen (sau khi đã scale canvas)
        # Lưu ý: Cần vẽ sau khi present() đã scale canvas
```

**Bước 2:** Cập nhật method `present()` để nhận thêm parameters:

```python
    def present(self, players=None, obstacles=None, goal=None, my_player_id=None):
        if pygame:
            # Vẽ particles trước khi scale
            self.draw_particles()
            # Scale low-res canvas to screen with nearest-neighbor
            scaled = pygame.transform.scale(self.canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled, (0, 0))
            # Optional scanline overlay for CRT feel
            self._draw_scanlines(self.screen)
            
            # Vẽ mini-map (sau khi đã scale)
            if players and obstacles is not None:
                self.draw_minimap(players, obstacles, goal, my_player_id)
            
            pygame.display.flip()
```

**Bước 3:** Cập nhật `client/main.py`:

Tìm dòng `renderer.present()` (khoảng dòng 706), thay bằng:

```python
            renderer.present(
                players=game_state.players,
                obstacles=game_state.obstacles,
                goal=getattr(game_state, 'goal', None),
                my_player_id=my_player_id
            )
```

**Bước 4:** Test và commit:

```bash
# Test
python -m server.main  # Terminal 1
python -m client.main  # Terminal 2

# Commit
git add client/src/graphics.py client/main.py
git commit -m "[FEAT] Thêm mini-map hiển thị vị trí players, obstacles và goal"
git push origin feature/client-ui-improvements
```

---

## ✅ COMMIT 3: [FEAT] Thêm animation cho player (nhấp nháy khi spawn)

### **Mục tiêu:**
Player nhấp nháy khi mới spawn

### **File cần sửa:**
- `client/src/game.py`
- `client/src/graphics.py`

### **Các bước:**

**Bước 1:** Thêm `spawn_time` vào Player class trong `client/src/game.py`:

```python
@dataclass
class Player:
    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    hp: int = 100
    spawn_time: float = None  # Thời điểm spawn (None nếu không mới spawn)
```

**Bước 2:** Cập nhật `add_player` trong GameState:

```python
    def add_player(self, player_id: str):
        if player_id not in self.players:
            import random
            import time
            self.players[player_id] = Player(
                id=player_id,
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                spawn_time=time.time()  # Ghi lại thời điểm spawn
            )
```

**Bước 3:** Cập nhật `draw_player` trong `graphics.py`:

```python
    def draw_player(self, x, y, color=(255, 255, 255), spawn_time=None):
        if pygame:
            # Scale world coords to virtual canvas
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            # Radius scales with Y factor to keep aspect
            vr = max(1, int(16 * self._sy))
            
            # Animation nhấp nháy khi spawn
            if spawn_time is not None:
                import time
                elapsed = time.time() - spawn_time
                if elapsed < 2.0:  # Animation trong 2 giây
                    # Tính alpha: 0 -> 255 trong 2 giây, nhấp nháy
                    blink_speed = 10  # Tốc độ nhấp nháy
                    alpha = int(128 + 127 * (1 + (elapsed * blink_speed) % 2 - 1))
                    # Tạo surface với alpha
                    temp_surface = pygame.Surface((vr * 2, vr * 2), pygame.SRCALPHA)
                    color_with_alpha = (*color, alpha)
                    pygame.draw.circle(temp_surface, color_with_alpha, (vr, vr), vr)
                    self.canvas.blit(temp_surface, (vx - vr, vy - vr))
                    return
            
            # Vẽ player bình thường
            pygame.draw.circle(self.canvas, color, (vx, vy), vr)
```

**Bước 4:** Cập nhật `client/main.py` để truyền spawn_time:

Tìm phần vẽ players (khoảng dòng 689):

```python
            # Vẽ tất cả players
            for pid, player in game_state.players.items():
                if local_multiplayer and pid in player_ids:
                    idx = player_ids.index(pid)
                    color = (0, 255, 0) if idx == 0 else (255, 255, 0)
                else:
                    color = (0, 255, 0) if (my_player_id and pid == my_player_id) else (255, 0, 0)
                renderer.draw_player(
                    player.x or 400, 
                    player.y or 300, 
                    color,
                    spawn_time=getattr(player, 'spawn_time', None)
                )
                renderer.draw_name(player.x or 400, (player.y or 300), getattr(player, 'name', ''))
```

**Bước 5:** Cập nhật server message handler để set spawn_time:

Trong `handle_server_message`, khi nhận message 'joined' hoặc 'state', cập nhật spawn_time:

```python
    if msg_type == 'state':
        # Cập nhật state từ server
        players_data = msg.get('players', {})
        for pid, data in players_data.items():
            if pid not in game_state.players:
                game_state.add_player(pid)
                # Set spawn_time cho player mới
                game_state.players[pid].spawn_time = time.time()
```

**Bước 6:** Test và commit:

```bash
# Test
python -m server.main
python -m client.main

# Commit
git add client/src/game.py client/src/graphics.py client/main.py
git commit -m "[FEAT] Thêm animation nhấp nháy cho player khi spawn"
git push origin feature/client-ui-improvements
```

---

## ✅ COMMIT 4: [FEAT] Thêm health bar cho mỗi player

### **Mục tiêu:**
Vẽ thanh HP phía trên đầu player

### **File cần sửa:**
- `client/src/graphics.py`

### **Các bước:**

**Bước 1:** Thêm method `draw_health_bar` vào GameRenderer:

```python
    def draw_health_bar(self, x, y, hp, max_hp=100):
        """Vẽ health bar phía trên player."""
        if not pygame:
            return
        
        # Scale coordinates
        vx = int(x * self._sx)
        vy = int(y * self._sy)
        
        # Kích thước health bar
        bar_width = 30
        bar_height = 4
        bar_x = vx - bar_width // 2
        bar_y = vy - int(25 * self._sy)  # Phía trên player
        
        # Tính tỷ lệ HP
        hp_ratio = max(0, min(1, hp / max_hp))
        
        # Màu sắc: xanh khi HP cao, đỏ khi HP thấp
        if hp_ratio > 0.6:
            bar_color = (0, 255, 0)  # Xanh
        elif hp_ratio > 0.3:
            bar_color = (255, 255, 0)  # Vàng
        else:
            bar_color = (255, 0, 0)  # Đỏ
        
        # Vẽ background (màu đỏ đậm)
        pygame.draw.rect(self.canvas, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Vẽ foreground (màu theo HP)
        hp_width = int(bar_width * hp_ratio)
        if hp_width > 0:
            pygame.draw.rect(self.canvas, bar_color, (bar_x, bar_y, hp_width, bar_height))
        
        # Vẽ viền
        pygame.draw.rect(self.canvas, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Vẽ text HP (nếu có font)
        if self._font and hp < max_hp:
            hp_text = str(int(hp))
            text_surf = self._font.render(hp_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(vx, bar_y - 8))
            self.canvas.blit(text_surf, text_rect)
```

**Bước 2:** Cập nhật `draw_player` để vẽ health bar:

```python
    def draw_player(self, x, y, color=(255, 255, 255), spawn_time=None, hp=100, max_hp=100):
        if pygame:
            # ... (code cũ vẽ player)
            # Vẽ health bar sau khi vẽ player
            if hp < max_hp:  # Chỉ vẽ khi HP không đầy
                self.draw_health_bar(x, y, hp, max_hp)
```

**Bước 3:** Cập nhật `client/main.py` để truyền HP:

Tìm phần vẽ players, cập nhật:

```python
                renderer.draw_player(
                    player.x or 400, 
                    player.y or 300, 
                    color,
                    spawn_time=getattr(player, 'spawn_time', None),
                    hp=getattr(player, 'hp', 100),
                    max_hp=100
                )
```

**Bước 4:** Test và commit:

```bash
# Test
python -m server.main
python -m client.main

# Commit
git add client/src/graphics.py client/main.py
git commit -m "[FEAT] Thêm health bar hiển thị HP cho mỗi player"
git push origin feature/client-ui-improvements
```

---

## ✅ COMMIT 5: [STYLE] Cải thiện màu sắc và contrast

### **Mục tiêu:**
Tối ưu màu sắc cho dễ nhìn

### **File cần sửa:**
- `client/src/graphics.py`
- `client/main.py`

### **Các bước:**

**Bước 1:** Cải thiện màu background và contrast:

Trong `clear()` method, đổi màu nền:

```python
    def clear(self, color=(20, 20, 40)):  # Xanh đậm thay vì đen
        if pygame:
            self.canvas.fill(color)
```

**Bước 2:** Cải thiện màu player:

Trong `client/main.py`, tìm phần set màu player, cải thiện:

```python
                if local_multiplayer and pid in player_ids:
                    idx = player_ids.index(pid)
                    color = (0, 255, 100) if idx == 0 else (255, 200, 0)  # Xanh lá sáng, vàng
                else:
                    color = (0, 255, 100) if (my_player_id and pid == my_player_id) else (255, 80, 80)  # Xanh lá, đỏ nhạt
```

**Bước 3:** Thêm shadow cho text:

Thêm method helper:

```python
    def draw_text_with_shadow(self, x, y, text, color=(255, 255, 255), shadow_color=(0, 0, 0)):
        """Vẽ text với shadow để dễ đọc."""
        if not pygame or not self._font:
            return
        # Vẽ shadow (lệch 1 pixel)
        shadow_surf = self._font.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(x + 1, y + 1))
        self.canvas.blit(shadow_surf, shadow_rect)
        # Vẽ text chính
        text_surf = self._font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        self.canvas.blit(text_surf, text_rect)
```

**Bước 4:** Cập nhật `draw_name` để dùng shadow:

```python
    def draw_name(self, x, y, name: str, color=(255, 255, 255)):
        if pygame and self._font and name:
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            self.draw_text_with_shadow(vx, vy - int(26 * self._sy), name, color)
```

**Bước 5:** Cải thiện màu obstacles:

```python
    def draw_obstacle(self, x, y, width, height, color=(120, 60, 40)):  # Sáng hơn
        """Vẽ chướng ngại vật dạng hình chữ nhật."""
        if pygame:
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            vw = max(1, int(width * self._sx))
            vh = max(1, int(height * self._sy))
            pygame.draw.rect(self.canvas, color, (vx, vy, vw, vh))
            # Vẽ viền sáng hơn
            pygame.draw.rect(self.canvas, (180, 90, 60), (vx, vy, vw, vh), 2)
```

**Bước 6:** Test và commit:

```bash
# Test
python -m server.main
python -m client.main

# Commit
git add client/src/graphics.py client/main.py
git commit -m "[STYLE] Cải thiện màu sắc, contrast và thêm shadow cho text"
git push origin feature/client-ui-improvements
```

---

## 🎉 HOÀN THÀNH!

Sau khi hoàn thành 5 commits, tạo Pull Request:

```bash
# Kiểm tra lại tất cả commits
git log --oneline -5

# Push tất cả lên remote
git push origin feature/client-ui-improvements
```

Sau đó lên GitHub/GitLab tạo Pull Request từ `feature/client-ui-improvements` vào `develop`.

---

## 📝 LƯU Ý

1. **Test mỗi commit** trước khi commit tiếp
2. **Commit message rõ ràng** theo format `[FEAT]` hoặc `[STYLE]`
3. **Pull thường xuyên** từ develop để tránh conflict
4. **Nếu có lỗi**, sửa và commit lại với message `[FIX]`

**Chúc bạn hoàn thành tốt! 🚀**

