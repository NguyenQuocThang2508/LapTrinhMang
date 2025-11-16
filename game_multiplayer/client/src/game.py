"""Game state and basic logic placeholder."""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Player:
    id: str
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    hp: int = 100
    spawn_time: float = None  # Thời điểm spawn (None nếu không mới spawn)

@dataclass
class Obstacle:
    id: str
    x: float = 0.0
    y: float = 0.0
    width: float = 40.0
    height: float = 40.0

@dataclass
class GameState:
    players: Dict[str, Player] = field(default_factory=dict)
    obstacles: Dict[str, Obstacle] = field(default_factory=dict)

    def update(self, dt: float):
        # apply physics, cooldowns, etc. Placeholder.
        pass

    def add_player(self, player_id: str):
        if player_id not in self.players:
            # Vị trí ban đầu random
            import random
            import time
            self.players[player_id] = Player(
                id=player_id,
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                spawn_time=time.time()  # Ghi lại thời điểm spawn
            )

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]
