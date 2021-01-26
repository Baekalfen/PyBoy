#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# imports
from pyboy.plugins.window_sdl2 import WindowSDL2 # isort:skip
from pyboy.plugins.window_open_gl import WindowOpenGL # isort:skip
from pyboy.plugins.window_headless import WindowHeadless # isort:skip
from pyboy.plugins.window_dummy import WindowDummy # isort:skip
from pyboy.plugins.debug import Debug # isort:skip
from pyboy.plugins.disable_input import DisableInput # isort:skip
from pyboy.plugins.auto_pause import AutoPause # isort:skip
from pyboy.plugins.record_replay import RecordReplay # isort:skip
from pyboy.plugins.rewind import Rewind # isort:skip
from pyboy.plugins.screen_recorder import ScreenRecorder # isort:skip
from pyboy.plugins.screenshot_recorder import ScreenshotRecorder # isort:skip
from pyboy.plugins.game_wrapper_super_mario_land import GameWrapperSuperMarioLand # isort:skip
from pyboy.plugins.game_wrapper_tetris import GameWrapperTetris # isort:skip
from pyboy.plugins.game_wrapper_kirby_dream_land import GameWrapperKirbyDreamLand # isort:skip
# imports end


def parser_arguments():
    # yield_plugins
    yield WindowSDL2.argv
    yield WindowOpenGL.argv
    yield WindowHeadless.argv
    yield WindowDummy.argv
    yield Debug.argv
    yield DisableInput.argv
    yield AutoPause.argv
    yield RecordReplay.argv
    yield Rewind.argv
    yield ScreenRecorder.argv
    yield ScreenshotRecorder.argv
    yield GameWrapperSuperMarioLand.argv
    yield GameWrapperTetris.argv
    yield GameWrapperKirbyDreamLand.argv
    # yield_plugins end
    pass


