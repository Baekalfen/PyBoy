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
cdef int GRID_ADDR, GRID_ROWS, GRID_COLS, CELL_STRIDE, ROW_STRIDE, GRID_BYTES
cdef int CURSOR_COL_ADDR, CURSOR_ROW_ADDR
cdef int TOTAL_BLOCKS_ADDR, BLOCKS_REMAINING_ADDR
cdef int STAGE_INDEX_ADDR, STAGE_LOADER_ENTRY
cdef int CELL_EMPTY, CELL_CLEARING, CELL_LEDGE, CELL_OUTSIDE, CELL_WALL
cdef int BLOCK_MIN, BLOCK_MAX, BLOCK_TYPE_OFFSET
cdef dict CELL_GLYPHS, MENU_ENTRIES
cdef int OAM_BUFFER_ADDR, OAM_BUFFER_BYTES, MENU_ARROW_TILE
cdef int MENU_PRESS_TICKS, MENU_GAP_TICKS, TITLE_MAX_TICKS
cdef int PASSWORD_TABLE_BANK, PASSWORD_TABLE_ADDR, PASSWORD_LENGTH, PASSWORD_STRIDE
cdef str PASSWORD_ALPHABET
cdef int TEXT_LETTER_BASE, TEXT_PERIOD, TILE_PERIOD
cdef int SLOT_Y, EMPTY_SLOT_TILE, ENTRY_PITCH
cdef tuple SLOT_X, ENTRY_ORIGIN, END_CELL
cdef int SETTLE_MAX_TICKS, SETTLE_STABLE_TICKS
cdef int BOOT_MAX_TICKS, BOOT_PRESS_EVERY
cdef int INTRO_MAX_TICKS, INTRO_STEP_TICKS, INTRO_PRESS_TICKS


cdef class GameWrapperPuzznic(PyBoyGameWrapper):
    cdef readonly int stage
    cdef readonly int blocks_total
    cdef readonly int blocks_remaining
    cdef readonly int blocks_cleared
    cdef readonly tuple cursor

    cdef list _forced_stage
    cdef bint _hook_registered

    cpdef list blocks(self)
    cpdef dict block_counts(self)
    cpdef list passwords(self)

    cpdef int start_game(self, timer_div=*, stage=*, password=*) except -1
