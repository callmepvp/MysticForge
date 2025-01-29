# Main imports
import pygame

# Game settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
GAME_NAME = "Mystic Forge"
RESIZE_FACTOR = 1.2

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
LIGHTER_GRAY = (240, 240, 240) 
DARK_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
RED = (237, 100, 100)

# Fonts
pygame.init()
FONT = pygame.font.Font(None, 24)
HEADER_FONT = pygame.font.Font(None, 48)
INFO_FONT = pygame.font.Font(None, 20)

# Slot settings
SLOT_SIZE = int(80 * RESIZE_FACTOR)
WIDER_SLOT_SIZE = int(SLOT_SIZE * 2 * RESIZE_FACTOR)
SLOT_MARGIN = int(10*RESIZE_FACTOR)

INVENTORY_ROWS = 2
INVENTORY_COLS = 5
MATERIALS_ROWS = 1
MATERIALS_COLS = 3

# Inventory settings
INVENTORY_X = 100
INVENTORY_Y = 150
INFO_BOX_X = INVENTORY_X + (INVENTORY_COLS * (SLOT_SIZE + SLOT_MARGIN)) + 30
INFO_BOX_Y = INVENTORY_Y

INFO_BOX_WIDTH = int(200*RESIZE_FACTOR)
INFO_BOX_HEIGHT = int(160*RESIZE_FACTOR)
INFO_BOX_MARGIN = int(20*RESIZE_FACTOR)

# Material inventory settings
MATERIALS_X = INVENTORY_X
MATERIALS_Y = INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 180

# Tab settings
TAB_SIZE = int(40*RESIZE_FACTOR)
TAB_MARGIN = int(10*RESIZE_FACTOR)
TAB_X = SCREEN_WIDTH - TAB_SIZE - TAB_MARGIN
TAB_Y = TAB_MARGIN

TAB_COLOR_ACTIVE = (200, 200, 200)
TAB_COLOR_INACTIVE = (150, 150, 150)
TAB_WIDTH, TAB_HEIGHT = 50, 50

# Testing settings (might change)
BUTTON_Y = INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 30

# Rectangles
tab_inventory_rect = pygame.Rect(SCREEN_WIDTH - TAB_WIDTH * 2 - 10, 10, TAB_WIDTH, TAB_HEIGHT)
tab_forge_rect = pygame.Rect(SCREEN_WIDTH - TAB_WIDTH - 5, 10, TAB_WIDTH, TAB_HEIGHT)

button_rect = pygame.Rect(INVENTORY_X + (SLOT_SIZE + SLOT_MARGIN) * 2, BUTTON_Y, 100, 40)  # Define button rect
button_text = FONT.render("Item", True, BLACK)  # Define button text

# Data arrays
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

# Game data
MAX_ITEM_LEVEL = 10