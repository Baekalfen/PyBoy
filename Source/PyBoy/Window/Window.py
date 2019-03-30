# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..Logger import logger, addConsoleHandler
addConsoleHandler()

from .Window_dummy import DummyWindow

try:
    from .Window_SDL2 import SdlWindow
except:
    logger.warning("Failed to load SDL2 Window.")

try:
    from .Window_Scanline import ScanlineWindow
except:
    logger.warning("Failed to load Scanline Window")

try:
    from .Window_OpenGL import OpenGLWindow
except:
    logger.warning("Failed to load OpenGL Window")


def getWindow(win_type, scale):
    logger.info("Window type is: %s" % win_type)
    if win_type is None:
        window = SdlWindow(scale)
    elif win_type == "SDL2":
        window = SdlWindow(scale)
    elif win_type == "scanline":
        window = ScanlineWindow(scale)
    elif win_type == "OpenGL":
        window = OpenGLWindow(scale)
    elif win_type == "dummy":
        window = DummyWindow(scale)
    else:
        logger.error("Invalid arguments! Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'scanline', 'OpenGL',  and 'dummy'")
        exit(1)

    window.init()
    return window


