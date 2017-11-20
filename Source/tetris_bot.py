#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import traceback
import time
import os.path
import os
import sys
import numpy as np
import platform
from PyBoy.Logger import logger
from PyBoy.WindowEvent import WindowEvent

if platform.system() != "Windows":
    from Debug import Debug
from PyBoy import PyBoy
from PyBoy.GameWindow import SdlGameWindow as Window

def getROM(ROMdir):
    # Give a list of ROMs to start
    found_files = filter(lambda f: f.lower().endswith(
        ".gb") or f.lower().endswith(".gbc"), os.listdir(ROMdir))
    for i, f in enumerate(found_files):
        print ("%s\t%s" % (i + 1, f))
    filename = raw_input("Write the name or number of the tetris ROM file:\n")

    try:
        filename = ROMdir + found_files[int(filename) - 1]
    except:
        filename = ROMdir + filename

    return filename


if __name__ == "__main__":
    # Automatically bump to '-OO' optimizations
    if __debug__:
        os.execl(sys.executable, sys.executable, '-OO', *sys.argv)

    bootROM = None
    ROMdir = "ROMs/"
    scale = 1

    # Verify directories
    if not bootROM is None and not os.path.exists(bootROM):
        print ("Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and len(sys.argv) < 2:
        print ("ROM folder not found. Please copy the Game-ROM to '%s'" % ROMdir)
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 1: # First arg is SDL2/PyGame
            filename = sys.argv[1]
        else:
            filename = getROM(ROMdir)

        # Start PyBoy and run loop
        pyboy = PyBoy(Window(scale=scale), filename, bootROM)
        frame = 0
        while not pyboy.tick():
            print "frame:", frame

            # Start game
            if frame == 144:
                pyboy.sendInput([WindowEvent.PressButtonStart])
            elif frame == 145:
                pyboy.sendInput([WindowEvent.ReleaseButtonStart])
            elif frame == 152:
                pyboy.sendInput([WindowEvent.PressButtonA])
            elif frame == 153:
                pyboy.sendInput([WindowEvent.ReleaseButtonA])
            elif frame == 156:
                pyboy.sendInput([WindowEvent.PressButtonA])
            elif frame == 157:
                pyboy.sendInput([WindowEvent.ReleaseButtonA])
            elif frame == 162:
                pyboy.sendInput([WindowEvent.PressButtonA])
            elif frame == 163:
                pyboy.sendInput([WindowEvent.ReleaseButtonA])

            # Play game
            elif frame >168:
                if frame % 2 == 0:
                    pyboy.sendInput([WindowEvent.PressArrowRight])
                elif frame % 2 == 1:
                    pyboy.sendInput([WindowEvent.ReleaseArrowRight])

            frame += 1
        pyboy.stop()

    except KeyboardInterrupt:
        print ("Interrupted by keyboard")
    except Exception as ex:
        traceback.print_exc()
