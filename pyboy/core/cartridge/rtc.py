#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy

import os
import struct
import time

import pyboy
from pyboy.utils import STATE_VERSION, IntIOWrapper

logger = pyboy.logging.get_logger(__name__)


class RTC:
    def __init__(self, filename):
        self.filename = filename + ".rtc"

        self.timezero = time.time()
        self.timelock = False
        self.day_carry = 0
        self.halt = 0

        if not os.path.exists(self.filename):
            logger.info("No RTC file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.load_state(IntIOWrapper(f), STATE_VERSION)

        self.latch_enabled = False
        self.sec_latch = 0
        self.min_latch = 0
        self.hour_latch = 0
        self.day_latch_low = 0
        self.day_latch_high = 0

    def stop(self):
        with open(self.filename, "wb") as f:
            self.save_state(IntIOWrapper(f))

    def save_state(self, f):
        for b in struct.pack("d", self.timezero):
            f.write(b)
        f.write(self.halt)
        f.write(self.day_carry)

    def load_state(self, f, state_version):
        if state_version <= 12:
            self.timezero = int(struct.unpack("f", bytes([f.read() for _ in range(4)]))[0])
        else:
            self.timezero = struct.unpack("d", bytes([f.read() for _ in range(8)]))[0]
        self.halt = f.read()
        self.day_carry = f.read()

    def latch_rtc(self):
        if self.timelock:
            t = 0
        else:
            t = time.time() - self.timezero
        self.sec_latch = int(t % 60)
        self.min_latch = int((t // 60) % 60)
        self.hour_latch = int((t // 3600) % 24)
        days = int(t // 3600 // 24)
        self.day_latch_low = days & 0xFF
        self.day_latch_high = days >> 8

        if self.day_latch_high > 1:
            self.day_carry = 1
            self.day_latch_high &= 0b1
            # Add 0x200 (512) days to "reset" the day counter to zero
            self.timezero += 0x200 * 3600 * 24

    def writecommand(self, value):
        if value == 0x00:
            self.latch_enabled = False
        elif value == 0x01:
            if not self.latch_enabled:
                self.latch_rtc()
            self.latch_enabled = True
        else:
            logger.debug("Invalid RTC command: %0.2x", value)

    def getregister(self, register):
        if not self.latch_enabled:
            logger.debug("RTC: Get register, but nothing is latched! 0x%0.2x", register)

        if register == 0x08:
            return self.sec_latch
        elif register == 0x09:
            return self.min_latch
        elif register == 0x0A:
            return self.hour_latch
        elif register == 0x0B:
            return self.day_latch_low
        elif register == 0x0C:
            day_high = self.day_latch_high & 0b1
            halt = self.halt << 6
            day_carry = self.day_carry << 7
            return day_high + halt + day_carry
        else:
            logger.debug("Invalid RTC register: %0.4x", register)

    def setregister(self, register, value):
        if not self.latch_enabled:
            logger.debug("RTC: Set register, but nothing is latched! 0x%0.4x, 0x%0.2x", register, value)

        if self.timelock:
            t = 0
        else:
            t = time.time() - self.timezero
        if register == 0x08:
            # TODO: What happens, when these value are larger than allowed?
            self.timezero = self.timezero - (t % 60) - value
        elif register == 0x09:
            self.timezero = self.timezero - (t // 60 % 60) - value
        elif register == 0x0A:
            self.timezero = self.timezero - (t // 3600 % 24) - value
        elif register == 0x0B:
            self.timezero = self.timezero - (t // 3600 // 24) - value
        elif register == 0x0C:
            day_high = value & 0b1
            halt = (value & 0b1000000) >> 6
            day_carry = (value & 0b10000000) >> 7

            self.halt = halt
            if self.halt == 0:
                pass  # TODO: Start the timer
            else:
                logger.debug("Stopping RTC is not implemented!")

            self.timezero = self.timezero - (t // 3600 // 24) - (day_high << 8)
            self.day_carry = day_carry
        else:
            logger.debug("Invalid RTC register: %0.4x %0.2x", register, value)
