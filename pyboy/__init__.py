#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "core": False,
    "logger": False,
    "pyboy": False,
    "utils": False,
}
__all__ = ["PyBoy", "WindowEvent"]

from .pyboy import PyBoy
from .utils import WindowEvent


def get_include():
    import os
    return os.path.dirname(os.path.abspath(__file__))
