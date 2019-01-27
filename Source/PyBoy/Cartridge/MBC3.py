# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .. import CoreDump
from .GenericMBC import GenericMBC

from ..Logger import logger

class MBC3(GenericMBC):
    def __setitem__(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0b1010:
                self.RAMBankEnabled = True
            elif value == 0:
                self.RAMBankEnabled = False
            else:
                # Pan Docs: "Practically any value with 0Ah in the lower 4 bits enables RAM, and any other value disables RAM."
                self.RAMBankEnabled = False
                logger.warn("Unexpected command for MBC3: Address: 0x%0.4x, Value: 0x%0.2x" % (address, value))
        elif 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            # print "ROM Bank switch:", value & 0b01111111
            self.ROMBankSelected = value & 0b01111111  # sets 7LSB of ROM bank address
        elif 0x4000 <= address < 0x6000:
            self.RAMBankSelected = value
        elif 0x6000 <= address < 0x8000:
            if self.rtcEnabled:
                self.rtc.writeCommand(value)
            else:
                # NOTE: Pokemon Red/Blue will do this, but it can safely be ignored:
                # https://github.com/pret/pokered/issues/155
                logger.warn("RTC not present. Game tried to issue RTC command: 0x%0.4x, 0x%0.2x" % (address, value))
        elif 0xA000 <= address < 0xC000:
            if self.RAMBankSelected <= 0x03:
                self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
            elif 0x08 <= self.RAMBankSelected <= 0x0C:
                self.rtc.setRegister(self.RAMBankSelected, value)
            else:
                raise CoreDump.CoreDump("Invalid RAM bank selected: 0x%0.2x" % self.RAMBankSelected)
        else:
            raise CoreDump.CoreDump("Invalid writing address: 0x%0.4x" % address)

