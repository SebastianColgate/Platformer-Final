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
MESSAGE_TIME = 2.5

# --- Tile Types ---
TILE_AIR = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_POISON_WATER = 3

# --- Level Layout ---
# Legend:
# . = air, # = solid, ~ = clean water, ! = poisoned water
# S = player spawn, E = land enemy, e = enemy starting in water
# P = poison pickup, A = antidote pickup, X = exit
LEVEL_LAYOUT = [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "...................................X....",
    ".................................#####..",
    "........................................",
    "..............................!!!.......",
    "..............................!!!.......",
    "..............................!!!.......",
    "................#~~~#.........!!!.......",
    "................#~e~#.........!!!.......",
    "..S...E.......P.#####.....A...!!!.......",
    "########################################",
]

SHOWCASE_LABELS = [
    (2, 12, "Start"),
    (5, 11, "Stomp enemy"),
    (14, 11, "Poison demo"),
    (26, 11, "Clean water"),
    (31, 7, "Swim up"),
    (34, 4, "Exit"),
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


def tile_to_world_center(col, row):
    return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2


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


def find_liquid_target(layout, start_row, start_col):
    best_target = (None, None)
    best_distance = None

    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            if layout[row][col] not in ("~", "!"):
                continue

            distance = abs(col - start_col) + abs(row - start_row)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_target = (row, col)

    return best_target


def calculate_clean_score(level, total_water_tiles):
    if total_water_tiles == 0:
        return 100

    poisoned_tiles = 0
    for row in level:
        poisoned_tiles += row.count(TILE_POISON_WATER)

    clean_tiles = total_water_tiles - poisoned_tiles
    return round((clean_tiles / total_water_tiles) * 100)


class ChemicalPickup:
    def __init__(self, kind, x, y, target_row, target_col):
        self.kind = kind
        self.x = x
        self.y = y
        self.target_row = target_row
        self.target_col = target_col
        self.size = 24

    def get_rect(self):
        return (
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.size,
            self.size,
        )

    def apply(self, level):
        if self.kind == "poison":
            return flood_fill_liquid(level, self.target_row, self.target_col, TILE_WATER, TILE_POISON_WATER)

        return flood_fill_liquid(level, self.target_row, self.target_col, TILE_POISON_WATER, TILE_WATER)

    def draw(self):
        box_color = PURPLE if self.kind == "poison" else GREEN
        label = b"P" if self.kind == "poison" else b"A"
        rect = Rectangle(*self.get_rect())

        DrawRectangleRounded(rect, 0.2, 4, box_color)
        DrawRectangleRoundedLines(rect, 0.2, 4, WHITE)
        DrawText(label, int(self.x - 6), int(self.y - 10), 20, WHITE)


def parse_level(layout):
    level = []
    pickups = []
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
                target_row, target_col = find_liquid_target(layout, row_index, col_index)
                center_x, center_y = tile_to_world_center(col_index, row_index)
                kind = "poison" if symbol == "P" else "antidote"
                pickups.append(ChemicalPickup(kind, center_x, center_y, target_row, target_col))
            elif symbol == "X":
                exit_x = col_index * TILE_SIZE + 6
                exit_y = row_index * TILE_SIZE + 6
                exit_rect = (exit_x, exit_y, TILE_SIZE - 12, TILE_SIZE - 12)

            row_tiles.append(tile)

        level.append(row_tiles)

    return level, spawn_position, pickups, enemies, exit_rect, total_water_tiles


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

    def check_pickup_collection(self, pickups):
        collected_indices = []
        player_rect = self.get_rect()

        for index, pickup in enumerate(pickups):
            if CheckCollisionRecs(player_rect, pickup.get_rect()):
                collected_indices.append(index)

        return collected_indices

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


def draw_pickups(pickups):
    for pickup in pickups:
        pickup.draw()


def draw_showcase_labels():
    for col, row, text in SHOWCASE_LABELS:
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        label = text.encode("utf-8")
        DrawText(label, x, y, 18, WHITE)
        DrawText(label, x + 1, y + 1, 18, BLACK)


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

    game_level, spawn_position, pickups, enemies, exit_rect, total_water_tiles = parse_level(LEVEL_LAYOUT)
    player = Player(*spawn_position)
    game_state = "PLAYING"
    status_message = "Mechanic showcase: stomp, poison, clean, swim, then exit."
    status_timer = 4.0

    camera = Camera2D()
    camera.target = Vector2(player.x, player.y)
    camera.offset = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    camera.rotation = 0.0
    camera.zoom = 1.0

    def restart_level(message):
        nonlocal game_level, spawn_position, pickups, enemies, exit_rect
        nonlocal total_water_tiles, player, game_state, status_message, status_timer

        game_level, spawn_position, pickups, enemies, exit_rect, total_water_tiles = parse_level(LEVEL_LAYOUT)
        player = Player(*spawn_position)
        game_state = "PLAYING"
        status_message = message
        status_timer = MESSAGE_TIME
        update_camera(camera, player)

    while not WindowShouldClose():
        delta_time = GetFrameTime()

        if status_timer > 0:
            status_timer -= delta_time
            if status_timer <= 0:
                status_message = ""

        if IsKeyPressed(KEY_R):
            restart_level("Level reset.")
            continue

        if IsKeyPressed(KEY_ESCAPE):
            if game_state == "PLAYING":
                game_state = "PAUSED"
                status_message = "Paused. Press Esc to resume."
                status_timer = MESSAGE_TIME
            elif game_state == "PAUSED":
                game_state = "PLAYING"
                status_message = "Back in."
                status_timer = 1.2

        if game_state == "PLAYING":
            enemy_count_before_update = len(enemies)
            player.update(delta_time, game_level)

            if player.y > WORLD_HEIGHT or player.is_touching_tile(game_level, TILE_POISON_WATER):
                restart_level("Poisoned water is unsafe. Restarting room.")
                continue

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

            if poisoned_enemy_count > 0:
                status_message = f"Poison cleared {poisoned_enemy_count} enemy."
                if poisoned_enemy_count > 1:
                    status_message = f"Poison cleared {poisoned_enemy_count} enemies."
                status_timer = MESSAGE_TIME

            hit_type, enemy_index = player.check_enemy_collision(enemies)
            if hit_type == "STOMP":
                enemies.pop(enemy_index)
                player.vy = STOMP_BOUNCE
                status_message = "Enemy stomped."
                status_timer = 1.4
            elif hit_type == "LETHAL":
                restart_level("Enemy got you. Restarting room.")
                continue

            collected_indices = player.check_pickup_collection(pickups)
            for index in sorted(collected_indices, reverse=True):
                pickup = pickups.pop(index)
                changed_tiles = pickup.apply(game_level)

                if pickup.kind == "poison":
                    if changed_tiles > 0:
                        status_message = f"Poison spread through {changed_tiles} water tiles."
                    else:
                        status_message = "That poison vial is not linked to water."
                else:
                    if changed_tiles > 0:
                        status_message = f"Antidote cleaned {changed_tiles} water tiles."
                    else:
                        status_message = "Antidote had nothing to clean."
                status_timer = MESSAGE_TIME

            if enemy_count_before_update > 0 and len(enemies) == 0:
                status_message = "Exit unlocked."
                status_timer = MESSAGE_TIME

            if exit_rect is not None and CheckCollisionRecs(player.get_rect(), exit_rect):
                if enemies:
                    status_message = "Exit locked. Clear every enemy first."
                    status_timer = MESSAGE_TIME
                else:
                    game_state = "LEVEL_CLEAR"
                    status_message = "Level clear."
                    status_timer = MESSAGE_TIME

        update_camera(camera, player)
        clean_score = calculate_clean_score(game_level, total_water_tiles)
        exit_unlocked = len(enemies) == 0

        BeginDrawing()
        ClearBackground(SKYBLUE)

        BeginMode2D(camera)
        draw_level(game_level, exit_rect, exit_unlocked)
        draw_showcase_labels()
        draw_pickups(pickups)

        for enemy in enemies:
            enemy.draw()

        player.draw()
        EndMode2D()

        DrawRectangle(0, 0, SCREEN_WIDTH, 76, Fade(BLACK, 0.18))
        enemy_text = f"Enemies: {len(enemies)}".encode("utf-8")
        clean_text = f"Clean Score: {clean_score}%".encode("utf-8")
        controls_text = b"Move: A/D or Arrows  Jump/Swim: Space/W  Dive: S  Reset: R  Pause: Esc"
        DrawText(enemy_text, 12, 10, 24, BLACK)
        DrawText(clean_text, 12, 36, 22, BLACK)
        DrawText(controls_text, 250, 14, 18, DARKGRAY)

        if status_message:
            status_bytes = status_message.encode("utf-8")
            status_width = MeasureText(status_bytes, 22)
            status_x = SCREEN_WIDTH / 2 - status_width / 2
            status_rect = Rectangle(status_x - 14, SCREEN_HEIGHT - 56, status_width + 28, 38)
            DrawRectangleRounded(status_rect, 0.25, 6, Fade(BLACK, 0.55))
            DrawText(status_bytes, int(status_x), SCREEN_HEIGHT - 48, 22, WHITE)

        if game_state == "PAUSED":
            DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(BLACK, 0.45))
            pause_text = b"Paused"
            help_text = b"Press Esc to resume or R to restart."
            DrawText(pause_text, SCREEN_WIDTH // 2 - MeasureText(pause_text, 40) // 2, 230, 40, WHITE)
            DrawText(help_text, SCREEN_WIDTH // 2 - MeasureText(help_text, 24) // 2, 280, 24, WHITE)
        elif game_state == "LEVEL_CLEAR":
            DrawRectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Fade(DARKGREEN, 0.28))
            clear_text = b"Showcase Clear"
            score_text = f"Final Clean Score: {clean_score}%".encode("utf-8")
            replay_text = b"Press R to replay the mechanic showcase."
            DrawText(clear_text, SCREEN_WIDTH // 2 - MeasureText(clear_text, 42) // 2, 220, 42, WHITE)
            DrawText(score_text, SCREEN_WIDTH // 2 - MeasureText(score_text, 28) // 2, 276, 28, WHITE)
            DrawText(replay_text, SCREEN_WIDTH // 2 - MeasureText(replay_text, 22) // 2, 316, 22, WHITE)

        EndDrawing()

    CloseWindow()


if __name__ == "__main__":
    main()
