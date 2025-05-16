#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array
from ctypes import c_void_p
from random import getrandbits

import pyboy
from pyboy.utils import PyBoyException, INTR_VBLANK, INTR_LCDC, FRAME_CYCLES
from pyboy.api.constants import ROWS, COLS, TILES

logger = pyboy.logging.get_logger(__name__)

VIDEO_RAM = 8 * 1024  # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0


def rgb_to_bgr(color):
    a = 0xFF
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (a << 24) | (b << 16) | (g << 8) | r


class LCD:
    def __init__(self, cgb, cartridge_cgb, color_palette, cgb_color_palette, randomize=False):
        self.VRAM0 = array("B", [0] * VIDEO_RAM)
        self.OAM = array("B", [0] * OBJECT_ATTRIBUTE_MEMORY)
        self.disable_renderer = False

        if randomize:
            for i in range(VIDEO_RAM):
                self.VRAM0[i] = getrandbits(8)
            for i in range(OBJECT_ATTRIBUTE_MEMORY):
                self.OAM[i] = getrandbits(8)

        self._LCDC = LCDCRegister(0)
        self._STAT = STATRegister()  # Bit 7 is always set.

        self.speed_shift = 0
        self.clock = 0
        self.clock_target = FRAME_CYCLES
        self.frame_done = False
        self.first_frame = False
        self.reset = False
        self._cycles_to_interrupt = 0
        self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift
        self.next_stat_mode = 2
        self.LY = 0x00
        self._STAT.set_mode(0)

        self.SCY = 0x00
        self.SCX = 0x00
        self.LYC = 0x00
        # self.DMA = 0x00
        self.WY = 0x00
        self.WX = 0x00

        self.cgb = cgb
        self._scanlineparameters = [[0, 0, 0, 0, 0] for _ in range(ROWS)]
        self.last_cycles = 0
        self._cycles_to_interrupt = 0
        self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift

        if self.cgb:
            # Setting for both modes, even though CGB is ignoring them. BGP[0] used in scanline_blank.
            bg_pal, obj0_pal, obj1_pal = cgb_color_palette
            self.BGP = PaletteRegister(0xFC, [(rgb_to_bgr(c)) for c in bg_pal])
            self.OBP0 = PaletteRegister(0xFF, [(rgb_to_bgr(c)) for c in obj0_pal])
            self.OBP1 = PaletteRegister(0xFF, [(rgb_to_bgr(c)) for c in obj1_pal])
            if cartridge_cgb:
                logger.debug("Starting CGB renderer")
                self.renderer = CGBRenderer()
            else:
                logger.debug("Starting CGB renderer in DMG-mode")
                # Running DMG ROM on CGB hardware uses the palettes above
                self.renderer = Renderer(False)
        else:
            logger.debug("Starting DMG renderer")
            self.BGP = PaletteRegister(0xFC, [(rgb_to_bgr(c)) for c in color_palette])
            self.OBP0 = PaletteRegister(0xFF, [(rgb_to_bgr(c)) for c in color_palette])
            self.OBP1 = PaletteRegister(0xFF, [(rgb_to_bgr(c)) for c in color_palette])
            self.renderer = Renderer(False)

    def set_lcdc(self, value):
        _lcd_enable = self._LCDC.lcd_enable
        self._LCDC.set(value)

        if _lcd_enable and (not self._LCDC.lcd_enable):
            # https://www.reddit.com/r/Gameboy/comments/a1c8h0/what_happens_when_a_gameboy_screen_is_disabled/
            # 1. LY (current rendering line) resets to zero. A few games rely on this behavior, namely Mr. Do! When LY
            # is reset to zero, no LYC check is done, so no STAT interrupt happens either.
            # 2. The LCD clock is reset to zero as far as I can tell.
            # 3. I believe the LCD enters Mode 0.
            self.clock = 0
            self.clock_target = 0
            self._cycles_to_frame = 0
            self._STAT.set_mode(0)
            if self.LY < 144:
                logger.debug("LCD disabled outside of VBLANK!")
            self.LY = 0
        elif (not _lcd_enable) and self._LCDC.lcd_enable:  # When switching from disabled to enabled
            # Registers are actually supposed to be frozen when LCD is disabled. This is mimicked by reseting them again
            self.clock_target = 0  # This will trigger an immediate update in tick()

            # The Cycle Accurate Game Boy Docs:
            # the LCD won't show any image during the first frame it is turned on. The first drawn frame is the second one.
            self.first_frame = True  # used to postpose rendering of first frame

            # Will schedule a full reset on next call to LCD.tick. This will happen immediately, as CPU.tick returns
            # because of CPU.bail and MB.tick proceeds to call LCD.tick.
            self.reset = True

    def cycles_to_mode0(self):
        mode2 = 80
        mode3 = 170
        mode1 = 456

        mode = self._STAT._mode
        # Remaining cycles for this already active mode
        remainder = self.clock_target - self.clock

        mode &= 0b11
        if mode == 2:
            return remainder + mode3
        elif mode == 3:
            return remainder
        elif mode == 0:
            return 0
        elif mode == 1:
            remaining_ly = 153 - self.LY
            return remainder + mode1 * remaining_ly + mode2 + mode3
        # else:
        #     logger.critical("Unsupported STAT mode: %d", mode)
        #     return 0

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        interrupt_flag = 0
        self.clock += cycles >> self.speed_shift

        if self.clock >= self.clock_target:
            if self._LCDC.lcd_enable and (self.LY == 153 or self.reset):
                if self.reset:
                    # RESET
                    self.clock = 0
                    self.clock_target = 0
                    self._STAT.set_mode(0)  # Side-effects?
                    self.reset = False

                self.frame_done = True

                # Reset to new frame and start from mode 2
                self.LY = 0
                self.clock %= FRAME_CYCLES
                self.clock_target = 0
                self.next_stat_mode = 2

                # Change to next mode
                interrupt_flag |= self._STAT.set_mode(self.next_stat_mode)

                # self._STAT._mode == 2:  # Searching OAM
                self.clock_target += 80
                self.next_stat_mode = 3
                interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

            elif self._LCDC.lcd_enable:
                # Change to next mode
                interrupt_flag |= self._STAT.set_mode(self.next_stat_mode)

                # Pan Docs:
                # The following are typical when the display is enabled:
                #   Mode 2  2_____2_____2_____2_____2_____2___________________2____
                #   Mode 3  _33____33____33____33____33____33__________________3___
                #   Mode 0  ___000___000___000___000___000___000________________000
                #   Mode 1  ____________________________________11111111111111_____

                # LCD state machine
                if self._STAT._mode == 2:  # Searching OAM
                    self.LY += 1
                    self.clock_target += 80
                    self.next_stat_mode = 3
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                elif self._STAT._mode == 3:
                    self.clock_target += 170
                    self.next_stat_mode = 0
                elif self._STAT._mode == 0:  # HBLANK
                    self.clock_target += 206

                    # Recorded for API
                    bx, by = self.getviewport()
                    wx, wy = self.getwindowpos()
                    self._scanlineparameters[self.LY][0] = bx
                    self._scanlineparameters[self.LY][1] = by
                    self._scanlineparameters[self.LY][2] = wx + 7
                    self._scanlineparameters[self.LY][3] = wy
                    self._scanlineparameters[self.LY][4] = self._LCDC.tiledata_select

                    self.renderer.scanline(self, self.LY)
                    self.renderer.scanline_sprites(
                        self, self.LY, self.renderer._screenbuffer, self.renderer._screenbuffer_attributes, False
                    )
                    if self.LY < 143:
                        self.next_stat_mode = 2
                    else:
                        self.next_stat_mode = 1
                elif self._STAT._mode == 1:  # VBLANK
                    self.clock_target += 456
                    self.next_stat_mode = 1

                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

                    if self.LY == 144:
                        interrupt_flag |= INTR_VBLANK
                        if self.first_frame:
                            # Pan Docs: https://gbdev.io/pandocs/LCDC.html#lcdc7--lcd-enable
                            # When re-enabling the LCD, the PPU will immediately start drawing again, but the screen
                            # will stay blank during the first frame.
                            self.renderer.blank_screen(self)
                            self.first_frame = False
            else:
                # See also `self.set_lcdc`
                self.frame_done = True
                self.clock %= FRAME_CYCLES
                self.clock_target = FRAME_CYCLES

                # Renderer
                self.renderer.blank_screen(self)

        # NOTE: speed_shift because they are using in externally in mb
        self._cycles_to_interrupt = (self.clock_target - self.clock) << self.speed_shift
        # TODO: STAT Cycles to interrupts
        self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift
        return interrupt_flag

    def save_state(self, f):
        for n in range(VIDEO_RAM):
            f.write(self.VRAM0[n])

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            f.write(self.OAM[n])

        f.write(self._LCDC.value)  # TODO: Mode to class
        f.write(self.BGP.value)
        f.write(self.OBP0.value)
        f.write(self.OBP1.value)

        self._STAT.save_state(f)
        f.write(self.LY)
        f.write(self.LYC)

        f.write(self.SCY)
        f.write(self.SCX)
        f.write(self.WY)
        f.write(self.WX)

        for y in range(ROWS):
            f.write(self._scanlineparameters[y][0])
            f.write(self._scanlineparameters[y][1])
            # We store (WX + 7). We added 7 earlier to make it easier to serialize
            f.write(self._scanlineparameters[y][2])
            f.write(self._scanlineparameters[y][3])
            f.write(self._scanlineparameters[y][4])

        f.write(self.cgb)
        f.write(self.speed_shift)
        f.write(self.frame_done)
        f.write(self.first_frame)
        f.write(self.reset)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self.clock)
        f.write_64bit(self.clock_target)
        f.write(self.next_stat_mode)

        if self.cgb:
            for n in range(VIDEO_RAM):
                f.write(self.VRAM1[n])
            f.write(self.vbk.active_bank)
            self.bcps.save_state(f)
            self.bcpd.save_state(f)
            self.ocps.save_state(f)
            self.ocpd.save_state(f)

    def load_state(self, f, state_version):
        for n in range(VIDEO_RAM):
            self.VRAM0[n] = f.read()

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            self.OAM[n] = f.read()

        self.set_lcdc(f.read())  # TODO: Mode to class
        self.BGP.set(f.read())
        self.OBP0.set(f.read())
        self.OBP1.set(f.read())

        if state_version >= 5:
            self._STAT.load_state(f, state_version)
            self.LY = f.read()
            self.LYC = f.read()

        self.SCY = f.read()
        self.SCX = f.read()
        self.WY = f.read()
        self.WX = f.read()

        if state_version >= 11:
            for y in range(ROWS):
                self._scanlineparameters[y][0] = f.read()
                self._scanlineparameters[y][1] = f.read()
                # Restore (WX - 7) as described above
                self._scanlineparameters[y][2] = f.read()
                self._scanlineparameters[y][3] = f.read()
                if state_version > 3:
                    self._scanlineparameters[y][4] = f.read()

        if state_version >= 8:
            _cgb = f.read()
            if self.cgb and not _cgb:
                raise PyBoyException("Loading state which *is not* CGB-mode, but PyBoy *is* in CGB mode!")
            if not self.cgb and _cgb:
                raise PyBoyException("Loading state which *is* CGB-mode, but PyBoy *is not* in CGB mode!")
            self.cgb = _cgb
            self.speed_shift = f.read()
            if state_version >= 13:
                self.frame_done = f.read()
                self.first_frame = f.read()
                self.reset = f.read()

            if state_version >= 12:
                self.last_cycles = f.read_64bit()
            self.clock = f.read_64bit()
            self.clock_target = f.read_64bit()
            # NOTE: speed_shift because they are using in externally in mb
            self._cycles_to_interrupt = (self.clock_target - self.clock) << self.speed_shift
            self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift
            self.next_stat_mode = f.read()

            if self.cgb:
                for n in range(VIDEO_RAM):
                    self.VRAM1[n] = f.read()
                self.vbk.active_bank = f.read()
                self.bcps.load_state(f, state_version)
                self.bcpd.load_state(f, state_version)
                self.ocps.load_state(f, state_version)
                self.ocpd.load_state(f, state_version)

    def getwindowpos(self):
        return (self.WX - 7, self.WY)

    def getviewport(self):
        return (self.SCX, self.SCY)


