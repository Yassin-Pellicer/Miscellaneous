from pathlib import Path
import argparse
import pickle

import neat  # type: ignore
import pygame  # type: ignore

from config import GameConfig
from render import Renderer
from scenario import Scenario

renderer = None
generation = 0
WINNER_PATH = Path(__file__).with_name("checkpoints") / "winner.pkl"


def _patch_neat_spawn_adjustment() -> None:
    def adjust_spawn_exact(self, spawn_amounts, pop_size, min_species_size):
        spawn_amounts = [
            max(min_species_size, int(round(spawn)))
            for spawn in spawn_amounts
        ]

        if len(spawn_amounts) * min_species_size > pop_size:
            raise RuntimeError(
                "Cannot satisfy species minima with pop_size={} and {} species".format(
                    pop_size,
                    len(spawn_amounts),
                )
            )

        while sum(spawn_amounts) < pop_size:
            index = min(range(len(spawn_amounts)), key=spawn_amounts.__getitem__)
            spawn_amounts[index] += 1

        while sum(spawn_amounts) > pop_size:
            removable_indexes = [
                index
                for index, spawn in enumerate(spawn_amounts)
                if spawn > min_species_size
            ]
            if not removable_indexes:
                break
            index = max(removable_indexes, key=spawn_amounts.__getitem__)
            spawn_amounts[index] -= 1

        return spawn_amounts

    neat.reproduction.DefaultReproduction._adjust_spawn_exact = adjust_spawn_exact


def _action_from_output(output: tuple[float, ...] | list[float]) -> str:
    steer = output[0]

    if steer < 0.45:
        return "left"
    if steer > 0.55:
        return "right"
    return "release"


def _inputs_from_observation(obs, game_config: GameConfig) -> tuple[float, ...]:
    return (
        obs.x / game_config.width,
        obs.y / game_config.height,
        obs.velocity_x / max(1.0, abs(game_config.displacement_velocity)),
        obs.velocity_y / max(1.0, abs(game_config.displacement_velocity * 2)),
        obs.next_platform_x / game_config.width,
        obs.next_platform_y / game_config.height,
        obs.horizontal_distance_to_platform / game_config.width,
        obs.vertical_distance_to_platform / game_config.height,
        obs.score / 100.0,
    )


def eval_genomes(genomes, neat_config):
    global renderer
    global generation

    generation += 1

    game_config = GameConfig()

    if renderer is None:
        renderer = Renderer(game_config)

    scenario = Scenario()
    scenario.reset(jumper_count=len(genomes))
    scenario.generation = generation

    nets = {}
    genome_by_jumper_id = {}
    last_score_by_jumper_id = {}
    death_penalized_jumper_ids = set()

    for jumper, (genome_id, genome) in zip(scenario.jumpers, genomes):
        genome.fitness = 0.0
        nets[jumper.jumper_id] = neat.nn.FeedForwardNetwork.create(
            genome,
            neat_config,
        )
        genome_by_jumper_id[jumper.jumper_id] = genome
        last_score_by_jumper_id[jumper.jumper_id] = 0

    elapsed_time = 0.0
    max_simulation_time = 20.0

    while not scenario.all_jumpers_dead() and elapsed_time < max_simulation_time:
        dt = renderer.tick(game_config.fps, speed=game_config.speed)
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        observations = scenario.get_observations()
        actions = {}

        for obs in observations:
            net = nets[obs.jumper_id]
            output = net.activate(_inputs_from_observation(obs, game_config))
            actions[obs.jumper_id] = _action_from_output(output)

        scenario.update(dt, actions)

        for jumper in scenario.jumpers:
            genome = genome_by_jumper_id[jumper.jumper_id]

            if jumper.alive:
                observation = scenario._build_observation(jumper)
                genome.fitness += dt * 3.0
                genome.fitness -= abs(
                    observation.horizontal_distance_to_platform
                ) / game_config.width * dt
            elif jumper.jumper_id not in death_penalized_jumper_ids:
                genome.fitness -= 5.0
                death_penalized_jumper_ids.add(jumper.jumper_id)

            if jumper.score > last_score_by_jumper_id[jumper.jumper_id]:
                genome.fitness += 100.0
                last_score_by_jumper_id[jumper.jumper_id] = jumper.score

        renderer.draw(scenario)


def run_neat():
    _patch_neat_spawn_adjustment()
    config_path = Path(__file__).with_name("neat_config.txt")

    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path),
    )

    population = neat.Population(neat_config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    winner = population.run(eval_genomes, 50)
    WINNER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WINNER_PATH.open("wb") as winner_file:
        pickle.dump(winner, winner_file)

    print("Best genome:")
    print(winner)
    print(f"Saved winner to {WINNER_PATH}")

    pygame.quit()


def run_winner() -> None:
    _patch_neat_spawn_adjustment()
    config_path = Path(__file__).with_name("neat_config.txt")

    if not WINNER_PATH.exists():
        raise FileNotFoundError(
            f"No trained winner found at {WINNER_PATH}. Run `python brain.py train` first."
        )

    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path),
    )

    with WINNER_PATH.open("rb") as winner_file:
        winner = pickle.load(winner_file)

    game_config = GameConfig()
    renderer = Renderer(game_config)
    scenario = Scenario()
    scenario.reset(jumper_count=1)
    net = neat.nn.FeedForwardNetwork.create(winner, neat_config)

    running = True
    while running:
        dt = renderer.tick(game_config.fps, speed=game_config.speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        actions = {}
        observations = scenario.get_observations()
        if observations:
            obs = observations[0]
            output = net.activate(_inputs_from_observation(obs, game_config))
            actions[obs.jumper_id] = _action_from_output(output)

        scenario.update(dt, actions)
        renderer.draw(scenario)

        if scenario.all_jumpers_dead():
            scenario.reset(jumper_count=1)

    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("train", "play"),
        nargs="?",
        default="train",
    )
    args = parser.parse_args()

    if args.mode == "play":
        run_winner()
    else:
        run_neat()
