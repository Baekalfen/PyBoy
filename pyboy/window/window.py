#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..logger import logger

ROWS, COLS = 144, 160


def getwindow(window_type, scale, debug, hide_window):
    logger.info("Window type is: %s" % window_type)

    # Debug mode overwrites any window setting
    if debug:
        from .debug_window import DebugWindow
        window = DebugWindow(scale)
    elif window_type == "SDL2" or window_type is None:
        from .window_sdl2 import SDLWindow
        window = SDLWindow(scale)
    elif window_type == "scanline":
        from .window_scanline import ScanlineWindow
        window = ScanlineWindow(scale)
    elif window_type == "OpenGL":
        from .window_opengl import OpenGLWindow
        window = OpenGLWindow(scale)
    elif window_type == "dummy":
        from .window_dummy import DummyWindow
        window = DummyWindow(scale)
    elif window_type == "headless":
        from .window_headless import HeadlessWindow
        window = HeadlessWindow(scale)
    else:
        logger.error("Invalid arguments! Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'scanline', 'OpenGL', 'headless', and 'dummy'")
        exit(1)

    window.init(hide_window)
    return window
