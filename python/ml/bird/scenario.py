from bird import Bird
from pipe import Pipe
from config import GameConfig, BirdConfig, PipeConfig, Observation

class Scenario:

    def __init__(self) -> None:
        self.config = GameConfig()
        self.generation = 0
        self.birds: list[Bird] = []
        self.pipes: list[Pipe] = []
        self.pipe_timer = 0.0
        self.spawned_pipe_count = 0

    def reset(self, bird_count: int = 1) -> list[Observation]:
        self.generation += 1
        self.pipe_timer = 0.0

        self.birds = [
            Bird(
                bird_id=i,
                x=BirdConfig.x,
                y=self.config.spawn_y,
            )
            for i in range(bird_count)
        ]

        self.pipes = [
            Pipe(
                x=self.config.width,
                screen_height=self.play_area_height,
            )
        ]
        self.spawned_pipe_count = len(self.pipes)

        return self.get_observations()

    @property
    def play_area_height(self) -> int:
        return self.config.height - self.config.floor_height

    def update(
        self, dt: float, actions: dict[int, bool] | None = None
    ) -> list[Observation]:
        if actions is None:
            actions = {}

        for bird in self.birds:
            if actions.get(bird.bird_id, False):
                bird.trigger_flap()

            bird.update(dt)

        for pipe in self.pipes:
            pipe.update(dt)

        self._spawn_pipes(dt)
        self._remove_old_pipes()
        self._check_collisions()
        self._update_scores()

        return self.get_observations()

    def _spawn_pipes(self, dt: float) -> None:
        self.pipe_timer += dt

        if self.pipe_timer >= PipeConfig.interval:
            self.pipe_timer = 0.0
            self.pipes.append(
                Pipe(
                    x=self.config.width,
                    screen_height=self.play_area_height,
                )
            )
            self.spawned_pipe_count += 1

    def _remove_old_pipes(self) -> None:
        self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]

        if not self.pipes:
            self.pipes.append(
                Pipe(
                    x=self.config.width,
                    screen_height=self.play_area_height,
                )
            )
            self.spawned_pipe_count += 1

    def _check_collisions(self) -> None:
        for bird in self.birds:
            if not bird.alive:
                continue

            for pipe in self.pipes:
                if bird.check_collision(pipe, self.play_area_height):
                    break

    def _update_scores(self) -> None:
        for bird in self.birds:
            if not bird.alive:
                continue

            bird.score = self.spawned_pipe_count

    def _next_pipe_for_bird(self, bird: Bird) -> Pipe:
        bird_left = bird.x - BirdConfig.width / 2

        for pipe in self.pipes:
            if pipe.x + pipe.width >= bird_left:
                return pipe

        return self.pipes[0]

    def _build_observation(self, bird: Bird) -> Observation:
        pipe = self._next_pipe_for_bird(bird)

        gap_top = pipe.gap_y
        gap_bottom = pipe.gap_y + pipe.gap_height
        gap_center = pipe.gap_y + pipe.gap_height / 2

        return Observation(
            bird_id=bird.bird_id,
            y=bird.y,
            velocity=bird.velocity,
            next_pipe_x=pipe.x,
            next_gap_y=gap_center,
            distance_to_pipe=pipe.x - bird.x,
            gap_top=gap_top,
            gap_bottom=gap_bottom,
            distance_to_gap_center=gap_center - bird.y,
            score=bird.score,
        )

    def get_observations(self) -> list[Observation]:
        return [self._build_observation(bird) for bird in self.birds if bird.alive]

    def all_birds_dead(self) -> bool:
        return all(not bird.alive for bird in self.birds)
