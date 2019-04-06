# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import platform
from ..Logger import logger, addConsoleHandler
addConsoleHandler()

def getWindow(win_type, scale):
    logger.info("Window type is: %s" % win_type)
    if win_type == "SDL2" or win_type is None:
        from .Window_SDL2 import SdlWindow
        window = SdlWindow(scale)
    elif win_type == "scanline":
        from .Window_Scanline import ScanlineWindow
        window = ScanlineWindow(scale)
    elif win_type == "OpenGL":
        from .Window_OpenGL import OpenGLWindow
        window = OpenGLWindow(scale)
    elif win_type == "dummy":
        from .Window_dummy import DummyWindow
        window = DummyWindow(scale)
    else:
        logger.error("Invalid arguments! Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'scanline', 'OpenGL',  and 'dummy'")
        exit(1)

    window.init()
    return window
