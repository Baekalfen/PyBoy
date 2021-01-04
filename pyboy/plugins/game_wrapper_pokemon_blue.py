import inspect
import logging
from argparse import ZERO_OR_MORE
from enum import Enum
from functools import cached_property
from typing import Any, List

from .base_plugin import PyBoyGameWrapper

logger = logging.getLogger(__name__)

try:
    from cython import compiled

    cythonmode = compiled
except ImportError:
    cythonmode = False

# TODO: Find a good way of adding typing for a classmethod that returns cls. See get()
# Addresses come from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map#Miscellaneous

# I keep this separate because it may be useful if we ever have to debug text boxes
class Alphabet(Enum):
    INVALID = 0
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
    HIRAGANA_I = 0x6E  # い
    HIRAGANA_U = 0x6F  # う
    BOLD_OPEN_SINGLE_QUOTE = 0x70
    BOLD_CLOSING_SINGLE_QUOTE = 0x71
    BOLD_OPEN_DOUBLE_QUOTE = 0x72
    BOLD_CLOSING_DOUBLE_QUOTE = 0x73
    BOLD_PERIOD = 0x74
    ELLIPSIS = 0x75
    HIRAGANA_A = 0x76  # あ
    HIRAGANA_E = 0x77  # え
    HIRAGANA_O = 0x78  # お
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
    e_WITH_FORWARD_ACCENT = 0xBA  # é
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
    KATAKANA_A = 0xE9  # ァ
    KATAKANA_U = 0xEA  # ゥ
    KATAKANA_E = 0xEB  # ェ
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

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.INVALID


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

    ADDRESS = 0xD355

    def __init__(
        self,
        text_speed: TextSpeed,
        battle_animation: BattleAnimation,
        battle_style: BattleStyle,
    ):
        self.text_speed = text_speed
        self.battle_animation = battle_animation
        self.battle_style = battle_style

    @classmethod
    def get(cls, game_wrapper: PyBoyGameWrapper):
        options = game_wrapper.pyboy.get_memory_value(cls.ADDRESS)
        return InGameOptions(
            TextSpeed(options & 0x0F),
            BattleAnimation((options & 0x80) >> 7),
            BattleStyle((options & 0x40) >> 6),
        )

    def __repr__(self) -> str:
        return (
            f"InGameOptions(text_speed={self.text_speed}, "
            f"battle_animation={self.battle_animation}, "
            f"battle_style={self.battle_style})"
        )


# Because Cython does not support dataclass
class EventFlags:
    class EventAddresses(Enum):
        STARTERS_BACK = 0xD5AB
        HAVE_TOWN_MAP = 0xD5F3
        HAVE_OAKS_PARCEL = 0xD60D
        HAVE_LAPRAS = 0xD72E
        DEBUG_NEW_GAME = 0xD732
        FOUGHT_GIOVANNI = 0xD751
        FOUGHT_BROCK = 0xD755
        FOUGHT_MISTY = 0xD75E
        FOUGHT_LT_SURGE = 0xD773
        FOUGHT_ERIKA = 0xD77C
        FOUGHT_ARTICUNO = 0xD782
        FOUGHT_KOGA = 0xD792
        FOUGHT_BLAINE = 0xD79A
        FOUGHT_SABRINA = 0xD7B3
        FOUGHT_ZAPDOS = 0xD7D4
        FOUGHT_VERMILLION_SNORLAX = 0xD7D8
        FOUGHT_CELADON_SNORLAX = 0xD7E0
        FOUGHT_MOLTRES = 0xD7EE
        SS_ANNE_HERE = 0xD803

    def __init__(
        self,
        starters_back,
        have_town_map,
        have_oaks_parcel,
        have_lapras,
        debug_new_game,
        fought_giovanni,
        fought_brock,
        fought_misty,
        fought_lt_surge,
        fought_erika,
        fought_articuno,
        fought_koga,
        fought_blaine,
        fought_sabrina,
        fought_zapdos,
        fought_vermillion_snorlax,
        fought_celadon_snorlax,
        fought_moltres,
        ss_anne_here,
    ):
        # TODO: Make all of these properties. I wish I had dataclasses...
        self.starters_back = starters_back
        self.have_town_map = have_town_map
        self.have_oaks_parcel = have_oaks_parcel
        self.have_lapras = have_lapras
        self.debug_new_game = debug_new_game
        self.fought_giovanni = fought_giovanni
        self.fought_brock = fought_brock
        self.fought_misty = fought_misty
        self.fought_lt_surge = fought_lt_surge
        self.fought_erika = fought_erika
        self.fought_articuno = fought_articuno
        self.fought_koga = fought_koga
        self.fought_blaine = fought_blaine
        self.fought_sabrina = fought_sabrina
        self.fought_zapdos = fought_zapdos
        self.fought_vermillion_snorlax = fought_vermillion_snorlax
        self.fought_celdaon_snorlax = fought_celadon_snorlax
        self.fought_moltres = fought_moltres
        self.ss_anne_here = ss_anne_here

    # 0100 0001 START
    # 0000 1001 CHOOSE CHARM
    # 0001 1001 RIVAL CHOOSE SQUIRT
    # 0001 0001 CHOOSE SQUIRT
    # 0011 0001 RIVAL CHOOSE BULBA
    # 0010 0001 CHOOSE BULBA
    # 0010 1001 RIVAL CHOOSE CHARM
    @classmethod
    def get(cls, game_wrapper: PyBoyGameWrapper):
        return cls(
            **{
                address.name.lower(): game_wrapper.pyboy.get_memory_value(address.value)
                for address in EventFlags.EventAddresses
            }
        )

    def __repr__(self) -> str:
        return f'EventFlags({", ".join(f"{k}={v}" for k, v in self.__dict__.items())})'


