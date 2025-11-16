"""Minimal pygame-based graphics helpers with a retro pixel-art scaler.
It renders to a low-resolution offscreen canvas and scales up with NEAREST
to create a classic 2D look. Also includes a light scanline overlay.
"""
try:
    import pygame
except Exception:
    pygame = None

try:
    # Import screen size to compute scaling
    from client.src.config import SCREEN_WIDTH, SCREEN_HEIGHT
except Exception:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        # Virtual resolution for pixel art style
        self._virtual_w = 320
        self._virtual_h = 240
        # Offscreen low-res canvas
        self.canvas = pygame.Surface((self._virtual_w, self._virtual_h)) if pygame else None
        self._font = pygame.font.Font(None, 18) if pygame else None
        # Precompute scale factors
        self._sx = self._virtual_w / float(SCREEN_WIDTH)
        self._sy = self._virtual_h / float(SCREEN_HEIGHT)

    def clear(self, color=(0, 0, 0)):
        if pygame:
            # Clear the low-res canvas
            self.canvas.fill(color)

    def draw_player(self, x, y, color=(255, 255, 255)):
        if pygame:
            # Scale world coords to virtual canvas
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            # Radius scales with Y factor to keep aspect
            vr = max(1, int(16 * self._sy))
            pygame.draw.circle(self.canvas, color, (vx, vy), vr)

    def draw_name(self, x, y, name: str, color=(230, 230, 230)):
        if pygame and self._font and name:
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            surf = self._font.render(name, True, color)
            rect = surf.get_rect(center=(vx, vy - int(26 * self._sy)))
            self.canvas.blit(surf, rect)

    def draw_obstacle(self, x, y, width, height, color=(100, 50, 30)):
        """Vẽ chướng ngại vật dạng hình chữ nhật."""
        if pygame:
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            vw = max(1, int(width * self._sx))
            vh = max(1, int(height * self._sy))
            pygame.draw.rect(self.canvas, color, (vx, vy, vw, vh))
            # Vẽ viền để dễ nhìn
            pygame.draw.rect(self.canvas, (60, 30, 15), (vx, vy, vw, vh), 1)

    def draw_goal(self, x, y, width, height):
        if pygame:
            vx = int(x * self._sx)
            vy = int(y * self._sy)
            vw = max(1, int(width * self._sx))
            vh = max(1, int(height * self._sy))
            # Vùng đích màu xanh neon
            pygame.draw.rect(self.canvas, (0, 220, 100), (vx, vy, vw, vh))
            pygame.draw.rect(self.canvas, (0, 150, 70), (vx, vy, vw, vh), 1)

    def _draw_scanlines(self, surface):
        if not pygame:
            return
        w, h = surface.get_size()
        # Semi-transparent black lines every 2 pixels
        scan = pygame.Surface((w, h), pygame.SRCALPHA)
        scan.fill((0, 0, 0, 0))
        for y in range(0, h, 2):
            pygame.draw.line(scan, (0, 0, 0, 24), (0, y), (w, y))
        surface.blit(scan, (0, 0))

    def present(self):
        if pygame:
            # Scale low-res canvas to screen with nearest-neighbor
            scaled = pygame.transform.scale(self.canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled, (0, 0))
            # Optional scanline overlay for CRT feel
            self._draw_scanlines(self.screen)
            pygame.display.flip()
