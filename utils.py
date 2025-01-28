# Main imports
# Other imports
from constants import *

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

def draw_tabs(screen, player):
    # Draw tabs with active highlighting
    pygame.draw.rect(screen, TAB_COLOR_ACTIVE if player.current_tab == "I" else TAB_COLOR_INACTIVE, tab_inventory_rect)
    pygame.draw.rect(screen, TAB_COLOR_ACTIVE if player.current_tab == "F" else TAB_COLOR_INACTIVE, tab_forge_rect)

    # Draw "I" and "F" text
    font = pygame.font.Font(None, 36)
    tab_i_text = font.render("I", True, BLACK)
    tab_f_text = font.render("F", True, BLACK)
    screen.blit(tab_i_text, (tab_inventory_rect.centerx - tab_i_text.get_width() // 2, tab_inventory_rect.centery - tab_i_text.get_height() // 2))
    screen.blit(tab_f_text, (tab_forge_rect.centerx - tab_f_text.get_width() // 2, tab_forge_rect.centery - tab_f_text.get_height() // 2))

def sort_items_by_rarity(items):
    rarity_order = ["Mythic", "Legendary", "Epic", "Rare", "Common"]
    return sorted(items, key=lambda item: rarity_order.index(item.rarity))