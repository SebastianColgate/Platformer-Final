from raylib import *
from pyray import *

from entities import Player
from helpers import calculate_clean_score, update_liquid_spread
from settings import (
    BACKGROUND_PARALLAX,
    LEVEL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_AIR,
    TILE_POISON_WATER,
    TILE_ROWS,
    TILE_COLS,
    TILE_SIZE,
    TILE_SOLID,
    TILE_WATER,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)

from level import parse_level
from sprites import draw_sprite, load_sprites, unload_sprites



def draw_level(level, exit_rect, exit_unlocked):
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            tile_value = level[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            if tile_value == TILE_SOLID:
                tile_above = TILE_SOLID
                if row > 0:
                    tile_above = level[row - 1][col]

                if tile_above == TILE_AIR:
                    draw_sprite("grass", x, y, TILE_SIZE, TILE_SIZE)
                else:
                    draw_sprite("dirt", x, y, TILE_SIZE, TILE_SIZE)

            elif tile_value == TILE_WATER:
                draw_sprite("water", x, y, TILE_SIZE, TILE_SIZE)

            elif tile_value == TILE_POISON_WATER:
                draw_sprite("poison_water", x, y, TILE_SIZE, TILE_SIZE)

    if exit_rect is not None:
        sprite_name = "exit_open" if exit_unlocked else "exit_locked"
        draw_sprite(sprite_name, exit_rect[0], exit_rect[1], exit_rect[2], exit_rect[3])


def draw_jars(jars):
    for jar in jars:
        jar.draw()


def draw_moving_platforms(moving_platforms):
    for platform in moving_platforms:
        platform.draw()


def draw_background(camera):
    camera_x = camera.target.x - SCREEN_WIDTH / 2
    scroll_x = -(camera_x * BACKGROUND_PARALLAX) % SCREEN_WIDTH
    draw_sprite("background", scroll_x - SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    draw_sprite("background", scroll_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    draw_sprite("background", scroll_x + SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


def update_camera(camera, player):
    camera.target.x = player.x + player.width / 2
    camera.target.y = player.y + player.height / 2

    min_x = SCREEN_WIDTH / 2
    max_x = WORLD_WIDTH - SCREEN_WIDTH / 2
    min_y = SCREEN_HEIGHT / 2
    max_y = WORLD_HEIGHT - SCREEN_HEIGHT / 2

    if WORLD_WIDTH <= SCREEN_WIDTH:
        camera.target.x = SCREEN_WIDTH / 2
    
    else:
        camera.target.x = max(min_x, min(camera.target.x, max_x))

    if WORLD_HEIGHT <= SCREEN_HEIGHT:
        camera.target.y = SCREEN_HEIGHT / 2
    
    else:
        camera.target.y = max(min_y, min(camera.target.y, max_y))

    camera.offset.x = SCREEN_WIDTH / 2
    camera.offset.y = SCREEN_HEIGHT / 2
    camera.target.x = round(camera.target.x)
    camera.target.y = round(camera.target.y)


def draw_debug_hitboxes(level, player, enemies, jars, moving_platforms, exit_rect):
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            tile = level[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            if tile == TILE_SOLID:
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, YELLOW)
            
            elif tile == TILE_WATER:
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, BLUE)
            
            elif tile == TILE_POISON_WATER:
                DrawRectangleLines(x, y, TILE_SIZE, TILE_SIZE, PURPLE)

    DrawRectangleLines(int(player.x), int(player.y), int(player.width), int(player.height), GREEN)


    for enemy in enemies:
        DrawRectangleLines(int(enemy.x), int(enemy.y), int(enemy.width), int(enemy.height), RED)

    for jar in jars:
        DrawRectangleLines(int(jar.x), int(jar.y), int(jar.width), int(jar.height), WHITE)

    for platform in moving_platforms:
        DrawRectangleLines(int(platform.x), int(platform.y), int(platform.width), int(platform.height), MAGENTA)

    if exit_rect is not None:
        DrawRectangleLines(int(exit_rect[0]), int(exit_rect[1]), int(exit_rect[2]), int(exit_rect[3]), ORANGE)


def main():

    # Initialize
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Amphibi-Man Prototype".encode("utf-8"))
    SetTargetFPS(60)
    load_sprites()

    # Prepare Level data
    game_level, spawn_position, jars, enemies, moving_platforms, exit_rect, total_water_tiles = parse_level(LEVEL)
    player = Player(*spawn_position)
    game_state = "PLAYING"
    debug_mode = False
    active_liquid_spreads = []

    #camera
    camera = Camera2D()
    camera.target = Vector2(player.x, player.y)
    camera.offset = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    camera.rotation = 0.0
    camera.zoom = 1.0

    #Put here because was having issues when outside with scope
    def restart_level():

        #Took a long time to figure out how to use this effectivly
        nonlocal game_level, spawn_position, jars, enemies, moving_platforms, exit_rect
        nonlocal total_water_tiles, player, game_state, active_liquid_spreads

        game_level, spawn_position, jars, enemies, moving_platforms, exit_rect, total_water_tiles = parse_level(LEVEL)
        player = Player(*spawn_position)
        active_liquid_spreads = []
        game_state = "PLAYING"
        update_camera(camera, player)


    #Gameloop
    while not WindowShouldClose():
        delta_time = GetFrameTime()
        restarted_this_frame = False

        # update
        if IsKeyPressed(KEY_R):
            restart_level()
            restarted_this_frame = True

        if IsKeyPressed(KEY_P):
            if game_state == "PLAYING":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                game_state = "PLAYING"

        if IsKeyPressed(KEY_F1):
            debug_mode = not debug_mode

        if game_state == "PLAYING" and not restarted_this_frame:
            for platform in moving_platforms:
                platform.update(delta_time, [player] + jars)

            player.update(delta_time, game_level, jars + moving_platforms)

            #Kill condition for posion or off height
            if player.y > WORLD_HEIGHT or player.is_touching_tile(game_level, TILE_POISON_WATER):
                restart_level()
                restarted_this_frame = True

            if not restarted_this_frame:
                active_jars = []


#start of all update calls

                for jar in jars:
                    jar.push(player, delta_time, game_level)
                    new_spread = jar.update(delta_time, game_level, moving_platforms)

                    if new_spread is not None:
                        active_liquid_spreads.append(new_spread)

                    if not jar.is_broken:
                        active_jars.append(jar)

                jars = active_jars

                still_spreading = []


                for spread in active_liquid_spreads:
                    finished = update_liquid_spread(game_level, spread, delta_time)

                    if not finished:
                        still_spreading.append(spread)

                active_liquid_spreads = still_spreading
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

                #player enemy collision kill condition
                elif hit_type == "LETHAL":
                    restart_level()
                    restarted_this_frame = True


                #Level end condition (not finished)
                if not restarted_this_frame and exit_rect is not None and CheckCollisionRecs(player.get_rect(), exit_rect):
                    if not enemies:
                        game_state = "LEVEL_CLEAR"



#Begins camera drawing updates


        update_camera(camera, player)
        clean_score = calculate_clean_score(game_level, total_water_tiles)
        exit_unlocked = len(enemies) == 0

        #draw
        BeginDrawing()
        ClearBackground(SKYBLUE)
        draw_background(camera)

        BeginMode2D(camera)
        draw_level(game_level, exit_rect, exit_unlocked)
        draw_moving_platforms(moving_platforms)
        draw_jars(jars)

        for enemy in enemies:
            enemy.draw()

        player.draw()

        if debug_mode:
            draw_debug_hitboxes(game_level, player, enemies, jars, moving_platforms, exit_rect)

        EndMode2D()

        #Basic top UI and Enemy counter, cleanscore
        DrawRectangle(0, 0, SCREEN_WIDTH, 76, Fade(BLACK, 0.18))
        enemy_text = f"Enemies: {len(enemies)}".encode("utf-8")
        clean_text = f"Clean Score: {clean_score}%".encode("utf-8")
        DrawText(enemy_text, 12, 10, 24, BLACK)
        DrawText(clean_text, 12, 36, 22, BLACK)


        if debug_mode:
            DrawText(b"Debug: hitboxes", 260, 12, 20, RED)

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


    unload_sprites()
    CloseWindow()


if __name__ == "__main__":
    main()
