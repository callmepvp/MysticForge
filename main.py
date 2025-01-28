# Main imports
import pygame
import sys
import random
import copy

# Other imports
from constants import *
from player import Player
from utils import draw_tabs, sort_items_by_rarity
from item import Item, Material

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_NAME)

# Materials & items
#### Upgrade Rocks
rock_1 = Material("Stone", "Common")
rock_2 = Material("Iron", "Rare")
rock_3 = Material("Diamond", "Epic")

materials = [rock_1, rock_2, rock_3]

#### All Items
available_items = [
    Item("Sword", RED, rarity="Common", quality="Poor"),
    Item("Shield", BLUE, rarity="Rare", quality="Good"),
    Item("Bow", BLUE, rarity="Common", quality="Average"),
    Item("Potion", RED, rarity="Common", quality="Bad"),
    Item("Helmet", BLUE, rarity="Legendary", quality="Excellent"),
    Item("Chestp", RED, rarity="Mythic", quality="Excellent")
]

# Create inventories and instantiate player
player = Player()
inventory = player.tabs["I"]["inventory"]
materials_inventory = player.tabs["I"]["materials"]
materials_inventory.fill_with_materials(materials)

forge_inventory = player.tabs["F"]["inventory"]

# Main game loop
clock = pygame.time.Clock()
running = True
dragged_item = None
dragged_item_original_slot = None  # Track the original slot of the dragged item
hovered_item = None

###### INVENTORY FUNCTIONS
# Handle dragging and dropping of items in the inventory
def handle_drag_and_drop(event, dragged_item, dragged_item_original_slot):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        if player.current_tab == "I":  # Only handle inventory actions if on the Inventory tab
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
        if dragged_item and player.current_tab == "I":  # Only handle inventory actions if on the Inventory tab
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

    return dragged_item, dragged_item_original_slot

# Handle the item button click to add a random item to the inventory
def handle_item_button_click(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos) and player.current_tab == "I":  # Only add item in Inventory tab
            # Add a random item to the inventory
            new_item = copy.deepcopy(random.choice(available_items))
            if not inventory.add_item_in_first_empty(new_item):
                print("No space!")

            player.calculate_valor(inventory)

# Handle hovering over an item and displaying the info box
def handle_item_hover(mouse_pos):
    hovered_item = None
    if not dragged_item and player.current_tab == "I":
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                item = inventory.slots[row][col]
                if item and item.rect.collidepoint(mouse_pos):
                    hovered_item = item
                    break
            if hovered_item:
                break

    # Hover detection in Forge Inventory (F tab)
    if not dragged_item and player.current_tab == "F":
        for row in range(forge_inventory.rows):
            for col in range(forge_inventory.cols):
                item = forge_inventory.slots[row][col]
                if item and item.rect.collidepoint(mouse_pos):
                    hovered_item = item
                    break
            if hovered_item:
                break

    return hovered_item

