#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.plugins.base_plugin import PyBoyWindowPlugin

logger = logging.getLogger(__name__)


class WindowHeadless(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

    def enabled(self):
        return self.pyboy_argv.get("window_type") == "headless"

    def set_title(self, title):
        logger.debug(title)
