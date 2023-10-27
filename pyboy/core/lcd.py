#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array
from copy import deepcopy
from ctypes import c_void_p
from random import getrandbits

import pyboy
from pyboy import utils

logger = pyboy.logging.get_logger(__name__)

VIDEO_RAM = 8 * 1024 # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0
INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
ROWS, COLS = 144, 160
TILES = 384

FRAME_CYCLES = 70224


class LCD:
    def __init__(self, cgb, cartridge_cgb, disable_renderer, color_palette, cgb_color_palette, randomize=False):
        self.VRAM0 = array("B", [0] * VIDEO_RAM)
        self.OAM = array("B", [0] * OBJECT_ATTRIBUTE_MEMORY)
        self.disable_renderer = disable_renderer

        if randomize:
            for i in range(VIDEO_RAM):
                self.VRAM0[i] = getrandbits(8)
            for i in range(OBJECT_ATTRIBUTE_MEMORY):
                self.OAM[i] = getrandbits(8)

        self._LCDC = LCDCRegister(0)
        self._STAT = STATRegister() # Bit 7 is always set.
        self.next_stat_mode = 2
        self.SCY = 0x00
        self.SCX = 0x00
        self.LY = 0x00
        self.LYC = 0x00
        # self.DMA = 0x00
        self.BGP = PaletteRegister(0xFC)
        self.OBP0 = PaletteRegister(0xFF)
        self.OBP1 = PaletteRegister(0xFF)
        self.WY = 0x00
        self.WX = 0x00
        self.clock = 0
        self.clock_target = 0
        self.frame_done = False
        self.double_speed = False
        self.cgb = cgb

        if self.cgb:
            if cartridge_cgb:
                logger.debug("Starting CGB renderer")
                self.renderer = CGBRenderer()
            else:
                logger.debug("Starting CGB renderer in DMG-mode")
                # Running DMG ROM on CGB hardware use the default palettes
                bg_pal, obj0_pal, obj1_pal = cgb_color_palette
                self.BGP.palette_mem_rgb = [(c << 8) for c in bg_pal]
                self.OBP0.palette_mem_rgb = [(c << 8) for c in obj0_pal]
                self.OBP1.palette_mem_rgb = [(c << 8) for c in obj1_pal]
                self.renderer = Renderer(False)
        else:
            logger.debug("Starting DMG renderer")
            self.BGP.palette_mem_rgb = [(c << 8) for c in color_palette]
            self.OBP0.palette_mem_rgb = [(c << 8) for c in color_palette]
            self.OBP1.palette_mem_rgb = [(c << 8) for c in color_palette]
            self.renderer = Renderer(False)

    def get_lcdc(self):
        return self._LCDC.value

    def set_lcdc(self, value):
        self._LCDC.set(value)

        if not self._LCDC.lcd_enable:
            # https://www.reddit.com/r/Gameboy/comments/a1c8h0/what_happens_when_a_gameboy_screen_is_disabled/
            # 1. LY (current rendering line) resets to zero. A few games rely on this behavior, namely Mr. Do! When LY
            # is reset to zero, no LYC check is done, so no STAT interrupt happens either.
            # 2. The LCD clock is reset to zero as far as I can tell.
            # 3. I believe the LCD enters Mode 0.
            self.clock = 0
            self.clock_target = FRAME_CYCLES # Doesn't render anything for the first frame
            self._STAT.set_mode(0)
            self.next_stat_mode = 2
            self.LY = 0

    def get_stat(self):
        return self._STAT.value

    def set_stat(self, value):
        self._STAT.set(value)

    def cycles_to_interrupt(self):
        return self.clock_target - self.clock

    def cycles_to_mode0(self):
        multiplier = 2 if self.double_speed else 1
        mode2 = 80 * multiplier
        mode3 = 170 * multiplier
        mode1 = 456 * multiplier

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
            return remainder + mode1*remaining_ly + mode2 + mode3
        # else:
        #     logger.critical("Unsupported STAT mode: %d", mode)
        #     return 0

    def tick(self, cycles):
        interrupt_flag = 0
        self.clock += cycles

        if self._LCDC.lcd_enable:
            if self.clock >= self.clock_target:
                # Change to next mode
                interrupt_flag |= self._STAT.set_mode(self.next_stat_mode)

                # Pan Docs:
                # The following are typical when the display is enabled:
                #   Mode 2  2_____2_____2_____2_____2_____2___________________2____
                #   Mode 3  _33____33____33____33____33____33__________________3___
                #   Mode 0  ___000___000___000___000___000___000________________000
                #   Mode 1  ____________________________________11111111111111_____
                multiplier = 2 if self.double_speed else 1

                # LCD state machine
                if self._STAT._mode == 2: # Searching OAM
                    if self.LY == 153:
                        self.LY = 0
                        self.clock %= FRAME_CYCLES
                        self.clock_target %= FRAME_CYCLES
                    else:
                        self.LY += 1

                    self.clock_target += 80 * multiplier
                    self.next_stat_mode = 3
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                elif self._STAT._mode == 3:
                    self.clock_target += 170 * multiplier
                    self.next_stat_mode = 0
                elif self._STAT._mode == 0: # HBLANK
                    self.clock_target += 206 * multiplier

                    self.renderer.scanline(self, self.LY)
                    self.renderer.scanline_sprites(self, self.LY, self.renderer._screenbuffer, False)
                    if self.LY < 143:
                        self.next_stat_mode = 2
                    else:
                        self.next_stat_mode = 1
                elif self._STAT._mode == 1: # VBLANK
                    self.clock_target += 456 * multiplier
                    self.next_stat_mode = 1

                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

                    if self.LY == 144:
                        interrupt_flag |= INTR_VBLANK
                        self.frame_done = True

                    if self.LY == 153:
                        # Reset to new frame and start from mode 2
                        self.next_stat_mode = 2
        else:
            # See also `self.set_lcdc`
            if self.clock >= FRAME_CYCLES:
                self.frame_done = True
                self.clock %= FRAME_CYCLES

                # Renderer
                self.renderer.blank_screen(self)

        return interrupt_flag

    def save_state(self, f):
        for n in range(VIDEO_RAM):
            f.write(self.VRAM0[n])

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            f.write(self.OAM[n])

        f.write(self._LCDC.value)
        f.write(self.BGP.value)
        f.write(self.OBP0.value)
        f.write(self.OBP1.value)

        f.write(self._STAT.value)
        f.write(self.LY)
        f.write(self.LYC)

        f.write(self.SCY)
        f.write(self.SCX)
        f.write(self.WY)
        f.write(self.WX)

        # CGB
        f.write(self.cgb)
        f.write(self.double_speed)
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

        self.set_lcdc(f.read())
        self.BGP.set(f.read())
        self.OBP0.set(f.read())
        self.OBP1.set(f.read())

        if state_version >= 5:
            self.set_stat(f.read())
            self.LY = f.read()
            self.LYC = f.read()

        self.SCY = f.read()
        self.SCX = f.read()
        self.WY = f.read()
        self.WX = f.read()

        # CGB
        if state_version >= 8:
            _cgb = f.read()
            if self.cgb != _cgb:
                logger.critical("Loading state which is not CGB, but PyBoy is loaded in CGB mode!")
                return
            self.cgb = _cgb
            self.double_speed = f.read()

            self.clock = f.read_64bit()
            self.clock_target = f.read_64bit()
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
    def __init__(self, value):
        self.value = 0
        self.lookup = [0] * 4
        self.set(value)
        self.palette_mem_rgb = [0] * 4

    def set(self, value):
        # Pokemon Blue continuously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        for x in range(4):
            self.lookup[x] = (value >> x * 2) & 0b11
        return True

    def get(self):
        return self.value

    def getcolor(self, i):
        if i==0:
            return self.palette_mem_rgb[self.lookup[0]] | COL0_FLAG
        else:
            return self.palette_mem_rgb[self.lookup[i]]


