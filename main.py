# Template pygame setup from replit
import sys
import random
from perlin_noise import PerlinNoise
import math

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
PLAYER_CENTER = (401, 299.5)
GRAVITY = 1
TERMINAL_VELOCITY = 16
JUMP_HEIGHT = 20
Y_VELOCITY = JUMP_HEIGHT
FALL_VELOCITY = 0
jumping = False
falling = False
mouse_pos = (0, 0)
selected_block = (0,0,0,0)


# some comment I've added to test git

class Player:

    def __init__(self):
        # More tool power equals faster mining speeds for certain blocks. Based on the tool being used
        self.shovel_power = 1
        self.pickaxe_power = 1
        self.axe_power = 1

        self.can_move_right = True
        self.can_move_left = True
        self.can_move_up = True
        self.l_col = (255, 0, 255)
        self.r_col = (255, 255, 255)
        self.tick = 5
        self.frame = 0
        self.dir = 1
        self.img = pygame.image.load("idle.png")
        self.rect = PLAYER_HITBOX
        right_edge = PLAYER_HITBOX.x + PLAYER_HITBOX.width
        self.right_sensor = pygame.Rect(right_edge, PLAYER_HITBOX.y, 20, PLAYER_HITBOX.height - 5)
        self.left_sensor = pygame.Rect(PLAYER_HITBOX.x - 20, PLAYER_HITBOX.y, 20, PLAYER_HITBOX.height - 5)
        self.up_sensor = pygame.Rect(PLAYER_HITBOX.x, PLAYER_HITBOX.y - 10, PLAYER_HITBOX.width, 10)

    def draw(self):
        global jumping, terrain_y
        screen.blit(self.img, (340, 240))
        # pygame.draw.rect(screen, 33333333, PLAYER_HITBOX, 2)
        # pygame.draw.rect(screen, self.r_col, self.right_sensor)
        # pygame.draw.rect(screen, self.l_col, self.left_sensor)
        # pygame.draw.rect(screen, self.l_col, self.up_sensor)

    def move(self):
        global jumping, falling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not jumping and not falling:
            jumping = True
        if keys[pygame.K_a] or keys[pygame.K_d]:
            if self.tick == 0:
                self.frame = 1 + self.frame % 4
                self.tick = 5
            else:
                self.tick -= 1
            self.img = pygame.image.load(walk_frames[self.frame])
            if self.dir == -1:
                self.img = pygame.transform.flip(self.img, True, False)
            if keys[pygame.K_a]:
                if self.dir != -1:
                    self.dir = -1
                if not self.can_move_left:
                    return False
            elif keys[pygame.K_d]:
                if self.dir != 1:
                    self.dir = 1
                if not self.can_move_right:
                    return False
            return self.dir
        else:
            self.img = pygame.image.load("idle.png")
            if self.dir == -1:
                self.img = pygame.transform.flip(self.img, True, False)
            return 0

    def find_floor(self):
        finder_depth = 5
        searching_for_floor = True
        while searching_for_floor:
            floor_finder = pygame.Rect(PLAYER_HITBOX.x, PLAYER_HITBOX.y, PLAYER_HITBOX.width, finder_depth)
            for column in terrain.blocks:
                for block in column:
                    if not block.destroyed and block.rect.colliderect(floor_finder):
                        floor = block.is_floor()
                        return floor
            finder_depth += 50
            if finder_depth > 10000:
                searching_for_floor = False

    def movement_options(self):
        self.l_col = (255, 0, 255)
        self.r_col = (255, 255, 255)
        self.can_move_up = True
        self.can_move_left = True
        self.can_move_right = True
        for column in terrain.blocks:
            for block in column:
                if not block.destroyed:
                    if block.rect.colliderect(self.left_sensor):
                        self.can_move_left = False
                        self.l_col = (0, 0, 0)
                    if block.rect.colliderect(self.right_sensor):
                        self.can_move_right = False
                        self.r_col = (0, 0, 0)
                    if block.rect.colliderect(self.up_sensor):
                        self.can_move_up = False


player = Player()


# player x dimension: 60
# player y dimension: 80


