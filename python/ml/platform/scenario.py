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

    def update(self, dt: float, actions: dict[int, str] | None = None):
        default = "release"
        if actions is None:
            actions = {}
        
        for jumper in self.jumpers:
            if actions.get(jumper.jumper_id, default) == "charge":
                jumper.hold_jump()
            if actions.get(jumper.jumper_id, default) == "charge_left":
                jumper.hold_left()
            if actions.get(jumper.jumper_id, default) == "charge_right":
                jumper.hold_right()
            if actions.get(jumper.jumper_id, default) == "release":
                jumper.release_jump()
            jumper.update(dt)
            
        self._spawn_platforms(dt)
        self._remove_old_platforms()
        self._check_collisions()
        self._update_scores()
        self.bring_platforms_down(dt)

    def bring_platforms_down(self, dt: float):
        for platform in self.platforms:
            platform.y += PlatformConfig.speed_y * dt
        
    
    def _spawn_platforms(self, dt: float) -> None:
        self.platform_timer += dt
        if self.platform_timer >= GameConfig.platform_separation / GameConfig.speed:
            self.platform_timer = 0.0
            new_platform = Platform(
                platform_id=self.spawned_platform_count,
                x=0,
                y=PlatformConfig.y,
            )
            previous_platform = self.platforms[-1] if self.platforms else None
            new_platform.x = self._generate_platform_x(new_platform, previous_platform)
            if random.random() < 1 / 7:
                new_platform.randomize_speed_x()
                new_platform.randomize_length_until_reverse()
            self.platforms.append(new_platform)
            self.spawned_platform_count += 1

    def _generate_platform_x(self, new_platform: Platform, previous_platform: Platform | None) -> float:
        max_x = max(0, GameConfig.width - new_platform.width)
        if previous_platform is None:
            return random.uniform(0, max_x)

        min_gap = PlatformConfig.width / 2
        valid_ranges: list[tuple[float, float]] = []

        left_max_x = previous_platform.x - min_gap
        if left_max_x >= 0:
            valid_ranges.append((0, min(max_x, left_max_x)))

        right_min_x = previous_platform.x + min_gap
        if right_min_x <= max_x:
            valid_ranges.append((max(0, right_min_x), max_x))

        if not valid_ranges and previous_platform.x < min_gap:
            new_platform.width = min(
                new_platform.width,
                int(GameConfig.width - previous_platform.x - min_gap)
            )
            max_x = max(0, GameConfig.width - new_platform.width)
            if right_min_x <= max_x:
                valid_ranges.append((max(0, right_min_x), max_x))

        if not valid_ranges:
            left_edge_x = 0
            right_edge_x = max_x
            if abs(left_edge_x - previous_platform.x) >= abs(right_edge_x - previous_platform.x):
                return left_edge_x
            return right_edge_x

        range_start, range_end = random.choice(valid_ranges)
        return random.uniform(range_start, range_end)
    
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
                if jumper.check_collision(platform):
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
