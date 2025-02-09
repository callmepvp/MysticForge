# Main imports
import pygame
import sys
import random
import copy

# Other imports
from constants import *
from player import Player
from utils import draw_tabs, sort_items_by_rarity, get_xp_threshold, calculate_valor
from item import Item, Material

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_NAME)

# Materials & items
#### Upgrade Rocks
rock_1 = Material("Ironheart Scraps", "Common", 5)
rock_2 = Material("Runed Obsidian", "Rare", 5)
rock_3 = Material("Godforge Ingot", "Epic", 5)

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
clicked_item = None

upgrade_popup_open = False
dismantle_popup_open = False
mouse_clicked = False
material_click_counts = {rock_1: 0, rock_2: 0, rock_3: 0}

###### MISC FUNCTIONS

def calculate_dismantle_materials(item):
    material_type = None
    multiplier = 1.0

    # Determine material type based on rarity
    if item.rarity in ["Common", "Rare"]:
        material_type = rock_1  # Ironheart Scraps
    elif item.rarity in ["Epic", "Legendary"]:
        material_type = rock_2  # Runed Obsidian
    elif item.rarity == "Mythic":
        material_type = rock_3  # Godforge Ingot

    material_quantity = int(item.valorValue * multiplier)
    return material_type, material_quantity

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
    global clicked_item, material_click_counts, upgrade_popup_open, dismantle_popup_open
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

            # Clear the forge upgrading screen
            clicked_item = None
            upgrade_popup_open = False
            dismantle_popup_open = False

            # Clear the upgraded materials selection
            material_click_counts = {rock_1: 0, rock_2: 0, rock_3: 0}

        # Handle tab switching (Forge tab)
        if tab_forge_rect.collidepoint(mouse_pos) and player.current_tab != "F":
            player.current_tab = "F"

            # Store every item's original location when switching tabs
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

def handle_item_click(event, forge_inventory):
    global clicked_item, upgrade_popup_open, dismantle_popup_open
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if forge tab
        if player.current_tab == "F":
            for row in range(forge_inventory.rows):
                for col in range(forge_inventory.cols):
                    item = forge_inventory.slots[row][col]
                    if item and item.rect.collidepoint(mouse_pos):
                        if clicked_item != item:  # If a new item is clicked
                            upgrade_popup_open = False  # Turn off the upgrade popup
                            dismantle_popup_open = False
                        clicked_item = item
                        break

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

            # Draw the item name text   
            item_name_text = FONT.render(f"{item.name}", True, BLACK)
            item_name_text_x = item.rect.centerx - item_name_text.get_width() // 2
            item_name_text_y = item.rect.bottom - item_name_text.get_height() - 5  # 5 pixels above the bottom
            screen.blit(item_name_text, (item_name_text_x, item_name_text_y))