# Handle tab switching
def handle_tab_switching(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()

        # Handle tab switching (Inventory tab)
        if tab_inventory_rect.collidepoint(mouse_pos) and player.current_tab != "I":
            player.current_tab = "I"

            # Restore item rects to original inventory positions when switching back to "I"
            for row in range(INVENTORY_ROWS):
                for col in range(INVENTORY_COLS):
                    item = inventory.slots[row][col]
                    if item:
                        item.rect = player.original_rects.get(id(item), None)

            # Clear the forge inventory of all items
            for row in range(forge_inventory.rows):
                for col in range(forge_inventory.cols):
                    forge_inventory.slots[row][col] = None

        # Handle tab switching (Forge tab)
        if tab_forge_rect.collidepoint(mouse_pos) and player.current_tab != "F":
            player.current_tab = "F"

            player_items = []
            for row in range(INVENTORY_ROWS):
                for col in range(INVENTORY_COLS):
                    item = inventory.slots[row][col]  # Fetch each item
                    if item:
                        player_items.append(item)
                        player.original_rects[id(item)] = copy.deepcopy(item.rect)

            # Add items to the Forge Inventory
            for item in player_items:
                if not forge_inventory.add_item_in_first_empty(item):
                    print("Forge inventory is full!")


###### FORGE FUNCTIONS
def draw_forge_inventory(screen, forge_inventory):
    x_offset = 20  # Margin from the left
    y_offset = 50  # Margin from the top

    # Loop through the forge inventory and draw the sorted items
    sorted_items = sort_items_by_rarity([item for row in forge_inventory.slots for item in row if item])

    background_width = (SLOT_SIZE + SLOT_MARGIN) * forge_inventory.cols + SLOT_MARGIN
    background_height = (SLOT_SIZE + SLOT_MARGIN) * forge_inventory.rows + SLOT_MARGIN
    background_rect = pygame.Rect(x_offset - 10, y_offset - 10, background_width, background_height)
    pygame.draw.rect(screen, LIGHT_GRAY, background_rect)

    for idx, item in enumerate(sorted_items):
        row = idx // forge_inventory.cols
        col = idx % forge_inventory.cols
        x = x_offset + col * (SLOT_SIZE + SLOT_MARGIN)
        y = y_offset + row * (SLOT_SIZE + SLOT_MARGIN)

        if item:
            item.rect = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)

            pygame.draw.rect(screen, BLACK, (x, y, SLOT_SIZE, SLOT_SIZE), 2)
            pygame.draw.rect(screen, item.color, (x + 5, y + 5, SLOT_SIZE - 10, SLOT_SIZE - 10))
            text = FONT.render(f"{item.name}", True, BLACK)
            screen.blit(text, (x + 10, y + SLOT_SIZE - 20))

###### MAIN CYCLE
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle dragging, dropping, item button click, hover, and tab switching
        dragged_item, dragged_item_original_slot = handle_drag_and_drop(event, dragged_item, dragged_item_original_slot)
        handle_item_button_click(event)
        hovered_item = handle_item_hover(pygame.mouse.get_pos())
        handle_tab_switching(event)

    # Update dragged item position
    if dragged_item and dragged_item.dragging:
        dragged_item.rect.center = pygame.mouse.get_pos()

    # Draw everything
    screen.fill(WHITE)
    draw_tabs(screen, player)

    # Draw the appropriate tab content
    if player.current_tab == "I":
        # Infobox background
        background_rect = pygame.Rect(INFO_BOX_X - 10, INFO_BOX_Y - 10, 220, 180)
        pygame.draw.rect(screen, LIGHT_GRAY, background_rect)

        # Draw Inventory header
        header_text = HEADER_FONT.render("Inventory", True, BLACK)
        header_text_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, INVENTORY_Y - 50))
        screen.blit(header_text, header_text_rect)

        # Draw the coins and valor count
        coins_text = FONT.render(f"Coins: {player.coins}", True, BLACK)
        valor_text = FONT.render(f"Valor: {round(player.valor, 3)}", True, BLACK)

        screen.blit(coins_text, (INVENTORY_X, INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 10))
        screen.blit(valor_text, (INVENTORY_X, INVENTORY_Y + (INVENTORY_ROWS * (SLOT_SIZE + SLOT_MARGIN)) + 40))

        # Draw inventories
        inventory.draw(screen)
        materials_inventory.draw(screen)

        # Item button
        pygame.draw.rect(screen, BLUE, button_rect)  # Draw the button
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))  # Center text

        # Material inventory label
        material_label_text = FONT.render("Materials", True, BLACK)
        screen.blit(material_label_text, (MATERIALS_X, MATERIALS_Y - 25))
    elif player.current_tab == "F":
        # Infobox background
        background_rect = pygame.Rect(INFO_BOX_X - 10, INFO_BOX_Y - 10, 220, 180)
        pygame.draw.rect(screen, LIGHT_GRAY, background_rect)
        draw_forge_inventory(screen, forge_inventory)

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()