class STATRegister:
    def __init__(self):
        self.value = 0b1000_0000
        self._mode = 0

    def set(self, value):
        value &= 0b0111_1000 # Bit 7 is always set, and bit 0-2 are read-only
        self.value &= 0b1000_0111 # Preserve read-only bits and clear the rest
        self.value |= value # Combine the two

    def update_LYC(self, LYC, LY):
        if LYC == LY:
            self.value |= 0b100 # Sets the LYC flag
            if self.value & 0b0100_0000: # LYC interrupt enabled flag
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
        self.value &= 0b11111100 # Clearing 2 LSB
        self.value |= mode # Apply mode to LSB

        # Check if interrupt is enabled for this mode
        # Mode "3" is not interruptable
        if mode != 3 and self.value & (1 << (mode + 3)):
            return INTR_LCDC
        return 0


class LCDCRegister:
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is true.
        # yapf: disable
        self.lcd_enable           = value & (1 << 7)
        self.windowmap_select     = value & (1 << 6)
        self.window_enable        = value & (1 << 5)
        self.tiledata_select      = value & (1 << 4)
        self.backgroundmap_select = value & (1 << 3)
        self.sprite_height        = value & (1 << 2)
        self.sprite_enable        = value & (1 << 1)
        self.background_enable    = value & (1 << 0)
        self.cgb_master_priority  = self.background_enable # Different meaning on CGB
        # yapf: enable


