#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy
from pyboy import utils
from pyboy.plugins.base_plugin import PyBoyWindowPlugin

logger = pyboy.logging.get_logger(__name__)


class WindowDummy(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

    def enabled(self):
        return self.pyboy_argv.get("window_type") == "dummy"

    def set_title(self, title):
        logger.debug(title)
