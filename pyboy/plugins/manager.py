#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# imports
from pyboy.plugins.window_sdl2 import WindowSDL2  # isort:skip
from pyboy.plugins.window_open_gl import WindowOpenGL  # isort:skip
from pyboy.plugins.window_headless import WindowHeadless  # isort:skip
from pyboy.plugins.window_dummy import WindowDummy  # isort:skip
from pyboy.plugins.debug import Debug  # isort:skip
from pyboy.plugins.disable_input import DisableInput  # isort:skip
from pyboy.plugins.auto_pause import AutoPause  # isort:skip
from pyboy.plugins.record_replay import RecordReplay  # isort:skip
from pyboy.plugins.rewind import Rewind  # isort:skip
from pyboy.plugins.screen_recorder import ScreenRecorder  # isort:skip
from pyboy.plugins.screenshot_recorder import ScreenshotRecorder  # isort:skip
from pyboy.plugins.base_plugin import PyBoyGameWrapper  # isort:skip
from pyboy.plugins.base_plugin import PyBoyPlugin  # isort:skip
from pyboy.plugins.base_plugin import PyBoyWindowPlugin  # isort: skip
from pyboy.plugins.game_wrapper_super_mario_land import GameWrapperSuperMarioLand  # isort:skip
from pyboy.plugins.game_wrapper_tetris import GameWrapperTetris  # isort:skip
from pyboy.plugins.game_wrapper_kirby_dream_land import GameWrapperKirbyDreamLand  # isort:skip

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
        self.window_open_gl = WindowOpenGL(pyboy, mb, pyboy_argv)
        self.window_headless = WindowHeadless(pyboy, mb, pyboy_argv)
        self.window_dummy = WindowDummy(pyboy, mb, pyboy_argv)
        self.debug = Debug(pyboy, mb, pyboy_argv)
        self.disable_input = DisableInput(pyboy, mb, pyboy_argv)
        self.auto_pause = AutoPause(pyboy, mb, pyboy_argv)
        self.record_replay = RecordReplay(pyboy, mb, pyboy_argv)
        self.rewind = Rewind(pyboy, mb, pyboy_argv)
        self.screen_recorder = ScreenRecorder(pyboy, mb, pyboy_argv)
        self.screenshot_recorder = ScreenshotRecorder(pyboy, mb, pyboy_argv)

        self.game_wrapper_super_mario_land = GameWrapperSuperMarioLand(pyboy, mb, pyboy_argv)
        self.game_wrapper_tetris = GameWrapperTetris(pyboy, mb, pyboy_argv)
        self.game_wrapper_kirby_dream_land = GameWrapperKirbyDreamLand(pyboy, mb, pyboy_argv)

        # all plugins
        self.plugins: list[PyBoyPlugin] = [
            self.window_sdl2,
            self.window_open_gl,
            self.window_headless,
            self.window_dummy,
            self.debug,
            self.disable_input,
            self.auto_pause,
            self.record_replay,
            self.rewind,
            self.screen_recorder,
            self.screenshot_recorder,
            self.game_wrapper_super_mario_land,
            self.game_wrapper_tetris,
            self.game_wrapper_kirby_dream_land,
        ]

        # only window plugins
        self.window_plugins: list[PyBoyWindowPlugin] = [
            self.window_sdl2,
            self.window_open_gl,
            self.window_headless,
            self.window_dummy,
            self.debug,
        ]

        # only game wrappers
        self.game_wrappers: list[PyBoyGameWrapper] = [
            self.game_wrapper_super_mario_land,
            self.game_wrapper_tetris,
            self.game_wrapper_kirby_dream_land,
        ]

        self.active_game_wrapper: PyBoyGameWrapper | None = None

        # plugins_enabled end

    def add_plugin(self, plugin):
        if isinstance(plugin, PyBoyGameWrapper):
            self.game_wrappers.append(plugin)
        elif isinstance(plugin, PyBoyWindowPlugin):
            self.window_plugins.append(plugin)
        self.plugins.append(plugin)

    def gamewrapper(self):
        # gamewrapper
        if self.active_game_wrapper:
            return self.active_game_wrapper
        for game_wrapper in self.game_wrappers:
            if game_wrapper.enabled:
                self.active_game_wrapper = game_wrapper
                return game_wrapper
        # gamewrapper end
        return None

    def handle_events(self, events):
        # foreach windows events = [].handle_events(events)
        for plugin in self.plugins:
            if plugin.enabled:
                events = plugin.handle_events(events)
        # foreach end
        return events

    def post_tick(self):
        # foreach plugins [].post_tick()
        for plugin in self.plugins:
            if plugin.enabled:
                plugin.post_tick()
        # foreach end

        self._post_tick_windows()
        self._set_title()

    def _set_title(self):
        # foreach windows [].set_title(self.pyboy.window_title)
        for window_plugin in self.window_plugins:
            if window_plugin.enabled:
                window_plugin.set_title(self.pyboy.window_title)
        # foreach end
        pass

    def _post_tick_windows(self):
        # foreach windows [].post_tick()
        for window_plugin in self.window_plugins:
            if window_plugin.enabled:
                window_plugin.post_tick()
        # foreach end

    def frame_limiter(self, speed):
        if speed <= 0:
            return
        # foreach windows done = [].frame_limiter(speed), if done: return
        for window_plugin in self.window_plugins:
            if window_plugin.enabled:
                done = window_plugin.frame_limiter(speed)
                if done:
                    return
        # foreach end

    def window_title(self):
        title = ""
        # foreach windows title += [].window_title()
        for plugin in self.plugins:
            if plugin.enabled:
                title += plugin.window_title()
        # foreach end
        return title

    def stop(self):
        # foreach windows [].stop()
        for plugin in self.plugins:
            if plugin.enabled:
                plugin.stop()
        # foreach end
        pass

    def handle_breakpoint(self):
        if self.debug.enabled:
            self.debug.handle_breakpoint()
