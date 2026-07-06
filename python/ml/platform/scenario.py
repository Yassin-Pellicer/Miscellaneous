import random

from jumper import Jumper
from platform import Platform
from config import GameConfig, JumperConfig, PlatformConfig

class Scenario:
    def __init__(self) -> None:
        self.generation = 0
        self.jumpers: list[Jumper] = []
        self.platforms: list[Platform] = []
        self.platform_timer = 0.0
        self.spawned_platform_count = 0

    def reset(self, jumper_count: int = 1) -> None:
        self.generation += 1
        self.platform_timer = 0.0

        self.jumpers = [
            Jumper(
                jumper_id=i,
                x=JumperConfig.x,
                y=JumperConfig.y,
            )
            for i in range(jumper_count)
        ]

        self.platforms = [
            Platform(
                platform_id=0,
                x=PlatformConfig.x,
                y=PlatformConfig.y,
            )
        ]
        self.spawned_platform_count = len(self.platforms)
    
    def _spawn_platforms(self, dt: float) -> None:
        self.platform_timer += dt
        if self.platform_timer >= GameConfig.platform_separation / GameConfig.speed:
            self.platform_timer = 0.0
            new_platform = Platform(
                platform_id=self.spawned_platform_count,
                x=0,
                y=PlatformConfig.y,
            )
            new_platform.x = random.uniform(0, max(0, GameConfig.width - new_platform.width))
            if random.random() < 1 / 7:
                new_platform.randomize_speed_x()
                new_platform.randomize_length_until_reverse()
            self.platforms.append(new_platform)
            self.spawned_platform_count += 1
    
    def _remove_old_platforms(self) -> None:
        self.platforms = [
            platform for platform in self.platforms
            if platform.y + platform.width / 2 >= 0
        ]
    
    def _check_collisions(self) -> None:
        for jumper in self.jumpers:
            if not jumper.alive:
                continue
            for platform in self.platforms:
                if jumper.check_collision(platform, self.play_area_height):
                    break

    def _update_scores(self) -> None:
        for jumper in self.jumpers:
            if not jumper.alive:
                continue
            jumper.score = self.spawned_platform_count
    
    def _next_platform_for_jumper(self, jumper: Jumper) -> Platform | None:
        for platform in self.platforms:
            if platform.x + platform.width / 2 >= jumper.x - jumper.width / 2:
                return platform
        return None

    def all_jumpers_dead(self) -> bool:
        return all(not jumper.alive for jumper in self.jumpers)
