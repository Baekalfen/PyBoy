from pyboy import PyBoy, bcd_to_dec, dec_to_bcd
from pyboy.api.memoryscanner import DynamicComparisonType


def test_bcd_to_dec_single_byte():
    assert bcd_to_dec(0b00110000) == 30


def test_dec_to_bcd_single_byte():
    assert dec_to_bcd(30) == 0b00110000


def test_bcd_to_dec_multi_byte():
    assert bcd_to_dec(0b0011000000110000, byte_width=2) == 3030


def test_dec_to_bcd_multi_byte():
    assert dec_to_bcd(3030, byte_width=2) == 0b0011000000110000


def test_bcd_to_dec_complex():
    assert bcd_to_dec(0b011101100101010010001001, byte_width=3) == 765489


def test_dec_to_bcd_complex():
    assert dec_to_bcd(765489, byte_width=3) == 0b011101100101010010001001


def test_bcd_to_dec_complex2():
    assert bcd_to_dec(0b10000000000000000000000000000000001000000, byte_width=6, byteorder="little") == 10000000040


def test_memoryscanner(kirby_rom):
    pyboy = PyBoy(kirby_rom, window_type="SDL2", game_wrapper=True)
    pyboy.set_emulation_speed(0)
    kirby = pyboy.game_wrapper()
    kirby.start_game()
    addresses = pyboy.memory_scanner.scan_memory()
    assert len(addresses) == 0x10000
    addresses = pyboy.memory_scanner.scan_memory(start_addr=0xC000, end_addr=0xDFFF)
    assert len(addresses) == 0xDFFF - 0xC000 + 1
    addresses = pyboy.memory_scanner.rescan_memory(DynamicComparisonType.INCREASED)
    assert len(addresses) == 0

    # Find score address
    pyboy.tick(1, True)
    pyboy.screen.image.show()
    score = 0
    addresses = pyboy.memory_scanner.scan_memory(score, start_addr=0xC000, end_addr=0xDFFF)
    assert len(addresses) > 1000, "We expected more values to be 0"
    pyboy.button_press("right")

    pyboy.tick(175, True) # Walk for 280 ticks
    pyboy.screen.image.show()
    addresses1 = pyboy.memory_scanner.rescan_memory(DynamicComparisonType.INCREASED)
    values1 = [pyboy.memory[x] for x in addresses]

    pyboy.tick(125, True) # Walk for 280 ticks
    addresses2 = pyboy.memory_scanner.rescan_memory(DynamicComparisonType.INCREASED)
    values2 = [pyboy.memory[x] for x in addresses]
    pyboy.screen.image.show()
    breakpoint()
    pass
