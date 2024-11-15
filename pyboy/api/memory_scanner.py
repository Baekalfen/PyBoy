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


class MemoryScanner:
    """A class for scanning memory within a given range."""

    def __init__(self, pyboy):
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
        byteorder="little",
    ):
        """
        This function scans a specified range of memory for a target value from the `start_addr` to the `end_addr` (both included).

        Example:
        ```python
        >>> current_score = 4 # You write current score in game
        >>> pyboy.memory_scanner.scan_memory(current_score, start_addr=0xC000, end_addr=0xDFFF)
        []

        ```

        Args:
            start_addr (int): The starting address for the scan.
            end_addr (int): The ending address for the scan.
            target_value (int or None): The value to search for. If None, any value is considered a match.
            standard_comparison_type (StandardComparisonType): The type of comparison to use.
            value_type (ValueType): The type of value (INT or BCD) to consider.
            byte_width (int): The number of bytes to consider for each value.
            byteorder (str): The endian type to use. This is only used for 16-bit values and higher. See [int.from_bytes](https://docs.python.org/3/library/stdtypes.html#int.from_bytes) for more details.

        Returns:
            list of int: A list of addresses where the target value is found.
        """
        self._memory_cache = {}
        self._memory_cache_byte_width = byte_width
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

    def rescan_memory(
        self, new_value=None, dynamic_comparison_type=DynamicComparisonType.UNCHANGED, byteorder="little"
    ):
        """
        Rescans the memory and updates the memory cache based on a dynamic comparison type.

        Example:
        ```python
        >>> current_score = 4 # You write current score in game
        >>> pyboy.memory_scanner.scan_memory(current_score, start_addr=0xC000, end_addr=0xDFFF)
        []
        >>> for _ in range(175):
        ...     pyboy.tick(1, True) # Progress the game to change score
        True...
        >>> current_score = 8 # You write the new score in game
        >>> from pyboy.api.memory_scanner import DynamicComparisonType
        >>> addresses = pyboy.memory_scanner.rescan_memory(current_score, DynamicComparisonType.MATCH)
        >>> print(addresses) # If repeated enough, only one address will remain
        []

        ```

        Args:
            new_value (int, optional): The new value for comparison. If not provided, the current value in memory is used.
            dynamic_comparison_type (DynamicComparisonType): The type of comparison to use. Defaults to UNCHANGED.

        Returns:
            list of int: A list of addresses remaining in the memory cache after the rescan.
        """
        for addr, value in self._memory_cache.copy().items():
            current_value = int.from_bytes(
                self.pyboy.memory[addr : addr + self._memory_cache_byte_width], byteorder=byteorder
            )
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
