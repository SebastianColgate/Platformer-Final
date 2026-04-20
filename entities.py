from raylib import *
from pyray import *

from helpers import find_touching_liquid_tile, flood_fill_liquid, rect_touches_tile
from settings import (
    ENEMY_SPEED,
    EXIT_LIQUID_VELOCITY,
    GRAVITY,
    JAR_HEIGHT,
    JAR_PUSH_SPEED,
    JAR_WIDTH,
    JUMP_VELOCITY,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
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


# --- Game Object Classes ---

class Player:
    def __init__(self, x, y):
        # Store starting position for reset
        self.start_x = x
        self.start_y = y

        # Current position (top-left for collision)
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_swimming = False
        self.stomp_bounce = STOMP_BOUNCE

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def is_touching_tile(self, level, tile_type):
        return rect_touches_tile(self.get_rect(), level, tile_type)

    def is_in_liquid(self, level):
        return self.is_touching_tile(level, (TILE_WATER, TILE_POISON_WATER))

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

    def update(self, delta_time, level):
        was_in_liquid = self.is_swimming
        self.is_swimming = self.is_in_liquid(level)

        self.vx = 0.0
        current_speed = SWIM_SPEED if self.is_swimming else PLAYER_SPEED

        if IsKeyDown(KEY_LEFT) or IsKeyDown(KEY_A):
            self.vx = -current_speed
        if IsKeyDown(KEY_RIGHT) or IsKeyDown(KEY_D):
            self.vx = current_speed

        if self.is_grounded and not self.is_swimming:
            self.vy = 0.0

        if self.is_swimming:
            if IsKeyDown(KEY_SPACE) or IsKeyDown(KEY_UP) or IsKeyDown(KEY_W):
                self.vy = SWIM_VELOCITY
            elif IsKeyDown(KEY_DOWN) or IsKeyDown(KEY_S):
                self.vy = SWIM_SPEED
            else:
                self.vy *= 0.9

            self.vy += WATER_GRAVITY * delta_time
            if self.vy > 250:
                self.vy = 250
        else:
            if (IsKeyPressed(KEY_SPACE) or IsKeyPressed(KEY_UP)) and self.is_grounded:
                self.vy = JUMP_VELOCITY

            self.vy += GRAVITY * delta_time
            if self.vy > 1000:
                self.vy = 1000

        self.is_grounded = False

        self.x += self.vx * delta_time
        self.handle_tile_collision(level, "X")

        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        self.y = min(self.y, WORLD_HEIGHT + TILE_SIZE)

        self.is_swimming = self.is_in_liquid(level)
        if was_in_liquid and not self.is_swimming and self.vy < 0:
            self.vy = EXIT_LIQUID_VELOCITY

    def handle_tile_collision(self, level, axis):
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
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

    def draw(self):
        player_color = GREEN if self.is_swimming else BLUE
        DrawRectangle(int(self.x), int(self.y), int(self.width), int(self.height), player_color)
        outline = WHITE if self.is_grounded else DARKBLUE
        DrawRectangleLines(int(self.x), int(self.y), int(self.width), int(self.height), outline)

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_swimming = False


class Enemy:
    def __init__(self, x, y):
        # Position (top-left for collision)
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.7
        self.height = TILE_SIZE * 0.7

        # Physics/Movement
        self.vx = ENEMY_SPEED
        self.vy = 0.0
        self.is_grounded = False

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def is_poisoned(self, level):
        return rect_touches_tile(self.get_rect(), level, TILE_POISON_WATER)

    def update(self, delta_time, level):
        if self.is_grounded:
            self.vy = 0.0

        self.vy += GRAVITY * delta_time
        self.is_grounded = False

        self.x += self.vx * delta_time
        self.handle_tile_collision(level, "X")

        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")

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
        DrawRectangle(int(self.x), int(self.y), int(self.width), int(self.height), RED)
        DrawRectangleLines(int(self.x), int(self.y), int(self.width), int(self.height), BLACK)

        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        indicator_size = self.width * 0.2

        if self.vx > 0:
            DrawTriangle(
                Vector2(center_x + indicator_size, center_y),
                Vector2(center_x - indicator_size, center_y - indicator_size),
                Vector2(center_x - indicator_size, center_y + indicator_size),
                WHITE,
            )
        elif self.vx < 0:
            DrawTriangle(
                Vector2(center_x - indicator_size, center_y),
                Vector2(center_x + indicator_size, center_y - indicator_size),
                Vector2(center_x + indicator_size, center_y + indicator_size),
                WHITE,
            )


class ChemicalJar:
    def __init__(self, kind, x, y):
        # Position (top-left for collision)
        self.kind = kind
        self.x = x
        self.y = y
        self.width = JAR_WIDTH
        self.height = JAR_HEIGHT

        # Physics/State
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_broken = False

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def try_break(self, level):
        row, col, _ = find_touching_liquid_tile(self.get_rect(), level)
        if row is None:
            return False

        self.is_broken = True
        if self.kind == "poison":
            flood_fill_liquid(level, row, col, TILE_WATER, TILE_POISON_WATER)
        else:
            flood_fill_liquid(level, row, col, TILE_POISON_WATER, TILE_WATER)
        return True

    def push(self, player, delta_time, level):
        if self.is_broken or player.vx == 0.0:
            return
        if not CheckCollisionRecs(player.get_rect(), self.get_rect()):
            return

        direction = 1 if player.vx > 0 else -1
        next_x = self.x + direction * JAR_PUSH_SPEED * delta_time
        next_rect = (next_x, self.y, self.width, self.height)
        if not rect_touches_tile(next_rect, level, TILE_SOLID):
            self.x = next_x
            self.vx = direction * JAR_PUSH_SPEED

    def update(self, delta_time, level):
        if self.is_broken:
            return

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

        self.y += self.vy * delta_time
        self.handle_tile_collision(level, "Y")

        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        self.try_break(level)

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

    def draw(self):
        if self.is_broken:
            return

        box_x = int(self.x)
        box_y = int(self.y)
        box_w = int(self.width)
        box_h = int(self.height)

        if self.kind == "poison":
            DrawRectangle(box_x, box_y, box_w, box_h, PURPLE)
            DrawRectangleLines(box_x, box_y, box_w, box_h, WHITE)
            DrawText(b"P", box_x + box_w // 2 - 6, box_y + box_h // 2 - 10, 22, WHITE)
        else:
            DrawRectangle(box_x, box_y, box_w, box_h, LIGHTGRAY)
            DrawRectangleLines(box_x, box_y, box_w, box_h, GREEN)
            DrawText(b"+", box_x + box_w // 2 - 7, box_y + box_h // 2 - 12, 26, GREEN)
