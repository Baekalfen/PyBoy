#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy
from pyboy.plugins.base_plugin import PyBoyWindowPlugin

logger = pyboy.logging.get_logger(__name__)


class WindowNull(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        if pyboy_argv.get("window") in ["headless", "dummy"]:
            logger.error(
                'Deprecated use of "headless" or "dummy" window. Change to "null" window instead. https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0'
            )

        pyboy.set_emulation_speed(0)

    def enabled(self):
        return self.pyboy_argv.get("window") in ["null", "headless", "dummy"]

    def set_title(self, title):
        logger.debug(title)
