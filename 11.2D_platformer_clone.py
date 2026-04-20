import sys
from raylib import *
from pyray import *

sys.dont_write_bytecode = True

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
GRAVITY = 1800.0
JUMP_VELOCITY = -750.0
STOMP_BOUNCE = JUMP_VELOCITY * 0.6
PLAYER_SPEED = 300.0
ENEMY_SPEED = 100.0
PLAYER_WIDTH = TILE_SIZE * 0.8
PLAYER_HEIGHT = TILE_SIZE * 0.9
WATER_GRAVITY = 500.0
SWIM_VELOCITY = -280.0
SWIM_SPEED = 140.0
EXIT_LIQUID_VELOCITY = -900.0
JAR_WIDTH = TILE_SIZE * 0.55
JAR_HEIGHT = TILE_SIZE * 0.7
JAR_PUSH_SPEED = 220.0

# --- Tile Types ---
TILE_AIR = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_POISON_WATER = 3

# --- Level Layout ---
# Legend:
# . = air, # = solid, ~ = clean water, ! = poisoned water
# S = player spawn, E = land enemy, e = enemy starting in water
# P = poison jar, A = antidote jar, X = exit
LEVEL_LAYOUT = [
    "............................................",
    "............................................",
    "............................................",
    "............................................",
    "............................................",
    "......................................X.....",
    "....................................#####...",
    "............................................",
    ".................................!!!........",
    ".................P............A..!!!........",
    "...............####.........####.!!!........",
    "..................#~~~#..........!!!........",
    "..................#~e~#..........!!!........",
    "..S....E.........................!!!........",
    "############################################",
]

assert LEVEL_LAYOUT, "LEVEL_LAYOUT must not be empty."
assert all(len(row) == len(LEVEL_LAYOUT[0]) for row in LEVEL_LAYOUT), "All level rows must have the same width."

TILE_ROWS = len(LEVEL_LAYOUT)
TILE_COLS = len(LEVEL_LAYOUT[0])
WORLD_WIDTH = TILE_COLS * TILE_SIZE
WORLD_HEIGHT = TILE_ROWS * TILE_SIZE


def make_spawn_position(col, row, width, height):
    x = col * TILE_SIZE + (TILE_SIZE - width) / 2
    y = row * TILE_SIZE + TILE_SIZE - height
    return x, y


def rect_touches_tile(rect, level, tile_types):
    if isinstance(tile_types, int):
        tile_types = {tile_types}
    else:
        tile_types = set(tile_types)

    px, py, pw, ph = rect
    min_col = int(px / TILE_SIZE)
    max_col = int((px + pw) / TILE_SIZE)
    min_row = int(py / TILE_SIZE)
    max_row = int((py + ph) / TILE_SIZE)

    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                continue

            if level[row][col] in tile_types:
                tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if CheckCollisionRecs(rect, tile_rect):
                    return True

    return False


def flood_fill_liquid(level, start_row, start_col, source_tile, target_tile):
    if start_row is None or start_col is None:
        return 0
    if source_tile == target_tile:
        return 0
    if start_row < 0 or start_row >= TILE_ROWS or start_col < 0 or start_col >= TILE_COLS:
        return 0
    if level[start_row][start_col] != source_tile:
        return 0

    changed_tiles = 0
    frontier = [(start_row, start_col)]

    while frontier:
        row, col = frontier.pop()
        if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
            continue
        if level[row][col] != source_tile:
            continue

        level[row][col] = target_tile
        changed_tiles += 1

        frontier.append((row - 1, col))
        frontier.append((row + 1, col))
        frontier.append((row, col - 1))
        frontier.append((row, col + 1))

    return changed_tiles


def find_touching_liquid_tile(rect, level):
    px, py, pw, ph = rect
    min_col = int(px / TILE_SIZE)
    max_col = int((px + pw) / TILE_SIZE)
    min_row = int(py / TILE_SIZE)
    max_row = int((py + ph) / TILE_SIZE)

    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                continue

            if level[row][col] not in (TILE_WATER, TILE_POISON_WATER):
                continue

            tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if CheckCollisionRecs(rect, tile_rect):
                return row, col, level[row][col]

    return None, None, None


