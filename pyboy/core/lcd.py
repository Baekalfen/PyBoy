#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging
from array import array
from copy import deepcopy
from ctypes import c_void_p
from random import getrandbits

from pyboy.utils import color_code

logger = logging.getLogger(__name__)

VIDEO_RAM = 8 * 1024 # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0
# LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)
INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
ROWS, COLS = 144, 160
TILES = 384

FRAME_CYCLES = 70224

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class LCD:
    def __init__(
        self, cgb, cartridge_cgb, disable_renderer, color_palette, randomize=False, patch_supermarioland=False
    ):
        self.VRAM0 = array("B", [0] * VIDEO_RAM)
        self.OAM = array("B", [0] * OBJECT_ATTRIBUTE_MEMORY)

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
        self.max_ly = 153
        if patch_supermarioland:
            self.max_ly = 155 # Avoid jittering of top scanline. Possibly a fault in the game ROM.
        self.double_speed = False
        self.cgb = cgb

        if self.cgb:
            if cartridge_cgb:
                logger.info("Starting CGB renderer")
                self.renderer = CGBRenderer(color_palette, color_palette, color_palette)
                # self.renderer = Renderer(False, color_palette, color_palette, color_palette)
            else:
                logger.info("Starting CGB renderer in DMG-mode")
                # Running DMG ROM on CGB hardware
                # use the default palettes
                bg_pal = (0xFFFFFF, 0x7BFF31, 0x0063C5, 0x000000)
                obj0_pal = (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000)
                obj1_pal = (0xFFFFFF, 0xFF8484, 0xFF8484, 0x000000)
                # self.renderer = CGBRenderer(bg_pal, obj0_pal, obj1_pal)
                self.renderer = Renderer(False, bg_pal, obj0_pal, obj1_pal)
        else:
            logger.info("Starting DMG renderer")
            self.renderer = Renderer(False, color_palette, color_palette, color_palette)

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

    def cyclestointerrupt(self):
        return self.clock_target - self.clock

    def processing_frame(self):
        b = (not self.frame_done)
        if not b:
            self.frame_done = False # Clear vblank flag for next iteration
        return b

    def tick(self, cycles):
        interrupt_flag = 0
        self.clock += cycles

        if self._LCDC.lcd_enable:
            if self.clock >= self.clock_target:
                if self.LY == self.max_ly:
                    # Reset to new frame and start from mode 2
                    self.next_stat_mode = 2
                    self.LY = -1
                    self.clock %= FRAME_CYCLES
                    self.clock_target %= FRAME_CYCLES

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
                    self.clock_target += 80 * multiplier
                    self.next_stat_mode = 3
                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                elif self._STAT._mode == 3:
                    self.clock_target += 170 * multiplier
                    self.next_stat_mode = 0
                elif self._STAT._mode == 0: # HBLANK
                    self.clock_target += 206 * multiplier
                    if self.LY <= 143:
                        self.renderer.update_cache(self)
                        self.renderer.scanline(self.LY, self)
                        self.renderer.scanline_sprites(self, self.LY, self.renderer._screenbuffer, False)
                        self.next_stat_mode = 2
                    else:
                        self.next_stat_mode = 1
                elif self._STAT._mode == 1: # VBLANK
                    self.clock_target += 456 * multiplier
                    self.next_stat_mode = 1

                    if self.LY == 144:
                        interrupt_flag |= INTR_VBLANK
                        self.frame_done = True

                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

        else:
            # See also `self.set_lcdc`
            if self.clock >= FRAME_CYCLES:
                self.frame_done = True
                self.clock %= FRAME_CYCLES

                # Renderer
                self.renderer.blank_screen()

        return interrupt_flag

    # def setVRAM(self, i, value):
    #     if not 0x8000 <= i < 0xA000:
    #         raise IndexError(
    #             "Make sure adress in setVRAM is a valid VRAM adress: 0x8000 <= addr < 0xA000, tried %s" % hex(i)
    #         )

    #     if i < 0x9800:
    #         self.renderer.tiles_changed0.add(i & 0xFFF0)

    #     self.VRAM0[i - 0x8000] = value

    # def getVRAM(self, i, offset=True):
    #     i_off = 0x8000 if offset else 0x0
    #     return self.VRAM0[i - i_off]

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

    def getwindowpos(self):
        return (self.WX - 7, self.WY)

    def getviewport(self):
        return (self.SCX, self.SCY)


