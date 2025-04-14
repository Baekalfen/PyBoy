#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy
from pyboy.plugins.game_wrapper_pokemon_pinball import Pokemon, SpecialMode, Stage


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

    assert pokemon_pinball.score == 100300
    assert pokemon_pinball.special_mode == SpecialMode.CATCH.value
    assert pokemon_pinball.current_stage == Stage.BLUE_BOTTOM.value
    assert pokemon_pinball.special_mode_active
    assert pokemon_pinball.balls_left == 2


def test_pokemon_catch_mode(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game(stage=Stage.RED_BOTTOM, timer_div=0x00)
    pyboy.button_press("a")
    pyboy.button_press("left")
    pyboy.tick(50, False, False)
    pokemon_pinball.start_catch_mode()
    pyboy.tick(270, False, False)
    pyboy.button_release("left")
    pyboy.button_release("a")
    pyboy.button("select")
    pyboy.tick(20, False, False)
    pyboy.button_press("left")
    pyboy.button_press("a")
    pyboy.tick(500, False, False)
    pyboy.button_release("left")
    pyboy.tick(21, False, False)
    pyboy.button_press("left")
    pyboy.tick(100, False, False)
    pyboy.button_release("a")
    pyboy.tick(31, False, False)
    pyboy.button_press("a")
    pyboy.tick(200, False, False)
    pyboy.button_release("left")
    pyboy.tick(31, False, False)
    pyboy.button_press("left")
    pyboy.tick(200, False, False)
    pyboy.button_release("left")
    pyboy.tick(31, False, False)
    pyboy.button_press("left")
    pyboy.tick(400, False, False)  # NOTE: This sequence broke because of changed instruction timings

    assert pokemon_pinball.score == 200
    assert not pokemon_pinball.has_pokemon(Pokemon.BULBASAUR)
    assert not pokemon_pinball.has_pokemon(Pokemon.CHARMANDER)
    assert pokemon_pinball.get_unique_pokemon_caught() == 0


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
