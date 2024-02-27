# Template pygame setup from replit
import sys
import random
import perlin_noise
from perlin_noise import PerlinNoise

import pygame
from pygame.locals import QUIT

pygame.init()
bg_color = (59, 190, 237)
screen = pygame.display.set_mode((800, 600))
screen.fill(bg_color)
pygame.display.set_caption('Pycraft')
clock = pygame.time.Clock()

walk_frames = ["idle.png", "1.png", "2.png", "3.png", "4.png"]
BLOCK_WIDTH_HEIGHT = 50
SEA_LEVEL = 340
WORLD_WIDTH = 40
WORLD_DEPTH = 20
NOISE_CONSTANT = 10
PLAYER_HITBOX = pygame.Rect(380, 259, 42, 81)
GRAVITY = 1
TERMINAL_VELOCITY = -20
JUMP_HEIGHT = 20
Y_VELOCITY = JUMP_HEIGHT
jumping = False

# some comment I've added to test git

class Player():

    def __init__(self):
        self.tick = 5
        self.frame = 0
        self.dir = 1
        self.vel_y = 0
        self.accel = 5
        self.floor = 0
        self.img = pygame.image.load("idle.png")
        self.rect = PLAYER_HITBOX

    def draw(self):
        global jumping, terrain_y
        screen.blit(self.img, (340, 240))
        pygame.draw.rect(screen, 33333333, PLAYER_HITBOX, 2)
    def move(self):
        global jumping, falling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not jumping:
            jumping = True
        if keys[pygame.K_a] or keys[pygame.K_d]:
            if self.tick == 0:
                self.frame = 1 + (self.frame) % 4
                self.tick = 5
            else:
                self.tick -= 1
            self.img = pygame.image.load(walk_frames[self.frame])
            if self.dir == -1:
                self.img = pygame.transform.flip(self.img, True, False)
            if keys[pygame.K_a] and self.dir != -1:
                self.dir = -1
            if keys[pygame.K_d] and self.dir != 1:
                self.dir = 1
            return self.dir
        else:
            self.img = pygame.image.load("idle.png")
            if self.dir == -1:
                self.img = pygame.transform.flip(self.img, True, False)
            return 0

    def find_floor(self):
        finder_depth = 5
        searching_for_floor = True
        self.floor = 0
        while searching_for_floor:
            floor_finder = pygame.Rect(PLAYER_HITBOX.x, PLAYER_HITBOX.y, PLAYER_HITBOX.width, finder_depth)
            for column in terrain.blocks:
                for block in column:
                    if block.rect.colliderect(floor_finder):
                        floor = block.is_floor()
                        return floor
            finder_depth += 50
            if finder_depth > 10000:
                searching_for_floor = False


player = Player()


# player x dimension: 60
# player y dimension: 80


class Block():
    def __init__(self, blockType, pos):
        self.destroyed = False
        self.img = pygame.image.load(blockType + ".png")
        self.img = pygame.transform.scale(self.img, (BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT))
        self.pos = pos
        self.draw(0,0)

    def draw(self, x_pos, y_pos):
        self.location = ((self.pos["x"] * BLOCK_WIDTH_HEIGHT) - x_pos, (self.pos["y"] * BLOCK_WIDTH_HEIGHT) + SEA_LEVEL - y_pos)
        screen.blit(self.img, self.location)
        self.rect = pygame.Rect(self.location[0], self.location[1], BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)
        pygame.draw.rect(screen, 000000, self.rect, 2)
        self.y = y_pos

    def destroy(self):
        if self.destroyed == False:
            self.img = pygame.image.load("air.png")
            self.destroyed = True

    def is_floor(self):
        return self.rect


class Terrain:
    def __init__(self, width, depth):
        self.blocks = []
        for w in range(width):
            column = []
            dirt_thickness = random.randint(3, 4)
            for d in range(depth[w]):
                height = WORLD_DEPTH - d
                if d - depth[w] == -1:
                    column.append(Block("grass", {"x": w, "y": height}))
                elif d >= depth[w] - dirt_thickness:
                    column.append(Block("dirt", {"x": w, "y": height}))
                else:
                    column.append(Block("stone", {"x": w, "y": height}))
            self.blocks.append(column)

    def draw(self, x, y):
        for column in self.blocks:
            for block in column:
                block.draw(x, y)




# Terrain generation shenanigans

seed = random.randint(0, 20000)
noise = PerlinNoise(octaves=3, seed=seed)
height_map = []
for i in range(WORLD_WIDTH):
    height = NOISE_CONSTANT * noise([i / WORLD_WIDTH])
    height = round(height)
    height_map.append(WORLD_DEPTH + height)

terrain = Terrain(WORLD_WIDTH, height_map)

terrain_x = 0
terrain_y = -30
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    move_dir = player.move()
    floor_block = player.find_floor()
    floor_collision = floor_block.colliderect(PLAYER_HITBOX)
    if abs(floor_block.top - PLAYER_HITBOX.bottom) > 3:
        if not floor_collision and not jumping:
            terrain_y += GRAVITY * 5
    if jumping:
        terrain_y -= Y_VELOCITY
        Y_VELOCITY -= GRAVITY
    if floor_collision:
        jumping = False
        Y_VELOCITY = JUMP_HEIGHT
        terrain_y -= 10
    if move_dir:
        terrain_x += 10 * move_dir
    screen.fill(bg_color)
    terrain.draw(terrain_x, terrain_y)
    player.draw()
    pygame.display.flip()
    clock.tick(60)
