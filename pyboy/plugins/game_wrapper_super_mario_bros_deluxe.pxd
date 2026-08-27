#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef class GameWrapperSuperMarioBrosDeluxe(PyBoyGameWrapper):
    cdef readonly tuple world
    cdef readonly int level
    cdef int selected_level
    cdef bint selected_super_player_levels
    cdef bint level_selected
    cdef readonly int coins
    cdef readonly int lives_left
    cdef readonly int score
    cdef readonly int time_left
    cdef readonly int level_progress
    cdef readonly bint stuck
    cdef readonly int stuck_frames
    cdef object metatile_interaction_types
    cdef int custom_level_sequence_index
    cdef bint custom_next_level_prepared
    cdef int _stuck_last_progress
    cdef bint _stuck_in_level

    cpdef int start_game(
        self,
        timer_div=*,
        world_level=*,
        level=*,
        super_player_levels=*,
        challenge=*,
        unlock_level_select=*,
    ) except -1
    cpdef void set_lives_left(self, int) noexcept
