#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.logger import logger


class WindowHeadless(PyBoyWindowPlugin):
    def enabled(self):
        return self.pyboy_argv.get("window_type") == "headless"

    def set_title(self, title):
        logger.info(title.encode())
