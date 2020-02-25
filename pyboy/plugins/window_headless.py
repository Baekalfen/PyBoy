#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin import PyBoyWindowPlugin


class WindowHeadless(PyBoyWindowPlugin):

    def enabled(self):
        return self.pyboy_argv.get('window_type') == 'headless'
