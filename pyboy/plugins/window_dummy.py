#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin import BaseWindowPlugin


class DummyWindow(BaseWindowPlugin):
    def __init__(self, pyboy, argv):
        super().__init__(pyboy, argv)

        if not self.enabled():
            return

        pyboy.mb.disable_renderer = True

    def enabled(self):
        return self.argv.get('window_type') == 'dummy'
