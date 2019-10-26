#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import os
import time

from .logger import logger

try:
    from PIL import Image
except ImportError:
    Image = None


FPS = 60


class ScreenRecorder:

    def __init__(self, gamename):
        self.gamename = gamename

        if Image:
            logger.info("ScreenRecorder started")
            self.frames = []
        else:
            logger.warning("ScreenRecorder: Dependency \"Pillow\" could not be imported. "
                           "Screen recording is disabled.")

    def add_frame(self, frame):
        if Image:
            self.frames.append(frame)

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

        if self.frames:
            self.frames[0].save(path, save_all=True, interlace=False,
                                loop=0, optimize=True,
                                append_images=self.frames[1:],
                                duration=int(round(1000 / fps, -1)))

            logger.info("Screen recording saved in {}".format(path))
        else:
            logger.error("Screen recording failed: no frames")
