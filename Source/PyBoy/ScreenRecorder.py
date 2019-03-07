# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
try:
    import imageio
except:
    imageio = None
import numpy as np
import time
from PyBoy.Logger import logger


class ScreenRecorder:

    def __init__(self):
        logger.info("ScreenRecorder started")
        if imageio is None:
            logger.warning("ScreenRecorder: Dependency \"imageio\" could not be imported. Screen recording is disabled.")
            return
        self.frames = []
        self.color_mapping = {0x00FFFFFF: np.uint8([255, 255, 255]), 0x00999999: np.uint8([153, 153, 153]),
                              0x00555555: np.uint8([85, 85, 85]), 0x00000000: np.uint8([0, 0, 0])}

    def add_frame(self, frame):
        if imageio is None:
            return

        self.frames.append(frame)

    def save(self, format='gif', path=None, fps=60):
        if imageio is None:
            logger.warning("ScreenRecorder: No recording to save. Missing dependency \"imageio\".")
            return

        logger.info("ScreenRecorder saving...")
        if format not in ['gif']:
            raise Exception("Unsupported file format.")
        if fps < 1 or fps > 100:
            raise Exception("Invalid FPS. Choose a number between 1 and 100.")

        if path is None:
            recordings_folder = os.getcwd() + "/recordings"
            if not os.path.exists(recordings_folder):
                os.makedirs(recordings_folder)
            path = recordings_folder + "/recording " + time.strftime("%Y-%m-%d %H-%M-%S") + "." + format

        images = []
        for frame in self.frames:
            rgb_image = np.array([[self.color_mapping[frame[x,y]] for x in range(frame.shape[0])] for y in range(frame.shape[1])], dtype=np.uint8)
            images.append(rgb_image)

        if format == 'gif':
            imageio.mimsave(path, images, fps=fps)
        # TODO: Add mp4

        logger.info("Screen recording saved in {}".format(path))
