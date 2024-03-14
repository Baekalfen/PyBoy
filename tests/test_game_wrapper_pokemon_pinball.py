#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
import sys

import numpy as np
import pytest

from pyboy import PyBoy
from pyboy.plugins.game_wrapper_pokemon_pinball import Pokemon, SpecialMode, Stage
from pyboy.utils import WindowEvent


def test_pokemon_pinball_basics(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game(timer_div=0x00)

    assert pokemon_pinball.score == 0
    assert pokemon_pinball.balls_left == 2
    assert pokemon_pinball.current_stage == Stage.RED_BOTTOM.value
    assert pokemon_pinball.special_mode_active == False
    pyboy.stop(False)


def test_pokemon_pinball_advanced(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game(stage=Stage.BLUE_BOTTOM, timer_div=0x00)
    pyboy.button_press("a")
    pyboy.button_press("left")
    pyboy.tick(500)
    pyboy.button_release("left")
    pyboy.button_release("a")
    pyboy.tick(26)
    pyboy.button_press("left")
    pyboy.button_press("a")
    pyboy.tick(700)
    pyboy.button_release("left")
    pyboy.button_release("a")

    assert pokemon_pinball.score == 100200
    assert pokemon_pinball.special_mode == SpecialMode.CATCH.value
    assert pokemon_pinball.current_stage == Stage.BLUE_BOTTOM.value
    assert pokemon_pinball.special_mode_active == True
    assert pokemon_pinball.balls_left == 2

    pyboy.stop(False)


def test_pokemon_catch_mode(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game(stage=Stage.RED_BOTTOM, timer_div=0x00)
    pyboy.button_press("a")
    pyboy.button_press("left")
    pyboy.tick(50)
    pokemon_pinball.start_catch_mode()
    pyboy.tick(270)
    pyboy.button_release("left")
    pyboy.button_release("a")
    pyboy.button("select")
    pyboy.tick(20)
    pyboy.button_press("left")
    pyboy.button_press("a")
    pyboy.tick(500)
    pyboy.button_release("left")
    pyboy.tick(21)
    pyboy.button_press("left")
    pyboy.tick(100)
    pyboy.button_release("a")
    pyboy.tick(31)
    pyboy.button_press("a")
    pyboy.tick(200)
    pyboy.button_release("left")
    pyboy.tick(31)
    pyboy.button_press("left")
    pyboy.tick(200)
    pyboy.button_release("left")
    pyboy.tick(31)
    pyboy.button_press("left")
    pyboy.tick(400)

    assert pokemon_pinball.score == 15635100
    assert pokemon_pinball.has_pokemon(Pokemon.BULBASAUR)
    assert pokemon_pinball.has_pokemon(Pokemon.CHARMANDER) == False
    assert pokemon_pinball.get_unique_pokemon_caught() == 1

    pyboy.stop(False)


def test_pokemon_pinball_game_over(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game(timer_div=0x00)

    for _ in range(62):
        pyboy.button("a")
        pyboy.tick(100, render=False)

    assert pokemon_pinball.game_over

    pyboy.stop(False)
