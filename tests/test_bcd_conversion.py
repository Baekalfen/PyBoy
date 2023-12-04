from pyboy.utils import BCDConverter,EndianType

def test_bcd_to_dec_single_byte():
    converter = BCDConverter()
    assert converter.bcd_to_dec(0b00110000) == 30

def test_dec_to_bcd_single_byte():
    converter = BCDConverter()
    assert converter.dec_to_bcd(30) == 0b00110000

def test_bcd_to_dec_multi_byte():
    converter = BCDConverter()
    assert converter.bcd_to_dec(0b0011000000110000, byte_width=2) == 3030

def test_dec_to_bcd_multi_byte():
    converter = BCDConverter()
    assert converter.dec_to_bcd(3030, byte_width=2) == 0b0011000000110000

def test_bcd_to_dec_complex():
    converter = BCDConverter()
    assert converter.bcd_to_dec(0b011101100101010010001001, byte_width=3) == 765489

def test_dec_to_bcd_complex():
    converter = BCDConverter()
    assert converter.dec_to_bcd(765489, byte_width=3) == 0b011101100101010010001001

def test_bcd_to_dec_complex2():
    converter = BCDConverter()
    assert converter.bcd_to_dec(0b10000000000000000000000000000000001000000, byte_width=6, endian_type=EndianType.LITTLE) == 10000000040