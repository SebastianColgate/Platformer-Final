from raylib import *
from pyray import *

from helpers import find_touching_liquid_tile, create_liquid_spread, rect_touches_tile
from settings import (
    ENEMY_SPEED,
    EXIT_LIQUID_VELOCITY,
    GRAVITY,
    JAR_HEIGHT,
    JAR_WIDTH,
    JUMP_VELOCITY,
    MOVING_PLATFORM_HEIGHT,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_SWIM_HEIGHT,
    PLAYER_SWIM_WIDTH,
    PLAYER_WIDTH,
    STOMP_BOUNCE,
    SWIM_SPEED,
    SWIM_VELOCITY,
    TILE_POISON_WATER,
    TILE_SIZE,
    TILE_SOLID,
    TILE_WATER,
    TILE_ROWS,
    TILE_COLS,
    WATER_GRAVITY,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from sprites import draw_sprite, draw_sprite_keep_height




class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y

        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_swimming = False
        self.facing_right = True
        self.stomp_bounce = STOMP_BOUNCE
        
        self.animation_timer = 0.0
        self.animation_frame = 0
        self.swim_kick_timer = 0.0
        self.is_pushing = False

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)


    def get_liquid_sensor_rect(self):
        sensor_width = TILE_SIZE * 0.5
        sensor_height = TILE_SIZE * 0.5
        center_x = self.x + self.width / 2
        bottom_y = self.y + self.height
        return (
            center_x - sensor_width / 2,
            bottom_y - sensor_height,
            sensor_width,
            sensor_height,
        )

    def change_swim_mode(self, swimming, level=None):
        if self.is_swimming == swimming:
            return

        old_center_x = self.x + self.width / 2
        old_bottom = self.y + self.height

        if swimming:
            new_width = PLAYER_SWIM_WIDTH
            new_height = PLAYER_SWIM_HEIGHT
        else:
            new_width = PLAYER_WIDTH
            new_height = PLAYER_HEIGHT

        new_x = old_center_x - new_width / 2
        new_y = old_bottom - new_height

        if level is not None:
            found_safe_spot = False
            test_offsets = [0]
            for offset in range(2, TILE_SIZE + 1, 2):
                test_offsets.append(-offset)
                test_offsets.append(offset)

            for offset in test_offsets:
                test_x = new_x + offset
                test_x = max(0, min(test_x, WORLD_WIDTH - new_width))
                test_rect = (test_x, new_y, new_width, new_height)
                if not rect_touches_tile(test_rect, level, TILE_SOLID):
                    new_x = test_x
                    found_safe_spot = True
                    break

            if not found_safe_spot:
                return

        self.is_swimming = swimming
        self.width = new_width
        self.height = new_height
        self.x = new_x
        self.y = new_y

    def is_touching_tile(self, level, tile_type):
        return rect_touches_tile(self.get_rect(), level, tile_type)

    def is_in_liquid(self, level):
        return rect_touches_tile(self.get_liquid_sensor_rect(), level, (TILE_WATER, TILE_POISON_WATER))

    def check_enemy_collision(self, enemies):
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect

        for index, enemy in enumerate(enemies):
            enemy_rect = enemy.get_rect()
            
            if CheckCollisionRecs(player_rect, enemy_rect):
                is_stompable_zone = py + ph < enemy.y + enemy.height * 0.5
                if self.vy > 0 and is_stompable_zone:
                    return "STOMP", index
                return "LETHAL", index

        return None, -1


    def update(self, delta_time, level, solid_objects=None):
        if solid_objects is None:
            solid_objects = []

        self.is_pushing = False

        #changes mode on liquid state change
        was_in_liquid = self.is_swimming
        self.change_swim_mode(self.is_in_liquid(level), level)

        self.vx = 0.0
        current_speed = SWIM_SPEED if self.is_swimming else PLAYER_SPEED

        moving_left = IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A)
        moving_right = IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D)

        if moving_left:
            self.vx = -current_speed
        if moving_right:
            self.vx = current_speed
        if self.vx < 0:
            self.facing_right = False
        elif self.vx > 0:
            self.facing_right = True

        if self.is_grounded and not self.is_swimming:
            self.vy = 0.0


        #water updates
        if self.is_swimming:
            swim_up_pressed = IsKeyPressed(KEY_SPACE) or IsKeyPressed(KEY_UP) or IsKeyPressed(KEY_W)
            swim_down_held = IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S)

            if moving_left or moving_right or swim_up_pressed or swim_down_held:
                self.swim_kick_timer = 0.25

            if swim_up_pressed:
                self.vy = SWIM_VELOCITY
            elif swim_down_held:
                self.vy = SWIM_SPEED
            else:
                self.vy *= 0.9

            self.vy += WATER_GRAVITY * delta_time
            if self.vy > 250:
                self.vy = 250
        
        #land updates
        else:
            if (IsKeyPressed(KEY_SPACE) or IsKeyPressed(KEY_UP)) and self.is_grounded:
                self.vy = JUMP_VELOCITY

            self.vy += GRAVITY * delta_time
            if self.vy > 1000:
                self.vy = 1000

        self.is_grounded = False
        self.x += self.vx * delta_time
        self.handle_tile_collision(level, "X")

        old_y = self.y
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")
        self.handle_object_collision(solid_objects, old_y)

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        self.y = min(self.y, WORLD_HEIGHT + TILE_SIZE)

        self.change_swim_mode(self.is_in_liquid(level), level)
        if was_in_liquid and not self.is_swimming and self.vy < 0:
            self.vy = EXIT_LIQUID_VELOCITY

        if self.swim_kick_timer > 0:
            self.swim_kick_timer -= delta_time

        self.update_animation(delta_time)


    def update_animation(self, delta_time):
        if self.is_swimming:
            is_moving = self.swim_kick_timer > 0
            frame_time = 0.3
        else:
            is_moving = self.is_grounded and abs(self.vx) > 1
            frame_time = 0.18

        if not is_moving:
            self.animation_timer = 0.0
            self.animation_frame = 0
            return

        self.animation_timer += delta_time
        if self.animation_timer >= frame_time:
            self.animation_timer = 0.0
            self.animation_frame = 1 - self.animation_frame

   
    def handle_tile_collision(self, level, axis):
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        #int rounding for simplicity
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                    continue
                if level[row][col] != TILE_SOLID:
                    continue

                tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if not CheckCollisionRecs(player_rect, tile_rect):
                    continue

                if axis == "X":
                    if self.vx > 0:
                        self.x = tile_rect[0] - self.width
                    elif self.vx < 0:
                        self.x = tile_rect[0] + TILE_SIZE
                    self.vx = 0.0

                else:
                    if self.vy >= 0:
                        self.y = tile_rect[1] - self.height
                        self.is_grounded = True
                    else:
                        self.y = tile_rect[1] + TILE_SIZE
                    self.vy = 0.0

                player_rect = self.get_rect()


    #seperate collision for "physics" objects (jars)
    def handle_object_collision(self, objects, old_y):
        player_rect = self.get_rect()
        old_top = old_y
        old_bottom = old_y + self.height

        for obj in objects:
            if getattr(obj, "is_broken", False):
                continue

            obj_rect = obj.get_rect()
            if not CheckCollisionRecs(player_rect, obj_rect):
                continue

            obj_y = obj_rect[1]
            obj_bottom = obj_rect[1] + obj_rect[3]

            if self.vy >= 0 and old_bottom <= obj_y:
                self.y = obj_y - self.height
                self.is_grounded = True
                self.vy = 0.0
            elif self.vy < 0 and old_top >= obj_bottom:
                self.y = obj_bottom
                self.vy = 0.0
            else:
                continue

            player_rect = self.get_rect()

    def draw(self):
        center_x = self.x + self.width / 2
        bottom_y = self.y + self.height

        if self.is_swimming:
            swim_rotation = -10.0 if self.facing_right else 10.0
            if self.animation_frame == 0:
                draw_sprite_keep_height("player_swim_idle", center_x, bottom_y, self.height, not self.facing_right, swim_rotation)
            else:
                draw_sprite_keep_height("player_swim_kick", center_x, bottom_y, self.height, not self.facing_right, swim_rotation)
        elif not self.is_grounded:
            draw_width = self.height * 0.65
            draw_x = self.x + (self.width - draw_width) / 2
            draw_sprite("player_jump", draw_x, self.y, draw_width, self.height, not self.facing_right)
        elif abs(self.vx) > 1 or self.is_pushing:
            if self.animation_frame == 0:
                draw_sprite_keep_height("player_stand", center_x, bottom_y, self.height, not self.facing_right)
            else:
                draw_sprite_keep_height("player_walk", center_x, bottom_y, self.height, not self.facing_right)
        else:
            draw_sprite_keep_height("player_stand", center_x, bottom_y, self.height, not self.facing_right)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_swimming = False
        self.facing_right = True
        self.animation_timer = 0.0
        self.animation_frame = 0
        self.swim_kick_timer = 0.0
        self.is_pushing = False

