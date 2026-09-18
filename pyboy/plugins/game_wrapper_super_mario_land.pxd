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

cdef int ADDR_MARIO_STRUCT, MARIO_STRUCT_BYTES
cdef int MARIO_Y, MARIO_X, MARIO_ANIMATION, MARIO_FACING, MARIO_JUMP_PHASE
cdef int MARIO_ON_GROUND, MARIO_SPEED, MARIO_DIRECTION, MARIO_MOVING
cdef int FACING_LEFT, MARIO_X_SATURATES_AT
cdef dict MARIO_DIRECTIONS
cdef int ADDR_OBJECTS, OBJECT_SLOTS, OBJECT_STRIDE, OBJECT_EMPTY
cdef int OBJECT_TYPE, OBJECT_Y, OBJECT_X, OBJECT_ANIMATION
cdef int ADDR_SCY, ADDR_SCX


cdef class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    cdef readonly tuple world
    cdef readonly int coins
    cdef readonly int lives_left
    cdef readonly int score
    cdef readonly int time_left
    cdef readonly int level_progress
    cdef readonly tuple mario_position
    cdef readonly str mario_facing
    cdef readonly bint mario_on_ground
    cdef readonly int mario_speed
    cdef readonly str mario_direction
    cdef readonly int mario_jump_phase
    cdef readonly tuple camera

    cpdef int start_game(self, timer_div=*, world_level=*, unlock_level_select=*) except -1
    cpdef void set_lives_left(self, int) noexcept
    cpdef list object_slots(self)