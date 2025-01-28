# Main imports
import pygame
import sys
import random
import copy

# Other imports
from constants import *
from player import Player
from utils import draw_tabs
from item import Item, Material
from inventory import Inventory, GridInventory

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_NAME)
    
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