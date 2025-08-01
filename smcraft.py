import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("S.mCraft")
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 7

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOUR = ("#000000")   
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Characters", "Character1", 32, 32, True)
    ANIMATION_DELAY = 3
    
    def __init__ (self, x, y, width, height):
        super().__init__()
        self.rect=pygame.Rect(x, y, width, height)
        self.x_vel=0
        self.y_vel=0
        self.mask=None
        self.direction="left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def make_hit(self):
        self.hit = True

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 1:
            self.hit = False
            self.hit_count = 0
            

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "Character1"
        if self.hit:
            sprite_sheet = "Hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "Jump"
            elif self.jump_count == 2:
                sprite_sheet = "Double_Jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "Fall"
        elif self.x_vel != 0:
            sprite_sheet = "Running"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite) 
            

    def draw(self, win, offset_x):
        win.blit(self.sprite,(self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Flag(Object):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "flag")
        self.flag = load_sprite_sheets("Level Stuff", "Flag", width, height)
        self.image = self.flag["flag1"][0]
        self.mask = pygame.mask.from_surface(self.image)

class Pillager(Object):
    ANIMATION_DELAY = 7

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "pillager")
        self.pillager = load_sprite_sheets("Monsters", "Pillager", width, height)
        self.image = self.pillager["Closed"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Closed"

    def move(self):
        self.animation_name = "move"

    def Closed(self):
        self.animation_name = "Closed"

    def loop(self):
        sprites = self.pillager[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width, height = image.get_rect()
    tiles=[]

    for i in range(WIDTH//width+1):
        for j in range (HEIGHT//height+1):
            pos=(i*width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object                
            

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "pillager":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("backgroundjt.png")
    
    block_size = 96
    flag = Flag(3900, HEIGHT - block_size*4 - 64, 16, 33)

    player = Player(100, 100, 50, 50)
    pillager = Pillager(700, HEIGHT - block_size - 64, 16, 33)
    pillager.move()
    floor = [Block(i*block_size, HEIGHT - block_size, block_size)for i in range(-WIDTH// block_size, WIDTH*2// block_size)]

    objects = [*floor, Block(block_size*0, HEIGHT - block_size*6, block_size), Block(block_size*1, HEIGHT - block_size*6, block_size)
                , Block(block_size*2, HEIGHT - block_size*6, block_size), Block(block_size*4, HEIGHT - block_size*4, block_size)
                    , Block(block_size*10, HEIGHT - block_size*3, block_size), Block(block_size*12, HEIGHT - block_size*4, block_size)
                        , Block(block_size*13, HEIGHT - block_size*4, block_size), Block(block_size*14, HEIGHT - block_size*4, block_size)
                            , Block(block_size*18, HEIGHT - block_size*5, block_size), Block(block_size*21, HEIGHT - block_size*4, block_size)
                                , Block(block_size*22, HEIGHT - block_size*4, block_size), Block(block_size*25, HEIGHT - block_size*5, block_size)
                                   , Block(block_size*24, HEIGHT - block_size*1, block_size), Block(block_size*26, HEIGHT - block_size*3, block_size)
                                        , Block(block_size*27, HEIGHT - block_size*7, block_size), Block(block_size*28, HEIGHT - block_size*7, block_size)
                                            , Block(block_size*28, HEIGHT - block_size*5, block_size), Block(block_size*30, HEIGHT - block_size*4, block_size)
                                                ,Block(block_size*33, HEIGHT - block_size*5, block_size), Block(block_size*36, HEIGHT - block_size*7, block_size)
                                                   ,Block(block_size*37, HEIGHT - block_size*7, block_size),Block(block_size*35, HEIGHT - block_size*2, block_size)
                                                       , Block(block_size*36, HEIGHT - block_size*2, block_size), Block(block_size*37, HEIGHT - block_size*2, block_size)
                                                           ,Block(block_size*35, HEIGHT - block_size*1, block_size), Block(block_size*36, HEIGHT - block_size*1, block_size)
                                                               , Block(block_size*37, HEIGHT - block_size*1, block_size), Block(block_size*40, HEIGHT - block_size*4, block_size), pillager, flag]
                                                    

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count <2:
                    player.jump()
                    

        player.loop(FPS)
        pillager.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