class Name:
    START_ADDRESS = 0xD158
    END_ADDRESS = 0xD162

    def __init__(self, name: List[Alphabet]):
        self.name = name

    @classmethod
    def get(cls, game_wrapper: PyBoyGameWrapper):
        return cls(
            [
                Alphabet(game_wrapper.pyboy.get_memory_value(addr)).name
                for addr in range(cls.START_ADDRESS, cls.END_ADDRESS + 1)
            ]
        )

    def __repr__(self) -> str:
        return f"Name({self.name})"


class Badges:
    ADDRESS = 0xD356

    def __init__(self, badges: int):
        """
        Args:
            badges (int): A bitset that refers to badges 0-8
        """
        self.badges = badges
        as_bits = f"{badges:08b}"

        @cached_property
        def boulder(self) -> bool:
            return bool(as_bits[0])

        @cached_property
        def cascade(self) -> bool:
            return bool(as_bits[1])

        @cached_property
        def thunder(self) -> bool:
            return bool(as_bits[2])

        @cached_property
        def rainbow(self) -> bool:
            return bool(as_bits[3])

        @cached_property
        def soul(self) -> bool:
            return bool(as_bits[4])

        @cached_property
        def marsh(self) -> bool:
            return bool(as_bits[5])

        @cached_property
        def volcano(self) -> bool:
            return bool(as_bits[6])

        @cached_property
        def earth(self) -> bool:
            return bool(as_bits[7])

    @classmethod
    def get(cls, game_wrapper: PyBoyGameWrapper):
        return cls(game_wrapper.pyboy.get_memory_value(cls.ADDRESS))

    def __repr__(self) -> str:
        return f"Badges({hex(self.badges)})"


class GameTime:
    HOURS_ADDRESS_MSB = 0xDA40
    HOURS_ADDRESS_LSB = 0xDA41

    MINUTES_ADDRESS_MSB = 0xDA42
    MINUTES_ADDRESS_LSB = 0xDA43

    SECONDS_ADDRESS = 0xDA44

    SECONDS = 1
    MINUTES = 60
    HOURS = MINUTES * 60

    def __init__(self, hours: int, minutes: int, seconds: int):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    @cached_property
    def total_seconds(self) -> int:
        return (
            self.hours * self.HOURS
            + self.minutes * self.MINUTES
            + self.seconds * self.SECONDS
        )

    @classmethod
    def get(cls, game_wrapper: PyBoyGameWrapper):
        hours = (
            game_wrapper.pyboy.get_memory_value(cls.HOURS_ADDRESS_MSB) << 8
        ) + game_wrapper.pyboy.get_memory_value(cls.HOURS_ADDRESS_LSB)
        minutes = (
            game_wrapper.pyboy.get_memory_value(cls.MINUTES_ADDRESS_MSB) << 8
        ) + game_wrapper.pyboy.get_memory_value(cls.MINUTES_ADDRESS_LSB)
        seconds = game_wrapper.pyboy.get_memory_value(cls.SECONDS_ADDRESS)

        return cls(hours, minutes, seconds)

    def __repr__(self) -> str:
        return f"GameTime(hours={self.hours}, minutes={self.minutes}, seconds={self.seconds})"


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
            options = InGameOptions.get(self)
            events = EventFlags.get(self)
            badges = Badges.get(self)

            # The fitness score is a combination of "bitset"
            # We have 3 ranges of values that we will eventually concatenate into one big value.
            # This is cause pathing in the game can be variable as
            # Misty, Blaine, Erika, Sabrina, Koga, Lt. Surge can be fought in a variety of orders.
            # Because Brock and Giovanni have requirements has to be fought separately they'll be in their own ranges
            # Ranges:
            # Gyms (A counter between 1 and 6 as each one is equally valuable imo)
            # TODO: Find a way to score the elite 4/hall of fame. The data is at 0xA598 - 0xB857 in SRAM Bank 0, but I'm not sure what's stored there.
            # TODO: Add scoring for end of game based on time spent + level (lower is better).
            #       Proposal is to do 100-level of pokemon for each pokemon in the party
            #       One way to do it would be to countdown starting from ~24 hours based on
            #       Jrose11's Abra run which took 17 hours 18 minutes
            bitset = (
                f"{badges.giovanni:01b}"
                f"{(badges.badges & 0x7E) >> 1:06b}"  # Middle six badges any order
                f"{badges.brock:01b}"
                f"{events.have_oaks_parcel > 0:01b}"
                f"{events.debug_new_game > 0:01b}"
                f"{options.battle_animation == BattleAnimation.OFF:01b}"
                f"{options.text_speed == TextSpeed.FAST:01b}"
            )
            self.fitness = int(bitset, 2)

    def game_over(self) -> bool:
        # Game over when we hit 24 hours or oak's parcel. Incrementally relax the second condition
        return (
            GameTime.get(self).total_seconds > 30 * GameTime.MINUTES
            or EventFlags.get(self).have_oaks_parcel
        )

    def __repr__(self) -> str:
        return (
            f"Pokemon Blue:\n"
            f"\tFitness: {self.fitness}\n"
            f"\tOptions: {InGameOptions.get(self)}\n"
            f"\tYour Name: {Name.get(self)}\n"
            f"\tEvent Flags: {EventFlags.get(self)}\n"
            f"\tBadges: {Badges.get(self)}\n"
            f"\tGame Time: {GameTime.get(self)}"
        )
