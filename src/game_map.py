import pygame
import random
from config import *

class Room:
    def __init__(self, x, y, width, height, room_type='normal'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = room_type
        self.cleared = False
        self.visited = False
        self.monsters = []
        self.loot = []
        self.exit_portal = None
    
    def get_center(self):
        return (self.x + self.width // 2) * TILE_SIZE, (self.y + self.height // 2) * TILE_SIZE
    
    def get_rect(self):
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, 
                          self.width * TILE_SIZE, self.height * TILE_SIZE)
    
    def contains(self, x, y):
        return (self.x * TILE_SIZE <= x < (self.x + self.width) * TILE_SIZE and
                self.y * TILE_SIZE <= y < (self.y + self.height) * TILE_SIZE)

class GameMap:
    def __init__(self, floor=1):
        self.floor = floor
        self.rooms = []
        self.walls = []
        self.current_room = None
        self.total_width = ROOM_WIDTH * 3
        self.total_height = ROOM_HEIGHT * 3
        self._generate_map()
    
    def _generate_map(self):
        self.rooms = []
        
        center_x = ROOM_WIDTH
        center_y = ROOM_HEIGHT
        
        start_room = Room(center_x, center_y, ROOM_WIDTH, ROOM_HEIGHT, 'start')
        self.rooms.append(start_room)
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        
        for i, (dx, dy) in enumerate(directions):
            room_type = 'normal' if i < 4 else 'treasure'
            room_x = center_x + dx * ROOM_WIDTH
            room_y = center_y + dy * ROOM_HEIGHT
            room = Room(room_x, room_y, ROOM_WIDTH, ROOM_HEIGHT, room_type)
            self.rooms.append(room)
        
        boss_room_x = center_x + directions[0][0] * ROOM_WIDTH * 2
        boss_room_y = center_y + directions[0][1] * ROOM_HEIGHT * 2
        boss_room = Room(boss_room_x, boss_room_y, ROOM_WIDTH + 4, ROOM_HEIGHT + 4, 'boss')
        self.rooms.append(boss_room)
        
        self._generate_walls()
        self.current_room = start_room
        start_room.visited = True
        start_room.cleared = True
    
    def _generate_walls(self):
        self.walls = []
        
        map_width = self.total_width * TILE_SIZE
        map_height = self.total_height * TILE_SIZE
        
        for x in range(0, map_width, TILE_SIZE):
            for y in range(0, map_height, TILE_SIZE):
                in_room = False
                in_corridor = False
                
                for room in self.rooms:
                    if (room.x * TILE_SIZE <= x < (room.x + room.width) * TILE_SIZE and
                        room.y * TILE_SIZE <= y < (room.y + room.height) * TILE_SIZE):
                        in_room = True
                        break
                
                if not in_room:
                    in_corridor = self._is_in_corridor(x, y)
                
                if not in_room and not in_corridor:
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
    
    def _is_in_corridor(self, x, y):
        start_room = self.rooms[0]
        start_center_x = (start_room.x + start_room.width // 2) * TILE_SIZE
        start_center_y = (start_room.y + start_room.height // 2) * TILE_SIZE
        
        corridor_width = TILE_SIZE * 2
        
        for room in self.rooms[1:]:
            room_center_x = (room.x + room.width // 2) * TILE_SIZE
            room_center_y = (room.y + room.height // 2) * TILE_SIZE
            
            h_corridor = pygame.Rect(min(start_center_x, room_center_x) - corridor_width//2,
                                    start_center_y - corridor_width//2,
                                    abs(start_center_x - room_center_x) + corridor_width,
                                    corridor_width)
            
            v_corridor = pygame.Rect(room_center_x - corridor_width//2,
                                    min(start_center_y, room_center_y) - corridor_width//2,
                                    corridor_width,
                                    abs(start_center_y - room_center_y) + corridor_width)
            
            if h_corridor.collidepoint(x + TILE_SIZE//2, y + TILE_SIZE//2):
                return True
            if v_corridor.collidepoint(x + TILE_SIZE//2, y + TILE_SIZE//2):
                return True
        
        if len(self.rooms) > 5:
            boss_room = self.rooms[-1]
            first_side_room = self.rooms[1]
            boss_center_x = (boss_room.x + boss_room.width // 2) * TILE_SIZE
            boss_center_y = (boss_room.y + boss_room.height // 2) * TILE_SIZE
            side_center_x = (first_side_room.x + first_side_room.width // 2) * TILE_SIZE
            side_center_y = (first_side_room.y + first_side_room.height // 2) * TILE_SIZE
            
            h_corridor = pygame.Rect(min(side_center_x, boss_center_x) - corridor_width//2,
                                    side_center_y - corridor_width//2,
                                    abs(side_center_x - boss_center_x) + corridor_width,
                                    corridor_width)
            
            v_corridor = pygame.Rect(boss_center_x - corridor_width//2,
                                    min(side_center_y, boss_center_y) - corridor_width//2,
                                    corridor_width,
                                    abs(side_center_y - boss_center_y) + corridor_width)
            
            if h_corridor.collidepoint(x + TILE_SIZE//2, y + TILE_SIZE//2):
                return True
            if v_corridor.collidepoint(x + TILE_SIZE//2, y + TILE_SIZE//2):
                return True
        
        return False
    
    def get_room_at(self, x, y):
        for room in self.rooms:
            if room.contains(x, y):
                return room
        return None
    
    def update_current_room(self, player_x, player_y):
        room = self.get_room_at(player_x, player_y)
        if room and room != self.current_room:
            self.current_room = room
            if not room.visited:
                room.visited = True
        return self.current_room
    
    def draw(self, screen, camera_offset):
        map_width = self.total_width * TILE_SIZE
        map_height = self.total_height * TILE_SIZE
        
        for x in range(0, map_width, TILE_SIZE):
            for y in range(0, map_height, TILE_SIZE):
                draw_x = x - camera_offset[0]
                draw_y = y - camera_offset[1]
                
                if (draw_x + TILE_SIZE < 0 or draw_x > SCREEN_WIDTH or
                    draw_y + TILE_SIZE < 0 or draw_y > SCREEN_HEIGHT):
                    continue
                
                in_room = False
                for room in self.rooms:
                    if (room.x * TILE_SIZE <= x < (room.x + room.width) * TILE_SIZE and
                        room.y * TILE_SIZE <= y < (room.y + room.height) * TILE_SIZE):
                        in_room = True
                        break
                
                if in_room:
                    color = (40, 40, 50)
                    pygame.draw.rect(screen, color, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, (50, 50, 60), (draw_x + 1, draw_y + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                elif self._is_in_corridor(x, y):
                    color = (60, 60, 70)
                    pygame.draw.rect(screen, color, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, (20, 20, 30), (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
        
        for wall in self.walls:
            draw_x = wall.x - camera_offset[0]
            draw_y = wall.y - camera_offset[1]
            
            if (draw_x + TILE_SIZE < 0 or draw_x > SCREEN_WIDTH or
                draw_y + TILE_SIZE < 0 or draw_y > SCREEN_HEIGHT):
                continue
            
            pygame.draw.rect(screen, (80, 80, 90), (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (100, 100, 110), (draw_x + 2, draw_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
            pygame.draw.rect(screen, (60, 60, 70), (draw_x + 4, draw_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
