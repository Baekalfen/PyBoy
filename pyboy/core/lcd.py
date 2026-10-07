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

# The target mode and timing phase are independent parts of the LCD state.
STAT_TRANSITION_NONE = 0
STAT_TRANSITION_ADVANCE_LY = 1
STAT_TRANSITION_START_MODE2 = 2
STAT_TRANSITION_VBLANK_PRETRIGGERED = 3

# The dot-accurate renderer lags the STAT mode 3 signal by this many dots. The
# pixel pipeline first runs a discarded fetch and then the first real fetch,
# so hardware colors the first background pixel 15 dots into mode 3 (kevtris:
# pixel output occupies the last 159 cycles of the 173.5-cycle mode 3). The
# renderer pipeline produces it at its own dot 9, so the renderer clock starts
# 6 dots after the mode change.
DOT_MODE3_RENDER_DELAY = 6


def rgb_to_bgr(color):
    a = 0xFF
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (a << 24) | (b << 16) | (g << 8) | r


class LCD:
    def __init__(self, cgb, cgb_mode, color_palette, cgb_color_palette, randomize=False):
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
        self.stat_mode_override = False
        self.lyc_changed_while_disabled = False
        self._cycles_to_interrupt = 0
        self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift
        self.next_stat_mode = 2
        self.stat_transition = STAT_TRANSITION_NONE
        self.stat_irq_delayed = False
        self.stat_irq_delivery_clock = 0
        self.LY = 0x00
        self.mode3_extension = 0
        self.mode3_start_clock = 0
        self._STAT.set_mode(0)

        self.SCY = 0x00
        self.SCX = 0x00
        self.LYC = 0x00
        # self.DMA = 0x00
        self.WY = 0x00
        self.WX = 0x00
        self.object_priority_mode = 0xFF  # TODO: Not implemented

        self.cgb = cgb
        self._downgraded_to_dmg = False
        self._scanlineparameters = [[0, 0, 0, 0, 0] for _ in range(ROWS)]
        self.last_cycles = 0
        self._cycles_to_interrupt = 0
        self._cycles_to_frame = (FRAME_CYCLES - self.clock) << self.speed_shift

        if self.cgb:
            logger.debug("Starting CGB renderer")
            # Setting for both modes, even though CGB is ignoring them.
            bg_pal, obj0_pal, obj1_pal = cgb_color_palette
            self.BGP = PaletteRegister(0xFC, bg_pal)
            self.OBP0 = PaletteRegister(0xFF, obj0_pal)
            self.OBP1 = PaletteRegister(0xFF, obj1_pal)
        else:
            logger.debug("Starting DMG renderer")
            self.BGP = PaletteRegister(0xFC, color_palette)
            self.OBP0 = PaletteRegister(0xFF, color_palette)
            self.OBP1 = PaletteRegister(0xFF, color_palette)
        self.renderer = Renderer(self, self.cgb)

        # CGB specific
        if self.cgb:
            self.VRAM1 = array("B", [0] * VIDEO_RAM)

            self.vbk = VBKregister()
            self.bcps = PaletteIndexRegister()  # Only stored here for access in mb
            self.bcpd = PaletteColorRegister(self.bcps)
            self.ocps = PaletteIndexRegister()  # Only stored here for access in mb
            self.ocpd = PaletteColorRegister(self.ocps)

    def switch_cgb(self, is_dmg_rom):
        # Bootrom requests CGB hardware to switch to DMG rendering. This is only
        # done once, and only downgraded from CGB to DMG at the end of CGB bootrom.
        if self.cgb and is_dmg_rom:
            logger.debug("Migrating from CGB renderer to DMG renderer")
            self.cgb = False
            self.renderer.cgb = False
            self._downgraded_to_dmg = True
        else:
            logger.debug("Ignoring key0 change")

    def set_lcdc(self, value):
        _lcd_enable = self._LCDC.lcd_enable
        _window_enable = self._LCDC.window_enable
        self._LCDC.set(value)

        # On CGB, clearing the window enable bit resets the window Y condition.
        if self.cgb and _window_enable and not self._LCDC.window_enable:
            self.renderer.wy_activated_frame = False

        # The WY==LY window condition is re-evaluated when LCDC is written,
        # at the next PPU clock edge (SameBoy schedules a wy_check on every
        # LCDC write). This catches a window enabled mid-mode-2, after the
        # mode-2-start comparison already ran with the window off.
        if self._LCDC.lcd_enable and self._LCDC.window_enable and self.WY == self.LY:
            self.renderer.wy_activated_frame = True

        if _lcd_enable and (not self._LCDC.lcd_enable):
            # https://www.reddit.com/r/Gameboy/comments/a1c8h0/what_happens_when_a_gameboy_screen_is_disabled/
            # 1. LY (current rendering line) resets to zero. A few games rely on this behavior, namely Mr. Do! When LY
            # is reset to zero, no LYC check is done, so no STAT interrupt happens either.
            # 2. The LCD clock is reset to zero as far as I can tell.
            # 3. I believe the LCD enters Mode 0.
            self.clock = 0
            self.clock_target = 0
            self._cycles_to_frame = 0
            self.stat_irq_delayed = False
            self._STAT.set_mode(0)
            self.renderer.dot_ly = -1
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
            if self.lyc_changed_while_disabled:
                if not self.cgb:
                    self.stat_mode_override = True
                self.lyc_changed_while_disabled = False
            if self._STAT.value & 0x40:
                return self._STAT.update_LYC(self.LYC, self.LY)

        return 0

    def write_lcdc(self, value):
        old_lcdc = self._LCDC.value
        lcd_interrupt = self.set_lcdc(value)
        # DMG: disabling sprites while a fetch session is in
        # progress aborts the fetch, and the pixel mixer resumes
        # on the write dot
        if (
            not self.cgb
            and old_lcdc & 0b10
            and not value & 0b10
            and self._STAT._mode == 3
            and self.renderer.dot_ly == self.LY
            and self.renderer.dot_sprite_session_dots > 0
        ):
            self.renderer.dot_abort_sprite_session()
        # An OBJ size change landing exactly on the sprite
        # fetcher's bitplane read dots is observed by those reads
        if (value ^ old_lcdc) & 0b100:
            if (self._STAT._mode == 3 or self._STAT._mode == 0) and self.renderer.dot_ly == self.LY:
                self.renderer.dot_relatch_sprite_size()
        # Latch mid-scanline LCDC write effects for the dot renderer
        if self._LCDC.lcd_enable and self._STAT._mode == 3 and self.renderer.dot_ly == self.LY:
            if self._is_cgb_hardware():
                if self.speed_shift:
                    # CGB double speed: any tile data select toggle glitches the fetcher for 2 dots
                    if (value ^ old_lcdc) & 0b1_0000:
                        self.renderer.dot_tiledata_glitch_dots = 2
                elif ~value & old_lcdc & 0b1_0000:
                    # CGB single speed: clearing tile data select glitches the fetcher for 1 dot
                    self.renderer.dot_tiledata_glitch_dots = 1
            elif old_lcdc & 0b10_0000 and not value & 0b10_0000 and self.renderer.dot_fetching_window:
                # DMG: disabling the window mid-fetch stops pixel insertion for the current fetch
                self.renderer.dot_win_glitch_blocked = True
        # DMG: clearing the BG enable bit blanks the pixel output on
        # the exact dot of the write, but only for a pixel colored
        # in a later phase of its dot: the first pixel of the line
        # (the mixer is stalled at line start and outputs as soon as
        # the fetcher delivers, after the write lands) and the first
        # pixel after a mid-line FIFO stall. Normal dots color the
        # pixel before the write lands, keeping the old value.
        # Setting the bit does not restore the current dot's pixel.
        # The final pixels of the line are colored a few dots into
        # HBlank, so the write can also land in mode 0.
        if (
            not self.cgb
            and old_lcdc & 0b1
            and not value & 0b1
            and (self._STAT._mode == 3 or self._STAT._mode == 0)
            and self.renderer.dot_ly == self.LY
            and self.renderer.dot_last_pixel_dot == self.renderer.dot_dots_elapsed
            and (self.renderer.dot_last_pixel_x == 0 or self.renderer.dot_last_pixel_stalled_recovery)
            and self.renderer.dot_last_pixel_raw >= 0
            and self.renderer.dot_last_pixel_sprite_raw < 0
        ):
            self.renderer._screenbuffer[self.LY, self.renderer.dot_last_pixel_x] = self.BGP.getcolor(0)
            self.renderer._screenbuffer_attributes[self.LY, self.renderer.dot_last_pixel_x] |= 0b01  # COL0_FLAG
            self.renderer.dot_last_pixel_raw = 0
        # DMG: clearing the OBJ enable bit suppresses a sprite pixel
        # mixed into the output on the exact dot of the write, under
        # the same first-pixel-of-line / post-stall condition as the
        # BG enable case above.
        if (
            not self.cgb
            and old_lcdc & 0b10
            and not value & 0b10
            and (self._STAT._mode == 3 or self._STAT._mode == 0)
            and self.renderer.dot_ly == self.LY
            and self.renderer.dot_last_pixel_dot == self.renderer.dot_dots_elapsed
            and (self.renderer.dot_last_pixel_x == 0 or self.renderer.dot_last_pixel_stalled_recovery)
            and self.renderer.dot_last_pixel_sprite_raw >= 0
        ):
            _raw = self.renderer.dot_last_pixel_raw
            self.renderer._screenbuffer[self.LY, self.renderer.dot_last_pixel_x] = self.BGP.getcolor(_raw)
            self.renderer._screenbuffer_attributes[self.LY, self.renderer.dot_last_pixel_x] = (
                0b01 if _raw == 0 else 0  # COL0_FLAG
            )
            self.renderer.dot_last_pixel_sprite_raw = -1
        return lcd_interrupt

    def write_bgp(self, value):
        old_bgp = self.BGP.get()
        self.BGP.set(value)
        # DMG write glitch: a mid-scanline BGP write recolors the
        # pixel colored on the exact dot of the write with the
        # bitwise OR of the old and new palette shades. The final
        # pixels of the line are colored a few dots into HBlank,
        # so the write can also land while STAT already reads
        # mode 0.
        if (
            not self.cgb
            and (self._STAT._mode == 3 or self._STAT._mode == 0)
            and self.renderer.dot_ly == self.LY
            and self.renderer.dot_last_pixel_dot == self.renderer.dot_dots_elapsed
            and self.renderer.dot_last_pixel_raw >= 0
            and self.renderer.dot_last_pixel_sprite_raw < 0
        ):
            raw = self.renderer.dot_last_pixel_raw
            # The glitch ORs the old and new 2-bit color values
            shade = ((old_bgp >> (raw << 1)) & 3) | ((value >> (raw << 1)) & 3)
            self.renderer._screenbuffer[self.LY, self.renderer.dot_last_pixel_x] = self.BGP.palette_mem_rgb[shade]

    def write_obp(self, index, value):
        if index == 0:
            self.OBP0.set(value)
        else:
            self.OBP1.set(value)
        # The pixel mixer reads the palette at output time, so a
        # sprite pixel output on the exact dot of an OBP write
        # must observe the new palette. The write lands after the
        # LCD tick that rendered that dot, so recolor it here.
        if (
            not self.cgb
            and (self._STAT._mode == 3 or self._STAT._mode == 0)
            and self.renderer.dot_ly == self.LY
            and self.renderer.dot_last_pixel_dot == self.renderer.dot_dots_elapsed
            and self.renderer.dot_last_pixel_sprite_palette == index
        ):
            if index == 0:
                self.renderer._screenbuffer[self.LY, self.renderer.dot_last_pixel_x] = self.OBP0.getcolor(
                    self.renderer.dot_last_pixel_sprite_raw
                )
            else:
                self.renderer._screenbuffer[self.LY, self.renderer.dot_last_pixel_x] = self.OBP1.getcolor(
                    self.renderer.dot_last_pixel_sprite_raw
                )

    def write_wy(self, value):
        self.WY = value
        # The WY==LY window condition is re-evaluated when WY is
        # written (SameBoy schedules a wy_check on every WY write)
        if self._LCDC.lcd_enable and self._LCDC.window_enable and self.WY == self.LY:
            self.renderer.wy_activated_frame = True

    def write_wx(self, value):
        self.WX = value
        if (
            not self._is_cgb_hardware()
            and self._LCDC.lcd_enable
            and self._STAT._mode == 3
            and self.renderer.dot_ly == self.LY
        ):
            # DMG: a WX write takes effect for one dot, even mid-fetch
            self.renderer.dot_wx_changed_dots = 1

    def _is_cgb_hardware(self):
        return self.cgb or self._downgraded_to_dmg

    def _is_startup_mode2_delay(self):
        return self.first_frame and self.stat_transition == STAT_TRANSITION_START_MODE2

    def _should_pretrigger_vblank_stat(self):
        return (
            self._is_cgb_hardware()
            and self._LCDC.lcd_enable
            and self.LY == 143
            and self._STAT._mode == 0
            and self.next_stat_mode == 1
            and self._STAT.value & 0x20
            and not self._STAT._irq_line
        )

    def _mode3_sprite_penalty(self, ly):
        if not self._LCDC.sprite_enable:
            return 0

        spriteheight = 16 if self._LCDC.sprite_height else 8
        spritecount = 0
        group_count = 0
        penalty = 0
        seen_x0 = 0
        seen_x1 = 0
        seen_x2 = 0
        for index in range(0, OBJECT_ATTRIBUTE_MEMORY, 4):
            y = self.OAM[index] - 16
            if y <= ly < y + spriteheight:
                x = self.OAM[index + 1]
                if x < 168:
                    penalty += 6
                    # Keep X-group bookkeeping local; the renderer's sprite list is live state.
                    x_mask = 1
                    if x < 64:
                        x_mask <<= x
                        duplicate = (seen_x0 & x_mask) != 0
                        seen_x0 |= x_mask
                    elif x < 128:
                        x_mask <<= x - 64
                        duplicate = (seen_x1 & x_mask) != 0
                        seen_x1 |= x_mask
                    else:
                        x_mask <<= x - 128
                        duplicate = (seen_x2 & x_mask) != 0
                        seen_x2 |= x_mask

                    if not duplicate:
                        group_count += 1
                        alignment = 5 - ((x + self.SCX - 8) & 7)
                        if alignment > 0:
                            penalty += alignment

                spritecount += 1
                if spritecount == 10:
                    break

        if spritecount and not group_count:
            # A line with only off-screen objects skips one machine cycle of mode-3 startup.
            return -4
        if not spritecount:
            return 0

        # The first seven dots of object fetching overlap the fixed mode-3 startup.
        penalty = max(0, penalty - 7)
        if self._is_cgb_hardware():
            penalty = (penalty + 3) // 4 * 4
        return penalty

    def _mode3_timing_adjustment(self, ly):
        penalty = self._mode3_sprite_penalty(ly)
        if not self.first_frame and not self._is_cgb_hardware():
            penalty += ((self.SCX & 7) + 3) // 4 * 4
        return penalty

    def cycles_to_mode0(self):
        mode = self._STAT._mode & 0b11
        remainder = self.clock_target - self.clock

        if mode == 0:
            return 0
        elif mode == 3:
            return remainder

        mode2 = 80
        cgb_hardware = self._is_cgb_hardware()
        sprite_line = 0 if mode == 1 else self.LY
        mode3_adjustment = self._mode3_timing_adjustment(sprite_line)
        normal_mode3 = 170 + mode3_adjustment if cgb_hardware else 172 + mode3_adjustment

        if mode == 2:
            mode3 = 172 + mode3_adjustment if self.first_frame else normal_mode3
            return remainder + mode3
        elif mode == 1:
            remaining_ly = 153 - self.LY
            return remainder + 456 * remaining_ly + mode2 + normal_mode3
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

        # Feed the dot-accurate renderer with the dots that have elapsed on the
        # current mode 3 line. Register writes land between LCD ticks, so the
        # dots processed here observe the current register values.
        if self._LCDC.lcd_enable and self._STAT._mode == 3 and self.renderer.dot_ly == self.LY:
            self.renderer.advance_dots(self.clock - self.mode3_start_clock - DOT_MODE3_RENDER_DELAY)

        if self._LCDC.lcd_enable and self._STAT._mode == 0 and self.renderer.dot_ly == self.LY:
            # The pixel pipeline pushes the last pixels of the line a few dots
            # after the STAT mode-0 signal. Keep feeding it during early
            # HBlank so register writes land dot-synchronously on those pops,
            # exactly as they do in mode 3.
            self.renderer.advance_dots(self.clock - self.mode3_start_clock - DOT_MODE3_RENDER_DELAY)
            if self.renderer.dot_x_counter == 160:
                # The pipeline reached its natural end; present the line
                self.renderer.dot_finish_line()
                self.renderer.dot_ly = -1

        if (
            self._LCDC.lcd_enable
            and self._STAT._mode == 3
            and self.next_stat_mode == 0
            and self.renderer.dot_ly == self.LY
            and not self.renderer.dot_mode0_fetcher_based
            and self.renderer.dot_mode0_elapsed >= 0
            and self.renderer.dot_mode0_elapsed != self.renderer.dot_mode0_corrected
        ):
            # The pixel pipeline just popped the pixel at screen column 157,
            # where hardware lowers the STAT mode-0 signal. The mode-3 target
            # was only an analytic estimate until now; correct it to the exact
            # dot so STAT reads observe the transition dot-accurately instead
            # of on the 4-dot extension grid. The correction is applied once
            # per popped value; a mode-3 extension may have already pushed the
            # target past a stale estimate, which must not snap it back.
            exact_target = self.mode3_start_clock + self.renderer.dot_mode0_elapsed + DOT_MODE3_RENDER_DELAY
            if exact_target != self.clock_target:
                self.mode3_extension += exact_target - self.clock_target
                self.clock_target = exact_target
            self.renderer.dot_mode0_corrected = self.renderer.dot_mode0_elapsed

        vblank_stat_pretriggered = False

        if self._should_pretrigger_vblank_stat() and self.clock >= self.clock_target - 4:
            # CGB hardware keeps this timing after switching to DMG compatibility mode.
            self.stat_transition = STAT_TRANSITION_VBLANK_PRETRIGGERED
            interrupt_flag |= INTR_LCDC

        if self.clock >= self.clock_target:
            if self._LCDC.lcd_enable and self.reset:
                self.reset = False
                self.frame_done = True

                self.LY = 0
                self.clock = 0
                # LCD startup begins in mode 0 and skips the initial mode 2.
                self.clock_target = 76
                self.next_stat_mode = 3
                self.stat_transition = STAT_TRANSITION_NONE
                interrupt_flag |= self._STAT.set_mode(0)
                # The window activation latch only sets when the window is
                # enabled at the WY==LY comparison (SameBoy wy_check)
                self.renderer.wy_activated_frame = self._LCDC.window_enable and self.WY == self.LY
                interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

            elif self._LCDC.lcd_enable and self.LY == 153:
                # The dot renderer's pipeline state is dead once the frame
                # wraps; neutralize it so a state saved here loads into a
                # fresh renderer identically. The mode-3 anchors are dead
                # too; the next mode 3 recomputes them.
                self.renderer.reset_dot_pipeline()
                self.mode3_start_clock = 0
                self.mode3_extension = 0
                if self.first_frame and self.clock_target < FRAME_CYCLES:
                    # The startup line is eight cycles short; keep the frame period unchanged.
                    self.clock_target = FRAME_CYCLES
                else:
                    self.frame_done = True
                    self.LY = 0
                    self.clock %= FRAME_CYCLES
                    self.first_frame = False
                    self.clock_target = self.clock_target % FRAME_CYCLES + 80
                    self.next_stat_mode = 3
                    self.stat_transition = STAT_TRANSITION_NONE
                    # The OAM STAT interrupt source triggers one dot before STAT
                    # changes to mode 2 on every line except line 0, which skips
                    # the early trigger and fires at the mode change (frame dot 0)
                    # instead. A CPU M-cycle boundary landing exactly on the
                    # trigger does not observe the interrupt, so the dispatch to
                    # the CPU is quantized to the next boundary. The clock was
                    # wrapped to the CPU overshoot above, so a delivery clock of
                    # 1 delivers within the same tick when the boundary is
                    # already past the trigger, and on the next boundary otherwise.
                    stat_irq = self._STAT.set_mode(2)
                    if stat_irq & INTR_LCDC:
                        self.stat_irq_delayed = True
                        self.stat_irq_delivery_clock = 1
                    else:
                        interrupt_flag |= stat_irq
                    self.renderer.wy_activated_frame = self._LCDC.window_enable and self.WY == self.LY
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

            elif self._LCDC.lcd_enable and self.stat_transition == STAT_TRANSITION_ADVANCE_LY:
                self.LY += 1
                if self.first_frame:
                    # Clear coincidence now, then compare again when mode 2 starts.
                    self._STAT.value &= 0xFB
                    interrupt_flag |= self._STAT._update_irq_line()
                else:
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                self.clock_target += 4
                self.stat_transition = STAT_TRANSITION_START_MODE2

            elif self._LCDC.lcd_enable and self.stat_transition == STAT_TRANSITION_START_MODE2:
                interrupt_flag |= self._STAT.set_mode(2)
                if self.first_frame:
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                self.clock_target += 80
                self.next_stat_mode = 3
                self.stat_transition = STAT_TRANSITION_NONE
                self.renderer.wy_activated_frame = self.renderer.wy_activated_frame | (
                    self._LCDC.window_enable and self.WY == self.LY
                )

            elif (
                self._LCDC.lcd_enable
                and self.next_stat_mode == 0
                and not self.renderer.dot_mode0_fetcher_based
                and self.renderer.dot_ly == self.LY
                and self.renderer.dot_x_counter != 160
                and self.mode3_extension < 116
                and (
                    self.renderer.dot_mode0_elapsed < 0
                    or self.renderer.dot_sprite_session_dots > 0
                    or self.renderer.dot_during_sprite_fetch
                    or (
                        self.renderer.dot_n_sprites > 0
                        and (self._LCDC.sprite_enable or self._is_cgb_hardware())
                        and self.renderer.dot_sprite_x[self.renderer.dot_n_sprites - 1] <= 167
                    )
                )
            ):
                # The dot renderer's pixel pipeline is still emitting this
                # line's pixels, or a sprite fetch session is still pending.
                # Hardware remains in mode 3 until the last pixel is pushed,
                # so extend mode 3 to the renderer's natural end and shorten
                # HBlank by the same amount. The extension is capped so a
                # stalled pipeline cannot lock up the LCD. Sprites at X >= 168
                # never enter the fetch pipeline and must not extend mode 3.
                self.mode3_extension += 4
                self.clock_target += 4

            elif self._LCDC.lcd_enable:
                # Change to next mode
                if self.stat_transition == STAT_TRANSITION_VBLANK_PRETRIGGERED:
                    self.stat_transition = STAT_TRANSITION_NONE
                    vblank_stat_pretriggered = True
                stat_irq = self._STAT.set_mode(self.next_stat_mode)
                if self.next_stat_mode == 1 and stat_irq & INTR_LCDC:
                    # The mode 1 STAT interrupt triggers at the STAT change
                    # itself, with no early trigger like mode 2 has on lines
                    # 1-152. A CPU M-cycle boundary coinciding with the
                    # trigger therefore does not observe it, so the dispatch
                    # is quantized to the next boundary: a boundary already
                    # past the trigger delivers on the current tick, and an
                    # exact hit delivers on the next tick.
                    self.stat_irq_delayed = True
                    self.stat_irq_delivery_clock = self.clock_target + 1
                else:
                    interrupt_flag |= stat_irq

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
                    self.stat_transition = STAT_TRANSITION_NONE
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)
                    # If this condition is not met in mode 2, at some point in this
                    # frame, the window will not show.
                    # FIXME: Strange Cython work-around. I thought I had fixed this.
                    self.renderer.wy_activated_frame = self.renderer.wy_activated_frame | (
                        self._LCDC.window_enable and self.WY == self.LY
                    )
                elif self._STAT._mode == 3:
                    self.mode3_start_clock = self.clock_target
                    # The dot renderer's pipeline produces the sprite and
                    # SCX mode-3 penalties naturally. The analytic estimate
                    # could overshoot the pipeline's natural finish and cut
                    # mode 3 short, so start from the unadjusted base
                    # length and let the pipeline extend it.
                    self.mode3_extension = 0
                    if self.first_frame:
                        self.clock_target += 172
                    elif self._is_cgb_hardware():
                        self.clock_target += 170
                    else:
                        self.clock_target += 172
                    self.next_stat_mode = 0
                    self.stat_transition = STAT_TRANSITION_NONE
                    self.renderer.start_dot_line(self.LY)
                    if self.renderer.dot_mode0_fetcher_based:
                        # The fetcher-based mode-0 dot is exact, so apply it
                        # directly and shorten HBlank by the same amount. The
                        # pixel pipeline may still be emitting this line's
                        # pixels when mode 0 arrives; it keeps running into
                        # HBlank exactly as it does on hardware.
                        # The mode-0 dot is the plain-line dot plus every
                        # sprite fetch session dot, minus the session dots
                        # that overlap the fixed mode-3 startup. CGB mode 3
                        # starts two dots further into the fetcher's work, so
                        # two fewer session dots overlap it. The STAT mode-0
                        # signal itself lags the last fetcher dot by one,
                        # which is folded into the overlap.
                        if not self.first_frame and self._is_cgb_hardware():
                            startup_overlap = 1
                        else:
                            startup_overlap = 3
                        penalty = self.renderer.dot_sprite_mode0_penalty(startup_overlap)
                        self.mode3_extension = penalty
                        self.clock_target += penalty
                elif self._STAT._mode == 0:  # HBLANK
                    if self.first_frame:
                        self.clock_target += 200 - self.mode3_extension
                        if self.LY < 143:
                            self.next_stat_mode = 2
                            self.stat_transition = STAT_TRANSITION_ADVANCE_LY
                        else:
                            self.next_stat_mode = 1
                            self.stat_transition = STAT_TRANSITION_NONE
                    elif self._is_cgb_hardware():
                        self.clock_target += 206 - self.mode3_extension
                        self.next_stat_mode = 2 if self.LY < 143 else 1
                        self.stat_transition = STAT_TRANSITION_NONE
                    elif self.LY < 143:
                        self.clock_target += 200 - self.mode3_extension
                        self.next_stat_mode = 2
                        self.stat_transition = STAT_TRANSITION_ADVANCE_LY
                    else:
                        self.clock_target += 204 - self.mode3_extension
                        self.next_stat_mode = 1
                        self.stat_transition = STAT_TRANSITION_NONE

                    # Recorded for API
                    bx, by = self.getviewport()
                    wx, wy = self.getwindowpos()
                    self._scanlineparameters[self.LY][0] = bx
                    self._scanlineparameters[self.LY][1] = by
                    self._scanlineparameters[self.LY][2] = wx + 7
                    self._scanlineparameters[self.LY][3] = wy
                    self._scanlineparameters[self.LY][4] = self._LCDC.tiledata_select

                    # The dot renderer's pixel pipeline is still pushing
                    # the last pixels of this line. It completes during
                    # early HBlank in tick(), dot-synchronously with the
                    # CPU, so that register writes on the final pop dots
                    # are observed at the exact dots as on hardware.
                elif self._STAT._mode == 1:  # VBLANK
                    self.clock_target += 456
                    self.next_stat_mode = 1
                    self.stat_transition = STAT_TRANSITION_NONE

                    self.LY += 1
                    interrupt_flag |= self._STAT.update_LYC(self.LYC, self.LY)

                    if self.LY == 144:
                        if self._STAT.value & 0x20 and not self._STAT._irq_line and not vblank_stat_pretriggered:
                            interrupt_flag |= INTR_LCDC
                        interrupt_flag |= INTR_VBLANK
                        self.renderer.wy_activated_frame = False
                        if self.first_frame:
                            # Pan Docs: https://gbdev.io/pandocs/LCDC.html#lcdc7--lcd-enable
                            # When re-enabling the LCD, the PPU will immediately start drawing again, but the screen
                            # will stay blank during the first frame.
                            self.renderer.blank_screen()
            else:
                # See also `self.set_lcdc`
                self.frame_done = True
                self.clock %= FRAME_CYCLES
                self.clock_target = FRAME_CYCLES

                # Renderer
                self.renderer.blank_screen()

        if self.stat_irq_delayed and self.clock >= self.stat_irq_delivery_clock:
            self.stat_irq_delayed = False
            interrupt_flag |= INTR_LCDC

        # NOTE: speed_shift because they are using in externally in mb
        cycles_to_interrupt = self.clock_target - self.clock
        if self._should_pretrigger_vblank_stat():
            cycles_to_interrupt -= 4
        if self.stat_irq_delayed:
            cycles_to_interrupt = min(cycles_to_interrupt, self.stat_irq_delivery_clock - self.clock)
        self._cycles_to_interrupt = cycles_to_interrupt << self.speed_shift
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
        f.write(self.object_priority_mode)

        for y in range(ROWS):
            f.write(self._scanlineparameters[y][0])
            f.write(self._scanlineparameters[y][1])
            # We store (WX + 7). We added 7 earlier to make it easier to serialize
            f.write(self._scanlineparameters[y][2])
            f.write(self._scanlineparameters[y][3])
            f.write(self._scanlineparameters[y][4])

        f.write(self.cgb)
        f.write(self._downgraded_to_dmg)
        f.write(self.speed_shift)
        f.write(self.frame_done)
        f.write(self.first_frame)
        f.write(self.reset)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self.clock)
        f.write_64bit(self.clock_target)
        f.write(self.next_stat_mode)
        f.write(self.stat_transition)

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
        if state_version >= 16:
            # See motherboard before version 16
            self.object_priority_mode = f.read()

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
            if state_version >= 17:
                self._downgraded_to_dmg = f.read()
                if self._downgraded_to_dmg:
                    logger.debug("Load-state from downgraded CGB renderer to DMG renderer")
                    self.renderer.cgb = False

            if self._downgraded_to_dmg and _cgb:
                raise PyBoyException("LCD was supposed to be downgraded!")
            elif not self._downgraded_to_dmg:
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
            self.stat_transition = f.read()
            if (
                self._should_pretrigger_vblank_stat()
                and self.clock <= self.clock_target
                and self.clock_target - self.clock >= 4
            ):
                self._cycles_to_interrupt -= 4 << self.speed_shift

            if self.cgb:
                for n in range(VIDEO_RAM):
                    self.VRAM1[n] = f.read()
                self.vbk.active_bank = f.read()
                self.bcps.load_state(f, state_version)
                self.bcpd.load_state(f, state_version)
                self.ocps.load_state(f, state_version)
                self.ocpd.load_state(f, state_version)

        # The dot-accurate renderer cannot resume a partially rendered line
        self.renderer.dot_ly = -1

    def getwindowpos(self):
        return (self.WX - 7, self.WY)

    def getviewport(self):
        return (self.SCX, self.SCY)


