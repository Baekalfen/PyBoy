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

if platform.system() != "Windows":
    from Debug import Debug
from PyBoy import PyBoy


def getWindow():
    if len(sys.argv) < 2:
        from PyBoy.GameWindow import SdlGameWindow as Window
    elif sys.argv[1] == "SDL2":
        from PyBoy.GameWindow import SdlGameWindow as Window
    elif sys.argv[1] == "dummy":
        from PyBoy.GameWindow import DummyGameWindow as Window
    else:
        print "Invalid arguments!"
        exit(1)

    return Window


def getROM(ROMdir):
    # Give a list of ROMs to start
    found_files = filter(lambda f: f.lower().endswith(
        ".gb") or f.lower().endswith(".gbc"), os.listdir(ROMdir))
    for i, f in enumerate(found_files):
        print ("%s\t%s" % (i + 1, f))
    filename = raw_input("Write the name or number of the ROM file:\n")

    try:
        filename = ROMdir + found_files[int(filename) - 1]
    except:
        filename = ROMdir + filename

    return filename

if __name__ == "__main__":
    # Automatically bump to '-OO' optimizations
    if __debug__:
        os.execl(sys.executable, sys.executable, '-OO', *sys.argv)

    bootROM = "ROMs/DMG_ROM.bin"
    ROMdir = "ROMs/"
    scale = 1
    debug = "debug" in sys.argv and platform.system() != "Windows"

    # Verify directories
    if not bootROM is None and not os.path.exists(bootROM):
        print ("Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and len(sys.argv) < 2:
        print ("ROM folder not found. Please copy the Game-ROM to '%s'" % ROMdir)
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 2: # First arg is SDL2/PyGame
            filename = sys.argv[2]
        else:
            filename = getROM(ROMdir)

        # Start PyBoy and run loop
        pyboy = PyBoy((getWindow())(scale=scale), filename, bootROM)
        while not pyboy.tick():
            pass
        pyboy.stop()

    except KeyboardInterrupt:
        print ("Interrupted by keyboard")
    except Exception as ex:
        traceback.print_exc()
        # time.sleep(10)
    # finally:
    #     if debugger:
    #         logger.info("Debugger ready for shutdown")
    #         time.sleep(10)
    #         debugger.quit()
