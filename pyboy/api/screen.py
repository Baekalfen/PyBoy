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
    It's much more efficient to use `pyboy.PyBoy.tilemap_background`, `pyboy.PyBoy.tilemap_window`, and `pyboy.PyBoy.get_sprite` instead.
    """

    def __init__(self, mb):
        self.mb = mb

        self.raw_buffer = self.mb.lcd.renderer._screenbuffer
        """
        Provides a raw, unfiltered `bytes` object with the data from the screen. Check
        `Screen.raw_buffer_format` to see which dataformat is used. **The returned type and dataformat are
        subject to change.** The screen buffer is row-major.

        Use this, only if you need to bypass the overhead of `Screen.image` or `Screen.ndarray`.

        Example:
        ```python
        >>> import numpy as np
        >>> rows, cols = pyboy.screen.raw_buffer_dims
        >>> ndarray = np.frombuffer(
        ...     pyboy.screen.raw_buffer,
        ...     dtype=np.uint8,
        ... ).reshape(rows, cols, 4) # Just an example, use pyboy.screen.ndarray instead

        ```

        Returns
        -------
        memoryview:
            92160 bytes memoryview of screen data.
        """
        self.raw_buffer_dims = self.mb.lcd.renderer.buffer_dims
        """
        Returns the dimensions of the raw screen buffer. The screen buffer is row-major.

        Example:
        ```python
        >>> pyboy.screen.raw_buffer_dims
        (144, 160)

        ```

        Returns
        -------
        tuple:
            A two-tuple of the buffer dimensions. E.g. (144, 160).
        """
        self.raw_buffer_format = self.mb.lcd.renderer.color_format
        """
        Returns the color format of the raw screen buffer. **This format is subject to change.**

        Example:
        ```python
        >>> from PIL import Image
        >>> pyboy.screen.raw_buffer_format
        'RGBA'
        >>> image = Image.frombuffer(
        ...    pyboy.screen.raw_buffer_format,
        ...    pyboy.screen.raw_buffer_dims[::-1],
        ...    pyboy.screen.raw_buffer,
        ... ) # Just an example, use pyboy.screen.image instead
        >>> image.save('frame.png')

        ```

        Returns
        -------
        str:
            Color format of the raw screen buffer. E.g. 'RGBA'.
        """
        self.image = None
        """
        Reference to a PIL Image from the screen buffer. **Remember to copy, resize or convert this object** if you
        intend to store it. The backing buffer will update, but it will be the same `PIL.Image` object.

        Convenient for screen captures, but might be a bottleneck, if you use it to train a neural network. In which
        case, read up on the `pyboy.api` features, [Pan Docs](https://gbdev.io/pandocs/) on tiles/sprites,
        and join our Discord channel for more help.

        Example:
        ```python
        >>> image = pyboy.screen.image
        >>> type(image)
        <class 'PIL.Image.Image'>
        >>> image.save('frame.png')

        ```

        Returns
        -------
        PIL.Image:
            RGB image of (160, 144) pixels
        """
        if not Image:
            logger.warning('Cannot generate screen image. Missing dependency "Pillow".')
            self.image = utils.PillowImportError()
        else:
            self._set_image()

        self.ndarray = np.frombuffer(
            self.mb.lcd.renderer._screenbuffer_raw,
            dtype=np.uint8,
        ).reshape(ROWS, COLS, 4)
        """
        References the screen data in NumPy format. **Remember to copy this object** if you intend to store it.
        The backing buffer will update, but it will be the same `ndarray` object.

        The format is given by `pyboy.api.screen.Screen.raw_buffer_format`. The screen buffer is row-major.

        Example:
        ```python
        >>> pyboy.screen.ndarray.shape
        (144, 160, 4)
        >>> # Display "P" on screen from the PyBoy bootrom
        >>> pyboy.screen.ndarray[66:80,64:72,0]
        array([[255, 255, 255, 255, 255, 255, 255, 255],
               [255,   0,   0,   0,   0,   0, 255, 255],
               [255,   0,   0,   0,   0,   0,   0, 255],
               [255,   0,   0, 255, 255,   0,   0, 255],
               [255,   0,   0, 255, 255,   0,   0, 255],
               [255,   0,   0, 255, 255,   0,   0, 255],
               [255,   0,   0,   0,   0,   0,   0, 255],
               [255,   0,   0,   0,   0,   0, 255, 255],
               [255,   0,   0, 255, 255, 255, 255, 255],
               [255,   0,   0, 255, 255, 255, 255, 255],
               [255,   0,   0, 255, 255, 255, 255, 255],
               [255,   0,   0, 255, 255, 255, 255, 255],
               [255,   0,   0, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255]], dtype=uint8)

        ```

        Returns
        -------
        numpy.ndarray:
            Screendata in `ndarray` of bytes with shape (144, 160, 4)
        """

    def _set_image(self):
        self.image = Image.frombuffer(
            self.mb.lcd.renderer.color_format,
            self.mb.lcd.renderer.buffer_dims[::-1],
            self.mb.lcd.renderer._screenbuffer_raw,
        )

    @property
    def tilemap_position_list(self):
        """
        This function provides the screen (SCX, SCY) and window (WX, WY) position for each horizontal line in the
        screen buffer. These parameters are often used for visual effects, and some games will reset the registers at
        the end of each call to `pyboy.PyBoy.tick()`.

        See `Screen.get_tilemap_position` for more information.

        Example:
        ```python
        >>> pyboy.tick(25)
        True
        >>> swoosh = pyboy.screen.tilemap_position_list[66:77]
        >>> print(*swoosh, sep=newline) # Just to pretty-print it
        [0, 0, -7, 0]
        [1, 0, -7, 0]
        [2, 0, -7, 0]
        [2, 0, -7, 0]
        [2, 0, -7, 0]
        [3, 0, -7, 0]
        [3, 0, -7, 0]
        [2, 0, -7, 0]
        [1, 0, -7, 0]
        [1, 0, -7, 0]
        [0, 0, -7, 0]

        ```

        Returns
        -------
        list:
            Nested list of SCX, SCY, WX and WY for each scanline (144x4). Returns (0, 0, 0, 0) when LCD is off.
        """

        if self.mb.lcd._LCDC.lcd_enable:
            return [[line[0], line[1], line[2] - 7, line[3]] for line in self.mb.lcd._scanlineparameters]
        else:
            return [[0, 0, 0, 0] for line in range(144)]

    def get_tilemap_position(self):
        """
        These coordinates define the offset in the tile map from where the top-left corner of the screen is place. Note
        that the tile map defines 256x256 pixels, but the screen can only show 160x144 pixels. When the offset is closer
        to the right or bottom edge than 160x144 pixels, the screen will wrap around and render from the opposite site
        of the tile map.

        For more details, see "7.4 Viewport" in the [report](https://github.com/Baekalfen/PyBoy/raw/master/extras/PyBoy.pdf),
        or the Pan Docs under [LCD Position and Scrolling](https://gbdev.io/pandocs/Scrolling.html).

        Example:
        ```python
        >>> pyboy.screen.get_tilemap_position()
        ((0, 0), (-7, 0))

        ```

        Returns
        -------
        tuple:
            Returns the tuple of registers ((SCX, SCY), (WX - 7, WY))
        """
        return (self.mb.lcd.getviewport(), self.mb.lcd.getwindowpos())
