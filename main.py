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
ITEM_WIDTH_HEIGHT = 25
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
items = []
font = pygame.font.Font("MinecraftRegular-Bmg3.otf", 24)
scroll = 0
sediments = ["dirt", "grass"]
stones = ["stone"]
bg_objects = ["tallgrass", "poppy", "tulip", "cornflower"]
wood = ["oak_log"]
weak_blocks = ["oak_leaf"]


# some comment I've added to test git

class Player:

    def __init__(self):
        self.inventory = {}
        self.selected = 0
        self.i_frames = 60

        self.health_regen = 0
        self.health = 10
        self.fall_counter = 0

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
                    if (not block.destroyed and block.rect.colliderect(floor_finder) and block.block_type not in
                            bg_objects):
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
                if not block.destroyed and block.block_type not in bg_objects:
                    if block.rect.colliderect(self.left_sensor):
                        self.can_move_left = False
                        self.l_col = (0, 0, 0)
                    if block.rect.colliderect(self.right_sensor):
                        self.can_move_right = False
                        self.r_col = (0, 0, 0)
                    if block.rect.colliderect(self.up_sensor):
                        self.can_move_up = False

    def health_bar(self):
        half_heart = False
        num_hearts = self.health / 2
        half_heart_img = pygame.image.load("half_heart.png")
        full_heart_img = pygame.image.load("full_heart.png")
        if not num_hearts.is_integer():
            num_hearts -= 0.5
            half_heart = True
        pos = 550
        for i in range(int(num_hearts)):
            screen.blit(full_heart_img, (pos, 20))
            pos += 45
        if half_heart:
            screen.blit(half_heart_img, (pos, 20))
        if self.health < 10:
            self.health_regen += 1
        if self.health_regen == 100:
            self.health += 1
            self.health_regen = 0

    def hotbar(self, scroll):
        hotbar_img = pygame.image.load("inventory_slot.png")
        selected_hotbar_img = pygame.image.load("selected_slot.png")
        hotbar_pos = 20
        self.selected = (scroll + self.selected) % 9
        for i in range(9):
            if i == self.selected:
                screen.blit(selected_hotbar_img, (hotbar_pos, 20))
            else:
                screen.blit(hotbar_img, (hotbar_pos, 20))
            hotbar_pos += 45
        item_pos = 32
        keys = self.inventory.keys()
        for item in keys:
            if self.inventory[item][0] <= 9:
                offset = 5.5
            else:
                offset = 0.5
            text = font.render(str(self.inventory[item][0]), True, (0, 0, 0))
            screen.blit(self.inventory[item][1], (item_pos, 32))
            screen.blit(text, (item_pos + offset, 70))
            item_pos += 45

    def inventory_manager(self):
        del_list = []
        keys = self.inventory.keys()
        for item in keys:
            if self.inventory[item][0] <= 0:
                del_list.append(item)
        for item in del_list:
            del self.inventory[item]


    def damage_check(self):
        if falling:
            self.fall_counter += 1
        else:
            if self.i_frames == 0:
                damage = self.fall_counter // 25
                self.health -= damage
                self.fall_counter = 0
                return True
            else:
                self.fall_counter = 0
        if self.i_frames > 0:
            self.i_frames -= 1


player = Player()


# player x dimension: 60
# player y dimension: 80


