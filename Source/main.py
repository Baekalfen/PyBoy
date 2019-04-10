#!/usr/bin/env python3
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import os
import traceback
import sys
from pyboy import PyBoy
from pyboy.logger import addConsoleHandler


addConsoleHandler()


def getROM(ROMdir):
    """Give a list of ROMs to start"""
    found_files = list(filter(lambda f: f.lower().endswith(
        ".gb") or f.lower().endswith(".gbc"), os.listdir(ROMdir)))
    for i, f in enumerate(found_files):
        print("%s\t%s" % (i + 1, f))
    filename = input("Write the name or number of the ROM file:\n")

    try:
        filename = ROMdir + found_files[int(filename) - 1]
    except TypeError:
        filename = ROMdir + filename

    return filename


def main():
    # Automatically bump to '-OO' optimizations
    if __debug__:
        os.execl(sys.executable, sys.executable, '-OO', *sys.argv)

    bootROM = "ROMs/DMG_ROM.bin"
    ROMdir = "ROMs/"
    scale = 3

    # Verify directories
    if bootROM is not None and not os.path.exists(bootROM):
        print("Boot-ROM not found. Please copy the Boot-ROM to '%s'."
              "Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and len(sys.argv) < 2:
        print("ROM folder not found. Please copy the Game-ROM to "
              "'%s'".format(ROMdir))
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 2:  # First arg is SDL2/PyGame
            filename = sys.argv[2]
        else:
            filename = getROM(ROMdir)

        # Start PyBoy and run loop
        pyboy = PyBoy(sys.argv[1] if len(sys.argv) > 1 else None,
                      scale, filename, bootROM)
        while not pyboy.tick():
            pass
        pyboy.stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard")
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