class PaletteRegister:
    def __init__(self, value):
        self.value = 0
        self.lookup = [0] * 4
        self.set(value)

    def set(self, value):
        # Pokemon Blue continuously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        for x in range(4):
            self.lookup[x] = (value >> x * 2) & 0b11
        return True

    def getcolor(self, i):
        return self.lookup[i]


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

    def next_mode(self, LY):
        if self._mode == 0 and LY != 144:
            return self.set_mode(2)
        else:
            return self.set_mode((self._mode + 1) % 4)

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
        # yapf: enable


class Renderer:
    def __init__(self, cgb, color_palette, obj0_palette, obj1_palette):
        self.cgb = cgb
        self.alphamask = 0xFF
        self.color_palette = [(c << 8) | self.alphamask for c in color_palette]
        self.obj0_palette = [(c << 8) | self.alphamask for c in obj0_palette]
        self.obj1_palette = [(c << 8) | self.alphamask for c in obj1_palette]
        self.color_format = "RGBA"

        self.buffer_dims = (ROWS, COLS)

        self.clearcache = False
        self.tiles_changed0 = set([])

        # Init buffers as white
        self._screenbuffer_raw = array("B", [0xFF] * (ROWS*COLS*4))
        self._tilecache0_raw = array("B", [0xFF] * (TILES*8*8*4))
        self._spritecache0_raw = array("B", [0xFF] * (TILES*8*8*4))
        self._spritecache1_raw = array("B", [0xFF] * (TILES*8*8*4))

        if cythonmode:
            self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
            self._tilecache0 = memoryview(self._tilecache0_raw).cast("I", shape=(TILES * 8, 8))
            self._spritecache0 = memoryview(self._spritecache0_raw).cast("I", shape=(TILES * 8, 8))
            self._spritecache1 = memoryview(self._spritecache1_raw).cast("I", shape=(TILES * 8, 8))
        else:
            v = memoryview(self._screenbuffer_raw).cast("I")
            self._screenbuffer = [v[i:i + COLS] for i in range(0, COLS * ROWS, COLS)]
            v = memoryview(self._tilecache0_raw).cast("I")
            self._tilecache0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            v = memoryview(self._spritecache0_raw).cast("I")
            self._spritecache0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            v = memoryview(self._spritecache1_raw).cast("I")
            self._spritecache1 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        self._scanlineparameters = [[0, 0, 0, 0, 0] for _ in range(ROWS)]
        self.ly_window = 0

    def scanline(self, y, lcd):
        bx, by = lcd.getviewport()
        wx, wy = lcd.getwindowpos()
        self._scanlineparameters[y][0] = bx
        self._scanlineparameters[y][1] = by
        self._scanlineparameters[y][2] = wx
        self._scanlineparameters[y][3] = wy
        self._scanlineparameters[y][4] = lcd._LCDC.tiledata_select

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

                if self.cgb:
                    palette, vbank, horiflip, vertflip, bgpriority = self.get_background_map_attributes(lcd, tile_addr)
                    tilecache = (self._tilecache1[palette] if vbank else self._tilecache0[palette])
                    # col_index = (self._col_index1 if vbank else self._col_index0)
                    xx = (7 - ((x-wx) % 8)) if horiflip else ((x-wx) % 8)
                    yy = (8*wt + (7 - (self.ly_window) % 8)) if vertflip else (8*wt + (self.ly_window) % 8)
                else:
                    tilecache = self._tilecache0
                    xx = (x-wx) % 8
                    yy = 8*wt + (self.ly_window) % 8

                self._screenbuffer[y][x] = tilecache[yy][xx]
            elif lcd._LCDC.background_enable:
                tile_addr = background_offset + (y+by) // 8 * 32 % 0x400 + (x+bx) // 8 % 32
                bt = lcd.VRAM0[tile_addr]
                # If using signed tile indices, modify index
                if not lcd._LCDC.tiledata_select:
                    # (x ^ 0x80 - 128) to convert to signed, then
                    # add 256 for offset (reduces to + 128)
                    bt = (bt ^ 0x80) + 128

                if self.cgb:
                    palette, vbank, horiflip, vertflip, bgpriority = self.get_background_map_attributes(lcd, tile_addr)
                    tilecache = (
                        self._tilecache1[palette] if vbank else self._tilecache0[palette]
                    ) # TODO: Pick palette as well self._tilecache1[p][y][x]
                    # col_index = (self._col_index1 if vbank else self._col_index0)
                    xx = (7 - ((x+offset) % 8)) if horiflip else ((x+offset) % 8)
                    yy = (8*bt + (7 - (y+by) % 8)) if vertflip else (8*bt + (y+by) % 8)
                else:
                    tilecache = self._tilecache0
                    xx = (x+offset) % 8
                    yy = 8*bt + (y+by) % 8

                # import pdb;pdb.set_trace()
                # if tilecache[yy][xx] != 255:
                #     breakpoint()
                self._screenbuffer[y][x] = tilecache[yy][xx]
            else:
                # If background is disabled, it becomes white
                self._screenbuffer[y][x] = self.color_palette[0]

        if y == 143:
            # Reset at the end of a frame. We set it to -1, so it will be 0 after the first increment
            self.ly_window = -1

    def key_priority(self, x):
        # NOTE: Cython is being insufferable, and demands a non-lambda function
        return (self.sprites_to_render_x[x], self.sprites_to_render_n[x])

    def scanline_sprites(self, lcd, ly, buffer, ignore_priority):

        if not lcd._LCDC.sprite_enable:
            return

        spriteheight = 16 if lcd._LCDC.sprite_height else 8
        bgpkey = self.color_palette[lcd.BGP.getcolor(0)]

        sprite_count = 0
        self.sprites_to_render_n = [0] * 10
        self.sprites_to_render_x = [0] * 10

        # Find the first 10 sprites in OAM that appears on this scanline.
        # The lowest X-coordinate has priority, when overlapping

        # Loop through OAM, find 10 first sprites for scanline. Order based on X-coordinate high-to-low. Render them.
        for n in range(0x00, 0xA0, 4):
            y = lcd.OAM[n] - 16 # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8 # Documentation states the x coordinate needs to be subtracted by 8

            if y <= ly < y + spriteheight:
                self.sprites_to_render_n[sprite_count] = n
                self.sprites_to_render_x[sprite_count] = x # Used for sorting for priority
                sprite_count += 1

            if sprite_count == 10:
                break

        # Pan docs:
        # When these 10 sprites overlap, the highest priority one will appear above all others, etc. (Thus, no
        # Z-fighting.) In CGB mode, the first sprite in OAM ($FE00-$FE03) has the highest priority, and so on. In
        # Non-CGB mode, the smaller the X coordinate, the higher the priority. The tie breaker (same X coordinates) is
        # the same priority as in CGB mode.
        sprites_priority = sorted(range(sprite_count), key=self.key_priority)

        for _n in sprites_priority[::-1]:
            n = self.sprites_to_render_n[_n]
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
                spritecache = self._spritecache1[palette] if attributes & 0b1000 else self._spritecache0[palette]
            else:
                spritecache = self._spritecache1 if attributes & 0b10000 else self._spritecache0

            dy = ly - y
            yy = spriteheight - dy - 1 if yflip else dy

            for dx in range(8):
                xx = 7 - dx if xflip else dx
                pixel = spritecache[8*tileindex + yy][xx]
                if 0 <= x < COLS:
                    # TODO: Checking `buffer[y][x] == bgpkey` is a bit of a hack
                    if (spritepriority and not buffer[ly][x] == bgpkey):
                        # Add a fake alphachannel to the sprite for BG pixels. We can't just merge this
                        # with the next 'if', as sprites can have an alpha channel in other ways
                        pixel &= ~self.alphamask

                    if pixel & self.alphamask:
                        buffer[ly][x] = pixel
                x += 1
            x -= 8

    def render_sprites(self, lcd, buffer, ignore_priority):
        # NOTE: LEGACY FUNCTION FOR DEBUG WINDOW! Use scanline_sprites instead

        # Render sprites
        # - Doesn't restrict 10 sprites per scan line
        # - Prioritizes sprite in inverted order
        spriteheight = 16 if lcd._LCDC.sprite_height else 8
        bgpkey = self.color_palette[lcd.BGP.getcolor(0)]

        sprites_on_ly = [0] * 144

        for n in range(0x00, 0xA0, 4):
            y = lcd.OAM[n] - 16 # Documentation states the y coordinate needs to be subtracted by 16
            x = lcd.OAM[n + 1] - 8 # Documentation states the x coordinate needs to be subtracted by 8
            tileindex = lcd.OAM[n + 2]
            attributes = lcd.OAM[n + 3]
            xflip = attributes & 0b00100000
            yflip = attributes & 0b01000000
            spritepriority = (attributes & 0b10000000) and not ignore_priority
            spritecache = (self._spritecache1 if attributes & 0b10000 else self._spritecache0)

            for dy in range(spriteheight):
                yy = spriteheight - dy - 1 if yflip else dy

                # Take care of sprite priorty. No more than 10 sprites per scanline
                if 0 <= y < 144:
                    if sprites_on_ly[y] >= 10:
                        continue
                    else:
                        sprites_on_ly[y] += 1

                if 0 <= y < ROWS:
                    for dx in range(8):
                        xx = 7 - dx if xflip else dx
                        pixel = spritecache[0][8*tileindex + yy][xx]
                        if 0 <= x < COLS:
                            # TODO: Checking `buffer[y][x] == bgpkey` is a bit of a hack
                            if (spritepriority and not buffer[y][x] == bgpkey):
                                # Add a fake alphachannel to the sprite for BG pixels. We can't just merge this
                                # with the next 'if', as sprites can have an alpha channel in other ways
                                pixel &= ~self.alphamask

                            if pixel & self.alphamask:
                                buffer[y][x] = pixel
                        x += 1
                    x -= 8
                y += 1

    def update_cache(self, lcd):
        if self.clearcache:
            self.tiles_changed0.clear()
            for x in range(0x8000, 0x9800, 16):
                self.tiles_changed0.add(x)
            self.clearcache = False

        for t in self.tiles_changed0:
            for k in range(0, 16, 2): # 2 bytes for each line
                byte1 = lcd.VRAM0[t + k - 0x8000]
                byte2 = lcd.VRAM0[t + k + 1 - 0x8000]
                y = (t+k-0x8000) // 2

                for x in range(8):
                    colorcode = color_code(byte1, byte2, 7 - x)

                    self._tilecache0[y][x] = self.color_palette[lcd.BGP.getcolor(colorcode)]
                    self._spritecache0[y][x] = self.obj0_palette[lcd.OBP0.getcolor(colorcode)]
                    self._spritecache1[y][x] = self.obj1_palette[lcd.OBP1.getcolor(colorcode)]

                    if colorcode == 0:
                        self._spritecache0[y][x] &= ~self.alphamask
                        self._spritecache1[y][x] &= ~self.alphamask

        self.tiles_changed0.clear()

    def blank_screen(self):
        # If the screen is off, fill it with a color.
        color = self.color_palette[0]
        for y in range(ROWS):
            for x in range(COLS):
                self._screenbuffer[y][x] = color

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
                z = self._screenbuffer[y][x]
                f.write_32bit(z)

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
                    self._screenbuffer[y][x] = f.read_32bit()

        self.clearcache = True


