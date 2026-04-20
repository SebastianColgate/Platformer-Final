from raylib import CheckCollisionRecs

from game_settings import TILE_COLS, TILE_POISON_WATER, TILE_ROWS, TILE_SIZE, TILE_WATER


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
