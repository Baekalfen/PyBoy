# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GLUT.freeglut

from .. import CoreDump
from ..MathUint8 import getSignedInt8
from ..WindowEvent import WindowEvent
from ..GameWindow import AbstractGameWindow

from ..Logger import logger

gameboyResolution = (160, 144)
w,h = gameboyResolution

def get_color_code(byte1,byte2,offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code

alphaMask = 0x0000007F
tiles = 384

class OpenGLGameWindow(AbstractGameWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

        if self._scale != 1:
            logger.warn("Scaling set to %s. The implementation is temporary, which means scaling above 1 will impact performance." % self._scale)


        self.tile_cache = np.ndarray((tiles * 8, 8), dtype='int32')
        self.sprite_cacheOBP0 = np.ndarray((tiles * 8, 8), dtype='int32')
        self.sprite_cacheOBP1 = np.ndarray((tiles * 8, 8), dtype='int32')

        self.color_palette = (0xFFFFFF00,0x99999900,0x55555500,0x00000000)


        self.debug = False

        CoreDump.windowHandle = self

        logger.debug("OpenGL GameWindow initialization")
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(*tuple([x*self._scale for x in gameboyResolution]))
        glutInitWindowPosition(100,100)
        glutCreateWindow("PyBoy")
        glutKeyboardFunc(lambda c,x,y: self.glKeyboard(c,x,y,False,False,))
        glutKeyboardUpFunc(lambda c,x,y: self.glKeyboard(c,x,y,False,True))
        glutSpecialFunc(lambda c,x,y: self.glKeyboard(c,x,y,True,False))
        glutSpecialUpFunc(lambda c,x,y: self.glKeyboard(c,x,y,True, True))
        self.events = []

        glPixelZoom(self._scale,self._scale)
        self._scaledResolution = tuple(x * self._scale for x in gameboyResolution)
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledResolution))


        self._screenBuffer = np.ndarray(shape=gameboyResolution, dtype='uint32')
        self._screenBuffer.fill(0x00558822)

        self.scanlineParameters = np.ndarray(shape=(gameboyResolution[0],4), dtype='uint8')

        glutReshapeFunc(self.glReshape)
        glutDisplayFunc(self.glDraw)

    def dump(self,filename):
        pass

    def setTitle(self,title):
        glutSetWindowTitle(title)

    def getEvents(self):
        evts = self.events[:]
        self.events = []
        return evts

    def glKeyboard(self, c, x, y, special, up):
        if special:
            if up:
                if c == GLUT_KEY_UP:
                    self.events.append(WindowEvent.ReleaseArrowUp)
                if c == GLUT_KEY_DOWN:
                    self.events.append(WindowEvent.ReleaseArrowDown)
                if c == GLUT_KEY_LEFT:
                    self.events.append(WindowEvent.ReleaseArrowLeft)
                if c == GLUT_KEY_RIGHT:
                    self.events.append(WindowEvent.ReleaseArrowRight)
            else:
                if c == GLUT_KEY_UP:
                    self.events.append(WindowEvent.PressArrowUp)
                if c == GLUT_KEY_DOWN:
                    self.events.append(WindowEvent.PressArrowDown)
                if c == GLUT_KEY_LEFT:
                    self.events.append(WindowEvent.PressArrowLeft)
                if c == GLUT_KEY_RIGHT:
                    self.events.append(WindowEvent.PressArrowRight)

        else:
            if up:
                if c == 'a':
                    self.events.append(WindowEvent.ReleaseButtonA)
                elif c == 's':
                    self.events.append(WindowEvent.ReleaseButtonB)
                elif c == 'z':
                    self.events.append(WindowEvent.SaveState)
                elif c == 'x':
                    self.events.append(WindowEvent.LoadState)
                elif c == ' ':
                    self.events.append(WindowEvent.ReleaseSpeedUp)
                elif c == chr(8):
                    self.events.append(WindowEvent.ReleaseButtonSelect)
                elif c == chr(13):
                    self.events.append(WindowEvent.ReleaseButtonStart)
            else:
                # if c == 'e':
                #     self.debug = True
                if c == 'a':
                    self.events.append(WindowEvent.PressButtonA)
                elif c == 's':
                    self.events.append(WindowEvent.PressButtonB)
                elif c == chr(27):
                    self.events.append(WindowEvent.Quit)
                elif c == 'd':
                    self.events.append(WindowEvent.DebugToggle)
                elif c == ' ':
                    self.events.append(WindowEvent.PressSpeedUp)
                elif c == 'i':
                    self.events.append(WindowEvent.ScreenRecordingToggle)
                elif c == chr(8):
                    self.events.append(WindowEvent.PressButtonSelect)
                elif c == chr(13):
                    self.events.append(WindowEvent.PressButtonStart)


    def glReshape(self, width, height):
        self._scale = max(min(float(height)/gameboyResolution[1], float(width)/gameboyResolution[0]), 1)
        # self._scale = int(self._scale*10)/10. # One decimal

        self._scaledResolution = tuple(int(x * self._scale) for x in gameboyResolution)
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledResolution))
        glPixelZoom(self._scale,self._scale)
        # glutReshapeWindow(*self._scaledResolution);

    def glDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawPixels(w,h, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, self._screenBuffer.transpose()[::-1,:])
        glFlush()

    def updateDisplay(self):
        self.glDraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def frameLimiter(self):
        pass

    def stop(self):
        pass

    def scanline(self, y, lcd):
        self.scanlineParameters[y] = lcd.get_view_port() + lcd.get_window_pos()

    def renderScreen(self, lcd):
        self.refreshTileData(lcd)

        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        backgroundViewAddress = 0x1800 if lcd.LCDC.background_map_select == 0 else 0x1C00
        windowViewAddress = 0x1800 if lcd.LCDC.window_map_select == 0 else 0x1C00

        for y in xrange(gameboyResolution[1]):
            xx, yy, wx, wy = self.scanlineParameters[y]
            # xx, yy = lcd.getViewPort()
            offset = xx & 0b111 # Used for the half tile at the left side when scrolling

            for x in xrange(gameboyResolution[0]):
                if lcd.LCDC.background_enable:
                    backgroundTileIndex = lcd.VRAM[backgroundViewAddress + (((xx + x)/8)%32 + ((y+yy)/8)*32)%0x400]

                    if lcd.LCDC.tile_select == 0: # If using signed tile indices
                        backgroundTileIndex = getSignedInt8(backgroundTileIndex)+256

                    self._screenBuffer[x,y] = self.tile_cache[backgroundTileIndex*8 + (x+offset)%8, (y+yy)%8]
                else:
                    # If background is disabled, it becomes white
                    self._screenBuffer[x,y] = self.color_palette[0]

                if lcd.LCDC.window_enabled:
                    # wx, wy = lcd.get_window_pos()
                    if wy <= y and wx <= x:
                        windowTileIndex = lcd.VRAM[windowViewAddress + (((x-wx)/8)%32 + ((y-wy)/8)*32)%0x400]

                        if lcd.LCDC.tile_select == 0: # If using signed tile indices
                            windowTileIndex = getSignedInt8(windowTileIndex)+256

                        self._screenBuffer[x,y] = self.tile_cache[windowTileIndex*8 + (x-(wx))%8, (y-wy)%8]

        ### RENDER SPRITES
        # Doesn't restrict 10 sprite pr. scan line.
        # Prioritizes sprite in inverted order
        # logger.debug("Rendering Sprites")
        spriteSize = 16 if lcd.LCDC.sprite_size else 8
        BGPkey = lcd.BGP.get_color(0)

        for n in xrange(0x00,0xA0,4):
            y = lcd.OAM[n] - 16 #TODO: Simplify reference
            x = lcd.OAM[n+1] - 8
            tileIndex = lcd.OAM[n+2]
            attributes = lcd.OAM[n+3]
            xFlip = bool(attributes & 0b100000)
            yFlip = bool(attributes & 0b1000000)
            spritePriority = bool(attributes & 0b10000000)

            fromXY = (tileIndex * 8, 0)
            toXY = (x, y)

            sprite_cache = self.sprite_cacheOBP1 if attributes & 0b10000 else self.sprite_cacheOBP0

            if x < 160 and y < 144:
                self.copySprite(fromXY, toXY, sprite_cache, self._screenBuffer, spriteSize, spritePriority, BGPkey, xFlip, yFlip)


    def refreshTileData(self, lcd):
        if self.flush_cache:
            self.tiles_changed.clear()
            for x in xrange(0x8000,0x9800,16):
                self.tiles_changed.add(x)
            self.flush_cache = False

        for t in self.tiles_changed:
            t -= 0x8000
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = lcd.VRAM[t+k]
                byte2 = lcd.VRAM[t+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = t/2 + 7-pixelOnLine

                    color_code = get_color_code(byte1, byte2, pixelOnLine)

                    self.tile_cache[x, y] = lcd.BGP.get_color(color_code)
                    # TODO: Find a more optimal way to do this
                    alpha = 0x00000000
                    if color_code == 0:
                        alpha = alphaMask # Add alpha channel
                    self.sprite_cacheOBP0[x, y] = lcd.OBP0.get_color(color_code) + alpha
                    self.sprite_cacheOBP1[x, y] = lcd.OBP1.get_color(color_code) + alpha

        self.tiles_changed.clear()

    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, spriteSize, spritePriority, BGPkey, xFlip = 0, yFlip = 0):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(spriteSize):
            yy = ((spriteSize-1)-y) if yFlip else y
            yy %= 8
            for x in xrange(8):
                xx = x1 # Base coordinate
                xx += ((7-x) if xFlip else x) # Reverse order, if sprite is x-flipped

                if spriteSize == 16: # If y-flipped on 8x16 sprites, we will have to load the sprites in reverse order
                    xx += (y&0b1000)^(yFlip<<3) # Shifting tile, when iteration past 8th line

                pixel = fromBuffer[xx, yy]

                if 0 <= x2+x < 160 and 0 <= y2+y < 144:
                    if not (not spritePriority or (spritePriority and toBuffer[x2+x, y2+y] == BGPkey)):
                        pixel += alphaMask # Add a fake alphachannel to the sprite for BG pixels.
                                            # We can't just merge this with the next if, as
                                            # sprites can have an alpha channel in other ways

                    if not (pixel & alphaMask):
                        toBuffer[x2+x, y2+y] = pixel


    def blankScreen(self):
        # If the screen is off, fill it with a color.
        if __debug__:
            # Currently, it's dark purple
            self._screenBuffer.fill(0x00403245)
        else:
            # Pan docs says it should be white, but it does fit with Pokemon?
            # self._screenBuffer.fill(0x00FFFFFF)
            self._screenBuffer.fill(0x00000000)


    def getScreenBuffer(self):
        return self._screenBuffer.get_buffer()

