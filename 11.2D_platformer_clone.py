import sys
from raylib import *
from pyray import *

from entities import Player
from help import calculate_clean_score
from settings import (
    LEVEL_LAYOUT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_POISON_WATER,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from level import parse_level

sys.dont_write_bytecode = True


def draw_level(level, exit_rect, exit_unlocked):
    from settings import TILE_ROWS, TILE_COLS, TILE_SIZE, TILE_SOLID, TILE_WATER, TILE_POISON_WATER

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
            for enemy in enemies:
                if enemy.is_poisoned(game_level):
                    continue
                alive_enemies.append(enemy)
            enemies = alive_enemies

            hit_type, enemy_index = player.check_enemy_collision(enemies)
            if hit_type == "STOMP":
                enemies.pop(enemy_index)
                player.vy = player.stomp_bounce
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
