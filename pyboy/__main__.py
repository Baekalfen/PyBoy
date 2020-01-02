#!/usr/bin/env python3
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import argparse
import base64
import hashlib
import io
import json
import zlib

from pyboy import PyBoy, core
from pyboy.logger import addconsolehandler, logger

parser = argparse.ArgumentParser(
        description='PyBoy -- Game Boy emulator written in Python',
        epilog="Warning: Features marked with (internal use) might be subject to change."
    )
parser.add_argument('ROM', type=str, help='Path to a Game Boy compatible ROM file')
parser.add_argument('-b', '--bootrom', type=str, help='Path to a boot-ROM file')
parser.add_argument('-w', '--window', default='SDL2', type=str,
        help='Specify "window". Options: SDL2 (default), scanline, OpenGL, headless, dummy')
parser.add_argument('-d', '--debug', action='store_true', help='Enable emulator debugging mode')
parser.add_argument('-s', '--scale', default=3, type=int, help='The scaling multiplier for the window')
parser.add_argument('--profiling', action='store_true', help='Enable opcode profiling (internal use)')
parser.add_argument('--autopause', action='store_true', help='Enable auto-pausing when window looses focus')
parser.add_argument('--no-input', action='store_true', help='Disable all user-input (mostly for autonomous testing)')
parser.add_argument('--no-logger', action='store_true', help='Disable all logging (mostly for autonomous testing)')
parser.add_argument('--rewind', action='store_true', help='Enable rewind function')
parser.add_argument('--record-input', type=str, help='Record user input and save to a file (internal use)')
parser.add_argument('-l', '--loadstate', nargs='?', default=None, const='', type=str, help=(
    'Load state from file. If filepath is specified, it will load the given path. Otherwise, it will automatically '
    'locate a saved state next to the ROM file.'))


def main(argv):
    if argv.no_logger:
        logger.disabled = True
    else:
        addconsolehandler()

    if argv.record_input and not argv.loadstate:
        logger.warning("To replay input consistently later, it is required to load a state at boot. This will be"
                       "embedded into the .replay file.")

    # Start PyBoy and run loop
    pyboy = PyBoy(
            argv.ROM,
            window_type=argv.window,
            window_scale=argv.scale,
            bootrom_file=argv.bootrom,
            autopause=argv.autopause,
            debugging=argv.debug,
            profiling=argv.profiling,
            record_input=argv.record_input is not None,
            disable_input=argv.no_input,
            enable_rewind=argv.rewind,
        )

    if argv.loadstate is not None:
        if argv.loadstate != '':
            # Use filepath given
            with open(argv.loadstate, 'rb') as f:
                pyboy.load_state(f)
        else:
            # Guess filepath from ROM path
            with open(argv.ROM+".state", 'rb') as f:
                pyboy.load_state(f)

    while not pyboy.tick():
        pass

    pyboy.stop()

    if argv.profiling:
        print("\n".join(profiling_printer(pyboy._get_cpu_hitrate())))

    if argv.record_input:
        save_replay(argv.ROM, argv.loadstate, argv.record_input, pyboy._get_recorded_input())


def profiling_printer(hitrate):
    print("Profiling report:")
    from operator import itemgetter
    names = [core.opcodes.CPU_COMMANDS[n] for n in range(0x200)]
    for hits, n, name in sorted(
            filter(itemgetter(0), zip(hitrate, range(0x200), names)), reverse=True):
        yield ("%3x %16s %s" % (n, name, hits))


def save_replay(rom, loadstate, replay_file, recorded_input):
    with open(rom, 'rb') as f:
        m = hashlib.sha256()
        m.update(f.read())
        b64_romhash = base64.b64encode(m.digest()).decode('utf8')

    if loadstate is None:
        b64_state = None
    else:
        with open(loadstate, 'rb') as f:
            b64_state = base64.b64encode(f.read()).decode('utf8')

    with open(replay_file, 'wb') as f:
        recorded_data = io.StringIO()
        json.dump([recorded_input, b64_romhash, b64_state], recorded_data)
        f.write(zlib.compress(recorded_data.getvalue().encode('ascii')))


if __name__ == "__main__":
    main(parser.parse_args())
