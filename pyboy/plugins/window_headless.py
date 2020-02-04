#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin import BaseWindowPlugin


class HeadlessWindow(BaseWindowPlugin):

    def enabled(self):
        return self.argv.get('window_type') == 'headless'
