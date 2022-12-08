from functools import reduce
import pygame
from settings import *
from event_timer import Timer

class Menu:
    def __init__(self, player) -> None:
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONT_PATH + FOLDER_SEPARATOR + 'LycheeSoda.ttf', 30)
        self.width = 350
        self.space = 6
        self.padding = 4

        self.selected_index = 0
        self.timer = Timer(200)
        self.setup()
        
    def setup(self):
        self.selling_options = list(self.player.inventory.item_inventory.keys()) 
        self.buying_options = list(self.player.inventory.seed_inventory.keys())

        self.selling_text_surfaces = list(map(lambda item : self.font.render(item, False, 'Black'), self.selling_options))
        self.buying_text_surfaces = list(map(lambda item :  self.font.render(item + ' seed', False, 'Black'), self.buying_options))

        self.total_height = sum( list( map( lambda text : text.get_height() + self.padding*2, self.buying_text_surfaces + self.selling_text_surfaces)))
        self.total_height += (len(self.selling_text_surfaces + self.buying_text_surfaces) - 1)*self.space

        self.menu_top = SCREEN_HEIGHT/2 - self.total_height/2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height
        )

        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')

    def display_money(self):
        text_surface = self.font.render(f'${self.player.inventory.money}', False, 'Black')
        text_rect = text_surface.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 10))
        self.display_surface.blit(text_surface, text_rect)

    def show_entry(self, text_surface, amount, top, selected):

        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surface.get_height() + self.padding * 2)
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        text_rect = text_surface.get_rect(midleft= (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surface, text_rect)

        amount_surface = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surface.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surface, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            if self.selected_index > len(self.selling_options) - 1:
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 200, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)
            else:
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 200, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)

    def update(self):
        amount_list = list(self.player.inventory.item_inventory.values()) + list(self.player.inventory.seed_inventory.values())
        for text_index, text_surface in enumerate(self.selling_text_surfaces + self.buying_text_surfaces):
            top = self.main_rect.top + text_index*(text_surface.get_height() + self.padding*2 + self.space)
            self.show_entry(top=top, text_surface=text_surface, amount=amount_list[text_index], selected=False)
        self.display_money()