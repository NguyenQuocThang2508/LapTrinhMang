"""Server-side game logic placeholder.
This module should validate actions, update authoritative state, and resolve collisions.
"""
from dataclasses import dataclass
import random
from typing import List, Dict, Tuple
from shared.constants import GAME_WIDTH, GAME_HEIGHT

@dataclass
class ServerPlayer:
    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    hp: int = 100

@dataclass
class Obstacle:
    id: str
    x: float = 0.0
    y: float = 0.0
    width: float = 40.0
    height: float = 40.0

class GameLogic:
    def __init__(self):
        self.players = {}
        self.obstacles: List[Obstacle] = []
        # Level system
        self.level_index: int = 1
        self.start_pos: Tuple[float, float] = (50.0, GAME_HEIGHT - 50.0)
        self.goal_rect: Tuple[float, float, float, float] = (GAME_WIDTH - 90.0, 30.0, 60.0, 60.0)
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
    
    def check_collision_with_obstacles(self, player_x: float, player_y: float, player_radius: float = 16) -> bool:
        """Kiểm tra va chạm giữa player và obstacles."""
        for obs in self.obstacles:
            # Kiểm tra circle-rectangle collision
            # Tìm điểm gần nhất trên rectangle với circle
            closest_x = max(obs.x, min(player_x, obs.x + obs.width))
            closest_y = max(obs.y, min(player_y, obs.y + obs.height))
            
            # Khoảng cách từ player đến điểm gần nhất
            dx = player_x - closest_x
            dy = player_y - closest_y
            dist_sq = dx * dx + dy * dy
            
            if dist_sq < player_radius * player_radius:
                return True
        return False

    def check_goal_reached(self, x: float, y: float, radius: float = 16) -> bool:
        """Kiểm tra người chơi đã chạm vùng đích chưa (circle-rect overlap)."""
        gx, gy, gw, gh = self.goal_rect
        closest_x = max(gx, min(x, gx + gw))
        closest_y = max(gy, min(y, gy + gh))
        dx = x - closest_x
        dy = y - closest_y
        return (dx * dx + dy * dy) <= radius * radius

    def reset_player(self, player_id: str):
        p = self.players.get(player_id)
        if p:
            p.x, p.y = self.start_pos

    def advance_level(self):
        self.level_index += 1
        self._init_level(self.level_index)
        # Reset tất cả người chơi về điểm bắt đầu
        for p in self.players.values():
            p.x, p.y = self.start_pos

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
