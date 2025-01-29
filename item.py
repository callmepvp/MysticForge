# Main imports
import pygame
import uuid
# Other imports
from constants import *

class Item:
    def __init__(self, name, color, level=1, rarity="Common", quality="Poor"):
        self.name = name
        self.color = color
        self.level = level
        self.rarity = rarity
        self.quality = quality
        self.valorValue = 0
        self.xp = 0
        self.uid = str(uuid.uuid4()) # Generate a random unique ID for each item instance

        self.rect = pygame.Rect(0, 0, SLOT_SIZE - 10, SLOT_SIZE - 10)  # Smaller than the slot
        self.dragging = False  # Whether the item is being dragged
    
    def upgrade(self):
        self.level += 1

class Material:
    def __init__(self, name, rarity, quantity=0):
        self.name = name
        self.rarity = rarity
        self.quantity = quantity
        self.color = self.set_color()

    def set_color(self):
        if self.rarity == "Common":
            return DARK_GRAY
        elif self.rarity == "Rare":
            return GREEN
        elif self.rarity == "Epic":
            return BLUE
        return (255, 255, 255)  # Default white for others