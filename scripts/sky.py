from random import randint, choice
import pygame
from settings import *
from utils import import_folder
from sprites import Generic

class Rain():
    def __init__(self, all_sprites) -> None:
        self.all_sprites = all_sprites
        self.rain_floor = import_folder(GRAPHICS_PATH + FOLDER_SEPARATOR + 'rain' + FOLDER_SEPARATOR + 'floor')
        self.rain_drops = import_folder(GRAPHICS_PATH + FOLDER_SEPARATOR + 'rain' + FOLDER_SEPARATOR + 'drops')
        self.floor_w, self.floor_h = pygame.image.load(GRAPHICS_PATH + FOLDER_SEPARATOR + 'world' + FOLDER_SEPARATOR + 'ground.png').get_size()

    def create_floor(self):
        Drop(
            surface=choice(self.rain_floor),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=False,
            groups=self.all_sprites,
            z=LAYERS['rain floor']
        )

    def create_drops(self):
        Drop(
            surface=choice(self.rain_drops),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=True,
            groups=self.all_sprites,
            z=LAYERS['rain drops']
        )

    def update(self):
        self.create_drops()
        self.create_floor()

class Drop(Generic):
    def __init__(self, pos, surface, moving, groups, z) -> None:
        super().__init__(pos, surface, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, delta_time) -> None:
        if self.moving:
            self.pos += self.direction * self.speed * delta_time
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class Sky:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.color = self.start_color.copy()
        self.end_color = [38, 101, 189]

    def update(self, delta_time):
        for index, value in enumerate(self.end_color):
            if self.color[index] > value:
                self.color[index] -= 3 * delta_time

    def display(self):
        self.full_surface.fill(self.color)
        self.display_surface.blit(self.full_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)