class Block:
    def __init__(self, block_type, pos):
        self.location = (0,0)
        self.breaking = 0
        self.destroyed = True
        if block_type != "air":
            self.destroyed = False
        self.block_type = block_type
        self.img = pygame.image.load(self.block_type + ".png")
        self.img = pygame.transform.scale(self.img, (BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT))
        self.pos = pos
        self.draw(0, 0)
        if block_type == "grass" or block_type == "dirt":
            self.break_time = 100 / player.shovel_power
        elif block_type == "stone":
            self.break_time = 400 / player.pickaxe_power

    def draw(self, x_pos, y_pos):
        global mouse_pos, selected_block
        self.location = ((self.pos["x"] * BLOCK_WIDTH_HEIGHT) - x_pos, (self.pos["y"] * BLOCK_WIDTH_HEIGHT) + SEA_LEVEL -
                        y_pos)
        if not self.destroyed:
            screen.blit(self.img, self.location)
            self.rect = pygame.Rect(self.location[0], self.location[1], BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)
            # pygame.draw.rect(screen, 000000, self.rect, 2)
            if self.breaking > 0:
                self.breaking -= 1
                if self.breaking > self.break_time * 0.8:
                    screen.blit(pygame.image.load("break_3.png"), self.rect)
                elif self.breaking > self.break_time * 0.6:
                    screen.blit(pygame.image.load("break_2.png"), self.rect)
                elif self.breaking > self.break_time * 0.4:
                    screen.blit(pygame.image.load("break_1.png"), self.rect)
                elif self.breaking > self.break_time * 0.2:
                    screen.blit(pygame.image.load("break_0.png"), self.rect)
            if self.rect.x < mouse_pos[0] < self.rect.x + BLOCK_WIDTH_HEIGHT:
                if self.rect.y < mouse_pos[1] < self.rect.y + BLOCK_WIDTH_HEIGHT:
                    selected_block = self.rect
        else:
            self.rect = None
            air_rect = pygame.Rect(self.location[0], self.location[1], BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)
            if air_rect.x < mouse_pos[0] < air_rect.x + BLOCK_WIDTH_HEIGHT:
                if air_rect.y < mouse_pos[1] < air_rect.y + BLOCK_WIDTH_HEIGHT:
                    selected_block = air_rect

    def destroy(self):
        self.breaking += 2
        if self.breaking > self.break_time:
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
                self.block_height = WORLD_DEPTH - d
                if d - depth[w] == -1:
                    column.append(Block("grass", {"x": w, "y": self.block_height}))
                elif d >= depth[w] - dirt_thickness:
                    column.append(Block("dirt", {"x": w, "y": self.block_height}))
                elif WORLD_DEPTH >= d < depth[w] - dirt_thickness:
                    column.append(Block("stone", {"x": w, "y": self.block_height}))
            while self.block_height > -6:
                self.block_height -= 1
                column.append(Block("air", {"x": w, "y": self.block_height}))
            self.blocks.append(column)

    def draw(self, x, y):
        for column in self.blocks:
            for block in column:
                block.draw(x, y)


class ClickHandler:
    def __init__(self):
        self.in_range = True
        pass

    def update_mouse(self):
        global mouse_pos
        mouse_pos = pygame.mouse.get_pos()
        mouse_vector = math.dist(mouse_pos, PLAYER_CENTER)
        if mouse_vector <= 250:
            self.in_range = True
        else:
            self.in_range = False

    def check_clicks(self):
        if pygame.mouse.get_pressed()[0]:
            self.left_click()
            return 0
        if pygame.mouse.get_pressed()[2]:
            # return value of 1 means right_click
            return 1

    def left_click(self):
        global mouse_pos
        mouse_pos = pygame.mouse.get_pos()
        for column in terrain.blocks:
            for block in column:
                if block.rect and self.in_range:
                    if block.rect.x < mouse_pos[0] < block.rect.x + BLOCK_WIDTH_HEIGHT:
                        if block.rect.y < mouse_pos[1] < block.rect.y + BLOCK_WIDTH_HEIGHT:
                            block.destroy()
                            return block
        return False


# Terrain generation shenanigans

seed = random.randint(0, 20000)
noise = PerlinNoise(octaves=3, seed=seed)
height_map = []
for i in range(WORLD_WIDTH):
    height = NOISE_CONSTANT * noise([i / WORLD_WIDTH])
    height = round(height)
    height_map.append(WORLD_DEPTH + height)

Click_Handler = ClickHandler()
terrain = Terrain(WORLD_WIDTH, height_map)

terrain_x = 0
terrain_y = -80

# Game loop

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    Click_Handler.update_mouse()
    mouse_input = Click_Handler.check_clicks()

    player.movement_options()
    can_move_up = player.can_move_up
    move_dir = player.move()
    floor_block = player.find_floor()
    floor_collision = floor_block.colliderect(PLAYER_HITBOX)
    if not floor_collision and not jumping:
        falling = True
    if jumping:
        if can_move_up:
            terrain_y -= Y_VELOCITY
        else:
            Y_VELOCITY = 0
        Y_VELOCITY -= GRAVITY
        if Y_VELOCITY < 0:
            falling = True
            jumping = False
            Y_VELOCITY = JUMP_HEIGHT
    if falling and can_move_up:
        if (floor_block.top - FALL_VELOCITY) > PLAYER_HITBOX.bottom:
            terrain_y += FALL_VELOCITY
            if FALL_VELOCITY < TERMINAL_VELOCITY:
                FALL_VELOCITY += 2
        else:
            terrain_y += (floor_block.top - PLAYER_HITBOX.bottom)
            FALL_VELOCITY = 0
            Y_VELOCITY = JUMP_HEIGHT
            falling = False
    elif falling and not can_move_up:
        terrain_y += 5
    if move_dir:
        terrain_x += 10 * move_dir
    screen.fill(bg_color)
    terrain.draw(terrain_x, terrain_y)
    player.draw()
    if Click_Handler.in_range:
        pygame.draw.rect(screen, (255, 255, 255), selected_block, 3)
    pygame.display.flip()
    clock.tick(60)