####################################
#
#  ██████   ██████   ██████
# ██       ██        ██   ██
# ██       ██   ███  ██████
# ██       ██    ██  ██   ██
#  ██████   ██████   ██████
#
# Palette memory = 4 colors of 2 bytes define colors for a palette, 8 different palettes
PALETTE_MEM_MAX_INDEX = 0x3f
NUM_PALETTES = 8
NUM_COLORS = 4


class CGBLCD(LCD):
    def __init__(
        self, cgb, cartridge_cgb, disable_renderer, color_palette, randomize=False, patch_supermarioland=False
    ):
        LCD.__init__(
            self, cgb, cartridge_cgb, disable_renderer, color_palette, randomize=False, patch_supermarioland=False
        )
        self.VRAM1 = array("B", [0] * VIDEO_RAM)

        #8 palettes of 4 colors each 2 bytes
        self.sprite_palette_mem = array("I", [0xFFFF] * NUM_PALETTES * NUM_COLORS)
        self.bg_palette_mem = array("I", [0xFFFF] * NUM_PALETTES * NUM_COLORS)

        # Init with some colors -- TODO: What are real defaults?
        for n in range(0, len(self.sprite_palette_mem), 4):
            c = [0x1CE7, 0x1E19, 0x7E31, 0x217B]
            for m in range(4):
                self.sprite_palette_mem[n + m] = c[m]
                self.bg_palette_mem[n + m] = c[m]

        self.vbk = VBKregister()
        self.bcps = PaletteIndexRegister()
        self.bcpd = PaletteColorRegister(self.bg_palette_mem, self.bcps)
        self.ocps = PaletteIndexRegister()
        self.ocpd = PaletteColorRegister(self.sprite_palette_mem, self.ocps)


