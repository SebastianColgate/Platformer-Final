import os
from raylib import *
from pyray import *


SPRITES = {}


def load_sprites():
    texture_folder = os.path.join(os.path.dirname(__file__), "textures")
    files = {
        "background": "background.png",
        "player": "player.png",
        "player_stand": "Player Standing.png",
        "player_swim": "playerswim.png",
        "enemy": "enemy.png",
        "poison_jar": "poison_jar.png",
        "antidote_jar": "antidote_jar.png",
        "dirt": "dirt.png",
        "grass": "grass.png",
        "water": "water_tile.png",
        "poison_water": "poison_water_tile.png",
        "exit_locked": "exit_locked.png",
        "exit_open": "exit_open.png",
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
