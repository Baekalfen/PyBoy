#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy


import os
import struct
import time

from ..logger import logger


class RTC:
    def __init__(self, filename):
        self.filename = filename + ".rtc"

        if not os.path.exists(self.filename):
            logger.info("No RTC file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.load_state(f)

        self.latchenabled = False

        self.timezero = time.time()

        self.seclatch = 0
        self.minlatch = 0
        self.hourlatch = 0
        self.daylatchlow = 0

        self.daylatchhigh = 0
        self.daycarry = 0
        self.halt = 0

    def stop(self):
        with open(self.filename, "wb") as f:
            self.save_state(f)

    def save_state(self, f):
        f.write(struct.pack('f', self.timezero))
        f.write(self.halt.to_bytes(1, 'little'))
        f.write(self.daycarry.to_bytes(1, 'little'))
        logger.info("RTC saved.")

    def load_state(self, f):
        self.timezero = struct.unpack('f', f.read(4))[0]
        self.halt = ord(f.read(1))
        self.daycarry = ord(f.read(1))
        logger.info("RTC loaded.")

    def latch_rtc(self):
        t = time.time() - self.timezero
        self.seclatch = int(t % 60)
        self.minlatch = int(t / 60 % 60)
        self.hourlatch = int(t / 3600 % 24)
        days = int(t / 3600 / 24)
        self.daylatchlow = days & 0xFF
        self.daylatchhigh = days >> 8

        if self.daylatchhigh > 1:
            self.daycarry = 1
            self.daylatchhigh &= 0b1
            # Add 0x200 (512) days to "reset" the day counter to zero
            self.timezero += 0x200 * 3600 * 24

    def writecommand(self, value):
        if value == 0x00:
            self.latchenabled = False
        elif value == 0x01:
            if not self.latchenabled:
                self.latch_rtc()
            self.latchenabled = True
        else:
            logger.warning("Invalid RTC command: %0.2x" % value)

    def getregister(self, register):
        if not self.latchenabled:
            logger.info("RTC: Get register, but nothing is latched! 0x%0.2x" % register)

        if register == 0x08:
            return self.seclatch
        elif register == 0x09:
            return self.minlatch
        elif register == 0x0A:
            return self.hourlatch
        elif register == 0x0B:
            return self.daylatchlow
        elif register == 0x0C:
            dayhigh = self.daylatchhigh & 0b1
            halt = self.halt << 6
            daycarry = self.daycarry << 7
            return dayhigh + halt + daycarry
        else:
            logger.warning("Invalid RTC register: %0.4x" % (register))

    def setregister(self, register, value):
        if not self.latchenabled:
            logger.info("RTC: Set register, but nothing is latched! 0x%0.4x, 0x%0.2x"
                        % (register, value))

        t = time.time() - self.timezero
        if register == 0x08:
            # TODO: What happens, when these value are larger than allowed?
            self.timezero -= int(t % 60) - value
        elif register == 0x09:
            self.timezero -= int(t / 60 % 60) - value
        elif register == 0x0A:
            self.timezero -= int(t / 3600 % 24) - value
        elif register == 0x0B:
            self.timezero -= int(t / 3600 / 24) - value
        elif register == 0x0C:
            dayhigh = value & 0b1
            halt = (value & 0b1000000) >> 6
            daycarry = (value & 0b10000000) >> 7

            self.halt = halt
            if self.halt == 0:
                pass  # TODO: Start the timer
            else:
                logger.warning("Stopping RTC is not implemented!")

            self.timezero -= int(t / 3600 / 24) - (dayhigh << 8)
            self.daycarry = daycarry
        else:
            logger.warning("Invalid RTC register: %0.4x %0.2x" % (register, value))
