#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import time

import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None

FPS = 60


class ScreenshotRecorder(PyBoyPlugin):
    def handle_events(self, events):
        for event in events:
            if event == WindowEvent.SCREENSHOT_RECORD:
                self.save()
                break
        return events

    def save(self, path=None):
        if path is None:
            directory = os.path.join(os.path.curdir, "screenshots")
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            path = os.path.join(directory, time.strftime(f"{self.pyboy.cartridge_title}-%Y.%m.%d-%H.%M.%S.png"))

        self.pyboy.screen.image.save(path)

        logger.info("Screenshot saved in {}".format(path))

    def enabled(self):
        if Image is None:
            logger.warning('%s: Missing dependency "Pillow". Screenshots disabled', __name__)
            return False
        return True
