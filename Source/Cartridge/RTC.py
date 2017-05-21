# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import CoreDump
import time
import os
import struct
from Logger import logger

class RTC():
    def __init__(self):
        self.latchEnabled = False

        self.timeZero = time.time()

        self.secLatch = 0
        self.minLatch = 0
        self.hourLatch = 0
        self.dayLatchLow = 0

        self.dayLatchHigh = 0
        self.dayCarry = 0
        self.halt = 0

    def save(self, filename):
        logger.info("Saving RTC...")
        romPath, ext = os.path.splitext(filename)
        with open(romPath + ".rtc", "wb") as f:
            f.write(struct.pack('f', self.timeZero))
            f.write(chr(self.halt))
            f.write(chr(self.dayCarry))
        logger.info("RTC saved.")

    def load(self, filename):
        logger.info("Loading RTC...")
        try:
            romPath, ext = os.path.splitext(filename)
            with open(romPath + ".rtc", "rb") as f:
                # import pdb; pdb.set_trace()
                self.timeZero = struct.unpack('f',f.read(4))[0]
                self.halt = ord(f.read(1))
                self.dayCarry = ord(f.read(1))
            logger.info("RTC loaded.")
        except Exception as ex:
            logger.info("Couldn't read RTC for cartridge:", ex)

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
            raise CoreDump.CoreDump("Invalid RTC command: %s" % hex(value))

    def getRegister(self, register):
        if not self.latchEnabled:
            logger.info("RTC: Get register, but nothing is latched!", register)

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
            raise CoreDump.CoreDump("Invalid RTC register: %s" % hex(register))

    def setRegister(self, register, value):
        if not self.latchEnabled:
            logger.info("RTC: Set register, but nothing is latched!", register, value)

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
                raise CoreDump.CoreDump("Stopping RTC is not implemented!")

            self.timeZero -= int(t / 3600 / 24) - (dayHigh<<8)
            self.dayCarry = dayCarry
        else:
            raise CoreDump.CoreDump("Invalid RTC register: %s" % hex(register))
