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
cdef int FIELD_ADDR, ROW_STRIDE, FIELD_ROWS, FIELD_COLS, FIELD_BYTES
cdef int CELL_OUTSIDE, CELL_BORDER, BLOCK_MIN, BLOCK_MAX, CELL_STAIRCASE, FLOOR_ROW
cdef dict CELL_GLYPHS
cdef int BLOCKS_ONES_ADDR, BLOCKS_TENS_ADDR, INITIAL_ONES_ADDR, INITIAL_TENS_ADDR
cdef int TIMER_SECONDS_ONES_ADDR, TIMER_SECONDS_TENS_ADDR, TIMER_MINUTES_ADDR
cdef int CLEAR_TARGET_ADDR, STAGE_ONES_ADDR, STAGE_TENS_ADDR
cdef int STAGE_LOADER_ADDR, STAGE_TABLE_ADDR, STAGE_COUNT, STAGE_DESCRIPTOR_BYTES, ROM_BANK
cdef int LAST_THROWN_ADDR, OAM_BUFFER_ADDR, OAM_BUFFER_BYTES
cdef tuple THROW_COUNT_ADDRS, THROW_BUTTONS, MOVE_BUTTONS
cdef int SETTLE_MAX_TICKS, SETTLE_STABLE_TICKS, BOOT_MAX_TICKS, BOOT_PRESS_EVERY
cdef int PRESS_TICKS, PROBE_MAX_HOLD


cdef class GameWrapperFlipull(PyBoyGameWrapper):
    cdef readonly int stage
    cdef readonly int blocks_remaining
    cdef readonly int blocks_initial
    cdef readonly int blocks_cleared
    cdef readonly int clear_target
    cdef readonly int time_left
    cdef readonly int throws
    cdef readonly int press_ticks
    cdef readonly str throw_button
    cdef readonly object player_sprite
    cdef readonly object held_sprite
    cdef readonly int row_pitch
    cdef readonly object row_span

    cdef list _forced_stage
    cdef bint _hook_registered

    cpdef list blocks(self)
    cpdef list row_blocks(self, row)
    cpdef list stages(self)

    cpdef int start_game(self, timer_div=*, stage=*, seed_ticks=*) except -1
