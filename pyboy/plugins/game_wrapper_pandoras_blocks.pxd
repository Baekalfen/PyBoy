#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger

cdef int TILES
cdef tuple PIECE_NAMES, GAME_OVER_TILES
cdef dict piece_table
cdef list TITLE_SCREEN_TILES
cdef int FIELD_EMPTY_TILE, PIECE_TILE_START, PIECE_TILE_END
cdef int GAME_STATE_ADDR, GAMEPLAY_STATE
cdef int MODE_ADDR, MODE_GAME_OVER, MODE_PRE_GAME_OVER
cdef int NEXT_BLOCK_ADDR, LEVEL_ADDR, SCORE_ADDR

cdef class GameWrapperPandorasBlocks(PyBoyGameWrapper):
    cdef readonly int score
    cdef readonly int level
    cdef readonly int lines

    cpdef void set_block(self, str) except *
    cpdef str next_block(self)
