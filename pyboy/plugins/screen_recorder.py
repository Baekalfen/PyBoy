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


class ScreenRecorder(PyBoyPlugin):
    def __init__(self, *args):
        super().__init__(*args)

        self.recording = False
        self.frames = []

    def handle_events(self, events):
        for event in events:
            if event == WindowEvent.SCREEN_RECORDING_TOGGLE:
                self.recording ^= True
                if not self.recording:
                    self.save()
                else:
                    logger.info("ScreenRecorder started")
                break
        return events

    def post_tick(self):
        # Plugin: Screen Recorder
        if self.recording:
            self.add_frame(self.pyboy.screen.image.copy())

    def add_frame(self, frame):
        # Pillow makes artifacts in the output, if we use 'RGB', which is PyBoy's default format
        self.frames.append(frame)

    def save(self, path=None, fps=60):
        logger.info("ScreenRecorder saving...")

        if path is None:
            directory = os.path.join(os.path.curdir, "recordings")
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            path = os.path.join(directory, time.strftime(f"{self.pyboy.cartridge_title}-%Y.%m.%d-%H.%M.%S.gif"))

        if len(self.frames) > 0:
            self.frames[0].save(
                path,
                save_all=True,
                interlace=False,
                loop=0,
                optimize=True,
                append_images=self.frames[1:],
                duration=int(round(1000 / fps, -1)),
            )

            logger.info("Screen recording saved in {}".format(path))
        else:
            logger.error("Screen recording failed: no frames")
        self.frames = []

    def enabled(self):
        if Image is None:
            logger.warning('%s: Missing dependency "Pillow". Recording disabled', __name__)
            return False
        return True
