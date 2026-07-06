import pygame

from config import GameConfig
from render import Renderer
from scenario import Scenario

def run() -> None:
    config = GameConfig()
    renderer = Renderer(config)

    scenario = Scenario()
    scenario.reset(jumper_count=10)

    running = True

    while running:
        dt = renderer.tick(config.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        scenario.update(dt)
        renderer.draw(scenario)

        if scenario.all_jumpers_dead():
            scenario.reset(jumper_count=10)

    pygame.quit()

if __name__ == "__main__":
    run()
