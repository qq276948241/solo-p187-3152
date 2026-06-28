import pygame
import math
import random
from config import *

class Weapon:
    def __init__(self, weapon_type, affixes=None):
        self.type = weapon_type
        base_stats = WEAPON_TYPES[weapon_type]
        self.damage = base_stats['damage']
        self.attack_speed = base_stats['attack_speed']
        self.range = base_stats['range']
        self.mp_cost = base_stats['mp_cost']
        self.color = base_stats['color']
        self.affixes = affixes if affixes else []
        self.last_attack_time = 0
        self._apply_affixes()
    
    def _apply_affixes(self):
        for affix in self.affixes:
            if affix['stat'] == 'attack_speed':
                self.attack_speed += affix['value']
            elif affix['stat'] == 'damage' or affix['stat'] == 'attack':
                self.damage += affix['value']
    
    def can_attack(self, current_time):
        return current_time - self.last_attack_time >= self.attack_speed * 1000
    
    def attack(self, player_pos, target_pos, current_time, projectiles):
        if not self.can_attack(current_time):
            return False, 0
        self.last_attack_time = current_time
        
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        direction = (dx / dist, dy / dist)
        
        if self.type == 'sword':
            return True, self.damage
        elif self.type == 'bow':
            arrow = Projectile(player_pos, direction, self.damage, self.range, self.mp_cost)
            projectiles.append(arrow)
            return True, 0
        
        return False, 0

class Projectile:
    def __init__(self, pos, direction, damage, max_range, mp_cost=0):
        self.x = pos[0]
        self.y = pos[1]
        self.dx = direction[0] * 8
        self.dy = direction[1] * 8
        self.damage = damage
        self.max_range = max_range
        self.traveled = 0
        self.mp_cost = mp_cost
        self.active = True
        self.size = 6
        self.color = YELLOW
    
    def update(self, walls):
        self.x += self.dx
        self.y += self.dy
        self.traveled += math.hypot(self.dx, self.dy)
        
        if self.traveled >= self.max_range:
            self.active = False
        
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        for wall in walls:
            if rect.colliderect(wall):
                self.active = False
                break
    
    def draw(self, screen, camera_offset):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(draw_x), int(draw_y)), self.size - 2)

def generate_random_weapon(floor=1):
    weapon_type = random.choice(['sword', 'bow'])
    num_affixes = min(3, 1 + floor // 2)
    affixes = []
    available_affixes = AFFIX_POOL.copy()
    for _ in range(num_affixes):
        if available_affixes:
            affix = random.choice(available_affixes)
            affixes.append(affix)
            available_affixes.remove(affix)
    return Weapon(weapon_type, affixes)
