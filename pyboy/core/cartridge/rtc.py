#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy

import struct
import time

import pyboy
from pyboy.utils import STATE_VERSION, IntIOWrapper

logger = pyboy.logging.get_logger(__name__)

RTC_CYCLES_PER_SECOND = 4_194_304


class RTC:
    def __init__(self, rtc_file):
        self.timezero = time.time()
        self.timelock = False
        self.day_carry = 0
        self.halt = 0
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.day_low = 0
        self.day_high = 0
        self.rtc_cycles = 0
        self.last_cycles = 0

        self.latch_enabled = False
        self.sec_latch = 0
        self.min_latch = 0
        self.hour_latch = 0
        self.day_latch_low = 0
        self.day_latch_high = 0

        if rtc_file is not None:
            self.load_state(IntIOWrapper(rtc_file), STATE_VERSION)
        else:
            logger.info("No RTC file found. Skipping.")
        self.timezero = time.time()

    def stop(self, rtc_file):
        if rtc_file is not None:
            self.save_state(IntIOWrapper(rtc_file))

    def save_state(self, f):
        now = time.time()
        elapsed = (
            self.seconds
            + self.minutes * 60
            + self.hours * 3600
            + ((self.day_high & 1) << 8 | self.day_low) * 86400
            + self.rtc_cycles / RTC_CYCLES_PER_SECOND
        )
        self.timezero = now - elapsed
        for b in struct.pack("d", self.timezero):
            f.write(b)
        f.write(self.halt)
        f.write(self.day_carry)
        f.write(self.seconds)
        f.write(self.minutes)
        f.write(self.hours)
        f.write(self.day_low)
        f.write(self.day_high & 1)
        f.write(self.halt)
        f.write(self.day_carry)
        f.write_64bit(self.rtc_cycles)
        for b in struct.pack("d", now):
            f.write(b)
        self.timezero = now

    def load_state(self, f, state_version):
        if state_version <= 12:
            self.timezero = int(struct.unpack("f", bytes([f.read() for _ in range(4)]))[0])
        else:
            self.timezero = struct.unpack("d", bytes([f.read() for _ in range(8)]))[0]
        self.halt = f.read()
        self.day_carry = f.read()

        if state_version < 21:
            self._load_legacy_state()
            return 0

        self.seconds = f.read() & 0x3F
        self.minutes = f.read() & 0x3F
        self.hours = f.read() & 0x1F
        self.day_low = f.read()
        self.day_high = f.read() & 1
        self.halt = f.read() & 1
        self.day_carry = f.read() & 1
        self.rtc_cycles = f.read_64bit() % RTC_CYCLES_PER_SECOND
        saved_time = struct.unpack("d", bytes([f.read() for _ in range(8)]))[0]

        self.last_cycles = 0

        if not self.halt and not self.timelock:
            elapsed = max(0.0, time.time() - saved_time)
            whole_seconds = int(elapsed)
            self.rtc_cycles += int((elapsed - whole_seconds) * RTC_CYCLES_PER_SECOND)
            self._advance_seconds(whole_seconds + self.rtc_cycles // RTC_CYCLES_PER_SECOND)
            self.rtc_cycles %= RTC_CYCLES_PER_SECOND

    def _load_legacy_state(self):
        elapsed = max(0.0, time.time() - self.timezero)
        if self.timelock:
            elapsed = 0.0
        whole_seconds = int(elapsed)
        self.seconds = whole_seconds % 60
        self.minutes = (whole_seconds // 60) % 60
        self.hours = (whole_seconds // 3600) % 24
        days = whole_seconds // 86400
        self.day_low = days & 0xFF
        self.day_high = (days >> 8) & 1
        if days >= 512:
            self.day_carry = 1
        self.rtc_cycles = int((elapsed - whole_seconds) * RTC_CYCLES_PER_SECOND)
        self.last_cycles = 0

    def _advance_seconds(self, seconds):
        # Make a quicker calculation without proper rollover when time is more than
        # an hour.
        if seconds > 60 * 60 and self.seconds < 60 and self.minutes < 60 and self.hours < 24:
            total = self.hours * 3600 + self.minutes * 60 + self.seconds + seconds
            days_elapsed = total // 86400
            total %= 86400
            self.hours = total // 3600
            self.minutes = (total // 60) % 60
            self.seconds = total % 60
            day = ((self.day_high & 1) << 8) | self.day_low
            day += days_elapsed
            if day > 0x1FF:
                self.day_carry = 1
                day &= 0x1FF
            self.day_low = day & 0xFF
            self.day_high = (day >> 8) & 1
            return

        # Do proper emulation of RTC
        while seconds:
            old_seconds = self.seconds
            old_minutes = self.minutes
            old_hours = self.hours

            if self.seconds in (59, 0x3F):
                self.seconds = 0
            else:
                self.seconds += 1

            if old_seconds == 59:
                if self.minutes in (59, 0x3F):
                    self.minutes = 0
                else:
                    self.minutes += 1

                if old_minutes == 59:
                    if self.hours in (23, 0x1F):
                        self.hours = 0
                    else:
                        self.hours += 1

                    if old_hours == 23:
                        day = ((self.day_high & 1) << 8) | self.day_low
                        day += 1
                        if day > 0x1FF:
                            day = 0
                            self.day_carry = 1
                        self.day_low = day & 0xFF
                        self.day_high = (day >> 8) & 1
            seconds -= 1

    def latch_rtc(self):
        if self.timelock:
            self.sec_latch = 0
            self.min_latch = 0
            self.hour_latch = 0
            self.day_latch_low = 0
            self.day_latch_high = 0
            return

        self.sec_latch = self.seconds & 0x3F
        self.min_latch = self.minutes & 0x3F
        self.hour_latch = self.hours & 0x1F
        self.day_latch_low = self.day_low
        self.day_latch_high = self.day_high & 1

    def tick(self, cycles):
        now = time.time()
        host_elapsed = now - self.timezero
        self.timezero = now

        if cycles < self.last_cycles:
            self.last_cycles = cycles
            return

        elapsed = cycles - self.last_cycles
        self.last_cycles = cycles
        if elapsed == 0 and host_elapsed > 0:
            elapsed = int(host_elapsed * RTC_CYCLES_PER_SECOND)
        if self.halt or self.timelock:
            return

        self.rtc_cycles += elapsed
        elapsed_seconds = self.rtc_cycles // RTC_CYCLES_PER_SECOND
        self.rtc_cycles %= RTC_CYCLES_PER_SECOND
        self._advance_seconds(elapsed_seconds)

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
            return

        if register == 0x08:
            self.seconds = value & 0x3F
            self.rtc_cycles = 0
        elif register == 0x09:
            self.minutes = value & 0x3F
        elif register == 0x0A:
            self.hours = value & 0x1F
        elif register == 0x0B:
            self.day_low = value
        elif register == 0x0C:
            day_high = value & 0b1
            halt = (value & 0b1000000) >> 6
            day_carry = (value & 0b10000000) >> 7

            self.day_high = day_high
            self.halt = halt
            self.day_carry = day_carry
        else:
            logger.debug("Invalid RTC register: %0.4x %0.2x", register, value)
