from enum import Enum
from pyboy.utils import EndianType, bcd_to_dec

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

class MemoryScanner():
    """A class for scanning memory within a given range."""

    def __init__(self, pyboy):
        """
        Initializes the MemoryScanner with a pyboy instance.

        :param pyboy: The pyboy emulator instance.
        """
        self.pyboy = pyboy

    def read_memory(self, address, byte_width=1, value_type=ScanMode.INT, endian_type=EndianType.LITTLE):
        """
        Reads memory at the specified address.

        :param address: The address to read.
        :param byte_width: The number of bytes to consider for each value.
        :param value_type: The type of value (INT or BCD) to consider.
        :param endian_type: The endian type to use. Note, this is only used for 16-bit values and higher.
        :return: The value at the specified address.
        """
        value_bytes = [self.pyboy.get_memory_value(address + i) for i in range(byte_width)]
        value = int.from_bytes(value_bytes, 'little' if endian_type == EndianType.LITTLE else 'big')

        if value_type == ScanMode.BCD:
            value = bcd_to_dec(value, byte_width, endian_type)

        return value

    def scan_memory(self, start_addr, end_addr, target_value, compare_type=CompareType.EXACT, value_type=ScanMode.INT, byte_width=1, endian_type=EndianType.LITTLE):
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
        found_addresses = []
        for addr in range(start_addr, end_addr - byte_width + 2): # Adjust the loop to prevent reading past end_addr
            # Read multiple bytes based on byte_width and endian_type
            value_bytes = [self.pyboy.get_memory_value(addr + i) for i in range(byte_width)]
            value = int.from_bytes(value_bytes, 'little' if endian_type == EndianType.LITTLE else 'big')

            if value_type == ScanMode.BCD:
                value = bcd_to_dec(value, byte_width, endian_type)

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