#     def setVRAM(self, i, value):
#         if not 0x8000 <= i < 0xA000:
#             raise IndexError(
#                 "Make sure adress in setVRAM is a valid VRAM adress: 0x8000 <= addr < 0xA000, tried %s" % hex(i)
#             )

#         if self.vbk.active_bank == 0:
#             self.VRAM0[i - 0x8000] = value
#             if i < 0x9800:
#                 self.renderer.tiles_changed0.add(i & 0xFFF0)
#         else:
#             self.VRAM1[i - 0x8000] = value
#             if i < 0x9800:
#                 self.renderer.tiles_changed1.add(i & 0xFFF0)

#     def getVRAM(self, i, offset=True):
#         i_off = 0x8000 if offset else 0x0
#         if self.vbk.active_bank == 0:
#             return self.VRAM0[i - i_off]
#         else:
#             return self.VRAM1[i - i_off]

#     def getVRAMbank(self, i, bank, offset=True):
#         i_off = 0x8000 if offset else 0x0
#         if bank == 0:
#             return self.VRAM0[i - i_off]
#         else:
#             return self.VRAM1[i - i_off]


class CGBRenderer(Renderer):
    def __init__(self, color_palette, obj0_palette, obj1_palette):
        Renderer.__init__(self, True, color_palette, obj0_palette, obj1_palette)
        self.tiles_changed1 = set([])

        # # Init buffers as white
        # self._screenbuffer_raw = array("B", [0xFF] * (ROWS*COLS*4))
        # self._tilecache0_raw = array("B", [0xFF] * (TILES*8*8*4))
        # self._spritecache0_raw = array("B", [0xFF] * (TILES*8*8*4))
        # self._spritecache1_raw = array("B", [0xFF] * (TILES*8*8*4))

        # if cythonmode:
        #     self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
        #     self._tilecache0 = memoryview(self._tilecache0_raw).cast("I", shape=(TILES * 8, 8))
        #     self._spritecache0 = memoryview(self._spritecache0_raw).cast("I", shape=(TILES * 8, 8))
        #     self._spritecache1 = memoryview(self._spritecache1_raw).cast("I", shape=(TILES * 8, 8))
        # else:
        #     v = memoryview(self._screenbuffer_raw).cast("I")
        #     self._screenbuffer = [v[i:i + COLS] for i in range(0, COLS * ROWS, COLS)]
        #     v = memoryview(self._tilecache0_raw).cast("I")
        #     self._tilecache0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
        #     v = memoryview(self._spritecache0_raw).cast("I")
        #     self._spritecache0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
        #     v = memoryview(self._spritecache1_raw).cast("I")
        #     self._spritecache1 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
        #     self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        # self._scanlineparameters = [[0, 0, 0, 0, 0] for _ in range(ROWS)]
        # self.ly_window = 0

        # Init buffers as white
        # 1 tile-/spritecache for each bank
        # self._screenbuffer_raw = array("B", [0xFF] * (ROWS*COLS*4))
        self._tilecache0_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))
        self._tilecache1_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))
        self._spritecache0_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))
        self._spritecache1_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))
        self._col_index0_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))
        self._col_index1_raw = array("B", [0xFF] * (TILES*8*8*4*NUM_PALETTES))

        if cythonmode:
            self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
            self._tilecache0 = memoryview(self._tilecache_raw).cast("I", shape=(NUM_PALETTES, TILES * 8, 8))
            self._tilecache1 = memoryview(self._tilecache_raw).cast("I", shape=(NUM_PALETTES, TILES * 8, 8))
            self._spritecache0 = memoryview(self._spritecache0_raw).cast("I", shape=(NUM_PALETTES, TILES * 8, 8))
            self._spritecache1 = memoryview(self._spritecache1_raw).cast("I", shape=(NUM_PALETTES, TILES * 8, 8))
        else:
            v = memoryview(self._screenbuffer_raw).cast("I")
            self._screenbuffer = [v[i:i + COLS] for i in range(0, COLS * ROWS, COLS)]

            stride = TILES * 8 * 8

            v = memoryview(self._tilecache0_raw).cast("I")
            v = array("I", self._tilecache0_raw.tolist())
            # self.tc0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._tilecache0 = [[v[i:i + 8] for i in range(stride * j, stride * (j+1), 8)] for j in range(NUM_PALETTES)]

            v = memoryview(self._tilecache1_raw).cast("I")
            v = array("I", self._tilecache1_raw.tolist())
            # self.tc1 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._tilecache1 = [[v[i:i + 8] for i in range(stride * j, stride * (j+1), 8)] for j in range(NUM_PALETTES)]

            v = memoryview(self._spritecache0_raw).cast("I")
            v = array("I", self._spritecache0_raw.tolist())
            # self.sc0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._spritecache0 = [[v[i:i + 8] for i in range(stride * j, stride * (j+1), 8)]
                                  for j in range(NUM_PALETTES)]

            v = memoryview(self._spritecache1_raw).cast("I")
            v = array("I", self._spritecache1_raw.tolist())
            # self.sc1 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._spritecache1 = [[v[i:i + 8] for i in range(stride * j, stride * (j+1), 8)]
                                  for j in range(NUM_PALETTES)]

            v = memoryview(self._col_index0_raw).cast("I")
            v = array("I", self._col_index0_raw.tolist())
            self._col_index0 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            v = memoryview(self._col_index1_raw).cast("I")
            v = array("I", self._col_index1_raw.tolist())
            self._col_index1 = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
            self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

            # create the 3d lists to hold palettes, 8 palettes


