import pygame

from itertools import cycle

from config import BirdConfig, PipeConfig, GameConfig


class Renderer:

    # We define the constructor which initializes the Pygame library and sets up the display
    def __init__(self, config) -> None:
        pygame.init()
        pygame.display.set_caption("Flappy Bird")

        self.config = config
        self.screen = pygame.display.set_mode((config.width, config.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)

        self._palette = cycle(
            [
                (239, 92, 84),
                (255, 186, 73),
                (90, 196, 255),
                (131, 215, 119),
                (180, 132, 255),
                (255, 123, 172),
            ]
        )

        self._bird_colors: dict[int, tuple[int, int, int]] = {}

    # We define the tick method which controls the frame rate of the game
    def tick(self, fps: int, speed: float | None = None) -> float:
        if speed is None:
            speed = self.config.speed

        raw_dt = self.clock.tick(max(1, int(fps * speed))) / 1000.0
        return min(raw_dt * speed, 1.0 / 15.0)

    def draw(self, scenario) -> None:
        # This method is responsible for drawing the game elements on the screen.
        self.screen.fill(self.config.sky_color)

        self._draw_pipes(scenario)
        self._draw_floor()
        self._draw_birds(scenario)
        self._draw_hud(scenario)

        pygame.display.flip()

    def _draw_floor(self) -> None:
        rect = pygame.Rect(
            0,
            self.config.height - self.config.floor_height,
            self.config.width,
            self.config.floor_height,
        )

        pygame.draw.rect(self.screen, self.config.floor_color, rect)

    def _draw_pipes(self, scenario) -> None:
        for pipe in scenario.pipes:
            top_rect = pygame.Rect(
                int(pipe.x),
                0,
                int(pipe.width),
                int(pipe.gap_y),
            )

            gap_bottom = pipe.gap_y + pipe.gap_height

            bottom_rect = pygame.Rect(
                int(pipe.x),
                int(gap_bottom),
                int(pipe.width),
                int(scenario.play_area_height - gap_bottom),
            )

            pygame.draw.rect(self.screen, PipeConfig.color, top_rect)
            pygame.draw.rect(self.screen, PipeConfig.color, bottom_rect)

    def _draw_birds(self, scenario) -> None:
        for bird in scenario.birds:
            if not bird.alive:
                continue

            color = self._get_bird_color(bird.bird_id)

            bird_rect = pygame.Rect(
                int(bird.x - BirdConfig.width / 2),
                int(bird.y - BirdConfig.height / 2),
                BirdConfig.width,
                BirdConfig.height,
            )

            pygame.draw.ellipse(self.screen, color, bird_rect)

    def _draw_hud(self, scenario) -> None:
        alive_count = sum(1 for bird in scenario.birds if bird.alive)
        best_score = max((bird.score for bird in scenario.birds), default=0)

        text = self.font.render(
            f"Gen {scenario.generation}  Alive {alive_count}  Score {best_score}",
            True,
            self.config.text_color,
        )

        self.screen.blit(text, (16, 16))

    def _get_bird_color(self, bird_id: int) -> tuple[int, int, int]:
        if bird_id not in self._bird_colors:
            self._bird_colors[bird_id] = next(self._palette)

        return self._bird_colors[bird_id]
