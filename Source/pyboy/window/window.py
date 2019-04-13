#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#


from ..logger import logger, addconsolehandler
addconsolehandler()


ROWS, COLS = 144, 160


def getwindow(win_type, scale):
    logger.info("Window type is: %s" % win_type)
    if win_type == "SDL2" or win_type is None:
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
        logger.error("Invalid arguments! "
                     "Usage: pypy main.py [Window] [ROM path]")
        logger.error("Valid Windows are: 'SDL2', 'scanline', "
                     "'OpenGL',  and 'dummy'")
        exit(1)  # TODO: is this imported here?

    window.init()
    return window


class Window:

    def __init__(self, scale=1):
        self._scale = scale
        logger.debug("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledresolution))

        self.colorpalette = (0xFFFFFFFF, 0xFF999999, 0xFF555555, 0xFF000000)
        self.alphamask = 0xFF000000
        self.colorformat = u"RGBA"

        self.clearcache = False
        self.tiles_changed = set([])
        self.enable_title = True

    def init(self):
        pass

    def dump(self, filename):
        raise NotImplementedError()

    def set_title(self, title):
        raise NotImplementedError()

    def get_events(self):
        raise NotImplementedError()

    def update_display(self):
        raise NotImplementedError()

    def frame_limiter(self, speed):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def scanline(self, y, lcd):
        raise NotImplementedError()

    def render_screen(self, lc):
        raise NotImplementedError()

    def blank_screen(self):
        pass

    def getscreenbuffer(self):
        raise NotImplementedError()

    def update_cache(self, lcd):
        pass

    def disable_title(self):
        self.enable_title = False