#             for i in range(8):
#                 self._tilecache0.append(deepcopy(self.tc0))
#                 self._tilecache1.append(deepcopy(self.tc1))
#                 self._spritecache0.append(deepcopy(self.sc0))
#                 self._spritecache1.append(deepcopy(self.sc1))

# self._scanlineparameters = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(ROWS)]

        self._col_i = [[0] * COLS for _ in range(ROWS)]
        self._bg_priority = [[0] * COLS for _ in range(ROWS)]

    def get_background_map_attributes(self, lcd, i):
        tile_num = lcd.VRAM1[i]
        palette = tile_num & 0b111
        vbank = (tile_num >> 3) & 1
        horiflip = (tile_num >> 5) & 1
        vertflip = (tile_num >> 6) & 1
        bgpriority = (tile_num >> 7) & 1

        return palette, vbank, horiflip, vertflip, bgpriority

    #def render_screen(self, lcd):
    #    self.update_cache(lcd)
    #    # All VRAM addresses are offset by 0x8000
    #    # Following addresses are 0x9800 and 0x9C00

    #    for y in range(ROWS):
    #        bx, by, wx, wy, tile_data_select, bgmap_select, wmap_select, window_enable, _ = self._scanlineparameters[y]
    #        background_offset = 0x1800 if bgmap_select == 0 else 0x1C00
    #        wmap = 0x1800 if wmap_select == 0 else 0x1C00

    #        # Used for the half tile at the left side when scrolling
    #        offset = bx & 0b111

    #        for x in range(COLS):
    #            # WINDOW
    #            if window_enable and wy <= y and wx <= x:
    #                index = wmap + (y-wy) // 8 * 32 % 0x400 + (x-wx) // 8 % 32
    #                wt = lcd.getVRAMbank(index, 0, False)

    #                #cgb specific map attributes

    #                palette, vbank, horiflip, vertflip, bgpriority = self.get_background_map_attributes(lcd, index)
    #                tilecache = (self._tilecache1 if vbank else self._tilecache0)
    #                col_index = (self._col_index1 if vbank else self._col_index0)
    #                xx = (7 - ((x-wx) % 8)) if horiflip else ((x-wx) % 8)

    #                # If using signed tile indices, modify index
    #                if not tile_data_select:
    #                    # (x ^ 0x80 - 128) to convert to signed, then
    #                    # add 256 for offset (reduces to + 128)
    #                    wt = (wt ^ 0x80) + 128

    #                yy = (8*wt + (7 - (y-wy) % 8)) if vertflip else (8*wt + (y-wy) % 8)
    #                self._screenbuffer[y][x] = tilecache[palette][yy][xx]
    #                self._col_i[y][x] = col_index[yy][xx]
    #                self._bg_priority[y][x] = bgpriority

    #            # BACKGROUND
    #            else:
    #                index = background_offset + (y+by) // 8 * 32 % 0x400 + (x+bx) // 8 % 32
    #                bt = lcd.getVRAMbank(index, 0, False)

    #                #cgb specific map attributes
    #                palette, vbank, horiflip, vertflip, bgpriority = self.get_background_map_attributes(lcd, index)
    #                tilecache = (self._tilecache1 if vbank else self._tilecache0)
    #                col_index = (self._col_index1 if vbank else self._col_index0)

    #                xx = (7 - ((x+offset) % 8)) if horiflip else ((x+offset) % 8)

    #                # If using signed tile indices, modify index
    #                if not tile_data_select:
    #                    # (x ^ 0x80 - 128) to convert to signed, then
    #                    # add 256 for offset (reduces to + 128)
    #                    bt = (bt ^ 0x80) + 128

    #                yy = (8*bt + (7 - (y+by) % 8)) if vertflip else (8*bt + (y+by) % 8)
    #                self._screenbuffer[y][x] = tilecache[palette][yy][xx]
    #                self._col_i[y][x] = col_index[yy][xx]
    #                self._bg_priority[y][x] = bgpriority

    #    if lcd.LCDC.sprite_enable:
    #        self.render_sprites(lcd, self._screenbuffer)

    #def render_sprites(self, lcd, buffer, ignore_priority=False):
    #    # Render sprites
    #    # - Doesn't restrict 10 sprites per scan line
    #    # - Prioritizes sprite in inverted order
    #    spriteheight = 16 if lcd.LCDC.sprite_height else 8

    #    # CGB priotizes sprites located first in OAM
    #    for n in range(0x9C, -0x04, -4):
    #        y = lcd.OAM[n] - 16 # Documentation states the y coordinate needs to be subtracted by 16
    #        x = lcd.OAM[n + 1] - 8 # Documentation states the x coordinate needs to be subtracted by 8
    #        tileindex = lcd.OAM[n + 2]
    #        attributes = lcd.OAM[n + 3]
    #        xflip = attributes & 0b00100000
    #        yflip = attributes & 0b01000000
    #        OAMbgpriority = (attributes & 0b10000000)

    #        # bit 3 selects tile vram-bank
    #        spritecache = (self._spritecache1 if attributes & 0b1000 else self._spritecache0)
    #        # bits 0-2 selects palette number
    #        palette = attributes & 0b111

    #        for dy in range(spriteheight):
    #            yy = spriteheight - dy - 1 if yflip else dy
    #            if 0 <= y < ROWS:
    #                for dx in range(8):
    #                    xx = 7 - dx if xflip else dx
    #                    pixel = spritecache[palette][8*tileindex + yy][xx]
    #                    if 0 <= x < COLS:
    #                        use_priority_flags = self._scanlineparameters[y][8]
    #                        if use_priority_flags:
    #                            bgmappriority = self._bg_priority[y][x]
    #                            col = self._col_i[y][x]
    #                            if bgmappriority:
    #                                if not col == 0:
    #                                    pixel &= ~self.alphamask
    #                            elif OAMbgpriority:
    #                                if not col == 0:
    #                                    pixel &= ~self.alphamask
    #                        if pixel & self.alphamask:
    #                            buffer[y][x] = pixel
    #                    x += 1
    #                x -= 8
    #            y += 1

    def update_cache(self, lcd):
        if self.clearcache:
            self.tiles_changed0.clear()
            self.tiles_changed1.clear()
            for x in range(0x8000, 0x9800, 16):
                self.tiles_changed0.add(x)
                self.tiles_changed1.add(x)
            self.clearcache = False
        self.update_tiles(lcd, self.tiles_changed0, 0)
        self.update_tiles(lcd, self.tiles_changed1, 1)
        # for p in range(len(self._tilecache1)):
        #     for t in range(len(self._tilecache1[0])):
        #         for x in range(len(self._tilecache1[0][0])):
        #             self._tilecache0[p][t][x] = 0x123456
        #             self._tilecache1[p][t][x] = 0x123456
        self.tiles_changed0.clear()
        self.tiles_changed1.clear()

    def convert_to_rgba(self, color):
        # converts a 24 bit RGB color to 32 bit RGBA
        return (color << 8) | self.alphamask

    def update_tiles(self, lcd, tiles_changed, bank):
        for t in tiles_changed:
            for k in range(0, 16, 2): # 2 bytes for each line
                if bank:
                    byte1 = lcd.VRAM1[t + k - 0x8000]
                    byte2 = lcd.VRAM1[t + k + 1 - 0x8000]
                else:
                    byte1 = lcd.VRAM0[t + k - 0x8000]
                    byte2 = lcd.VRAM0[t + k + 1 - 0x8000]

                # byte1 = lcd.getVRAMbank(t + k, bank)
                # byte2 = lcd.getVRAMbank(t + k + 1, bank)

                y = (t+k-0x8000) // 2

                for x in range(8):
                    #index into the palette for the current pixel
                    colorcode = color_code(byte1, byte2, 7 - x)

                    if bank:
                        self._col_index1[y][x] = colorcode
                    else:
                        self._col_index0[y][x] = colorcode

                    # update for the 8 palettes
                    for p in range(8):
                        if bank:
                            self._tilecache1[p][y][x] = self.convert_to_rgba(lcd.bcpd.getcolor(p, colorcode))
                            self._spritecache1[p][y][x] = self.convert_to_rgba(lcd.ocpd.getcolor(p, colorcode))
                        else:
                            self._tilecache0[p][y][x] = self.convert_to_rgba(lcd.bcpd.getcolor(p, colorcode))
                            self._spritecache0[p][y][x] = self.convert_to_rgba(lcd.ocpd.getcolor(p, colorcode))

                        # first color transparent for sprites
                        if colorcode == 0:
                            if bank:
                                self._spritecache1[p][y][x] &= ~self.alphamask
                            else:
                                self._spritecache0[p][y][x] &= ~self.alphamask