def calculate_clean_score(level, total_water_tiles):
    if total_water_tiles == 0:
        return 100

    poisoned_tiles = 0
    for row in level:
        poisoned_tiles += row.count(TILE_POISON_WATER)

    clean_tiles = total_water_tiles - poisoned_tiles
    return round((clean_tiles / total_water_tiles) * 100)


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

    def try_break(self, level):
        row, col, _ = find_touching_liquid_tile(self.get_rect(), level)
        if row is None:
            return False, 0

        self.is_broken = True
        if self.kind == "poison":
            changed_tiles = flood_fill_liquid(level, row, col, TILE_WATER, TILE_POISON_WATER)
        else:
            changed_tiles = flood_fill_liquid(level, row, col, TILE_POISON_WATER, TILE_WATER)
        return True, changed_tiles

    def can_move_to(self, level, next_x, next_y):
        jar_rect = (next_x, next_y, self.width, self.height)
        return not rect_touches_tile(jar_rect, level, TILE_SOLID)

    def push(self, player, delta_time, level):
        if self.is_broken or player.vx == 0.0:
            return

        if not CheckCollisionRecs(player.get_rect(), self.get_rect()):
            return

        direction = 1 if player.vx > 0 else -1
        next_x = self.x + direction * JAR_PUSH_SPEED * delta_time
        if self.can_move_to(level, next_x, self.y):
            self.x = next_x
            self.vx = direction * JAR_PUSH_SPEED

    def update(self, delta_time, level):
        if self.is_broken:
            return False, 0

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

    def draw(self):
        if self.is_broken:
            return

        glass_color = PURPLE if self.kind == "poison" else GREEN
        rect = Rectangle(*self.get_rect())
        cork_x = int(self.x + self.width * 0.25)
        cork_y = int(self.y - 4)

        DrawRectangleRounded(rect, 0.2, 4, Fade(glass_color, 0.8))
        DrawRectangleRoundedLines(rect, 0.2, 4, WHITE)
        DrawRectangle(cork_x, cork_y, int(self.width * 0.5), 6, BROWN)


def parse_level(layout):
    level = []
    jars = []
    enemies = []
    spawn_position = make_spawn_position(2, 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    exit_rect = None
    total_water_tiles = 0

    for row_index, row_text in enumerate(layout):
        row_tiles = []

        for col_index, symbol in enumerate(row_text):
            tile = TILE_AIR

            if symbol == "#":
                tile = TILE_SOLID
            elif symbol in ("~", "e"):
                tile = TILE_WATER
            elif symbol == "!":
                tile = TILE_POISON_WATER

            if tile in (TILE_WATER, TILE_POISON_WATER):
                total_water_tiles += 1

            if symbol == "S":
                spawn_position = make_spawn_position(col_index, row_index, PLAYER_WIDTH, PLAYER_HEIGHT)
            elif symbol == "E":
                enemy_x, enemy_y = make_spawn_position(col_index, row_index, TILE_SIZE * 0.7, TILE_SIZE * 0.7)
                enemies.append(Enemy(enemy_x, enemy_y))
            elif symbol == "e":
                enemy_x, enemy_y = make_spawn_position(col_index, row_index, TILE_SIZE * 0.7, TILE_SIZE * 0.7)
                enemies.append(Enemy(enemy_x, enemy_y))
            elif symbol in ("P", "A"):
                kind = "poison" if symbol == "P" else "antidote"
                jar_x, jar_y = make_spawn_position(col_index, row_index, JAR_WIDTH, JAR_HEIGHT)
                jars.append(ChemicalJar(kind, jar_x, jar_y))
            elif symbol == "X":
                exit_x = col_index * TILE_SIZE + 6
                exit_y = row_index * TILE_SIZE + 6
                exit_rect = (exit_x, exit_y, TILE_SIZE - 12, TILE_SIZE - 12)

            row_tiles.append(tile)

        level.append(row_tiles)

    return level, spawn_position, jars, enemies, exit_rect, total_water_tiles


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.is_swimming = False

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
        player_color = BLUE
        if self.is_swimming:
            player_color = GREEN

        DrawRectangle(int(self.x), int(self.y), int(self.width), int(self.height), player_color)
        outline = WHITE if self.is_grounded else DARKBLUE
        DrawRectangleLines(int(self.x), int(self.y), int(self.width), int(self.height), outline)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.7
        self.height = TILE_SIZE * 0.7
        self.vx = ENEMY_SPEED
        self.vy = 0.0
        self.is_grounded = False

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

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


def draw_level(level, exit_rect, exit_unlocked):
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            tile_value = level[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            if tile_value == TILE_SOLID:
                DrawRectangle(x, y, TILE_SIZE, TILE_SIZE, DARKGRAY)
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, BLACK)
            elif tile_value == TILE_WATER:
                DrawRectangle(x, y, TILE_SIZE, TILE_SIZE, Fade(BLUE, 0.55))
                DrawRectangle(x, y, TILE_SIZE, 6, SKYBLUE)
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, DARKBLUE)
            elif tile_value == TILE_POISON_WATER:
                DrawRectangle(x, y, TILE_SIZE, TILE_SIZE, Fade(PURPLE, 0.65))
                DrawRectangle(x, y, TILE_SIZE, 6, PINK)
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, DARKPURPLE)

    if exit_rect is not None:
        exit_color = GREEN if exit_unlocked else MAROON
        rect = Rectangle(*exit_rect)
        DrawRectangleRounded(rect, 0.15, 4, exit_color)
        DrawRectangleRoundedLines(rect, 0.15, 4, WHITE)
        DrawText(b"EXIT", int(exit_rect[0] + 5), int(exit_rect[1] + 8), 16, WHITE)


