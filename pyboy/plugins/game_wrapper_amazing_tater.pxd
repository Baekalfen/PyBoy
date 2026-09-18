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
cdef int BOARD_ADDR, BOARD_COLS, BOARD_ROWS, ROW_STRIDE, BOARD_BYTES
cdef int BOARD_WIDTH_ADDR, BOARD_HEIGHT_ADDR, BOARD_X_OFFSET_ADDR, BOARD_Y_OFFSET_ADDR
cdef int GAME_MODE_ADDR, OVERLAY_ADDR, TATERS_ON_BOARD_ADDR, ACTIVE_TATER_ADDR, MENU_CURSOR_ADDR
cdef int LOAD_LEVEL, ROM_BANK
cdef int CODE_FLOOR, CODE_PIT, CODE_OUTSIDE, EXIT_CODE
cdef int BLOCK_MIN, BLOCK_MAX, SETTLED_MIN, SETTLED_MAX
cdef int ARM_MIN, ARM_MAX, ARM_PIT_MIN, ARM_PIT_MAX
cdef int PIVOT_MIN, PIVOT_MAX, TATER_MIN, TATER_MAX, WALL_MIN, WALL_MAX
cdef int SHAPE_TABLE_ADDR, SHAPE_TABLE_ENTRIES
cdef tuple LEVEL_SETS, DIRECTIONS
cdef int LEVEL_COUNT, MIN_ROOM, MAX_ROOM
cdef dict MODE_MENU_ROW, CELL_GLYPHS
cdef int SETTLE_MAX_TICKS, SETTLE_STABLE_TICKS, PRESS_TICKS, SWITCH_LOCKOUT_TICKS
cdef int BOOT_MAX_TICKS, BOOT_PRESS_TICKS, BOOT_STEP_TICKS
cdef int INTRO_MAX_TICKS, INTRO_STEP_TICKS, INTRO_FALLBACK_TICKS
cdef str SWITCH_BUTTON


cdef class GameWrapperAmazingTater(PyBoyGameWrapper):
    cdef readonly int level
    cdef readonly int taters_left
    cdef readonly int taters_home
    cdef readonly int taters_total
    cdef readonly int active_tater
    cdef readonly tuple room_size

    cdef list _forced_level
    cdef bint _hook_registered

    cpdef dict taters(self)
    cpdef list blocks(self)
    cpdef list pits(self)
    cpdef list turnstiles(self)

    cpdef int start_game(self, timer_div=*, level=*) except -1
