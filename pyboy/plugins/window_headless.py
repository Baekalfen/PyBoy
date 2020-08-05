#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logger import logger
from pyboy.plugins.base_plugin import PyBoyWindowPlugin


class WindowHeadless(PyBoyWindowPlugin):
    def enabled(self):
        return self.pyboy_argv.get("window_type") == "headless"

    def set_title(self, title):
        logger.info(title)
