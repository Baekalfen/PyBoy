#!/usr/bin/env python3
#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import argparse
import copy
import os

from pyboy import PyBoy
from pyboy.plugins.manager import parser_arguments
from pyboy.pyboy import defaults

INTERNAL_LOADSTATE = "INTERNAL_LOADSTATE_TOKEN"


def color_tuple(string):
    color_palette = [int(c.strip(), 16) for c in string.split(",")]
    if not (len(color_palette) == 4):
        parser.error(f"Not the correct amount of colors! Expected four, got {len(color_palette)}")
    return color_palette


def cgb_color_tuple(string):
    color_palette = [int(c.strip(), 16) for c in string.split(",")]
    if not (len(color_palette) == 12):
        parser.error(f"Not the correct amount of colors! Expected twelve, got {len(color_palette)}")
    return [color_palette[0:4], color_palette[4:8], color_palette[8:12]]


def valid_file_path(path):
    if not path == INTERNAL_LOADSTATE and not os.path.isfile(path):
        parser.error(f"Filepath '{path}' couldn't be found, or isn't a file!")
    return path


def valid_volume(vol):
    if isinstance(vol, bool):
        return 100 if vol else 0
    elif vol.isnumeric() and (0 <= int(vol) <= 100):
        return int(vol)
    else:
        parser.error("Invalid volume")


def valid_sample_rate(freq):
    if freq.isnumeric() and int(freq) % 60 == 0:
        return int(freq)
    else:
        parser.error("Invalid sample rate")


parser = argparse.ArgumentParser(
    description="PyBoy -- Game Boy emulator written in Python",
    epilog="Warning: Features marked with (internal use) might be subject to change.",
)
parser.add_argument("ROM", type=valid_file_path, help="Path to a Game Boy compatible ROM file")
parser.add_argument("-b", "--bootrom", dest="bootrom", type=valid_file_path, help="Path to a boot-ROM file")
parser.add_argument("--no-input", action="store_true", help="Disable all user-input (mostly for autonomous testing)")
parser.add_argument(
    "--log-level",
    default=defaults["log_level"],
    type=str,
    choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    help="Set logging level",
)
parser.add_argument(
    "--color-palette",
    type=color_tuple,
    default=defaults["color_palette"],
    help=('Four comma seperated, hexadecimal, RGB values for colors (i.e. "FFFFFF,999999,555555,000000")'),
)
parser.add_argument(
    "--cgb-color-palette",
    type=cgb_color_tuple,
    default=defaults["cgb_color_palette"],
    help=(
        'Three sets of four comma seperated, hexadecimal, RGB values for colors in the order of: background, obj0, obj1 (i.e. "FFFFFF,7BFF31,0063C5,000000,FFFFFF,FF8484,FF8484,000000,FFFFFF,FF8484,FF8484,000000")'
    ),
)
parser.add_argument(
    "-l",
    "--loadstate",
    nargs="?",
    default=None,
    const=INTERNAL_LOADSTATE,
    type=valid_file_path,
    help=(
        "Load state from file. If filepath is specified, it will load the given path. Otherwise, it will automatically "
        "locate a saved state next to the ROM file."
    ),
)
parser.add_argument(
    "-w",
    "--window",
    default=defaults["window"],
    type=str,
    choices=["SDL2", "OpenGL", "null"],
    help="Specify window-type to use",
)
parser.add_argument("-s", "--scale", default=defaults["scale"], type=int, help="The scaling multiplier for the window")
parser.add_argument("--no-renderer", action="store_true", help="Disable rendering (internal use)")
parser.add_argument(
    "--gameshark",
    type=str,
    help="Add GameShark cheats on start-up. Add multiple by comma separation (i.e. '010138CD, 01033CD1')",
)

gameboy_type_parser = parser.add_mutually_exclusive_group()
gameboy_type_parser.add_argument(
    "--dmg", action="store_const", const=False, dest="cgb", help="Force emulator to run as original Game Boy (DMG)"
)
gameboy_type_parser.add_argument(
    "--cgb", action="store_const", const=True, dest="cgb", help="Force emulator to run as Game Boy Color"
)

# NOTE: Inverted logic on variable
parser.add_argument(
    "--no-sound-emulation",
    default=True,
    action="store_false",
    dest="sound_emulated",
    help="Disables sound emulation (not just muted!)",
)

sound_parser = parser.add_mutually_exclusive_group()

sound_parser.add_argument(
    "--sound",
    action="store_const",
    const=100,
    dest="sound_volume",
    help="Deprecated setting. Now sets sound volume to 100%%. See '--sound-volume'",
)
sound_parser.add_argument(
    "--sound-volume",
    default=100,
    type=valid_volume,
    help="Set sound volume in percent (0-100)",
)
parser.set_defaults(sound_volume=100)

parser.add_argument(
    "--sound-sample-rate",
    default=None,
    type=valid_sample_rate,
    help="Set sound sample rate. Has to be divisible in 60.",
)

parser.add_argument("--title-status", action="store_true", help="Enable performance status in window title")

for arguments in parser_arguments():
    for a in arguments:
        *args, kwargs = a
        if args[0] not in parser._option_string_actions:
            parser.add_argument(*args, **kwargs)


def main():
    argv = parser.parse_args()

    print(
        """
The Game Boy controls are as follows:

| Keyboard key | GameBoy equivalant |
| ---          | ---                |
| Up           | Up                 |
| Down         | Down               |
| Left         | Left               |
| Right        | Right              |
| A            | A                  |
| S            | B                  |
| Return       | Start              |
| Backspace    | Select             |

The other controls for the emulator:

| Keyboard key | Emulator function       |
| ---          | ---                     |
| F11          | Toggle fullscreen       |
| Escape       | Quit                    |
| D            | Debug                   |
| Space        | Unlimited FPS           |
| Z            | Save state              |
| X            | Load state              |
| I            | Toggle screen recording |
| O            | Save screenshot         |
| ,            | Rewind backwards        |
| .            | Rewind forward          |
| J            | Memory Window + 0x100   |
| K            | Memory Window - 0x100   |
| Shift + J    | Memory Window + 0x1000  |
| Shift + K    | Memory Window - 0x1000  |

See "pyboy --help" for how to enable rewind and other awesome features!
"""
    )

    # Start PyBoy and run loop
    kwargs = copy.deepcopy(vars(argv))
    kwargs.pop("ROM", None)
    kwargs.pop("loadstate", None)
    kwargs.pop("no_renderer", None)
    pyboy = PyBoy(argv.ROM, **kwargs)

    if argv.loadstate is not None:
        if argv.loadstate == INTERNAL_LOADSTATE:
            # Guess filepath from ROM path
            state_path = argv.ROM + ".state"
        else:
            # Use filepath given
            state_path = argv.loadstate

        valid_file_path(state_path)
        with open(state_path, "rb") as f:
            pyboy.load_state(f)

    while pyboy.tick():
        pass

    pyboy.stop()


if __name__ == "__main__":
    main()
