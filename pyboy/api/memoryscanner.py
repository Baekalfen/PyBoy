from enum import Enum

from pyboy.utils import bcd_to_dec


class StandardComparisonType(Enum):
    """Enumeration for defining types of comparisons that do not require a previous value."""
    EXACT = 1
    LESS_THAN = 2
    GREATER_THAN = 3
    LESS_THAN_OR_EQUAL = 4
    GREATER_THAN_OR_EQUAL = 5


class DynamicComparisonType(Enum):
    """Enumeration for defining types of comparisons that require a previous value."""
    UNCHANGED = 1
    CHANGED = 2
    INCREASED = 3
    DECREASED = 4
    MATCH = 5


class ScanMode(Enum):
    """Enumeration for defining scanning modes."""
    INT = 1
    BCD = 2


class MemoryScanner():
    """A class for scanning memory within a given range."""
    def __init__(self, pyboy):
        """
        Initializes the MemoryScanner with a pyboy instance.

        :param pyboy: The pyboy emulator instance.
        """
        self.pyboy = pyboy
        self._memory_cache = {}
        self._memory_cache_byte_width = 1

    def scan_memory(
        self,
        target_value=None,
        start_addr=0x0000,
        end_addr=0xFFFF,
        standard_comparison_type=StandardComparisonType.EXACT,
        value_type=ScanMode.INT,
        byte_width=1,
        byteorder="little"
    ):
        """
        Scans memory in the specified range, looking for a target value.

        :param start_addr: The starting address for the scan.
        :param end_addr: The ending address for the scan.
        :param target_value: The value to search for or None for any value (used in relation to `MemoryScanner.rescan_memory`).
        :param standard_comparison_type: The type of comparison to use.
        :param value_type: The type of value (INT or BCD) to consider.
        :param byte_width: The number of bytes to consider for each value.
        :param byteorder: The endian type to use (see [int.from_bytes](https://docs.python.org/3/library/stdtypes.html#int.from_bytes)). Note, this is only used for 16-bit values and higher.
        :return: A list of addresses where the target value is found.
        """
        self._memory_cache = {}
        self._memory_cache_byte_width = byte_width
        for addr in range(start_addr, end_addr - byte_width + 2): # Adjust the loop to prevent reading past end_addr
            # Read multiple bytes based on byte_width and byteorder
            value_bytes = self.pyboy.memory[addr:addr + byte_width]
            value = int.from_bytes(value_bytes, byteorder)

            if value_type == ScanMode.BCD:
                value = bcd_to_dec(value, byte_width, byteorder)

            if target_value is None or self._check_value(value, target_value, standard_comparison_type.value):
                self._memory_cache[addr] = value

        return list(self._memory_cache.keys())

    def rescan_memory(self, dynamic_comparison_type=DynamicComparisonType.UNCHANGED, new_value=None):
        for addr, value in self._memory_cache.copy().items():
            if (dynamic_comparison_type == DynamicComparisonType.UNCHANGED):
                if value != int.from_bytes(self.pyboy.memory[addr:addr + self._memory_cache_byte_width]):
                    self._memory_cache.pop(addr)
            elif (dynamic_comparison_type == DynamicComparisonType.CHANGED):
                if value == int.from_bytes(self.pyboy.memory[addr:addr + self._memory_cache_byte_width]):
                    self._memory_cache.pop(addr)
            elif (dynamic_comparison_type == DynamicComparisonType.INCREASED):
                if value >= int.from_bytes(self.pyboy.memory[addr:addr + self._memory_cache_byte_width]):
                    self._memory_cache.pop(addr)
            elif (dynamic_comparison_type == DynamicComparisonType.DECREASED):
                if value <= int.from_bytes(self.pyboy.memory[addr:addr + self._memory_cache_byte_width]):
                    self._memory_cache.pop(addr)
            elif (dynamic_comparison_type == DynamicComparisonType.MATCH):
                if new_value == None:
                    raise ValueError("new_value must be specified when using DynamicComparisonType.MATCH")
                if value != new_value:
                    self._memory_cache.pop(addr)
        return list(self._memory_cache.keys())

    def _check_value(self, value, target_value, standard_comparison_type):
        """
        Compares a value with the target value based on the specified compare type.

        :param value: The value to compare.
        :param target_value: The target value to compare against.
        :param standard_comparison_type: The type of comparison to use.
        :return: True if the comparison condition is met, False otherwise.
        """
        if standard_comparison_type == StandardComparisonType.EXACT.value:
            return value == target_value
        elif standard_comparison_type == StandardComparisonType.LESS_THAN.value:
            return value < target_value
        elif standard_comparison_type == StandardComparisonType.GREATER_THAN.value:
            return value > target_value
        elif standard_comparison_type == StandardComparisonType.LESS_THAN_OR_EQUAL.value:
            return value <= target_value
        elif standard_comparison_type == StandardComparisonType.GREATER_THAN_OR_EQUAL.value:
            return value >= target_value
        return False
