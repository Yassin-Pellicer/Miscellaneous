from config import JumperConfig, GameConfig
from platform import Platform

class Jumper:
    def __init__(self, jumper_id: int, x: float, y: float) -> None:
        self.jumper_id = jumper_id

        self.width: int = JumperConfig.width
        self.height: int = JumperConfig.height

        self.x: float = x - self.width / 2 if x is not None else JumperConfig.x
        self.y: float = y - self.height / 2 if y is not None else JumperConfig.y
        self.acceleration_x = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.alive = True
        self.score = 0
        self.fitness = 0.0
        self.last_platform_id: int | None = None
        self.can_jump = True

        self.stored_jump_strength: float = 0.0
    
    def trigger_jump(self) -> None:
        if self.alive and self.can_jump:
            self.velocity_y = JumperConfig.jump_strength
            self.can_jump = False

    def hold_left(self) -> None:
        if self.alive:
            self.acceleration_x = -JumperConfig.acceleration_x

    def hold_right(self) -> None:
        if self.alive:
            self.acceleration_x = JumperConfig.acceleration_x

    def release_horizontal(self) -> None:
        if self.alive:
            self.acceleration_x = 0.0

    def update(self, dt: float) -> None:
        if not self.alive:
            return

        self.velocity_y += JumperConfig.gravity * dt
        self.velocity_y = min(self.velocity_y, JumperConfig.max_fall_speed)

        self.velocity_x += self.acceleration_x * dt
        self.velocity_x = max(
            -JumperConfig.max_speed_x,
            min(JumperConfig.max_speed_x, self.velocity_x),
        )

        if self.acceleration_x == 0.0:
            friction = JumperConfig.friction_x * dt
            if abs(self.velocity_x) <= friction:
                self.velocity_x = 0.0
            elif self.velocity_x > 0:
                self.velocity_x -= friction
            else:
                self.velocity_x += friction
    
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def check_out_of_bounds(self) -> bool:
        if not self.alive:
            return True

        jumper_left = self.x - self.width / 2
        jumper_right = self.x + self.width / 2
        jumper_top = self.y - self.height / 2
        jumper_bottom = self.y + self.height / 2

        if (
            jumper_bottom > GameConfig.height or
            jumper_top < 0 or
            jumper_right > GameConfig.width or
            jumper_left < 0
        ):
            self.alive = False
            return True

        return False
    
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

        # Collision with the top of the platform
        if (
            self.velocity_y >= 0 and
            jumper_bottom >= platform_top and
            jumper_top < platform_top and
            jumper_right > platform_left and
            jumper_left < platform_right
        ):
            self.y = platform_top - self.height / 2
            self.velocity_y = 0.0
            self.can_jump = True
            self.trigger_jump()
            
            if self.last_platform_id != platform.platform_id:
                self.score += 1
                self.last_platform_id = platform.platform_id

            return True
        
        return False
