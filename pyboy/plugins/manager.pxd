#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
# imports
from pyboy.plugins.window_sdl2 cimport WindowSDL2
from pyboy.plugins.window_open_gl cimport WindowOpenGL
from pyboy.plugins.window_headless cimport WindowHeadless
from pyboy.plugins.window_dummy cimport WindowDummy
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
# imports end
from pyboy.plugins.base_plugin cimport PyBoyPlugin, PyBoyWindowPlugin



cdef class PluginManager:
    cdef object pyboy

    # plugin_cdef
    cdef public WindowSDL2 window_sdl2
    cdef public WindowOpenGL window_open_gl
    cdef public WindowHeadless window_headless
    cdef public WindowDummy window_dummy
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
    cdef bint window_sdl2_enabled
    cdef bint window_open_gl_enabled
    cdef bint window_headless_enabled
    cdef bint window_dummy_enabled
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
    # plugin_cdef end

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin, events=list)
    cdef list handle_events(self, list)

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin)
    cdef void post_tick(self)

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin)
    cdef void _post_tick_windows(self)

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin)
    cdef void frame_limiter(self, int)

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin)
    cdef str window_title(self)

    @cython.locals(p=PyBoyPlugin, w=PyBoyWindowPlugin)
    cdef void stop(self)