class PluginManager:
    def __init__(self, pyboy, mb, pyboy_argv):
        self.pyboy = pyboy

        # plugins_enabled
        self.window_sdl2 = WindowSDL2(pyboy, mb, pyboy_argv)
        self.window_sdl2_enabled = self.window_sdl2.enabled()
        self.window_open_gl = WindowOpenGL(pyboy, mb, pyboy_argv)
        self.window_open_gl_enabled = self.window_open_gl.enabled()
        self.window_headless = WindowHeadless(pyboy, mb, pyboy_argv)
        self.window_headless_enabled = self.window_headless.enabled()
        self.window_dummy = WindowDummy(pyboy, mb, pyboy_argv)
        self.window_dummy_enabled = self.window_dummy.enabled()
        self.debug = Debug(pyboy, mb, pyboy_argv)
        self.debug_enabled = self.debug.enabled()
        self.disable_input = DisableInput(pyboy, mb, pyboy_argv)
        self.disable_input_enabled = self.disable_input.enabled()
        self.auto_pause = AutoPause(pyboy, mb, pyboy_argv)
        self.auto_pause_enabled = self.auto_pause.enabled()
        self.record_replay = RecordReplay(pyboy, mb, pyboy_argv)
        self.record_replay_enabled = self.record_replay.enabled()
        self.rewind = Rewind(pyboy, mb, pyboy_argv)
        self.rewind_enabled = self.rewind.enabled()
        self.screen_recorder = ScreenRecorder(pyboy, mb, pyboy_argv)
        self.screen_recorder_enabled = self.screen_recorder.enabled()
        self.screenshot_recorder = ScreenshotRecorder(pyboy, mb, pyboy_argv)
        self.screenshot_recorder_enabled = self.screenshot_recorder.enabled()
        self.game_wrapper_super_mario_land = GameWrapperSuperMarioLand(pyboy, mb, pyboy_argv)
        self.game_wrapper_super_mario_land_enabled = self.game_wrapper_super_mario_land.enabled()
        self.game_wrapper_tetris = GameWrapperTetris(pyboy, mb, pyboy_argv)
        self.game_wrapper_tetris_enabled = self.game_wrapper_tetris.enabled()
        self.game_wrapper_kirby_dream_land = GameWrapperKirbyDreamLand(pyboy, mb, pyboy_argv)
        self.game_wrapper_kirby_dream_land_enabled = self.game_wrapper_kirby_dream_land.enabled()
        # plugins_enabled end

    def gamewrapper(self):
        # gamewrapper
        if self.game_wrapper_super_mario_land_enabled:
            return self.game_wrapper_super_mario_land
        if self.game_wrapper_tetris_enabled:
            return self.game_wrapper_tetris
        if self.game_wrapper_kirby_dream_land_enabled:
            return self.game_wrapper_kirby_dream_land
        # gamewrapper end
        return None

    def handle_events(self, events):
        # foreach windows events = [].handle_events(events)
        if self.window_sdl2_enabled:
            events = self.window_sdl2.handle_events(events)
        if self.window_open_gl_enabled:
            events = self.window_open_gl.handle_events(events)
        if self.window_headless_enabled:
            events = self.window_headless.handle_events(events)
        if self.window_dummy_enabled:
            events = self.window_dummy.handle_events(events)
        if self.debug_enabled:
            events = self.debug.handle_events(events)
        # foreach end
        # foreach plugins events = [].handle_events(events)
        if self.disable_input_enabled:
            events = self.disable_input.handle_events(events)
        if self.auto_pause_enabled:
            events = self.auto_pause.handle_events(events)
        if self.record_replay_enabled:
            events = self.record_replay.handle_events(events)
        if self.rewind_enabled:
            events = self.rewind.handle_events(events)
        if self.screen_recorder_enabled:
            events = self.screen_recorder.handle_events(events)
        if self.screenshot_recorder_enabled:
            events = self.screenshot_recorder.handle_events(events)
        if self.game_wrapper_super_mario_land_enabled:
            events = self.game_wrapper_super_mario_land.handle_events(events)
        if self.game_wrapper_tetris_enabled:
            events = self.game_wrapper_tetris.handle_events(events)
        if self.game_wrapper_kirby_dream_land_enabled:
            events = self.game_wrapper_kirby_dream_land.handle_events(events)
        # foreach end
        return events

    def post_tick(self):
        # foreach plugins [].post_tick()
        if self.disable_input_enabled:
            self.disable_input.post_tick()
        if self.auto_pause_enabled:
            self.auto_pause.post_tick()
        if self.record_replay_enabled:
            self.record_replay.post_tick()
        if self.rewind_enabled:
            self.rewind.post_tick()
        if self.screen_recorder_enabled:
            self.screen_recorder.post_tick()
        if self.screenshot_recorder_enabled:
            self.screenshot_recorder.post_tick()
        if self.game_wrapper_super_mario_land_enabled:
            self.game_wrapper_super_mario_land.post_tick()
        if self.game_wrapper_tetris_enabled:
            self.game_wrapper_tetris.post_tick()
        if self.game_wrapper_kirby_dream_land_enabled:
            self.game_wrapper_kirby_dream_land.post_tick()
        # foreach end

        self._post_tick_windows()
        self._set_title()

    def _set_title(self):
        # foreach windows [].set_title(self.pyboy.window_title)
        if self.window_sdl2_enabled:
            self.window_sdl2.set_title(self.pyboy.window_title)
        if self.window_open_gl_enabled:
            self.window_open_gl.set_title(self.pyboy.window_title)
        if self.window_headless_enabled:
            self.window_headless.set_title(self.pyboy.window_title)
        if self.window_dummy_enabled:
            self.window_dummy.set_title(self.pyboy.window_title)
        if self.debug_enabled:
            self.debug.set_title(self.pyboy.window_title)
        # foreach end
        pass

    def _post_tick_windows(self):
        # foreach windows [].post_tick()
        if self.window_sdl2_enabled:
            self.window_sdl2.post_tick()
        if self.window_open_gl_enabled:
            self.window_open_gl.post_tick()
        if self.window_headless_enabled:
            self.window_headless.post_tick()
        if self.window_dummy_enabled:
            self.window_dummy.post_tick()
        if self.debug_enabled:
            self.debug.post_tick()
        # foreach end
        pass

    def frame_limiter(self, speed):
        if speed <= 0:
            return
        # foreach windows done = [].frame_limiter(speed), if done: return
        if self.window_sdl2_enabled:
            done = self.window_sdl2.frame_limiter(speed)
            if done:
                return
        if self.window_open_gl_enabled:
            done = self.window_open_gl.frame_limiter(speed)
            if done:
                return
        if self.window_headless_enabled:
            done = self.window_headless.frame_limiter(speed)
            if done:
                return
        if self.window_dummy_enabled:
            done = self.window_dummy.frame_limiter(speed)
            if done:
                return
        if self.debug_enabled:
            done = self.debug.frame_limiter(speed)
            if done:
                return
        # foreach end

    def window_title(self):
        title = ""
        # foreach windows title += [].window_title()
        if self.window_sdl2_enabled:
            title += self.window_sdl2.window_title()
        if self.window_open_gl_enabled:
            title += self.window_open_gl.window_title()
        if self.window_headless_enabled:
            title += self.window_headless.window_title()
        if self.window_dummy_enabled:
            title += self.window_dummy.window_title()
        if self.debug_enabled:
            title += self.debug.window_title()
        # foreach end
        # foreach plugins title += [].window_title()
        if self.disable_input_enabled:
            title += self.disable_input.window_title()
        if self.auto_pause_enabled:
            title += self.auto_pause.window_title()
        if self.record_replay_enabled:
            title += self.record_replay.window_title()
        if self.rewind_enabled:
            title += self.rewind.window_title()
        if self.screen_recorder_enabled:
            title += self.screen_recorder.window_title()
        if self.screenshot_recorder_enabled:
            title += self.screenshot_recorder.window_title()
        if self.game_wrapper_super_mario_land_enabled:
            title += self.game_wrapper_super_mario_land.window_title()
        if self.game_wrapper_tetris_enabled:
            title += self.game_wrapper_tetris.window_title()
        if self.game_wrapper_kirby_dream_land_enabled:
            title += self.game_wrapper_kirby_dream_land.window_title()
        # foreach end
        return title

    def stop(self):
        # foreach windows [].stop()
        if self.window_sdl2_enabled:
            self.window_sdl2.stop()
        if self.window_open_gl_enabled:
            self.window_open_gl.stop()
        if self.window_headless_enabled:
            self.window_headless.stop()
        if self.window_dummy_enabled:
            self.window_dummy.stop()
        if self.debug_enabled:
            self.debug.stop()
        # foreach end
        # foreach plugins [].stop()
        if self.disable_input_enabled:
            self.disable_input.stop()
        if self.auto_pause_enabled:
            self.auto_pause.stop()
        if self.record_replay_enabled:
            self.record_replay.stop()
        if self.rewind_enabled:
            self.rewind.stop()
        if self.screen_recorder_enabled:
            self.screen_recorder.stop()
        if self.screenshot_recorder_enabled:
            self.screenshot_recorder.stop()
        if self.game_wrapper_super_mario_land_enabled:
            self.game_wrapper_super_mario_land.stop()
        if self.game_wrapper_tetris_enabled:
            self.game_wrapper_tetris.stop()
        if self.game_wrapper_kirby_dream_land_enabled:
            self.game_wrapper_kirby_dream_land.stop()
        # foreach end
        pass

    def handle_breakpoint(self):
        if self.debug_enabled:
            self.debug.handle_breakpoint()
