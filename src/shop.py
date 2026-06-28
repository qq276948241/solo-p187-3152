import pygame
from config import *

class Shop:
    def __init__(self):
        self.upgrades = SHOP_UPGRADES.copy()
        self.purchase_counts = {upgrade['stat']: 0 for upgrade in self.upgrades}
    
    def get_upgrade_cost(self, upgrade):
        base_cost = upgrade['base_cost']
        count = self.purchase_counts[upgrade['stat']]
        return int(base_cost * (1 + count * 0.5))
    
    def purchase_upgrade(self, upgrade, player_gold, permanent_upgrades):
        cost = self.get_upgrade_cost(upgrade)
        if player_gold >= cost:
            player_gold -= cost
            self.purchase_counts[upgrade['stat']] += 1
            stat = upgrade['stat']
            value = upgrade['value']
            permanent_upgrades[stat] = permanent_upgrades.get(stat, 0) + value
            return True, player_gold, permanent_upgrades
        return False, player_gold, permanent_upgrades
    
    def draw(self, screen, permanent_gold, permanent_upgrades, selected_index):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        center_x = SCREEN_WIDTH // 2
        start_y = 100
        
        title_text = FONT_TITLE.render("商店 - 永久强化", True, GOLD)
        screen.blit(title_text, (center_x - title_text.get_width() // 2, start_y))
        
        gold_text = FONT_LARGE.render(f"金币: {permanent_gold}", True, YELLOW)
        screen.blit(gold_text, (center_x - gold_text.get_width() // 2, start_y + 50))
        
        item_height = 70
        item_width = 500
        list_start_y = start_y + 120
        
        for i, upgrade in enumerate(self.upgrades):
            item_y = list_start_y + i * item_height
            is_selected = i == selected_index
            
            bg_color = DARK_GRAY if not is_selected else (80, 80, 100)
            pygame.draw.rect(screen, bg_color, (center_x - item_width // 2, item_y, item_width, item_height - 10))
            pygame.draw.rect(screen, GOLD if is_selected else GRAY, 
                            (center_x - item_width // 2, item_y, item_width, item_height - 10), 2)
            
            name_text = FONT_LARGE.render(upgrade['name'], True, WHITE)
            screen.blit(name_text, (center_x - item_width // 2 + 20, item_y + 10))
            
            cost = self.get_upgrade_cost(upgrade)
            cost_color = GREEN if permanent_gold >= cost else RED
            cost_text = FONT.render(f"花费: {cost} 金币", True, cost_color)
            screen.blit(cost_text, (center_x + item_width // 2 - cost_text.get_width() - 20, item_y + 15))
            
            count = self.purchase_counts[upgrade['stat']]
            total_value = permanent_upgrades.get(upgrade['stat'], 0)
            
            if upgrade['stat'] in ['crit_rate', 'crit_damage']:
                value_str = f"+{int(upgrade['value'] * 100)}%"
                total_str = f"当前: +{int(total_value * 100)}%"
            else:
                value_str = f"+{upgrade['value']}"
                total_str = f"当前: +{total_value}"
            
            info_text = FONT.render(f"每次: {value_str}  |  已购买: {count}次  |  {total_str}", True, GRAY)
            screen.blit(info_text, (center_x - item_width // 2 + 20, item_y + 35))
        
        instructions = [
            "[W/S] 上下选择",
            "[空格/回车] 购买",
            "[R] 重新开始",
            "[ESC] 返回"
        ]
        
        for i, instr in enumerate(instructions):
            text = FONT.render(instr, True, YELLOW)
            screen.blit(text, (center_x - text.get_width() // 2, list_start_y + len(self.upgrades) * item_height + 20 + i * 30))
    
    def handle_input(self, event, permanent_gold, permanent_upgrades, selected_index):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(self.upgrades)
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(self.upgrades)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                upgrade = self.upgrades[selected_index]
                success, permanent_gold, permanent_upgrades = self.purchase_upgrade(
                    upgrade, permanent_gold, permanent_upgrades)
                return 'purchase', permanent_gold, permanent_upgrades, selected_index
            elif event.key == pygame.K_r:
                return 'restart', permanent_gold, permanent_upgrades, selected_index
            elif event.key == pygame.K_ESCAPE:
                return 'back', permanent_gold, permanent_upgrades, selected_index
        
        return None, permanent_gold, permanent_upgrades, selected_index
