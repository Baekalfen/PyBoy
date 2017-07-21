# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import CoreDump
import os
import struct

from GenericMBC import GenericMBC
from GenericMBC import ROM_only
from MBC1 import MBC1
from MBC2 import MBC2
from MBC3 import MBC3
from MBC5 import MBC5

from Logger import logger

def Cartridge(filename):
    ROMBanks = loadROMfile(filename)
    cartType = ROMBanks[0][0x0147]

    # logger.debug("Cartridge type: " + hex(cartType))
    # ROMSize = ROMBanks[0][0x0148]
    # WARN: The following table doesn't work for MBC2! See Pan Docs
    exRAMCount = ExRAMTable[ROMBanks[0][0x0149]]

    validateCartType(cartType)
    cartInfo = cartridgeTable[cartType]
    logger.info("Cartridge type: 0x%0.2x - %s, %s" % (cartType, cartInfo[0].__name__, ", ".join([x for x,y in zip(["SRAM", "Battery", "RTC"], cartInfo[1:]) if y == True])))
    logger.info("Cartridge size: %d ROM banks of 16KB, %s RAM banks of 8KB" % (len(ROMBanks), ExRAMTable.get(exRAMCount,None)))
    ROMBankController = cartridgeTable[cartType]

    return ROMBankController[0](filename, ROMBanks, exRAMCount, cartType, *ROMBankController[1:])


def loadROMfile(filename):
    with open(filename, 'rb') as ROMFile:
        ROMData = ROMFile.read()

        bankSize = (16 * 1024)
        ROMBanks = [[0] * bankSize for n in xrange(len(ROMData) / bankSize)]

        for i, byte in enumerate(ROMData):
            ROMBanks[i / bankSize][i % bankSize] = ord(byte)

    return ROMBanks


def validateCartType(cartType):
    try:
        cartridgeInfo = cartridgeTable[cartType]
    except KeyError:
        raise Exception("Catridge type invalid: %s" % cartType)

    if cartridgeInfo is None:
        raise Exception("Cartridge type not supported")

cartridgeTable = {
#          MBC      , SRAM  , Battery , RTC
    0x00: (ROM_only , False , False   , False) , # ROM
    0x01: (MBC1     , False , False   , False) , # MBC1
    0x02: (MBC1     , True  , False   , False) , # MBC1+RAM
    0x03: (MBC1     , True  , True    , False) , # MBC1+RAM+BATT
    0x05: (MBC2     , False , False   , False) , # MBC2
    0x06: (MBC2     , False , True    , False) , # MBC2+BATTERY
    0x08: (ROM_only , True  , False   , False) , # ROM+RAM
    0x09: (ROM_only , True  , True    , False) , # ROM+RAM+BATTERY
    0x0F: (MBC3     , False , True    , True)  , # MBC3+TIMER+BATT
    0x10: (MBC3     , True  , True    , True)  , # MBC3+TIMER+RAM+BATT
    0x11: (MBC3     , False , False   , False) , # MBC3
    0x12: (MBC3     , True  , False   , False) , # MBC3+RAM
    0x13: (MBC3     , True  , True    , False) , # MBC3+RAM+BATT
    0x19: (MBC5     , False , False   , False) , # MBC5
    0x1A: (MBC5     , True  , False   , False) , # MBC5+RAM
    0x1B: (MBC5     , True  , True    , False) , # MBC5+RAM+BATT
}

# Number of 8KB banks
ExRAMTable = {
    0x00 : None,
    0x02 : 1,
    0x03 : 4,
    0x04 : 16,
}
