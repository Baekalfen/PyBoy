#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .autopause import AutoPause
from .base_plugin import PyBoyPlugin
from .disable_input import DisableInput
from .record_replay import RecordReplay
from .rewind import Rewind
from .screenrecorder import ScreenRecorder

# parser.add_argument('-w', '--window', default='SDL2', type=str,
#         help='Specify "window". Options: SDL2 (default), OpenGL, headless, dummy')
# hide window
# parser.add_argument('-s', '--scale', default=3, type=int, help='The scaling multiplier for the window')
# parser.add_argument('-d', '--debug', action='store_true', help='Enable emulator debugging mode')

plugins = [DisableInput, AutoPause, RecordReplay, Rewind, ScreenRecorder]

def get_parser_arguments():
    for p in plugins:
        yield p.argv


class PluginManager(PyBoyPlugin):
    def __init__(self, pyboy, argv):
        self.plugins = []

        for plugin in plugins:
            p = plugin(pyboy, argv)
            if p.enabled():
                self.plugins.append(p)

    def handle_events(self, events):
        for p in self.plugins:
            events = p.handle_events(events)
        return events

    def pre_tick(self):
        for p in self.plugins:
             p.pre_tick()

    def post_tick(self):
        for p in self.plugins:
            p.post_tick()

    def window_title(self):
        title = ""
        for p in self.plugins:
            title += p.handle_events()
        return title

    def stop(self):
        for p in self.plugins:
            p.stop()
