import math
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
        self.displacement = math.inf

    def reset(self, jumper_count: int = 1) -> None:
        self.generation += 1
        self.platform_timer = 0.0
        self.platforms = []
        self.spawned_platform_count = 0

        initial_x = GameConfig.width / 2
        initial_y = GameConfig.height - GameConfig.floor - PlatformConfig.height / 2
        for index in range(4):
            self._create_platform(
                x=initial_x,
                y=initial_y - index * GameConfig.platform_separation,
            )

        self.jumpers = [
            Jumper(
                jumper_id=i,
                x=JumperConfig.x,
                y=JumperConfig.y,
            )
            for i in range(jumper_count)
        ]
        initial_platform = self.platforms[0]
        initial_platform.x = (GameConfig.width - initial_platform.width) / 2
        for jumper in self.jumpers:
            jumper.x = initial_platform.x + initial_platform.width / 2
            jumper.y = initial_platform.y - initial_platform.height / 2 - jumper.height / 2

    def update(self, dt: float, actions: dict[int, str] | None = None):
        default = "release"
        if actions is None:
            actions = {}
        
        for jumper in self.jumpers:
            if actions.get(jumper.jumper_id, default) == "left":
                jumper.hold_left()
            if actions.get(jumper.jumper_id, default) == "right":
                jumper.hold_right()
            jumper.update(dt)
            
        self._remove_old_platforms()
        self._check_collisions(dt)
        self._update_scores()
        self.displace_world(dt)
        
    def _create_platform(self, x: float, y: float) -> Platform:
        new_platform = Platform(
            platform_id=self.spawned_platform_count,
            x=0,
            y=PlatformConfig.y,
        )
        new_platform.x = random.uniform(GameConfig.margins/2, GameConfig.width - GameConfig.margins)
        new_platform.y = y
        self.platforms.append(new_platform)
        self.spawned_platform_count += 1
        return new_platform

    def displace_world(self, dt: float) -> None:
        if self.displacement > GameConfig.platform_separation:
            return
        self.displacement += dt * GameConfig.displacement_velocity
        for platform in self.platforms:
            platform.y += dt * GameConfig.displacement_velocity
        for jumper in self.jumpers:
            jumper.y += dt * GameConfig.displacement_velocity
        
    def _spawn_platforms(self, platform: Platform) -> None:
        next_y = platform.y - GameConfig.platform_separation
        for existing_platform in self.platforms:
            if abs(existing_platform.y - next_y) < 1e-6:
                return
        self._create_platform(x=platform.x, y=next_y)
    
    def _remove_old_platforms(self) -> None:
        self.platforms = [
            platform for platform in self.platforms
            if platform.y - platform.height / 2 <= GameConfig.height
        ]
    
    def _check_collisions(self, dt: float) -> None:
        for jumper in self.jumpers:
            if not jumper.alive:
                continue
            for platform in self.platforms:
                previous_score = jumper.score
                if jumper.check_collision(platform):
                    if jumper.score > previous_score:
                        self._spawn_platforms(platform)
                        if jumper.score > 1: self.displacement = 0 
                    break

    def _update_scores(self) -> None:
        for jumper in self.jumpers:
            if not jumper.alive:
                continue
            jumper.fitness = jumper.score
    
    def _next_platform_for_jumper(self, jumper: Jumper) -> Platform | None:
        for platform in self.platforms:
            if platform.x + platform.width / 2 >= jumper.x - jumper.width / 2:
                return platform
        return None

    def all_jumpers_dead(self) -> bool:
        return all(not jumper.alive for jumper in self.jumpers)
