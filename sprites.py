import os
from raylib import *
from pyray import *


SPRITES = {}


def load_sprites():
    texture_folder = os.path.join(os.path.dirname(__file__), "textures")
    files = {
        "background": "background.png",
        "menu_background": "menu_background.png",
        "player": "player.png",
        "player_stand": "Player Standing.png",
        "player_walk": "player_walking.png",
        "player_jump": "jump_sprite.png",
        "player_swim_idle": "swim_idle.png",
        "player_swim_kick": "swim_kick.png",
        "enemy": "enemy.png",
        "water_enemy_1": "water_enemy_1.png",
        "water_enemy_2": "water_enemy_2.png",
        "poison_jar": "poison_jar.png",
        "antidote_jar": "antidote_jar.png",
        "dirt": "dirt.png",
        "grass": "grass.png",
        "water": "water_tile.png",
        "poison_water": "poison_water_tile.png",
        "moving_platform": "moving_platform.png",
        "exit_locked": "locked_door.png",
        "exit_open": "unlocked_door.png",
    }

    for name, file_name in files.items():
        path = os.path.join(texture_folder, file_name)
        SPRITES[name] = LoadTexture(path.encode("utf-8"))


def unload_sprites():
    for texture in SPRITES.values():
        UnloadTexture(texture)
    SPRITES.clear()


def draw_sprite(name, x, y, width, height, flip_x=False):
    texture = SPRITES.get(name)
    if texture is None:
        return

    if flip_x:
        source = Rectangle(texture.width, 0, -texture.width, texture.height)
    else:
        source = Rectangle(0, 0, texture.width, texture.height)

    destination = Rectangle(x, y, width, height)
    DrawTexturePro(texture, source, destination, Vector2(0, 0), 0.0, WHITE)

#Needed to implement this as a fix for some animation, where I keep the height, but the width may vary, as some sprites are resized to one height, but not exactly the same width
def draw_sprite_keep_height(name, center_x, bottom_y, height, flip_x=False, rotation=0.0):
    texture = SPRITES.get(name)
    if texture is None:
        return

    width = height * (texture.width / texture.height)
    x = center_x - width / 2
    y = bottom_y - height

    if rotation == 0.0:
        draw_sprite(name, x, y, width, height, flip_x)
        return

    if flip_x:
        source = Rectangle(texture.width, 0, -texture.width, texture.height)
    else:
        source = Rectangle(0, 0, texture.width, texture.height)

    destination = Rectangle(center_x, y + height / 2, width, height)
    origin = Vector2(width / 2, height / 2)
    DrawTexturePro(texture, source, destination, origin, rotation, WHITE)
