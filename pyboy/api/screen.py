#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
This class gives access to the frame buffer and other screen parameters of PyBoy.
"""

import numpy as np

from pyboy import utils
from pyboy.logging import get_logger

from .constants import COLS, ROWS

logger = get_logger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None


class Screen:
    """
    As part of the emulation, we generate a screen buffer in 32-bit RGBA format. This class has several helper methods
    to make it possible to read this buffer out.

    If you're making an AI or bot, it's highly recommended to _not_ use this class for detecting objects on the screen.
    It's much more efficient to use `pyboy.tilemap_background`, `pyboy.tilemap_window`, and `pyboy.sprite` instead.
    """
    def __init__(self, mb):
        self.mb = mb

        self.raw_buffer = self.mb.lcd.renderer._screenbuffer
        """
        Provides a raw, unfiltered `bytes` object with the data from the screen. Check
        `Screen.raw_buffer_format` to see which dataformat is used. The returned type and dataformat are
        subject to change.

        Use this, only if you need to bypass the overhead of `Screen.image` or `Screen.ndarray`.

        Returns
        -------
        bytes:
            92160 bytes of screen data in a `bytes` object.
        """
        self.raw_buffer_dims = self.mb.lcd.renderer.buffer_dims
        """
        Returns the dimensions of the raw screen buffer.

        Returns
        -------
        tuple:
            A two-tuple of the buffer dimensions. E.g. (160, 144).
        """
        self.raw_buffer_format = self.mb.lcd.renderer.color_format
        """
        Returns the color format of the raw screen buffer.

        Returns
        -------
        str:
            Color format of the raw screen buffer. E.g. 'RGB'.
        """
        if not Image:
            logger.warning("Cannot generate screen image. Missing dependency \"Pillow\".")
            self.image = None
        else:
            self.image = Image.frombuffer(
                self.mb.lcd.renderer.color_format, self.mb.lcd.renderer.buffer_dims[::-1],
                self.mb.lcd.renderer._screenbuffer_raw
            )
        """
        Generates a PIL Image from the screen buffer.

        Convenient for screen captures, but might be a bottleneck, if you use it to train a neural network. In which
        case, read up on the `pyboy.api` features, [Pan Docs](http://bgb.bircd.org/pandocs.htm) on tiles/sprites,
        and join our Discord channel for more help.

        Returns
        -------
        PIL.Image:
            RGB image of (160, 144) pixels
        """
        self.ndarray = np.frombuffer(self.mb.lcd.renderer._screenbuffer_raw, dtype=np.uint8).reshape(ROWS, COLS,
                                                                                                     4)[:, :, 1:]
        """
        Provides the screen data in NumPy format. The dataformat is always RGB.

        Returns
        -------
        numpy.ndarray:
            Screendata in `ndarray` of bytes with shape (160, 144, 3)
        """

    @property
    def tilemap_position_list(self):
        """
        This function provides the screen (SCX, SCY) and window (WX. WY) position for each horizontal line in the
        screen buffer. These parameters are often used for visual effects, and some games will reset the registers at
        the end of each call to `pyboy.PyBoy.tick()`. For such games, `Screen.tilemap_position` becomes useless.

        See `Screen.tilemap_position` for more information.

        Returns
        -------
        list:
            Nested list of SCX, SCY, WX and WY for each scanline (144x4). Returns (0, 0, 0, 0) when LCD is off.
        """
        # self.tilemap_position_list = np.asarray(self.mb.lcd.renderer._scanlineparameters, dtype=np.uint8).reshape(144, 5)[:, :4]
        # self.tilemap_position_list = self.mb.lcd.renderer._scanlineparameters

        # # return self.mb.lcd.renderer._scanlineparameters
        if self.mb.lcd._LCDC.lcd_enable:
            return [[line[0], line[1], line[2], line[3]] for line in self.mb.lcd.renderer._scanlineparameters]
        else:
            return [[0, 0, 0, 0] for line in range(144)]

    def get_tilemap_position(self):
        """
        These coordinates define the offset in the tile map from where the top-left corner of the screen is place. Note
        that the tile map defines 256x256 pixels, but the screen can only show 160x144 pixels. When the offset is closer
        to the right or bottom edge than 160x144 pixels, the screen will wrap around and render from the opposite site
        of the tile map.

        For more details, see "7.4 Viewport" in the [report](https://github.com/Baekalfen/PyBoy/raw/master/extras/PyBoy.pdf),
        or the Pan Docs under [LCD Position and Scrolling](http://bgb.bircd.org/pandocs.htm#lcdpositionandscrolling).

        Returns
        -------
        tuple:
            Returns the tuple of registers ((SCX, SCY), (WX - 7, WY))
        """
        return (self.mb.lcd.getviewport(), self.mb.lcd.getwindowpos())
