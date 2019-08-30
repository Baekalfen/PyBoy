#!/usr/bin/env python3
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys
import traceback

from pyboy import PyBoy
from pyboy.logger import addconsolehandler, logger

addconsolehandler()

if "--no-logger" in sys.argv:
    logger.disabled = True

argv_debug = "--debug" in sys.argv
argv_profiling = "--profiling" in sys.argv
argv_autopause = "--autopause" in sys.argv
argv_disable_input = "--no-input" in sys.argv

# TODO: Find a library to take care of argv
argv_load_state_file = None
argv_loadstate = "--loadstate" in sys.argv
if argv_loadstate:
    idx = sys.argv.index("--loadstate")
    assert len(sys.argv) > idx+1
    argv_load_state_file = sys.argv[idx+1]
    assert argv_load_state_file[0] != '-', "Load state file looks like an argument"

argv_record_input_file = None
argv_record_input = "--record-input" in sys.argv
if argv_record_input:
    assert not argv_disable_input
    idx = sys.argv.index("--record-input")
    assert len(sys.argv) > idx+1
    argv_record_input_file = sys.argv[idx+1]
    assert argv_record_input_file[0] != '-', "Output file looks like an argument"


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
        pyboy = PyBoy(
                filename,
                window_type=(sys.argv[1] if len(sys.argv) > 1 else None),
                window_scale=scale,
                bootrom_file=bootrom,
                autopause=argv_autopause,
                loadstate_file=argv_load_state_file, # Needs filename
                debugging=argv_debug,
                profiling=argv_profiling,
                record_input_file=argv_record_input_file,
                disable_input=argv_disable_input,
            )
        while not pyboy.tick():
            pass
        pyboy.stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard")
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
