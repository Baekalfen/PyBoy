#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy import windowevent
from pyboy.plugins.base_plugin import PyBoyPlugin


class AutoPause(PyBoyPlugin):
    argv = [('--autopause', {'action': 'store_true', "help": 'Enable auto-pausing when window looses focus'})]

    def handle_events(self, events):
        for event in events:
            if event == windowevent.WINDOW_UNFOCUS:
                events.append(windowevent.PAUSE)
            elif event == windowevent.WINDOW_FOCUS:
                events.append(windowevent.UNPAUSE)
        return events

    def enabled(self):
        return self.argv.get('autopause')
