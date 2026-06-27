import random

from config import PipeConfig

class Pipe:
  def __init__(self, x: float, screen_height: int, config: PipeConfig | None = None) -> None:
    self.config = config or PipeConfig()

    self.x = x
    self.width = self.config.width
    self.gap_height = self.config.gap_height
    self.speed = self.config.speed
    self.passed = False

    self.randomize_gap(screen_height)

  def randomize_gap(self, screen_height: int) -> None:
    min_gap_y = self.config.margin
    max_gap_y = screen_height - self.config.margin - self.gap_height

    self.gap_y = random.uniform(min_gap_y, max_gap_y)

  def update(self, dt: float) -> None:
    self.x -= self.speed * dt

  def is_off_screen(self) -> bool:
    return self.x + self.width < 0

  def has_passed_bird(self, bird) -> bool:
    if not self.passed and self.x + self.width < bird.x:
      self.passed = True
      return True

    return False