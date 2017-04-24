# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import CoreDump
from GenericMBC import GenericMBC

class MBC3(GenericMBC):
    def __setitem__(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0b1010:
                self.RAMBankEnabled = True
            elif value == 0:
                self.RAMBankEnabled = False
            else:
                raise CoreDump.CoreDump("Invalid command for MBC: Address: %s, Value: %s" % (hex(address), hex(value)))

        elif 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            # Same as for MBC1, except that the whole 7 bits of the RAM Bank Number are written
            # directly to this address
            self.ROMBankSelected = value & 0b01111111  # sets 7LSB of ROM bank address
        elif 0x4000 <= address < 0x6000:
            # MBC3 is always 16/8 mode
            self.RAMBankSelected = value # TODO: Should this has a mask?
        elif 0x6000 <= address < 0x8000:
            if self.rtcEnabled:
                self.rtc.writeCommand(value)
            else:
                # NOTE: Pokemon Red/Blue will do this, but it can safely be ignored:
                # https://github.com/pret/pokered/issues/155
                logging.info("RTC not present. Game tried to issue RTC command:", hex(address), hex(value))
        elif 0xA000 <= address < 0xC000:
            if self.RAMBankSelected <= 0x03:
                self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
            elif 0x08 <= self.RAMBankSelected <= 0x0C:
                self.rtc.setRegister(self.RAMBankSelected, value)
            else:
                raise CoreDump.CoreDump("Invalid RAM bank selected: %s" % hex(self.RAMBankSelected))
        else:
            raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))