###### MAIN CYCLE
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle events
        dragged_item, dragged_item_original_slot = handle_drag_and_drop(event, dragged_item, dragged_item_original_slot)

        handle_item_button_click(event)

        hovered_item = handle_item_hover(pygame.mouse.get_pos())
        handle_item_click(event, forge_inventory) # Must use a global variable for it to not be updated every tick

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
        info_box_width = INFO_BOX_WIDTH
        info_box_height = INFO_BOX_HEIGHT
        margin = INFO_BOX_MARGIN

        info_box_x = SCREEN_WIDTH - info_box_width - margin  # Align to right edge
        info_box_y = INFO_BOX_Y
        background_rect = pygame.Rect(info_box_x, info_box_y, info_box_width, info_box_height)
        pygame.draw.rect(screen, LIGHT_GRAY, background_rect)  # Background for info box

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
        info_box_width = INFO_BOX_WIDTH
        info_box_height = INFO_BOX_HEIGHT
        margin = INFO_BOX_MARGIN

        info_box_x = SCREEN_WIDTH - info_box_width - margin  # Align to right edge
        info_box_y = INFO_BOX_Y  # Keep the same Y position
        background_rect = pygame.Rect(info_box_x, info_box_y, info_box_width, info_box_height)
        pygame.draw.rect(screen, LIGHT_GRAY, background_rect)  # Background for info box
        draw_forge_inventory(screen, forge_inventory)

    # Draw dragged item
    if dragged_item and dragged_item.dragging:
        pygame.draw.rect(screen, dragged_item.color, dragged_item.rect)
        text = FONT.render(dragged_item.name, True, BLACK)
        screen.blit(text, (dragged_item.rect.x + 10, dragged_item.rect.y + SLOT_SIZE - 20))
    
    ###### HANDLE EVENTS FOR HOVERED AND CLICKED ITEMS
    if hovered_item:
        info_box_width = INFO_BOX_WIDTH
        info_box_height = INFO_BOX_HEIGHT
        margin = INFO_BOX_MARGIN

        info_box_x = SCREEN_WIDTH - info_box_width - margin  # Align to right edge
        info_box_y = INFO_BOX_Y  # Keep the same Y position

        info_box_rect = pygame.Rect(info_box_x, info_box_y, info_box_width, info_box_height)
        pygame.draw.rect(screen, LIGHTER_GRAY, info_box_rect)  # Info box background
        pygame.draw.rect(screen, BLACK, info_box_rect, 2)  # Border of info box

        # Display item info
        item_name_text = INFO_FONT.render(f"Name: {hovered_item.name} (+{hovered_item.valorValue:.2f})", True, BLACK)
        item_type_text = INFO_FONT.render(f"Type: {hovered_item.type}", True, BLACK)
        item_level_text = INFO_FONT.render(f"Level: {hovered_item.level}", True, BLACK)
        item_rarity_text = INFO_FONT.render(f"Rarity: {hovered_item.rarity}", True, BLACK)
        item_quality_text = INFO_FONT.render(f"Quality: {hovered_item.quality}", True, BLACK)

        screen.blit(item_name_text, (info_box_x + 10, info_box_y + 10))
        screen.blit(item_type_text, (info_box_x + 10, info_box_y + 40))
        screen.blit(item_level_text, (info_box_x + 10, info_box_y + 70))
        screen.blit(item_rarity_text, (info_box_x + 10, info_box_y + 100))
        screen.blit(item_quality_text, (info_box_x + 10, info_box_y + 130))

    if clicked_item:
        # Draw the item name text at the top center
        item_name_text = FONT.render(f"{clicked_item.name}", True, BLACK)
        item_name_text_rect = item_name_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(item_name_text, item_name_text_rect)

        rect_width = 200
        rect_height = 30  # Set the height of the rectangle
        rect_x = (SCREEN_WIDTH - rect_width) // 2  # Center the rectangle
        rect_y = item_name_text_rect.bottom + 5  # Place it below the text
        
        upgrade_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        if upgrade_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, LIGHTER_GRAY, upgrade_rect)  # Lighten the rectangle on hover
        else:
            pygame.draw.rect(screen, LIGHT_GRAY, upgrade_rect)  

        upgrade_level_text = FONT.render("Upgrade Level", True, BLACK)
        upgrade_level_text_rect = upgrade_level_text.get_rect(center=(rect_x + rect_width // 2, rect_y + rect_height // 2))
        screen.blit(upgrade_level_text, upgrade_level_text_rect)

        scrap_rect_y = rect_y + rect_height + 5  # Place below the first rectangle
        scrap_rect = pygame.Rect(rect_x, scrap_rect_y, rect_width, rect_height)

        if scrap_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, LIGHTER_GRAY, scrap_rect)  # Lighten the rectangle on hover
        else:
            pygame.draw.rect(screen, LIGHT_GRAY, scrap_rect)  # Default color for the rectangle

        scrap_text = FONT.render("Dismantle", True, BLACK)
        scrap_text_rect = scrap_text.get_rect(center=(rect_x + rect_width // 2, scrap_rect_y + rect_height // 2))
        screen.blit(scrap_text, scrap_text_rect)

        # Handle button clicks
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()

            # Clicking the Upgrade button
            if pygame.Rect(rect_x, rect_y, rect_width, rect_height).collidepoint(mouse_pos):
                if not mouse_clicked:
                    upgrade_popup_open = not upgrade_popup_open
                    dismantle_popup_open = False  # Close dismantle popup if open
                    mouse_clicked = True  

            # Clicking the Scrap button (Dismantle)
            elif scrap_rect.collidepoint(mouse_pos):
                if not mouse_clicked:
                    dismantle_popup_open = not dismantle_popup_open
                    upgrade_popup_open = False  # Close upgrade popup if open
                    mouse_clicked = True  

        if not pygame.mouse.get_pressed()[0]:  # Reset mouse click flag when released
            mouse_clicked = False

        # Handle menu interactions
        if upgrade_popup_open:
            # Create the upgrade rectangle that pops up below the "Upgrade Level"
            upgrade_rect_width = 250  # Slightly bigger width
            upgrade_rect_height = 120  # Taller height for the upgrade pop-up
            upgrade_rect_x = (SCREEN_WIDTH - upgrade_rect_width) // 2
            upgrade_rect_y = scrap_rect_y + rect_height + 50

            # Draw the upgrade rectangle
            pygame.draw.rect(screen, LIGHT_GRAY, (upgrade_rect_x, upgrade_rect_y, upgrade_rect_width, upgrade_rect_height))
            pygame.draw.rect(screen, BLACK, (upgrade_rect_x, upgrade_rect_y, upgrade_rect_width, upgrade_rect_height), 2)

            # Draw the upgrade contents
            current_text = FONT.render("Current", True, BLACK)
            current_text_x = upgrade_rect_x + 10  # Slight padding from the left
            current_text_y = upgrade_rect_y + 10  # Slight padding from the top
            screen.blit(current_text, (current_text_x, current_text_y))

            # Draw "New" text on the right side of the upgrade rectangle
            new_text = FONT.render("New", True, BLACK)
            new_text_x = upgrade_rect_x + upgrade_rect_width - new_text.get_width() - 10  # Slight padding from the right
            new_text_y = upgrade_rect_y + 10  # Same vertical alignment as "Current"
            screen.blit(new_text, (new_text_x, new_text_y))

            # Now add the upgrade material squares to the left of the rectangle
            material_square_size = 30  # Size of each small material square
            material_square_margin = 3  # Margin between squares

            material_x = upgrade_rect_x - material_square_size - material_square_margin  # Position it just to the left of the upgrade rectangle
            material_y = upgrade_rect_y + (upgrade_rect_height // 2) - (material_square_size * 3) // 2  # Center them vertically

            # Create the material squares
            no_materials = True
            for row in range(materials_inventory.rows):
                for col in range(materials_inventory.cols):
                    material = materials_inventory.slots[row][col] 

                    if material:
                        # Get the position of each material square in the upgrade popup
                        material_rect = pygame.Rect(material_x, material_y + (col * (material_square_size + material_square_margin))-1.5, material_square_size, material_square_size)

                        # Draw material square and border
                        pygame.draw.rect(screen, material.color, material_rect)
                        pygame.draw.rect(screen, BLACK, material_rect, 2)  # Border for the material square

                        # Show the quantity inside the square
                        quantity_text = FONT.render(f"{material.quantity}", True, BLACK)
                        text_x = material_rect.centerx - quantity_text.get_width() // 2
                        text_y = material_rect.centery - quantity_text.get_height() // 2

                        # Blit the quantity text at the calculated position
                        screen.blit(quantity_text, (text_x, text_y))

                        # Handle material upgrade clicks
                        if material.quantity - material_click_counts[material] - 1 >= 0 and material_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                            if not mouse_clicked:  # Prevent multiple clicks in one frame
                                material_click_counts[material] += 1
                                mouse_clicked = True
                                no_materials = False # We have at least one material

            if not pygame.mouse.get_pressed()[0]:
                mouse_clicked = False

            # Calculate the total XP for the upgrades
            total_xp = 0
            for material, clicks in material_click_counts.items():
                if material == rock_1:
                    total_xp += clicks * 10
                elif material == rock_2:
                    total_xp += clicks * 50
                elif material == rock_3:
                    total_xp += clicks * 100
        
            # Calculate new level and XP
            current_level = clicked_item.level
            current_xp = clicked_item.xp
            new_xp = current_xp + total_xp
            new_level = current_level

            while new_level < MAX_ITEM_LEVEL:
                xp_threshold = get_xp_threshold(new_level)
                if new_xp >= xp_threshold:
                    new_xp -= xp_threshold
                    new_level += 1
                else:
                    break

            # Create a dummy item to calculate the new Valor
            dummy_item = copy.deepcopy(clicked_item)  # Copy the clicked item
            dummy_item.level = new_level  # Update the dummy item's level
            dummy_item.xp = new_xp  # Update the dummy item's XP

            # Calculate current and new Valor
            current_valor = clicked_item.valorValue
            new_valor = calculate_valor(dummy_item)

            # Draw the current level and XP on the left side
            current_level_text = FONT.render(f"Level {current_level}", True, BLACK)
            current_level_text_x = upgrade_rect_x + 10  # Left-aligned
            current_level_text_y = upgrade_rect_y + upgrade_rect_height - 70
            screen.blit(current_level_text, (current_level_text_x, current_level_text_y))

            current_xp_text = FONT.render(f"+{current_xp} XP", True, BLACK)
            current_xp_text_x = upgrade_rect_x + 10  # Left-aligned
            current_xp_text_y = upgrade_rect_y + upgrade_rect_height - 50
            screen.blit(current_xp_text, (current_xp_text_x, current_xp_text_y))

            current_valor_text = FONT.render(f"Valor: {current_valor:.2f}", True, BLACK)
            current_valor_text_x = upgrade_rect_x + 10  # Left-aligned
            current_valor_text_y = upgrade_rect_y + upgrade_rect_height - 30  # Place below the XP text
            screen.blit(current_valor_text, (current_valor_text_x, current_valor_text_y))

            # Draw the preview of the new level and XP on the right side
            preview_level_text = FONT.render(f"Level {new_level}", True, BLACK)
            preview_level_text_x = upgrade_rect_x + upgrade_rect_width - preview_level_text.get_width() - 10  # Right-aligned
            preview_level_text_y = upgrade_rect_y + upgrade_rect_height - 70  # Place above the XP text
            screen.blit(preview_level_text, (preview_level_text_x, preview_level_text_y))

            preview_xp_text = FONT.render(f"+{new_xp} XP", True, BLACK)
            preview_xp_text_x = upgrade_rect_x + upgrade_rect_width - preview_xp_text.get_width() - 10  # Right-aligned
            preview_xp_text_y = upgrade_rect_y + upgrade_rect_height - 50  # Place below the level text
            screen.blit(preview_xp_text, (preview_xp_text_x, preview_xp_text_y))

            preview_valor_text = FONT.render(f"Valor: {new_valor:.2f}", True, BLACK)
            preview_valor_text_x = upgrade_rect_x + upgrade_rect_width - preview_valor_text.get_width() - 10  # Right-aligned
            preview_valor_text_y = upgrade_rect_y + upgrade_rect_height - 30  # Place below the XP text
            screen.blit(preview_valor_text, (preview_valor_text_x, preview_valor_text_y))

            # Confirm Upgrade Button
            confirm_button_width = 150
            confirm_button_height = 40
            confirm_button_x = (SCREEN_WIDTH - confirm_button_width) // 2
            confirm_button_y = upgrade_rect_y + upgrade_rect_height + 10
            confirm_button_rect = pygame.Rect(confirm_button_x, confirm_button_y, confirm_button_width, confirm_button_height)

            # Hover effect
            button_color = GRAY if confirm_button_rect.collidepoint(pygame.mouse.get_pos()) else DARK_GRAY
            pygame.draw.rect(screen, button_color, confirm_button_rect)

            # Center text inside button
            confirm_text = FONT.render("Confirm", True, WHITE)
            confirm_text_x = confirm_button_x + (confirm_button_width - confirm_text.get_width()) // 2
            confirm_text_y = confirm_button_y + (confirm_button_height - confirm_text.get_height()) // 2
            screen.blit(confirm_text, (confirm_text_x, confirm_text_y))

            # Handle confirm upgrade click
            if confirm_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                if not mouse_clicked:  # Prevent multiple clicks
                    if total_xp > 0:
                        # Apply the upgrade
                        clicked_item.level = new_level
                        clicked_item.xp = new_xp
                        clicked_item.valorValue = new_valor  # Update valor

                        # Deduct used materials
                        for material, clicks in material_click_counts.items():
                            if clicks > 0 and material.quantity >= clicks:
                                material.quantity -= clicks

                        # Reset material click counts
                        material_click_counts = {rock_1: 0, rock_2: 0, rock_3: 0}
                    mouse_clicked = True

            if not pygame.mouse.get_pressed()[0]:
                mouse_clicked = False    
        if not upgrade_popup_open:
            material_click_counts = {rock_1: 0, rock_2: 0, rock_3: 0}

        if dismantle_popup_open:
            # Create the dismantle pop-up rectangle
            dismantle_rect_width = 250
            dismantle_rect_height = 120
            dismantle_rect_x = (SCREEN_WIDTH - dismantle_rect_width) // 2
            dismantle_rect_y = scrap_rect_y + rect_height + 50

            # Draw the dismantle pop-up background and border
            pygame.draw.rect(screen, LIGHT_GRAY, (dismantle_rect_x, dismantle_rect_y, dismantle_rect_width, dismantle_rect_height))
            pygame.draw.rect(screen, BLACK, (dismantle_rect_x, dismantle_rect_y, dismantle_rect_width, dismantle_rect_height), 2)

            # Calculate materials from dismantling
            material_type, material_quantity = calculate_dismantle_materials(clicked_item)

            # Display the materials the player will receive
            materials_text = FONT.render(f"You will receive:", True, BLACK)
            materials_text_x = dismantle_rect_x + (dismantle_rect_width - materials_text.get_width()) // 2  # Center text
            materials_text_y = dismantle_rect_y + 10
            screen.blit(materials_text, (materials_text_x, materials_text_y))

            material_text = FONT.render(f"{material_quantity} x {material_type.name}", True, BLACK)
            material_text_x = dismantle_rect_x + (dismantle_rect_width - material_text.get_width()) // 2  # Center text
            material_text_y = materials_text_y + 30
            screen.blit(material_text, (material_text_x, material_text_y))

            # Draw the material icon
            material_icon_rect = pygame.Rect(material_text_x + material_text.get_width() + 10, material_text_y, 30, 30)
            pygame.draw.rect(screen, material_type.color, material_icon_rect)
            pygame.draw.rect(screen, BLACK, material_icon_rect, 2)

            # Confirm Dismantle Button
            confirm_button_width = 150
            confirm_button_height = 40
            confirm_button_x = (SCREEN_WIDTH - confirm_button_width) // 2  # Center button horizontally
            confirm_button_y = dismantle_rect_y + dismantle_rect_height + 10  # Place below the dismantle UI
            confirm_button_rect = pygame.Rect(confirm_button_x, confirm_button_y, confirm_button_width, confirm_button_height)

            # Hover effect
            button_color = GRAY if confirm_button_rect.collidepoint(pygame.mouse.get_pos()) else DARK_GRAY
            pygame.draw.rect(screen, button_color, confirm_button_rect)

            # Center text inside button
            confirm_text = FONT.render("Confirm", True, WHITE)
            confirm_text_x = confirm_button_x + (confirm_button_width - confirm_text.get_width()) // 2
            confirm_text_y = confirm_button_y + (confirm_button_height - confirm_text.get_height()) // 2
            screen.blit(confirm_text, (confirm_text_x, confirm_text_y))

            # Handle button clicks
            if pygame.mouse.get_pressed()[0]:
                if not mouse_clicked:  # Prevent multiple clicks in one frame
                    mouse_pos = pygame.mouse.get_pos()

                    # Confirm dismantle
                    if confirm_button_rect.collidepoint(mouse_pos):
                        # Add materials to the player's inventory
                        material_type.quantity += material_quantity

                        # Remove the dismantled item from the inventory and forge inventory
                        for row in range(inventory.rows):
                            for col in range(inventory.cols):
                                if inventory.slots[row][col] == clicked_item:
                                    inventory.slots[row][col] = None
                                    break

                        for row in range(forge_inventory.rows):
                            for col in range(forge_inventory.cols):
                                if forge_inventory.slots[row][col] == clicked_item:
                                    forge_inventory.slots[row][col] = None
                                    break

                        # Close the dismantle pop-up
                        dismantle_popup_open = False
                        clicked_item = None # Reset the clicked item as it does not exist anymore

                    mouse_clicked = True

            # Reset mouse_clicked when the mouse button is released
            if not pygame.mouse.get_pressed()[0]:
                mouse_clicked = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()