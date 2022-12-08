from random import randint
import pygame
from overlay import Overlay
from camera_group import CameraGroup
from settings import *
from utils import *
from player import Player
from transition import Transition
from sprites import Generic, Water, WildFlower, Tree, Interaction
from soil import SoilLayer
from sky import Rain, Sky
from merchant import Merchant
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

        self.soil_layer = SoilLayer(self.all_sprites)
        self.map_setup(tmx_data)
        
        Generic(
            pos = (0,0),
            surface = pygame.image.load(GRAPHICS_PATH + FOLDER_SEPARATOR + 'world' + FOLDER_SEPARATOR + 'ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground']
        )
        self.overlay = Overlay(self.player)

        self.rain = Rain(self.all_sprites)
        self.sky = Sky()
        self.will_rain()
        self.shop_active = False
        self.merchant = Merchant(self.player, self.toggle_shop)
        self.show_inventory = False

        self.music = pygame.mixer.Sound(AUDIO_PATH + FOLDER_SEPARATOR + 'music.mp3')
        self.music.set_volume(0.2)
        self.music.play(loops=-1)


    def player_add(self, item, qtd):
        self.player.add_to_inventory(item, qtd)

    def toggle_shop(self):
        self.shop_active = not self.shop_active

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
                        pos=(x*TILE_SIZE,y*TILE_SIZE),
                        surface=surface,
                        groups= self.all_sprites,
                        z = LAYERS[layer]
                    )

        for x, y, surface in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(
                pos=(x*TILE_SIZE,y*TILE_SIZE),
                surface=surface,
                groups= [self.all_sprites, self.collision_sprites],
                z = LAYERS[layer]
            )
        
        for x, y, surface in tmx_data.get_layer_by_name('Water').tiles():
            Water(
                pos=(x*TILE_SIZE,y*TILE_SIZE),
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
                (x*TILE_SIZE, y*TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),
                self.collision_sprites
            )

        for object in tmx_data.get_layer_by_name('Player'):
            if object.name == 'Start':
                self.player = Player(
                    pos=(object.x, object.y), 
                    group=self.all_sprites, 
                    collision_sprites=self.collision_sprites, 
                    trees=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop = self.toggle_shop,
                )
            elif object.name == 'Bed' or object.name == 'Trader':
                Interaction(
                    pos=(object.x, object.y),
                    size=(object.width, object.height),
                    groups=self.interaction_sprites,
                    name= object.name
                )

    def will_rain(self):
        self.raining = randint(0, 10) > 7

    def reset(self):
        for tree in self.tree_sprites.sprites():
            if not tree.alive:
                tree.create_tree()
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()
        
        self.soil_layer.grow_plants()
        self.soil_layer.remove_water()
        self.sky.color.clear()
        self.sky.color.extend(self.sky.start_color)
        self.will_rain()

    def input(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_TAB]:
            self.show_inventory = True
        if pressed_keys[pygame.K_ESCAPE]:
            self.show_inventory = False

    def run(self, delta_time):
        
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(player=self.player)
        self.input()
        
        self.sky.display()

        if self.shop_active:
            self.merchant.update()
        elif self.show_inventory:
            self.player.inventory.update()
        else:
            self.all_sprites.update(delta_time)
            self.sky.update(delta_time)
            if self.raining:
                self.rain.update()
                self.soil_layer.water_all()
        
        self.overlay.display()                

        if self.player.sleeping:
            self.transition.play()