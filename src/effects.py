import pygame
import math
import random
from config import *

class Particle:
    def __init__(self, x, y, color, velocity=None, life=30, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        
        if velocity:
            self.vx = velocity[0]
            self.vy = velocity[1]
        else:
            angle = random.random() * math.pi * 2
            speed = random.uniform(1, 3)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1
    
    def draw(self, screen, camera_offset):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]
        alpha = int((self.life / self.max_life) * 255)
        
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), 
                          (self.size, self.size), self.size)
        screen.blit(particle_surface, (draw_x - self.size, draw_y - self.size))

class EffectSystem:
    def __init__(self):
        self.particles = []
        self.screen_flash = None
        self.level_up_effect = None
    
    def create_death_effect(self, x, y, color):
        for _ in range(15):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def create_attack_effect(self, x, y, direction, weapon_type):
        if weapon_type == 'sword':
            for _ in range(5):
                offset_x = direction[0] * random.uniform(10, 40)
                offset_y = direction[1] * random.uniform(10, 40)
                particle = Particle(x + offset_x, y + offset_y, (200, 200, 200),
                                   velocity=(direction[0] * 2, direction[1] * 2),
                                   life=15, size=2)
                self.particles.append(particle)
        else:
            pass
    
    def create_level_up_effect(self, x, y):
        self.level_up_effect = {
            'x': x,
            'y': y,
            'life': 60,
            'max_life': 60,
            'radius': 0,
            'max_radius': 100
        }
        for _ in range(30):
            angle = random.random() * math.pi * 2
            speed = random.uniform(2, 5)
            particle = Particle(x, y, YELLOW,
                               velocity=(math.cos(angle) * speed, math.sin(angle) * speed),
                               life=40, size=4)
            self.particles.append(particle)
    
    def create_boss_entry_effect(self, x, y):
        self.screen_flash = {'color': RED, 'life': 30, 'max_life': 30}
        for _ in range(50):
            angle = random.random() * math.pi * 2
            speed = random.uniform(3, 8)
            particle = Particle(x, y, ORANGE,
                               velocity=(math.cos(angle) * speed, math.sin(angle) * speed),
                               life=60, size=5)
            self.particles.append(particle)
    
    def create_heal_effect(self, x, y):
        for _ in range(10):
            offset_y = random.uniform(-20, 0)
            particle = Particle(x + random.uniform(-10, 10), y + offset_y, GREEN,
                               velocity=(0, -2), life=30, size=3)
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        if self.screen_flash:
            self.screen_flash['life'] -= 1
            if self.screen_flash['life'] <= 0:
                self.screen_flash = None
        
        if self.level_up_effect:
            self.level_up_effect['life'] -= 1
            progress = 1 - (self.level_up_effect['life'] / self.level_up_effect['max_life'])
            self.level_up_effect['radius'] = self.level_up_effect['max_radius'] * progress
            if self.level_up_effect['life'] <= 0:
                self.level_up_effect = None
    
    def draw(self, screen, camera_offset):
        for particle in self.particles:
            particle.draw(screen, camera_offset)
        
        if self.level_up_effect:
            draw_x = self.level_up_effect['x'] - camera_offset[0]
            draw_y = self.level_up_effect['y'] - camera_offset[1]
            alpha = int((self.level_up_effect['life'] / self.level_up_effect['max_life']) * 150)
            
            effect_surface = pygame.Surface((self.level_up_effect['max_radius'] * 2, 
                                            self.level_up_effect['max_radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(effect_surface, (*YELLOW, alpha),
                              (self.level_up_effect['max_radius'], self.level_up_effect['max_radius']),
                              int(self.level_up_effect['radius']), 3)
            screen.blit(effect_surface, (draw_x - self.level_up_effect['max_radius'], 
                                         draw_y - self.level_up_effect['max_radius']))
    
    def draw_screen_effects(self, screen):
        if self.screen_flash:
            alpha = int((self.screen_flash['life'] / self.screen_flash['max_life']) * 150)
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            effect_surface.set_alpha(alpha)
            effect_surface.fill(self.screen_flash['color'])
            screen.blit(effect_surface, (0, 0))
