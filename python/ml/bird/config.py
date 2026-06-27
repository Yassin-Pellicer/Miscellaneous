from dataclasses import dataclass

class GameConfig:
    width: int = 480
    height: int = 720
    floor_height: int = 110
    spawn_y: float = 300.0
    fps: int = 165
    speed: float = 1.5

    sky_color: tuple[int, int, int] = (139, 214, 247)
    floor_color: tuple[int, int, int] = (222, 216, 149)
    text_color: tuple[int, int, int] = (29, 29, 29)

class BirdConfig:
    width: int = 34
    height: int = 24
    x: float = 120.0

    flap_strength: float = -400.0
    gravity: float = 1200.0
    max_fall_speed: float = 500.0

class PipeConfig:
    width: int = 78
    gap_height: int = 180
    speed: float = 180.0
    interval: float = 1.3
    margin: int = 90

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