class Enemy:
    def __init__(self, x, y, kind="land"):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.9
        self.height = TILE_SIZE * 0.9

        self.kind = kind

        self.vx = ENEMY_SPEED
        self.vy = 0.0
        self.is_grounded = False
        self.animation_timer = 0.0
        self.animation_frame = 0

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def is_poisoned(self, level):
        return rect_touches_tile(self.get_rect(), level, TILE_POISON_WATER)

    def update(self, delta_time, level):
        if self.kind == "water":
            self.update_water_enemy(delta_time, level)
        else:
            self.update_land_enemy(delta_time, level)

    def update_land_enemy(self, delta_time, level):
        if self.is_grounded:
            self.vy = 0.0

        self.vy += GRAVITY * delta_time
        self.is_grounded = False

        self.x += self.vx * delta_time
        self.handle_tile_collision(level, "X")

        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))

    def update_water_enemy(self, delta_time, level):
        # Water enemies float/swim instead of falling.
        self.vy = 0.0
        self.animation_timer += delta_time
        if self.animation_timer >= 0.45:
            self.animation_timer = 0.0
            self.animation_frame = 1 - self.animation_frame

        self.x += self.vx * delta_time

        # If it hits a wall, turn around.
        if rect_touches_tile(self.get_rect(), level, TILE_SOLID):
            self.x -= self.vx * delta_time
            self.vx *= -1

        # If it starts leaving the water, turn around.
        if not rect_touches_tile(self.get_rect(), level, (TILE_WATER, TILE_POISON_WATER)):
            self.x -= self.vx * delta_time
            self.vx *= -1

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))

    def handle_tile_collision(self, level, axis):
        enemy_rect = self.get_rect()
        px, py, pw, ph = enemy_rect
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                    continue
                if level[row][col] != TILE_SOLID:
                    continue

                tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if not CheckCollisionRecs(enemy_rect, tile_rect):
                    continue

                if axis == "X":
                    if self.vx > 0:
                        self.x = tile_rect[0] - self.width
                    elif self.vx < 0:
                        self.x = tile_rect[0] + TILE_SIZE
                    self.vx *= -1
                else:
                    if self.vy >= 0:
                        self.y = tile_rect[1] - self.height
                        self.is_grounded = True
                    self.vy = 0.0

                enemy_rect = self.get_rect()

    def draw(self):
        flip_x = self.vx < 0
        if self.kind == "water":
            if self.animation_frame == 0:
                draw_sprite("water_enemy_1", self.x, self.y, self.width, self.height, flip_x)
            else:
                draw_sprite("water_enemy_2", self.x, self.y, self.width, self.height, flip_x)
        else:
            draw_sprite("enemy", self.x, self.y, self.width, self.height, flip_x)