def draw_jars(jars):
    for jar in jars:
        jar.draw()


def update_camera(camera, player):
    camera.target.x = player.x + player.width / 2
    camera.target.y = player.y + player.height / 2

    min_x = SCREEN_WIDTH / 2
    max_x = WORLD_WIDTH - SCREEN_WIDTH / 2
    min_y = SCREEN_HEIGHT / 2
    max_y = WORLD_HEIGHT - SCREEN_HEIGHT / 2

    camera.target.x = max(min_x, min(camera.target.x, max_x))
    camera.target.y = max(min_y, min(camera.target.y, max_y))
    camera.offset.x = SCREEN_WIDTH / 2
    camera.offset.y = SCREEN_HEIGHT / 2


def main():
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Amphibi-Man Prototype".encode("utf-8"))
    SetTargetFPS(60)

    game_level, spawn_position, jars, enemies, exit_rect, total_water_tiles = parse_level(LEVEL_LAYOUT)
    player = Player(*spawn_position)
    game_state = "PLAYING"

    camera = Camera2D()
    camera.target = Vector2(player.x, player.y)
    camera.offset = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    camera.rotation = 0.0
    camera.zoom = 1.0

    def restart_level():
        nonlocal game_level, spawn_position, jars, enemies, exit_rect
        nonlocal total_water_tiles, player, game_state

        game_level, spawn_position, jars, enemies, exit_rect, total_water_tiles = parse_level(LEVEL_LAYOUT)
        player = Player(*spawn_position)
        game_state = "PLAYING"
        update_camera(camera, player)

    while not WindowShouldClose():
        delta_time = GetFrameTime()

        if IsKeyPressed(KEY_R):
            restart_level()
            continue

        if IsKeyPressed(KEY_ESCAPE):
            if game_state == "PLAYING":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                game_state = "PLAYING"

        if game_state == "PLAYING":
            player.update(delta_time, game_level)

            if player.y > WORLD_HEIGHT or player.is_touching_tile(game_level, TILE_POISON_WATER):
                restart_level()
                continue

            active_jars = []
            for jar in jars:
                jar.push(player, delta_time, game_level)
                jar.update(delta_time, game_level)
                if not jar.is_broken:
                    active_jars.append(jar)
            jars = active_jars

            for enemy in enemies:
                enemy.update(delta_time, game_level)

            alive_enemies = []
            poisoned_enemy_count = 0
            for enemy in enemies:
                if rect_touches_tile(enemy.get_rect(), game_level, TILE_POISON_WATER):
                    poisoned_enemy_count += 1
                else:
                    alive_enemies.append(enemy)
            enemies = alive_enemies

            hit_type, enemy_index = player.check_enemy_collision(enemies)
            if hit_type == "STOMP":
                enemies.pop(enemy_index)
                player.vy = STOMP_BOUNCE
            elif hit_type == "LETHAL":
                restart_level()
                continue

            if exit_rect is not None and CheckCollisionRecs(player.get_rect(), exit_rect):
                if not enemies:
                    game_state = "LEVEL_CLEAR"

        update_camera(camera, player)
        clean_score = calculate_clean_score(game_level, total_water_tiles)
        exit_unlocked = len(enemies) == 0

        BeginDrawing()
        ClearBackground(SKYBLUE)

        BeginMode2D(camera)
        draw_level(game_level, exit_rect, exit_unlocked)
        draw_jars(jars)

        for enemy in enemies:
            enemy.draw()

        player.draw()
        EndMode2D()

        DrawRectangle(0, 0, SCREEN_WIDTH, 76, Fade(BLACK, 0.18))
        enemy_text = f"Enemies: {len(enemies)}".encode("utf-8")
        clean_text = f"Clean Score: {clean_score}%".encode("utf-8")
        DrawText(enemy_text, 12, 10, 24, BLACK)
        DrawText(clean_text, 12, 36, 22, BLACK)

        if game_state == "PAUSED":
            DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(BLACK, 0.45))
            pause_text = b"Paused"
            DrawText(pause_text, SCREEN_WIDTH // 2 - MeasureText(pause_text, 40) // 2, 230, 40, WHITE)
        elif game_state == "LEVEL_CLEAR":
            DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(DARKGREEN, 0.28))
            clear_text = b"Room Clear"
            score_text = f"Final Clean Score: {clean_score}%".encode("utf-8")
            DrawText(clear_text, SCREEN_WIDTH // 2 - MeasureText(clear_text, 42) // 2, 220, 42, WHITE)
            DrawText(score_text, SCREEN_WIDTH // 2 - MeasureText(score_text, 28) // 2, 276, 28, WHITE)

        EndDrawing()

    CloseWindow()


if __name__ == "__main__":
    main()
