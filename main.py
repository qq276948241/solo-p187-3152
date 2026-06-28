import sys
import os
import random
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import *
from player import Player
from monster import Monster, Boss, spawn_monster
from weapon import generate_random_weapon
from game_map import GameMap
from combat import CombatSystem
from effects import EffectSystem
from ui import UIManager
from shop import Shop

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("像素地牢爬塔 - Pixel Dungeon")
        self.clock = pygame.time.Clock()
        
        self.permanent_gold = 0
        self.permanent_upgrades = {}
        
        self.combat_system = CombatSystem()
        self.effect_system = EffectSystem()
        self.ui_manager = UIManager()
        self.shop = Shop()
        
        self.game_state = 'menu'
        self.selected_shop_index = 0
        
        self.new_game()
    
    def new_game(self):
        self.game_map = GameMap(floor=1)
        start_room = self.game_map.rooms[0]
        center_x, center_y = start_room.get_center()
        
        self.player = Player(center_x, center_y, self.permanent_upgrades)
        self.player.floor = 1
        
        self.monsters = []
        self.projectiles = []
        self.monster_projectiles = []
        self.loot_items = []
        
        self.current_wave = 0
        self.total_waves = WAVES_PER_FLOOR
        self.wave_announcement_time = 0
        self.wave_announcement_alpha = 0
        self.is_boss_wave = False
        
        self.camera_offset = [0, 0]
        
        self.game_state = 'playing'
        self.paused = False
        
        self._start_next_wave()
    
    def _start_next_wave(self):
        self.current_wave += 1
        
        if self.current_wave > self.total_waves:
            self._spawn_boss()
            self.is_boss_wave = True
            self.wave_announcement_time = pygame.time.get_ticks() + 2000
            self.wave_announcement_alpha = 255
            return
        
        self.is_boss_wave = False
        room = self.game_map.current_room
        num_monsters = 3 + self.player.floor + self.current_wave
        
        for _ in range(num_monsters):
            monster = spawn_monster(room.x, room.y, room.width, room.height, 
                                   self.player.floor)
            self.monsters.append(monster)
        
        self.wave_announcement_time = pygame.time.get_ticks() + 1500
        self.wave_announcement_alpha = 255
    
    def _spawn_boss(self):
        room = self.game_map.current_room
        center_x, center_y = room.get_center()
        boss = Boss(center_x, center_y, self.player.floor)
        self.monsters.append(boss)
        self.effect_system.create_boss_entry_effect(center_x, center_y)
    
    def _check_wave_complete(self):
        alive_monsters = [m for m in self.monsters if not m.is_dead()]
        if len(alive_monsters) == 0:
            if self.is_boss_wave:
                self.game_state = 'victory'
            else:
                if self.current_wave < self.total_waves:
                    self._start_next_wave()
                else:
                    self._spawn_boss()
                    self.is_boss_wave = True
    
    def _handle_monster_death(self, monster):
        if monster.is_dead() and not hasattr(monster, 'rewarded'):
            monster.rewarded = True
            self.player.gain_exp(monster.exp_reward)
            self.player.gold += monster.gold_reward
            
            if monster.type == 'explode':
                self.effect_system.create_death_effect(monster.x, monster.y, ORANGE)
            else:
                self.effect_system.create_death_effect(monster.x, monster.y, monster.color)
            
            if random.random() < 0.15:
                weapon = generate_random_weapon(self.player.floor)
                self.loot_items.append({
                    'type': 'weapon',
                    'x': monster.x,
                    'y': monster.y,
                    'item': weapon
                })
            elif random.random() < 0.1:
                self.loot_items.append({
                    'type': 'gold',
                    'x': monster.x,
                    'y': monster.y,
                    'amount': random.randint(5, 15) * self.player.floor
                })
            elif random.random() < 0.05:
                self.loot_items.append({
                    'type': 'heal',
                    'x': monster.x,
                    'y': monster.y,
                    'amount': 30
                })
    
    def _update_camera(self):
        target_x = self.player.x - SCREEN_WIDTH // 2
        target_y = self.player.y - SCREEN_HEIGHT // 2
        
        self.camera_offset[0] += (target_x - self.camera_offset[0]) * 0.1
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * 0.1
        
        shake_x, shake_y = self.combat_system.get_screen_shake(self.monsters, pygame.time.get_ticks())
        self.camera_offset[0] += shake_x
        self.camera_offset[1] += shake_y
    
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.game_state == 'menu':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.new_game()
            
            elif self.game_state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_q and not self.paused:
                        old_level = self.player.level
                        self.player.switch_weapon()
                    elif event.key == pygame.K_f and not self.paused:
                        self._try_pickup_loot()
                    elif not self.paused:
                        if event.key in [pygame.K_j, pygame.K_SPACE]:
                            mouse_pos = pygame.mouse.get_pos()
                            world_pos = (mouse_pos[0] + self.camera_offset[0], 
                                        mouse_pos[1] + self.camera_offset[1])
                            success, damage, is_crit = self.player.attack(
                                world_pos, pygame.time.get_ticks(), self.projectiles)
                            if success:
                                self.effect_system.create_attack_effect(
                                    self.player.x, self.player.y, self.player.facing, 
                                    self.player.weapon.type)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        world_pos = (mouse_pos[0] + self.camera_offset[0], 
                                    mouse_pos[1] + self.camera_offset[1])
                        success, damage, is_crit = self.player.attack(
                            world_pos, pygame.time.get_ticks(), self.projectiles)
                        if success:
                            self.effect_system.create_attack_effect(
                                self.player.x, self.player.y, self.player.facing,
                                self.player.weapon.type)
            
            elif self.game_state == 'dead':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.game_state = 'shop'
                    elif event.key == pygame.K_r:
                        self.permanent_gold += self.player.gold
                        self.new_game()
            
            elif self.game_state == 'shop':
                action, self.permanent_gold, self.permanent_upgrades, self.selected_shop_index = \
                    self.shop.handle_input(event, self.permanent_gold, self.permanent_upgrades, 
                                          self.selected_shop_index)
                if action == 'restart':
                    self.new_game()
                elif action == 'back':
                    self.game_state = 'dead'
            
            elif self.game_state == 'victory':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._next_floor()
    
    def _try_pickup_loot(self):
        player_rect = self.player.get_rect()
        for loot in self.loot_items[:]:
            loot_rect = pygame.Rect(loot['x'] - 15, loot['y'] - 15, 30, 30)
            if player_rect.colliderect(loot_rect):
                if loot['type'] == 'weapon':
                    self.player.pick_up_weapon(loot['item'])
                elif loot['type'] == 'gold':
                    self.player.gold += loot['amount']
                elif loot['type'] == 'heal':
                    self.player.heal(loot['amount'])
                    self.effect_system.create_heal_effect(self.player.x, self.player.y)
                self.loot_items.remove(loot)
                break
    
    def _next_floor(self):
        self.player.floor += 1
        self.game_map = GameMap(floor=self.player.floor)
        start_room = self.game_map.rooms[0]
        center_x, center_y = start_room.get_center()
        
        self.player.x = center_x
        self.player.y = center_y
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        
        self.monsters = []
        self.projectiles = []
        self.monster_projectiles = []
        self.loot_items = []
        
        self.current_wave = 0
        self.game_state = 'playing'
        
        self._start_next_wave()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.game_state != 'playing' or self.paused:
            return
        
        keys = pygame.key.get_pressed()
        
        old_level = self.player.level
        self.player.update(keys, self.game_map.walls, current_time)
        if self.player.level > old_level:
            self.effect_system.create_level_up_effect(self.player.x, self.player.y)
        
        self.combat_system.update(self.player, self.monsters, self.projectiles, 
                                 self.monster_projectiles, self.game_map.walls, current_time)
        
        for monster in self.monsters:
            self._handle_monster_death(monster)
        
        self.monsters = [m for m in self.monsters if not m.is_dead()]
        
        self._check_wave_complete()
        
        self.effect_system.update()
        
        self.game_map.update_current_room(self.player.x, self.player.y)
        
        self._update_camera()
        
        if current_time < self.wave_announcement_time:
            self.wave_announcement_alpha = int(
                (self.wave_announcement_time - current_time) / 2000 * 255)
        else:
            self.wave_announcement_alpha = 0
        
        if self.player.is_dead():
            self.permanent_gold += self.player.gold
            self.game_state = 'dead'
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_state == 'menu':
            self._draw_menu()
        elif self.game_state in ['playing', 'paused']:
            self._draw_game()
            if self.paused:
                self.ui_manager.draw_pause_screen(self.screen)
        elif self.game_state == 'dead':
            self._draw_game()
            self.ui_manager.draw_death_screen(self.screen, self.player, self.permanent_gold)
        elif self.game_state == 'shop':
            self._draw_game()
            self.shop.draw(self.screen, self.permanent_gold, self.permanent_upgrades, 
                          self.selected_shop_index)
        elif self.game_state == 'victory':
            self._draw_game()
            self.ui_manager.draw_victory_screen(self.screen, self.player)
        
        pygame.display.flip()
    
    def _draw_menu(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        title_text = FONT_TITLE.render("像素地牢爬塔", True, YELLOW)
        self.screen.blit(title_text, (center_x - title_text.get_width() // 2, center_y - 150))
        
        subtitle_text = FONT_LARGE.render("Pixel Dungeon", True, WHITE)
        self.screen.blit(subtitle_text, (center_x - subtitle_text.get_width() // 2, center_y - 90))
        
        controls = [
            "WASD / 方向键 - 移动",
            "鼠标左键 / J / 空格 - 攻击",
            "Q - 切换武器",
            "F - 拾取物品",
            "ESC - 暂停"
        ]
        
        for i, control in enumerate(controls):
            text = FONT.render(control, True, GRAY)
            self.screen.blit(text, (center_x - text.get_width() // 2, center_y - 20 + i * 30))
        
        start_text = FONT_LARGE.render("按 回车 或 空格 开始游戏", True, GREEN)
        self.screen.blit(start_text, (center_x - start_text.get_width() // 2, center_y + 150))
    
    def _draw_game(self):
        self.game_map.draw(self.screen, self.camera_offset)
        
        for loot in self.loot_items:
            draw_x = loot['x'] - self.camera_offset[0]
            draw_y = loot['y'] - self.camera_offset[1]
            
            if loot['type'] == 'weapon':
                color = loot['item'].color
                pygame.draw.rect(self.screen, color, (draw_x - 10, draw_y - 10, 20, 20))
                pygame.draw.rect(self.screen, GOLD, (draw_x - 12, draw_y - 12, 24, 24), 2)
            elif loot['type'] == 'gold':
                pygame.draw.circle(self.screen, GOLD, (int(draw_x), int(draw_y)), 8)
                pygame.draw.circle(self.screen, YELLOW, (int(draw_x), int(draw_y)), 5)
            elif loot['type'] == 'heal':
                pygame.draw.circle(self.screen, RED, (int(draw_x), int(draw_y)), 8)
                pygame.draw.circle(self.screen, WHITE, (int(draw_x), int(draw_y)), 5)
        
        for proj in self.projectiles:
            proj.draw(self.screen, self.camera_offset)
        
        for proj in self.monster_projectiles:
            proj.draw(self.screen, self.camera_offset)
        
        for monster in self.monsters:
            if not monster.is_dead():
                monster.draw(self.screen, self.camera_offset, pygame.time.get_ticks())
        
        self.player.draw(self.screen, self.camera_offset, pygame.time.get_ticks())
        
        self.combat_system.draw_effects(self.screen, self.camera_offset, pygame.time.get_ticks())
        self.effect_system.draw(self.screen, self.camera_offset)
        self.effect_system.draw_screen_effects(self.screen)
        
        self.ui_manager.draw_hud(self.screen, self.player, self.current_wave, 
                                self.total_waves + 1, self.game_map.current_room.type)
        
        if self.wave_announcement_alpha > 0:
            self.ui_manager.draw_wave_announcement(
                self.screen, self.current_wave, self.is_boss_wave, 
                self.wave_announcement_alpha)
        
        player_rect = self.player.get_rect()
        for loot in self.loot_items:
            loot_rect = pygame.Rect(loot['x'] - 15, loot['y'] - 15, 30, 30)
            if player_rect.colliderect(loot_rect) and loot['type'] == 'weapon':
                self.ui_manager.draw_loot_prompt(self.screen, loot['item'])
                break
    
    def run(self):
        while True:
            self._handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
