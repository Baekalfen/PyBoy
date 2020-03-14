#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import os
import time

from pyboy.logger import logger
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent

try:
    from PIL import Image
except ImportError:
    Image = None


FPS = 60


class ScreenRecorder(PyBoyPlugin):
    def __init__(self, *args):
        super().__init__(*args)

        self.gamename = self.pyboy.get_cartridge_title()
        self.recording = False
        self.frames = []

        if not Image:
            logger.warning("ScreenRecorder: Dependency \"Pillow\" could not be imported. Screen recording is disabled.")

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
            self.add_frame(self.pyboy.get_screen().get_screen_image())

    def add_frame(self, frame):
        if Image:
            # Pillow makes artifacts in the output, if we use 'RGB', which is PyBoy's default format
            self.frames.append(frame.convert('RGBA'))

    def save(self, path=None, fps=60):
        if not Image:
            logger.warning("ScreenRecorder: No recording to save. Missing dependency \"Pillow\".")
            return

        logger.info("ScreenRecorder saving...")

        if path is None:
            directory = os.path.join(os.path.curdir, "recordings")
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            path = os.path.join(directory, time.strftime(f"{self.gamename}-%Y.%m.%d-%H.%M.%S.gif"))

        if len(self.frames) > 0:
            self.frames[0].save(path, save_all=True, interlace=False,
                                loop=0, optimize=True,
                                append_images=self.frames[1:],
                                duration=int(round(1000 / fps, -1)))

            logger.info("Screen recording saved in {}".format(path))
        else:
            logger.error("Screen recording failed: no frames")
        self.frames = []