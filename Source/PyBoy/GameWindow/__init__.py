#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Thoams Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#


from ..Logger import logger
from .AbstractGameWindow import AbstractGameWindow

try:
    from .GameWindow_SDL2 import SdlGameWindow
except:
    logger.warning("Failed to load SDL2 GameWindow.")

try:
    from .GameWindow_Scanline import ScanlineGameWindow
except:
    logger.warning("Failed to load Scanline GameWindow")

try:
    from .GameWindow_OpenGL import OpenGLGameWindow
except:
    logger.warning("Failed to load OpenGL GameWindow")

try:
    from .GameWindow_Multiprocess import MultiprocessGameWindow
except:
    logger.warning("Failed to load MultiProcess GameWindow")

from .GameWindow_dummy import DummyGameWindow
from .GameWindow_Scanline import ScanlineGameWindow