class Block:
    def __init__(self, block_type, pos):
        self.location = (0, 0)
        self.breaking = 0
        self.destroyed = True
        if block_type != "air":
            self.destroyed = False
        self.block_type = block_type
        self.img = pygame.image.load(self.block_type + ".png")
        self.img = pygame.transform.scale(self.img, (BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT))
        self.pos = pos
        self.draw(0, 0)
        if block_type in sediments:
            self.break_time = 100 / player.shovel_power
        elif block_type in stones:
            self.break_time = 400 / player.pickaxe_power
        elif block_type in bg_objects or block_type in weak_blocks:
            self.break_time = 10
        elif block_type in wood:
            self.break_time = 200 / player.axe_power

    def draw(self, x_pos, y_pos):
        global mouse_pos, selected_block
        self.location = (
            (self.pos["x"] * BLOCK_WIDTH_HEIGHT) - x_pos, (self.pos["y"] * BLOCK_WIDTH_HEIGHT) + SEA_LEVEL -
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
                    selected_block = (self.rect, self)
        else:
            self.rect = None
            self.air_rect = pygame.Rect(self.location[0], self.location[1], BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)
            if self.air_rect.x < mouse_pos[0] < self.air_rect.x + BLOCK_WIDTH_HEIGHT:
                if self.air_rect.y < mouse_pos[1] < self.air_rect.y + BLOCK_WIDTH_HEIGHT:
                    if not self.air_rect.colliderect(PLAYER_HITBOX):
                        selected_block = (self.air_rect, self)

    def destroy(self, block):
        self.breaking += 2
        if self.breaking > self.break_time:
            Item(self.block_type, self.pos["x"], self.pos["y"])
            self.img = pygame.image.load(block + ".png")
            self.destroyed = True

    def place(self, temp):
        if temp == 0:
            try:
                key = list(player.inventory.keys())[player.selected]
            except IndexError:
                return
        else:
            key = temp
        if self.destroyed:
            self.destroyed = False
            self.rect = pygame.Rect(self.location[0], self.location[1], BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)
            self.img = pygame.image.load(str(key) + ".png")
            self.img = pygame.transform.scale(self.img, (BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT))
            self.block_type = key
            if self.block_type in sediments:
                self.break_time = 100 / player.shovel_power
            elif self.block_type in stones:
                self.break_time = 400 / player.pickaxe_power
            elif self.block_type in bg_objects or self.block_type in weak_blocks:
                self.break_time = 10
            elif self.block_type in wood:
                self.break_time = 200 / player.axe_power
            if temp == 0:
                player.inventory[key][0] -= 1
    def is_floor(self):
        return self.rect


selected_block = ((0, 0, 0, 0), Block("grass", {"x": 10000, "y": 10000}))


class Terrain:
    def __init__(self, width, depth):
        self.blocks = []
        for w in range(width):
            column = []
            terrain_rand = random.randint(1, 20)
            dirt_thickness = random.randint(3, 4)
            for d in range(depth[w]):
                self.block_height = WORLD_DEPTH - d
                if d - depth[w] == -1:
                    column.append(Block("grass", {"x": w, "y": self.block_height}))
                elif d >= depth[w] - dirt_thickness:
                    column.append(Block("dirt", {"x": w, "y": self.block_height}))
                elif WORLD_DEPTH >= d < depth[w] - dirt_thickness:
                    column.append(Block("stone", {"x": w, "y": self.block_height}))
            while self.block_height > -15:
                self.block_height -= 1
                if 0 < terrain_rand <= 6:
                    column.append(Block("tallgrass", {"x": w, "y": self.block_height}))
                elif 6 < terrain_rand <= 8:
                    column.append(Block("poppy", {"x": w, "y": self.block_height}))
                elif 8 < terrain_rand <= 10:
                    column.append(Block("tulip", {"x": w, "y": self.block_height}))
                elif 10 < terrain_rand <= 12:
                    column.append(Block("cornflower", {"x": w, "y": self.block_height}))
                elif 12 < terrain_rand <= 14:
                    column.append(Block("oak_log", {"x": w, "y": self.block_height}))
                else:
                    column.append(Block("air", {"x": w, "y": self.block_height}))
                self.block_height -= 1
                terrain_rand = 0
                column.append(Block("air", {"x": w, "y": self.block_height}))
            self.blocks.append(column)
        self.tree_constructor()

    def tree_constructor(self):
        tree_blocks = []
        for i in range(len(self.blocks)):
            column = self.blocks[i]
            for j in range(len(column)):
                block = column[j]
                if block.block_type == "oak_log" and block not in tree_blocks:
                    rand = random.randint(4, 7)
                    for k in range(rand):
                        if j + k < len(column) - 1:
                            if k < rand - 3:
                                (self.blocks[i][j+k]).place("oak_log")
                                tree_blocks.append(self.blocks[i][j + k])
                            elif k < rand - 1:
                                if i-1 >= 0:
                                    (self.blocks[i-1][j + k]).place("oak_leaf")
                                (self.blocks[i][j + k]).place("oak_leaf")
                                if i+1 < len(self.blocks):
                                    (self.blocks[i+1][j + k]).place("oak_leaf")
                            else:
                                (self.blocks[i][j + k]).place("oak_leaf")



    def draw(self, x, y):
        for column in self.blocks:
            for block in column:
                block.draw(x, y)
        for item in items:
            item.draw(x, y)
            item.pick_up()


class Item:
    def __init__(self, origin_tile, origin_x, origin_y):
        self.origin = origin_tile
        self.visible = True
        self.rect = (0, 0, 0, 0)
        self.bob = 1
        self.bobbing = 0
        self.location = (origin_x, origin_y)
        items.append(self)
        self.img = pygame.image.load(origin_tile + ".png")
        self.img = pygame.transform.scale(self.img, (ITEM_WIDTH_HEIGHT, ITEM_WIDTH_HEIGHT))

    def draw(self, x_pos, y_pos):
        if self.visible:
            self.bobbing += 0.25 * self.bob
            if abs(self.bobbing) == 3:
                self.bob *= -1
            location = (self.location[0] * BLOCK_WIDTH_HEIGHT + ITEM_WIDTH_HEIGHT / 2 - x_pos, self.location[1] *
                        BLOCK_WIDTH_HEIGHT + SEA_LEVEL + self.bobbing + ITEM_WIDTH_HEIGHT / 2 - y_pos)
            screen.blit(self.img, location)
            self.rect = pygame.Rect(location[0] - ITEM_WIDTH_HEIGHT / 2, location[1] - ITEM_WIDTH_HEIGHT / 2,
                                    BLOCK_WIDTH_HEIGHT, BLOCK_WIDTH_HEIGHT)

    def pick_up(self):
        if self.rect.colliderect(PLAYER_HITBOX) and self.visible:
            if self.origin not in player.inventory.keys():
                player.inventory[self.origin] = [1, self.img]
            else:
                player.inventory[self.origin][0] += 1
            self.visible = False


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
        global selected_block
        if pygame.mouse.get_pressed()[0]:
            if selected_block[1].rect:
                selected_block[1].destroy("air")
            return 0
        if pygame.mouse.get_pressed()[2]:
            selected_block[1].place(0)
            return 1


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
terrain_y = -500

# Game loop

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            scroll = -1 * event.y

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
    player.damage_check()
    player.health_bar()
    player.inventory_manager()
    player.hotbar(scroll)
    scroll = 0
    if Click_Handler.in_range:
        pygame.draw.rect(screen, (255, 255, 255), selected_block[0], 3)
    pygame.display.flip()

    clock.tick(60)
