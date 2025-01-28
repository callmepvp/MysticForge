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