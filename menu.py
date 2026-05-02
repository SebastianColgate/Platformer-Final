from raylib import *
from pyray import *

from entities import Player
from helpers import format_level_time
from settings import (
    PLAYER_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_AIR,
    TILE_COLS,
    TILE_ROWS,
    TILE_SIZE,
    TILE_SOLID,
    TILE_WATER,
)
from sprites import draw_sprite


POOL_COL = 20
POOL_COLS = 9
GROUND_ROW = TILE_ROWS - 4

menu_level = None
menu_player = None
wait_timer = 0.0
menu_timer = 0.0
first_jump_done = False
pool_jump_done = False
next_swim_time = 0.0


def draw_menu_background():
    ClearBackground(DARKBLUE)
    scroll = -(GetTime() * 18) % (SCREEN_WIDTH * 2)
    for i in range(-2, 4):
        x = scroll + i * SCREEN_WIDTH
        flip = i % 2 != 0
        draw_sprite("menu_background", x, 0, SCREEN_WIDTH, SCREEN_HEIGHT, flip)

    draw_menu_scene()


def create_menu_level():
    level = []
    for row in range(TILE_ROWS):
        level.append([TILE_AIR] * TILE_COLS)

    for col in range(TILE_COLS):
        in_pool = col >= POOL_COL and col < POOL_COL + POOL_COLS
        for row in range(GROUND_ROW, TILE_ROWS):
            if in_pool and row < TILE_ROWS - 1:
                level[row][col] = TILE_WATER
            else:
                level[row][col] = TILE_SOLID

    return level


def reset_menu_player():
    global menu_level, menu_player, menu_timer, first_jump_done, pool_jump_done
    global next_swim_time

    if menu_level is None:
        menu_level = create_menu_level()

    player_y = GROUND_ROW * TILE_SIZE - PLAYER_HEIGHT
    menu_player = Player(0, player_y)
    menu_timer = 0.0
    first_jump_done = False
    pool_jump_done = False
    next_swim_time = 0.0

#does player animmation for menu  simulation
def update_menu_player(delta_time):
    global menu_player, wait_timer, menu_timer, first_jump_done
    global pool_jump_done, next_swim_time

    if wait_timer > 0:
        wait_timer -= delta_time
        return

    if menu_player is None:
        reset_menu_player()

    menu_timer += delta_time
    pool_x = POOL_COL * TILE_SIZE
    pool_y = GROUND_ROW * TILE_SIZE
    pool_right = (POOL_COL + POOL_COLS) * TILE_SIZE
    keys = {"right": True}

    if menu_timer > 0.8 and menu_player.is_grounded and not first_jump_done:
        keys["jump"] = True
        first_jump_done = True

    if menu_player.x > pool_x - TILE_SIZE * 3.5 and menu_player.is_grounded and not pool_jump_done:
        keys["jump"] = True
        pool_jump_done = True

    if menu_player.is_swimming:
        swim_wait = 0.38
        swim_up = menu_player.y > pool_y + TILE_SIZE * 1.2

        if menu_player.x > pool_right - TILE_SIZE * 5:
            swim_wait = 0.25
            swim_up = menu_player.y > pool_y - TILE_SIZE * 0.4

        if swim_up and menu_timer >= next_swim_time:
            keys["swim_up"] = True
            next_swim_time = menu_timer + swim_wait

    menu_player.update(delta_time, menu_level, [], keys)

    if menu_player.x > SCREEN_WIDTH + TILE_SIZE * 3:
        menu_player = None
        wait_timer = 20.0


