#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef class GameWrapperPokemonPinball(PyBoyGameWrapper):
    # Attributes extracted from memory
    cdef readonly int ball_saver_seconds_left
    cdef readonly int ball_size
    cdef readonly int ball_type
    cdef readonly int ball_x
    cdef readonly int ball_x_velocity
    cdef readonly int ball_y
    cdef readonly int ball_y_velocity
    cdef readonly int balls_left
    cdef readonly int current_map
    cdef readonly int current_stage
    cdef readonly long long score
    cdef readonly int special_mode
    cdef readonly int special_mode_active
    cdef readonly list pokedex

    # Dynamic values from hooks
    cdef public int diglett_stages_completed
    cdef public int diglett_stages_visited
    cdef public int evolution_count
    cdef public int evolution_failure_count
    cdef public int evolution_success_count
    cdef public int extra_balls_added
    cdef public bint game_over
    cdef public int gengar_stages_completed
    cdef public int gengar_stages_visited
    cdef public int great_ball_upgrades
    cdef public int ultra_ball_upgrades
    cdef public int map_change_attempts
    cdef public int map_change_successes
    cdef public int master_ball_upgrades
    cdef public int meowth_stages_completed
    cdef public int meowth_stages_visited
    cdef public int mewtwo_stages_completed
    cdef public int mewtwo_stages_visited
    cdef public int multiplier
    cdef public int pikachu_saver_charge
    cdef public int pikachu_saver_increments
    cdef public int pikachu_saver_used
    cdef public int pokemon_caught_in_session
    cdef public int pokemon_seen_in_session
    cdef public int roulette_slots_entered
    cdef public int roulette_slots_opened
    cdef public int seel_stages_completed
    cdef public int seel_stages_visited
    cdef public int slots_entered
    cdef public int slots_opened
    cdef public int lost_ball_during_saver

    cdef bint _unlimited_saver

    cpdef int start_game(self, timer_div=*, stage=*) except -1