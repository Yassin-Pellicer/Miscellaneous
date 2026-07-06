import pygame # type: ignore
from itertools import cycle
from config import JumperConfig, GameConfig, PlatformConfig

class Renderer:

    def __init__(self, config) -> None:
        pygame.init()
        pygame.display.set_caption("Platform")

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

        self._jumper_colors: dict[int, tuple[int, int, int]] = {}

    def tick(self, fps: int, speed: float | None = None) -> float:
        if speed is None:
            speed = self.config.speed

        raw_dt = self.clock.tick(max(1, int(fps * speed))) / 1000.0
        return min(raw_dt * speed, 1.0 / 15.0)

    def draw(self, scenario) -> None:
        self.screen.fill(self.config.sky_color)

        self._draw_platforms(scenario)
        self._draw_jumpers(scenario)
        self._draw_hud(scenario)

        pygame.display.flip()

    def _draw_platforms(self, scenario) -> None:
        for platform in scenario.platforms:
            rect = pygame.Rect(
                int(platform.x - platform.width / 2),
                int(platform.y - platform.height / 2),
                int(platform.width),
                int(platform.height),
            )

            pygame.draw.rect(self.screen, PlatformConfig.color, rect)

    def _draw_jumpers(self, scenario) -> None:
        for jumper in scenario.jumpers:
            if not jumper.alive:
                continue

            color = self._get_jumper_color(jumper.jumper_id)

            rect = pygame.Rect(
                int(jumper.x - jumper.width / 2),
                int(jumper.y - jumper.height / 2),
                JumperConfig.width,
                JumperConfig.height,
            )

            pygame.draw.ellipse(self.screen, color, rect)

    def _draw_hud(self, scenario) -> None:
        alive_count = sum(1 for  jumper in scenario.jumpers if jumper.alive)
        best_score = max((jumper.score for jumper in scenario.jumpers), default=0)

        text = self.font.render(
            f"Gen {scenario.generation}  Alive {alive_count}  Score {best_score}",
            True,
            self.config.text_color,
        )

        self.screen.blit(text, (16, 16))

    def _get_jumper_color(self, jumper_id: int) -> tuple[int, int, int]:
        if jumper_id not in self._jumper_colors:
            self._jumper_colors[jumper_id] = next(self._palette)

        return self._jumper_colors[jumper_id]
