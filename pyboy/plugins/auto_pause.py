#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent


class AutoPause(PyBoyPlugin):
    argv = [("--autopause", {"action": "store_true", "help": "Enable auto-pausing when window looses focus"})]

    def handle_events(self, events):
        for event in events:
            if event == WindowEvent.WINDOW_UNFOCUS:
                events.append(WindowEvent(WindowEvent.PAUSE))
            elif event == WindowEvent.WINDOW_FOCUS:
                events.append(WindowEvent(WindowEvent.UNPAUSE))
        return events

    def enabled(self):
        return self.pyboy_argv.get("autopause")
