import pygame
from settings import *

class Overlay:
    def __init__(self, player) -> None:
        
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.assets_setup()
        

    def assets_setup(self):
        overlay_path = GRAPHICS_PATH + FOLDER_SEPARATOR + 'overlay'
        self.tools_surfaces = {tool : pygame.image.load(f'{overlay_path}{FOLDER_SEPARATOR}{tool}.png').convert_alpha() for tool in self.player.tools}
        self.seeds_surfaces = {seed : pygame.image.load(f'{overlay_path}{FOLDER_SEPARATOR}{seed}.png').convert_alpha() for seed in self.player.seeds}

    def display(self):
        tool_surface = self.tools_surfaces[self.player.tools[self.player.selected_tool]]
        tool_rect = tool_surface.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surface, tool_rect)

        seed_surface = self.seeds_surfaces[self.player.seeds[self.player.selected_seed]]
        seed_rect = seed_surface.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surface, seed_rect)