class PaletteRegister:
    def __init__(self, value, palette):
        self.value = 0
        self.lookup = [0] * 4
        self.palette_mem_rgb = palette
        self.set(value)

    def set(self, value):
        # Pokemon Blue continuously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        for x in range(4):
            self.lookup[x] = self.palette_mem_rgb[(value >> x * 2) & 0b11]
        return True

    def get(self):
        return self.value

    def getcolor(self, i):
        return self.lookup[i]


class STATRegister:
    def __init__(self):
        self.value = 0b1000_0000
        self._mode = 0

    def set(self, value):
        value &= 0b0111_1000  # Bit 7 is always set, and bit 0-2 are read-only
        self.value &= 0b1000_0111  # Preserve read-only bits and clear the rest
        self.value |= value  # Combine the two

    def update_LYC(self, LYC, LY):
        if LYC == LY:
            self.value |= 0b100  # Sets the LYC flag
            if self.value & 0b0100_0000:  # LYC interrupt enabled flag
                return INTR_LCDC
        else:
            # Clear LYC flag
            self.value &= 0b1111_1011
        return 0

    def set_mode(self, mode):
        if self._mode == mode:
            # Mode already set
            return 0

        self._mode = mode
        self.value &= 0b11111100  # Clearing 2 LSB
        self.value |= mode  # Apply mode to LSB

        # Check if interrupt is enabled for this mode
        # Mode "3" is not interruptable
        if mode != 3 and self.value & (1 << (mode + 3)):
            return INTR_LCDC
        return 0

    def save_state(self, f):
        f.write(self.value)

    def load_state(self, f, state_version):
        value = f.read()
        self.value = value
        self._mode = value & 0b11