#New, needs collision work
class MovingPlatform:
    def __init__(self, start_x, start_y, end_x, end_y, width, speed):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = MOVING_PLATFORM_HEIGHT
        self.speed = speed

        self.dx = 0.0
        self.dy = 0.0

        if self.start_x != self.end_x:
            self.direction = 1 if self.end_x > self.start_x else -1
        else:
            self.direction = 1 if self.end_y > self.start_y else -1

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def is_carrying(self, obj, old_x, old_y):
        #handy to check for jars
        if getattr(obj, "is_broken", False):
            return False

        obj_x, obj_y, obj_width, obj_height = obj.get_rect()
        obj_bottom = obj_y + obj_height

        overlaps_x = obj_x + obj_width > old_x and obj_x < old_x + self.width
        is_on_top = old_y - 3 <= obj_bottom <= old_y + 5
        return overlaps_x and is_on_top

    #basically just moves back and forth, checking when it should switch
    def update(self, delta_time, riders):
        old_x = self.x
        old_y = self.y

        if self.start_x != self.end_x:
            self.x += self.direction * self.speed * delta_time

            left_point = min(self.start_x, self.end_x)
            right_point = max(self.start_x, self.end_x)
            if self.x <= left_point:
                self.x = left_point
                self.direction = 1
            elif self.x >= right_point:
                self.x = right_point
                self.direction = -1
        else:
            self.y += self.direction * self.speed * delta_time

            top_point = min(self.start_y, self.end_y)
            bottom_point = max(self.start_y, self.end_y)
            if self.y <= top_point:
                self.y = top_point
                self.direction = 1
            elif self.y >= bottom_point:
                self.y = bottom_point
                self.direction = -1

        self.dx = self.x - old_x
        self.dy = self.y - old_y

        #Makes things on it move with it
        for obj in riders:
            if self.is_carrying(obj, old_x, old_y):
                obj.x += self.dx
                obj.y += self.dy

    def draw(self):
        draw_sprite("moving_platform", self.x, self.y, self.width, self.height)


