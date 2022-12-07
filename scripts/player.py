import pygame
from event_timer import Timer
from settings import *
from utils import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, trees, interaction_sprites) -> None:
        super().__init__(group)
        
        self.graphics_setup(pos)
        self.dynamics_setup(collision_sprites)
        self.interactions_setup(trees, interaction_sprites)
        self.inventory_setup()
        self.tools_setup()
        self.timers_setup()
        self.seeds_setup()

    def inventory_setup(self):
        self.item_inventory = {
            'wood' : 0,
            'apple' : 0,
            'corn' : 0,
            'tomato' : 0,
        }

    def interactions_setup(self, trees, interaction_sprites):
        self.trees = trees
        self.get_target_pos()
        self.interaction_sprites = interaction_sprites
        self.sleeping = False

    def timers_setup(self):
        self.timers = {
            'tool use' : Timer(350, self.use_tool),
            'tool cooldown' : Timer(1000),
            'tool switch' : Timer(200),
            'seed use' : Timer(350, self.use_seed),
            'seed cooldown' : Timer(1000),
            'seed switch' : Timer(200),
        }

    def tools_setup(self):
        self.tools = ['axe', 'hoe', 'water']
        self.selected_tool = 0

    def seeds_setup(self):
        self.seeds = ['corn', 'tomato']
        self.selected_seed = 0

    def import_assets(self):
        self.animations = { 
            'up' : [], 'down': [], 'left': [], 'right': [],
            'up_idle' : [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_hoe' : [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
            'up_axe' : [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
            'up_water' : [], 'down_water': [], 'left_water': [], 'right_water': [],
        }

        for animation in self.animations.keys():
            full_path = GRAPHICS_PATH + FOLDER_SEPARATOR + 'character' + FOLDER_SEPARATOR + animation
            self.animations[animation] = import_folder(full_path)

    def dynamics_setup(self, collision_sprites) -> None:
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED

        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

    def graphics_setup(self, pos) -> None:
        self.import_assets()        
        self.frame_index = 0
        self.status = 'down_idle'
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        self.z = LAYERS['main']

    def use_tool(self):
        if self.tools[self.selected_tool] == 'hoe':
            pass
        elif self.tools[self.selected_tool] == 'axe':
            for tree in self.trees.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.tools[self.selected_tool] == 'water':
            pass

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_seed(self):
        pass

    def input(self):
        pressed_keys = pygame.key.get_pressed()

        # directions
        if not self.timers['tool use'].active and not self.sleeping:
            if pressed_keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif pressed_keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if pressed_keys[pygame.K_RIGHT]:
                self.status = 'right'
                self.direction.x = 1
            elif pressed_keys[pygame.K_LEFT]:
                self.status = 'left'
                self.direction.x = -1
            else:
                self.direction.x = 0

        # tool use
        if pressed_keys[pygame.K_SPACE] and not self.timers['tool cooldown'].active:
            self.timers['tool use'].activate()
            self.timers['tool cooldown'].activate()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        # change tool
        if pressed_keys[pygame.K_q] and not self.timers['tool switch'].active:
            self.timers['tool switch'].activate()
            self.selected_tool += 1
            self.selected_tool %= len(self.tools)

        # tool use
        if ( pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL] )and not self.timers['seed cooldown'].active:
            self.timers['seed use'].activate()
            self.timers['seed cooldown'].activate()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        # change tool
        if pressed_keys[pygame.K_e] and not self.timers['seed switch'].active:
            self.timers['seed switch'].activate()
            self.selected_seed += 1
            self.selected_seed %= len(self.seeds)

        if pressed_keys[pygame.K_RETURN]:
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Trader':
                    pass
                elif collided_interaction_sprite[0].name == 'Bed':
                    self.status = 'left_idle'
                    self.sleeping = True
                    


    def move(self, delta_time):
        # normalizing the direction vector to keep the speed constant
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * delta_time
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        # vertical movement
        self.pos.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    elif direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def animate(self, delta_time):
        self.frame_index += 4 * delta_time
        self.frame_index %= len(self.animations[self.status])
        self.image = self.animations[self.status][int(self.frame_index)]

    def get_status(self):
        # if the player is not moving, start idling
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        
        # tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.tools[self.selected_tool]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, delta_time) -> None:
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(delta_time)
        self.animate(delta_time)