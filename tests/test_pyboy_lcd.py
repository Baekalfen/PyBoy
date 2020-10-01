#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.core.lcd import INTR_LCDC, LCD


def test_set_stat_mode():
    lcd = LCD()
    lcd._STAT._mode = 2 # Set mode 2 manually
    assert lcd._STAT._mode == 2 # Init value
    assert lcd._STAT.set_mode(2) == 0 # Already set

    lcd._STAT._mode = 0 # Set any mode that isn't 1
    assert lcd._STAT.set_mode(1) == 0 # Newly set, but no interrupt

    lcd._STAT._mode = 0 # Set any mode that isn't 1
    lcd.set_stat(1 << (1 + 3)) # Set mode 1 as interrupting
    assert lcd._STAT.set_mode(1) == INTR_LCDC # Newly set, now interrupting


def test_stat_register():
    # The Cycle Accurate Game Boy Docs
    # "Bit 7 is unused and always returns '1'. Bits 0-2 return '0' when the LCD is off."
    # 3 LSB are read-only

    lcd = LCD()
    lcd.set_lcdc(0b1000_0000) # Turn on LCD. Don't care about rest of the flags
    lcd._STAT.value &= 0b11111000 # Force LY=LYC and mode bits to 0
    lcd.set_stat(0b0111_1111) # Try to clear top bit, to check that it still returns 1. Try setting 3 LSB (read-only).
    assert (lcd.get_stat() & 0b1000_0000) == 0x80 # LCD on bit (read-only) will not be affected
    assert (lcd.get_stat() & 0b0000_0111) == 0b000

    assert (lcd.get_stat() & 0b11) == 0b00 # Check that we can read out screen mode
    lcd._STAT.set_mode(2)
    assert (lcd.get_stat() & 0b11) == 0b10 # Check that we can read out screen mode

    # lcd.set_stat(0b0111_1111) # Clear top bit, to check that it still returns 1


def test_check_lyc():
    lcd = LCD()

    lcd.LYC = 0
    lcd.LY = 0
    assert not lcd.get_stat() & 0b100 # LYC flag not set
    assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0 # Interrupts not enabled
    assert lcd.get_stat() & 0b100 # LYC flag set

    lcd.LYC = 0
    lcd.LY = 1
    assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0 # LYC!=LY, and no interrupts enabled
    assert not lcd.get_stat() & 0b100 # LYC flag automatically cleared

    lcd.LYC = 0
    lcd.LY = 0
    lcd.set_stat(0b0100_0000) # Enable LYC==LY interrupt
    assert not (lcd.get_stat() & 0b100) # LYC flag not set
    assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == INTR_LCDC # Trigger on seting LYC flag
    assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0 # Don't trigger on second call
    assert lcd.get_stat() & 0b100 # LYC flag set


def test_tick():
    lcd = LCD()
    assert lcd.clock == 0
    assert lcd.clock_target == 80

    def cyclestointerrupt(self):
        return self.clock_target - self.clock

    def tick(self, cycles):
        interrupt_flag = 0

        if self.LCDC.lcd_enable:
            self.clock += cycles

            self.LY = (self.clock % 70224) // 456
            interrupt_flag |= self.check_LYC() # Triggered many times?

            if self.clock >= self.clock_target:
                # Change to next mode
                if self._mode == 0 and self.LY != 144:
                    self._mode = 2
                else:
                    self._mode += 1
                    self._mode %= 4

                # Handle new mode
                if self._mode == 0: # HBLANK
                    interrupt_flag |= self.set_STAT_mode(0)
                    self.clock_target += 206
                elif self._mode == 1: # VBLANK
                    interrupt_flag |= INTR_VBLANK
                    interrupt_flag |= self.set_STAT_mode(1)
                    self.clock_target += 456 * 10
                    # Interrupt will trigger renderer.render_screen
                elif self._mode == 2: # Searching OAM
                    interrupt_flag |= self.set_STAT_mode(2)
                    self.clock_target += 80
                elif self._mode == 3: # Transferring data to LCD driver
                    interrupt_flag |= self.set_STAT_mode(3)
                    self.clock_target += 170
                    # Interrupt will trigger renderer.scanline
        else:
            self.clock = 0
            self.clock_target = 1 << 16
            self.LY = 0
        return interrupt_flag
