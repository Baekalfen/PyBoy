#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.plugins.base_plugin import PyBoyWindowPlugin

logger = logging.getLogger(__name__)


class WindowDummy(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        pyboy._rendering(False)
        logger.warning(
            'This window type does not support frame-limiting. `pyboy.set_emulation_speed(...)` will have no effect, as it\'s always running at full speed.'
        )

    def enabled(self):
        return self.pyboy_argv.get("window_type") == "dummy"

    def set_title(self, title):
        logger.debug(title)
