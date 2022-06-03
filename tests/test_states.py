#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import io
import platform

from pyboy import PyBoy, WindowEvent
from tests.utils import tetris_rom

NEXT_TETROMINO_ADDR = 0xC213


def test_all_modes():
    pyboy = PyBoy(tetris_rom, window_type="headless", game_wrapper=True)
    assert pyboy.cartridge_title() == "TETRIS"
    pyboy.set_emulation_speed(0)
    pyboy.get_memory_value(NEXT_TETROMINO_ADDR)

    tetris = pyboy.game_wrapper()

    timer_div = 0x00
    saved_state = io.BytesIO()

    # Boot screen
    while True:
        pyboy.tick()
        tilemap_background = pyboy.botsupport_manager().tilemap_background()
        if tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]: # '1PLAYER' on the first screen
            break

    # Start game. Just press Start when the game allows us.
    for i in range(2):
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        for _ in range(6):
            pyboy.tick()

    saved_state.seek(0)
    pyboy.save_state(saved_state)
    tetris._set_timer_div(timer_div)

    game_has_started = True

    saved_state.seek(0)
    pyboy.load_state(saved_state)

    saved_state2 = io.BytesIO()
    pyboy.save_state(saved_state2)
    saved_state2.seek(0)
    saved_state.seek(0)
    first = saved_state.read()
    second = saved_state2.read()
    assert first == second
