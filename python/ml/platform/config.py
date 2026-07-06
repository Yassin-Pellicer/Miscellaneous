from dataclasses import dataclass

class GameConfig:
    width: int = 480
    height: int = 720
    fps: int = 165
    speed: float = 3.5

    platform_separation: int = 400
    platform_max_separation_variance: int = 150
    platform_min_separation_variance: int = 50

    sky_color: tuple[int, int, int] = (139, 214, 247)
    text_color: tuple[int, int, int] = (29, 29, 29)

    floor_height: int = 110

class JumperConfig:
    width: int = 21
    height: int = 42
    x: float = GameConfig.width / 2 - width / 2
    y: float = GameConfig.height - height / 2

    charge_coefficient = 0.01
    speed_x = 100.0
    max_jump_strength: float = -800.0
    gravity: float = 1200.0
    max_fall_speed: float = 600.0

class PlatformConfig:
    width: int = 200
    height: int = 20

    variant_width: int = 100
    variant_min_length_until_reverse: int = 50
    variant_max_length_until_reverse: int = 200
    variant_speed_x: int = 100

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
    bird_id: int
    y: float
    velocity: float
    next_pipe_x: float
    next_gap_y: float
    distance_to_pipe: float
    gap_top: float
    gap_bottom: float
    distance_to_gap_center: float
    score: int
