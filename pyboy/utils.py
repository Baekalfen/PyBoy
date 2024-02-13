#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__all__ = ["WindowEvent", "dec_to_bcd", "bcd_to_dec"]

STATE_VERSION = 10

##############################################################
# Buffer classes


class IntIOInterface:
    def __init__(self, buf):
        pass

    def write(self, byte):
        raise Exception("Not implemented!")

    def write_64bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)
        self.write((value >> 16) & 0xFF)
        self.write((value >> 24) & 0xFF)
        self.write((value >> 32) & 0xFF)
        self.write((value >> 40) & 0xFF)
        self.write((value >> 48) & 0xFF)
        self.write((value >> 56) & 0xFF)

    def read_64bit(self):
        a = self.read()
        b = self.read()
        c = self.read()
        d = self.read()
        e = self.read()
        f = self.read()
        g = self.read()
        h = self.read()
        return a | (b << 8) | (c << 16) | (d << 24) | (e << 32) | (f << 40) | (g << 48) | (h << 56)

    def write_32bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)
        self.write((value >> 16) & 0xFF)
        self.write((value >> 24) & 0xFF)

    def read_32bit(self):
        a = self.read()
        b = self.read()
        c = self.read()
        d = self.read()
        return int(a | (b << 8) | (c << 16) | (d << 24))

    def write_16bit(self, value):
        self.write(value & 0xFF)
        self.write((value >> 8) & 0xFF)

    def read_16bit(self):
        a = self.read()
        b = self.read()
        return int(a | (b << 8))

    def read(self):
        raise Exception("Not implemented!")

    def seek(self, pos):
        raise Exception("Not implemented!")

    def flush(self):
        raise Exception("Not implemented!")

    def new(self):
        raise Exception("Not implemented!")

    def commit(self):
        raise Exception("Not implemented!")

    def seek_frame(self, _):
        raise Exception("Not implemented!")

    def tell(self):
        raise Exception("Not implemented!")


class IntIOWrapper(IntIOInterface):
    """
    Wraps a file-like object to allow writing integers to it.
    This allows for higher performance, when writing to a memory map in rewind.
    """
    def __init__(self, buf):
        self.buffer = buf

    def write(self, byte):
        assert isinstance(byte, int)
        assert 0 <= byte <= 0xFF
        return self.buffer.write(byte.to_bytes(1, "little"))

    def read(self):
        # assert count == 1, "Only a count of 1 is supported"
        data = self.buffer.read(1)
        assert len(data) == 1, "No data"
        return ord(data)

    def seek(self, pos):
        self.buffer.seek(pos)

    def flush(self):
        self.buffer.flush()

    def tell(self):
        return self.buffer.tell()


##############################################################
# Misc


# TODO: Would a lookup-table increase performance? For example a lookup table of each 4-bit nibble?
# That's 16**2 = 256 values. Index calculated as: (byte1 & 0xF0) | ((byte2 & 0xF0) >> 4)
# and then: (byte1 & 0x0F) | ((byte2 & 0x0F) >> 4)
# Then could even be preloaded for each color palette
def color_code(byte1, byte2, offset):
    """Convert 2 bytes into color code at a given offset.

    The colors are 2 bit and are found like this:

    Color of the first pixel is 0b10
    | Color of the second pixel is 0b01
    v v
    1 0 0 1 0 0 0 1 <- byte1
    0 1 1 1 1 1 0 0 <- byte2
    """
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)


##############################################################
# Window Events
# Temporarily placed here to not be exposed on public API


