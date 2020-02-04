#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.plugins.base_plugin import PyBoyPlugin


class Debug(PyBoyPlugin):
    argv = [('-d', '--debug', {"action":'store_true', "help": 'Enable emulator debugging mode'})]
