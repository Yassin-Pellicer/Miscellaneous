from dataclasses import dataclass

class GameConfig:
    width: int = 880
    height: int = 720
    fps: int = 165
    speed: float = 10

    platform_separation: int = 200
    margins: int = 300
    displacement_velocity: float = 1200.0

    sky_color: tuple[int, int, int] = (139, 214, 247)
    text_color: tuple[int, int, int] = (29, 29, 29)

    floor: int = 100

class JumperConfig:
    width: int = 21
    height: int = 42
    x: float = GameConfig.width / 2 - width / 2
    y: float = GameConfig.height - height / 2

    charge_coefficient = 0.01
    speed_x = 600.0
    jump_strength: float = -1200.0
    gravity: float = 2400.0
    max_fall_speed: float = 3000.0

class PlatformConfig:
    width: int = 150
    height: int = 20

    variant_width: int = 50

    x: float = GameConfig.width 
    y: float = GameConfig.height

    speed_y = 10.0
    speed_x = 0.0

    acceleration: float = 600
    max_speed: float = 900
    min_speed: float = 100


    color: tuple[int, int, int] = (85, 181, 76)

@dataclass
class Observation:
    jumper_id: int
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    next_platform_x: float
    next_platform_y: float
    horizontal_distance_to_platform: float
    vertical_distance_to_platform: float
    score: int
