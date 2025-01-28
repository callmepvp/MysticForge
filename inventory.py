# Main imports
import pygame
# Other imports
from constants import *

class Inventory:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.slots = [[None for _ in range(cols)] for _ in range(rows)]

    def draw(self, surface):
        # Draw grid slots
        for row in range(self.rows):
            for col in range(self.cols):
                x = INVENTORY_X + col * (SLOT_SIZE + SLOT_MARGIN)
                y = INVENTORY_Y + row * (SLOT_SIZE + SLOT_MARGIN)
                pygame.draw.rect(surface, GRAY, (x, y, SLOT_SIZE, SLOT_SIZE))
                pygame.draw.rect(surface, BLACK, (x, y, SLOT_SIZE, SLOT_SIZE), 2)  # Border

                # Draw item if present
                item = self.slots[row][col]
                if item:
                    item.rect.topleft = (x + 5, y + 5)
                    pygame.draw.rect(surface, item.color, item.rect)
                    text = FONT.render(item.name, True, BLACK)
                    surface.blit(text, (x + 10, y + SLOT_SIZE - 20))

    def add_item(self, item, row, col):
        if self.slots[row][col] is None:
            self.slots[row][col] = item
            return True
        return False
    
    def add_item_in_first_empty(self, item):
        # Find the first available slot
        for row in range(self.rows):
            for col in range(self.cols):
                if self.slots[row][col] is None:
                    self.slots[row][col] = item
                    return True
        return False  # No space available

    def remove_item(self, row, col):
        self.slots[row][col] = None

# Grid Inventory class for Materials
class GridInventory:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.slots = [[None for _ in range(cols)] for _ in range(rows)]

    def draw(self, surface):
        # Draw grid slots for materials
        for row in range(self.rows):
            for col in range(self.cols):
                x = MATERIALS_X + col * (WIDER_SLOT_SIZE + SLOT_MARGIN)
                y = MATERIALS_Y + row * (SLOT_SIZE + SLOT_MARGIN)
                pygame.draw.rect(surface, GRAY, (x, y, WIDER_SLOT_SIZE, SLOT_SIZE))
                pygame.draw.rect(surface, BLACK, (x, y, WIDER_SLOT_SIZE, SLOT_SIZE), 2)  # Border

                # Draw material if present
                material = self.slots[row][col]
                if material:
                    pygame.draw.rect(surface, material.color, (x + 5, y + 5, WIDER_SLOT_SIZE - 10, SLOT_SIZE - 10))
                    text = FONT.render(f"{material.name}", True, BLACK)
                    surface.blit(text, (x + 10, y + SLOT_SIZE - 20))  # Shorten name for display

                    # Show the quantity of materials
                    quantity_text = FONT.render(f"{material.quantity}", True, BLACK)
                    surface.blit(quantity_text, (x + WIDER_SLOT_SIZE - 25, y + SLOT_SIZE - 20))  # Show quantity at the bottom-right

    def add_material(self, material, row, col):
        if self.slots[row][col] is None:
            self.slots[row][col] = material
            return True
        return False
    
    def fill_with_materials(self, materials):
        """
        Fill the grid's slots with a list of material items.
        Assumes the list of materials is of size <= grid slots.
        """
        index = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if index < len(materials):
                    self.slots[row][col] = materials[index]
                    index += 1

class ForgeInventory:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.slots = [[None for _ in range(cols)] for _ in range(rows)]  # 2x5 grid

    def add_item_in_first_empty(self, item):
        # Try to place the item in the first empty slot in the inventory
        for row in range(self.rows):
            for col in range(self.cols):
                if self.slots[row][col] is None:  # Empty slot
                    self.slots[row][col] = item
                    return True  # Successfully added
        return False  # Inventory is full