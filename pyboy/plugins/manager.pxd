#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython


from pyboy.logging.logging cimport Logger
from pyboy.plugins.auto_pause cimport AutoPause

# imports
from pyboy.plugins.window_sdl2 cimport WindowSDL2
from pyboy.plugins.window_open_gl cimport WindowOpenGL
from pyboy.plugins.window_null cimport WindowNull
from pyboy.plugins.debug cimport Debug
from pyboy.plugins.disable_input cimport DisableInput
from pyboy.plugins.auto_pause cimport AutoPause
from pyboy.plugins.record_replay cimport RecordReplay
from pyboy.plugins.rewind cimport Rewind
from pyboy.plugins.screen_recorder cimport ScreenRecorder
from pyboy.plugins.screenshot_recorder cimport ScreenshotRecorder
from pyboy.plugins.game_wrapper_super_mario_land cimport GameWrapperSuperMarioLand
from pyboy.plugins.game_wrapper_tetris cimport GameWrapperTetris
from pyboy.plugins.game_wrapper_kirby_dream_land cimport GameWrapperKirbyDreamLand
from pyboy.plugins.game_wrapper_pokemon_gen1 cimport GameWrapperPokemonGen1
# imports end

cdef Logger logger


cdef class PluginManager:
    cdef object pyboy

    # plugin_cdef
    cdef public WindowSDL2 window_sdl2
    cdef public WindowOpenGL window_open_gl
    cdef public WindowNull window_null
    cdef public Debug debug
    cdef public DisableInput disable_input
    cdef public AutoPause auto_pause
    cdef public RecordReplay record_replay
    cdef public Rewind rewind
    cdef public ScreenRecorder screen_recorder
    cdef public ScreenshotRecorder screenshot_recorder
    cdef public GameWrapperSuperMarioLand game_wrapper_super_mario_land
    cdef public GameWrapperTetris game_wrapper_tetris
    cdef public GameWrapperKirbyDreamLand game_wrapper_kirby_dream_land
    cdef public GameWrapperPokemonGen1 game_wrapper_pokemon_gen1
    cdef bint window_sdl2_enabled
    cdef bint window_open_gl_enabled
    cdef bint window_null_enabled
    cdef bint debug_enabled
    cdef bint disable_input_enabled
    cdef bint auto_pause_enabled
    cdef bint record_replay_enabled
    cdef bint rewind_enabled
    cdef bint screen_recorder_enabled
    cdef bint screenshot_recorder_enabled
    cdef bint game_wrapper_super_mario_land_enabled
    cdef bint game_wrapper_tetris_enabled
    cdef bint game_wrapper_kirby_dream_land_enabled
    cdef bint game_wrapper_pokemon_gen1_enabled
    # plugin_cdef end

    cdef list handle_events(self, list) noexcept
    cdef void post_tick(self) noexcept
    cdef void _post_tick_windows(self) noexcept
    cdef void frame_limiter(self, int) noexcept
    cdef str window_title(self) noexcept
    cdef void stop(self) noexcept
    cdef void _set_title(self) noexcept
    cdef void handle_breakpoint(self) noexcept
