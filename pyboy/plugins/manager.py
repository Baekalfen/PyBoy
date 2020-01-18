#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


class PyBoyPlugin:
    def __init__(self):
        self.argvs = []
        pass

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


class PluginManager(PyBoyPlugin):
    def __init__(self):
        pass

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


