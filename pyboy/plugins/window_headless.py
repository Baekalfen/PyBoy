#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.plugins.base_plugin import PyBoyWindowPlugin

logger = logging.getLogger(__name__)


class WindowHeadless(PyBoyWindowPlugin):
    def enabled(self):
        return self.pyboy_argv.get("window_type") == "headless"

    def set_title(self, title):
        logger.info(title)
