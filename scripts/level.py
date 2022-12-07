import pygame
from overlay import Overlay
from camera_group import CameraGroup
from settings import *
from utils import *
from player import Player
from transition import Transition
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame

class Level:

    def __init__(self) -> None:
        # get display surface from pygame display
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.setup()
        self.transition = Transition(self.reset, self.player)

    def setup(self):
        tmx_data = load_pygame(DATA_PATH + FOLDER_SEPARATOR + 'map.tmx')

        self.map_setup(tmx_data)
        
        Generic(
            pos = (0,0),
            surface = pygame.image.load(GRAPHICS_PATH + FOLDER_SEPARATOR + 'world' + FOLDER_SEPARATOR + 'ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
        )
        self.overlay = Overlay(self.player)

    def player_add(self, item, qtd):
        self.player.item_inventory[item] += qtd
        print(self.player.item_inventory)

    def map_setup(self, tmx_data):  

        map_generics = {
            'house bottom' : [tmx_data.get_layer_by_name('HouseFloor'), tmx_data.get_layer_by_name('HouseFurnitureBottom')],
            'main' :  [tmx_data.get_layer_by_name('HouseWalls'), tmx_data.get_layer_by_name('HouseFurnitureTop')]
        }
        
        for layer in map_generics:
            assets = map_generics[layer]
            for asset in assets:
                for x, y, surface in asset.tiles():
                    Generic(
                        pos=(x*TITLE_SIZE,y*TITLE_SIZE),
                        surface=surface,
                        groups= self.all_sprites,
                        z = LAYERS[layer]
                    )

        for x, y, surface in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(
                pos=(x*TITLE_SIZE,y*TITLE_SIZE),
                surface=surface,
                groups= [self.all_sprites, self.collision_sprites],
                z = LAYERS[layer]
            )
        
        for x, y, surface in tmx_data.get_layer_by_name('Water').tiles():
            Water(
                pos=(x*TITLE_SIZE,y*TITLE_SIZE),
                frames=import_folder(GRAPHICS_PATH + FOLDER_SEPARATOR + 'water'),
                groups= self.all_sprites,
            )

        for object in tmx_data.get_layer_by_name('Decoration'):
            WildFlower(
                pos=(object.x, object.y),
                surface=object.image,
                groups= [self.all_sprites, self.collision_sprites],
            )

        for object in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(object.x, object.y),
                surface = object.image,
                name = object.name,
                player_add = self.player_add,
                groups = [self.all_sprites, self.collision_sprites, self.tree_sprites],
            )

        for x, y, surface in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(
                (x*TITLE_SIZE, y*TITLE_SIZE),
                pygame.Surface((TITLE_SIZE, TITLE_SIZE)),
                self.collision_sprites
            )

        for object in tmx_data.get_layer_by_name('Player'):
            if object.name == 'Start':
                self.player = Player(
                    pos=(object.x, object.y), 
                    group=self.all_sprites, 
                    collision_sprites=self.collision_sprites, 
                    trees=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites
                )
            elif object.name == 'Bed':
                Interaction(
                    pos=(object.x, object.y),
                    size=(object.width, object.height),
                    groups=self.interaction_sprites,
                    name= object.name
                )

    def reset(self):
        for tree in self.tree_sprites.sprites():
            if not tree.alive:
                tree.create_tree()
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def run(self, delta_time):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(player=self.player)
        self.all_sprites.update(delta_time)
        self.overlay.display()

        if self.player.sleeping:
            self.transition.play()