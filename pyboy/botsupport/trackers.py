#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.botsupport.sprite import Sprite
from pyboy.utils import flatten_list


class BaseTracker:
    def __init__(self, pyboy, mb):
        self.pyboy = pyboy
        self.mb = mb
        # self.tile_identifiers = tile_identifiers
        # self.singleton = singleton

    def get_objects(self):
        return []


# class SpriteGroup:
#     def __init__(self, sprites):
#         self.sprites = sprites
#         sprite_width, sprite_height = self.sprites[0].shape
#         x0 = min([s.x for s in self.sprites])
#         x1 = max([s.x for s in self.sprites]) + sprite_width # We want the outer coordinates
#         y0 = min([s.y for s in self.sprites])
#         y1 = max([s.y for s in self.sprites]) + sprite_height # We want the outer coordinates
#         self.bbox = (x0, y0, x1, y1)

#     def get_objects(self):
#         return [Sprite(s) for s in self.sprites]

#     @property
#     def shape(self):
#         """
#         Sprites can be set to be 8x8 or 8x16 pixels (16 pixels tall). This is defined globally for the rendering
#         hardware, so it's either all sprites using 8x16 pixels, or all sprites using 8x8 pixels.

#         Returns:
#             (int, int): The width and height of the sprite.
#         """
#         return (self.bbox[2] - self.bbox[0], self.bbox[3] - self.bbox[1])

#     @property
#     def y(self):
#         """
#         The Y-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

#         Returns:
#             int: Y-coordinate
#         """
#         # Documentation states the y coordinate needs to be subtracted by 16
#         return self.bbox[0]

#     @property
#     def x(self):
#         """
#         The X-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

#         Returns:
#             int: X-coordinate
#         """
#         # Documentation states the x coordinate needs to be subtracted by 8
#         return self.bbox[1]

#     def __repr__(self):
#         return f"SpriteGroup [{', '.join([str(s.sprite_index) for s in self.sprites])}]: Position: ({self.x}, {self.y}), Shape: {self.shape}"


class SpriteTracker(BaseTracker):
    def get_objects(self):
        return [sprite for sprite in (Sprite(self.mb, s) for s in range(40)) if sprite.on_screen]
        # matching_sprites = flatten_list(self.pyboy.get_sprite_by_tile_identifier(self.tile_identifiers))
        # sprites = [Sprite(self.mb, s) for s in matching_sprites]
        # if self.singleton:
        #     if matching_sprites == []:
        #         return None
        #     else:
        #         return SpriteGroup(sprites)
        # else:
        #     return sprites


class TileTracker(BaseTracker):
    pass