class WindowEvent:
    """
    All supported events can be found in the class description below.

    It can be used as follows:

    ```python
    >>> from pyboy.utils import WindowEvent
    >>> pyboy.send_input(WindowEvent.PAUSE)

    ```

    Just for button presses, it might be easier to use: `pyboy.PyBoy.button`,
    `pyboy.PyBoy.button_press` and `pyboy.PyBoy.button_release`.
    """

    # ONLY ADD NEW EVENTS AT THE END OF THE LIST!
    # Otherwise, it will break replays, which depend on the id of the event
    (
        QUIT,
        PRESS_ARROW_UP,
        PRESS_ARROW_DOWN,
        PRESS_ARROW_RIGHT,
        PRESS_ARROW_LEFT,
        PRESS_BUTTON_A,
        PRESS_BUTTON_B,
        PRESS_BUTTON_SELECT,
        PRESS_BUTTON_START,
        RELEASE_ARROW_UP,
        RELEASE_ARROW_DOWN,
        RELEASE_ARROW_RIGHT,
        RELEASE_ARROW_LEFT,
        RELEASE_BUTTON_A,
        RELEASE_BUTTON_B,
        RELEASE_BUTTON_SELECT,
        RELEASE_BUTTON_START,
        _INTERNAL_TOGGLE_DEBUG,
        PRESS_SPEED_UP,
        RELEASE_SPEED_UP,
        STATE_SAVE,
        STATE_LOAD,
        PASS,
        SCREEN_RECORDING_TOGGLE,
        PAUSE,
        UNPAUSE,
        PAUSE_TOGGLE,
        PRESS_REWIND_BACK,
        PRESS_REWIND_FORWARD,
        RELEASE_REWIND_BACK,
        RELEASE_REWIND_FORWARD,
        WINDOW_FOCUS,
        WINDOW_UNFOCUS,
        _INTERNAL_RENDERER_FLUSH,
        _INTERNAL_MOUSE,
        _INTERNAL_MARK_TILE,
        SCREENSHOT_RECORD,
        DEBUG_MEMORY_SCROLL_DOWN,
        DEBUG_MEMORY_SCROLL_UP,
        MOD_SHIFT_ON,
        MOD_SHIFT_OFF,
        FULL_SCREEN_TOGGLE,
    ) = range(42)

    def __init__(self, event):
        self.event = event

    def __eq__(self, x):
        if isinstance(x, int):
            return self.event == x
        else:
            return self.event == x.event

    def __int__(self):
        return self.event

    def __str__(self):
        return (
            "QUIT",
            "PRESS_ARROW_UP",
            "PRESS_ARROW_DOWN",
            "PRESS_ARROW_RIGHT",
            "PRESS_ARROW_LEFT",
            "PRESS_BUTTON_A",
            "PRESS_BUTTON_B",
            "PRESS_BUTTON_SELECT",
            "PRESS_BUTTON_START",
            "RELEASE_ARROW_UP",
            "RELEASE_ARROW_DOWN",
            "RELEASE_ARROW_RIGHT",
            "RELEASE_ARROW_LEFT",
            "RELEASE_BUTTON_A",
            "RELEASE_BUTTON_B",
            "RELEASE_BUTTON_SELECT",
            "RELEASE_BUTTON_START",
            "_INTERNAL_TOGGLE_DEBUG",
            "PRESS_SPEED_UP",
            "RELEASE_SPEED_UP",
            "STATE_SAVE",
            "STATE_LOAD",
            "PASS",
            "SCREEN_RECORDING_TOGGLE",
            "PAUSE",
            "UNPAUSE",
            "PAUSE_TOGGLE",
            "PRESS_REWIND_BACK",
            "PRESS_REWIND_FORWARD",
            "RELEASE_REWIND_BACK",
            "RELEASE_REWIND_FORWARD",
            "WINDOW_FOCUS",
            "WINDOW_UNFOCUS",
            "_INTERNAL_RENDERER_FLUSH",
            "_INTERNAL_MOUSE",
            "_INTERNAL_MARK_TILE",
            "SCREENSHOT_RECORD",
            "DEBUG_MEMORY_SCROLL_DOWN",
            "DEBUG_MEMORY_SCROLL_UP",
            "MOD_SHIFT_ON",
            "MOD_SHIFT_OFF",
            "FULL_SCREEN_TOGGLE",
        )[self.event]


class WindowEventMouse(WindowEvent):
    def __init__(
        self, *args, window_id=-1, mouse_x=-1, mouse_y=-1, mouse_scroll_x=-1, mouse_scroll_y=-1, mouse_button=-1
    ):
        super().__init__(*args)
        self.window_id = window_id
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.mouse_scroll_x = mouse_scroll_x
        self.mouse_scroll_y = mouse_scroll_y
        self.mouse_button = mouse_button


##############################################################
# Memory Scanning
#


def dec_to_bcd(value, byte_width=1, byteorder="little"):
    """
    Converts a decimal value to Binary Coded Decimal (BCD).

    Args:
        value (int): The integer value to convert.
        byte_width (int): The number of bytes to consider for each value.
        byteorder (str): The endian type to use. This is only used for 16-bit values and higher. See [int.from_bytes](https://docs.python.org/3/library/stdtypes.html#int.from_bytes) for more details.

    Example:
    ```python
    >>> from pyboy.utils import dec_to_bcd
    >>> f"{dec_to_bcd(30):08b}"
    '00110000'
    >>> f"{dec_to_bcd(32):08b}"
    '00110010'

    ```

    Returns:
        int: The BCD equivalent of the decimal value.
    """
    bcd_result = []
    for _ in range(byte_width):
        tens = ((value%100) // 10) << 4
        units = value % 10
        bcd_byte = (tens | units) & 0xFF
        bcd_result.append(bcd_byte)
        value //= 100
    return int.from_bytes(bcd_result, byteorder)


def bcd_to_dec(value, byte_width=1, byteorder="little"):
    """
    Converts a Binary Coded Decimal (BCD) value to decimal.

    Args:
        value (int): The BCD value to convert.
        byte_width (int): The number of bytes to consider for each value.
        byteorder (str): The endian type to use. This is only used for 16-bit values and higher. See [int.to_bytes](https://docs.python.org/3/library/stdtypes.html#int.to_bytes) for more details.

    Example:
    ```python
    >>> from pyboy.utils import bcd_to_dec
    >>> bcd_to_dec(0b00110000)
    30
    >>> bcd_to_dec(0b00110010)
    32

    ```

    Returns:
        int: The decimal equivalent of the BCD value.
    """
    decimal_value = 0
    multiplier = 1

    bcd_bytes = value.to_bytes(byte_width, byteorder)

    for bcd_byte in bcd_bytes:
        decimal_value += ((bcd_byte >> 4) * 10 + (bcd_byte & 0x0F)) * multiplier
        multiplier *= 100

    return decimal_value
