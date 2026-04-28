from entities import ChemicalJar, Enemy, MovingPlatform
from helpers import make_spawn_position
from settings import (
    JAR_HEIGHT,
    JAR_WIDTH,
    MOVING_PLATFORM_SPEED,
    MOVING_PLATFORMS,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    TILE_AIR,
    TILE_POISON_WATER,
    TILE_SIZE,
    TILE_SOLID,
    TILE_WATER,
)


def parse_level(layout):
    """
    Parses the level map, extracts dynamic entities, and returns the
    tile collision map plus the objects that need to be spawn from the layout.
    """
    
    level = []
    jars = []
    enemies = []
    moving_platforms = []
    
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
            elif symbol in ("E", "e"):
                enemy_x, enemy_y = make_spawn_position(col_index, row_index, TILE_SIZE * 0.7, TILE_SIZE * 0.7)

                if symbol == "e":
                    enemies.append(Enemy(enemy_x, enemy_y, "water"))
                else:
                    enemies.append(Enemy(enemy_x, enemy_y, "land"))
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

    for platform_data in MOVING_PLATFORMS:
        start_col, start_row, end_col, end_row, width_tiles = platform_data
        start_x = start_col * TILE_SIZE
        start_y = start_row * TILE_SIZE
        end_x = end_col * TILE_SIZE
        end_y = end_row * TILE_SIZE
        width = width_tiles * TILE_SIZE
        moving_platforms.append(MovingPlatform(start_x, start_y, end_x, end_y, width, MOVING_PLATFORM_SPEED))

    return level, spawn_position, jars, enemies, moving_platforms, exit_rect, total_water_tiles
