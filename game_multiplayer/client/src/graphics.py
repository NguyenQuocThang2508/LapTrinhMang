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
            # Vẽ particle nhỏ (2-3 pixels)
            pygame.draw.circle(canvas, particle.color[:3], (vx, vy), max(1, int(2 * sy)))


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
        # Particle system
        self.particle_system = ParticleSystem()

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

    def draw_particles(self):
        """Vẽ particles lên canvas."""
        if pygame:
            self.particle_system.draw(self.canvas, self._sx, self._sy)

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
