#!/usr/bin/env python3
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import traceback
import sys
from Source.pyboy import PyBoy
from Source.pyboy.logger import addconsolehandler

addconsolehandler()


def getROM(romdir):
    """Give a list of ROMs to start"""
    found_files = list(filter(lambda f: f.lower().endswith(".gb") or f.lower().endswith(".gbc"), os.listdir(romdir)))
    for i, f in enumerate(found_files):
        print("%s\t%s" % (i + 1, f))
    filename = input("Write the name or number of the ROM file:\n")

    try:
        filename = romdir + found_files[int(filename) - 1]
    except TypeError:
        filename = romdir + filename

    return filename


def main():
    # Automatically bump to '-OO' optimizations
    if __debug__:
        os.execl(sys.executable, sys.executable, '-OO', *sys.argv)

    bootrom = "ROMs/DMG_ROM.bin"
    romdir = "ROMs/"
    scale = 3

    # Verify directories
    if bootrom is not None and not os.path.exists(bootrom):
        print("Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootrom)
        bootrom = None

    if not os.path.exists(romdir) and len(sys.argv) < 2:
        print("ROM folder not found. Please copy the Game-ROM to '%s'".format(romdir))
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 2: # First arg is SDL2/PyGame
            filename = sys.argv[2]
        else:
            filename = getROM(romdir)

        # Start PyBoy and run loop
        pyboy = PyBoy(sys.argv[1] if len(sys.argv) > 1 else None, filename, scale, bootrom)
        while not pyboy.tick():
            pass
        pyboy.stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard")
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
