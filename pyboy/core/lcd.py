#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging
from array import array
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
    def __init__(self, disable_renderer, color_palette, randomize=False):
        self.VRAM = array("B", [0] * VIDEO_RAM)
        self.OAM = array("B", [0] * OBJECT_ATTRIBUTE_MEMORY)

        if randomize:
            for i in range(VIDEO_RAM):
                self.VRAM[i] = getrandbits(8)
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
        self.renderer = Renderer(disable_renderer, color_palette)

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
                if self.LY == 153:
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

                # LCD state machine
                if self._STAT._mode == 2: # Searching OAM
                    self.clock_target += 80
                    self.next_stat_mode = 3
                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                elif self._STAT._mode == 3:
                    self.clock_target += 170
                    self.next_stat_mode = 0
                elif self._STAT._mode == 0: # HBLANK
                    self.clock_target += 206
                    if self.LY <= 143:
                        self.renderer.update_cache(self)
                        self.renderer.scanline(self.LY, self)
                        self.renderer.scanline_sprites(self, self.LY, self.renderer._screenbuffer, False)
                        self.next_stat_mode = 2
                    else:
                        self.next_stat_mode = 1
                elif self._STAT._mode == 1: # VBLANK
                    self.clock_target += 456
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

    def save_state(self, f):
        for n in range(VIDEO_RAM):
            f.write(self.VRAM[n])

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
            self.VRAM[n] = f.read()

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
    def __init__(self, disable_renderer, color_palette):
        self.alphamask = 0xFF
        self.color_palette = [(c << 8) | self.alphamask for c in color_palette]
        self.color_format = "RGBA"

        self.buffer_dims = (160, 144)

        self.clearcache = False
        self.tiles_changed = set([])
        self.disable_renderer = disable_renderer

        # Init buffers as white
        self._screenbuffer_raw = array("B", [0xFF] * (ROWS*COLS*4))
        self._tilecache_raw = array("B", [0xFF] * (TILES*8*8*4))
        self._spritecache0_raw = array("B", [0xFF] * (TILES*8*8*4))
        self._spritecache1_raw = array("B", [0xFF] * (TILES*8*8*4))

        if cythonmode:
            self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
            self._tilecache = memoryview(self._tilecache_raw).cast("I", shape=(TILES * 8, 8))
            self._spritecache0 = memoryview(self._spritecache0_raw).cast("I", shape=(TILES * 8, 8))
            self._spritecache1 = memoryview(self._spritecache1_raw).cast("I", shape=(TILES * 8, 8))
        else:
            v = memoryview(self._screenbuffer_raw).cast("I")
            self._screenbuffer = [v[i:i + COLS] for i in range(0, COLS * ROWS, COLS)]
            v = memoryview(self._tilecache_raw).cast("I")
            self._tilecache = [v[i:i + 8] for i in range(0, TILES * 8 * 8, 8)]
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
                wt = lcd.VRAM[wmap + (self.ly_window) // 8 * 32 % 0x400 + (x-wx) // 8 % 32]
                # If using signed tile indices, modify index
                if not lcd._LCDC.tiledata_select:
                    # (x ^ 0x80 - 128) to convert to signed, then
                    # add 256 for offset (reduces to + 128)
                    wt = (wt ^ 0x80) + 128
                self._screenbuffer[y][x] = self._tilecache[8*wt + (self.ly_window) % 8][(x-wx) % 8]
            elif lcd._LCDC.background_enable:
                bt = lcd.VRAM[background_offset + (y+by) // 8 * 32 % 0x400 + (x+bx) // 8 % 32]
                # If using signed tile indices, modify index
                if not lcd._LCDC.tiledata_select:
                    # (x ^ 0x80 - 128) to convert to signed, then
                    # add 256 for offset (reduces to + 128)
                    bt = (bt ^ 0x80) + 128
                self._screenbuffer[y][x] = self._tilecache[8*bt + (y+by) % 8][(x+offset) % 8]
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
            spritecache = (self._spritecache1 if attributes & 0b10000 else self._spritecache0)

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
                        pixel = spritecache[8*tileindex + yy][xx]
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
            self.tiles_changed.clear()
            for x in range(0x8000, 0x9800, 16):
                self.tiles_changed.add(x)
            self.clearcache = False

        for t in self.tiles_changed:
            for k in range(0, 16, 2): # 2 bytes for each line
                byte1 = lcd.VRAM[t + k - 0x8000]
                byte2 = lcd.VRAM[t + k + 1 - 0x8000]
                y = (t+k-0x8000) // 2

                for x in range(8):
                    colorcode = color_code(byte1, byte2, 7 - x)

                    self._tilecache[y][x] = self.color_palette[lcd.BGP.getcolor(colorcode)]
                    self._spritecache0[y][x] = self.color_palette[lcd.OBP0.getcolor(colorcode)]
                    self._spritecache1[y][x] = self.color_palette[lcd.OBP1.getcolor(colorcode)]

                    if colorcode == 0:
                        self._spritecache0[y][x] &= ~self.alphamask
                        self._spritecache1[y][x] &= ~self.alphamask

        self.tiles_changed.clear()

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