class PaletteRegister:
    def __init__(self, value, palette):
        self.value = 0
        self.lookup = [0] * 4

        self.set_palette_colors(palette)
        self.set(value)

    def set(self, value):
        # Pokemon Blue continuously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        self._update_lookup()
        return True

    def set_palette_colors(self, palette):
        self.palette_mem_rgb = [(rgb_to_bgr(c)) for c in palette]
        self._update_lookup()

    def _update_lookup(self):
        for x in range(4):
            self.lookup[x] = self.palette_mem_rgb[(self.value >> x * 2) & 0b11]

    def get(self):
        return self.value

    def getcolor(self, i):
        return self.lookup[i]


class STATRegister:
    def __init__(self):
        self.value = 0b1000_0000
        self._mode = 0
        self._irq_line = False

    def set(self, value):
        value &= 0b0111_1000  # Bit 7 is always set, and bit 0-2 are read-only
        self.value &= 0b1000_0111  # Preserve read-only bits and clear the rest
        self.value |= value  # Combine the two
        return self._update_irq_line()

    def update_LYC(self, LYC, LY):
        # WARNING: Only call when LCD is enabled!
        if LYC == LY:
            self.value |= 0b100  # Sets the LYC flag
        else:
            # Clear LYC flag
            self.value &= 0b1111_1011
        return self._update_irq_line()

    def set_mode(self, mode):
        if self._mode == mode:
            # Mode already set
            return 0

        self._mode = mode
        self.value &= 0b11111100  # Clearing 2 LSB
        self.value |= mode  # Apply mode to LSB
        return self._update_irq_line()

    def _update_irq_line(self):
        mode_irq = self._mode != 3 and self.value & (1 << (self._mode + 3))
        lyc_irq = self.value & 0x44 == 0x44
        irq_line = mode_irq or lyc_irq
        interrupt = INTR_LCDC if irq_line and not self._irq_line else 0
        self._irq_line = irq_line
        return interrupt

    def save_state(self, f):
        f.write(self.value)

    def load_state(self, f, state_version):
        value = f.read()
        self.value = value
        self._mode = value & 0b11
        self._irq_line = False
        self._update_irq_line()


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
    def __init__(self, lcd, cgb):
        self.lcd = lcd
        self.cgb = cgb
        self.color_format = "RGBA"

        self.buffer_dims = (ROWS, COLS)

        # Init buffers as white
        self._screenbuffer_raw = array("B", [0x00] * (ROWS * COLS * 4))
        self._screenbuffer_attributes_raw = array("B", [0x00] * (ROWS * COLS))
        self._tilecache_raw = array("B", [0x00] * (TILES * 8 * 8 * 2))
        self._spritecache_raw = array("B", [0x00] * (TILES * 8 * 8 * 2))
        self.sprites_to_render = array("i", [0] * 10)

        # Allocate both cache 0 and 1. Even on DMG, where tilecache[0] is only used.
        self._tilecache_state = array("B", [0] * TILES * 2)
        self._spritecache_state = array("B", [0] * TILES * 2)
        self.clear_cache()

        self._screenbuffer = memoryview(self._screenbuffer_raw).cast("I", shape=(ROWS, COLS))
        self._screenbuffer_attributes = memoryview(self._screenbuffer_attributes_raw).cast("B", shape=(ROWS, COLS))
        self._tilecache = memoryview(self._tilecache_raw).cast("B", shape=(2, TILES * 8, 8))
        self._tilecache_64 = memoryview(self._tilecache_raw).cast(
            "Q",
            shape=(
                2,
                TILES * 8,
            ),
        )

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

        # OBP0 and OBP1 palette
        self._spritecache = memoryview(self._spritecache_raw).cast("B", shape=(2, TILES * 8, 8))
        self._spritecache_64 = memoryview(self._spritecache_raw).cast("Q", shape=(2, TILES * 8))

        self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        # WY has a strange behavior described at:
        # https://gbdev.io/pandocs/Scrolling.html#window
        self.wy_activated_frame = False

        # State for the dot-accurate renderer
        self.dot_ly = -1
        self.dot_dots_elapsed = 0
        self.dot_mode0_elapsed = -1
        self.dot_mode0_corrected = -1
        self.dot_mode0_fetcher_based = False
        self.dot_x_counter = 240
        self.dot_screen_x = 0
        self.dot_fetch_phase = 0
        self.dot_tile_index = 0
        self.dot_tile_attrs = 0
        self.dot_tile_data_low = 0
        self.dot_tile_data_high = 0
        self.dot_tilemap_addr = 0
        self.dot_tiledata_addr = 0
        self.dot_window_triggered = False
        self.dot_fetching_window = False
        self.dot_window_column = 0
        self.dot_window_line = 0
        self.dot_x_counter_fractional = False
        self.dot_bg_insert_pending = False
        self.dot_win_glitch_blocked = False
        self.dot_last_pixel_dot = -1
        self.dot_last_pixel_x = 0
        self.dot_last_pixel_raw = -1
        self.dot_last_pixel_sprite_raw = -1
        self.dot_last_pixel_sprite_palette = -1
        self.dot_mixer_stalled = False
        self.dot_last_pixel_stalled_recovery = False
        self.dot_bg_fifo_pixel = array("B", [0] * 8)
        self.dot_bg_fifo_palette = array("B", [0] * 8)
        self.dot_bg_fifo_priority = array("B", [0] * 8)
        self.dot_bg_fifo_count = 0
        self.dot_bg_fifo_read = 0
        self.dot_obj_fifo_pixel = array("B", [0] * 8)
        self.dot_obj_fifo_palette = array("B", [0] * 8)
        self.dot_obj_fifo_priority = array("B", [0] * 8)
        self.dot_obj_fifo_bg_priority = array("B", [0] * 8)
        self.dot_obj_fifo_count = 0
        self.dot_obj_fifo_read = 0
        self.dot_sprite_x = array("B", [0] * 10)
        self.dot_sprite_y = array("B", [0] * 10)
        self.dot_sprite_index = array("i", [0] * 10)
        self.dot_n_sprites = 0
        self.dot_sprite_fetch_tile = 0
        self.dot_sprite_fetch_flags = 0
        self.dot_sprite_fetch_data_low = 0
        self.dot_sprite_fetch_data_high = 0
        self.dot_sprite_fetch_row_addr = 0
        self.dot_sprite_merge_pending = False
        self.dot_sprite_merge_priority = 0
        self.dot_sprite_merge_y = 0
        self.dot_sprite_low_read_dot = -1
        self.dot_sprite_high_read_dot = -1
        self.dot_during_sprite_fetch = False
        self.dot_sprite_session_dots = 0
        self.dot_sprite_session_count = 0
        self.dot_sprite_session_low = 0
        self.dot_sprite_session_high = 0
        self.dot_session_overlap_dots = 3
        self.dot_glitch_data = 0
        self.dot_latched_tiledata_select = False
        self.dot_tiledata_glitch_dots = 0
        self.dot_cgb_window_glitch = False
        self.dot_wx_changed_dots = 0
        self.dot_window_extra_dot_pending = False

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

    def scanline_sprites(self, ly, buffer, buffer_attributes, ignore_priority):
        if not self.lcd._LCDC.sprite_enable or self.lcd.disable_renderer:
            return

        # Find the first 10 sprites in OAM that appears on this scanline.
        # The lowest X-coordinate has priority, when overlapping
        spriteheight = 16 if self.lcd._LCDC.sprite_height else 8
        sprite_count = 0
        for n in range(0x00, OBJECT_ATTRIBUTE_MEMORY, 4):
            y = self.lcd.OAM[n] - 16  # Documentation states the y coordinate needs to be subtracted by 16
            x = self.lcd.OAM[n + 1] - 8  # Documentation states the x coordinate needs to be subtracted by 8

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
            y = self.lcd.OAM[n] - 16  # Documentation states the y coordinate needs to be subtracted by 16
            x = self.lcd.OAM[n + 1] - 8  # Documentation states the x coordinate needs to be subtracted by 8
            tileindex = self.lcd.OAM[n + 2]
            if spriteheight == 16:
                tileindex &= 0b11111110
            attributes = self.lcd.OAM[n + 3]
            xflip = attributes & 0b00100000
            yflip = attributes & 0b01000000
            spritepriority = (attributes & 0b10000000) and not ignore_priority
            sprite_cache_no = 0
            if self.cgb:
                palette = attributes & 0b111
                if attributes & 0b1000:
                    sprite_cache_no = 1
            else:
                # Fake palette index
                palette = 0
                if attributes & 0b10000:
                    sprite_cache_no = 1

            self.update_spritecache(sprite_cache_no, self.lcd, tileindex, sprite_cache_no if self.cgb else 0)
            if self.lcd._LCDC.sprite_height:
                self.update_spritecache(sprite_cache_no, self.lcd, tileindex + 1, sprite_cache_no if self.cgb else 0)

            dy = ly - y
            yy = spriteheight - dy - 1 if yflip else dy

            for dx in range(8):
                xx = 7 - dx if xflip else dx
                color_code = self._spritecache[sprite_cache_no, 8 * tileindex + yy, xx]
                if 0 <= x < COLS and not color_code == 0:  # If pixel is not transparent
                    if self.cgb:
                        pixel = self.lcd.ocpd.getcolor(palette, color_code)
                        bgmappriority = buffer_attributes[ly, x] & BG_PRIORITY_FLAG

                        if (
                            self.lcd._LCDC.cgb_master_priority
                        ):  # If 0, sprites are always on top, if 1 follow priorities
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
                            pixel = self.lcd.OBP1.getcolor(color_code)
                        else:
                            pixel = self.lcd.OBP0.getcolor(color_code)

                        if spritepriority:  # If 1, sprite is behind bg/window. Color 0 of window/bg is transparent
                            if buffer_attributes[ly, x] & COL0_FLAG:  # if BG pixel is transparent
                                buffer[ly, x] = pixel
                        else:
                            buffer[ly, x] = pixel
                x += 1
            x -= 8

    def clear_cache(self):
        self.clear_tilecache(0)
        if self.cgb:
            self.clear_tilecache(1)
        self.clear_spritecache(0)
        self.clear_spritecache(1)

    def invalidate_tile(self, tile, vbank):
        # TODO: Is this right?
        if vbank and self.cgb:
            self._tilecache_state[tile] = 0
            self._tilecache_state[tile + TILES] = 0
            self._spritecache_state[tile] = 0
            self._spritecache_state[tile + TILES] = 0
        else:
            self._tilecache_state[tile] = 0
            if self.cgb:
                self._tilecache_state[tile + TILES] = 0
            self._spritecache_state[tile] = 0
            self._spritecache_state[tile + TILES] = 0

    def clear_tilecache(self, cache_no):
        for i in range(TILES):
            self._tilecache_state[i + (TILES if cache_no else 0)] = 0

    def clear_spritecache(self, cache_no):
        for i in range(TILES):
            self._spritecache_state[i + (TILES if cache_no else 0)] = 0

    def update_tilecache(self, cache_no, lcd, t, bank):
        if self._tilecache_state[t + (TILES if cache_no else 0)]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            if self.cgb and bank:
                byte1 = lcd.VRAM1[t * 16 + k]
                byte2 = lcd.VRAM1[t * 16 + k + 1]
            else:
                byte1 = lcd.VRAM0[t * 16 + k]
                byte2 = lcd.VRAM0[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._tilecache_64[cache_no, y] = self.colorcode(byte1, byte2)

        self._tilecache_state[t + (TILES if cache_no else 0)] = 1

    def update_spritecache(self, cache_no, lcd, t, bank):
        if self._spritecache_state[t + (TILES if cache_no else 0)]:
            return
        # for t in self.tiles_changed0:
        for k in range(0, 16, 2):  # 2 bytes for each line
            if self.cgb and bank:
                byte1 = lcd.VRAM1[t * 16 + k]
                byte2 = lcd.VRAM1[t * 16 + k + 1]
            else:
                byte1 = lcd.VRAM0[t * 16 + k]
                byte2 = lcd.VRAM0[t * 16 + k + 1]
            y = (t * 16 + k) // 2

            self._spritecache_64[cache_no, y] = self.colorcode(byte1, byte2)

        self._spritecache_state[t + (TILES if cache_no else 0)] = 1

    def colorcode(self, byte1, byte2):
        colorcode_low = self.colorcode_table[(byte1 & 0xF) | ((byte2 & 0xF) << 4)]
        colorcode_high = self.colorcode_table[((byte1 >> 4) & 0xF) | (byte2 & 0xF0)]
        return (colorcode_low << 32) | colorcode_high

    def blank_screen(self):
        # If the screen is off, fill it with a color.
        for y in range(ROWS):
            for x in range(COLS):
                self._screenbuffer[y, x] = self.lcd.BGP.getcolor(0)
                self._screenbuffer_attributes[y, x] = 0

    def save_state(self, f):
        for y in range(ROWS):
            for x in range(COLS):
                f.write_32bit(self._screenbuffer[y, x])
                f.write(self._screenbuffer_attributes[y, x])
        f.write(self.wy_activated_frame)

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

        if state_version >= 18:
            self.wy_activated_frame = f.read()

        self.clear_cache()

    def reset_dot_pipeline(self):
        # Neutralize the dot renderer between frames. Everything below is
        # either reset again at the start of the next line or only read
        # while a line is being rendered, so a running renderer and a
        # freshly constructed one hold the same state here. A state file
        # saved at a frame boundary therefore loads into a renderer that
        # continues identically.
        self.dot_ly = -1
        self.dot_dots_elapsed = 0
        self.dot_mode0_elapsed = -1
        self.dot_mode0_corrected = -1
        self.dot_mode0_fetcher_based = False
        self.dot_x_counter = 240
        self.dot_screen_x = 0
        self.dot_fetch_phase = 0
        self.dot_tile_index = 0
        self.dot_tile_attrs = 0
        self.dot_tile_data_low = 0
        self.dot_tile_data_high = 0
        self.dot_tilemap_addr = 0
        self.dot_tiledata_addr = 0
        self.dot_window_triggered = False
        self.dot_fetching_window = False
        self.dot_window_column = 0
        self.dot_window_line = 0
        self.dot_x_counter_fractional = False
        self.dot_bg_insert_pending = False
        self.dot_win_glitch_blocked = False
        self.dot_last_pixel_dot = -1
        self.dot_last_pixel_x = 0
        self.dot_last_pixel_raw = -1
        self.dot_last_pixel_sprite_raw = -1
        self.dot_last_pixel_sprite_palette = -1
        self.dot_mixer_stalled = False
        self.dot_last_pixel_stalled_recovery = False
        self.dot_bg_fifo_count = 0
        self.dot_bg_fifo_read = 0
        self.dot_obj_fifo_count = 0
        self.dot_obj_fifo_read = 0
        for i in range(8):
            self.dot_bg_fifo_pixel[i] = 0
            self.dot_bg_fifo_palette[i] = 0
            self.dot_bg_fifo_priority[i] = 0
            self.dot_obj_fifo_pixel[i] = 0
            self.dot_obj_fifo_palette[i] = 0
            self.dot_obj_fifo_priority[i] = 0
            self.dot_obj_fifo_bg_priority[i] = 0
        self.dot_n_sprites = 0
        for i in range(10):
            self.dot_sprite_x[i] = 0
            self.dot_sprite_y[i] = 0
            self.dot_sprite_index[i] = 0
        self.dot_sprite_fetch_tile = 0
        self.dot_sprite_fetch_flags = 0
        self.dot_sprite_fetch_data_low = 0
        self.dot_sprite_fetch_data_high = 0
        self.dot_sprite_fetch_row_addr = 0
        self.dot_sprite_merge_pending = False
        self.dot_sprite_merge_priority = 0
        self.dot_sprite_merge_y = 0
        self.dot_sprite_low_read_dot = -1
        self.dot_sprite_high_read_dot = -1
        self.dot_during_sprite_fetch = False
        self.dot_sprite_session_dots = 0
        self.dot_sprite_session_count = 0
        self.dot_sprite_session_low = 0
        self.dot_sprite_session_high = 0
        self.dot_session_overlap_dots = 3
        self.dot_glitch_data = 0
        self.dot_latched_tiledata_select = False
        self.dot_tiledata_glitch_dots = 0
        self.dot_cgb_window_glitch = False
        self.dot_wx_changed_dots = 0
        self.dot_window_extra_dot_pending = False

    ####################################
    #
    #  Dot-accurate renderer
    #
    #  Renders a scanline one dot at a time through a fetcher pipeline and two
    #  pixel FIFOs, so that PPU register writes landing mid-scanline produce
    #  the same pixels as hardware. The pipeline follows the documented PPU
    #  design: a background/window fetcher producing rows of 8 pixels, a
    #  sprite fetcher overlaying up to 10 sprites per line, and the SCX/WX
    #  window and scrolling edge cases described in Pan Docs and exercised by
    #  the mealybug tearoom tests.
    #

    def start_dot_line(self, ly):
        if self.dot_ly != -1 and self.dot_ly != ly:
            # Safety net: the previous line's pipeline never reached its
            # natural end (a permanently stalled fetcher). Force it to
            # complete so its pixels are not lost.
            self.advance_dots(456)
            self.dot_finish_line()
            self.dot_ly = -1
        self.dot_ly = ly
        self.dot_dots_elapsed = 0
        self.dot_mode0_elapsed = -1
        self.dot_mode0_corrected = -1
        self.dot_mode0_fetcher_based = False
        self.dot_win_glitch_blocked = False
        self.dot_bg_fifo_count = 0
        self.dot_bg_fifo_read = 0
        self.dot_obj_fifo_count = 0
        self.dot_obj_fifo_read = 0
        # Prime the background FIFO with a blank row. Hardware starts the line
        # with a full FIFO of junk that is discarded off-screen anyway.
        self.dot_fill_bg_fifo(0, 0, 0, False, False)
        self.dot_screen_x = 0
        self.dot_fetch_phase = 0
        self.dot_x_counter = 240
        self.dot_x_counter_fractional = False
        self.dot_bg_insert_pending = False
        self.dot_fetching_window = False
        self.dot_during_sprite_fetch = False
        self.dot_sprite_session_dots = 0
        self.dot_sprite_session_count = 0
        self.dot_sprite_session_low = 0
        self.dot_sprite_session_high = 0
        self.dot_session_overlap_dots = 3
        self.dot_sprite_merge_pending = False
        self.dot_sprite_low_read_dot = -1
        self.dot_sprite_high_read_dot = -1
        self.dot_window_extra_dot_pending = False
        self.dot_tiledata_glitch_dots = 0
        self.dot_wx_changed_dots = 0
        self.dot_last_pixel_dot = -1
        self.dot_last_pixel_sprite_raw = -1
        self.dot_last_pixel_sprite_palette = -1
        self.dot_mixer_stalled = False
        self.dot_last_pixel_stalled_recovery = False
        self.dot_cgb_window_glitch = False
        if ly == 0:
            self.dot_window_line = 255
            self.dot_window_triggered = False
        if not self.lcd._is_cgb_hardware():
            self.dot_tile_attrs = 0
        # OAM scan. Hardware interleaves this with mode 2; doing it up front is
        # an accepted approximation for the dot renderer.
        self.dot_scan_sprites()

        # On a line with sprites to fetch, the STAT mode-0 signal follows the
        # object fetcher's dot counter rather than the pixel pipeline. The
        # fetcher-based mode-0 dot is then known in full from the scan results,
        # so the mode-0 target is computed from them when mode 3 starts, and
        # neither the pixel-pipeline correction nor the mode-3 extension loop
        # may move it afterwards.
        self.dot_mode0_fetcher_based = self.dot_n_sprites > 0 and self.lcd._LCDC.sprite_enable

    def advance_dots(self, target):
        if self.dot_ly < 0 or self.dot_x_counter == 160:
            return
        while self.dot_dots_elapsed < target:
            if self.dot_sprite_merge_pending:
                self._dot_sprite_flush_merge()
            if self.dot_window_extra_dot_pending:
                # Resume right after the extra dot a WX==0 activation costs
                self.dot_window_extra_dot_pending = False
                self.dot_dots_elapsed += 1
                self._dot_decay_glitch_counters()
                self.dot_window_triggered = True
                self.dot_fetch_phase = 0
                self.dot_fetching_window = True
            elif self.dot_sprite_session_dots > 0:
                # Sprite fetch session dot: the pixel mixer and the background
                # fetcher are frozen while the sprite fetcher runs
                self.dot_dots_elapsed += 1
                self._dot_decay_glitch_counters()
                if self.dot_session_overlap_dots > 0:
                    # The line's first sprite session opens with a fetcher
                    # startup: the sprite fetcher's first VRAM read happens
                    # later in the session, and the background fetcher keeps
                    # the bus for the first three dots. The pixel mixer is
                    # frozen for the whole session including the overlap, so
                    # the fetched row still lands at the sprite's x position;
                    # mode 3 is only extended by the session length minus the
                    # overlap because the mixer is stalled for the mode-3
                    # startup dots anyway. Every later session of the line
                    # stalls the pipeline for its full length.
                    self.dot_session_overlap_dots -= 1
                    self.dot_step_fetcher()
                self.dot_sprite_session_dots -= 1
                if self.dot_sprite_session_count > 0:
                    self.dot_sprite_session_low -= 1
                    if self.dot_sprite_session_low == 0:
                        self._dot_sprite_session_low_read()
                    self.dot_sprite_session_high -= 1
                    if self.dot_sprite_session_high == 0:
                        self._dot_sprite_session_high_read()
                if self.dot_sprite_session_dots == 0:
                    self.dot_during_sprite_fetch = False
                    self._dot_sprite_session_end()
                # The pixel mixer and fetcher are frozen for every session
                # dot, including the last one
                continue
            else:
                # Fresh dot: pay the dot, then run the per-dot line work
                self.dot_dots_elapsed += 1

                # Drop sprites that have scrolled out of fetch range
                x_match = self.dot_sprite_fetch_x()
                while self.dot_n_sprites != 0 and self.dot_sprite_x[self.dot_n_sprites - 1] < x_match:
                    self.dot_n_sprites -= 1

                # A sprite fetch session starts when the fetcher's x position
                # reaches the smallest un-fetched sprite on the line
                if (
                    self.dot_n_sprites != 0
                    and (self.lcd._LCDC.sprite_enable or self.lcd._is_cgb_hardware())
                    and self.dot_sprite_x[self.dot_n_sprites - 1] == x_match
                ):
                    self._dot_sprite_session_start(x_match)
                    continue

                # Window activation. The x counter counts modulo 256, so the
                # values 240-255 denote the pre-line dots -16 to -1.
                if not self.dot_window_triggered and self.wy_activated_frame and self.lcd._LCDC.window_enable:
                    win_activation = False
                    if self.lcd.WX == 0:
                        if self.dot_x_counter == 249:  # -7
                            win_activation = True
                        elif self.dot_x_counter == 240 and (self.lcd.SCX & 7):  # -16
                            win_activation = True
                        elif 241 <= self.dot_x_counter <= 248:  # -15 to -8
                            win_activation = True
                    elif self.lcd.WX < 166 + self.lcd._is_cgb_hardware():
                        if self.lcd.WX == (self.dot_x_counter + 7) & 0xFF:
                            win_activation = True
                        elif (
                            not self.lcd._is_cgb_hardware()
                            and self.lcd.WX == (self.dot_x_counter + 6) & 0xFF
                            and not self.dot_wx_changed_dots
                        ):
                            win_activation = True
                            # LCD-PPU horizontal desync (DMG only)
                            if self.dot_screen_x > 0:
                                self.dot_screen_x -= 1

                    if win_activation:
                        self.dot_window_line = (self.dot_window_line + 1) & 0xFF
                        self.dot_window_column = 0
                        self.dot_bg_fifo_count = 0
                        self.dot_bg_fifo_read = 0
                        if self.lcd.WX == 0 and (self.lcd.SCX & 7) and not self.lcd._is_cgb_hardware():
                            # Window activation costs an extra dot
                            if self.dot_dots_elapsed >= target:
                                self.dot_window_extra_dot_pending = True
                                return
                            self.dot_dots_elapsed += 1
                            self._dot_decay_glitch_counters()
                        self.dot_window_triggered = True
                        self.dot_fetch_phase = 0
                        self.dot_fetching_window = True
                    elif (
                        not self.lcd._is_cgb_hardware()
                        and self.lcd.WX == 166
                        and self.lcd.WX == (self.dot_x_counter + 7) & 0xFF
                    ):
                        self.dot_window_line = (self.dot_window_line + 1) & 0xFF

                # Queue a pixel insertion at the FIFO's end
                if (
                    self.lcd.WX == (self.dot_x_counter + 7) & 0xFF
                    and (not self.lcd._is_cgb_hardware() or self.lcd.WX == 0)
                    and self.dot_window_triggered
                    and not self.dot_fetching_window
                    and self.dot_fetch_phase == 0
                    and self.dot_bg_fifo_count == 8
                ):
                    self.dot_bg_insert_pending = True

            self.dot_render_pixel()
            self.dot_step_fetcher()
            self._dot_decay_glitch_counters()
            if self.dot_x_counter == 160:
                break

    def _dot_sprite_session_start(self, x_match):
        # All sprites sharing the fetcher's x position are fetched in one
        # session. The session length depends on the SCX alignment (idx) and
        # on the number of sprites in the session. After the last fetch the
        # fetcher pays a fixed restart delay that depends only on the
        # alignment, whether or not further sprites follow on the line:
        # 11,10,9,8,7,6,6,6 dots in total for idx 0..7.
        count = 0
        while count < self.dot_n_sprites and self.dot_sprite_x[self.dot_n_sprites - 1 - count] <= x_match:
            count += 1
        idx = (x_match + self.lcd.SCX) & 7
        if idx < 2:
            startup = 8
        elif idx < 4:
            startup = 6
        elif idx < 7:
            startup = 4
        else:
            # The background fetcher is a single dot away from completing its
            # fetch, so the sprite fetcher overlaps it almost entirely and
            # the session is one dot shorter than for the other alignments
            startup = 3
        session_length = startup + 6 * (count - 1)
        if idx == 0 or idx == 2 or idx == 4 or idx == 7:
            session_length += 3
        else:
            session_length += 2
        # The trigger dot has already been paid by the caller
        self.dot_sprite_session_dots = session_length - 1
        self.dot_sprite_session_count = count
        first_fetch_end = session_length - 6 * (count - 1)
        self.dot_sprite_session_low = max(1, first_fetch_end - 3)
        self.dot_sprite_session_high = first_fetch_end - 1
        self.dot_during_sprite_fetch = True

    def dot_sprite_mode0_penalty(self, startup_overlap):
        # On a line whose OAM scan found sprites, the STAT mode-0 signal
        # follows the object fetcher's dot counter rather than the pixel
        # pipeline. Every sprite fetch session holds the fetcher for its
        # full length, so the mode-0 dot is the plain-line dot plus the
        # sum of the session lengths, minus the `startup_overlap` dots of
        # the line's first session that overlap the fixed mode-3 startup.
        # The session lengths follow the same alignment model as
        # _dot_sprite_session_start. Sprites at x >= 168 are never
        # reached by the fetcher and add nothing, but a scan that found
        # any sprite at all still pays the startup overlap.
        penalty = (self.lcd.SCX & 7) - startup_overlap
        i = self.dot_n_sprites - 1
        while i >= 0:
            x = self.dot_sprite_x[i]
            if x >= 168:
                # The list is sorted by descending x, so every remaining
                # sprite is also out of the fetcher's reach
                break
            count = 1
            while i - count >= 0 and self.dot_sprite_x[i - count] == x:
                count += 1
            i -= count
            idx = (x + self.lcd.SCX) & 7
            if idx < 2:
                startup = 8
            elif idx < 4:
                startup = 6
            elif idx < 7:
                startup = 4
            else:
                startup = 3
            session_length = startup + 6 * (count - 1)
            if idx == 0 or idx == 2 or idx == 4 or idx == 7:
                session_length += 3
            else:
                session_length += 2
            penalty += session_length
        return penalty

    def _dot_sprite_session_low_read(self):
        self.dot_sprite_low_read_dot = self.dot_dots_elapsed
        # Latch the tile number and attributes from OAM and read the low
        # bitplane of the sprite row
        sprite = self.dot_sprite_index[self.dot_n_sprites - 1]
        self.dot_sprite_fetch_tile = self.lcd.OAM[sprite * 4 + 2]
        self.dot_sprite_fetch_flags = self.lcd.OAM[sprite * 4 + 3]
        row_addr = self.dot_sprite_row_addr(
            self.dot_sprite_y[self.dot_n_sprites - 1], self.dot_sprite_fetch_tile, self.dot_sprite_fetch_flags
        )
        self.dot_sprite_fetch_row_addr = row_addr
        self.dot_sprite_fetch_data_low = self.dot_read_vram(row_addr)

    def _dot_sprite_session_high_read(self):
        self.dot_sprite_high_read_dot = self.dot_dots_elapsed
        # The high bitplane address is re-derived at read time, so a register
        # write landing between the two reads (for example an OBJ size
        # change) is observed here even though the low bitplane address was
        # derived before it
        self.dot_sprite_merge_y = self.dot_sprite_y[self.dot_n_sprites - 1]
        row_addr = self.dot_sprite_row_addr(
            self.dot_sprite_merge_y, self.dot_sprite_fetch_tile, self.dot_sprite_fetch_flags
        )
        self.dot_sprite_fetch_row_addr = row_addr
        self.dot_sprite_fetch_data_high = self.dot_read_vram(row_addr + 1)
        self.dot_glitch_data = self.dot_read_vram(row_addr + 1)
        # On CGB, the sprite with the lower OAM index wins when sprites
        # overlap. The merge overwrites a pixel when the already-merged
        # sprite has a higher priority value, so the OAM index is captured
        # here and passed to the deferred merge. On DMG the priority is the
        # x coordinate, which the fetch order (ascending x) already accounts
        # for: the first sprite merged wins, and a tie never overwrites.
        self.dot_sprite_merge_priority = self.dot_sprite_index[self.dot_n_sprites - 1] if self.lcd.cgb else 0
        self.dot_n_sprites -= 1
        self.dot_sprite_session_count -= 1
        if self.dot_sprite_session_count > 0:
            self.dot_sprite_session_low = 4
            self.dot_sprite_session_high = 6
        # The merge into the object FIFO is deferred to the start of the next
        # dot: hardware commits a register write landing on this read dot
        # mid-dot, before the fetcher's address phase, so the relatch below
        # can still update the fetched data before the merge consumes it
        self.dot_sprite_merge_pending = True

    def _dot_sprite_flush_merge(self):
        # Overlay the sprite row (costs no dots)
        if self.lcd.cgb:
            palette = self.dot_sprite_fetch_flags & 0b111
            priority = self.dot_sprite_merge_priority
        else:
            palette = 1 if (self.dot_sprite_fetch_flags & 0x10) else 0
            priority = 0
        self.dot_merge_sprite_row(
            self.dot_sprite_fetch_data_low,
            self.dot_sprite_fetch_data_high,
            palette,
            (self.dot_sprite_fetch_flags & 0x80) != 0,
            priority,
            (self.dot_sprite_fetch_flags & 0x20) != 0,
        )
        self.dot_sprite_merge_pending = False

    def dot_relatch_sprite_size(self):
        # A mid-scanline LCDC size write landing exactly on the fetcher's
        # low or high bitplane read dot is committed by hardware mid-dot,
        # before the fetcher's address phase, so the read observes the new
        # size even though the dot has already been processed. Redo the
        # address derivation and the read with the new size bit. The merge
        # is deferred, so the high read redo only has to refresh the fetched
        # data.
        if self.dot_sprite_low_read_dot == self.dot_dots_elapsed:
            self._dot_sprite_session_low_read()
        if self.dot_sprite_high_read_dot == self.dot_dots_elapsed and self.dot_sprite_merge_pending:
            row_addr = self.dot_sprite_row_addr(
                self.dot_sprite_merge_y, self.dot_sprite_fetch_tile, self.dot_sprite_fetch_flags
            )
            self.dot_sprite_fetch_row_addr = row_addr
            self.dot_sprite_fetch_data_high = self.dot_read_vram(row_addr + 1)
            self.dot_glitch_data = self.dot_read_vram(row_addr + 1)

    def _dot_sprite_session_end(self):
        # The background fetcher restarts for free when a sprite fetch
        # session ends: if it was mid-fetch with an empty FIFO it catches up
        # without charging further dots, as the session length already
        # includes the fetcher restart
        if self.dot_bg_fifo_count == 0 and self.dot_fetch_phase < 6:
            while self.dot_bg_fifo_count == 0:
                self.dot_step_fetcher()

    def dot_abort_sprite_session(self):
        # DMG: clearing the OBJ enable bit while a sprite fetch session is
        # in progress aborts the in-flight fetch. The fetch is discarded
        # without merging into the object FIFO, and the pixel mixer resumes
        # on the write dot itself. The write lands after the LCD tick already
        # ran the current dot as a frozen session dot, so refund it and let
        # it re-run as a normal rendering dot. The un-fetched sprite stays
        # in the fetch list; it is dropped once the fetcher's x position
        # passes it, or fetched by a fresh session if sprites are re-enabled
        # while it is still in range.
        self.dot_sprite_session_dots = 0
        self.dot_sprite_session_count = 0
        self.dot_sprite_session_low = 0
        self.dot_sprite_session_high = 0
        self.dot_session_overlap_dots = 0
        self.dot_during_sprite_fetch = False
        self.dot_dots_elapsed -= 1

    def dot_finish_line(self):
        self.dot_x_counter = 240
        self.dot_x_counter_fractional = False
        if self.dot_fetch_phase == 4 or self.dot_fetch_phase == 5:
            # Keep the high bitplane byte holding the last tile data read
            self.dot_tile_data_high = self.dot_tile_data_low
        if self.dot_screen_x != 160 and not self.lcd.disable_renderer:
            # The PPU and LCD desynced; fill the rest of the line with the last color
            if self.dot_screen_x == 0:
                color = self.lcd.bcpd.getcolor(0, 0) if self.lcd.cgb else self.lcd.BGP.getcolor(0)
            for x in range(self.dot_screen_x, 160):
                if self.dot_screen_x == 0:
                    self._screenbuffer[self.dot_ly, x] = color
                else:
                    self._screenbuffer[self.dot_ly, x] = self._screenbuffer[self.dot_ly, x - 1]
                self._screenbuffer_attributes[self.dot_ly, x] = 0
        if self.dot_ly == 143:
            self.dot_window_line = 255
        if (
            not self.lcd._is_cgb_hardware()
            and self.wy_activated_frame
            and self.lcd._LCDC.window_enable
            and self.lcd.WX == 166
        ):
            # WX=166 activates the window during HBlank on DMG
            self.dot_window_triggered = True
            self.dot_window_column = 1
            self.dot_window_line = (self.dot_window_line + 1) & 0xFF
        else:
            self.dot_window_triggered = False

    def dot_scan_sprites(self):
        height = 16 if self.lcd._LCDC.sprite_height else 8
        self.dot_n_sprites = 0
        for index in range(40):
            sprite_y = self.lcd.OAM[index * 4]
            sprite_x = self.lcd.OAM[index * 4 + 1]
            if self.dot_n_sprites == 10:
                return
            dy = sprite_y - 16
            if dy <= self.lcd.LY < dy + height:
                # Sort the visible sprites by descending x (and priority)
                j = 0
                while j < self.dot_n_sprites:
                    if self.dot_sprite_x[j] <= sprite_x:
                        break
                    j += 1
                for k in range(self.dot_n_sprites, j, -1):
                    self.dot_sprite_x[k] = self.dot_sprite_x[k - 1]
                    self.dot_sprite_y[k] = self.dot_sprite_y[k - 1]
                    self.dot_sprite_index[k] = self.dot_sprite_index[k - 1]
                self.dot_sprite_index[j] = index
                self.dot_sprite_x[j] = sprite_x
                self.dot_sprite_y[j] = sprite_y
                self.dot_n_sprites += 1

    def dot_step_fetcher(self):
        # The background/window fetcher pipeline. Each phase completes in one
        # call (one dot):
        #   0: compute the tile map address
        #   1: read the tile map entry (index and, on CGB, attributes)
        #   2: compute the tile data address for the low bitplane
        #   3: read the low bitplane byte
        #   4: compute the tile data address for the high bitplane
        #   5: read the high bitplane byte and push the row to the FIFO
        #   6: push stalled because the FIFO is full
        if self.dot_fetch_phase == 0:
            self.dot_update_window_glitch()
            map_addr = 0x1800
            if not self.lcd._LCDC.window_enable:
                self.dot_window_triggered = False
            if self.lcd._LCDC.backgroundmap_select and not self.dot_window_triggered:
                map_addr = 0x1C00
            elif self.lcd._LCDC.windowmap_select and self.dot_window_triggered:
                map_addr = 0x1C00
            if self.dot_window_triggered:
                row = self.dot_window_line
            else:
                row = (self.lcd.LY + self.lcd.SCY) & 0xFF
            if self.dot_window_triggered:
                column = self.dot_window_column
            elif ((self.dot_x_counter + 16) & 0xFF) < 8:
                column = self.lcd.SCX >> 3
            else:
                column = (
                    self.lcd.SCX
                    + self.dot_x_counter
                    + 8
                    - (1 if self.lcd._is_cgb_hardware() and not self.dot_during_sprite_fetch else 0)
                ) // 8 & 0b11111
            self.dot_tilemap_addr = map_addr + column + (row // 8) * 32
            self.dot_fetch_phase = 1
        elif self.dot_fetch_phase == 1:
            if self.dot_cgb_window_glitch:
                self.dot_fetch_phase = 2
            else:
                self.dot_tile_index = self.dot_read_vram(self.dot_tilemap_addr)
                # The CGB tile attributes are only honored in CGB mode. A
                # DMG game running on CGB hardware ignores the attribute map
                # entirely (VRAM bank 0, no flips, no BG priority), which is
                # what keeps the attribute bytes left behind by the boot ROM
                # logo from leaking into its rendering
                if self.lcd.cgb:
                    self.dot_tile_attrs = self.dot_read_vram(self.dot_tilemap_addr + 0x2000)
                else:
                    self.dot_tile_attrs = 0
                self.dot_fetch_phase = 2
        elif self.dot_fetch_phase == 2:
            self.dot_update_window_glitch()
            self.dot_tiledata_addr = self._dot_tiledat_addr(0)
            self.dot_fetch_phase = 3
        elif self.dot_fetch_phase == 3:
            if self.dot_cgb_window_glitch:
                self.dot_tile_data_low = self.dot_tile_data_high
                self.dot_fetch_phase = 4
            else:
                stale_replay = False
                if self.dot_tiledata_glitch_dots:
                    # CGB tile data select conflict: the fetcher may replay
                    # stale data instead of reading VRAM
                    if self.dot_latched_tiledata_select:
                        stale_replay = not (self.dot_tile_index & 0x80)
                    else:
                        stale_replay = True
                if not stale_replay:
                    self.dot_tile_data_low = self.dot_read_vram(self.dot_tiledata_addr)
                if self.dot_latched_tiledata_select and self.dot_tiledata_glitch_dots:
                    self.dot_glitch_data = self.dot_read_vram(self.dot_tiledata_addr)
                self.dot_fetch_phase = 4
        elif self.dot_fetch_phase == 4:
            self.dot_update_window_glitch()
            self.dot_tiledata_addr = self._dot_tiledat_addr(1)
            self.dot_fetch_phase = 5
        elif self.dot_fetch_phase == 5:
            if self.dot_cgb_window_glitch:
                self.dot_tile_data_high = self.dot_tile_data_low
                self.dot_fetch_phase = 6
                if self.dot_window_triggered:
                    self.dot_window_column = (self.dot_window_column + 1) & 0b11111
            else:
                stale_replay = False
                if self.dot_tiledata_glitch_dots:
                    if self.dot_latched_tiledata_select:
                        stale_replay = not (self.dot_tile_index & 0x80)
                    else:
                        stale_replay = True
                if not stale_replay:
                    self.dot_tile_data_high = self.dot_read_vram(self.dot_tiledata_addr)
                    self.dot_glitch_data = self.dot_tile_data_high
                if self.dot_latched_tiledata_select and self.dot_tiledata_glitch_dots:
                    self.dot_glitch_data = self.dot_read_vram(self.dot_tiledata_addr)
                self.dot_fetch_phase = 6
                if self.dot_window_triggered:
                    self.dot_window_column = (self.dot_window_column + 1) & 0b11111
                # Fall through to the push
                self.dot_fetcher_push()
        elif self.dot_fetch_phase == 6:
            self.dot_fetcher_push()

    def _dot_tiledat_addr(self, byte_offset):
        # Latch the tile data addressing mode and compute the VRAM address of
        # one bitplane byte for the tile being fetched.
        self.dot_latched_tiledata_select = self.lcd._LCDC.tiledata_select
        if self.dot_latched_tiledata_select:
            tile_addr = self.dot_tile_index * 0x10
        else:
            tile_addr = (
                self.dot_tile_index - 256 if self.dot_tile_index >= 128 else self.dot_tile_index
            ) * 0x10 + 0x1000
        if self.dot_tile_attrs & 0b1000:  # CGB VRAM bank
            tile_addr += 0x2000
        y_flip = 0b111 if (self.dot_tile_attrs & 0b1000000) else 0  # Vertical flip
        if self.dot_window_triggered:
            row = self.dot_window_line
        else:
            row = (self.lcd.LY + self.lcd.SCY) & 0xFF
        return tile_addr + ((row & 7) ^ y_flip) * 2 + byte_offset

    def dot_fetcher_push(self):
        self.dot_fetch_phase = 6
        if self.dot_bg_fifo_count > 0:
            return
        if (
            self.wy_activated_frame
            and not self.lcd._LCDC.window_enable
            and not self.lcd._is_cgb_hardware()
            and not self.dot_win_glitch_blocked
        ):
            # DMG window pixel insertion glitch: with the window disabled after
            # WY matched, a lone pixel is inserted when WX lines up with the
            # fetcher position offset by the pipeline delay. Past the right
            # screen edge the comparator reads 0, matching WX=0
            if self.lcd.WX == (self.dot_x_counter + 7 if self.dot_x_counter <= 160 else 0):
                self.dot_bg_fifo_read = (self.dot_bg_fifo_read - 1) & 7
                self.dot_bg_fifo_pixel[self.dot_bg_fifo_read] = 0
                self.dot_bg_fifo_palette[self.dot_bg_fifo_read] = 0
                self.dot_bg_fifo_priority[self.dot_bg_fifo_read] = 0
                self.dot_bg_fifo_count = 1
                return
        self.dot_fill_bg_fifo(
            self.dot_tile_data_low,
            self.dot_tile_data_high,
            self.dot_tile_attrs & 0b111,
            (self.dot_tile_attrs & 0x80) != 0,
            (self.dot_tile_attrs & 0b100000) != 0,
        )
        self.dot_fetch_phase = 0

    def dot_render_pixel(self):
        # Rendering stalls while a sprite at x=0 is still pending. Pixels
        # the x counter places off-screen are discarded anyway, so the stall
        # only applies to pixels that would land on the screen.
        if (
            self.dot_n_sprites != 0
            and self.dot_x_counter < 160
            and (self.lcd._LCDC.sprite_enable or self.lcd._is_cgb_hardware())
            and self.dot_sprite_x[self.dot_n_sprites - 1] == 0
        ):
            self.dot_mixer_stalled = True
            return
        if self.dot_bg_fifo_count == 0:
            self.dot_mixer_stalled = True
            return

        if self.dot_bg_insert_pending:
            self.dot_bg_insert_pending = False
            # Consume an empty FIFO slot without popping a pixel
            pixel = 0
            palette = 0
            bg_priority = False
        else:
            pixel = self.dot_bg_fifo_pixel[self.dot_bg_fifo_read]
            palette = self.dot_bg_fifo_palette[self.dot_bg_fifo_read]
            bg_priority = self.dot_bg_fifo_priority[self.dot_bg_fifo_read] != 0
            self.dot_bg_fifo_read = (self.dot_bg_fifo_read + 1) & 7
            self.dot_bg_fifo_count -= 1

        draw_sprite = False
        sprite_pixel = 0
        sprite_palette = 0
        if self.dot_obj_fifo_count > 0:
            sprite_pixel = self.dot_obj_fifo_pixel[self.dot_obj_fifo_read]
            sprite_palette = self.dot_obj_fifo_palette[self.dot_obj_fifo_read]
            sprite_bg_priority = self.dot_obj_fifo_bg_priority[self.dot_obj_fifo_read] != 0
            self.dot_obj_fifo_read = (self.dot_obj_fifo_read + 1) & 7
            self.dot_obj_fifo_count -= 1
            if sprite_pixel and self.lcd._LCDC.sprite_enable:
                draw_sprite = True
                bg_priority = bg_priority or sprite_bg_priority

        # SCX adjustment of the x counter (values 240-255 are the pre-line
        # dots -16 to -1)
        if ((self.dot_x_counter + 16) & 0xFF) < 8:
            if self.dot_x_counter == 239:  # -17
                self.dot_x_counter = 240
            elif (self.dot_x_counter & 7) == (self.lcd.SCX & 7):
                self.dot_x_counter = 248
            elif self.dot_fetching_window and (self.dot_x_counter & 7) == 6 and (self.lcd.SCX & 7) == 7:
                self.dot_x_counter = 248
            elif self.dot_x_counter == 247:  # -9
                self.dot_x_counter = 240
                self.dot_mixer_stalled = False
                return
            else:
                self.dot_x_counter_fractional = True
        self.dot_fetching_window = False

        # Discard pixels that fall outside the screen
        if self.dot_x_counter >= 160:
            self.dot_x_counter = (self.dot_x_counter + 1) & 0xFF
            self.dot_mixer_stalled = False
            return

        # Pixel mixing. The pipeline state advances identically whether or
        # not the screen is being rendered: STAT timing depends on it, and
        # hardware has no notion of a disabled framebuffer. Only the
        # screenbuffer writes are skipped when rendering is disabled.
        bg_enabled = True
        if not self.lcd._LCDC.background_enable:
            if self.lcd.cgb:
                bg_priority = False
            else:
                bg_enabled = False
        raw_pixel = pixel if bg_enabled else 0
        if raw_pixel and bg_priority:
            draw_sprite = False

        if self.lcd.cgb:
            color = self.lcd.bcpd.getcolor(palette, raw_pixel)
        else:
            color = self.lcd.BGP.getcolor(raw_pixel)
        if not self.lcd.disable_renderer:
            self._screenbuffer[self.dot_ly, self.dot_screen_x] = color
        attributes = 0
        if bg_priority:
            attributes |= BG_PRIORITY_FLAG
        if raw_pixel == 0:
            attributes |= COL0_FLAG
        if not self.lcd.disable_renderer:
            self._screenbuffer_attributes[self.dot_ly, self.dot_screen_x] = attributes

        if draw_sprite:
            if self.lcd.cgb:
                color = self.lcd.ocpd.getcolor(sprite_palette, sprite_pixel)
            else:
                if sprite_palette:
                    color = self.lcd.OBP1.getcolor(sprite_pixel)
                else:
                    color = self.lcd.OBP0.getcolor(sprite_pixel)
            if not self.lcd.disable_renderer:
                self._screenbuffer[self.dot_ly, self.dot_screen_x] = color

        self.dot_last_pixel_dot = self.dot_dots_elapsed
        self.dot_last_pixel_x = self.dot_screen_x
        if self.dot_screen_x == 157:
            # Hardware lowers the STAT mode-0 signal when this pixel is
            # popped, two dots before the pipeline pushes the line's last
            # pixel
            self.dot_mode0_elapsed = self.dot_dots_elapsed
        self.dot_last_pixel_raw = raw_pixel
        self.dot_last_pixel_sprite_raw = sprite_pixel if draw_sprite else -1
        self.dot_last_pixel_sprite_palette = sprite_palette if draw_sprite else -1
        self.dot_last_pixel_stalled_recovery = self.dot_mixer_stalled
        self.dot_mixer_stalled = False
        self.dot_x_counter = (self.dot_x_counter + 1) & 0xFF
        self.dot_screen_x += 1

    def dot_fill_bg_fifo(self, lower, upper, palette, bg_priority, flip_x):
        self.dot_bg_fifo_count = 8
        if not flip_x:
            for i in range(8):
                self.dot_bg_fifo_pixel[i] = (lower >> 7) | ((upper >> 7) << 1)
                self.dot_bg_fifo_palette[i] = palette
                self.dot_bg_fifo_priority[i] = 1 if bg_priority else 0
                lower = (lower << 1) & 0xFF
                upper = (upper << 1) & 0xFF
        else:
            for i in range(8):
                self.dot_bg_fifo_pixel[i] = (lower & 1) | ((upper & 1) << 1)
                self.dot_bg_fifo_palette[i] = palette
                self.dot_bg_fifo_priority[i] = 1 if bg_priority else 0
                lower >>= 1
                upper >>= 1

    def dot_merge_sprite_row(self, lower, upper, palette, bg_priority, priority, flip_x):
        # Pad the sprite FIFO to a full row before merging
        while self.dot_obj_fifo_count < 8:
            index = (self.dot_obj_fifo_read + self.dot_obj_fifo_count) & 7
            self.dot_obj_fifo_pixel[index] = 0
            self.dot_obj_fifo_palette[index] = 0
            self.dot_obj_fifo_priority[index] = 0
            self.dot_obj_fifo_bg_priority[index] = 0
            self.dot_obj_fifo_count += 1
        for i in range(7, -1, -1):
            pixel = (lower >> 7) | ((upper >> 7) << 1)
            # An X-flipped sprite scans its bitplane row in reverse order
            row_bit = i if flip_x else 7 - i
            target = (self.dot_obj_fifo_read + row_bit) & 7
            if pixel != 0 and (self.dot_obj_fifo_pixel[target] == 0 or self.dot_obj_fifo_priority[target] > priority):
                self.dot_obj_fifo_pixel[target] = pixel
                self.dot_obj_fifo_palette[target] = palette
                self.dot_obj_fifo_bg_priority[target] = 1 if bg_priority else 0
                self.dot_obj_fifo_priority[target] = priority
            lower = (lower << 1) & 0xFF
            upper = (upper << 1) & 0xFF

    def dot_sprite_row_addr(self, sprite_y, tile, flags):
        mask = 0b1111 if self.lcd._LCDC.sprite_height else 0b111
        tile_y = (self.lcd.LY - sprite_y) & mask
        if flags & 0b1000000:  # Y flip
            tile_y ^= mask
        addr = ((tile & 0b11111110) if self.lcd._LCDC.sprite_height else tile) * 0x10 + tile_y * 2
        if self.lcd.cgb and (flags & 0b1000):  # CGB VRAM bank
            addr += 0x2000
        return addr

    def dot_sprite_fetch_x(self):
        # The x position where the next sprite fetch is due, in the wrapped
        # x counter domain
        ret = (self.dot_x_counter + 8) & 0xFF
        if ret > 240:
            return 0
        return ret

    def dot_read_vram(self, addr):
        if addr & 0x2000:
            return self.lcd.VRAM1[addr & 0x1FFF]
        return self.lcd.VRAM0[addr]

    def dot_update_window_glitch(self):
        # CGB: a window trigger arriving while a fetch is in progress makes
        # the fetcher replay its previous data instead of reading VRAM
        if not self.lcd._is_cgb_hardware():
            self.dot_cgb_window_glitch = False
        elif (not self.lcd._LCDC.window_enable) or not self.wy_activated_frame:
            self.dot_cgb_window_glitch = False
        elif self.lcd.WX == 0:
            # The x counter counts modulo 256; (x + 16) & 0xFF <= 8 covers the
            # pre-line dots down to -8
            self.dot_cgb_window_glitch = ((self.dot_x_counter + 16) & 0xFF) <= 8 or (
                self.dot_x_counter == 249 and self.dot_x_counter_fractional
            )
        else:
            self.dot_cgb_window_glitch = (self.dot_x_counter + 7 + self.dot_fetching_window) & 0xFF == self.lcd.WX

    def _dot_decay_glitch_counters(self):
        # Register write conflicts last exactly one dot (two in CGB double
        # speed for the tile data select conflict)
        if self.dot_wx_changed_dots > 0:
            self.dot_wx_changed_dots -= 1
        if self.dot_tiledata_glitch_dots > 0:
            self.dot_tiledata_glitch_dots -= 1

    ####################################
    #
    #  ██████   ██████   ██████
    # ██       ██        ██   ██
    # ██       ██   ███  ██████
    # ██       ██    ██  ██   ██
    #  ██████   ██████   ██████
    #

    def _cgb_get_background_map_attributes(self, lcd, i):
        tile_num = self.lcd.VRAM1[i]
        palette = tile_num & 0b111
        vbank = (tile_num >> 3) & 1
        horiflip = (tile_num >> 5) & 1
        vertflip = (tile_num >> 6) & 1
        bg_priority = (tile_num >> 7) & 1

        return palette, vbank, horiflip, vertflip, bg_priority


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
