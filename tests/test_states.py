#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import io
import platform

from pyboy import PyBoy, WindowEvent

NEXT_TETROMINO_ADDR = 0xC213


def test_load_save_consistency(tetris_rom):
    pyboy = PyBoy(tetris_rom, window_type="null")
    assert pyboy.cartridge_title() == "TETRIS"
    pyboy.set_emulation_speed(0)
    pyboy.memory[NEXT_TETROMINO_ADDR]

    ##############################################################
    # Set up some kind of state, where not all registers are reset
    ##############################################################

    tetris = pyboy.game_wrapper

    timer_div = 0x00
    saved_state = io.BytesIO()

    # Boot screen
    while True:
        pyboy.tick(1, True)
        tilemap_background = pyboy.tilemap_background
        if tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]: # '1PLAYER' on the first screen
            break

    # Start game. Just press Start when the game allows us.
    for i in range(2):
        pyboy.button("start")
        pyboy.tick(7, True)

    ##############################################################
    # Verify
    ##############################################################

    # Save
    saved_state.seek(0)
    pyboy.save_state(saved_state)
    tetris._set_timer_div(timer_div)

    # Load
    saved_state.seek(0)
    pyboy.load_state(saved_state)

    # Save again
    saved_state2 = io.BytesIO()
    pyboy.save_state(saved_state2)

    # Compare saves
    saved_state2.seek(0)
    saved_state.seek(0)
    first = saved_state.read()
    second = saved_state2.read()
    assert first == second
