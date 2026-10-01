#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Run a headless pair and save both emulators and the wire together.

python extras/examples/link_cable.py left.gb right.gb --save pair.state
python extras/examples/link_cable.py left.gb right.gb --load pair.state --save next.state

Input/strategy is deliberately left to the caller; this example does not initiate
an in-game trade. Read each screen/sound buffer after cable.tick() to stream it.
"""

import argparse
import io
from pathlib import Path

from pyboy import LinkCable, PyBoy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--load", type=Path)
    parser.add_argument("--save", type=Path, required=True)
    args = parser.parse_args()
    machines = []
    try:
        for path in (args.left, args.right):
            machine = PyBoy(io.BytesIO(path.read_bytes()), window="null", no_input=True)
            machine.set_emulation_speed(0)
            machines.append(machine)
        with LinkCable(*machines) as cable:
            if args.load:
                with args.load.open("rb") as source:
                    cable.load_state(source)
                cable.resume()
            for _ in range(args.frames):
                if not cable.tick():
                    break
            with args.save.open("xb") as target:
                cable.save_state(target)
    finally:
        for machine in machines:
            machine.stop(save=False)


if __name__ == "__main__":
    main()