COL0_FLAG = 0b01
BG_PRIORITY_FLAG = 0b10


class Renderer:
    def __init__(self, cgb):
        self.cgb = cgb
        self.color_format = "RGBA"

        self.buffer_dims = (ROWS, COLS)

        # self.clearcache = False
        # self.tiles_changed0 = set([])

        # Init buffers as white
        self._screenbuffer_raw = array("B", [0x00] * (ROWS*COLS*4))
        self._tilecache0_raw = array("B", [0x00] * (TILES*8*8*4))
        self._spritecache0_raw = array("B", [0x00] * (TILES*8*8*4))
        self._spritecache1_raw = array("B", [0x00] * (TILES*8*8*4))
        self.sprites_to_render = array("i", [0] * 10)

        self._tilecache0_state = array("B", [0] * TILES)
        self._spritecache0_state = array("B", [0] * TILES)
        self._spritecache1_state = array("B", [0] * TILES)
        self.clear_cache()

        self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
        self._tilecache0 = memoryview(self._tilecache0_raw).cast("I", shape=(TILES * 8, 8))
        # OBP0 palette
        self._spritecache0 = memoryview(self._spritecache0_raw).cast("I", shape=(TILES * 8, 8))
        # OBP1 palette
        self._spritecache1 = memoryview(self._spritecache1_raw).cast("I", shape=(TILES * 8, 8))
        self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        self._scanlineparameters = [[0, 0, 0, 0, 0] for _ in range(ROWS)]
        self.ly_window = 0

    def _cgb_get_background_map_attributes(self, lcd, i):
        tile_num = lcd.VRAM1[i]
        palette = tile_num & 0b111
        vbank = (tile_num >> 3) & 1
        horiflip = (tile_num >> 5) & 1
        vertflip = (tile_num >> 6) & 1
        bg_priority = (tile_num >> 7) & 1

        return palette, vbank, horiflip, vertflip, bg_priority

    def scanline(self, lcd, y):
        bx, by = lcd.getviewport()
        wx, wy = lcd.getwindowpos()
        # TODO: Move to lcd class
        self._scanlineparameters[y][0] = bx
        self._scanlineparameters[y][1] = by
        self._scanlineparameters[y][2] = wx
        self._scanlineparameters[y][3] = wy
        self._scanlineparameters[y][4] = lcd._LCDC.tiledata_select

        if lcd.disable_renderer:
            return

        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        background_offset = 0x1800 if lcd._LCDC.backgroundmap_select == 0 else 0x1C00
        wmap = 0x1800 if lcd._LCDC.windowmap_select == 0 else 0x1C00

        # Used for the half tile at the left side when scrolling
        offset = bx & 0b111

        # Weird behavior, where the window has it's own internal line counter. It's only incremented whenever the
        # window is drawing something on the screen.
        if lcd._LCDC.window_enable and wy <= y and wx < COLS:
            self.ly_window += 1

        for x in range(COLS):
            if lcd._LCDC.window_enable and wy <= y and wx <= x:
                tile_addr = wmap + (self.ly_window) // 8 * 32 % 0x400 + (x-wx) // 8 % 32
                wt = lcd.VRAM0[tile_addr]
                # If using signed tile indices, modify index
                if not lcd._LCDC.tiledata_select:
                    # (x ^ 0x80 - 128) to convert to signed, then
                    # add 256 for offset (reduces to + 128)
                    wt = (wt ^ 0x80) + 128

                bg_priority_apply = 0x00
                if self.cgb:
                    palette, vbank, horiflip, vertflip, bg_priority = self._cgb_get_background_map_attributes(
                        lcd, tile_addr
                    )
                    if vbank:
                        self.update_tilecache1(lcd, wt, vbank)
                        tilecache = self._tilecache1
                    else:
                        self.update_tilecache0(lcd, wt, vbank)
                        tilecache = self._tilecache0

                    xx = (7 - ((x-wx) % 8)) if horiflip else ((x-wx) % 8)
                    yy = (8*wt + (7 - (self.ly_window) % 8)) if vertflip else (8*wt + (self.ly_window) % 8)

                    pixel = lcd.bcpd.getcolor(palette, tilecache[yy, xx])
                    if bg_priority:
                        # We hide extra rendering information in the lower 8 bits (A) of the 32-bit RGBA format
                        bg_priority_apply = BG_PRIORITY_FLAG
                else:
                    self.update_tilecache0(lcd, wt, 0)
                    xx = (x-wx) % 8
                    yy = 8*wt + (self.ly_window) % 8
                    pixel = lcd.BGP.getcolor(self._tilecache0[yy, xx])

                self._screenbuffer[y, x] = pixel | bg_priority_apply
            # background_enable doesn't exist for CGB. It works as master priority instead
            elif (not self.cgb and lcd._LCDC.background_enable) or self.cgb:
                tile_addr = background_offset + (y+by) // 8 * 32 % 0x400 + (x+bx) // 8 % 32
                bt = lcd.VRAM0[tile_addr]
                # If using signed tile indices, modify index
                if not lcd._LCDC.tiledata_select:
                    # (x ^ 0x80 - 128) to convert to signed, then
                    # add 256 for offset (reduces to + 128)
                    bt = (bt ^ 0x80) + 128

                bg_priority_apply = 0x00
                if self.cgb:
                    palette, vbank, horiflip, vertflip, bg_priority = self._cgb_get_background_map_attributes(
                        lcd, tile_addr
                    )

                    if vbank:
                        self.update_tilecache1(lcd, bt, vbank)
                        tilecache = self._tilecache1
                    else:
                        self.update_tilecache0(lcd, bt, vbank)
                        tilecache = self._tilecache0
                    xx = (7 - ((x+offset) % 8)) if horiflip else ((x+offset) % 8)
                    yy = (8*bt + (7 - (y+by) % 8)) if vertflip else (8*bt + (y+by) % 8)

                    pixel = lcd.bcpd.getcolor(palette, tilecache[yy, xx])
                    if bg_priority:
                        # We hide extra rendering information in the lower 8 bits (A) of the 32-bit RGBA format
                        bg_priority_apply = BG_PRIORITY_FLAG
                else:
                    self.update_tilecache0(lcd, bt, 0)
                    xx = (x+offset) % 8
                    yy = 8*bt + (y+by) % 8
                    pixel = lcd.BGP.getcolor(self._tilecache0[yy, xx])

                self._screenbuffer[y, x] = pixel | bg_priority_apply
            else:
                # If background is disabled, it becomes white
                self._screenbuffer[y, x] = lcd.BGP.getcolor(0)

        if y == 143:
            # Reset at the end of a frame. We set it to -1, so it will be 0 after the first increment
            self.ly_window = -1

    def sort_sprites(self, sprite_count):
        # Use insertion sort, as it has O(n) on already sorted arrays. This
        # functions is likely called multiple times with unchanged data.
        # Sort descending because of the sprite priority.

        for i in range(1, sprite_count):
            key = self.sprites_to_render[i] # The current element to be inserted into the sorted portion
            j = i - 1 # Index of the last element in the sorted portion of the array

            # Move elements of the sorted portion greater than the key to the right
            while j >= 0 and key > self.sprites_to_render[j]:
                self.sprites_to_render[j + 1] = self.sprites_to_render[j]
                j -= 1

            # Insert the key into its correct position in the sorted portion
            self.sprites_to_render[j + 1] = key

    def scanline_sprites(self, lcd, ly, buffer, ignore_priority):
        if not lcd._LCDC.sprite_enable or lcd.disable_renderer:
            return

        # Find the first 10 sprites in OAM that appears on this scanline.
        # The lowest X-coordinate has priority, when overlapping
        spriteheight = 16 if lcd._LCDC.sprite_height else 8
        sprite_count = 0
        for n in range(0x00, 0xA0, 4):
            y = lcd.OAM[n] - 16 # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8 # Documentation states the x coordinate needs to be subtracted by 8

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
            y = lcd.OAM[n] - 16 # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8 # Documentation states the x coordinate needs to be subtracted by 8
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
                color_code = spritecache[8*tileindex + yy, xx]
                if 0 <= x < COLS and not color_code == 0: # If pixel is not transparent
                    if self.cgb:
                        pixel = lcd.ocpd.getcolor(palette, color_code)
                        bgmappriority = buffer[ly, x] & BG_PRIORITY_FLAG

                        if lcd._LCDC.cgb_master_priority: # If 0, sprites are always on top, if 1 follow priorities
                            if bgmappriority: # If 0, use spritepriority, if 1 take priority
                                if buffer[ly, x] & COL0_FLAG:
                                    buffer[ly, x] = pixel
                            elif spritepriority: # If 1, sprite is behind bg/window. Color 0 of window/bg is transparent
                                if buffer[ly, x] & COL0_FLAG:
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

                        if spritepriority: # If 1, sprite is behind bg/window. Color 0 of window/bg is transparent
                            if buffer[ly, x] & COL0_FLAG: # if BG pixel is transparent
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

    def color_code(self, byte1, byte2, offset):
        """Convert 2 bytes into color code at a given offset.

        The colors are 2 bit and are found like this:

        Color of the first pixel is 0b10
        | Color of the second pixel is 0b01
        v v
        1 0 0 1 0 0 0 1 <- byte1
        0 1 1 1 1 1 0 0 <- byte2
        """
        return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)

    def update_tilecache0(self, lcd, t, bank):
        if self._tilecache0_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = lcd.VRAM0[t*16 + k]
            byte2 = lcd.VRAM0[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                colorcode = self.color_code(byte1, byte2, 7 - x)
                self._tilecache0[y, x] = colorcode

        self._tilecache0_state[t] = 1

    def update_tilecache1(self, lcd, t, bank):
        pass

    def update_spritecache0(self, lcd, t, bank):
        if self._spritecache0_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = lcd.VRAM0[t*16 + k]
            byte2 = lcd.VRAM0[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                colorcode = self.color_code(byte1, byte2, 7 - x)
                self._spritecache0[y, x] = colorcode

        self._spritecache0_state[t] = 1

    def update_spritecache1(self, lcd, t, bank):
        if self._spritecache1_state[t]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = lcd.VRAM0[t*16 + k]
            byte2 = lcd.VRAM0[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                colorcode = self.color_code(byte1, byte2, 7 - x)
                self._spritecache1[y, x] = colorcode

        self._spritecache1_state[t] = 1

    def blank_screen(self, lcd):
        # If the screen is off, fill it with a color.
        for y in range(ROWS):
            for x in range(COLS):
                self._screenbuffer[y, x] = lcd.BGP.getcolor(0)

    def save_state(self, f):
        for y in range(ROWS):
            f.write(self._scanlineparameters[y][0])
            f.write(self._scanlineparameters[y][1])
            # We store (WX - 7). We add 7 and mask 8 bits to make it easier to serialize
            f.write((self._scanlineparameters[y][2] + 7) & 0xFF)
            f.write(self._scanlineparameters[y][3])
            f.write(self._scanlineparameters[y][4])

        for y in range(ROWS):
            for x in range(COLS):
                f.write_32bit(self._screenbuffer[y, x])

    def load_state(self, f, state_version):
        if state_version >= 2:
            for y in range(ROWS):
                self._scanlineparameters[y][0] = f.read()
                self._scanlineparameters[y][1] = f.read()
                # Restore (WX - 7) as described above
                self._scanlineparameters[y][2] = (f.read() - 7) & 0xFF
                self._scanlineparameters[y][3] = f.read()
                if state_version > 3:
                    self._scanlineparameters[y][4] = f.read()

        if state_version >= 6:
            for y in range(ROWS):
                for x in range(COLS):
                    self._screenbuffer[y, x] = f.read_32bit()

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
    def __init__(self, cgb, cartridge_cgb, disable_renderer, color_palette, cgb_color_palette, randomize=False):
        LCD.__init__(self, cgb, cartridge_cgb, disable_renderer, color_palette, cgb_color_palette, randomize=False)
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

        self._tilecache1_raw = array("B", [0xFF] * (TILES*8*8*4))

        self._tilecache1 = memoryview(self._tilecache1_raw).cast("I", shape=(TILES * 8, 8))
        self._tilecache1_state = array("B", [0] * TILES)
        self.clear_cache()

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
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = vram_bank[t*16 + k]
            byte2 = vram_bank[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                self._tilecache0[y, x] = self.color_code(byte1, byte2, 7 - x)

        self._tilecache0_state[t] = 1

    def update_tilecache1(self, lcd, t, bank):
        if self._tilecache1_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = vram_bank[t*16 + k]
            byte2 = vram_bank[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                self._tilecache1[y, x] = self.color_code(byte1, byte2, 7 - x)

        self._tilecache1_state[t] = 1

    def update_spritecache0(self, lcd, t, bank):
        if self._spritecache0_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = vram_bank[t*16 + k]
            byte2 = vram_bank[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                self._spritecache0[y, x] = self.color_code(byte1, byte2, 7 - x)

        self._spritecache0_state[t] = 1

    def update_spritecache1(self, lcd, t, bank):
        if self._spritecache1_state[t]:
            return
        if bank:
            vram_bank = lcd.VRAM1
        else:
            vram_bank = lcd.VRAM0
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = vram_bank[t*16 + k]
            byte2 = vram_bank[t*16 + k + 1]
            y = (t*16 + k) // 2

            for x in range(8):
                self._spritecache1[y, x] = self.color_code(byte1, byte2, 7 - x)

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
        #8 palettes of 4 colors each 2 bytes
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
        red = (cgb_color & 0x1F) << 3
        green = ((cgb_color >> 5) & 0x1F) << 3
        blue = ((cgb_color >> 10) & 0x1F) << 3
        rgb_color = ((red << 16) | (green << 8) | blue) << 8
        if index % 4 == 0:
            rgb_color |= COL0_FLAG
        return rgb_color

    def set(self, val):
        i_val = self.palette_mem[self.index_reg.getindex()]
        if self.index_reg.hl:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0x00FF) | (val << 8)
        else:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0xFF00) | val

        cgb_color = self.palette_mem[self.index_reg.getindex()] & 0x7FFF
        self.palette_mem_rgb[self.index_reg.getindex()] = self.cgb_to_rgb(cgb_color, self.index_reg.getindex())

        #check for autoincrement after write
        self.index_reg.shouldincrement()

    def get(self):
        if self.index_reg.hl:
            return (self.palette_mem[self.index_reg.getindex()] & 0xFF00) >> 8
        else:
            return self.palette_mem[self.index_reg.getindex()] & 0x00FF

    def getcolor(self, paletteindex, colorindex):
        # Each palette = 8 bytes or 4 colors of 2 bytes
        # if not (paletteindex <= 7 and colorindex <= 3):
        #     logger.error("Palette Mem Index Error, tried: Palette %d color %d", paletteindex, colorindex)

        return self.palette_mem_rgb[paletteindex*4 + colorindex]

    def save_state(self, f):
        for n in range(CGB_NUM_PALETTES * 4):
            f.write_16bit(self.palette_mem[n])

    def load_state(self, f, state_version):
        for n in range(CGB_NUM_PALETTES * 4):
            self.palette_mem[n] = f.read_16bit()
            self.palette_mem_rgb[n] = self.cgb_to_rgb(self.palette_mem[n], n % 4)
