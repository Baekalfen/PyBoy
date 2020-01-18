#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin import PyBoyPlugin


class DisableInput(PyBoyPlugin):
    def handle_events(self, pyboy, events):
        return []
