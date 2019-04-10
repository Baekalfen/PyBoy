#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t

cimport sdl2 as sdl2
from pyboy.lcd cimport LCD
from pyboy.window.genericwindow cimport GenericWindow


cdef (int, int) gameboyResolution
cdef uint32_t[4] palette
cdef dict windowEventsDown
cdef dict windowEventsUp


cdef class ScanlineWindow(GenericWindow):

    cdef sdl2.SDL_Window* _window
    cdef sdl2.SDL_Renderer* _sdlrenderer
    cdef sdl2.SDL_Texture* _screenbuf

    cdef uint32_t[160] _linebuf
    cdef sdl2.SDL_Rect _linerect

    cdef uint32_t ticks
    cdef int scale

    @cython.profile(False)
    @cython.locals(now=uint32_t, delay=int)
    cdef void framelimiter(self, int)

    @cython.locals(
        bOffset=int,
        wOffset=int,
        bx=int,
        by=int,
        wx=int,
        wy=int,
        bdy=int,
        wdy=int,
        tile_select=bint,
        window_enabled_and_y=bint,
        bgp=uint32_t[4],
        obp0 = uint32_t[4],
        obp1 = uint32_t[4],
        bt=int,
        wt=int,
        sprites=int[10],
        nsprites=int,
        ymin=int,
        ymax=int,
        x=int,
        n=int,
        sx=int,
        sy=int,  # These maybe should be uint8_t, since they're
        st=int,  # getting unpacked from an array of bytes, but then
        sf=int,  # the operations would have to be overflow safe.
        dy=int,
        dx=int,
        bbyte0=uint8_t,
        bbyte1=uint8_t,
        sbyte0=uint8_t,
        sbyte1=uint8_t,
        bpixel=int,
        spixel=int
        )
    cdef void scanline(self, int, LCD)

    cdef inline void _scanlineCopy(self):
        sdl2.SDL_UpdateTexture(self._screenbuf,
                               &self._linerect,
                               &self._linebuf,
                               160)

    cdef inline void _renderCopy(self):
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._screenbuf,
                NULL,
                NULL)

    cdef inline void _renderPresent(self):
        sdl2.SDL_RenderPresent(self._sdlrenderer)