class VBKregister:
    def __init__(self, value=0):
        self.active_bank = value

    def set(self, value):
        # when writing to VBK, bit 0 indicates which bank to switch to
        bank = value & 1
        self._switch_bank(bank)

    def get(self):
        # reading from this register returns current VRAM bank in bit 0, other bits = 1
        return self.active_bank | 0xFE

    def _switch_bank(self, bank):
        if bank == self.active_bank:
            return
        else:
            self.active_bank = bank


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

    # hl defines which of the two bytes in a color is needed
    def gethl(self):
        return self.hl

    def _inc_index(self):
        # what happens if increment is set and index is at max 0x3F?
        # undefined behavior
        self.index += 1

    def shouldincrement(self):
        if self.auto_inc:
            # ensure autoinc also set for new val
            new_val = 0x80 | (self.value + 1)
            self.set(new_val)


class PaletteColorRegister:
    def __init__(self, palette_mem, i_reg):
        self.palette_mem = palette_mem
        self.index_reg = i_reg

    def set(self, val):
        hl = self.index_reg.gethl()
        i_val = self.palette_mem[self.index_reg.getindex()]
        if hl:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0x00FF) | (val << 8)
        else:
            self.palette_mem[self.index_reg.getindex()] = (i_val & 0xFF00) | val

        #check for autoincrement after write
        self.index_reg.shouldincrement()

    def get(self):
        return self.palette_mem[self.index_reg.getindex()]

    def getcolor(self, paletteindex, colorindex):
        #each palette = 8 bytes or 4 colors of 2 bytes
        if paletteindex > 7 or colorindex > 3:
            raise IndexError("Palette Mem Index Error, tried: Palette %s color %s" % (paletteindex, colorindex))

        i = paletteindex*4 + colorindex
        color = self.palette_mem[i]

        cgb_col = self._cgbcolor(color)
        return self._convert15bitcol(cgb_col)


### MOVE TO UTILS?
# takes 2 bytes from palette memory and gets the cgb color
# only first 15 bits used

    def _cgbcolor(self, color_bytes):
        #only care about 15 first bits
        mask = 0x7FFF
        return color_bytes & mask

    # converts 15 bit color to 24 bit
    def _convert15bitcol(self, color):
        # colors 5 bits
        color_mask = 0x1F

        red = (color & color_mask) << 3
        green = ((color >> 5) & color_mask) << 3
        blue = ((color >> 10) & color_mask) << 3

        final_color = (red << 16) | (green << 8) | blue
        return final_color
