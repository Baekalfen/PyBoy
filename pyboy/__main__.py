#!/usr/bin/env python3
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import argparse

from pyboy import PyBoy, core
from pyboy.logger import addconsolehandler, logger
from pyboy.plugins.manager import get_parser_arguments

parser = argparse.ArgumentParser(
        description='PyBoy -- Game Boy emulator written in Python',
        epilog="Warning: Features marked with (internal use) might be subject to change.",
        # argument_default=argparse.SUPPRESS,
    )
parser.add_argument('ROM', type=str, help='Path to a Game Boy compatible ROM file')
parser.add_argument('-b', '--bootrom', type=str, help='Path to a boot-ROM file')
parser.add_argument('--profiling', action='store_true', help='Enable opcode profiling (internal use)')
parser.add_argument('--no-logger', action='store_true', help='Disable all logging (mostly for autonomous testing)')
parser.add_argument('--color-palette', type=str, help=(
    'Four comma seperated, hexadecimal, RGB values for colors (i.e. "FFFFFF,999999,555555,000000")'))
parser.add_argument('-l', '--loadstate', nargs='?', default=None, const='', type=str, help=(
    'Load state from file. If filepath is specified, it will load the given path. Otherwise, it will automatically '
    'locate a saved state next to the ROM file.'))

# parser.set_defaults(bar=42, baz='badger')

for arguments in get_parser_arguments():
    for a in arguments:
        *args, kwargs = a
        parser.add_argument(*args, **kwargs)


def main():
    argv = parser.parse_args()
    if argv.no_logger:
        logger.disabled = True
    else:
        addconsolehandler()

    kwargs = vars(argv) # Extract dictionary of arguments

    # Add these, only if defined, as we otherwise want the PyBoy default
    if argv.color_palette is not None:
        color_palette = [int(c.strip(), 16) for c in argv.color_palette.split(',')]
        assert len(color_palette) == 4, f"Not the correct amount of colors! Expected four, got {len(color_palette)}"
        kwargs['color_palette'] = color_palette
    else:
        kwargs.pop('color_palette')

    # Start PyBoy and run loop
    pyboy = PyBoy(
            kwargs.pop('ROM', None),
            # argv.ROM,
            # window_type=argv.window,
            # window_scale=argv.scale,
            # bootrom_file=argv.bootrom,
            # autopause=argv.autopause,
            # debugging=argv.debug,
            # profiling=argv.profiling,
            # disable_input=argv.no_input,
            # enable_rewind=argv.rewind,
            **kwargs
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


def profiling_printer(hitrate):
    print("Profiling report:")
    from operator import itemgetter
    names = [core.opcodes.CPU_COMMANDS[n] for n in range(0x200)]
    for hits, n, name in sorted(
            filter(itemgetter(0), zip(hitrate, range(0x200), names)), reverse=True):
        yield ("%3x %16s %s" % (n, name, hits))


if __name__ == "__main__":
    main()
