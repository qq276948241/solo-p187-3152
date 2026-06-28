import pygame
import math
from config import *
from monster import Monster, Boss, MonsterProjectile

class CombatSystem:
    def __init__(self):
        self.damage_numbers = []
        self.hit_effects = []
    
    def update(self, player, monsters, projectiles, monster_projectiles, walls, current_time):
        for proj in projectiles[:]:
            proj.update(walls)
            if not proj.active:
                projectiles.remove(proj)
                continue
            
            proj_rect = pygame.Rect(proj.x - proj.size//2, proj.y - proj.size//2, 
                                   proj.size, proj.size)
            for monster in monsters:
                if monster.is_dead():
                    continue
                if proj_rect.colliderect(monster.get_rect()):
                    damage = monster.take_damage(proj.damage, current_time)
                    self._add_damage_number(monster.x, monster.y - monster.size, damage, YELLOW)
                    self._add_hit_effect(monster.x, monster.y)
                    proj.active = False
                    break
        
        for proj in monster_projectiles[:]:
            proj.update(walls)
            if not proj.active:
                monster_projectiles.remove(proj)
                continue
            
            if proj.damage > 0:
                proj_rect = pygame.Rect(proj.x - proj.size//2, proj.y - proj.size//2,
                                       proj.size, proj.size)
                if proj_rect.colliderect(player.get_rect()):
                    damage = player.take_damage(proj.damage, current_time)
                    if damage > 0:
                        self._add_damage_number(player.x, player.y - player.size, damage, RED)
                    proj.active = False
        
        attack_rect = player.get_attack_rect()
        if attack_rect and player.is_attacking:
            for monster in monsters:
                if monster.is_dead():
                    continue
                if attack_rect.colliderect(monster.get_rect()):
                    total_damage = player.attack + player.weapon.damage
                    damage = monster.take_damage(total_damage, current_time)
                    self._add_damage_number(monster.x, monster.y - monster.size, damage, WHITE)
                    self._add_hit_effect(monster.x, monster.y)
        
        for monster in monsters:
            if monster.is_dead():
                continue
            
            if isinstance(monster, Boss):
                monster.update(player, walls, monster_projectiles, current_time)
            else:
                monster.update(player, walls, monster_projectiles, current_time)
            
            if monster.type == 'melee' or monster.type == 'charge':
                if monster.get_rect().colliderect(player.get_rect()):
                    if hasattr(monster, 'last_attack_time'):
                        if current_time - monster.last_attack_time > 1000:
                            damage = player.take_damage(monster.damage, current_time)
                            if damage > 0:
                                self._add_damage_number(player.x, player.y - player.size, damage, RED)
                            monster.last_attack_time = current_time
        
        for effect in self.hit_effects[:]:
            effect['life'] -= 1
            if effect['life'] <= 0:
                self.hit_effects.remove(effect)
        
        for dn in self.damage_numbers[:]:
            dn['life'] -= 1
            dn['y'] -= 1
            if dn['life'] <= 0:
                self.damage_numbers.remove(dn)
    
    def _add_damage_number(self, x, y, damage, color):
        self.damage_numbers.append({
            'x': x,
            'y': y,
            'damage': int(damage),
            'color': color,
            'life': 40
        })
    
    def _add_hit_effect(self, x, y):
        self.hit_effects.append({
            'x': x,
            'y': y,
            'radius': 5,
            'max_radius': 20,
            'life': 15
        })
    
    def draw_effects(self, screen, camera_offset, current_time):
        for effect in self.hit_effects:
            draw_x = effect['x'] - camera_offset[0]
            draw_y = effect['y'] - camera_offset[1]
            alpha = int((effect['life'] / 15) * 255)
            radius = effect['max_radius'] - (effect['life'] / 15) * (effect['max_radius'] - effect['radius'])
            
            effect_surface = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(effect_surface, (*WHITE, alpha), (int(radius), int(radius)), int(radius), 2)
            screen.blit(effect_surface, (draw_x - radius, draw_y - radius))
        
        for dn in self.damage_numbers:
            draw_x = dn['x'] - camera_offset[0]
            draw_y = dn['y'] - camera_offset[1]
            alpha = int((dn['life'] / 40) * 255)
            
            text_surface = FONT.render(str(dn['damage']), True, dn['color'])
            text_surface.set_alpha(alpha)
            
            outline_surface = FONT.render(str(dn['damage']), True, BLACK)
            outline_surface.set_alpha(alpha)
            
            screen.blit(outline_surface, (draw_x - text_surface.get_width()//2 + 1, draw_y + 1))
            screen.blit(outline_surface, (draw_x - text_surface.get_width()//2 - 1, draw_y + 1))
            screen.blit(outline_surface, (draw_x - text_surface.get_width()//2 + 1, draw_y - 1))
            screen.blit(outline_surface, (draw_x - text_surface.get_width()//2 - 1, draw_y - 1))
            screen.blit(text_surface, (draw_x - text_surface.get_width()//2, draw_y))
    
    def get_screen_shake(self, monsters, current_time):
        shake_x, shake_y = 0, 0
        for monster in monsters:
            if isinstance(monster, Boss) and not monster.is_dead():
                sx, sy = monster.get_screen_shake(current_time)
                shake_x += sx
                shake_y += sy
        return shake_x, shake_y
