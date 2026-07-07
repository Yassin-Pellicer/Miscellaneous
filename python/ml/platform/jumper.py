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
    
    def trigger_jump(self) -> None:
        print("Jumper {} triggered jump".format(self.jumper_id))
        if self.alive:
            self.velocity_y = JumperConfig.jump_strength

    def hold_left(self) -> None:
        if self.alive:
            self.velocity_x = -JumperConfig.jump_strength

    def hold_right(self) -> None:
        if self.alive:
            self.velocity_x = -JumperConfig.jump_strength

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
            self.trigger_jump()
            
            if not platform.stepped_on:
                self.score += 1
                platform.stepped_on = True

            return True
        
        return False
