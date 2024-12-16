#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import pytest

from pyboy.core.lcd import LCD, Renderer
from pyboy.utils import color_code, cython_compiled

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]

color_palette = (0xFFFFFF, 0x999999, 0x555555, 0x000000)
cgb_color_palette = (
    (0xFFFFFF, 0x7BFF31, 0x0063C5, 0x000000),
    (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000),
    (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000),
)


@pytest.mark.skipif(
    not hasattr(LCD, "get_stat"), reason="This test requires access to internal registers not available in Cython"
)
class TestLCD:
    def test_set_stat_mode(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd._STAT._mode = 2  # Set mode 2 manually
        assert lcd._STAT._mode == 2  # Init value
        assert lcd._STAT.set_mode(2) == 0  # Already set

        lcd._STAT._mode = 0  # Set any mode that isn't 1
        assert lcd._STAT.set_mode(1) == 0  # Newly set, but no interrupt

        lcd._STAT._mode = 0  # Set any mode that isn't 1
        lcd.set_stat(1 << (1 + 3))  # Set mode 1 as interrupting
        assert lcd._STAT.set_mode(1) == INTR_LCDC  # Newly set, now interrupting

    def test_stat_register(self):
        # The Cycle Accurate Game Boy Docs
        # "Bit 7 is unused and always returns '1'. Bits 0-2 return '0' when the LCD is off."
        # 3 LSB are read-only

        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd.set_lcdc(0b1000_0000)  # Turn on LCD. Don't care about rest of the flags
        lcd._STAT.value &= 0b11111000  # Force LY=LYC and mode bits to 0
        lcd.set_stat(
            0b0111_1111
        )  # Try to clear top bit, to check that it still returns 1. Try setting 3 LSB (read-only).
        assert (lcd.get_stat() & 0b1000_0000) == 0x80  # LCD on bit (read-only) will not be affected
        assert (lcd.get_stat() & 0b0000_0111) == 0b000

        assert (lcd.get_stat() & 0b11) == 0b00  # Check that we can read out screen mode
        lcd._STAT.set_mode(2)
        assert (lcd.get_stat() & 0b11) == 0b10  # Check that we can read out screen mode

        # lcd.set_stat(0b0111_1111) # Clear top bit, to check that it still returns 1

    def test_check_lyc(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)

        lcd.LYC = 0
        lcd.LY = 0
        assert not lcd.get_stat() & 0b100  # LYC flag not set
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0  # Interrupts not enabled
        assert lcd.get_stat() & 0b100  # LYC flag set

        lcd.LYC = 0
        lcd.LY = 1
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0  # LYC!=LY, and no interrupts enabled
        assert not lcd.get_stat() & 0b100  # LYC flag automatically cleared

        lcd.LYC = 0
        lcd.LY = 0
        lcd.set_stat(0b0100_0000)  # Enable LYC==LY interrupt
        assert not (lcd.get_stat() & 0b100)  # LYC flag not set
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == INTR_LCDC  # Trigger on seting LYC flag
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == INTR_LCDC  # Also trigger on second call
        assert lcd.get_stat() & 0b100  # LYC flag set


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
class TestRenderer:
    def test_colorcode_example(self):
        renderer = Renderer(False)

        # Color of the first pixel is 0b10
        # | Color of the second pixel is 0b01
        # v v
        # 1 0 0 1 0 0 0 1 <- byte1
        # 0 1 1 1 1 1 0 0 <- byte2
        b1_l = 0b0001
        b1_h = 0b1001
        b2_l = 0b1100
        b2_h = 0b0111
        assert renderer.colorcode_table[(b2_l << 4) | b1_l] == 0x01_00_02_02
        assert renderer.colorcode_table[(b2_h << 4) | b1_h] == 0x03_02_02_01

    def test_colorcode_table(self):
        renderer = Renderer(False)

        for byte1 in range(0x100):
            for byte2 in range(0x100):
                colorcode_low = renderer.colorcode_table[(byte1 & 0xF) | ((byte2 & 0xF) << 4)]
                colorcode_high = renderer.colorcode_table[((byte1 >> 4) & 0xF) | (byte2 & 0xF0)]
                for offset in range(4):
                    assert (colorcode_low >> (3 - offset) * 8) & 0xFF == color_code(byte1, byte2, offset)
                    assert (colorcode_high >> (3 - offset) * 8) & 0xFF == color_code(byte1, byte2, offset + 4)

    # def test_tick(self):
    #     lcd = LCD()
    #     assert lcd.clock == 0
    #     assert lcd.clock_target == 0

    #     def cycles_to_interrupt(self):
    #         return self.clock_target - self.clock

    #     def tick(self, cycles):
    #         interrupt_flag = 0

    #         if self.LCDC.lcd_enable:
    #             self.clock += cycles

    #             self.LY = (self.clock % 70224) // 456
    #             interrupt_flag |= self.check_LYC() # Triggered many times?

    #             if self.clock >= self.clock_target:
    #                 # Change to next mode
    #                 if self._mode == 0 and self.LY != 144:
    #                     self._mode = 2
    #                 else:
    #                     self._mode += 1
    #                     self._mode %= 4

    #                 # Handle new mode
    #                 if self._mode == 0: # HBLANK
    #                     interrupt_flag |= self.set_STAT_mode(0)
    #                     self.clock_target += 206
    #                 elif self._mode == 1: # VBLANK
    #                     interrupt_flag |= INTR_VBLANK
    #                     interrupt_flag |= self.set_STAT_mode(1)
    #                     self.clock_target += 456 * 10
    #                     # Interrupt will trigger renderer.render_screen
    #                 elif self._mode == 2: # Searching OAM
    #                     interrupt_flag |= self.set_STAT_mode(2)
    #                     self.clock_target += 80
    #                 elif self._mode == 3: # Transferring data to LCD driver
    #                     interrupt_flag |= self.set_STAT_mode(3)
    #                     self.clock_target += 170
    #                     # Interrupt will trigger renderer.scanline
    #         else:
    #             self.clock = 0
    #             self.clock_target = 1 << 16
    #             self.LY = 0
    #         return interrupt_flag
