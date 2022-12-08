import pygame
from settings import *
from menu import Menu

class Merchant(Menu):
    def __init__(self, player, toggle_menu) -> None:
        super().__init__(player)
        self.toggle_menu = toggle_menu

    def update(self):
        self.input()
        amount_list = list(self.player.inventory.item_inventory.values()) + list(self.player.inventory.seed_inventory.values())
        for text_index, text_surface in enumerate(self.selling_text_surfaces + self.buying_text_surfaces):
            top = self.main_rect.top + text_index*(text_surface.get_height() + self.padding*2 + self.space)
            self.show_entry(top=top, text_surface=text_surface, amount=amount_list[text_index], selected=text_index == self.selected_index)
        self.display_money()

    def input(self):
        pressed_keys = pygame.key.get_pressed()
        self.timer.update()

        if pressed_keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if pressed_keys[pygame.K_UP] and self.selected_index > 0:
                self.selected_index -= 1
                self.timer.activate()

            if pressed_keys[pygame.K_DOWN] and self.selected_index < len(self.buying_options + self.selling_options) - 1:
                self.selected_index += 1
                self.timer.activate()

            if pressed_keys[pygame.K_SPACE]:
                self.timer.activate()
                if self.selected_index < len(self.selling_options):
                    item = self.selling_options[self.selected_index]
                    if self.player.inventory.item_inventory[item] > 0:
                        self.player.inventory.item_inventory[item] -= 1
                        self.player.inventory.money += SALE_PRICES[item]
                else:
                    item = self.buying_options[self.selected_index % len(self.selling_options)]
                    seed_price = PURCHASE_PRICES[item]
                    if self.player.inventory.money >= seed_price:
                        self.player.inventory.seed_inventory[item] += 1
                        self.player.inventory.money -= seed_price