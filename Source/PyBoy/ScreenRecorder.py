# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import os
import time

from PIL import Image

from .Logger import logger


class ScreenRecorder:

    def __init__(self, colorScheme):
        logger.info("ScreenRecorder started")
        self.frames = []

    def add_frame(self, frame):
        # self.frames.append(Image.frombytes("RGBA", (160, 144), frame))
        self.frames.append(Image.fromarray(frame))

    def save(self, path=None, *, fps=60):

        logger.info("ScreenRecorder saving...")

        if path is None:
            directory = os.path.join(os.path.curdir, "Recordings")
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            path = os.path.join(directory, time.strftime("Recording-%Y-%m-%d-%H:%M:%S.gif"))

        if self.frames:
            self.frames[0].save(path, save_all=True, interlace=False,
                                duration=1000/fps, optimize=True,
                                append_images=self.frames[1:])
            logger.info("Screen recording saved in {}".format(path))
        else:
            logger.error("Screen recording failed: no frames")
