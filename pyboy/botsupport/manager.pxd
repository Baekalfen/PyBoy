#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from pyboy.core.mb cimport Motherboard
from pyboy.botsupport.screen cimport Screen
from pyboy.botsupport.sprite cimport Sprite
from pyboy.botsupport.tile cimport Tile
from pyboy.botsupport.tilemap cimport TileMap



cdef class BotSupportManager:
    cdef object pyboy
    cdef Motherboard mb
    cpdef Screen screen(self)
    cpdef Sprite sprite(self, int)
    cpdef list sprite_by_tile_identifier(self, list, on_screen=*)
    cpdef Tile tile(self, int)
    cpdef TileMap tilemap_background(self)
    cpdef TileMap tilemap_window(self)
