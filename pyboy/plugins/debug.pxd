#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from cpython.array cimport array
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

cimport pyboy.plugins.window_sdl2
from pyboy.api.tilemap cimport TileMap
from pyboy.api.tile cimport Tile
from pyboy.api.sprite cimport Sprite
from pyboy.core.lcd cimport Renderer
from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
from pyboy.utils cimport WindowEvent

cdef uint64_t COLS, ROWS, TILES, VRAM_OFFSET, HIGH_TILEMAP, SPRITES
cdef uint32_t COLOR, COLOR_BACKGROUND, SPRITE_BACKGROUND, COLOR_WINDOW

cdef Logger logger

cdef uint32_t COLOR
cdef uint32_t MASK
cdef uint32_t HOVER
cdef int mark_counter
cdef set marked_tiles
cdef uint32_t[:] MARK


cdef class MarkedTile:
    cdef public int tile_identifier
    cdef str mark_id
    cdef public uint32_t mark_color
    cdef int sprite_height


cdef class Debug(PyBoyWindowPlugin):
    cdef dict rom_symbols
    cdef TileViewWindow tile1
    cdef TileViewWindow tile2
    cdef SpriteViewWindow spriteview
    cdef SpriteWindow sprite
    cdef TileDataWindow tiledata0
    cdef TileDataWindow tiledata1
    cdef MemoryWindow memory
    cdef GameAreaWindow gamearea
    cdef bint sdl2_event_pump


cdef class BaseDebugWindow(PyBoyWindowPlugin):
    cdef int width
    cdef int height
    cdef int hover_x
    cdef int hover_y
    cdef str base_title
    cdef int window_id

    cdef object _window
    cdef object _sdlrenderer
    cdef object _sdltexturebuffer
    cdef uint32_t[:,:] buf0
    cdef uint8_t[:,:] buf0_attributes
    cdef object buf_p

    @cython.locals(y=int, x=int, _y=int, _x=int)
    cdef void copy_tile(self, uint8_t[:, :, :], int, int, int, int, uint32_t[:,:], bint, bint, uint32_t[:]) noexcept

    @cython.locals(i=int, tw=int, th=int, xx=int, yy=int)
    cdef void mark_tile(self, int, int, uint32_t, int, int, bint) noexcept

    @cython.locals(event=WindowEvent)
    cdef list handle_events(self, list)


cdef class TileViewWindow(BaseDebugWindow):
    cdef int scanline_x
    cdef int scanline_y
    cdef TileMap tilemap
    cdef uint32_t color

    # cdef uint8_t[:,:] tilecache # Fixing Cython locals
    cdef uint32_t[4] palette_rgb
    @cython.locals(
        mem_offset=uint16_t,
        tile_index=int,
        tile_column=int,
        tile_row=int,
        tile_num = uint8_t,
        palette = uint8_t,
        vbank = uint8_t,
        horiflip = uint8_t,
        vertflip = uint8_t,
        bg_priority = uint8_t,
        color = int,
    )
    cdef void post_tick(self) noexcept

    # scanlineparameters=uint8_t[:,:],
    @cython.locals(x=int, y=int, xx=int, yy=int, row=int, column=int, background_view=bint, t=MarkedTile)
    cdef void draw_overlay(self) noexcept

    @cython.locals(tile_x=int, tile_y=int, tile_identifier=int)
    cdef list handle_events(self, list)


cdef class TileDataWindow(BaseDebugWindow):
    cdef bint tilecache_select

    # cdef uint8_t[:,:] tilecache # Fixing Cython locals
    cdef uint32_t[4] palette_rgb
    @cython.locals(t=int, xx=int, yy=int, color=int)
    cdef void post_tick(self) noexcept

    @cython.locals(tile_x=int, tile_y=int, tile_identifier=int)
    cdef list handle_events(self, list)

    @cython.locals(t=MarkedTile, column=int, row=int)
    cdef void draw_overlay(self) noexcept


cdef class SpriteWindow(BaseDebugWindow):
    @cython.locals(tile_x=int, tile_y=int, sprite_identifier=int, sprite=object)
    cdef list handle_events(self, list)

    @cython.locals(m=MarkedTile, xx=int, yy=int, sprite=object, i=int, sprite_index=int)
    cdef void draw_overlay(self) noexcept

    @cython.locals(title=str)
    cdef void update_title(self) noexcept

    # cdef uint8_t[:,:] spritecache # Fixing Cython locals
    cdef uint32_t[4] palette_rgb
    @cython.locals(color=int)
    cdef void post_tick(self) noexcept

cdef class SpriteViewWindow(BaseDebugWindow):
    @cython.locals(t=int, x=int, y=int)
    cdef void post_tick(self) noexcept

    @cython.locals(m=MarkedTile, sprite=Sprite, i=int, sprite_index=int)
    cdef void draw_overlay(self) noexcept

    @cython.locals(title=str)
    cdef void update_title(self) noexcept


cdef class MemoryWindow(BaseDebugWindow):
    cdef int NCOLS, NROWS
    cdef bint shift_down
    cdef int start_address
    cdef uint8_t[:] _text_buffer_raw
    cdef uint8_t[:,:] text_buffer
    cdef object font_texture
    cdef array fbuf
    cdef uint32_t[:,:] fbuf0
    cdef object fbuf_p
    cdef object src, dst
    cdef int[3] fg_color
    cdef int[3] bg_color

    cdef void write_border(self) noexcept
    # @cython.locals(header=uint8_t[:], addr=uint8_t[:])
    cdef void write_addresses(self) noexcept
    # @cython.locals(a=uint8_t[:])
    cdef void write_memory(self) noexcept
    @cython.locals(text=uint8_t[:])
    cdef void render_text(self) noexcept
    @cython.locals(i=int, c=uint8_t)
    cdef void draw_text(self, int, int, uint8_t[:]) noexcept
    cdef void _scroll_view(self, int)


cdef class GameAreaWindow(BaseDebugWindow):
    cdef TileMap tilemap
    cdef int display_mode
    cdef int screen_x
    cdef int screen_y
    cdef int area_x
    cdef int area_y
    cdef uint32_t[4] palette_rgb

    @cython.locals(area_width=int, area_height=int, area_left=int, area_top=int, left=int, top=int, right=int, bottom=int)
    cdef tuple _layout(self, tuple, tuple, int, bint)

    @cython.locals(
        tile_index=int,
        tile_column=int,
        tile_row=int,
        palette=uint8_t,
        vbank=uint8_t,
        horiflip=uint8_t,
        vertflip=uint8_t,
        bg_priority=uint8_t,
        color=int,
    )
    cdef void _render_background(self, int, int, int, int, int) noexcept

    @cython.locals(x=int, y=int, value=int)
    cdef void _render_mapping(self, object) noexcept

    @cython.locals(x=int, y=int, digit=object, offset=int)
    cdef void _draw_number(self, int, int, int) noexcept

    @cython.locals(y=int, x=int)
    cdef void _render_screen(self, int, int) noexcept

    @cython.locals(title=str)
    cdef void update_title(self) noexcept

    cdef list handle_events(self, list)
    cdef void post_tick(self) noexcept
