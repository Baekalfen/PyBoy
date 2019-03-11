# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#


from ..Logger import logger
from .AbstractGameWindow import AbstractGameWindow
from .GameWindow_dummy import DummyGameWindow


windowTypes = ["SDL2", "scanline", "dummy", "OpenGL", "Multiprocess"]
defaultWindowType = "SDL2"


def createGameWindow(windowType):
    if windowType == "SDL2":
        from .GameWindow_SDL2 import SdlGameWindow
        return SdlGameWindow(scale=2)
    elif windowType == "scanline":
        from .GameWindow_Scanline import ScanlineGameWindow
        return ScanlineGameWindow(scale=2)
    elif windowType == "OpenGL":
        from .GameWindow_OpenGL import OpenGLGameWindow
        return OpenGLGameWindow(scale=2)
    elif windowType == "Multiprocess":
        from .GameWindow_Multiprocess import MultiprocessGameWindow
        return MultiprocessGameWindow()
    elif windowType == "dummy":
        return DummyGameWindow()
    else:
        raise Exception("Invalid GameWindow type " + str(windowType))
