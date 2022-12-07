import pygame
from pytmx.util_pygame import load_pygame
from utils import import_folder_dict, import_folder
from random import choice
from settings import *

class SoilLayer:
    def __init__(self, all_sprites) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        self.soil_surfaces = import_folder_dict(GRAPHICS_PATH + FOLDER_SEPARATOR + 'soil' + FOLDER_SEPARATOR)
        self.soil_water_surfaces = import_folder(GRAPHICS_PATH + FOLDER_SEPARATOR + 'soil_water' + FOLDER_SEPARATOR)

        self.create_soil_grid()

    def create_soil_grid(self):
        # requirements
        # if the area is farmable
        # if the soil has a plant
        # if the soil has been watered
        tmx_data = load_pygame(DATA_PATH + FOLDER_SEPARATOR + 'map.tmx')
        h_tiles, v_tiles = tmx_data.width, tmx_data.height
        
        self.grid = [ [ [] for _ in range(h_tiles) ]  for _ in range(v_tiles)]
        self.hit_rects = []
        for x, y, _ in tmx_data.get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
            rect = pygame.Rect(
                    (x*TILE_SIZE,y*TILE_SIZE),
                    (TILE_SIZE, TILE_SIZE),
                )
            self.hit_rects.append( rect )
    
    def get_hit(self, point):
        hits = filter(
            lambda rect : rect.collidepoint(point),
            self.hit_rects
        )
        for hit in hits:
            x = hit.x // TILE_SIZE
            y = hit.y // TILE_SIZE
            
            if 'F' in self.grid[y][x] and not 'X' in self.grid[y][x]:
                self.grid[y][x].append('X')
                self.create_soil_tiles()

    def water(self, point):
        hits = filter(
            lambda sprite : sprite.rect.collidepoint(point),
            self.soil_sprites
        )

        for hit in hits:
            x = hit.rect.x // TILE_SIZE
            y = hit.rect.y // TILE_SIZE
            
            if not 'W' in self.grid[y][x]:
                self.grid[y][x].append('W')
                pos = (x*TILE_SIZE, y*TILE_SIZE)
                WaterTile(pos, choice(self.soil_water_surfaces), [self.all_sprites, self.water_sprites])

    def water_all(self):
        for soil in self.soil_sprites:
            self.water(soil.rect.center)

    def remove_water(self):
        for soil in self.water_sprites:
            soil.kill()
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def plant_seed(self, point, seed, collision_group):
        hits = filter(
            lambda sprite : sprite.rect.collidepoint(point),
            self.soil_sprites
        )

        for hit in hits:
            x = hit.rect.x // TILE_SIZE
            y = hit.rect.y // TILE_SIZE

            if not 'P' in self.grid[y][x]:
                self.grid[y][x].append('P')
                Plant(plant_type=seed, soil=hit, groups=[self.all_sprites, self.plant_sprites, collision_group])

    def create_soil_tiles(self):
        for soil in self.soil_sprites:
            soil.kill()
        soils =  [ [ [] for _ in range(len(self.grid[0])) ]  for _ in range(len(self.grid))]

        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    b = 'b' if index_row > 0 and 'X' in self.grid[index_row - 1][index_col] else ''
                    t = 't' if index_row < len(self.grid) - 1 and 'X' in self.grid[index_row + 1][index_col] else ''
                    l = 'l' if index_col < len(row) - 1 and 'X' in self.grid[index_row][index_col + 1] else ''
                    r = 'r' if index_col > 0 and 'X' in self.grid[index_row][index_col - 1] else ''

                    tile_type = b + t + l + r
                    tile_type = 'o' if not tile_type else tile_type
                    soils[index_row][index_col] = tile_type

                    pos = (index_col*TILE_SIZE, index_row*TILE_SIZE)
                    SoilTile(pos, self.soil_surfaces[tile_type], [self.all_sprites, self.soil_sprites])
        # for soil_row in soils:
        #     print(soil_row)

    def check_water(self, point):
        hits = filter(
            lambda sprite : sprite.rect.collidepoint(point),
            self.water_sprites
        )

        return len(list(hits)) > 0

    def remove_plant(self, plant):
        row = plant.rect.centery//TILE_SIZE
        col = plant.rect.centerx//TILE_SIZE

        self.grid[row][col].remove('P')

    def grow_plants(self):
        plants = filter( 
            lambda p : self.check_water(p.rect.center),
            self.plant_sprites
        )

        for plant in plants:
            plant.grow()

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups) -> None:
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']
      
class WaterTile(SoilTile):

    def __init__(self, pos, surface, groups) -> None:
        super().__init__(pos, surface, groups)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, soil, plant_type, groups) -> None:
        super().__init__(groups)
        self.frames = import_folder(GRAPHICS_PATH + FOLDER_SEPARATOR + 'fruit' + FOLDER_SEPARATOR + plant_type)
        self.z = LAYERS['ground plant']
        self.plant_type = plant_type
        
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvastable = False
        
        self.image = self.frames[self.age]
        self.soil = soil
        self.y_offset = PLANTS_OFFSET[plant_type]
        self.rect = self.image.get_rect(midbottom= soil.rect.midbottom + pygame.math.Vector2(0 , self.y_offset))
        
    def grow(self):
        self.age += self.grow_speed

        if int(self.age) > 0:
            self.z = LAYERS['main']
            self.hitbox = self.rect.copy().inflate(-26, -self.rect.height*0.4)

        if self.age >= self.max_age:
            self.age = self.max_age
            self.harvastable = True
        self.image = self.frames[int(self.age)]
        self.rect = self.image.get_rect(midbottom= self.soil.rect.midbottom + pygame.math.Vector2(0 , self.y_offset))