def draw_menu_scene():
    ground_y = SCREEN_HEIGHT - TILE_SIZE * 4
    pool_x = POOL_COL * TILE_SIZE
    pool_y = ground_y

    for col in range(SCREEN_WIDTH // TILE_SIZE + 1):
        x = col * TILE_SIZE
        in_pool = col >= POOL_COL and col < POOL_COL + POOL_COLS

        if in_pool:
            draw_sprite("dirt", x, ground_y + TILE_SIZE * 3, TILE_SIZE, TILE_SIZE)
            continue

        for row in range(4):
            draw_sprite("dirt", x, ground_y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        draw_sprite("grass", x, ground_y, TILE_SIZE, TILE_SIZE)

    for row in range(3):
        for col in range(POOL_COLS):
            draw_sprite("water", pool_x + col * TILE_SIZE, pool_y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    update_menu_player(GetFrameTime())
    if menu_player is not None:
        menu_player.draw()


def draw_title_block(title, subtitle):
    title_size = 64
    title_text = b"AMPHIBIMAN"
    title_x = SCREEN_WIDTH // 2 - MeasureText(title_text, title_size) // 2

    DrawText(title_text, title_x + 4, 84 + 4, title_size, Fade(BLACK, 0.55))
    DrawText(title_text, title_x, 84, title_size, RAYWHITE)


def draw_start_menu(selected):
    draw_menu_background()
    draw_title_block("AMPHIBI-MAN", "")

    options = ["Start", "Controls"]
    panel_x = SCREEN_WIDTH // 2 - 210
    panel_y = 220
    DrawRectangle(panel_x - 24, panel_y - 20, 468, 150, Fade(BLACK, 0.35))
    DrawRectangleLines(panel_x - 24, panel_y - 20, 468, 150, RAYWHITE)

    for i, option in enumerate(options):
        y = panel_y + i * 58
        on = i == selected
        color = RAYWHITE if on else Fade(RAYWHITE, 0.72)
        if on:
            DrawRectangle(panel_x - 8, y - 8, 420, 42, Fade(GREEN, 0.32))
            DrawText(b">", panel_x + 8, y, 28, RAYWHITE)
        DrawText(option.encode("utf-8"), panel_x + 44, y, 28, color)


def draw_info_screen(title, lines):
    draw_menu_background()
    draw_title_block(title, "")

    box_x = 155
    box_y = 230
    DrawRectangle(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(BLACK, 0.42))
    DrawRectangleLines(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(RAYWHITE, 0.45))

    y = box_y + 34
    for line in lines:
        DrawText(line.encode("utf-8"), box_x + 34, y, 24, RAYWHITE)
        y += 42


def draw_objective_briefing():
    draw_menu_background()
    draw_title_block("MAIN OBJECTIVE", "")

    box_x = 155
    box_y = 230
    DrawRectangle(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(BLACK, 0.42))
    DrawRectangleLines(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(RAYWHITE, 0.45))

    lines = [
        "An chemical explosion at the Ho Science Building mutated you and the wildlife!",
        "Get back to Ho to find the cure, and clean-up the water along the way",
        "Use poison and antidote jars to change the and clear enemies",
        "Switch between platforming on land and swimming in clean water",
        "Reach the lab door, and find the cure",
        "Finish levels with the best clean score and time",
    ]

    y = box_y + 34
    for line in lines:
        DrawText(line.encode("utf-8"), box_x + 34, y, 24, RAYWHITE)
        y += 42


def draw_game_clear_screen(level_results):
    draw_menu_background()
    draw_title_block("CURE FOUND", "")

    box_x = 190
    box_y = 230
    DrawRectangle(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(BLACK, 0.42))
    DrawRectangleLines(box_x, box_y, SCREEN_WIDTH - box_x * 2, 310, Fade(RAYWHITE, 0.45))

    DrawText(b"You found the cure!", box_x + 34, box_y + 28, 30, RAYWHITE)

    name_x = box_x + 34
    clean_x = box_x + 430
    time_x = box_x + 610
    y = box_y + 82

    for res in level_results:
        level_text = res["name"].encode("utf-8")
        clean_text = f"Clean {res['clean_score']}%".encode("utf-8")
        time_text = f"Time {format_level_time(res['time'])}".encode("utf-8")

        DrawText(level_text, name_x, y, 24, RAYWHITE)
        DrawText(clean_text, clean_x, y, 24, RAYWHITE)
        DrawText(time_text, time_x, y, 24, RAYWHITE)
        y += 44

    DrawText(b"The cure is unstable, but it is enough to start cleaning campus!", box_x + 34, y + 18, 22, Fade(RAYWHITE, 0.85))
    DrawText(b"ENTER: play again     ESC: quit", box_x + 34, box_y + 260, 22, RAYWHITE)
