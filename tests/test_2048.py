#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_2048_basics(gb2048_file):
    pyboy = PyBoy(gb2048_file, window="null")
    pyboy.set_emulation_speed(0)

    wrapper = pyboy.game_wrapper

    for _ in range(500):
        pyboy.tick(1, False)

    pyboy.button("start")
    for _ in range(60):
        pyboy.tick(1, False)

    assert wrapper.score == 0
    assert wrapper.winner == False
    assert wrapper.game_over() == False

    non_zero = sum(1 for row in wrapper.board for tile in row if tile != 0)
    assert non_zero == 2

    pyboy.stop()


def test_2048_score_increases(gb2048_file):
    pyboy = PyBoy(gb2048_file, window="null")
    pyboy.set_emulation_speed(0)

    wrapper = pyboy.game_wrapper

    for _ in range(500):
        pyboy.tick(1, False)

    pyboy.button("start")
    for _ in range(60):
        pyboy.tick(1, False)

    for _ in range(10):
        pyboy.button("right")
        pyboy.tick(30, False)
        pyboy.button("up")
        pyboy.tick(30, False)

    assert wrapper.score >= 0

    pyboy.stop()


def test_2048_game_over(gb2048_file):
    pyboy = PyBoy(gb2048_file, window="null")
    pyboy.set_emulation_speed(0)

    wrapper = pyboy.game_wrapper

    for _ in range(500):
        pyboy.tick(1, False)

    pyboy.button("start")
    for _ in range(200):
        pyboy.tick(1, False)

    for i in range(5000):
        pyboy.button_press("right")
        pyboy.tick(10, False)
        pyboy.button_release("right")
        pyboy.tick(5, False)

        pyboy.button_press("down")
        pyboy.tick(10, False)
        pyboy.button_release("down")
        pyboy.tick(5, False)

        if wrapper.game_over():
            break

    assert wrapper.game_over() == True

    pyboy.stop()