class ChemicalJar:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.width = JAR_WIDTH
        self.height = JAR_HEIGHT

        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_broken = False

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    #checks for proper breaking open
    def try_break(self, level):
        row, col, _ = find_touching_liquid_tile(self.get_rect(), level)

        if row is None:
            return None

        self.is_broken = True

        if self.kind == "poison":
            return create_liquid_spread(level, row, col, TILE_WATER, TILE_POISON_WATER)
        else:
            return create_liquid_spread(level, row, col, TILE_POISON_WATER, TILE_WATER)

    #when moved by player, pushed around. 
    def push(self, player, delta_time, level):
        if self.is_broken or player.vx == 0.0:
            return

        if not CheckCollisionRecs(player.get_rect(), self.get_rect()):
            return

        direction = 1 if player.vx > 0 else -1
        push_speed = abs(player.vx)

        next_x = self.x + direction * push_speed * delta_time
        next_rect = (next_x, self.y, self.width, self.height)

        if not rect_touches_tile(next_rect, level, TILE_SOLID):
            self.x = next_x

        self.vx = 0.0

        if direction > 0:
            player.x = self.x - player.width
        else:
            player.x = self.x + self.width

        player.is_pushing = True
        player.vx = 0.0


    def update(self, delta_time, level, solid_objects=None):
        if solid_objects is None:
            solid_objects = []

        if self.is_broken:
            return None

        if self.is_grounded:
            self.vx *= 0.82

            if abs(self.vx) < 5.0:
                self.vx = 0.0

        self.vy += GRAVITY * delta_time

        if self.vy > 1000:
            self.vy = 1000

        self.is_grounded = False

        self.x += self.vx * delta_time
        self.handle_tile_collision(level, "X")

        old_y = self.y
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")
        self.handle_object_collision(solid_objects, old_y)

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))

        return self.try_break(level)

    def handle_tile_collision(self, level, axis):
        jar_rect = self.get_rect()
        px, py, pw, ph = jar_rect

        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                    continue

                if level[row][col] != TILE_SOLID:
                    continue

                tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if not CheckCollisionRecs(jar_rect, tile_rect):
                    continue

                if axis == "X":
                    if self.vx > 0:
                        self.x = tile_rect[0] - self.width
                    elif self.vx < 0:
                        self.x = tile_rect[0] + TILE_SIZE

                    self.vx = 0.0

                else:
                    if self.vy >= 0:
                        self.y = tile_rect[1] - self.height
                        self.is_grounded = True
                    else:
                        self.y = tile_rect[1] + TILE_SIZE

                    self.vy = 0.0

                jar_rect = self.get_rect()

    def handle_object_collision(self, objects, old_y):
        jar_rect = self.get_rect()

        old_top = old_y
        old_bottom = old_y + self.height

        for obj in objects:
            obj_rect = obj.get_rect()

            if not CheckCollisionRecs(jar_rect, obj_rect):
                continue

            obj_y = obj_rect[1]
            obj_bottom = obj_rect[1] + obj_rect[3]

            if self.vy >= 0 and old_bottom <= obj_y:
                self.y = obj_y - self.height
                self.is_grounded = True
                self.vy = 0.0

            elif self.vy < 0 and old_top >= obj_bottom:
                self.y = obj_bottom
                self.vy = 0.0

            else:
                continue

            jar_rect = self.get_rect()

    def draw(self):
        if self.is_broken:
            return

        if self.kind == "poison":
            draw_sprite("poison_jar", self.x, self.y, self.width, self.height)
        else:
            draw_sprite("antidote_jar", self.x, self.y, self.width, self.height)
