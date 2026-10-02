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
    """Comparisons between values found in the previous and current scans."""

    UNCHANGED = 1
    CHANGED = 2
    INCREASED = 3
    DECREASED = 4
    MATCH = 5


class ScanMode(Enum):
    """Interpret scanned bytes as an unsigned integer or binary-coded decimal."""

    INT = 1
    BCD = 2


class MemoryScanner:
    """A class for scanning memory within a given range."""

    def __init__(self, pyboy):
        self.pyboy = pyboy
        self._memory_cache = {}
        self._memory_cache_byte_width = 1
        self._memory_cache_value_type = ScanMode.INT
        self._memory_cache_byteorder = "little"

    def scan_memory(
        self,
        target_value=None,
        start_addr=0x0000,
        end_addr=0xFFFF,
        standard_comparison_type=StandardComparisonType.EXACT,
        value_type=ScanMode.INT,
        byte_width=1,
        byteorder="little",
    ):
        """
        Scan the inclusive address range from `start_addr` to `end_addr` for a target value.

        Example:
        ```python
        >>> pyboy.memory[0xC000] = 4
        >>> pyboy.memory_scanner.scan_memory(4, start_addr=0xC000, end_addr=0xC000)
        [49152]

        ```

        Args:
            target_value (int or None): Value to search for. If None, every value matches.
            start_addr (int): First address to scan. Defaults to 0.
            end_addr (int): Last address to scan, inclusive. Defaults to 65535.
            standard_comparison_type (StandardComparisonType): Comparison to apply. Defaults to EXACT.
            value_type (ScanMode): Interpret values as INT or BCD. Defaults to INT.
            byte_width (int): Positive number of bytes per value. Defaults to 1.
            byteorder (str): "little" or "big" byte order for multi-byte values. Defaults to "little".

        Returns:
            list[int]: Addresses where the target value is found.

        Raises:
            ValueError: If `byte_width` is not positive.
        """
        if byte_width <= 0:
            raise ValueError("byte_width must be positive")

        self._memory_cache = {}
        self._memory_cache_byte_width = byte_width
        self._memory_cache_value_type = value_type
        self._memory_cache_byteorder = byteorder
        for addr in range(
            start_addr, end_addr - (byte_width - 1) + 1
        ):  # Adjust the loop to prevent reading past end_addr
            # Read multiple bytes based on byte_width and byteorder
            value_bytes = self.pyboy.memory[addr : addr + byte_width]
            value = int.from_bytes(value_bytes, byteorder)

            if value_type == ScanMode.BCD:
                value = bcd_to_dec(value, byte_width, byteorder)

            if target_value is None or self._check_value(value, target_value, standard_comparison_type.value):
                self._memory_cache[addr] = value

        return list(self._memory_cache.keys())

    def rescan_memory(self, new_value=None, dynamic_comparison_type=DynamicComparisonType.UNCHANGED, byteorder=None):
        """
        Filter cached addresses using values read in the current scan.

        Example:
        ```python
        >>> pyboy.memory[0xC000] = 4
        >>> pyboy.memory_scanner.scan_memory(4, start_addr=0xC000, end_addr=0xC000)
        [49152]
        >>> pyboy.memory[0xC000] = 8
        >>> from pyboy.api.memory_scanner import DynamicComparisonType
        >>> addresses = pyboy.memory_scanner.rescan_memory(8, DynamicComparisonType.MATCH)
        >>> print(addresses)
        [49152]

        ```

        Args:
            new_value (int or None): Target value used by MATCH; required for MATCH and ignored by other comparisons.
            dynamic_comparison_type (DynamicComparisonType): Comparison to apply. Defaults to UNCHANGED.
            byteorder (str or None): Byte order for reading values. If None, reuse the byte order from the previous
                `scan_memory` call.

        Returns:
            list[int]: Addresses remaining in the cache after filtering.
        """
        if byteorder is None:
            byteorder = self._memory_cache_byteorder

        for addr, value in self._memory_cache.copy().items():
            current_value = int.from_bytes(
                self.pyboy.memory[addr : addr + self._memory_cache_byte_width], byteorder=byteorder
            )
            if self._memory_cache_value_type == ScanMode.BCD:
                current_value = bcd_to_dec(current_value, self._memory_cache_byte_width, byteorder)
            if dynamic_comparison_type == DynamicComparisonType.UNCHANGED:
                if value != current_value:
                    self._memory_cache.pop(addr)
                else:
                    self._memory_cache[addr] = current_value
            elif dynamic_comparison_type == DynamicComparisonType.CHANGED:
                if value == current_value:
                    self._memory_cache.pop(addr)
                else:
                    self._memory_cache[addr] = current_value
            elif dynamic_comparison_type == DynamicComparisonType.INCREASED:
                if value >= current_value:
                    self._memory_cache.pop(addr)
                else:
                    self._memory_cache[addr] = current_value
            elif dynamic_comparison_type == DynamicComparisonType.DECREASED:
                if value <= current_value:
                    self._memory_cache.pop(addr)
                else:
                    self._memory_cache[addr] = current_value
            elif dynamic_comparison_type == DynamicComparisonType.MATCH:
                if new_value is None:
                    raise ValueError("new_value must be specified when using DynamicComparisonType.MATCH")
                if current_value != new_value:
                    self._memory_cache.pop(addr)
                else:
                    self._memory_cache[addr] = current_value
            else:
                raise ValueError("Invalid comparison type")
        return list(self._memory_cache.keys())

    def _check_value(self, value, target_value, standard_comparison_type):
        """
        Compares a value with the target value based on the specified compare type.

        Args:
            value (int): The value to compare.
            target_value (int or None): The target value to compare against.
            standard_comparison_type (StandardComparisonType): The type of comparison to use.

        Returns:
            bool: True if the comparison condition is met, False otherwise.
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
        else:
            raise ValueError("Invalid comparison type")
