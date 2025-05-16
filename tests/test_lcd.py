#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io

import pytest

import numpy as np
from pyboy import PyBoy
from pyboy.core.lcd import CGBLCD, LCD, Renderer
from pyboy.utils import cython_compiled, INTR_LCDC, FRAME_CYCLES

color_palette = (0xFFFFFF, 0x999999, 0x555555, 0x000000)
cgb_color_palette = (
    (0xFFFFFF, 0x7BFF31, 0x0063C5, 0x000000),
    (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000),
    (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000),
)


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_cycles_when_enabling_lcd(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    c = 0
    assert pyboy._cycles() == 0

    for n in range(4):  # Specific number of frames where LCDC is disabled on boot.
        pyboy.tick(1)
        print("cycles for frame:", pyboy._cycles() - c)
        assert pyboy._cycles() - c == FRAME_CYCLES
        assert not pyboy.mb.lcd._LCDC.lcd_enable
        assert pyboy.mb.lcd.LY == 0
        c = pyboy._cycles()

    pyboy.tick(1, True)  # Enable render to check blank screen
    assert np.all(pyboy.screen.ndarray == 255)
    print("cycles for frame:", pyboy._cycles() - c)
    assert pyboy.mb.lcd._LCDC.lcd_enable
    assert pyboy._cycles() - c == 17016  # Specific cycles when LCD is reenabled, and tick-frame is flushed.

    # When disabling LCD, we still do the write to set_lcdc before accounting for the 8-cycle opcode.
    # These 8 cycles are placed on the closing frame and we start on a clean slate.
    assert pyboy.mb.lcd.clock == 0
    assert pyboy.mb.lcd.clock_target == 80

    # Because the LCD should never render the first frame after enabling LCDC
    # We should always see a white (disabled) screen.
    c = pyboy._cycles()
    pyboy.tick(1, True)
    assert np.all(pyboy.screen.ndarray == 255)
    assert abs((pyboy._cycles() - c) - FRAME_CYCLES) <= 20, "Frame cycles should be within maximum possible overshoot"

    c = pyboy._cycles()
    pyboy.tick(1, True)
    assert not np.all(pyboy.screen.ndarray == 255)
    assert abs((pyboy._cycles() - c) - FRAME_CYCLES) <= 20, "Frame cycles should be within maximum possible overshoot"

    # We expect a new frame to be calulated immediately as per "cycle accurate"?
    for n in range(200):
        pyboy.mb.lcd.frame_done = False
        c = pyboy._cycles()
        pyboy.tick(1)
        print("cycles for frame:", pyboy._cycles() - c)
        assert (
            abs((pyboy._cycles() - c) - FRAME_CYCLES) <= 20
        ), "Frame cycles should be within maximum possible overshoot"

    c = pyboy._cycles()
    assert (
        c - 17016
    ) // FRAME_CYCLES == 206, "Expected 206 frames worth of cycles plus the odd cycles when turning LCD on"
    assert (c - 17016) % FRAME_CYCLES <= 20, "Expected the only remainder to be within the maximum overshoot of a frame"


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_cycles_when_disabling_lcd(default_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym", log_level="DEBUG")
    pyboy.tick(60, False, False)

    def hook(context):
        if context[0].memory[0xFF40] & 0x80:
            context[0].memory[0xFF40] &= 0b0111_1111  # Disable LCD
            context[1] += 1
            print("frame count", context[0].frame_count)
            # if context[1] > 1:
            #     breakpoint()
            pass
            # breakpoint()

    context = [pyboy, 0]
    pyboy.hook_register(None, "Main.inner_loop", hook, context)

    # Hook will disable in VBLANK, but continue until full frame is done.
    while not context[1]:
        c = pyboy._cycles()
        pyboy.tick(1, False, False)

    assert context[1] == 1
    assert not pyboy.mb.lcd._LCDC.lcd_enable

    cycles = pyboy._cycles() - c
    # Should actually be significantly lower than FRAME_CYCLES, as we disabled LCD early in VBLANK
    assert cycles <= FRAME_CYCLES
    # Fragile, but used as sanity check for now
    assert cycles // 456 == 148

    # Next cycle should be a full FRAME_CYCLE, as it's just a regular frame with LCD disabled
    c = pyboy._cycles()
    pyboy.tick(1, False, False)
    assert abs((pyboy._cycles() - c) - FRAME_CYCLES) <= 20, "Frame cycles should be within maximum possible overshoot"


def test_firstwhite(firstwhite_file):
    pyboy = PyBoy(firstwhite_file, window="null")
    pyboy.tick(120, True)
    for _ in range(30):
        # Because the LCD should never render the first frame after enabling LCDC
        # We should always see a white (disabled) screen.
        pyboy.tick(1, True)
        assert np.all(pyboy.screen.ndarray == 255)


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_saveload_cycles(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    print(pyboy.mb.lcd._cycles_to_frame, pyboy.mb.lcd.clock, pyboy.mb.lcd.clock_target)

    for _ in range(120):
        pyboy.tick(1, False, False)
        print(pyboy.mb.lcd._cycles_to_frame, pyboy.mb.lcd.clock, pyboy.mb.lcd.clock_target)
        assert (
            pyboy.mb.lcd._cycles_to_frame >= 0
        )  # Could be slightly negative? >= -20? (longest opcode 24, minus 4 as the minimum missing before 0)
        assert pyboy.mb.lcd.clock >= 0
        assert pyboy.mb.lcd.clock_target >= 0

    saved_state = io.BytesIO()
    pyboy.save_state(saved_state)

    pyboy.tick(10, False, False)  # Any unaccounted cycles will be offset

    # Load
    saved_state.seek(0)
    pyboy.load_state(saved_state)

    assert pyboy.mb.lcd._cycles_to_frame >= 0
    assert pyboy.mb.lcd.clock >= 0
    assert pyboy.mb.lcd.clock_target >= 0


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
class TestLCD:
    def test_set_stat_mode(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd._STAT._mode = 2  # Set mode 2 manually
        assert lcd._STAT._mode == 2  # Init value
        assert lcd._STAT.set_mode(2) == 0  # Already set

        lcd._STAT._mode = 0  # Set any mode that isn't 1
        assert lcd._STAT.set_mode(1) == 0  # Newly set, but no interrupt

        lcd._STAT._mode = 0  # Set any mode that isn't 1
        lcd._STAT.set(1 << (1 + 3))  # Set mode 1 as interrupting
        assert lcd._STAT.set_mode(1) == INTR_LCDC  # Newly set, now interrupting

    def test_stat_register(self):
        # The Cycle Accurate Game Boy Docs
        # "Bit 7 is unused and always returns '1'. Bits 0-2 return '0' when the LCD is off."
        # 3 LSB are read-only

        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd.set_lcdc(0b1000_0000)  # Turn on LCD. Don't care about rest of the flags
        lcd._STAT.value &= 0b11111000  # Force LY=LYC and mode bits to 0
        lcd._STAT.set(
            0b0111_1111
        )  # Try to clear top bit, to check that it still returns 1. Try setting 3 LSB (read-only).
        assert (lcd._STAT.value & 0b1000_0000) == 0x80  # LCD on bit (read-only) will not be affected
        assert (lcd._STAT.value & 0b0000_0111) == 0b000

        assert (lcd._STAT.value & 0b11) == 0b00  # Check that we can read out screen mode
        lcd._STAT.set_mode(2)
        assert (lcd._STAT.value & 0b11) == 0b10  # Check that we can read out screen mode

        # lcd._STAT.set(0b0111_1111) # Clear top bit, to check that it still returns 1

    def test_check_lyc(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)

        lcd.LYC = 0
        lcd.LY = 0
        assert not lcd._STAT.value & 0b100  # LYC flag not set
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0  # Interrupts not enabled
        assert lcd._STAT.value & 0b100  # LYC flag set

        lcd.LYC = 0
        lcd.LY = 1
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == 0  # LYC!=LY, and no interrupts enabled
        assert not lcd._STAT.value & 0b100  # LYC flag automatically cleared

        lcd.LYC = 0
        lcd.LY = 0
        lcd._STAT.set(0b0100_0000)  # Enable LYC==LY interrupt
        assert not (lcd._STAT.value & 0b100)  # LYC flag not set
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == INTR_LCDC  # Trigger on seting LYC flag
        assert lcd._STAT.update_LYC(lcd.LYC, lcd.LY) == INTR_LCDC  # Also trigger on second call
        assert lcd._STAT.value & 0b100  # LYC flag set

    def test_frame_cycles_disabled(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        assert not lcd._LCDC.lcd_enable

        assert lcd.clock == 0
        assert lcd.clock_target == FRAME_CYCLES
        assert lcd._cycles_to_interrupt == 0
        assert lcd._cycles_to_frame == FRAME_CYCLES

        lcd.tick(FRAME_CYCLES - 1)
        assert lcd.clock == FRAME_CYCLES - 1
        assert lcd.clock_target == FRAME_CYCLES
        assert lcd._cycles_to_interrupt == 1
        assert lcd._cycles_to_frame == 1

        lcd.tick(FRAME_CYCLES)
        assert lcd.clock == 0
        assert lcd.clock_target == FRAME_CYCLES
        assert lcd._cycles_to_interrupt == FRAME_CYCLES
        assert lcd._cycles_to_frame == FRAME_CYCLES

    def test_frame_cycles_toggle_on(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        assert not lcd._LCDC.lcd_enable

        lcd.set_lcdc(1 << 7)  # Enable LCD
        lcd.tick(FRAME_CYCLES - 1000)
        assert lcd._LCDC.lcd_enable

        # Whatever clock for outstanding blank frame is flushed
        assert lcd.clock == 0
        assert lcd.frame_done
        assert lcd.first_frame

        lcd.tick(FRAME_CYCLES - 1000 + 1)  # Tick 1 cycles to update stat mode, clock target, _cycles_to_...
        assert lcd._STAT._mode == 2  # First STAT mode for scanline
        assert lcd.clock_target == 80  # Assumed from stat mode 2
        assert lcd._cycles_to_interrupt == 80 - 1
        assert lcd._cycles_to_frame == FRAME_CYCLES - 1

    def test_frame_cycles_enabled(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd.set_lcdc(1 << 7)  # Enable LCD
        assert lcd._LCDC.lcd_enable

        pre_ticks = 1
        lcd.tick(pre_ticks)  # Need to tick to update registers

        assert lcd.clock == 0
        assert lcd.clock_target == 80  # STAT mode 2
        assert lcd._cycles_to_interrupt == 80
        assert lcd._cycles_to_frame == FRAME_CYCLES
        assert lcd.frame_done  # When initially enable the LCD, we flush the frame
        lcd.frame_done = False  # frame_done is reset from MB

        for i, cycle in enumerate(range(pre_ticks, FRAME_CYCLES - 1 + pre_ticks)):
            lcd.tick(cycle)  # Progresses cycles to new absolute cycles. NOT RELATIVE!
            assert lcd._cycles_to_frame == FRAME_CYCLES - i
            assert not lcd.frame_done

        # We should now be in a state of 1 cycle left, and frame not done!
        lcd.tick(FRAME_CYCLES + pre_ticks)
        assert lcd.clock == 0
        assert lcd.clock_target == 80  # STAT mode 2
        assert lcd._cycles_to_interrupt == 80
        assert lcd._cycles_to_frame == FRAME_CYCLES
        assert lcd.frame_done  # We just exactly close the frame

    def test_frame_cycles_enabled_overshoot(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd.set_lcdc(1 << 7)  # Enable LCD
        assert lcd._LCDC.lcd_enable

        # The maximum possible overshoot. Longest opcode is 24 cycles, minus 4, as the smallest missing cycles
        lcd.tick(FRAME_CYCLES + 20)

    def test_frame_cycles_toggle_off(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        assert not lcd._LCDC.lcd_enable

        lcd.tick(FRAME_CYCLES - 1000)
        lcd.set_lcdc(1 << 7)  # Enable LCD
        assert lcd._LCDC.lcd_enable

        # 1. Run until part of VBLANK
        # 2. Disabled LCD
        # 3. Clock gets reset
        # 4. Reenable LCD
        # 5. The cycles between LY 144 and 153 from the first frame are lost

        # Enable should start immediately

        # Disable in VBLANK, but continue until full frame is done.

        # Check one blank frame after enabling, but it should be progressing and increase LCD registers (cycles, LY, LYC)
        # https://forums.nesdev.org/viewtopic.php?f=20&t=18023

    def test_frame_cycles_double_speed(self):
        lcd = CGBLCD(True, True, color_palette, cgb_color_palette)
        lcd.set_lcdc(1 << 7)  # Enable LCD
        assert lcd._LCDC.lcd_enable

        lcd.speed_shift = 1  # Emulation CGB double speed mode. Now we need twice as many cycles on .tick() as before.

        pre_ticks = 2
        lcd.tick(pre_ticks)  # Need to tick to update registers

        assert lcd.clock == 0
        # NOTE: CGB double speed: clock_target is internal and shows normal timings
        assert lcd.clock_target == 80  # STAT mode 2
        # NOTE: CGB double speed: _cycles_to_interrupt is external and shows double timings
        assert lcd._cycles_to_interrupt == 80 * 2
        assert lcd._cycles_to_frame == FRAME_CYCLES * 2
        assert lcd.frame_done  # When initially enable the LCD, we flush the frame
        lcd.frame_done = False  # frame_done is reset from MB

        for i, cycle in enumerate(
            range(pre_ticks, FRAME_CYCLES * 2 - 2 + pre_ticks, 2)
        ):  # Resolution not less than 2 cycles! Real hardware shows no less than 4...
            lcd.tick(cycle)  # Progresses cycles to new absolute cycles. NOT RELATIVE!
            assert lcd._cycles_to_frame == FRAME_CYCLES * 2 - i * 2
            assert not lcd.frame_done

        # We should now be in a state of 1 cycle left, and frame not done!
        lcd.tick(FRAME_CYCLES * 2 + pre_ticks)
        assert lcd.clock == 0
        # NOTE: CGB double speed: clock_target is internal and shows normal timings
        assert lcd.clock_target == 80  # STAT mode 2
        # NOTE: CGB double speed: _cycles_to_interrupt is external and shows double timings
        assert lcd._cycles_to_interrupt == 80 * 2
        assert lcd._cycles_to_frame == FRAME_CYCLES * 2
        assert lcd.frame_done  # We just exactly close the frame

    def test_frame_cycles_modes(self):
        lcd = LCD(False, False, color_palette, cgb_color_palette)
        lcd.set_lcdc(1 << 7)  # Enable LCD
        assert lcd._LCDC.lcd_enable

        pre_ticks = 1
        lcd.tick(pre_ticks)  # Need to tick to update registers
        lcd.frame_done = False  # frame_done is reset from MB

        for i, cycle in enumerate(range(pre_ticks, FRAME_CYCLES - 1 + pre_ticks)):
            lcd.tick(cycle)  # Progresses cycles to new absolute cycles. NOT RELATIVE!
            assert lcd.clock == i
            assert lcd._cycles_to_frame == FRAME_CYCLES - i
            assert not lcd.frame_done

            ly = lcd.clock // 456
            assert lcd.LY == ly
            if ly < 144:
                ly_remainder = lcd.clock % 456
                if ly_remainder < 80:
                    assert lcd._STAT._mode == 2
                    assert lcd.cycles_to_mode0() == 456 - 206 - ly_remainder
                elif ly_remainder < 80 + 170:
                    assert lcd._STAT._mode == 3
                    assert lcd.cycles_to_mode0() == 456 - 206 - ly_remainder
                elif ly_remainder < 80 + 170 + 206:
                    assert lcd._STAT._mode == 0  # HBLANK
                    assert lcd.cycles_to_mode0() == 0
                else:
                    assert None, "Invalid STAT mode for LY and clock"
            else:
                ly_remainder = lcd.clock % 456
                assert lcd._STAT._mode == 1  # VBLANK
                assert lcd.cycles_to_mode0() == 456 * (153 - lcd.LY + 1) + (456 - 206 - ly_remainder)


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
        def legacy_color_code(byte1, byte2, offset):
            """Convert 2 bytes into color code at a given offset.

            The colors are 2 bit and are found like this:

            Color of the first pixel is 0b10
            | Color of the second pixel is 0b01
            v v
            1 0 0 1 0 0 0 1 <- byte1
            0 1 1 1 1 1 0 0 <- byte2
            """
            return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)

        renderer = Renderer(False)

        for byte1 in range(0x100):
            for byte2 in range(0x100):
                colorcode_low = renderer.colorcode_table[(byte1 & 0xF) | ((byte2 & 0xF) << 4)]
                colorcode_high = renderer.colorcode_table[((byte1 >> 4) & 0xF) | (byte2 & 0xF0)]
                for offset in range(4):
                    assert (colorcode_low >> (3 - offset) * 8) & 0xFF == legacy_color_code(byte1, byte2, offset)
                    assert (colorcode_high >> (3 - offset) * 8) & 0xFF == legacy_color_code(byte1, byte2, offset + 4)
