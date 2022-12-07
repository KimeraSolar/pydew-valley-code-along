import pygame, sys
from level import Level
from settings import *

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            delta_time = self.clock.tick() / 1000
            self.level.run(delta_time)
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()