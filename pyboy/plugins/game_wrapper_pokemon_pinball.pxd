#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef class GameWrapperPokemonPinball(PyBoyGameWrapper):
    cdef public long long score
    cdef public int balls_left
    cdef public bint game_over
    cdef public bint saver_active
    cdef public int ball_type
    cdef public int multiplier
    cdef public int current_stage
    cdef int ball_size
    cdef public int ball_saver_seconds_left
    cdef public int pokemon_caught_in_session
    cdef public int pokemon_seen_in_session
    cdef public int actual_pokemon_caught_in_session
    cdef public int evolution_count
    cdef public list pokedex
    cdef public int pikachu_saver_charge
    cdef public int pikachu_saver_increments
    cdef public int pikachu_saver_used
    cdef public int current_map
    cdef public int map_change_attempts
    cdef public int map_change_successes
    cdef public int evolution_success_count
    cdef public int evolution_failure_count
    cdef public int great_ball_upgrades
    cdef public int ultra_ball_upgrades
    cdef public int master_ball_upgrades
    cdef public int extra_balls_added
    cdef public int slots_opened
    cdef public int slots_entered
    cdef public int diglett_stages_completed
    cdef public int diglett_stages_visited
    cdef public int gengar_stages_completed
    cdef public int gengar_stages_visited
    cdef public int meowth_stages_completed
    cdef public int meowth_stages_visited
    cdef public int mewtwo_stages_completed
    cdef public int mewtwo_stages_visited
    cdef public int seel_stages_completed
    cdef public int seel_stages_visited
    #cdef public int left_diglett_hits
    #cdef public int first_left_diglett_hits
    #cdef public int second_left_diglett_hits
    #cdef public int third_left_diglett_hits
    #cdef public int right_diglett_hits
    #cdef public int first_right_diglett_hits
    #cdef public int second_right_diglett_hits
    #cdef public int third_right_diglett_hits
    cdef public int ball_x
    cdef public int ball_y
    cdef public int ball_x_velocity
    cdef public int ball_y_velocity


    cdef bint _unlimited_saver

    cpdef void start_game(self, timer_div=*, stage=*) noexcept
    cpdef void reset_game(self, timer_div=*) noexcept