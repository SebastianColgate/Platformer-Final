#Game Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 40

GRAVITY = 1800.0
JUMP_VELOCITY = -750.0
STOMP_BOUNCE = JUMP_VELOCITY * 0.6
PLAYER_SPEED = 300.0
ENEMY_SPEED = 100.0
PLAYER_WIDTH = TILE_SIZE
PLAYER_HEIGHT = TILE_SIZE * 2
PLAYER_SWIM_WIDTH = TILE_SIZE * 2.5
PLAYER_SWIM_HEIGHT = TILE_SIZE
DOOR_WIDTH = TILE_SIZE * 2
DOOR_HEIGHT = TILE_SIZE * 3

WATER_GRAVITY = 500.0
SWIM_VELOCITY = -420.0
SWIM_SPEED = 140.0
EXIT_LIQUID_VELOCITY = -900.0
JAR_WIDTH = TILE_SIZE * 0.8
JAR_HEIGHT = TILE_SIZE
JAR_PUSH_SPEED = 220.0
MOVING_PLATFORM_HEIGHT = TILE_SIZE * 0.5
MOVING_PLATFORM_SPEED = 80.0
BACKGROUND_PARALLAX = 0.25

#Tilemap Definitions
TILE_AIR = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_POISON_WATER = 3

#Layout legend
# . = air, # = solid, ~ = clean water, ! = poisoned water
# S = player spawn, E = land enemy, e = enemy in water
# P = poison jar, A = antidote jar, X = exit

LEVEL_ONE = [
    "..........................................................",
    "..........................................................",
    "..........................................................",
    "..........................................................",
    "..........................................................",
    ".....................................................X....",
    "................................###................#####..",
    "........................###...............................",
    "...............P.............................#~~~~#.......",
    "....................................A........#~~~~#.......",
    "..............###..................######....#~~~~#.......",
    "..........##.......#~e~~~~~~~~~~~~~######....#~~~~#.......",
    "...................#~~~~~~e~~~~~~~~~~~~~##...#~~~~#.......",
    "#.S................#~~~~~~~~~~~~~~~~~~~~##...#~~~~#.......",
    "##########################################################",
    "##########################################################",
    "##########################################################",
    "##########################################################",
]

LEVEL_TWO = [
    "..........................................................",
    "..........................................................",
    "..........................................................",
    "..........................................................",
    "..........................................................",
    "......................................................X...",
    "...........................................P.......#######",
    "..........................................########........",
    "....A..........................######.....................",
    "...#####...........................................#....#.",
    "..#...............P.######.........................#~~e~#.",
    "........#####...................#~~~~~~~~~~~~~#....#~~~~#.",
    ".............#~~~~e~~~~~#.......#~~~~~e~~~~~~~#....#~~~~#.",
    ".#S..........#~~~~~~~~~~#.......#~~~~~~~~~~~~~#....#~~~~#.",
    "##########################################################",
    "##########################################################",
    "##########################################################",
    "##########################################################",
]

# Moving platforms are (start_col, start_row, end_col, end_row, width_in_tiles)
LEVEL_ONE_PLATFORMS = [
    (17, 10, 30, 10, 3),
]

LEVEL_TWO_PLATFORMS = [
    (13, 9, 27, 9, 3),
    (28, 6, 41, 6, 3),
]

LEVELS = [
    {
        "name": "Lebanon Reservoir",
        "subtitle": "Campus cleanup begins at the spill site.",
        "layout": LEVEL_ONE,
        "platforms": LEVEL_ONE_PLATFORMS,
        "background": "background",
        "background_y": 0,
        "background_height": SCREEN_HEIGHT,
    },
    {
        "name": "Taylor Lake",
        "subtitle": "A wider cleanup before the run back to Ho Science.",
        "layout": LEVEL_TWO,
        "platforms": LEVEL_TWO_PLATFORMS,
        "background": "background",
        "background_y": 0,
        "background_height": SCREEN_HEIGHT,
    },
]

LEVEL = LEVELS[0]["layout"]
MOVING_PLATFORMS = LEVELS[0]["platforms"]

#World dimensions
TILE_ROWS = len(LEVEL)
TILE_COLS = len(LEVEL[0])
WORLD_WIDTH = TILE_COLS * TILE_SIZE
WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
