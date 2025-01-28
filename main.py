# Main imports
import pygame
import sys
import random
import uuid 
import copy

# Other imports
from constants import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mystic Forge")

def draw_tabs(surface):
    # Draw "I" tab
    tab_i_rect = pygame.Rect(TAB_X, TAB_Y, TAB_SIZE, TAB_SIZE)
    pygame.draw.rect(surface, GRAY, tab_i_rect)
    pygame.draw.rect(surface, BLACK, tab_i_rect, 2)  # Border
    tab_i_text = FONT.render("I", True, BLACK)
    surface.blit(tab_i_text, (TAB_X + TAB_SIZE // 4, TAB_Y + TAB_SIZE // 4))

    # Draw "F" tab
    tab_f_rect = pygame.Rect(TAB_X, TAB_Y + TAB_SIZE + TAB_MARGIN, TAB_SIZE, TAB_SIZE)
    pygame.draw.rect(surface, GRAY, tab_f_rect)
    pygame.draw.rect(surface, BLACK, tab_f_rect, 2)  # Border
    tab_f_text = FONT.render("F", True, BLACK)
    surface.blit(tab_f_text, (TAB_X + TAB_SIZE // 4, TAB_Y + TAB_SIZE + TAB_MARGIN + TAB_SIZE // 4))

# Rarity and Quality Multipliers
RARITY_MULTIPLIERS = {
    "Common": 1,
    "Rare": 2,
    "Epic": 3,
    "Legendary": 4,
    "Mythic": 5
}

QUALITY_MULTIPLIERS = {
    "Poor": 1,
    "Bad": 1.5,
    "Average": 2,
    "Good": 3,
    "Excellent": 5
}

# Function to calculate valor for an item
def calculate_valor(item):
    # Base value is used to normalize the calculation (e.g., 10)
    base_value = 10
    
    # Get multipliers for rarity and quality
    rarity_multiplier = RARITY_MULTIPLIERS.get(item.rarity, 1)
    quality_multiplier = QUALITY_MULTIPLIERS.get(item.quality, 1)
    
    # Formula: valor = (rarity_multiplier * quality_multiplier * item.level) / base_value
    valor = (rarity_multiplier * quality_multiplier * item.level) / base_value
    item.valorValue = valor
    
    return valor

# Player class
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

# Item class
class Item:
    def __init__(self, name, color, level=1, rarity="Common", quality="Poor"):
        self.name = name
        self.color = color
        self.level = level
        self.rarity = rarity
        self.quality = quality
        self.valorValue = 0
        self.uid = str(uuid.uuid4()) # Generate a random unique ID for each item instance

        self.rect = pygame.Rect(0, 0, SLOT_SIZE - 10, SLOT_SIZE - 10)  # Smaller than the slot
        self.dragging = False  # Whether the item is being dragged
    
    def upgrade(self):
        self.level += 1

# Material class (for material items)
class Material:
    def __init__(self, name, rarity, quantity=0):
        self.name = name
        self.rarity = rarity
        self.quantity = quantity
        self.color = self.set_color()

    def set_color(self):
        if self.rarity == "Common":
            return (150, 150, 150)  # Gray for common materials
        elif self.rarity == "Uncommon":
            return (100, 200, 100)  # Green for uncommon materials
        elif self.rarity == "Rare":
            return (50, 100, 200)  # Blue for rare materials
        return (255, 255, 255)  # Default white for others

# Inventory class
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
    
# Material item definitions
## Upgrade Rocks
rock_1 = Material("Stone", "Common")
rock_2 = Material("Iron", "Uncommon")
rock_3 = Material("Diamond", "Rare")

materials = [rock_1, rock_2, rock_3]

# Available items
available_items = [
    Item("Sword", RED, rarity="Common", quality="Poor"),
    Item("Shield", BLUE, rarity="Rare", quality="Good"),
    Item("Bow", BLUE, rarity="Uncommon", quality="Average"),
    Item("Potion", RED, rarity="Common", quality="Bad"),
    Item("Helmet", BLUE, rarity="Legendary", quality="Excellent")
]

# Create inventories
inventory = Inventory(INVENTORY_ROWS, INVENTORY_COLS)
materials_inventory = GridInventory(MATERIALS_ROWS, MATERIALS_COLS)
materials_inventory.fill_with_materials(materials)

# Instantiate the Player
player = Player()

# Main game loop
clock = pygame.time.Clock()
running = True
dragged_item = None
dragged_item_original_slot = None  # Track the original slot of the dragged item
hovered_item = None

# Define the "Item" button
button_rect = pygame.Rect(INVENTORY_X + (SLOT_SIZE + SLOT_MARGIN) * 2, BUTTON_Y, 100, 40)  # Define button rect
button_text = FONT.render("Item", True, BLACK)  # Define button text

# Main cycle
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse down event for dragging items
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for row in range(INVENTORY_ROWS):
                for col in range(INVENTORY_COLS):
                    item = inventory.slots[row][col]
                    if item and item.rect.collidepoint(mouse_pos):
                        dragged_item = item
                        dragged_item_original_slot = (row, col)  # Store the original slot
                        inventory.remove_item(row, col)
                        item.dragging = True

        # Mouse up event for dropping items
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged_item:
                mouse_pos = pygame.mouse.get_pos()
                dropped = False
                for row in range(INVENTORY_ROWS):
                    for col in range(INVENTORY_COLS):
                        x = INVENTORY_X + col * (SLOT_SIZE + SLOT_MARGIN)
                        y = INVENTORY_Y + row * (SLOT_SIZE + SLOT_MARGIN)
                        slot_rect = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)

                        if slot_rect.collidepoint(mouse_pos):
                            existing_item = inventory.slots[row][col]

                            # If another item exists, swap positions
                            if existing_item:
                                inventory.slots[dragged_item_original_slot[0]][dragged_item_original_slot[1]] = existing_item
                                inventory.slots[row][col] = dragged_item
                            else:
                                # Just place the item in the empty slot
                                inventory.slots[row][col] = dragged_item

                            dropped = True
                            break

                # If the item wasn't dropped in the inventory, revert to its original position
                if not dropped and dragged_item_original_slot:
                    row, col = dragged_item_original_slot
                    inventory.add_item(dragged_item, row, col)

                dragged_item.dragging = False
                dragged_item = None
                dragged_item_original_slot = None  # Reset the original slot
                hovered_item = None

        # Detect hovering over an item
        mouse_pos = pygame.mouse.get_pos()
        hovered_item = None
        if not dragged_item:
            for row in range(INVENTORY_ROWS):
                for col in range(INVENTORY_COLS):
                    item = inventory.slots[row][col]
                    if item and item.rect.collidepoint(mouse_pos):
                        hovered_item = item
                        break
                if hovered_item:
                    break

        # Check for Item button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect(INVENTORY_X + (SLOT_SIZE + SLOT_MARGIN) * 2, BUTTON_Y, 100, 40)
            if button_rect.collidepoint(mouse_pos):
                # Add a random item to the inventory
                new_item = copy.deepcopy(random.choice(available_items))
                if not inventory.add_item_in_first_empty(new_item):
                    print("No space!")

                player.calculate_valor(inventory)

    # Update dragged item position
    if dragged_item and dragged_item.dragging:
        dragged_item.rect.center = pygame.mouse.get_pos()

    # Draw everything
    screen.fill(WHITE)

    # Draw inventory header
    header_text = HEADER_FONT.render("Inventory", True, BLACK)
    header_text_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, INVENTORY_Y - 50))  # Centered above inventory
    screen.blit(header_text, header_text_rect)

    # Draw the coins and valor count
    coins_text = FONT.render(f"Coins: {player.coins}", True, BLACK)
    valor_text = FONT.render(f"Valor: {round(player.valor, 3)}", True, BLACK)

    screen.blit(coins_text, (INVENTORY_X, INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 10))
    screen.blit(valor_text, (INVENTORY_X, INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 40))

    # Draw inventories
    inventory.draw(screen)
    materials_inventory.draw(screen)

    # Draw dragged item
    if dragged_item and dragged_item.dragging:
        pygame.draw.rect(screen, dragged_item.color, dragged_item.rect)
        text = FONT.render(dragged_item.name, True, BLACK)
        screen.blit(text, (dragged_item.rect.x + 10, dragged_item.rect.y + SLOT_SIZE - 20))

    # Display info box if hovering over an item
    if hovered_item:
        info_box_rect = pygame.Rect(INFO_BOX_X, INFO_BOX_Y, 200, 160)
        pygame.draw.rect(screen, INFO_BOX_COLOR, info_box_rect)  # Info box background
        pygame.draw.rect(screen, BLACK, info_box_rect, 2)  # Border of info box

        # Display item info
        item_name_text = INFO_FONT.render(f"Name: {hovered_item.name} (+{hovered_item.valorValue:.2f})", True, BLACK)
        item_level_text = INFO_FONT.render(f"Level: {hovered_item.level}", True, BLACK)
        item_rarity_text = INFO_FONT.render(f"Rarity: {hovered_item.rarity}", True, BLACK)
        item_quality_text = INFO_FONT.render(f"Quality: {hovered_item.quality}", True, BLACK)

        screen.blit(item_name_text, (INFO_BOX_X + 10, INFO_BOX_Y + 10))
        screen.blit(item_level_text, (INFO_BOX_X + 10, INFO_BOX_Y + 40))
        screen.blit(item_rarity_text, (INFO_BOX_X + 10, INFO_BOX_Y + 70))
        screen.blit(item_quality_text, (INFO_BOX_X + 10, INFO_BOX_Y + 100))

    # Item button
    pygame.draw.rect(screen, BLUE, button_rect)  # Draw the button
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))  # Center text

    # Material inventory label
    material_label_text = FONT.render("Materials", True, BLACK)
    screen.blit(material_label_text, (MATERIALS_X, MATERIALS_Y - 25))

    draw_tabs(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()