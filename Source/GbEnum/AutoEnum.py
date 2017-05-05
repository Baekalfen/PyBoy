# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from enum import Enum

class AutoEnum(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
