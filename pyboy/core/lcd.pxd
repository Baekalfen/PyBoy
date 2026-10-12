#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython
from cython cimport final

from cpython.array cimport array
from libc.stdint cimport int16_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t

cimport pyboy.utils
from pyboy cimport utils
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface


cdef uint8_t INTR_VBLANK, INTR_LCDC
cdef uint16_t LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX
cdef int ROWS, COLS, TILES, FRAME_CYCLES, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
cdef int DOT_MODE3_RENDER_DELAY
cdef uint32_t COL0_FLAG, BG_PRIORITY_FLAG
cdef uint8_t CGB_NUM_PALETTES
cdef uint8_t STAT_TRANSITION_NONE, STAT_TRANSITION_ADVANCE_LY, STAT_TRANSITION_START_MODE2
cdef uint8_t STAT_TRANSITION_VBLANK_PRETRIGGERED

cdef Logger logger

@cython.locals(a=uint32_t, r=uint32_t, g=uint32_t, b=uint32_t)
cpdef uint32_t rgb_to_bgr(uint32_t) noexcept

@final
cdef class LCD:
    cdef bint disable_renderer
    cdef uint8_t[8 * 1024] VRAM0
    cdef uint8_t[0xA0] OAM

    cdef uint8_t SCY
    cdef uint8_t SCX
    cdef uint8_t WY
    cdef uint8_t WX
    cdef uint8_t object_priority_mode
    cdef uint8_t next_stat_mode
    cdef uint8_t stat_transition
    cdef bint stat_irq_delayed
    cdef uint64_t stat_irq_delivery_clock
    cdef bint frame_done
    cdef bint first_frame
    cdef bint reset
    cdef bint stat_mode_override
    cdef bint lyc_changed_while_disabled
    cdef uint8_t LY
    cdef uint8_t LYC
    cdef int16_t mode3_extension
    cdef uint64_t clock
    cdef uint64_t clock_target
    cdef LCDCRegister _LCDC
    cdef STATRegister _STAT
    cdef PaletteRegister BGP
    cdef PaletteRegister OBP0
    cdef PaletteRegister OBP1
    cdef Renderer renderer
    cdef uint8_t[144][5] _scanlineparameters
    cdef uint64_t last_cycles
    cdef int64_t _cycles_to_interrupt, _cycles_to_frame
    cdef int64_t mode3_start_clock

    @final
    cdef void switch_cgb(self, bint) noexcept with gil

    @final
    @cython.locals(
        interrupt_flag=uint8_t,
        bx=int,
        by=int,
        wx=int,
        wy=int,
        vblank_stat_pretriggered=bint,
        cycles_to_interrupt=int64_t,
    )
    cdef uint8_t tick(self, uint64_t) noexcept nogil

    @final
    cdef uint8_t set_lcdc(self, uint8_t) noexcept nogil

    @final
    cdef uint8_t write_lcdc(self, uint8_t) noexcept nogil
    @final
    cdef void write_bgp(self, uint8_t) noexcept nogil
    @final
    cdef void write_obp(self, uint8_t, uint8_t) noexcept nogil
    @final
    cdef void write_wy(self, uint8_t) noexcept nogil
    @final
    cdef void write_wx(self, uint8_t) noexcept nogil

    @final
    cdef int64_t cycles_to_mode0(self) noexcept nogil
    @final
    cdef inline bint _is_cgb_hardware(self) noexcept nogil
    @final
    cdef inline bint _is_startup_mode2_delay(self) noexcept nogil
    @final
    cdef inline bint _should_pretrigger_vblank_stat(self) noexcept nogil
    @final
    @cython.locals(
        index=int,
        y=int,
        x=int,
        spriteheight=int,
        spritecount=int,
        penalty=int,
        group_count=int,
        duplicate=bint,
        alignment=int,
        seen_x0=uint64_t,
        seen_x1=uint64_t,
        seen_x2=uint64_t,
        x_mask=uint64_t,
    )
    cdef int _mode3_sprite_penalty(self, int) noexcept nogil
    @final
    @cython.locals(penalty=int)
    cdef inline int _mode3_timing_adjustment(self, int) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

    @final
    cdef inline (int, int) getwindowpos(self) noexcept nogil
    @final
    cdef inline (int, int) getviewport(self) noexcept nogil

    # CGB
    cdef bint cgb, _downgraded_to_dmg
    cdef uint8_t speed_shift
    cdef uint8_t[8 * 1024] VRAM1
    cdef VBKregister vbk
    cdef PaletteIndexRegister bcps
    cdef PaletteColorRegister bcpd
    cdef PaletteIndexRegister ocps
    cdef PaletteColorRegister ocpd

