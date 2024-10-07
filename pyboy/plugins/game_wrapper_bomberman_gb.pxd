cimport cython
cimport numpy as np

from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef class GameWrapperBombermanGB(PyBoyGameWrapper):
    cdef readonly tuple _GAME_AREA_SHAPE
    cdef readonly list _ENEMY

    cdef readonly int AGENT_DEAD
    cdef readonly int AGENT_STATS_BOMB_PLACED
    cdef readonly int AGENT_STATS_BOMB_MAX
    cdef readonly int AGENT_STATS_BOMB_RANGE

    cdef readonly dict _COORD_MEM_ADDR[str, (int,int)]
    cdef readonly dict _ENEMY_DEAD_MEM_ADDR[str, int]

    cdef readonly int BOMBINFO_START
    cdef readonly int BOMBINGO_END

    cdef list _ENEMY_ALIVE

    cdef bint _agent_dead
    cdef int _agent_bombs_available
    cdef int _agent_bomb_max
    cdef int _agent_bomb_range
    cdef list _agent_bombs

    cdef bint _score_agent_kill
    cdef bint _agent_suicide

    cdef bint _score_agent_placed_bomb 
    cdef int _bomb_block_hits
    
    cdef int _min_global_distance
    cdef int _score_min_global_dist
    cdef int _last_min_enemy_distance
    cdef int _score_last_dist
    cdef bint _agent_in_bomb_range

    cpdef void start_game(self, timer_div=*, enemies=*, int win=*, int time=*) noexcept
    cpdef void reset_game(self, timer_div=*, enemies=*, int win=*, int time=*) noexcept
    cpdef bint game_over(self) noexcept
    cdef void _reset_settings(self) noexcept
    cpdef void post_tick(self) noexcept

    cpdef (int,int,int,int,int,int,int,int, int, int, int, int) score(self) noexcept
    
    cdef bint _suicide(self) noexcept
    cdef np.ndarray[np.uint8_t, ndim=2] _get_explosion_map(self) noexcept
    cdef (int, int) _player_game_area_coordinate(self, str player) noexcept
    cdef void _update_enemy_alive_cache(self) noexcept
    cdef void _check_agent_kill(self, str enemy) noexcept
    cdef void _update_agent_bomb_info(self) noexcept
    cdef int _agent_placed_bomb(self) noexcept
    cdef void _check_bomb_hits(self, int x_coord, int y_coord) noexcept
    cdef bint _check_bomb_x_hits(self, list coord_to_check, int y_coord, area_cache)
    cdef bint _check_bomb_y_hits(self, list coord_to_check, int x_coord, area_cache)
    cdef void _distance_checks(self) noexcept

    cdef bint _agent_bomb_max_increased(self) noexcept
    cdef bint _agent_bomb_range_increased(self) noexcept


    cdef void _navigate_to_password_screen(self) noexcept
    cdef void _handle_password_screen(self) noexcept
    cdef void _set_enemies(self, int n_enemy=*, bint shuffle=*) noexcept
    cdef void _handle_rules_screen(self, int win=*, int time=*) noexcept
    cdef void _select_stage_screen(self,  int stage=*) noexcept
    
    cpdef void _save_picture(self, name=*) noexcept
    
    cdef np.ndarray[np.uint8_t, ndim=1] _minimal_mapping(self) noexcept
    
