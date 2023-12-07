from pyboy import bcd_to_dec, dec_to_bcd


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
