"""Server-side game logic placeholder.
This module should validate actions, update authoritative state, and resolve collisions.
"""
from dataclasses import dataclass
import random
from typing import List, Dict, Tuple, Optional
from shared.constants import GAME_WIDTH, GAME_HEIGHT

@dataclass
class ServerPlayer:
    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    hp: int = 100
    score: int = 0  # Điểm số của người chơi
    speed_boost: float = 1.0  # Hệ số tăng tốc từ power-up
    speed_boost_end_time: float = 0.0  # Thời điểm hết hiệu lực speed boost
    is_dead: bool = False  # Trạng thái chết
    respawn_time: float = 0.0  # Thời điểm có thể respawn
    respawn_cooldown: float = 3.0  # Cooldown 3 giây

@dataclass
class Obstacle:
    id: str
    x: float = 0.0
    y: float = 0.0
    width: float = 40.0
    height: float = 40.0

@dataclass
class PowerUp:
    id: str
    x: float = 0.0
    y: float = 0.0
    type: str = "speed"  # "speed" cho tăng tốc
    duration: float = 5.0  # Thời gian hiệu lực (giây)
    spawn_time: float = 0.0  # Thời điểm spawn

class GameLogic:
    def __init__(self):
        self.players = {}
        self.obstacles: List[Obstacle] = []
        self.powerups: List[PowerUp] = []  # Danh sách power-ups
        # Level system
        self.level_index: int = 1
        self.start_pos: Tuple[float, float] = (50.0, GAME_HEIGHT - 50.0)
        self.goal_rect: Tuple[float, float, float, float] = (GAME_WIDTH - 90.0, 30.0, 60.0, 60.0)
        self.powerup_spawn_timer: float = 0.0  # Timer để spawn power-up
        self.powerup_spawn_interval: float = 10.0  # Spawn mỗi 10 giây
        self.powerup_counter: int = 0  # Đếm số power-up đã spawn
        self._init_level(self.level_index)

    def add_player(self, player_id, name: str = ""):
        if player_id not in self.players:
            # Vị trí ban đầu: player đầu tiên ở start_pos, các player sau offset một chút
            num_players = len(self.players)
            offset_x = num_players * 30  # Mỗi player cách nhau 30 pixels
            offset_y = num_players * 30
            spawn_x = self.start_pos[0] + offset_x
            spawn_y = self.start_pos[1] - offset_y  # Offset lên trên một chút
            
            # Đảm bảo không ra ngoài biên
            spawn_x = max(50, min(GAME_WIDTH - 50, spawn_x))
            spawn_y = max(50, min(GAME_HEIGHT - 50, spawn_y))
            
            self.players[player_id] = ServerPlayer(
                id=player_id,
                name=name,
                x=spawn_x,
                y=spawn_y
            )

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
    
    def _init_level(self, level: int):
        """Khởi tạo level: obstacles + start/goal."""
        self.obstacles = []
        self.powerups = []  # Reset power-ups khi chuyển level
        # Cấu hình start/goal theo level
        self.start_pos = (50.0, GAME_HEIGHT - 50.0)
        self.goal_rect = (GAME_WIDTH - 90.0, 30.0, 60.0, 60.0)

        # Sinh chướng ngại vật dựa vào level: thêm hàng rào dạng hành lang ziczac
        rng = random.Random(level * 1337)
        num = 6 + level  # tăng dần độ khó
        for i in range(num):
            w = rng.randint(50, 110)
            h = rng.randint(40, 100)
            x = rng.randint(120, int(GAME_WIDTH - 160))
            y = rng.randint(90, int(GAME_HEIGHT - 160))
            self.obstacles.append(Obstacle(
                id=f"obstacle_{i}", x=float(x), y=float(y), width=float(w), height=float(h)
            ))
    
    def spawn_powerup(self, current_time: float):
        """Spawn một power-up ngẫu nhiên trên map."""
        rng = random.Random()
        # Tìm vị trí không trùng với obstacles
        max_attempts = 20
        for _ in range(max_attempts):
            x = rng.uniform(50, GAME_WIDTH - 50)
            y = rng.uniform(50, GAME_HEIGHT - 50)
            # Kiểm tra không trùng với obstacles
            if not self.check_collision_with_obstacles(x, y, player_radius=20):
                powerup_id = f"powerup_{self.powerup_counter}"
                self.powerup_counter += 1
                self.powerups.append(PowerUp(
                    id=powerup_id,
                    x=x,
                    y=y,
                    type="speed",
                    duration=5.0,
                    spawn_time=current_time
                ))
                return True
        return False
    
    def check_powerup_collection(self, player_x: float, player_y: float, player_radius: float = 16) -> Optional[PowerUp]:
        """Kiểm tra player có nhặt được power-up không. Trả về power-up nếu có."""
        for powerup in self.powerups[:]:  # Copy list để có thể xóa
            dx = player_x - powerup.x
            dy = player_y - powerup.y
            dist_sq = dx * dx + dy * dy
            if dist_sq < (player_radius + 10) ** 2:  # 10 là radius của power-up
                self.powerups.remove(powerup)
                return powerup
        return None
    
    def update_powerups(self, current_time: float):
        """Cập nhật power-ups: spawn mới và xóa cũ."""
        # Spawn power-up mới nếu đủ thời gian
        if current_time - self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup(current_time)
            self.powerup_spawn_timer = current_time
    
    def get_powerups_dict(self) -> Dict:
        """Trả về power-ups dưới dạng dict để serialize."""
        return {
            pu.id: {
                "x": pu.x,
                "y": pu.y,
                "type": pu.type
            }
            for pu in self.powerups
        }
    
    def check_collision_with_obstacles(self, player_x: float, player_y: float, player_radius: float = 16, margin: float = 2.0) -> bool:
        """Kiểm tra va chạm giữa player và obstacles với cải thiện độ chính xác.
        
        Args:
            player_x, player_y: Vị trí player
            player_radius: Bán kính player
            margin: Margin an toàn để tránh false positives (mặc định 2.0)
        """
        effective_radius = player_radius + margin
        radius_sq = effective_radius * effective_radius
        
        for obs in self.obstacles:
            # Kiểm tra circle-rectangle collision với cải thiện
            # Tìm điểm gần nhất trên rectangle với circle
            closest_x = max(obs.x, min(player_x, obs.x + obs.width))
            closest_y = max(obs.y, min(player_y, obs.y + obs.height))
            
            # Khoảng cách từ player đến điểm gần nhất
            dx = player_x - closest_x
            dy = player_y - closest_y
            dist_sq = dx * dx + dy * dy
            
            # Nếu khoảng cách nhỏ hơn bán kính hiệu dụng => va chạm
            if dist_sq < radius_sq:
                return True
            
            # Kiểm tra thêm: nếu player nằm hoàn toàn trong rectangle
            if (obs.x <= player_x <= obs.x + obs.width and 
                obs.y <= player_y <= obs.y + obs.height):
                return True
                
        return False
    
    def check_collision_with_obstacles_prediction(self, old_x: float, old_y: float, 
                                                 new_x: float, new_y: float, 
                                                 player_radius: float = 16) -> bool:
        """Kiểm tra va chạm với prediction để tránh player đi xuyên qua obstacles.
        
        Sử dụng line-circle intersection để kiểm tra đường đi từ old_pos đến new_pos
        có cắt obstacles không.
        """
        # Kiểm tra vị trí mới trước
        if self.check_collision_with_obstacles(new_x, new_y, player_radius):
            return True
        
        # Kiểm tra đường đi (line segment) có cắt obstacles không
        for obs in self.obstacles:
            # Kiểm tra line segment (old_x,old_y) -> (new_x,new_y) có cắt rectangle không
            # Sử dụng thuật toán line-rectangle intersection
            if self._line_intersects_rect(old_x, old_y, new_x, new_y, 
                                         obs.x, obs.y, obs.width, obs.height, player_radius):
                return True
        
        return False
    
    def _line_intersects_rect(self, x1: float, y1: float, x2: float, y2: float,
                              rect_x: float, rect_y: float, rect_w: float, rect_h: float,
                              radius: float) -> bool:
        """Kiểm tra line segment có cắt rectangle (với margin = radius) không."""
        # Mở rộng rectangle với margin = radius
        expanded_x = rect_x - radius
        expanded_y = rect_y - radius
        expanded_w = rect_w + 2 * radius
        expanded_h = rect_h + 2 * radius
        
        # Kiểm tra line segment có cắt expanded rectangle không
        # Sử dụng thuật toán Liang-Barsky hoặc đơn giản hơn: kiểm tra các cạnh
        
        # Kiểm tra 4 cạnh của rectangle
        edges = [
            (expanded_x, expanded_y, expanded_x + expanded_w, expanded_y),  # Top
            (expanded_x + expanded_w, expanded_y, expanded_x + expanded_w, expanded_y + expanded_h),  # Right
            (expanded_x, expanded_y + expanded_h, expanded_x + expanded_w, expanded_y + expanded_h),  # Bottom
            (expanded_x, expanded_y, expanded_x, expanded_y + expanded_h),  # Left
        ]
        
        for edge_x1, edge_y1, edge_x2, edge_y2 in edges:
            if self._line_segments_intersect(x1, y1, x2, y2, edge_x1, edge_y1, edge_x2, edge_y2):
                return True
        
        return False
    
    def _line_segments_intersect(self, x1: float, y1: float, x2: float, y2: float,
                                 x3: float, y3: float, x4: float, y4: float) -> bool:
        """Kiểm tra 2 line segments có giao nhau không."""
        # Sử dụng cross product để kiểm tra
        def ccw(Ax, Ay, Bx, By, Cx, Cy):
            return (Cy - Ay) * (Bx - Ax) > (By - Ay) * (Cx - Ax)
        
        return (ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and
                ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4))

    def check_goal_reached(self, x: float, y: float, radius: float = 16) -> bool:
        """Kiểm tra người chơi đã chạm vùng đích chưa (circle-rect overlap)."""
        gx, gy, gw, gh = self.goal_rect
        closest_x = max(gx, min(x, gx + gw))
        closest_y = max(gy, min(y, gy + gh))
        dx = x - closest_x
        dy = y - closest_y
        return (dx * dx + dy * dy) <= radius * radius
    
    def add_score(self, player_id: str, points: int = 10):
        """Thêm điểm cho người chơi khi đạt goal."""
        if player_id in self.players:
            self.players[player_id].score += points

    def reset_player(self, player_id: str, current_time: float = None):
        """Reset player về vị trí spawn và bắt đầu cooldown respawn."""
        p = self.players.get(player_id)
        if p:
            p.x, p.y = self.start_pos
            p.is_dead = True
            if current_time is None:
                import time
                current_time = time.time()
            p.respawn_time = current_time + p.respawn_cooldown
    
    def can_respawn(self, player_id: str, current_time: float) -> bool:
        """Kiểm tra player có thể respawn chưa."""
        p = self.players.get(player_id)
        if not p:
            return False
        if not p.is_dead:
            return True  # Đã sống rồi
        return current_time >= p.respawn_time
    
    def respawn_player(self, player_id: str):
        """Respawn player (chỉ gọi khi can_respawn trả về True)."""
        p = self.players.get(player_id)
        if p:
            p.is_dead = False
            p.respawn_time = 0.0

    def advance_level(self, player_id: str = None):
        """Chuyển level mới. Nếu có player_id, chỉ player đó được điểm."""
        if player_id:
            self.add_score(player_id, 10)  # +10 điểm khi đạt goal
        self.level_index += 1
        self._init_level(self.level_index)
        # Reset tất cả người chơi về điểm bắt đầu
        for p in self.players.values():
            p.x, p.y = self.start_pos
    
    def get_leaderboard(self, top_n: int = 3) -> List[Tuple[str, str, int]]:
        """Trả về top N người chơi có điểm cao nhất. Format: [(id, name, score), ...]"""
        players_list = [(p.id, p.name, p.score) for p in self.players.values()]
        players_list.sort(key=lambda x: x[2], reverse=True)  # Sắp xếp theo score giảm dần
        return players_list[:top_n]

    def process_action(self, player_id, action):
        # action is expected to be a dict. Validate and apply.
        # Placeholder: move actions
        if action.get('type') == 'move':
            dx = action.get('dx', 0)
            dy = action.get('dy', 0)
            p = self.players.get(player_id)
            if p:
                new_x = max(0, min(GAME_WIDTH, p.x + dx))
                new_y = max(0, min(GAME_HEIGHT, p.y + dy))

                # Nếu chạm chướng ngại vật: coi như chết
                if self.check_collision_with_obstacles(new_x, new_y):
                    self.reset_player(player_id)
                    return True

                # Không va chạm: cập nhật
                p.x = new_x
                p.y = new_y
                return True
        return False
    
    def get_obstacles_dict(self) -> Dict:
        """Trả về obstacles dưới dạng dict để serialize."""
        return {
            obs.id: {
                "x": obs.x,
                "y": obs.y,
                "width": obs.width,
                "height": obs.height
            }
            for obs in self.obstacles
        }

    def get_goal_dict(self) -> Dict:
        gx, gy, gw, gh = self.goal_rect
        return {"x": gx, "y": gy, "width": gw, "height": gh}
