#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from enum import Enum

STATE_VERSION = 9

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


def flatten_list(l):
    flat_list = []
    for sublist in l:
        for item in sublist:
            flat_list.append(item)
    return flat_list


##############################################################
# Window Events
# Temporarily placed here to not be exposed on public API


class WindowEvent:
    """
    All supported events can be found in the class description below.

    It can be used as follows:

    >>> from pyboy import PyBoy, WindowEvent
    >>> pyboy = PyBoy('file.rom')
    >>> pyboy.send_input(WindowEvent.PAUSE)

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
class EndianType(Enum):
    """Enumeration for defining endian types."""
    LITTLE = 1
    BIG = 2

class CompareType(Enum):
    """Enumeration for defining types of comparisons."""
    EXACT = 1
    LESS_THAN = 2
    GREATER_THAN = 3
    LESS_THAN_OR_EQUAL = 4
    GREATER_THAN_OR_EQUAL = 5

class ScanMode(Enum):
    """Enumeration for defining scanning modes."""
    INT = 1
    BCD = 2

class BCDConverter:
    def dec_to_bcd(self, value, byte_width=1, endian_type=EndianType.LITTLE):
        """
        Converts a decimal value to Binary Coded Decimal (BCD).

        :param value: Integer value to convert.
        :param byte_width: The number of bytes to consider for each value.
        :param endian_type: The endian type to use. Note, this is only used for 16-bit values and higher.
        :return: BCD equivalent of the decimal value.
        """
        bcd_result = []
        for _ in range(byte_width):
            tens = ((value%100) // 10) << 4
            units = value % 10
            bcd_byte = (tens | units) & 0xFF
            bcd_result.append(bcd_byte)
            value //= 100
        if endian_type == EndianType.BIG:
            return int.from_bytes(bcd_result, byteorder='big')
        else:
            return int.from_bytes(bcd_result, byteorder='little')
        #return int.from_bytes([0b00110000,0b00110000],byteorder='little')

    def bcd_to_dec(self, value, byte_width=1, endian_type=EndianType.LITTLE):
        """
        Converts a Binary Coded Decimal (BCD) value to decimal.

        :param value: BCD value to convert.
        :param byte_width: The number of bytes to consider for each value.
        :param endian_type: The endian type to use. Note, this is only used for 16-bit values and higher.
        :return: Decimal equivalent of the BCD value.
        """
        decimal_value = 0
        multiplier = 1

        bcd_bytes = value.to_bytes(byte_width, 'big' if endian_type == EndianType.BIG else 'little')
        
        for bcd_byte in bcd_bytes:
            decimal_value += ((bcd_byte >> 4) * 10 + (bcd_byte & 0x0F)) * multiplier
            multiplier *= 100

        return decimal_value

class MemoryScanner():
    """A class for scanning memory within a given range."""

    def __init__(self, pyboy):
        """
        Initializes the MemoryScanner with a pyboy instance.

        :param pyboy: The pyboy emulator instance.
        """
        self.pyboy = pyboy
        self.bcd_converter = BCDConverter()


    def scan_memory(self, start_addr, end_addr, target_value, compare_type=CompareType.EXACT, value_type=ScanMode.INT,byte_width=1,endian_type=EndianType.LITTLE):
        """
        Scans memory in the specified range, looking for a target value.

        :param start_addr: The starting address for the scan.
        :param end_addr: The ending address for the scan.
        :param target_value: The value to search for.
        :param compare_type: The type of comparison to use.
        :param value_type: The type of value (INT or BCD) to consider.
        :param byte_width: The number of bytes to consider for each value.
        :param endian_type: The endian type to use. Note, this is only used for 16-bit values and higher.
        :return: A list of addresses where the target value is found.
        """
        #TODO - Add support for 16-bit values and higher
        found_addresses = []
        for addr in range(start_addr, end_addr + 1):
            value = self.pyboy.get_memory_value(addr)
            if value_type == ScanMode.BCD:
                value = self.bcd_converter.bcd_to_dec(value)
            if self._check_value(value, target_value, compare_type.value):
                found_addresses.append(addr)

        return found_addresses

    def _check_value(self, value, target_value, compare_type):
        """
        Compares a value with the target value based on the specified compare type.

        :param value: The value to compare.
        :param target_value: The target value to compare against.
        :param compare_type: The type of comparison to use.
        :return: True if the comparison condition is met, False otherwise.
        """
        if compare_type == CompareType.EXACT.value:
            return value == target_value
        elif compare_type == CompareType.LESS_THAN.value:
            return value < target_value
        elif compare_type == CompareType.GREATER_THAN.value:
            return value > target_value
        elif compare_type == CompareType.LESS_THAN_OR_EQUAL.value:
            return value <= target_value
        elif compare_type == CompareType.GREATER_THAN_OR_EQUAL.value:
            return value >= target_value
        return False
