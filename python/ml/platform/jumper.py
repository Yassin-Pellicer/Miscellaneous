from config import JumperConfig, GameConfig
from platform import Platform

class Jumper:
    def __init__(self, jumper_id: int, x: float, y: float) -> None:
        self.jumper_id = jumper_id

        self.width: int = JumperConfig.width
        self.height: int = JumperConfig.height

        self.x: float = x - self.width / 2 if x is not None else JumperConfig.x
        self.y: float = y - self.height / 2 if y is not None else JumperConfig.y
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.alive = True
        self.score = 0
        self.fitness = 0.0

        self.stored_jump_strength: float = 0.0
        self.stored_side_strength: float = 0.0
        self.is_holding_jump: bool = False
        self.can_load_jump: bool = True

    def hold_jump(self) -> None:
        if self.alive and self.can_load_jump:
            self.is_holding_jump = True
            self.stored_jump_strength = min(
                self.stored_jump_strength + JumperConfig.max_jump_strength * JumperConfig.charge_coefficient, 
                JumperConfig.max_jump_strength
            )

    def hold_left(self) -> None:
        if self.alive and not self.is_holding_jump:
            self.stored_side_strength = max(
                self.stored_side_strength - JumperConfig.speed_x * JumperConfig.charge_coefficient, 
                -JumperConfig.speed_x
            )

    def hold_right(self) -> None:
        if self.alive and not self.is_holding_jump:
            self.stored_side_strength = min(
                self.stored_side_strength + JumperConfig.speed_x * JumperConfig.charge_coefficient, 
                JumperConfig.speed_x
            )

    def release_jump(self) -> None:
        if self.alive and self.is_holding_jump:
            self.velocity_y = self.stored_jump_strength
            self.stored_jump_strength = 0.0
            self.velocity_x = self.stored_side_strength
            self.stored_side_strength = 0.0
            self.is_holding_jump = False
            self.can_load_jump = False

    def update(self, dt: float) -> None:
        if not self.alive:
            return

        self.velocity_y += JumperConfig.gravity * dt
        self.velocity_y = min(self.velocity_y, JumperConfig.max_fall_speed)

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
    
    def check_collision(self, platform: Platform) -> bool:
        if not self.alive:
            return True
        
        jumper_left = self.x - self.width / 2
        jumper_right = self.x + self.width / 2
        jumper_top = self.y - self.height / 2
        jumper_bottom = self.y + self.height / 2

        platform_left = platform.x
        platform_right = platform.x + platform.width
        platform_top = platform.y
        platform_bottom = platform.y + platform.height
        
        # Out of Bounds
        if (
            jumper_bottom >= GameConfig.height and
            jumper_top < 0 and
            jumper_right > GameConfig.width and
            jumper_left < 0
        ):
            self.alive = False
            return True

        # Collision with the top of the platform
        if (
            jumper_bottom >= platform_top and
            jumper_top < platform_top and
            jumper_right > platform_left and
            jumper_left < platform_right
        ):
            self.y = platform_top - self.height / 2
            self.velocity_y = 0.0
            self.velocity_x = 0.0
            self.can_load_jump = True
            return True

        # Bottom collision
        if (
            jumper_top < platform_bottom and
            jumper_bottom > platform_bottom and
            jumper_right > platform_left and
            jumper_left < platform_right
        ):
            self.alive = False
            return True

        # Left side collision
        if (
            jumper_right > platform_left and
            jumper_left < platform_right and
            jumper_bottom > platform_top and
            jumper_top < platform_bottom
        ):
            self.alive = False
            return True 

        # Right side collision
        if (
            jumper_left < platform_right and
            jumper_right > platform_left and
            jumper_bottom > platform_top and
            jumper_top < platform_bottom
        ):
            self.alive = False
            return True
        
        return False