# Main imports
# Other imports
from constants import *
from utils import calculate_valor

class Player:
    def __init__(self):
        self.coins = 0  # Starting coins
        self.valor = 0  # Starting valor

    def update_coins(self, amount):
        self.coins = amount

    def update_valor(self, amount):
        self.valor = amount

    def calculate_valor(self, inventory):
        total_valor = 0
        # Loop through inventory and calculate valor for each item
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                item = inventory.slots[row][col]
                if item:
                    total_valor += calculate_valor(item)  # Add item's valor to total valor

        if not total_valor == self.valor:
            self.update_valor(total_valor)
