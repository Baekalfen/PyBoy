#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import argparse
import traceback
import time
import os
import sys
import platform
from PyBoy import GameWindow
from PyBoy.Logger import logger, addConsoleHandler


addConsoleHandler()


if platform.system() != "Windows":
    from Debug import Debug
from PyBoy import PyBoy


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


def parse_arguments(argstring=None):

    parser = argparse.ArgumentParser(description="A Python Gameboy Emulator")

    parser.add_argument("romfile", type=str, help="path to Gameboy ROM")
    parser.add_argument("--window",
                        choices=GameWindow.windowTypes,
                        default=GameWindow.defaultWindowType,
                        help="Name of a valid Game Window implementation. "
                        "Choices: " + ", ".join(GameWindow.windowTypes))
    parser.add_argument("--debug", help="Enable debug mode",
                        action='store_true')
    parser.add_argument("--profiling", help="Enable profiling",
                        action="store_true")
    parser.add_argument("--loadState", help="Load state from .state file",
                        action="store_true")

    return vars(parser.parse_args())


def main(romfile=None, window=None, debug=False, profiling=False,
         loadState=False):

    # Automatically bump to '-OO' optimizations
    if __debug__:
        os.execl(sys.executable, sys.executable, '-OO', *sys.argv)

    bootROM = "ROMs/DMG_ROM.bin"
    ROMdir = "ROMs/"

    # Verify directories
    if not bootROM is None and not os.path.exists(bootROM):
        print ("Boot-ROM not found. Please copy the Boot-ROM to '%s'. "
               "Some games are known to not work without it. "
               "Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and not romfile:
        print ("ROM folder not found. Please copy the Game ROM to '%s'" %
               ROMdir)
        return

    if not romfile:
        romfile = getROM(ROMdir)
    
    try:
        # Start PyBoy and run loop
        pyboy = PyBoy(window, romfile, bootROM)
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


if __name__ == "__main__":
    arguments = parse_arguments()
    main(**arguments)

    #import cProfile
    #cProfile.run('main()', sort='cumulative')
