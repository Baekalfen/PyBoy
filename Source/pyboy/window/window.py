#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..logger import logger

ROWS, COLS = 144, 160


def getwindow(win_type, scale, debug):
    logger.info("Window type is: %s" % win_type)

    # Choose SDL2 if we the user enabled debugging, if SDL2 is chosen, or if nothing is chosen.
    if debug:
        from .debug_window import DebugWindow
        window = DebugWindow(scale)
    elif win_type == "SDL2" or win_type is None:
        from .window_sdl2 import SDLWindow
        window = SDLWindow(scale)
    elif win_type == "scanline":
        from .window_scanline import ScanlineWindow
        window = ScanlineWindow(scale)
    elif win_type == "OpenGL":
        from .window_opengl import OpenGLWindow
        window = OpenGLWindow(scale)
    elif win_type == "dummy":
        from .window_dummy import DummyWindow
        window = DummyWindow(scale)
    elif win_type == "headless":
        from .window_headless import HeadlessWindow
        window = HeadlessWindow(scale)
    else:
        logger.error("Invalid arguments! Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'scanline', 'OpenGL', 'headless',  and 'dummy'")
        exit(1) # TODO: is this imported here?

    window.init()
    return window
