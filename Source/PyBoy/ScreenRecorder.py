#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
import time
import os

try:
    import imageio
except:
    imageio = None

from .Logger import logger


class ScreenRecorder:

    def __init__(self, colorScheme):
        logger.info("ScreenRecorder started")
        if imageio is None:
            logger.warning("ScreenRecorder: Dependency \"imageio\" could not be imported. Screen recording is disabled.")
            return
        self.frames = []
        self.colorScheme = colorScheme

    def add_frame(self, frame):
        if imageio is None:
            return

        self.frames.append(np.asarray(frame, dtype=np.uint32))

    def save(self, format='gif', path=None, fps=60):
        if imageio is None:
            logger.warning("ScreenRecorder: No recording to save. Missing dependency \"imageio\".")
            return

        assert format not in ['gif'], "Unsupported file format."
        assert 1 <= fps <= 60, "Invalid FPS. Choose a number between 1 and 60."

        logger.info("ScreenRecorder saving...")

        if path is None:
            recordings_folder = os.getcwd() + "/recordings"
            if not os.path.exists(recordings_folder):
                os.makedirs(recordings_folder)
            path = recordings_folder + "/recording " + time.strftime("%Y-%m-%d %H-%M-%S") + "." + format

        images = []
        for frame in self.frames:
            # Reshape uint32->4xuint8. Strip alpha channel.
            # Transpose dimensions, but not colors. Otherwise the recording comes out mirrored.
            rgb_image = frame.view(np.uint8).reshape(frame.shape + (4,))
            if self.colorScheme == "RGBA":
                rgb_image = rgb_image[:,:,1:]
            elif self.colorScheme == "ARGB":
                rgb_image = rgb_image[:,:,:-1]
            else:
                logger.error("Unsupported color scheme! Trying to continue.")
            images.append(rgb_image)

        if format == 'gif':
            imageio.mimsave(path, images, fps=fps)
        # TODO: Add mp4

        logger.info("Screen recording saved in {}".format(path))
