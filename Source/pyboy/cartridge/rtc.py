#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy


import time
import os
import struct
from ..logger import logger


class RTC():
    def __init__(self, filename):
        self.filename = filename + ".rtc"

        if not os.path.exists(self.filename):
            logger.info("No RTC file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.loadState(f)

        self.latchEnabled = False

        self.timeZero = time.time()

        self.secLatch = 0
        self.minLatch = 0
        self.hourLatch = 0
        self.dayLatchLow = 0

        self.dayLatchHigh = 0
        self.dayCarry = 0
        self.halt = 0

    def stop(self):
        with open(self.filename, "wb") as f:
            self.saveState(f)

    def saveState(self, f):
        f.write(struct.pack('f', self.timeZero))
        f.write(self.halt.to_bytes(1, 'little'))
        f.write(self.dayCarry.to_bytes(1, 'little'))
        logger.info("RTC saved.")

    def loadState(self, f):
        self.timeZero = struct.unpack('f',f.read(4))[0]
        self.halt = ord(f.read(1))
        self.dayCarry = ord(f.read(1))
        logger.info("RTC loaded.")

    def latchRTC(self):
        t = time.time() - self.timeZero
        self.secLatch = int(t % 60)
        self.minLatch = int(t / 60 % 60)
        self.hourLatch = int(t / 3600 % 24)
        days = int(t / 3600 / 24)
        self.dayLatchLow = days & 0xFF
        self.dayLatchHigh = days >> 8

        if self.dayLatchHigh > 1:
            self.dayCarry = 1
            self.dayLatchHigh &= 0b1
            self.timeZero += 0x200 * 3600 * 24 # Add 0x200 (512) days to "reset" the day counter to zero

    def writeCommand(self, value):
        if value == 0x00:
            self.latchEnabled = False
        elif value == 0x01:
            if not self.latchEnabled:
                self.latchRTC()
            self.latchEnabled = True
        else:
            logger.warning("Invalid RTC command: %0.2x" % value)

    def getRegister(self, register):
        if not self.latchEnabled:
            logger.info("RTC: Get register, but nothing is latched! 0x%0.2x" % register)

        if register == 0x08:
            return self.secLatch
        elif register == 0x09:
            return self.minLatch
        elif register == 0x0A:
            return self.hourLatch
        elif register == 0x0B:
            return self.dayLatchLow
        elif register == 0x0C:
            dayHigh = self.dayLatchHigh & 0b1
            halt = self.halt << 6
            dayCarry = self.dayCarry << 7
            return dayHigh + halt + dayCarry
        else:
            logger.warning("Invalid RTC register: %0.4x" % (register))

    def setRegister(self, register, value):
        if not self.latchEnabled:
            logger.info("RTC: Set register, but nothing is latched! 0x%0.4x, 0x%0.2x" % (register, value))

        t = time.time() - self.timeZero
        if register == 0x08:
            self.timeZero -= int(t % 60) - value # TODO: What happens, when these value are larger than allowed?
        elif register == 0x09:
            self.timeZero -= int(t / 60 % 60) - value
        elif register == 0x0A:
            self.timeZero -= int(t / 3600 % 24) - value
        elif register == 0x0B:
            self.timeZero -= int(t / 3600 / 24) - value
        elif register == 0x0C:
            dayHigh = value & 0b1
            halt = (value & 0b1000000) >> 6
            dayCarry = (value & 0b10000000) >> 7

            self.halt = halt
            if self.halt == 0:
                pass # TODO: Start the timer
            else:
                logger.warning("Stopping RTC is not implemented!")

            self.timeZero -= int(t / 3600 / 24) - (dayHigh<<8)
            self.dayCarry = dayCarry
        else:
            logger.warning("Invalid RTC register: %0.4x %0.2x" % (register, value))
