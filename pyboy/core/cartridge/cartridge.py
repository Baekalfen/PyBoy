#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging
from array import array

from .base_mbc import ROMOnly
from .mbc1 import MBC1
from .mbc2 import MBC2
from .mbc3 import MBC3
from .mbc5 import MBC5

logger = logging.getLogger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


def load_cartridge(filename):
    rombanks = load_romfile(filename)
    if not validate_checksum(rombanks):
        raise Exception("Cartridge header checksum mismatch!")

    # WARN: The following table doesn't work for MBC2! See Pan Docs
    external_ram_count = int(EXTERNAL_RAM_TABLE[rombanks[0][0x0149]])

    carttype = rombanks[0][0x0147]
    cartinfo = CARTRIDGE_TABLE.get(carttype, None)
    if cartinfo is None:
        raise Exception("Catridge type invalid: %s" % carttype)

    cartdata = (
        carttype, cartinfo[0].__name__, ", ".join([x for x, y in zip(["SRAM", "Battery", "RTC"], cartinfo[1:]) if y])
    )
    logger.debug("Cartridge type: 0x%0.2x - %s, %s" % cartdata)
    logger.debug("Cartridge size: %d ROM banks of 16KB, %s RAM banks of 8KB" % (len(rombanks), external_ram_count))
    cartmeta = CARTRIDGE_TABLE[carttype]

    return cartmeta[0](filename, rombanks, external_ram_count, carttype, *cartmeta[1:])


def validate_checksum(rombanks):
    x = 0
    for m in range(0x134, 0x14D):
        x = x - rombanks[0][m] - 1
        x &= 0xff
    return rombanks[0][0x14D] == x


def load_romfile(filename):
    with open(filename, "rb") as romfile:
        romdata = array("B", romfile.read())

    logger.debug(f"Loading ROM file: {len(romdata)} bytes")
    if len(romdata) == 0:
        logger.error("ROM file is empty!")
        raise Exception("Empty ROM file")

    banksize = 16 * 1024
    if len(romdata) % banksize != 0:
        logger.error("Unexpected ROM file length")
        raise Exception("Bad ROM file size")

    if cythonmode:
        return memoryview(romdata).cast("B", shape=(len(romdata) // banksize, banksize))
    else:
        v = memoryview(romdata)
        return [v[i:i + banksize] for i in range(0, len(romdata), banksize)]


# yapf: disable
CARTRIDGE_TABLE = {
    #      MBC     , SRAM  , Battery , RTC
    0x00: (ROMOnly , False , False   , False) , # ROM
    0x01: (MBC1    , False , False   , False) , # MBC1
    0x02: (MBC1    , True  , False   , False) , # MBC1+RAM
    0x03: (MBC1    , True  , True    , False) , # MBC1+RAM+BATT
    0x05: (MBC2    , False , False   , False) , # MBC2
    0x06: (MBC2    , False , True    , False) , # MBC2+BATTERY
    0x08: (ROMOnly , True  , False   , False) , # ROM+RAM
    0x09: (ROMOnly , True  , True    , False) , # ROM+RAM+BATTERY
    0x0F: (MBC3    , False , True    , True)  , # MBC3+TIMER+BATT
    0x10: (MBC3    , True  , True    , True)  , # MBC3+TIMER+RAM+BATT
    0x11: (MBC3    , False , False   , False) , # MBC3
    0x12: (MBC3    , True  , False   , False) , # MBC3+RAM
    0x13: (MBC3    , True  , True    , False) , # MBC3+RAM+BATT
    0x19: (MBC5    , False , False   , False) , # MBC5
    0x1A: (MBC5    , True  , False   , False) , # MBC5+RAM
    0x1B: (MBC5    , True  , True    , False) , # MBC5+RAM+BATT
    0x1C: (MBC5    , False , False   , False) , # MBC5+RUMBLE
    0x1D: (MBC5    , True  , False   , False) , # MBC5+RUMBLE+RAM
    0x1E: (MBC5    , True  , True    , False) , # MBC5+RUMBLE+RAM+BATT
}
# yapf: enable

# Number of external 8KB banks in the cartridge. Taken from Pan Docs
EXTERNAL_RAM_TABLE = {
    0x00: 1, # We wrongfully allocate some RAM, to help Cython
    0x01: 1, # Only supposed to be 2KB, but we allocate 8KB.
    0x02: 1,
    0x03: 4,
    0x04: 16,
    0x05: 8,
}
