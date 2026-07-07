import pygame # type: ignore
import neat # type: ignore

from config import GameConfig
from render import Renderer
from scenario import Scenario

renderer = None
generation = 0

def eval_genomes(genomes, neat_config):
    global renderer
    global generation

    generation += 1

    game_config = GameConfig()

    if renderer is None:
        renderer = Renderer(game_config)

    scenario = Scenario()
    scenario.reset(bird_count=len(genomes))
    scenario.generation = generation

    nets = {}
    genome_by_bird_id = {}
    last_score_by_bird_id = {}

    for bird, (genome_id, genome) in zip(scenario.birds, genomes):
        genome.fitness = 0.0

        nets[bird.bird_id] = neat.nn.FeedForwardNetwork.create(
            genome,
            neat_config,
        )

        genome_by_bird_id[bird.bird_id] = genome
        last_score_by_bird_id[bird.bird_id] = 0

    while not scenario.all_birds_dead():
        dt = renderer.tick(game_config.fps, speed=game_config.speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        observations = scenario.get_observations()
        actions = {}

        for obs in observations:
            net = nets[obs.bird_id]
            output = net.activate(
                (
                    obs.y / game_config.height,
                    obs.velocity / 600.0,
                    obs.next_pipe_x / game_config.width,
                    obs.next_gap_y / game_config.height,
                    obs.distance_to_pipe / game_config.width,
                    obs.gap_top / game_config.height,
                    obs.gap_bottom / game_config.height,
                    obs.distance_to_gap_center / game_config.height,
                    obs.score / 100.0,
                )
            )
            actions[obs.bird_id] = output[0] > 0.5

        scenario.update(dt, actions)

        for bird in scenario.birds:
            genome = genome_by_bird_id[bird.bird_id]

            if bird.alive:
                genome.fitness += 0.1
            else:
                genome.fitness -= 1.0

            if bird.score > last_score_by_bird_id[bird.bird_id]:
                genome.fitness += 50.0
                last_score_by_bird_id[bird.bird_id] = bird.score

        renderer.draw(scenario)


def run_neat():
    config_path = "neat_config.txt"

    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    population = neat.Population(neat_config)

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    winner = population.run(eval_genomes, 50)

    print("Best genome:")
    print(winner)

    pygame.quit()
