#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin import PyBoyWindowPlugin

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class WindowDummy(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.mb.disable_renderer = True

    def enabled(self):
        return self.pyboy_argv.get("window_type") == "dummy"
