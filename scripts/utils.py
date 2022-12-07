import pygame
from os import walk
from settings import *

def import_folder(path) -> list:
    surface_list = []

    for _, _, files in walk(path):
        for file in files:
            full_path = path + FOLDER_SEPARATOR + file
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list