#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef class GameWrapperSuperMarioBrosDeluxe(PyBoyGameWrapper):
    cdef readonly tuple world
    cdef readonly int level
    cdef int selected_level
    cdef int selected_level_set
    cdef bint level_selected
    cdef readonly int coins
    cdef readonly int lives_left
    cdef readonly int score
    cdef readonly int time_left
    cdef readonly int level_progress

    cpdef int start_game(self, timer_div=*, world_level=*, level=*, level_set=*, unlock_level_select=*) except -1
    cpdef void set_lives_left(self, int) noexcept
