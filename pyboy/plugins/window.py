#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from pyboy.logger import logger

ROWS, COLS = 144, 160


def get_window(*, window="SDL2", debug=False, scale=3, hide_window=False, **kwargs):
    window_type = window
    logger.info("Window type is: %s" % window_type)

    # Debug mode overwrites any window setting
    if debug:
        logger.warning("Debug mode overwrites window type to SDL2!")
        from .window_implementations.debug_window import DebugWindow
        window = DebugWindow
    elif window_type == "SDL2" or window_type is None:
        from .window_implementations.window_sdl2 import SDLWindow
        window = SDLWindow
    elif window_type == "OpenGL":
        from .window_implementations.window_opengl import OpenGLWindow
        window = OpenGLWindow
    elif window_type == "dummy" or window_type == "headless":
        from .window_implementations.window_dummy import DummyWindow
        window = DummyWindow
    else:
        logger.error("Invalid arguments! Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'OpenGL', and 'dummy'")
        exit(1)

    return window.color_format, lambda renderer, color_palette: window(renderer, scale, color_palette, hide_window)
