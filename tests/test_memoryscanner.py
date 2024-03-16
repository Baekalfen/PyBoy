from pyboy import PyBoy
from pyboy.api.memory_scanner import DynamicComparisonType
from pyboy.utils import bcd_to_dec, dec_to_bcd


def test_bcd_to_dec_single_byte():
    assert bcd_to_dec(0b00110000) == 30
    assert bcd_to_dec(0b00110001) == 31


def test_dec_to_bcd_single_byte():
    assert dec_to_bcd(30) == 0b00110000
    assert dec_to_bcd(32) == 0b00110010


def test_bcd_to_dec_multi_byte():
    assert bcd_to_dec(0b0011010000110010, byte_width=2) == 3432
    assert bcd_to_dec(0b0011010000110010, byte_width=2, byteorder="big") == 3234


def test_dec_to_bcd_multi_byte():
    assert dec_to_bcd(3034, byte_width=2) == 0b0011000000110100


def test_bcd_to_dec_complex():
    assert bcd_to_dec(0b011101100101010010001001, byte_width=3) == 765489


def test_dec_to_bcd_complex():
    assert dec_to_bcd(765489, byte_width=3) == 0b011101100101010010001001


def test_bcd_to_dec_complex2():
    assert bcd_to_dec(0b10000000000000000000000000000000001000000, byte_width=6, byteorder="little") == 10000000040


def test_memoryscanner_basic(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    addresses = pyboy.memory_scanner.scan_memory()
    assert len(addresses) == 0x10000
    addresses = pyboy.memory_scanner.scan_memory(start_addr=0xC000, end_addr=0xDFFF)
    assert len(addresses) == 0xDFFF - 0xC000 + 1
    addresses = pyboy.memory_scanner.rescan_memory(None, DynamicComparisonType.INCREASED)
    assert len(addresses) == 0


def test_memoryscanner_boundary(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    # Byte width of 1
    pyboy.memory[0xC000:0xD000] = 0
    addresses = pyboy.memory_scanner.scan_memory(0, start_addr=0xC000, end_addr=0xC0FF, byte_width=1)
    assert len(addresses) == 0x100 # We scan all two-byte addresses from 0, 1, 2, ..., n (including n)

    pyboy.memory[0xC0FF] = 1
    addresses = pyboy.memory_scanner.scan_memory(0, start_addr=0xC000, end_addr=0xC0FF, byte_width=1)
    assert len(addresses) == 0x100 - 1 # Where one value is now not 0

    # Byte width of 2
    pyboy.memory[0xC000:0xD000] = 0
    addresses = pyboy.memory_scanner.scan_memory(0, start_addr=0xC000, end_addr=0xC0FF, byte_width=2)
    assert len(
        addresses
    ) == 0x100 - 1 # We scan all two-byte addresses from 0, 1, 2, ..., n-1 (excluding n, as we can't go to n+1 for the second byte)

    pyboy.memory[0xC0FF] = 1
    addresses = pyboy.memory_scanner.scan_memory(0, start_addr=0xC000, end_addr=0xC0FF, byte_width=2)
    assert len(addresses) == 0x100 - 1 - 1 # Where one value is now not 0, and we cannot get n+1


SCORE_100 = 0xD072


def test_memoryscanner_absolute(kirby_rom):
    pyboy = PyBoy(kirby_rom, window="null")
    pyboy.set_emulation_speed(0)
    kirby = pyboy.game_wrapper
    kirby.start_game()

    # Find score address
    pyboy.tick(1, True)
    pyboy.button_press("right")

    pyboy.tick(175, True)
    assert pyboy.memory[SCORE_100] == 4
    addresses = pyboy.memory_scanner.scan_memory(4, start_addr=0xC000, end_addr=0xDFFF)
    assert SCORE_100 in addresses
    values = [pyboy.memory[x] for x in addresses]
    assert all([x == 4 for x in values])

    pyboy.tick(175, True)
    assert pyboy.memory[SCORE_100] == 8
    addresses = pyboy.memory_scanner.rescan_memory(8, DynamicComparisonType.MATCH)
    values = [pyboy.memory[x] for x in addresses]
    assert all([x == 8 for x in values])

    # Actual score address for third digit
    assert SCORE_100 in addresses
    assert pyboy.memory[SCORE_100] == 8


def test_memoryscanner_relative(kirby_rom):
    pyboy = PyBoy(kirby_rom, window="null")
    pyboy.set_emulation_speed(0)
    kirby = pyboy.game_wrapper
    kirby.start_game()

    # Find score address
    pyboy.tick(1, True)
    score = 0
    addresses = pyboy.memory_scanner.scan_memory(score, start_addr=0xC000, end_addr=0xDFFF)
    assert len(addresses) > 1000, "We expected more values to be 0"
    pyboy.button_press("right")

    pyboy.tick(175, True)
    addresses1 = pyboy.memory_scanner.rescan_memory(None, DynamicComparisonType.INCREASED)
    values1 = [pyboy.memory[x] for x in addresses1]

    pyboy.tick(175, True)
    addresses2 = pyboy.memory_scanner.rescan_memory(None, DynamicComparisonType.INCREASED)
    values2 = [pyboy.memory[x] for x in addresses2]

    # Actual score address for third digit
    assert SCORE_100 in addresses2
    assert pyboy.memory[SCORE_100] == 8
