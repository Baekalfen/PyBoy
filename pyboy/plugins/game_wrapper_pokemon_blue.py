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

        self.game_has_started = True

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

        self._set_timer_div(timer_div)

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
