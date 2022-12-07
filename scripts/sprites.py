import pygame
from event_timer import Timer
from settings import *
from random import randint, choice

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z = LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.2, -self.rect.height*0.75)

class AnimatedSprite(Generic):
    def __init__(self, pos, frames, groups, z=LAYERS['main']) -> None:
        self.frames = frames
        self.frame_index = 0
        surface = self.frames[self.frame_index]
        super().__init__(pos, surface, groups, z)

    def animate(self, delta_time):
        self.frame_index += 4 * delta_time
        self.frame_index %= len(self.frames)
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time):
        self.animate(delta_time)

class Water(AnimatedSprite):
    def __init__(self, pos, frames, groups) -> None:
        z = LAYERS['water']
        super().__init__(pos, frames, groups, z)

class WildFlower(Generic):
    def __init__(self, pos, surface, groups) -> None:
        z=LAYERS['main']
        super().__init__(pos, surface, groups, z)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height*0.9)

class Particle(Generic):
    def __init__(self, pos, surface, groups, z=LAYERS['main'], color=(255, 255, 255), duration = 200) -> None:
        mask_surface = pygame.mask.from_surface(surface)
        new_surface = mask_surface.to_surface(setcolor=color)
        new_surface.set_colorkey((0, 0, 0))
        
        super().__init__(pos, new_surface , groups, z)
        self.duration = duration
        self.start_time = pygame.time.get_ticks()     
    
    def update(self, delta_time):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

class Interaction(Generic):
    def __init__(self, pos, size, groups, name) -> None:
        surface = pygame.Surface(size)
        super().__init__(pos, surface, groups)
        self.name = name

class Tree(Generic):
    def __init__(self, pos, surface, groups, name, player_add) -> None:
        self.player_add = player_add
        self.name = name
        z=LAYERS['main']
        super().__init__(pos, surface, groups, z)

        self.apple_surface = pygame.image.load(GRAPHICS_PATH + FOLDER_SEPARATOR + 'fruit' + FOLDER_SEPARATOR + 'apple.png')
        self.alive_surface = surface
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
        self.health = 5 if name == 'Small' else 8
        self.alive = True
        self.stump_surface = pygame.image.load(f'{GRAPHICS_PATH}{FOLDER_SEPARATOR}stumps{FOLDER_SEPARATOR}{"small" if name == "Small" else "large"}.png').convert_alpha()
        self.invul_timer = Timer(200)

    def damage(self):
        if self.alive:
            self.health -= 1
            Particle(
                    pos=self.rect.topleft,
                    surface=self.image,
                    groups=self.groups()[0],
                    z=LAYERS['main'],
                    duration=300,
                    color=(200, 0, 0),
                )
            if len(self.apple_sprites.sprites()) > 0:
                random_apple = choice(self.apple_sprites.sprites())
                random_apple.kill()
                Particle(
                    pos=random_apple.rect.topleft,
                    surface=random_apple.image,
                    groups=self.groups()[0],
                    z=LAYERS['fruit']
                )
                self.player_add('apple', 1)

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                Generic(
                    pos=(pos[0] + self.rect.left, pos[1] + self.rect.top), 
                    surface=self.apple_surface, 
                    groups = [self.apple_sprites, self.groups()[0]],
                    z=LAYERS['fruit']
                )

    def check_death(self):
        if self.health <= 0:
            Particle(
                pos=self.rect.topleft,
                surface=self.image,
                groups=self.groups()[0],
                z=LAYERS['fruit'],
                duration=300
            )
            self.alive = False
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height*0.6)
            self.player_add('wood', 3 if self.name == 'Large' else 1)

    def create_tree(self):
        self.alive = True
        self.health = 5 if self.name == 'Small' else 8
        self.image = self.alive_surface
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.2, -self.rect.height*0.75)

    def update(self, delta_time) -> None:
        if self.alive:
            self.check_death()