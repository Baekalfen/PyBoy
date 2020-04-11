#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin import PyBoyPlugin


class DisableInput(PyBoyPlugin):
    argv = [("--no-input", {"action": "store_true", "help": "Disable all user-input (mostly for autonomous testing)"})]

    def handle_events(self, events):
        return []

    def enabled(self):
        return self.pyboy_argv.get("no_input")
