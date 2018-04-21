# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time
import pygame
import numpy as np
import warnings

from .. import CoreDump
from ..MathUint8 import getSignedInt8
from .. import WindowEvent
# from ..LCD import colorPalette, alphaMask
from FrameBuffer import SimpleFrameBuffer, ScaledFrameBuffer
from ..GameWindow import AbstractGameWindow

from ..Logger import logger

gameboyResolution = (160, 144)


# TODO: class PyGameGameWindow(AbstractGameWindow):
class PyGameGameWindow():
    def __init__(self, scale=1):
        self._scale = scale

        if self._scale != 1:
            logger.warn("Scaling set to %s. The implementation is temporary, which means scaling above 1 will impact performance." % self._scale)

        super(self.__class__, self).__init__(scale)

        self.debug = False

        CoreDump.windowHandle = self

        logger.debug("PyGame initialization")
        self.scanlineParameters = np.ndarray(shape=(gameboyResolution[0],4), dtype='uint8')

