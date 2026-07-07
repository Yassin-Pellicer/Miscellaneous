import math
import random

from jumper import Jumper
from platform import Platform
from config import GameConfig, JumperConfig, Observation, PlatformConfig

class Scenario:
    platform_buffer_size = 8

    def __init__(self) -> None:
        self.generation = 0
        self.jumpers: list[Jumper] = []
        self.platforms: list[Platform] = []
        self.platform_timer = 0.0
        self.spawned_platform_count = 0
        self.displacement = math.inf

    def reset(self, jumper_count: int = 1) -> list[Observation]:
        self.generation += 1
        self.platform_timer = 0.0
        self.platforms = []
        self.spawned_platform_count = 0
        self.displacement = math.inf

        initial_y = GameConfig.height - GameConfig.floor - PlatformConfig.height / 2
        next_x = (GameConfig.width - PlatformConfig.width) / 2
        for index in range(self.platform_buffer_size):
            platform = self._create_platform(
                x=next_x,
                y=initial_y - index * GameConfig.platform_separation,
                randomize_x=index > 0,
            )
            if index == 0:
                platform.x = (GameConfig.width - platform.width) / 2
            next_x = platform.x

        self.jumpers = [
            Jumper(
                jumper_id=i,
                x=JumperConfig.x,
                y=JumperConfig.y,
            )
            for i in range(jumper_count)
        ]
        initial_platform = self.platforms[0]
        for jumper in self.jumpers:
            jumper.x = initial_platform.x + initial_platform.width / 2
            jumper.y = initial_platform.y - initial_platform.height / 2 - jumper.height / 2
            jumper.last_platform_id = initial_platform.platform_id

        return self.get_observations()

    def update(self, dt: float, actions: dict[int, str] | None = None) -> list[Observation]:
        default = "release"
        if actions is None:
            actions = {}
        
        for jumper in self.jumpers:
            action = actions.get(jumper.jumper_id, default)
            if action == "left":
                jumper.hold_left()
            elif action == "right":
                jumper.hold_right()
            else:
                jumper.release_horizontal()
            jumper.update(dt)
            
        self._remove_old_platforms()
        self._check_collisions(dt)
        self._ensure_platform_buffer()
        self._update_scores()
        self.displace_world(dt)
        return self.get_observations()
        
    def _create_platform(self, x: float, y: float, randomize_x: bool = True) -> Platform:
        new_platform = Platform(
            platform_id=self.spawned_platform_count,
            x=0,
            y=PlatformConfig.y,
        )
        if randomize_x:
            min_x = max(0.0, x - GameConfig.margins)
            max_x = min(GameConfig.width - new_platform.width, x + GameConfig.margins)
            if min_x > max_x:
                min_x = max_x = min(
                    max(0.0, x),
                    GameConfig.width - new_platform.width,
                )
            new_platform.x = random.uniform(min_x, max_x)
        else:
            new_platform.x = min(
                max(0.0, x),
                GameConfig.width - new_platform.width,
            )
        new_platform.y = y
        self.platforms.append(new_platform)
        self.spawned_platform_count += 1
        return new_platform

    def displace_world(self, dt: float) -> None:
        if self.displacement >= GameConfig.platform_separation:
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

    def _ensure_platform_buffer(self) -> None:
        if not self.platforms:
            initial_y = GameConfig.height - GameConfig.floor - PlatformConfig.height / 2
            self._create_platform(
                x=(GameConfig.width - PlatformConfig.width) / 2,
                y=initial_y,
                randomize_x=False,
            )

        while len(self.platforms) < self.platform_buffer_size:
            top_platform = min(self.platforms, key=lambda platform: platform.y)
            self._spawn_platforms(top_platform)
    
    def _remove_old_platforms(self) -> None:
        self.platforms = [
            platform for platform in self.platforms
            if platform.y - platform.height / 2 <= GameConfig.height
        ]
    
    def _check_collisions(self, dt: float) -> None:
        for jumper in self.jumpers:
            if not jumper.alive:
                continue
            if jumper.check_out_of_bounds():
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
    
    def _next_platform_for_jumper(self, jumper: Jumper) -> Platform:
        next_platforms = [
            platform
            for platform in self.platforms
            if (
                jumper.last_platform_id is None or
                platform.platform_id > jumper.last_platform_id
            )
        ]

        if next_platforms:
            return min(next_platforms, key=lambda platform: platform.platform_id)

        return min(
            self.platforms,
            key=lambda platform: abs(platform.y + platform.height / 2 - jumper.y),
        )

    def _build_observation(self, jumper: Jumper) -> Observation:
        target_platform = self._next_platform_for_jumper(jumper)
        target_center_x = target_platform.x + target_platform.width / 2

        return Observation(
            jumper_id=jumper.jumper_id,
            x=jumper.x,
            y=jumper.y,
            velocity_x=jumper.velocity_x,
            velocity_y=jumper.velocity_y,
            next_platform_x=target_center_x,
            next_platform_y=target_platform.y,
            horizontal_distance_to_platform=target_center_x - jumper.x,
            vertical_distance_to_platform=target_platform.y - jumper.y,
            score=jumper.score,
        )

    def get_observations(self) -> list[Observation]:
        return [
            self._build_observation(jumper)
            for jumper in self.jumpers
            if jumper.alive
        ]

    def all_jumpers_dead(self) -> bool:
        return all(not jumper.alive for jumper in self.jumpers)
