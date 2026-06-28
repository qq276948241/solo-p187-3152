import pygame
import math
import random
from config import *

class Monster:
    def __init__(self, x, y, monster_type, floor=1):
        self.x = x
        self.y = y
        self.type = monster_type
        self.floor = floor
        
        base_stats = MONSTER_TYPES[monster_type]
        scaling = 1 + (floor - 1) * 0.15
        
        self.max_hp = int(base_stats['hp'] * scaling)
        self.hp = self.max_hp
        self.damage = int(base_stats['damage'] * scaling)
        self.speed = base_stats['speed']
        self.size = base_stats['size']
        self.color = base_stats['color']
        self.exp_reward = int(base_stats['exp'] * scaling)
        self.gold_reward = int(base_stats['gold'] * scaling)
        
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.hit_flash_time = 0
        
        self.state = 'idle'
        self.state_timer = 0
        self.charge_direction = (0, 0)
        
        if monster_type == 'explode':
            self.explode_radius = base_stats['explode_radius']
            self.fuse_timer = 0
            self.is_fusing = False
        elif monster_type == 'ranged':
            self.attack_range = base_stats['attack_range']
            self.projectiles = []
    
    def update(self, player, walls, projectiles, current_time):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            direction = (dx / dist, dy / dist)
        else:
            direction = (1, 0)
        
        if current_time < self.hit_flash_time:
            pass
        
        if self.type == 'melee':
            self._update_melee(direction, dist, player, walls, current_time)
        elif self.type == 'charge':
            self._update_charge(direction, dist, player, walls, current_time)
        elif self.type == 'explode':
            self._update_explode(direction, dist, player, walls, projectiles, current_time)
        elif self.type == 'ranged':
            self._update_ranged(direction, dist, player, walls, projectiles, current_time)
    
    def _update_melee(self, direction, dist, player, walls, current_time):
        if dist > 30:
            self._move(direction, walls)
        else:
            if current_time - self.last_attack_time > 1000:
                player.take_damage(self.damage, current_time)
                self.last_attack_time = current_time
    
    def _update_charge(self, direction, dist, player, walls, current_time):
        if self.state == 'idle':
            if dist < 200:
                self.state = 'charging'
                self.state_timer = current_time + 500
                self.charge_direction = direction
        elif self.state == 'charging':
            if current_time > self.state_timer:
                self.state = 'dash'
                self.state_timer = current_time + 400
        elif self.state == 'dash':
            self._move(self.charge_direction, walls, self.speed * 2)
            if self.get_rect().colliderect(player.get_rect()):
                player.take_damage(self.damage, current_time)
                self.state = 'idle'
            if current_time > self.state_timer:
                self.state = 'idle'
        else:
            if dist > 50:
                self._move(direction, walls, self.speed * 0.5)
    
    def _update_explode(self, direction, dist, player, walls, projectiles, current_time):
        if not self.is_fusing:
            if dist < 80:
                self.is_fusing = True
                self.fuse_timer = current_time + 1500
            else:
                self._move(direction, walls)
        else:
            if current_time > self.fuse_timer:
                self._explode(player, projectiles, current_time)
            else:
                pass
    
    def _explode(self, player, projectiles, current_time):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.explode_radius:
            player.take_damage(self.damage, current_time)
        
        for i in range(12):
            angle = (i / 12) * math.pi * 2
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            proj = MonsterProjectile((self.x, self.y), (dir_x, dir_y), 0, 30, is_explosion=True)
            projectiles.append(proj)
        
        self.hp = 0
    
    def _update_ranged(self, direction, dist, player, walls, projectiles, current_time):
        if dist < self.attack_range:
            if dist < 100:
                self._move((-direction[0], -direction[1]), walls)
            if current_time - self.last_attack_time > 1500:
                proj = MonsterProjectile((self.x, self.y), direction, self.damage, self.attack_range)
                projectiles.append(proj)
                self.last_attack_time = current_time
        else:
            self._move(direction, walls)
    
    def _move(self, direction, walls, speed=None):
        if speed is None:
            speed = self.speed
        new_x = self.x + direction[0] * speed
        new_y = self.y + direction[1] * speed
        
        if not self._check_collision(new_x, self.y, walls):
            self.x = new_x
        if not self._check_collision(self.x, new_y, walls):
            self.y = new_y
    
    def _check_collision(self, x, y, walls):
        rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False
    
    def take_damage(self, damage, current_time):
        self.hp -= damage
        self.hit_flash_time = current_time + 100
        return damage
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
    
    def is_dead(self):
        return self.hp <= 0
    
    def draw(self, screen, camera_offset, current_time):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        flash = current_time < self.hit_flash_time
        
        if self.type == 'explode' and self.is_fusing:
            flicker = (current_time // 100) % 2 == 0
            color = RED if flicker else self.color
        else:
            color = WHITE if flash else self.color
        
        pygame.draw.rect(screen, color, (draw_x - self.size//2, draw_y - self.size//2, self.size, self.size))
        pygame.draw.rect(screen, BLACK, (draw_x - self.size//4, draw_y - self.size//4, self.size//2, self.size//2))
        
        pygame.draw.circle(screen, RED, (int(draw_x - 3), int(draw_y - 2)), 2)
        pygame.draw.circle(screen, RED, (int(draw_x + 3), int(draw_y - 2)), 2)
        
        bar_width = self.size
        bar_height = 4
        bar_x = draw_x - bar_width // 2
        bar_y = draw_y - self.size // 2 - 8
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

class MonsterProjectile:
    def __init__(self, pos, direction, damage, max_range, is_explosion=False):
        self.x = pos[0]
        self.y = pos[1]
        self.dx = direction[0] * (4 if not is_explosion else 6)
        self.dy = direction[1] * (4 if not is_explosion else 6)
        self.damage = damage
        self.max_range = max_range
        self.traveled = 0
        self.active = True
        self.size = 6
        self.color = PURPLE if not is_explosion else ORANGE
        self.is_explosion = is_explosion
    
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
        if self.is_explosion:
            pygame.draw.circle(screen, YELLOW, (int(draw_x), int(draw_y)), self.size - 2)

class Boss(Monster):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, 'melee', floor)
        scaling = 1 + (floor - 1) * 0.2
        self.max_hp = int(BOSS_BASE_HP * scaling)
        self.hp = self.max_hp
        self.damage = int(BOSS_BASE_DAMAGE * scaling)
        self.size = BOSS_SIZE
        self.color = BOSS_COLOR
        self.exp_reward = 100 * floor
        self.gold_reward = 50 * floor
        self.phase = 1
        self.special_attack_cooldown = 0
        self.screen_shake_time = 0
        self.fullscreen_effect_time = 0
    
    def update(self, player, walls, projectiles, current_time):
        super().update(player, walls, projectiles, current_time)
        
        if self.hp < self.max_hp * 0.5 and self.phase == 1:
            self.phase = 2
            self.fullscreen_effect_time = current_time + 1000
            self.screen_shake_time = current_time + 500
        
        if current_time > self.special_attack_cooldown:
            if self.phase == 2:
                self._special_attack(player, projectiles, current_time)
                self.special_attack_cooldown = current_time + 3000
            else:
                self.special_attack_cooldown = current_time + 5000
    
    def _special_attack(self, player, projectiles, current_time):
        self.fullscreen_effect_time = current_time + 500
        self.screen_shake_time = current_time + 300
        
        num_projectiles = 16
        for i in range(num_projectiles):
            angle = (i / num_projectiles) * math.pi * 2
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            proj = MonsterProjectile((self.x, self.y), (dir_x, dir_y), self.damage // 2, 300)
            projectiles.append(proj)
    
    def draw(self, screen, camera_offset, current_time):
        if current_time < self.fullscreen_effect_time:
            alpha = int((self.fullscreen_effect_time - current_time) / 500 * 100)
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            effect_surface.set_alpha(alpha)
            effect_surface.fill(RED)
            screen.blit(effect_surface, (0, 0))
        
        super().draw(screen, camera_offset, current_time)
        
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        
        pygame.draw.rect(screen, GOLD, (draw_x - self.size//2 + 2, draw_y - self.size//2 + 2, self.size - 4, 4))
        pygame.draw.rect(screen, GOLD, (draw_x - self.size//2 + 2, draw_y + self.size//2 - 6, self.size - 4, 4))
        
        if self.phase == 2:
            pygame.draw.circle(screen, ORANGE, (int(draw_x), int(draw_y - self.size//2 - 10)), 5)
    
    def get_screen_shake(self, current_time):
        if current_time < self.screen_shake_time:
            return random.randint(-5, 5), random.randint(-5, 5)
        return 0, 0

def spawn_monster(room_x, room_y, room_width, room_height, floor, monster_type=None):
    if monster_type is None:
        types = ['melee', 'charge', 'explode', 'ranged']
        weights = [0.4, 0.25, 0.15, 0.2]
        monster_type = random.choices(types, weights=weights)[0]
    
    x = random.randint(room_x + 2, room_x + room_width - 2) * TILE_SIZE
    y = random.randint(room_y + 2, room_y + room_height - 2) * TILE_SIZE
    
    return Monster(x, y, monster_type, floor)
