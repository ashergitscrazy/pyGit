# Template pygame setup from replit
import sys
import random

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
SEA_LEVEL = 341
WORLD_WIDTH = 20
WORLD_DEPTH = 10
player_x = (369,431)
player_y = 0



class Player():

    def __init__(self):
        self.tick = 5
        self.frame = 0
        self.dir = 1
        self.vel = 0
        self.accel = 5
        self.img = pygame.image.load("idle.png")
        self.hitbox = pygame.Rect(369, 259, 62, 82)

    def draw(self):
        screen.blit(self.img, (340, 240))
        # 340, 240

    def move(self):
        global player_x, player_y
        keys = pygame.key.get_pressed()
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

player = Player()
# player x dimension: 60
# player y dimension: 80


class Block():
    def __init__(self, blockType, pos):
        self.destroyed = False
        self.img = pygame.image.load(blockType + ".png")
        self.img = pygame.transform.scale(self.img, (BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT))
        self.pos = pos
        self.draw(0)

    def draw(self, x_pos):
        screen.blit(self.img, (self.pos["x"] * BLOCK_WIDTH_HEIGHT - x_pos, self.pos["y"] * BLOCK_WIDTH_HEIGHT + SEA_LEVEL))
    def destroy(self):
        self.img = pygame.image.load("air.png")
        self.destroyed = True



class Terrain():
    def __init__(self, width, depth, block):
        self.blocks = []
        for d in range(depth):
            row = []
            for w in range(width):
                row.append(Block(block, {"x": w, "y": d}))
            self.blocks.append(row)

    def draw(self, x):
        for row in self.blocks:
            for block in row:
                block.draw(x)



terrain = Terrain(WORLD_WIDTH, WORLD_DEPTH, "dirt")

terrain_x = 0
tick = 5
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    dir = player.move()
    if dir:
        terrain_x += 10 * dir
        tick = 2
    if tick > 0:
        screen.fill(bg_color)
        terrain.draw(terrain_x)
        tick -= 1
    player.draw()
    pygame.display.flip()
    clock.tick(60)

