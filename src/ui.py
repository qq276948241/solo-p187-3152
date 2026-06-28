import pygame
from config import *

class UIManager:
    def __init__(self):
        self.minimap_scale = 4
    
    def draw_hud(self, screen, player, current_wave, total_waves, current_room_type):
        self._draw_bars(screen, player)
        self._draw_stats(screen, player)
        self._draw_floor_info(screen, player.floor, current_wave, total_waves, current_room_type)
        self._draw_weapon_info(screen, player)
        self._draw_minimap(screen, player)
    
    def _draw_bars(self, screen, player):
        bar_x = 20
        bar_y = 20
        bar_width = 250
        bar_height = 20
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = max(0, player.hp / player.max_hp)
        hp_color = RED if hp_ratio < 0.3 else GREEN
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = FONT.render(f"HP: {int(player.hp)}/{player.max_hp}", True, WHITE)
        screen.blit(hp_text, (bar_x + 5, bar_y + 2))
        
        bar_y += 30
        pygame.draw.rect(screen, DARK_GRAY, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        mp_ratio = max(0, player.mp / player.max_mp)
        pygame.draw.rect(screen, BLUE, (bar_x, bar_y, int(bar_width * mp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        mp_text = FONT.render(f"MP: {int(player.mp)}/{player.max_mp}", True, WHITE)
        screen.blit(mp_text, (bar_x + 5, bar_y + 2))
        
        bar_y += 30
        pygame.draw.rect(screen, DARK_GRAY, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        exp_ratio = max(0, player.exp / player.exp_to_next)
        pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, int(bar_width * exp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        exp_text = FONT.render(f"EXP: {player.exp}/{player.exp_to_next} (Lv.{player.level})", True, WHITE)
        screen.blit(exp_text, (bar_x + 5, bar_y + 2))
    
    def _draw_stats(self, screen, player):
        start_x = SCREEN_WIDTH - 220
        start_y = 20
        line_height = 25
        
        stats = [
            f"攻击: {player.attack + player.weapon.damage}",
            f"防御: {player.defense}",
            f"暴击: {int(player.crit_rate * 100)}%",
            f"暴伤: {int(player.crit_damage * 100)}%",
            f"移速: {player.speed:.1f}",
            f"金币: {player.gold}"
        ]
        
        for i, stat in enumerate(stats):
            text = FONT.render(stat, True, WHITE)
            screen.blit(text, (start_x, start_y + i * line_height))
    
    def _draw_floor_info(self, screen, floor, current_wave, total_waves, room_type):
        center_x = SCREEN_WIDTH // 2
        floor_text = FONT_LARGE.render(f"第 {floor} 层", True, WHITE)
        screen.blit(floor_text, (center_x - floor_text.get_width() // 2, 20))
        
        wave_text = FONT.render(f"波次: {current_wave}/{total_waves}", True, YELLOW)
        screen.blit(wave_text, (center_x - wave_text.get_width() // 2, 55))
        
        room_names = {
            'start': '起始房间',
            'normal': '战斗房间',
            'treasure': '宝藏房间',
            'boss': 'BOSS房间'
        }
        room_text = FONT.render(room_names.get(room_type, '未知'), True, ORANGE)
        screen.blit(room_text, (center_x - room_text.get_width() // 2, 80))
    
    def _draw_weapon_info(self, screen, player):
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 80
        
        weapon_type_names = {'sword': '剑', 'bow': '弓'}
        weapon_name = weapon_type_names.get(player.weapon.type, '未知')
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x - 5, bar_y - 5, 300, 70))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, 290, 60))
        
        title_text = FONT.render(f"当前武器: {weapon_name}", True, WHITE)
        screen.blit(title_text, (bar_x + 10, bar_y + 5))
        
        stats_text = FONT.render(f"伤害:{player.weapon.damage} 攻速:{player.weapon.attack_speed:.2f}s 范围:{player.weapon.range}", True, GRAY)
        screen.blit(stats_text, (bar_x + 10, bar_y + 30))
        
        if player.weapon.affixes:
            affix_text = FONT.render(f"词条: {', '.join([a['name'] for a in player.weapon.affixes])}", True, GREEN)
            screen.blit(affix_text, (bar_x + 10, bar_y + 45))
        
        switch_text = FONT.render("[Q] 切换武器", True, YELLOW)
        screen.blit(switch_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))
    
    def _draw_minimap(self, screen, player):
        minimap_size = 120
        minimap_x = SCREEN_WIDTH - minimap_size - 20
        minimap_y = SCREEN_HEIGHT - minimap_size - 20
        scale = self.minimap_scale
        
        pygame.draw.rect(screen, BLACK, (minimap_x - 2, minimap_y - 2, minimap_size + 4, minimap_size + 4))
        pygame.draw.rect(screen, DARK_GRAY, (minimap_x, minimap_y, minimap_size, minimap_size))
        
        center_x = minimap_x + minimap_size // 2
        center_y = minimap_y + minimap_size // 2
        
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                tile_x = int(player.x / TILE_SIZE) + dx
                tile_y = int(player.y / TILE_SIZE) + dy
                
                map_x = center_x + dx * scale
                map_y = center_y + dy * scale
                
                wall_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                is_wall = any(wall_rect.colliderect(w) for w in [])
                
                if is_wall:
                    color = GRAY
                else:
                    color = (50, 50, 60)
                
                pygame.draw.rect(screen, color, (map_x, map_y, scale - 1, scale - 1))
        
        player_map_x = center_x
        player_map_y = center_y
        pygame.draw.circle(screen, BLUE, (player_map_x, player_map_y), 3)
    
    def draw_death_screen(self, screen, player, permanent_gold):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        title_text = FONT_TITLE.render("你死了", True, RED)
        screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 150))
        
        stats = [
            f"到达层数: {player.floor}",
            f"最终等级: {player.level}",
            f"获得金币: {player.gold}",
            f"总金币: {permanent_gold}"
        ]
        
        for i, stat in enumerate(stats):
            text = FONT_LARGE.render(stat, True, WHITE)
            screen.blit(text, (center_x - text.get_width() // 2, center_y - 80 + i * 40))
        
        shop_text = FONT.render("[E] 进入商店   [R] 重新开始", True, YELLOW)
        screen.blit(shop_text, (center_x - shop_text.get_width() // 2, center_y + 100))
    
    def draw_victory_screen(self, screen, player):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        title_text = FONT_TITLE.render("层通关!", True, GREEN)
        screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 100))
        
        reward_text = FONT_LARGE.render(f"获得 {50 * player.floor} 金币!", True, GOLD)
        screen.blit(reward_text, (center_x - reward_text.get_width() // 2, center_y - 20))
        
        continue_text = FONT.render("[空格] 进入下一层", True, YELLOW)
        screen.blit(continue_text, (center_x - continue_text.get_width() // 2, center_y + 60))
    
    def draw_wave_announcement(self, screen, wave_number, is_boss=False, alpha=255):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        if is_boss:
            text = FONT_TITLE.render("BOSS 来袭!", True, RED)
        else:
            text = FONT_TITLE.render(f"第 {wave_number} 波", True, WHITE)
        
        text.set_alpha(alpha)
        screen.blit(text, (center_x - text.get_width() // 2, center_y - text.get_height() // 2))
    
    def draw_loot_prompt(self, screen, weapon):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 + 150
        
        weapon_type_names = {'sword': '剑', 'bow': '弓'}
        weapon_name = weapon_type_names.get(weapon.type, '未知')
        
        prompt_text = FONT.render(f"[F] 拾取 {weapon_name} (伤害:{weapon.damage})", True, GOLD)
        screen.blit(prompt_text, (center_x - prompt_text.get_width() // 2, center_y))
    
    def draw_pause_screen(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        title_text = FONT_TITLE.render("暂停", True, WHITE)
        screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 50))
        
        resume_text = FONT.render("[ESC] 继续游戏", True, YELLOW)
        screen.blit(resume_text, (center_x - resume_text.get_width() // 2, center_y + 30))
