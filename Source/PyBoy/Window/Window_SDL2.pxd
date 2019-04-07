#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from cpython.array cimport array
from array import array

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

    cdef uint32_t ticks
    # cdef list getEvents(self)
    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef array _screenBuffer
    cdef array _tileCache, _spriteCacheOBP0, _spriteCacheOBP1
    cdef uint32_t[:,:] screenBuffer
    cdef uint32_t[:,:] tileCache, spriteCacheOBP0, spriteCacheOBP1

    cdef uint8_t[144][4] scanlineParameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdlTextureBuffer

    # cdef void setTitle(self, char*)

    @cython.locals(now=uint32_t, delay=cython.int)
    cdef void framelimiter(self, int)

    @cython.locals(viewPos=(int, int), windowPos=(int, int))
    cdef void scanline(self, int, LCD)

    @cython.locals(
            y=int,
            x=int,
            windowViewAddress=int,
            backgroundViewAddress=int,
            backgroundTileIndex=int,
            windowTileIndex=int,
            bx=int,
            by=int,
            wx=int,
            wy=int,
            offset=int,
            BGPkey=uint32_t,
            spriteSize=int,
            n=int,
            tileIndex=int,
            attributes=int,
            xFlip=bint,
            yFlip=bint,
            spritePriority=bint,
            spriteCache=uint32_t[:,:],
            dy=int,
            dx=int,
            yy=int,
            xx=int,
            pixel=uint32_t,
            )
    cdef void renderScreen(self, LCD)

    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorCode=uint32_t,
        alpha=uint32_t
        )
    cdef void updateCache(self, LCD)

    cdef inline void _updateDisplay(self):
        sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, NULL,
                               self._screenBuffer.data.as_voidptr, 160*4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdlTextureBuffer,
                            NULL, NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)

