import os
import sys

from pyboy import PyBoy

# fn = "gb-link.gb"
fn = "pokeyellow_debug.gbc" if len(sys.argv) == 1 else "pokeyellow_debug - Copy.gbc"
# fn = "Tetris.gb"

pyboy = PyBoy(
    fn,
    log_level="DEBUG",
    scale=2,
    cgb=True,
    # symbols=fn.split(".")[0] + ".sym",
    serial_bind="127.0.0.1:6900" if len(sys.argv) == 1 else None,
    serial_address="127.0.0.1:6900"
)
if os.path.isfile(os.path.join("saves", fn + ".state")):
    with open(os.path.join("saves", fn + ".state"), "rb") as f:
        pyboy.load_state(f)
# if os.path.isfile(os.path.join("saves", fn + ".ram")):
#     with open(os.path.join("saves", fn + ".ram"), "rb") as f:
#         pyboy.load_ram(f)

while pyboy.tick():
    continue
