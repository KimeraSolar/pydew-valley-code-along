class Inventory():
    def __init__(self) -> None:
        self.item_inventory = {
            'wood' : 0,
            'apple' : 0,
            'corn' : 0,
            'tomato' : 0,
        }

        self.seed_inventory = {
            'corn' : 5,
            'tomato' : 5,
        }

        self.money = 200
    
    def display_config(self, menu):
        self.menu = menu
    
    def update(self):
        self.menu.update()