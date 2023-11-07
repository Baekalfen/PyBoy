import numpy as np

STRING_TERMINATOR = 80
ASCII_DELTA = 63

def get_character_index(character):
    if character == ' ':
        return 0x7F
    if character == '?':
        return 0xE6
    if character == '!':
        return 0xE7
    if character == 'é':
        return 0xBA

    index = ord(character)
    if index > 47 and index < 58:
        # number
        return index + 197
    return index + ASCII_DELTA

def read_multibyte_value(pyboy, addr, num_bytes):
    val = 0
    for i in range(num_bytes):
        val += pyboy.get_memory_value(addr+i) << i*8
    return val

def get_int_at_address(pyboy, address, size=2, byte_order='big'):
    """Returns an integer from a given address of a specified size."""
    bytes = []
    for i in range(size):
        bytes.append(pyboy.get_memory_value(address + i))
    return int.from_bytes(bytes, byteorder=byte_order)

def set_int_at_address(pyboy, address, value, size=2, byte_order='big'):
    """Sets an integer at a given address of a specified size."""
    bytes = value.to_bytes(2, byteorder=byte_order)
    i = 0
    for byte in bytes:
        pyboy.set_memory_value(address + i, byte)
        i += 1

def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

