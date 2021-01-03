from argparse import ZERO_OR_MORE
import logging
from enum import Enum
from typing import Any

from .base_plugin import PyBoyGameWrapper

logger = logging.getLogger(__name__)

try:
    from cython import compiled

    cythonmode = compiled
except ImportError:
    cythonmode = False


class Alphabet(Enum):
    END_OF_NAME = 0x50
    BOLD_A = 0x60
    BOLD_B = 0x61
    BOLD_C = 0x62
    BOLD_D = 0x63
    BOLD_E = 0x64
    BOLD_F = 0x65
    BOLD_G = 0x66
    BOLD_H = 0x67
    BOLD_I = 0x68
    BOLD_V = 0x69
    BOLD_S = 0x6A
    BOLD_L = 0x6B
    BOLD_M = 0x6C
    BOLD_COLON = 0x6D
    ぃ = 0x6E
    ぅ = 0x6F
    BOLD_OPEN_SINGLE_QUOTE = 0x70
    BOLD_CLOSING_SINGLE_QUOTE = 0x71
    BOLD_OPEN_DOUBLE_QUOTE = 0x72
    BOLD_CLOSING_DOUBLE_QUOTE = 0x73
    BOLD_PERIOD = 0x74
    ELLIPSIS = 0x75
    ぁ = 0x76
    ぇ = 0x77
    ぉ = 0x78
    POKEBALL_BORDER_TOP_LEFT = 0x79
    POKEBALL_BORDER_HORIZONTAL = 0x7A
    POKEBALL_BORDER_TOP_RIGHT = 0x7B
    POKEBALL_BORDER_VERTICAL = 0x7C
    POKEBALL_BORDER_BOTTOM_LEFT = 0x7D
    POKEBALL_BORDER_BOTTOM_RIGHT = 0x7E
    SPACE = 0x7F
    A = 0x80
    B = 0x81
    C = 0x82
    D = 0x83
    E = 0x84
    F = 0x85
    G = 0x86
    H = 0x87
    I = 0x88
    J = 0x89
    K = 0x8A
    L = 0x8B
    M = 0x8C
    N = 0x8D
    O = 0x8E
    P = 0x8F
    Q = 0x90
    R = 0x91
    S = 0x92
    T = 0x93
    U = 0x94
    V = 0x95
    W = 0x96
    X = 0x97
    Y = 0x98
    Z = 0x99
    LEFT_PARENTHESIS = 0x9A
    RIGHT_PARENTHESIS = 0x9B
    COLON = 0x9C
    SEMICOLON = 0x9D
    LEFT_BRACKET = 0x9E
    RIGHT_BRACKET = 0x9F
    a = 0xA0
    b = 0xA1
    c = 0xA2
    d = 0xA3
    e = 0xA4
    f = 0xA5
    g = 0xA6
    h = 0xA7
    i = 0xA8
    j = 0xA9
    k = 0xAA
    l = 0xAB
    m = 0xAC
    n = 0xAD
    o = 0xAE
    p = 0xAF
    q = 0xB0
    r = 0xB1
    s = 0xB2
    t = 0xB3
    u = 0xB4
    v = 0xB5
    w = 0xB6
    x = 0xB7
    y = 0xB8
    z = 0xB9
    é = 0xBA
    APOSTROPHE_d = 0xBB
    APOSTROPHE_l = 0xBC
    APOSTROPHE_s = 0xBD
    APOSTROPHE_t = 0xBE
    APOSTROPHE_v = 0xBF
    APOSTRPOHE = 0xE0
    PK = 0xE1
    MN = 0xE2
    DASH = 0xE3
    APOSTROPHE_r = 0xE4
    APOSTROPHE_m = 0xE5
    QUESTION_MARK = 0xE6
    EXCLAMATION_MARK = 0xE7
    PERIOD = 0xE8
    ァ = 0xE9
    ゥ = 0xEA
    ェ = 0xEB
    OUTLINE_RIGHT_ARROW = 0xEC
    RIGHT_ARROW = 0xED
    DOWN_ARROW = 0xEE
    MALE_SYMBOL = 0xEF
    POKEDOLLAR = 0xF0
    MULTIPLICATION_SIGN = 0xF1
    PERIOD_2 = 0xF2
    FORWARD_SLASH = 0xF3
    COMMA = 0xF4
    FEMALE_SYMBOL = 0xF5
    ZERO = 0xF6
    ONE = 0xF7
    TWO = 0xF8
    THREE = 0xF9
    FOUR = 0xFA
    FIVE = 0xFB
    SIX = 0xFC
    SEVEN = 0xFD
    EIGHT = 0xFE
    NINE = 0xFF


class TextSpeed(Enum):
    INVALID = -1
    FAST = 1
    MEDIUM = 3
    SLOW = 5

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.INVALID


class BattleAnimation(Enum):
    INVALID = -1
    OFF = 1
    ON = 0

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.INVALID


class BattleStyle(Enum):
    INVALID = -1
    SET = 1
    SHIFT = 0

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.INVALID


# Because Cython does not support dataclass
class InGameOptions:
    def __init__(
        self,
        text_speed: TextSpeed,
        battle_animation: BattleAnimation,
        battle_style: BattleStyle,
    ):
        self.text_speed = text_speed
        self.battle_animation = battle_animation
        self.battle_style = battle_style

    def __repr__(self) -> str:
        return (
            f"InGameOptions(text_speed={self.text_speed}, "
            f"battle_animation={self.battle_animation}, "
            f"battle_style={self.battle_style})"
        )


EXPECTED_OPTIONS = InGameOptions(
    TextSpeed.FAST,
    BattleAnimation.OFF,
    BattleStyle.SHIFT,
)


class GameWrapperPokemonBlue(PyBoyGameWrapper):
    cartridge_title = "POKEMON BLUE"

    def __init__(self, *args, **kwargs):
        self.shape = (20, 18)
        self.fitness = 0

        super().__init__(
            *args,
            game_area_section=(0, 0) + self.shape,
            game_area_wrap_around=True,
            **kwargs,
        )

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)
        self._set_timer_div(timer_div)

        self.game_has_started = True

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

        self._set_timer_div(timer_div)

    def post_tick(self):
        if self.game_has_started:
            options = self.parse_options()
            print(f"OPTIONS: {options}")
            your_name = [
                Alphabet(self.pyboy.get_memory_value(addr))
                for addr in range(0xD158, 0xD163)
            ]
            print(f"YOUR NAME: {your_name}")
            print(f"DEBUG NEW GAME: {self.pyboy.get_memory_value(0xD732)}")
            self.fitness = (
                int(options.text_speed == EXPECTED_OPTIONS.text_speed)
                + int(options.battle_animation == EXPECTED_OPTIONS.battle_animation)
                + int(options.battle_style == EXPECTED_OPTIONS.battle_style)
            )

    def game_over(self) -> bool:
        return self.parse_options() == EXPECTED_OPTIONS

    def __repr__(self) -> str:
        return f"Pokemon Blue:\n\tFitness: {self.fitness}"

    def parse_options(self) -> InGameOptions:
        # https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#Miscellaneous
        options = self.pyboy.get_memory_value(0xD355)
        return InGameOptions(
            TextSpeed(options & 0x0F),
            BattleAnimation((options & 0x80) >> 7),
            BattleStyle((options & 0x40) >> 6),
        )