@final
cdef class PaletteRegister:
    cdef uint8_t value
    cdef uint32_t[4] lookup
    cdef uint32_t[4] palette_mem_rgb

    @final
    @cython.locals(x=uint16_t)
    cdef bint set(self, uint64_t) noexcept nogil
    @final
    cdef inline void _update_lookup(self) noexcept nogil
    @final
    cdef uint8_t get(self) noexcept nogil
    @final
    cdef inline uint32_t getcolor(self, uint8_t) noexcept nogil

@final
cdef class STATRegister:
    cdef uint8_t value
    cdef uint8_t _mode
    cdef bint _irq_line
    @final
    cdef uint8_t set_mode(self, uint8_t) noexcept nogil
    @final
    cdef uint8_t update_LYC(self, uint8_t, uint8_t) noexcept nogil
    @final
    cdef uint8_t set(self, uint64_t) noexcept nogil
    @final
    @cython.locals(mode_irq=bint, lyc_irq=bint, irq_line=bint, interrupt=uint8_t)
    cdef uint8_t _update_irq_line(self) noexcept nogil
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

@final
cdef class LCDCRegister:
    cdef uint8_t value

    @final
    cdef void set(self, uint64_t) noexcept nogil

    cdef bint lcd_enable
    cdef bint windowmap_select
    cdef bint window_enable
    cdef bint tiledata_select
    cdef bint backgroundmap_select
    cdef readonly bint sprite_height
    cdef bint sprite_enable
    cdef bint background_enable
    cdef bint cgb_master_priority

    cdef uint16_t backgroundmap_offset
    cdef uint16_t windowmap_offset

