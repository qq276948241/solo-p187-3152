import pygame

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
TILE_SIZE = 32
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 50)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

PLAYER_BASE_HP = 100
PLAYER_BASE_MP = 50
PLAYER_BASE_SPEED = 3
PLAYER_BASE_ATTACK = 10
PLAYER_BASE_DEFENSE = 2
PLAYER_BASE_CRIT_RATE = 0.05
PLAYER_BASE_CRIT_DAMAGE = 1.5
PLAYER_SIZE = 24

MONSTER_TYPES = {
    'melee': {'hp': 30, 'damage': 8, 'speed': 1.5, 'size': 20, 'color': RED, 'exp': 10, 'gold': 5},
    'charge': {'hp': 40, 'damage': 15, 'speed': 4, 'size': 22, 'color': ORANGE, 'exp': 15, 'gold': 8},
    'explode': {'hp': 20, 'damage': 25, 'speed': 2, 'size': 18, 'color': YELLOW, 'exp': 12, 'gold': 10, 'explode_radius': 60},
    'ranged': {'hp': 25, 'damage': 10, 'speed': 1, 'size': 20, 'color': PURPLE, 'exp': 12, 'gold': 7, 'attack_range': 200}
}

BOSS_BASE_HP = 300
BOSS_BASE_DAMAGE = 20
BOSS_SIZE = 48
BOSS_COLOR = (200, 0, 0)

WEAPON_TYPES = {
    'sword': {'damage': 15, 'attack_speed': 0.4, 'range': 45, 'mp_cost': 0, 'color': (200, 200, 200)},
    'bow': {'damage': 12, 'attack_speed': 0.7, 'range': 250, 'mp_cost': 2, 'color': BROWN}
}

WAVES_PER_FLOOR = 5
ROOM_WIDTH = 25
ROOM_HEIGHT = 18

AFFIX_POOL = [
    {'name': '攻击+', 'stat': 'attack', 'value': 5},
    {'name': '生命+', 'stat': 'max_hp', 'value': 20},
    {'name': '暴击率+', 'stat': 'crit_rate', 'value': 0.05},
    {'name': '暴击伤害+', 'stat': 'crit_damage', 'value': 0.2},
    {'name': '移速+', 'stat': 'speed', 'value': 0.5},
    {'name': '防御+', 'stat': 'defense', 'value': 3},
    {'name': '攻速+', 'stat': 'attack_speed', 'value': -0.05},
    {'name': '法力+', 'stat': 'max_mp', 'value': 10}
]

SHOP_UPGRADES = [
    {'name': '生命强化', 'stat': 'max_hp', 'value': 10, 'base_cost': 20},
    {'name': '攻击强化', 'stat': 'attack', 'value': 3, 'base_cost': 25},
    {'name': '防御强化', 'stat': 'defense', 'value': 1, 'base_cost': 20},
    {'name': '移速强化', 'stat': 'speed', 'value': 0.2, 'base_cost': 30},
    {'name': '暴击强化', 'stat': 'crit_rate', 'value': 0.02, 'base_cost': 35}
]

pygame.font.init()
FONT = pygame.font.Font(None, 24)
FONT_LARGE = pygame.font.Font(None, 36)
FONT_TITLE = pygame.font.Font(None, 48)
