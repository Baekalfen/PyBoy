# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

# from .. import Global

from ..Logger import logger
from AbstractGameWindow import AbstractGameWindow
from GameWindow_dummy import DummyGameWindow

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

