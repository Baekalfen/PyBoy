#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array

from .mbc import ROM
from .mbc1 import MBC1
from .mbc2 import MBC2
from .mbc3 import MBC3
from .mbc5 import MBC5

from ..logger import logger


def Cartridge(filename):
    rombanks = loadromfile(filename)
    if not validatechecksum(rombanks):
        raise Exception("Cartridge header checksum mismatch!")

    # WARN: The following table doesn't work for MBC2! See Pan Docs
    exramcount = int(EXRAMTABLE[rombanks[0][0x0149]])

    carttype = rombanks[0][0x0147]
    cartinfo = CARTRIDGETABLE.get(carttype, None)
    if carttype is None:
        raise Exception("Catridge type invalid: %s" % carttype)

    logger.info("Cartridge type: 0x%0.2x - %s, %s" %
                (carttype, cartinfo[0].__name__, ", ".join(
                    [x for x, y in zip(["SRAM", "Battery", "RTC"], cartinfo[1:]) if y])))
    logger.info("Cartridge size: %d ROM banks of 16KB, %s RAM banks of 8KB" %
                (len(rombanks), EXRAMTABLE.get(exramcount, None)))
    rombankcontroller = CARTRIDGETABLE[carttype]

    return rombankcontroller[0](filename, rombanks, exramcount, carttype,
                                *rombankcontroller[1:])


def validatechecksum(rombanks):
    x = 0
    for m in range(0x134, 0x14D):
        x = x - rombanks[0][m] - 1
        x &= 0xff
    return rombanks[0][0x14D] == x


def loadromfile(filename):
    with open(filename, 'rb') as romfile:
        romdata = romfile.read()

        banksize = (16 * 1024)
        rombanks = [array.array('B', [0] * banksize) for n in range(len(romdata) // banksize)]

        for i, byte in enumerate(romdata):
            rombanks[i // banksize][i % banksize] = byte & 0xFF

    return rombanks


CARTRIDGETABLE = {
    #      MBC,  SRAM,  Battery, RTC
    0x00: (ROM,  False, False, False),  # ROM
    0x01: (MBC1, False, False, False),  # MBC1
    0x02: (MBC1, True,  False, False),  # MBC1+RAM
    0x03: (MBC1, True,  True,  False),  # MBC1+RAM+BATT
    0x05: (MBC2, False, False, False),  # MBC2
    0x06: (MBC2, False, True,  False),  # MBC2+BATTERY
    0x08: (ROM,  True,  False, False),  # ROM+RAM
    0x09: (ROM,  True,  True,  False),  # ROM+RAM+BATTERY
    0x0F: (MBC3, False, True,  True),   # MBC3+TIMER+BATT
    0x10: (MBC3, True,  True,  True),   # MBC3+TIMER+RAM+BATT
    0x11: (MBC3, False, False, False),  # MBC3
    0x12: (MBC3, True,  False, False),  # MBC3+RAM
    0x13: (MBC3, True,  True,  False),  # MBC3+RAM+BATT
    0x19: (MBC5, False, False, False),  # MBC5
    0x1A: (MBC5, True,  False, False),  # MBC5+RAM
    0x1B: (MBC5, True,  True,  False),  # MBC5+RAM+BATT
}

# Number of 8KB banks
EXRAMTABLE = {
    0x00: 1,  # We wrongfully allocate some RAM, to help Cython
    # 0x00: None,
    0x02: 1,
    0x03: 4,
    0x04: 16,
}