@final
cdef class Renderer:
    cdef LCD lcd
    cdef uint8_t[:] _tilecache_state, _spritecache_state
    cdef str color_format
    cdef tuple buffer_dims
    cdef bint cgb

    cdef array _screenbuffer_raw
    cdef array _screenbuffer_attributes_raw
    cdef object _screenbuffer_ptr
    cdef array _tilecache_raw, _spritecache_raw
    cdef uint32_t[:,:] _screenbuffer
    cdef uint8_t[:,:] _screenbuffer_attributes
    cdef uint8_t[:,:,:] _tilecache, _spritecache
    cdef uint64_t[:, :] _tilecache_64, _spritecache_64
    cdef uint32_t[:] colorcode_table

    cdef int[10] sprites_to_render
    cdef bint wy_activated_frame

    # Dot-accurate renderer: fetcher pipeline and pixel FIFOs that reproduce
    # mid-scanline register change behavior
    cdef int dot_ly
    cdef int dot_dots_elapsed
    # Dots elapsed when the pipeline popped the pixel at screen column 157.
    # Hardware lowers the STAT mode-0 signal here, two dots before the line's
    # last pixel is pushed, or -1 before that pixel is reached
    cdef int dot_mode0_elapsed
    # The dot_mode0_elapsed value already consumed by the mode-0 target
    # correction, or -1. Guards against re-applying a stale correction after
    # sprite fetch work has extended mode 3 past the corrected target.
    cdef int dot_mode0_corrected
    # True when the line's OAM scan found sprites that the fetcher will fetch,
    # in which case the STAT mode-0 signal follows the fetcher's dot counter
    # and the mode-0 target is computed from the scan instead of the pipeline
    cdef bint dot_mode0_fetcher_based
    cdef int dot_x_counter
    cdef int dot_screen_x
    cdef int dot_fetch_phase
    cdef uint8_t dot_tile_index
    cdef uint8_t dot_tile_attrs
    cdef uint8_t dot_tile_data_low
    cdef uint8_t dot_tile_data_high
    cdef int dot_tilemap_addr
    cdef int dot_tiledata_addr
    cdef int dot_tileaddr_dot
    cdef bint dot_window_triggered
    cdef bint dot_fetching_window
    cdef int dot_window_column
    cdef int dot_window_line
    cdef bint dot_x_counter_fractional
    cdef bint dot_bg_insert_pending
    cdef bint dot_win_glitch_blocked
    cdef uint8_t[:] dot_bg_fifo_pixel
    cdef uint8_t[:] dot_bg_fifo_palette
    cdef uint8_t[:] dot_bg_fifo_priority
    cdef int dot_bg_fifo_count
    cdef int dot_bg_fifo_read
    cdef uint8_t[:] dot_obj_fifo_pixel
    cdef uint8_t[:] dot_obj_fifo_palette
    cdef uint8_t[:] dot_obj_fifo_priority
    cdef uint8_t[:] dot_obj_fifo_bg_priority
    cdef int dot_obj_fifo_count
    cdef int dot_obj_fifo_read
    cdef uint8_t[:] dot_sprite_x
    cdef uint8_t[:] dot_sprite_y
    cdef int[:] dot_sprite_index
    cdef int dot_n_sprites
    cdef uint8_t dot_sprite_fetch_tile
    cdef uint8_t dot_sprite_fetch_flags
    cdef uint8_t dot_sprite_fetch_data_low
    cdef uint8_t dot_sprite_fetch_data_high
    cdef int dot_sprite_fetch_row_addr
    # The sprite row fetch completes on its high-bitplane read dot, but the
    # merge into the object FIFO is deferred to the start of the next dot:
    # a register write landing on the read dot itself is committed by
    # hardware mid-dot, before the fetcher's address phase, so the read must
    # still be able to observe it before the merge consumes the data.
    cdef bint dot_sprite_merge_pending
    cdef int dot_sprite_merge_priority
    cdef int dot_sprite_merge_y
    # Dots of this line at which the sprite fetcher's low and high bitplane
    # reads fired, or -1. A mid-scanline LCDC size write landing exactly on
    # one of these dots is observed by that read.
    cdef int dot_sprite_low_read_dot
    cdef int dot_sprite_high_read_dot
    cdef bint dot_during_sprite_fetch
    cdef int dot_sprite_session_dots
    cdef int dot_sprite_session_count
    cdef int dot_sprite_session_low
    cdef int dot_sprite_session_high
    # Background-fetcher steps still owed during a sprite fetch session: the
    # fetcher completes its in-flight fetch during the session's startup
    # before the sprite fetcher takes over the bus.
    cdef int dot_session_bg_steps
    cdef uint8_t dot_glitch_data
    cdef bint dot_latched_tiledata_select
    cdef int dot_tiledata_glitch_dots
    cdef bint dot_tiledata_glitch_index
    cdef bint dot_cgb_window_glitch
    cdef int dot_wx_changed_dots
    cdef bint dot_window_extra_dot_pending
    # Set around the LCD sync of an LCDC write that changes the win-enable
    # bit: the sync stops one dot short so the write lands on its own cycle
    cdef int _sync_minus
    # The WX register and win-enable signal as sampled one dot ago, for the
    # window activation comparator (WX) and the fetch-type decision (win-en)
    cdef int dot_wx_prev
    cdef bint dot_wen_prev
    cdef bint dot_wen_cur
    # SCY as sampled one dot ago. On CGB, SCY writes take effect two dots
    # later (the write lands between LCD ticks, so the fetcher observes the
    # new value from two dots after the write dot).
    cdef int dot_scy_prev
    cdef int dot_scy_reg
    # The OBJ size bit as sampled one dot ago. On CGB the sprite fetcher
    # observes LCDC size writes two dots after the write dot
    cdef bint dot_objsize_prev
    cdef bint dot_objsize_reg
    # The LCDC tile data select as sampled one dot ago. While a sprite fetch
    # session owns the fetch unit, the fetcher observes the tile data select
    # as of one dot ago; on normal dots it observes it live
    cdef bint dot_tdsel_prev
    cdef bint dot_tdsel_reg
    # The x-based part of the map column latched at fetch phase 0; -1 marks
    # the first-fetch special case that uses SCX>>3
    cdef int dot_col_x
    # The LCDC map-select bits latched at fetch phase 0 (the address phase).
    # The map read at phase 1 uses the latched values: on CGB a write landing
    # between the two phases is committed after the address phase, so the map
    # read keeps the old map.
    cdef bint dot_latched_bgmap
    cdef bint dot_latched_winmap
    # SCX latched at fetch phase 0 (the start of each tile fetch). The map
    # read at phase 1 uses the latched value: on CGB a write landing between
    # the two phases keeps the old SCX for the current fetch.
    cdef int dot_scx_latched
    # The most recently colored pixel of the current line, tracked so that a
    # mid-scanline palette write can apply the DMG write glitch to the pixel
    # colored on the exact dot of the write. dot_last_pixel_raw always holds
    # the background color number; dot_last_pixel_sprite_raw is negative when
    # no sprite pixel was mixed into the output.
    cdef int dot_last_pixel_dot
    cdef int dot_last_pixel_x
    cdef int dot_last_pixel_raw
    cdef int dot_last_pixel_sprite_raw
    cdef int dot_last_pixel_sprite_palette
    # True while the pixel mixer is stalled waiting for FIFO data. The first
    # pixel output after a stall is colored in a later phase of its dot, so a
    # register write on that exact dot is observed by the pixel (unlike normal
    # dots, where the pixel is colored before the write lands).
    cdef bint dot_mixer_stalled
    cdef bint dot_last_pixel_stalled_recovery
    @cython.locals(i=int)
    cdef void start_dot_line(self, int) noexcept nogil
    @cython.locals(
        x_match=uint8_t,
        wx_reg=int,
        wen_reg=bint,
        win_activation=bint,
        bgmap=bint,
        winmap=bint,
        row=int,
        column=int,
        scx=int,
    )
    cdef void advance_dots(self, int64_t) noexcept nogil
    @cython.locals(color=uint32_t)
    cdef void dot_finish_line(self) noexcept nogil
    @cython.locals(
        map_addr=int,
        row=int,
        column=int,
        stale_replay=bint,
        glitch_data=uint8_t,
        bgmap=bint,
        winmap=bint,
        scx=int,
    )
    cdef void dot_step_fetcher(self) noexcept nogil
    @cython.locals(
        pixel=uint8_t,
        sprite_pixel=uint8_t,
        palette=uint8_t,
        sprite_palette=uint8_t,
        bg_priority=bint,
        sprite_bg_priority=bint,
        draw_sprite=bint,
        bg_enabled=bint,
        color=uint32_t,
        attributes=uint8_t,
    )
    cdef void dot_render_pixel(self) noexcept nogil
    @cython.locals(
        index=int,
        sprite_y=uint8_t,
        sprite_x=uint8_t,
        dy=int,
        j=int,
    )
    cdef void dot_scan_sprites(self) noexcept nogil
    @final
    cdef void reset_dot_pipeline(self) noexcept nogil
    @cython.locals(
        count=int,
        idx=int,
        startup=int,
        session_length=int,
        first_fetch_end=int,
    )
    cdef void _dot_sprite_session_start(self, uint8_t) noexcept nogil
    @cython.locals(
        count=int,
        idx=int,
        startup=int,
        session_length=int,
        i=int,
        x=int,
    )
    cdef int dot_sprite_mode0_penalty(self, int) noexcept nogil
    @cython.locals(sprite=int, row_addr=int)
    cdef void _dot_sprite_session_low_read(self) noexcept nogil
    @cython.locals(row_addr=int, data_high=uint8_t, palette=uint8_t)
    cdef void _dot_sprite_session_high_read(self) noexcept nogil
    cdef void _dot_sprite_flush_merge(self) noexcept nogil
    cdef void dot_relatch_sprite_size(self) noexcept nogil
    cdef void dot_relatch_scy(self) noexcept nogil
    cdef void _dot_sprite_session_end(self) noexcept nogil
    cdef void dot_abort_sprite_session(self) noexcept nogil
    cdef inline uint8_t dot_read_vram(self, int) noexcept nogil
    cdef inline void dot_update_window_glitch(self) noexcept nogil
    cdef inline void _dot_decay_glitch_counters(self) noexcept nogil
    cdef inline int _dot_scy_sample(self) noexcept nogil
    cdef void dot_fetcher_push(self) noexcept nogil
    @cython.locals(i=int, pixel=uint8_t)
    cdef void dot_fill_bg_fifo(self, uint8_t, uint8_t, uint8_t, bint, bint) noexcept nogil
    @cython.locals(
        i=int,
        target=int,
        row_bit=int,
        pixel=uint8_t,
    )
    cdef void dot_merge_sprite_row(self, uint8_t, uint8_t, uint8_t, bint, int, bint) noexcept nogil
    @cython.locals(tile_y=int, mask=int, addr=int)
    cdef inline int dot_sprite_row_addr(self, uint8_t, uint8_t, uint8_t) noexcept nogil
    @cython.locals(ret=int)
    cdef inline uint8_t dot_sprite_fetch_x(self) noexcept nogil
    @cython.locals(
        tile_addr=int,
        y_flip=int,
        row=int,
    )
    cdef int _dot_tiledat_addr(self, int) noexcept nogil

    cdef void invalidate_tile(self, int, int) noexcept nogil

    cdef void blank_screen(self) noexcept nogil


    @cython.locals(
        tile_num = uint8_t,
        palette = uint8_t,
        vbank = uint8_t,
        horiflip = uint8_t,
        vertflip = uint8_t,
        bg_priority = uint8_t,
    )
    cdef inline (int, int, int, int, int) _cgb_get_background_map_attributes(self, LCD, int) noexcept nogil
    @cython.locals(
        spriteheight=int,
        spritecount=int,
        n=int,
        x=int,
        y=int,
        _n=int,
        tileindex=int,
        attributes=int,
        xflip=bint,
        yflip=bint,
        spritepriority=bint,
        palette=uint8_t,
        spritecache=uint8_t[:,:],
        dy=int,
        dx=int,
        yy=int,
        xx=int,
        color_code=uint8_t,
        pixel=uint32_t,
        bgmappriority=bint,
        sprite_cache_no=int,
    )
    cdef void scanline_sprites(self, int, uint32_t[:,:], uint8_t[:,:], bint) noexcept nogil
    cdef void sort_sprites(self, int) noexcept nogil

    cdef void clear_cache(self) noexcept nogil
    cdef void clear_tilecache(self, int) noexcept nogil
    cdef void clear_spritecache(self, int) noexcept nogil
    # @final
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_tilecache(self, int, LCD, int, int) noexcept nogil
    # @final
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_spritecache(self, int, LCD, int, int) noexcept nogil

    @cython.locals(colorcode_low=uint64_t, colorcode_high=uint64_t)
    cdef inline uint64_t colorcode(self, uint64_t, uint64_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

@final
cdef class VBKregister:
    cdef uint8_t active_bank

    cdef void set(self, uint8_t) noexcept nogil
    cdef uint8_t get(self) noexcept nogil

@final
cdef class PaletteIndexRegister:
    cdef uint8_t value
    cdef int auto_inc
    cdef int index
    cdef int hl

    cdef void set(self, uint8_t) noexcept nogil
    cdef uint8_t get(self) noexcept nogil
    cdef int getindex(self) noexcept nogil
    cdef void shouldincrement(self) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

@final
cdef class PaletteColorRegister:
    cdef uint16_t[8 * 4] palette_mem
    cdef uint32_t[8 * 4] palette_mem_rgb
    cdef PaletteIndexRegister index_reg

    cdef uint32_t cgb_to_rgb(self, uint16_t, uint8_t) noexcept nogil
    cdef void set(self, uint16_t) noexcept nogil
    cdef uint16_t get(self) noexcept nogil
    cdef inline uint32_t getcolor(self, uint8_t, uint8_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
