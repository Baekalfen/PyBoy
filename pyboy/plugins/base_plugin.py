#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

class PyBoyPlugin:
    argv = []

    def __init__(self, pyboy, kwargs):
        self.pyboy = pyboy
        self.kwargs = kwargs

    def handle_events(self, events):
        return events

    def post_tick(self):
        pass

    def pre_tick(self):
        pass

    def window_title(self):
        return ""

    def stop(self):
        pass

    def enabled(self):
        return True
