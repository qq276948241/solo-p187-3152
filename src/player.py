import pygame
import math
import random
from config import *
from weapon import Weapon, generate_random_weapon

class Player:
    def __init__(self, x, y, permanent_upgrades=None):
        self.x = x
        self.y = y
        self.permanent_upgrades = permanent_upgrades if permanent_upgrades else {}
        
        self._calculate_base_stats()
        
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.exp = 0
        self.level = 1
        self.exp_to_next = 50
        self.gold = 0
        self.floor = 1
        
        self.weapon = Weapon('sword')
        self.secondary_weapon = Weapon('bow')
        
        self.facing = (1, 0)
        self.invincible_time = 0
        self.attack_animation_time = 0
        self.is_attacking = False
        
        self.size = PLAYER_SIZE
        self.color = (100, 150, 255)
        self.armor_color = (200, 200, 220)
    
    def _calculate_base_stats(self):
        self.max_hp = PLAYER_BASE_HP + self.permanent_upgrades.get('max_hp', 0)
        self.max_mp = PLAYER_BASE_MP + self.permanent_upgrades.get('max_mp', 0)
        self.speed = PLAYER_BASE_SPEED + self.permanent_upgrades.get('speed', 0)
        self.attack = PLAYER_BASE_ATTACK + self.permanent_upgrades.get('attack', 0)
        self.defense = PLAYER_BASE_DEFENSE + self.permanent_upgrades.get('defense', 0)
        self.crit_rate = PLAYER_BASE_CRIT_RATE + self.permanent_upgrades.get('crit_rate', 0)
        self.crit_damage = PLAYER_BASE_CRIT_DAMAGE + self.permanent_upgrades.get('crit_damage', 0)
    
    def update(self, keys, walls, current_time):
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
        
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx = (dx / length) * self.speed
            dy = (dy / length) * self.speed
            self.facing = (dx / self.speed, dy / self.speed)
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if not self._check_collision(new_x, self.y, walls):
            self.x = new_x
        if not self._check_collision(self.x, new_y, walls):
            self.y = new_y
        
        if current_time < self.invincible_time:
            self.is_attacking = False
        if self.is_attacking and current_time > self.attack_animation_time:
            self.is_attacking = False
        
        if self.mp < self.max_mp:
            self.mp = min(self.max_mp, self.mp + 0.02)
    
    def _check_collision(self, x, y, walls):
        rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False
    
    def attack(self, target_pos, current_time, projectiles):
        total_damage = self.attack + self.weapon.damage
        is_crit = random.random() < self.crit_rate
        if is_crit:
            total_damage *= self.crit_damage
        
        if self.weapon.type == 'bow' and self.mp < self.weapon.mp_cost:
            return False, 0, False
        
        success, weapon_damage = self.weapon.attack((self.x, self.y), target_pos, current_time, projectiles)
        if success:
            self.is_attacking = True
            self.attack_animation_time = current_time + 200
            if self.weapon.type == 'bow':
                self.mp -= self.weapon.mp_cost
            return True, total_damage, is_crit
        return False, 0, False
    
    def switch_weapon(self):
        self.weapon, self.secondary_weapon = self.secondary_weapon, self.weapon
    
    def take_damage(self, damage, current_time):
        if current_time < self.invincible_time:
            return 0
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        self.invincible_time = current_time + 500
        return actual_damage
    
    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.max_mp += 5
        self.attack += 2
        self.defense += 1
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.exp_to_next = int(self.exp_to_next * 1.5)
    
    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def pick_up_weapon(self, weapon):
        self.secondary_weapon = weapon
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
    
    def get_attack_rect(self):
        if self.weapon.type != 'sword':
            return None
        
        attack_length = self.weapon.range
        attack_width = 30
        
        fx, fy = self.facing
        center_x = self.x + fx * (self.size//2 + attack_length//2)
        center_y = self.y + fy * (self.size//2 + attack_length//2)
        
        if abs(fx) > abs(fy):
            rect = pygame.Rect(center_x - attack_length//2, center_y - attack_width//2, attack_length, attack_width)
        else:
            rect = pygame.Rect(center_x - attack_width//2, center_y - attack_length//2, attack_width, attack_length)
        return rect
    
    def draw(self, screen, camera_offset, current_time):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        flash = current_time < self.invincible_time and (current_time // 100) % 2 == 0
        
        if not flash:
            pygame.draw.rect(screen, self.armor_color, (draw_x - self.size//2, draw_y - self.size//2, self.size, self.size))
            pygame.draw.rect(screen, self.color, (draw_x - self.size//3, draw_y - self.size//3, self.size*2//3, self.size*2//3))
            
            eye_offset_x = self.facing[0] * 4
            eye_offset_y = self.facing[1] * 4
            pygame.draw.circle(screen, BLACK, (int(draw_x - 4 + eye_offset_x), int(draw_y - 2 + eye_offset_y)), 2)
            pygame.draw.circle(screen, BLACK, (int(draw_x + 4 + eye_offset_x), int(draw_y - 2 + eye_offset_y)), 2)
            
            if self.is_attacking and self.weapon.type == 'sword':
                weapon_x = draw_x + self.facing[0] * (self.size//2 + 10)
                weapon_y = draw_y + self.facing[1] * (self.size//2 + 10)
                pygame.draw.rect(screen, self.weapon.color, (weapon_x - 3, weapon_y - 15, 6, 30))
    
    def is_dead(self):
        return self.hp <= 0
