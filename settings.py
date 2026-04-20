#Game Constants
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

#Tilemap Definitions
TILE_AIR = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_POISON_WATER = 3

#Level Layout
# . = air, # = solid, ~ = clean water, ! = poisoned water, S = player spawn, E = land enemy, e = enemy in water, P = poison jar, A = antidote jar, X = exit
LEVEL = [
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

assert LEVEL, "LEVEL must not be empty."
assert all(len(row) == len(LEVEL[0]) for row in LEVEL), "All level rows must have the same width."

#World Dimensions
TILE_ROWS = len(LEVEL)
TILE_COLS = len(LEVEL[0])
WORLD_WIDTH = TILE_COLS * TILE_SIZE
WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
