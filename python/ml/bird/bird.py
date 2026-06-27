from config import BirdConfig

class Bird:
  def __init__(self, bird_id: int, x: float, y: float) -> None:
    self.bird_id = bird_id
    self.x = x
    self.y = y
    self.velocity = 0.0
    self.alive = True
    self.score = 0
    self.fitness = 0.0
    self.time_alive = 0.0

  def trigger_flap(self) -> None:
    if self.alive:
      self.velocity = BirdConfig.flap_strength

  def update(self, dt: float) -> None:
    if not self.alive:
      return

    self.velocity += BirdConfig.gravity * dt
    self.velocity = min(self.velocity, BirdConfig.max_fall_speed)

    self.y += self.velocity * dt
    self.time_alive += dt

  def get_rect(self) -> tuple[float, float, float, float]:
    return (
      self.x - BirdConfig.width / 2,
      self.y - BirdConfig.height / 2,
      BirdConfig.width,
      BirdConfig.height,
    )

  def check_collision(self, pipe, screen_height: int) -> bool:
    if not self.alive:
      return True

    bird_left = self.x - BirdConfig.width / 2
    bird_right = self.x + BirdConfig.width / 2
    bird_top = self.y - BirdConfig.height / 2
    bird_bottom = self.y + BirdConfig.height / 2

    # Ceiling/floor collision
    if bird_top < 0 or bird_bottom > screen_height:
      self.alive = False
      return True

    pipe_left = pipe.x
    pipe_right = pipe.x + pipe.width

    # No horizontal overlap with pipe
    if bird_right < pipe_left or bird_left > pipe_right:
      return False

    gap_top = pipe.gap_y
    gap_bottom = pipe.gap_y + pipe.gap_height

    # Bird overlaps pipe horizontally and is outside the gap vertically
    if bird_top < gap_top or bird_bottom > gap_bottom:
      self.alive = False
      return True

    return False