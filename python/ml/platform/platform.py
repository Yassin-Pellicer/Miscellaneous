import random

from config import PlatformConfig, GameConfig 

class Platform:
    def __init__(self, platform_id: int, x: float, y: float) -> None:
        self.platform_id = platform_id

        self.width: int = PlatformConfig.width
        self.height: int = PlatformConfig.height

        self.x: float = x - self.width / 2 if x is not None else PlatformConfig.x
        self.y: float = y - self.height / 2 if y is not None else PlatformConfig.y

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.length_until_reverse = 0
        self.floor_advance_distance = 0.0
        self.floor_advance_moved = 0.0
        self.floor_advance_direction = 1.0

        self.stepped_on = False

        self.randomize_width()

    def randomize_width(self) -> None:
        self.width = PlatformConfig.width + random.randint(
            -PlatformConfig.variant_width,
            PlatformConfig.variant_width
        )

    def update(self, dt: float) -> None:
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        if self.length_until_reverse > 0:
            self.length_until_reverse -= abs(self.velocity_x) * dt
        else:
            self.velocity_x *= -1