class LCDCRegister:
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is true.
        # fmt: off
        self.lcd_enable           = value & (1 << 7)
        self.windowmap_select     = value & (1 << 6)
        self.window_enable        = value & (1 << 5)
        self.tiledata_select      = value & (1 << 4)
        self.backgroundmap_select = value & (1 << 3)
        self.sprite_height        = value & (1 << 2)
        self.sprite_enable        = value & (1 << 1)
        self.background_enable    = value & (1 << 0)
        self.cgb_master_priority  = self.background_enable # Different meaning on CGB
        # fmt: on

        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        self.backgroundmap_offset = 0x1800 if self.backgroundmap_select == 0 else 0x1C00
        self.windowmap_offset = 0x1800 if self.windowmap_select == 0 else 0x1C00


COL0_FLAG = 0b01
BG_PRIORITY_FLAG = 0b10


class Renderer:
    def __init__(self, cgb):
        self.cgb = cgb
        self.color_format = "RGBA"

        self.buffer_dims = (ROWS, COLS)

        # Init buffers as white
        self._screenbuffer_raw = array("B", [0x00] * (ROWS * COLS * 4))
        self._screenbuffer_attributes_raw = array("B", [0x00] * (ROWS * COLS))
        self._tilecache0_raw = array("B", [0x00] * (TILES * 8 * 8))
        self._spritecache0_raw = array("B", [0x00] * (TILES * 8 * 8))
        self._spritecache1_raw = array("B", [0x00] * (TILES * 8 * 8))
        self.sprites_to_render = array("i", [0] * 10)

        self._tilecache0_state = array("B", [0] * TILES)
        self._spritecache0_state = array("B", [0] * TILES)
        self._spritecache1_state = array("B", [0] * TILES)
        self.clear_cache()

        self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
        self._screenbuffer_attributes = memoryview(self._screenbuffer_attributes_raw).cast("B", shape=(ROWS, COLS))
        self._tilecache0 = memoryview(self._tilecache0_raw).cast("B", shape=(TILES * 8, 8))
        self._tilecache0_64 = memoryview(self._tilecache0_raw).cast("Q", shape=(TILES * 8,))

        # The look-up table only stored 4 bits from each byte, packed into a single byte
        self.colorcode_table = array("I", [0x00000000] * (0x100))  # Should be "L"!?
        """Convert 2 bytes into color code at a given offset.

        The colors are 2 bit and are found like this:

        Color of the first pixel is 0b10
        | Color of the second pixel is 0b01
        v v
        1 0 0 1 0 0 0 1 <- byte1
        0 1 1 1 1 1 0 0 <- byte2
        """
        for byte in range(0x100):
            byte1 = byte & 0xF
            byte2 = (byte >> 4) & 0xF
            v = 0
            for offset in range(4):
                t = (((byte2 >> (offset)) & 0b1) << 1) | ((byte1 >> (offset)) & 0b1)
                assert t < 4
                v |= t << (8 * (3 - offset))  # Store them in little-endian
            self.colorcode_table[byte] = v

        # OBP0 palette
        self._spritecache0 = memoryview(self._spritecache0_raw).cast("B", shape=(TILES * 8, 8))
        self._spritecache0_64 = memoryview(self._spritecache0_raw).cast("Q", shape=(TILES * 8,))
        # OBP1 palette
        self._spritecache1 = memoryview(self._spritecache1_raw).cast("B", shape=(TILES * 8, 8))
        self._spritecache1_64 = memoryview(self._spritecache1_raw).cast("Q", shape=(TILES * 8,))

        self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        self.ly_window = 0

    def scanline(self, lcd, y):
        if lcd.disable_renderer:
            return

        bx, by = lcd.getviewport()
        wx, wy = lcd.getwindowpos()

        x = 0
        if lcd._LCDC.window_enable and wy <= y and wx < COLS:
            # Window has it's own internal line counter. It's only incremented whenever the window is drawing something on the screen.
            self.ly_window += 1

            # Before window
            if wx > x:
                x += self.scanline_background(y, x, bx, by, wx, lcd)

            # Window hit
            self.scanline_window(y, x, wx, wy, COLS - x, lcd)
        elif lcd._LCDC.background_enable:
            # No window
            self.scanline_background(y, x, bx, by, COLS, lcd)
        else:
            self.scanline_blank(y, x, COLS, lcd)

        if y == 143:
            # Reset at the end of a frame. We set it to -1, so it will be 0 after the first increment
            self.ly_window = -1

    def _get_tile(self, y, x, offset, lcd):
        tile_addr = offset + y // 8 * 32 % 0x400 + x // 8 % 32
        tile = lcd.VRAM0[tile_addr]

        # If using signed tile indices, modify index
        if not lcd._LCDC.tiledata_select:
            # (x ^ 0x80 - 128) to convert to signed, then
            # add 256 for offset (reduces to + 128)
            tile = (tile ^ 0x80) + 128

        yy = 8 * tile + y % 8
        return tile, yy, tile_addr

    def _pixel(self, tilecache, pixel, x, y, xx, yy, bg_priority_apply):
        col0 = (tilecache[yy, xx] == 0) & 1
        self._screenbuffer[y, x] = pixel
        # COL0_FLAG is 1
        self._screenbuffer_attributes[y, x] = bg_priority_apply | col0

    def scanline_window(self, y, _x, wx, wy, cols, lcd):
        for x in range(_x, _x + cols):
            xx = (x - wx) % 8
            if xx == 0 or x == _x:
                wt, yy, _ = self._get_tile(self.ly_window, x - wx, lcd._LCDC.windowmap_offset, lcd)
                self.update_tilecache0(lcd, wt, 0)

            pixel = lcd.BGP.getcolor(self._tilecache0[yy, xx])
            self._pixel(self._tilecache0, pixel, x, y, xx, yy, 0)
        return cols

    def scanline_background(self, y, _x, bx, by, cols, lcd):
        for x in range(_x, _x + cols):
            # bx mask used for the half tile at the left side when scrolling
            b_xx = (x + (bx & 0b111)) % 8
            if b_xx == 0 or x == 0:
                bt, b_yy, _ = self._get_tile(y + by, x + bx, lcd._LCDC.backgroundmap_offset, lcd)
                self.update_tilecache0(lcd, bt, 0)

            xx = b_xx
            yy = b_yy

            pixel = lcd.BGP.getcolor(self._tilecache0[yy, xx])
            self._pixel(self._tilecache0, pixel, x, y, xx, yy, 0)
        return cols

    def scanline_blank(self, y, _x, cols, lcd):
        # If background is disabled, it becomes white
        for x in range(_x, _x + cols):
            self._screenbuffer[y, x] = lcd.BGP.getcolor(0)
            self._screenbuffer_attributes[y, x] = 0
        return cols

    def sort_sprites(self, sprite_count):
        # Use insertion sort, as it has O(n) on already sorted arrays. This
        # functions is likely called multiple times with unchanged data.
        # Sort descending because of the sprite priority.

        for i in range(1, sprite_count):
            key = self.sprites_to_render[i]  # The current element to be inserted into the sorted portion
            j = i - 1  # Index of the last element in the sorted portion of the array

            # Move elements of the sorted portion greater than the key to the right
            while j >= 0 and key > self.sprites_to_render[j]:
                self.sprites_to_render[j + 1] = self.sprites_to_render[j]
                j -= 1

            # Insert the key into its correct position in the sorted portion
            self.sprites_to_render[j + 1] = key

    def scanline_sprites(self, lcd, ly, buffer, buffer_attributes, ignore_priority):
        if not lcd._LCDC.sprite_enable or lcd.disable_renderer:
            return

        # Find the first 10 sprites in OAM that appears on this scanline.
        # The lowest X-coordinate has priority, when overlapping
        spriteheight = 16 if lcd._LCDC.sprite_height else 8
        sprite_count = 0
        for n in range(0x00, OBJECT_ATTRIBUTE_MEMORY, 4):
            y = lcd.OAM[n] - 16  # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8  # Documentation states the x coordinate needs to be subtracted by 8

            if y <= ly < y + spriteheight:
                # x is used for sorting for priority
                if self.cgb:
                    self.sprites_to_render[sprite_count] = n
                else:
                    self.sprites_to_render[sprite_count] = x << 16 | n
                sprite_count += 1

            if sprite_count == 10:
                break

        # Pan docs:
        # When these 10 sprites overlap, the highest priority one will appear above all others, etc. (Thus, no
        # Z-fighting.) In CGB mode, the first sprite in OAM ($FE00-$FE03) has the highest priority, and so on. In
        # Non-CGB mode, the smaller the X coordinate, the higher the priority. The tie breaker (same X coordinates) is
        # the same priority as in CGB mode.
        self.sort_sprites(sprite_count)

        for _n in self.sprites_to_render[:sprite_count]:
            if self.cgb:
                n = _n
            else:
                n = _n & 0xFF
            # n = self.sprites_to_render_n[_n]
            y = lcd.OAM[n] - 16  # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8  # Documentation states the x coordinate needs to be subtracted by 8
            tileindex = lcd.OAM[n + 2]
            if spriteheight == 16:
                tileindex &= 0b11111110
            attributes = lcd.OAM[n + 3]
            xflip = attributes & 0b00100000
            yflip = attributes & 0b01000000
            spritepriority = (attributes & 0b10000000) and not ignore_priority
            if self.cgb:
                palette = attributes & 0b111
                if attributes & 0b1000:
                    self.update_spritecache1(lcd, tileindex, 1)
                    if lcd._LCDC.sprite_height:
                        self.update_spritecache1(lcd, tileindex + 1, 1)
                    spritecache = self._spritecache1
                else:
                    self.update_spritecache0(lcd, tileindex, 0)
                    if lcd._LCDC.sprite_height:
                        self.update_spritecache0(lcd, tileindex + 1, 0)
                    spritecache = self._spritecache0
            else:
                # Fake palette index
                palette = 0
                if attributes & 0b10000:
                    self.update_spritecache1(lcd, tileindex, 0)
                    if lcd._LCDC.sprite_height:
                        self.update_spritecache1(lcd, tileindex + 1, 0)
                    spritecache = self._spritecache1
                else:
                    self.update_spritecache0(lcd, tileindex, 0)
                    if lcd._LCDC.sprite_height:
                        self.update_spritecache0(lcd, tileindex + 1, 0)
                    spritecache = self._spritecache0

            dy = ly - y
            yy = spriteheight - dy - 1 if yflip else dy

            for dx in range(8):
                xx = 7 - dx if xflip else dx
                color_code = spritecache[8 * tileindex + yy, xx]
                if 0 <= x < COLS and not color_code == 0:  # If pixel is not transparent
                    if self.cgb:
                        pixel = lcd.ocpd.getcolor(palette, color_code)
                        bgmappriority = buffer_attributes[ly, x] & BG_PRIORITY_FLAG

                        if lcd._LCDC.cgb_master_priority:  # If 0, sprites are always on top, if 1 follow priorities
                            if bgmappriority:  # If 0, use spritepriority, if 1 take priority
                                if buffer_attributes[ly, x] & COL0_FLAG:
                                    buffer[ly, x] = pixel
                            elif (
                                spritepriority
                            ):  # If 1, sprite is behind bg/window. Color 0 of window/bg is transparent
                                if buffer_attributes[ly, x] & COL0_FLAG:
                                    buffer[ly, x] = pixel
                            else:
                                buffer[ly, x] = pixel
                        else:
                            buffer[ly, x] = pixel
                    else:
                        # TODO: Unify with CGB
                        if attributes & 0b10000:
                            pixel = lcd.OBP1.getcolor(color_code)
                        else:
                            pixel = lcd.OBP0.getcolor(color_code)

                        if spritepriority:  # If 1, sprite is behind bg/window. Color 0 of window/bg is transparent
                            if buffer_attributes[ly, x] & COL0_FLAG:  # if BG pixel is transparent
                                buffer[ly, x] = pixel
                        else:
                            buffer[ly, x] = pixel
                x += 1
            x -= 8

    def clear_cache(self):
        self.clear_tilecache0()
        self.clear_spritecache0()
        self.clear_spritecache1()

    def invalidate_tile(self, tile, vbank):
        if vbank and self.cgb:
            self._tilecache0_state[tile] = 0
            self._tilecache1_state[tile] = 0
            self._spritecache0_state[tile] = 0
            self._spritecache1_state[tile] = 0
        else:
            self._tilecache0_state[tile] = 0
            if self.cgb:
                self._tilecache1_state[tile] = 0
            self._spritecache0_state[tile] = 0
            self._spritecache1_state[tile] = 0

    def clear_tilecache0(self):
        for i in range(TILES):
            self._tilecache0_state[i] = 0

    def clear_tilecache1(self):
        pass

    def clear_spritecache0(self):
        for i in range(TILES):
            self._spritecache0_state[i] = 0

    def clear_spritecache1(self):
        for i in range(TILES):
            self._spritecache1_state[i] = 0

    def update_tilecache0(self, lcd, t, bank):
        if self._tilecache0_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = lcd.VRAM0[t * 16 + k]
            byte2 = lcd.VRAM0[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._tilecache0_64[y] = self.colorcode(byte1, byte2)

        self._tilecache0_state[t] = 1

    def update_tilecache1(self, lcd, t, bank):
        pass

    def update_spritecache0(self, lcd, t, bank):
        if self._spritecache0_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = lcd.VRAM0[t * 16 + k]
            byte2 = lcd.VRAM0[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._spritecache0_64[y] = self.colorcode(byte1, byte2)

        self._spritecache0_state[t] = 1

    def update_spritecache1(self, lcd, t, bank):
        if self._spritecache1_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = lcd.VRAM0[t * 16 + k]
            byte2 = lcd.VRAM0[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._spritecache1_64[y] = self.colorcode(byte1, byte2)

        self._spritecache1_state[t] = 1

    def colorcode(self, byte1, byte2):
        colorcode_low = self.colorcode_table[(byte1 & 0xF) | ((byte2 & 0xF) << 4)]
        colorcode_high = self.colorcode_table[((byte1 >> 4) & 0xF) | (byte2 & 0xF0)]
        return (colorcode_low << 32) | colorcode_high

    def blank_screen(self, lcd):
        # If the screen is off, fill it with a color.
        for y in range(ROWS):
            for x in range(COLS):
                self._screenbuffer[y, x] = lcd.BGP.getcolor(0)
                self._screenbuffer_attributes[y, x] = 0

    def save_state(self, f):
        for y in range(ROWS):
            for x in range(COLS):
                f.write_32bit(self._screenbuffer[y, x])
                f.write(self._screenbuffer_attributes[y, x])

    def load_state(self, f, state_version):
        if 2 <= state_version < 11:
            # Dummy reads to align scanline parameters. See LCD instead
            for y in range(ROWS):
                f.read()
                f.read()
                f.read()
                f.read()
                if state_version > 3:
                    f.read()

        if state_version >= 6:
            for y in range(ROWS):
                for x in range(COLS):
                    self._screenbuffer[y, x] = f.read_32bit()
                    if state_version >= 10:
                        self._screenbuffer_attributes[y, x] = f.read()

        self.clear_cache()


####################################
#
#  ██████   ██████   ██████
# ██       ██        ██   ██
# ██       ██   ███  ██████
# ██       ██    ██  ██   ██
#  ██████   ██████   ██████
#


class CGBLCD(LCD):
    def __init__(self, cgb, cartridge_cgb, color_palette, cgb_color_palette, randomize=False):
        LCD.__init__(self, cgb, cartridge_cgb, color_palette, cgb_color_palette, randomize=False)
        self.VRAM1 = array("B", [0] * VIDEO_RAM)

        self.vbk = VBKregister()
        self.bcps = PaletteIndexRegister()
        self.bcpd = PaletteColorRegister(self.bcps)
        self.ocps = PaletteIndexRegister()
        self.ocpd = PaletteColorRegister(self.ocps)


class CGBRenderer(Renderer):
    def __init__(self):
        self._tilecache1_state = array("B", [0] * TILES)
        Renderer.__init__(self, True)

        self._tilecache1_raw = array("B", [0xFF] * (TILES * 8 * 8))

        self._tilecache1 = memoryview(self._tilecache1_raw).cast("B", shape=(TILES * 8, 8))
        self._tilecache1_64 = memoryview(self._tilecache1_raw).cast("Q", shape=(TILES * 8,))
        self._tilecache1_state = array("B", [0] * TILES)
        self.clear_cache()

    def _cgb_get_background_map_attributes(self, lcd, i):
        tile_num = lcd.VRAM1[i]
        palette = tile_num & 0b111
        vbank = (tile_num >> 3) & 1
        horiflip = (tile_num >> 5) & 1
        vertflip = (tile_num >> 6) & 1
        bg_priority = (tile_num >> 7) & 1

        return palette, vbank, horiflip, vertflip, bg_priority

    def _get_tile_cgb(self, y, x, offset, lcd):
        tile, yy, tile_addr = self._get_tile(y, x, offset, lcd)

        palette, vbank, horiflip, vertflip, bg_priority = self._cgb_get_background_map_attributes(lcd, tile_addr)

        bg_priority_apply = 0
        if bg_priority:
            # We hide extra rendering information in the lower 8 bits (A) of the 32-bit RGBA format
            bg_priority_apply = BG_PRIORITY_FLAG

        if vertflip:
            yy = 8 * tile + (7 - (y) % 8)

        return tile, yy, palette, horiflip, bg_priority_apply, vbank

    def scanline_window(self, y, _x, wx, wy, cols, lcd):
        bg_priority_apply = 0
        for x in range(_x, _x + cols):
            xx = (x - wx) % 8
            if xx == 0 or x == _x:
                wt, yy, w_palette, w_horiflip, bg_priority_apply, vbank = self._get_tile_cgb(
                    self.ly_window, x - wx, lcd._LCDC.windowmap_offset, lcd
                )
                # NOTE: Not allowed to return memoryview in Cython tuple
                if vbank:
                    self.update_tilecache1(lcd, wt, vbank)
                    tilecache = self._tilecache1
                else:
                    self.update_tilecache0(lcd, wt, vbank)
                    tilecache = self._tilecache0

            if w_horiflip:
                xx = 7 - xx

            pixel = lcd.bcpd.getcolor(w_palette, tilecache[yy, xx])
            self._pixel(tilecache, pixel, x, y, xx, yy, bg_priority_apply)
        return cols

    def scanline_background(self, y, _x, bx, by, cols, lcd):
        for x in range(_x, _x + cols):
            # bx mask used for the half tile at the left side when scrolling
            xx = (x + (bx & 0b111)) % 8
            if xx == 0 or x == 0:
                bt, yy, b_palette, b_horiflip, bg_priority_apply, vbank = self._get_tile_cgb(
                    y + by, x + bx, lcd._LCDC.backgroundmap_offset, lcd
                )
                # NOTE: Not allowed to return memoryview in Cython tuple
                if vbank:
                    self.update_tilecache1(lcd, bt, vbank)
                    tilecache = self._tilecache1
                else:
                    self.update_tilecache0(lcd, bt, vbank)
                    tilecache = self._tilecache0

            if b_horiflip:
                xx = 7 - xx

            pixel = lcd.bcpd.getcolor(b_palette, tilecache[yy, xx])
            self._pixel(tilecache, pixel, x, y, xx, yy, bg_priority_apply)
        return cols

    def scanline(self, lcd, y):
        if lcd.disable_renderer:
            return

        bx, by = lcd.getviewport()
        wx, wy = lcd.getwindowpos()

        x = 0

        if lcd._LCDC.window_enable and wy <= y and wx < COLS:
            # Window has it's own internal line counter. It's only incremented whenever the window is drawing something on the screen.
            self.ly_window += 1

            # Before window
            if wx > x:
                x += self.scanline_background(y, x, bx, by, wx, lcd)

            # Window hit
            self.scanline_window(y, x, wx, wy, COLS - x, lcd)
        else:  # background_enable doesn't exist for CGB. It works as master priority instead
            # No window
            self.scanline_background(y, x, bx, by, COLS, lcd)

        if y == 143:
            # Reset at the end of a frame. We set it to -1, so it will be 0 after the first increment
            self.ly_window = -1

    def clear_cache(self):
        self.clear_tilecache0()
        self.clear_tilecache1()
        self.clear_spritecache0()
        self.clear_spritecache1()

    def clear_tilecache1(self):
        for i in range(TILES):
            self._tilecache1_state[i] = 0

    def update_tilecache0(self, lcd, t, bank):
        if self._tilecache0_state[t]:
            return

        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0

        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = vram_bank[t * 16 + k]
            byte2 = vram_bank[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._tilecache0_64[y] = self.colorcode(byte1, byte2)

        self._tilecache0_state[t] = 1

    def update_tilecache1(self, lcd, t, bank):
        if self._tilecache1_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = vram_bank[t * 16 + k]
            byte2 = vram_bank[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._tilecache1_64[y] = self.colorcode(byte1, byte2)

        self._tilecache1_state[t] = 1

    def update_spritecache0(self, lcd, t, bank):
        if self._spritecache0_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = vram_bank[t * 16 + k]
            byte2 = vram_bank[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._spritecache0_64[y] = self.colorcode(byte1, byte2)

        self._spritecache0_state[t] = 1

    def update_spritecache1(self, lcd, t, bank):
        if self._spritecache1_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            byte1 = vram_bank[t * 16 + k]
            byte2 = vram_bank[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._spritecache1_64[y] = self.colorcode(byte1, byte2)

        self._spritecache1_state[t] = 1


class VBKregister:
    def __init__(self, value=0):
        self.active_bank = value

    def set(self, value):
        # when writing to VBK, bit 0 indicates which bank to switch to
        bank = value & 1
        self.active_bank = bank

    def get(self):
        # reading from this register returns current VRAM bank in bit 0, other bits = 1
        return self.active_bank | 0xFE


class PaletteIndexRegister:
    def __init__(self, val=0):
        self.value = val
        self.auto_inc = 0
        self.index = 0
        self.hl = 0

    def set(self, val):
        if self.value == val:
            return
        self.value = val
        self.hl = val & 0b1
        self.index = (val >> 1) & 0b11111
        self.auto_inc = (val >> 7) & 0b1

    def get(self):
        return self.value

    def getindex(self):
        return self.index

    def shouldincrement(self):
        if self.auto_inc:
            # ensure autoinc also set for new val
            new_val = 0x80 | (self.value + 1)
            self.set(new_val)

    def save_state(self, f):
        f.write(self.value)
        f.write(self.auto_inc)
        f.write(self.index)
        f.write(self.hl)

    def load_state(self, f, state_version):
        self.value = f.read()
        self.auto_inc = f.read()
        self.index = f.read()
        self.hl = f.read()


CGB_NUM_PALETTES = 8


class PaletteColorRegister:
    def __init__(self, i_reg):
        # 8 palettes of 4 colors each 2 bytes
        self.palette_mem = array("I", [0xFFFF] * CGB_NUM_PALETTES * 4)
        self.palette_mem_rgb = array("L", [0] * CGB_NUM_PALETTES * 4)
        self.index_reg = i_reg

        # Init with some colors -- TODO: What are real defaults?
        for n in range(0, len(self.palette_mem), 4):
            c = [0x1CE7, 0x1E19, 0x7E31, 0x217B]
            for m in range(4):
                self.palette_mem[n + m] = c[m]
                self.palette_mem_rgb[n + m] = self.cgb_to_rgb(c[m], m)

    def cgb_to_rgb(self, cgb_color, index):
        alpha = 0xFF
        red = (cgb_color & 0x1F) << 3
        green = ((cgb_color >> 5) & 0x1F) << 3
        blue = ((cgb_color >> 10) & 0x1F) << 3
        # NOTE: Actually BGR, not RGB
        rgb_color = (alpha << 24) | (blue << 16) | (green << 8) | red
        return rgb_color

    def set(self, val):
        i_val = self.palette_mem[self.index_reg.getindex()]
        if self.index_reg.hl:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0x00FF) | (val << 8)
        else:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0xFF00) | val

        cgb_color = self.palette_mem[self.index_reg.getindex()] & 0x7FFF
        self.palette_mem_rgb[self.index_reg.getindex()] = self.cgb_to_rgb(cgb_color, self.index_reg.getindex())

        # check for autoincrement after write
        self.index_reg.shouldincrement()

    def get(self):
        if self.index_reg.hl:
            return (self.palette_mem[self.index_reg.getindex()] & 0xFF00) >> 8
        else:
            return self.palette_mem[self.index_reg.getindex()] & 0x00FF

    def getcolor(self, paletteindex, colorindex):
        # Each palette = 8 bytes or 4 colors of 2 bytes
        return self.palette_mem_rgb[paletteindex * 4 + colorindex]

    def save_state(self, f):
        for n in range(CGB_NUM_PALETTES * 4):
            f.write_16bit(self.palette_mem[n])

    def load_state(self, f, state_version):
        for n in range(CGB_NUM_PALETTES * 4):
            self.palette_mem[n] = f.read_16bit()
            self.palette_mem_rgb[n] = self.cgb_to_rgb(self.palette_mem[n], n % 4)
