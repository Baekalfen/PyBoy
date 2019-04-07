#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
# cimport PyBoy.WindowEvent


cimport SDL2 as sdl2
from PyBoy.LCD cimport LCD
from PyBoy.Window.GenericWindow cimport GenericWindow

cdef (int, int, int, int) _dummy_declaration2

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef unsigned char getColorCode(unsigned char, unsigned char, unsigned char)

cdef (int, int) gameboyResolution

cdef class SdlWindow(GenericWindow):
    # cdef tuple makeWindowAndGetBuffer(self, int, int, int, int, char*)

    cdef int ticks
    # cdef list getEvents(self)
    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef uint32_t[144][160] _screenBuffer
    cdef int[144][4] scanlineParameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdlTextureBuffer

    # cdef void setTitle(self, char*)

    @cython.locals(now=cython.int, delay=cython.int)
    cdef void framelimiter(self, int)

    @cython.locals(viewPos=(int, int), windowPos=(int, int))
    cdef void scanline(self, int, LCD)

    @cython.locals(
            y=ushort,
            x=ushort,
            windowViewAddress=ushort,
            backgroundViewAddress=ushort,
            backgroundTileIndex=int,
            windowTileIndex=int,
            xx=int,
            yy=int,
            wx=int,
            wy=int,
            offset=int,
            n=uchar,
            fromXY=(int, int),
            toXY=(int, int),
            tileIndex=uchar,
            attributes=uchar,
            xFlip=bint,
            yFlip=bint,
            spritePriority=bint,
            spriteSize=uchar,
            )
    cdef void renderScreen(self, LCD)

    @cython.locals(
            x1=ushort,
            y1=ushort,
            x2=ushort,
            y2=ushort,
            y=ushort,
            x=ushort,
            yy=ushort,
            xx=ushort,
            pixel=int,
            )
    cdef void copySprite(self, bint, (int, int), (int, int), int, bint, unsigned int, bint, bint)

    # Not directly override updateDisplay. Otherwise we get: "Overriding final methods is not allowed"
    cdef inline void _updateDisplay(self):
        sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, NULL, &self._screenBuffer, 160*4)
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._sdlTextureBuffer,
                NULL,
                NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)


    cdef uint32_t[384 * 8][8] tileCache
    cdef uint32_t[384 * 8][8] spriteCacheOBP0
    cdef uint32_t[384 * 8][8] spriteCacheOBP1


