#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc import BaseMBC
from ..logger import logger


class MBC3(BaseMBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0b1010:
                self.rambank_enabled = True
            elif value == 0:
                self.rambank_enabled = False
            else:
                # Pan Docs: "Practically any value with 0Ah in the
                # lower 4 bits enables RAM, and any other value
                # disables RAM."
                self.rambank_enabled = False
                logger.warning("Unexpected command for MBC3: Address: 0x%0.4x, Value: 0x%0.2x"
                               % (address, value))
        elif 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            # print "ROM Bank switch:", value & 0b01111111
            self.rombank_selected = value & 0b01111111 # sets 7LSB of ROM bank address
        elif 0x4000 <= address < 0x6000:
            self.rambank_selected = value
        elif 0x6000 <= address < 0x8000:
            if self.rtc_enabled:
                self.rtc.writecommand(value)
            else:
                # NOTE: Pokemon Red/Blue will do this, but it can safely be ignored:
                # https://github.com/pret/pokered/issues/155
                logger.warning("RTC not present. Game tried to issue RTC command: 0x%0.4x, 0x%0.2x"
                               % (address, value))
        elif 0xA000 <= address < 0xC000:
            if self.rambank_selected <= 0x03:
                self.rambanks[self.rambank_selected][address-0xA000] = value
            elif 0x08 <= self.rambank_selected <= 0x0C:
                self.rtc.setregister(self.rambank_selected, value)
            else:
                raise logger.error("Invalid RAM bank selected: 0x%0.2x" % self.rambank_selected)
        else:
            raise logger.error("Invalid writing address: 0x%0.4x" % address)
