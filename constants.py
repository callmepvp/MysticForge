# Main imports
import pygame

# Game settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GAME_NAME = "Mystic Forge"

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (237, 100, 100)

INFO_BOX_COLOR = (240, 240, 240)

# Fonts
pygame.init()
FONT = pygame.font.Font(None, 24)
HEADER_FONT = pygame.font.Font(None, 48)
INFO_FONT = pygame.font.Font(None, 20)

# Slot settings
SLOT_SIZE = 80
WIDER_SLOT_SIZE = SLOT_SIZE * 2
SLOT_MARGIN = 10

INVENTORY_ROWS = 2
INVENTORY_COLS = 5
MATERIALS_ROWS = 1
MATERIALS_COLS = 3

# Inventory settings
INVENTORY_X = 100
INVENTORY_Y = 150
INFO_BOX_X = INVENTORY_X + (INVENTORY_COLS * (SLOT_SIZE + SLOT_MARGIN)) + 30
INFO_BOX_Y = INVENTORY_Y

# Material inventory settings
MATERIALS_X = INVENTORY_X
MATERIALS_Y = INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 180

# Tab settings
TAB_SIZE = 40
TAB_MARGIN = 10
TAB_X = SCREEN_WIDTH - TAB_SIZE - TAB_MARGIN
TAB_Y = TAB_MARGIN

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

# Testing settings (might change)
BUTTON_Y = INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 30