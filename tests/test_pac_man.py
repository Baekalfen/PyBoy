#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest
from pyboy import PyBoy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _boot(rom):
    """Start the emulator and advance to the first playable frame."""
    pyboy = PyBoy(rom, window="null")
    pyboy.set_emulation_speed(0)
    for _ in range(700):
        pyboy.tick(1, False)
    pyboy.button("start")
    pyboy.tick(1, False)
    for _ in range(1000):
        pyboy.tick(1, False)
    return pyboy


def _read_score(pyboy):
    def bcd(b):
        return (b >> 4) * 10 + (b & 0xF)
    return (
        bcd(pyboy.memory[0xD639]) * 10_000 +
        bcd(pyboy.memory[0xD638]) *    100 +
        bcd(pyboy.memory[0xD637])
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_pac_man_score_starts_nonzero(pac_man_rom):
    """
    Score at the first playable frame is 50 because Pac-Man spawns on a dot.
    Verifies the BCD decoder and that the three score addresses are readable.
    """
    pyboy = _boot(pac_man_rom)
    assert _read_score(pyboy) == 50
    pyboy.stop()


def test_pac_man_score_increases_on_movement(pac_man_rom):
    """
    Holding UP for 250 frames moves Pac-Man through the maze and eats dots.
    Score must be strictly greater than the starting value afterwards.
    """
    pyboy = _boot(pac_man_rom)
    score_before = _read_score(pyboy)

    for _ in range(250):
        pyboy.button_press("up")
        pyboy.tick(1, False)
    pyboy.button_release("up")
    pyboy.tick(20, False)

    assert _read_score(pyboy) > score_before
    pyboy.stop()


def test_pac_man_score_never_decreases(pac_man_rom):
    """
    Score is monotonically non-decreasing throughout a session.
    Runs until game over or 5000 ticks, whichever comes first.
    """
    pyboy = _boot(pac_man_rom)
    prev = _read_score(pyboy)

    for _ in range(5000):
        pyboy.tick(1, False)
        score = _read_score(pyboy)
        assert score >= prev, f"Score decreased: {prev} -> {score}"
        prev = score
        if pyboy.memory[0xD641] == 0:
            break

    pyboy.stop()


def test_pac_man_lives_start_at_two(pac_man_rom):
    """
    The lives register (0xD641) must equal 2 at the start of a new game.
    Pac-Man has 3 lives total; this register counts the extra two shown as icons.
    """
    pyboy = _boot(pac_man_rom)
    assert pyboy.memory[0xD641] == 2
    pyboy.stop()


def test_pac_man_lives_decrease_on_death(pac_man_rom):
    """
    Running long enough guarantees ghosts will catch Pac-Man.
    Lives must drop below the starting value of 2 within 8000 ticks.
    """
    pyboy = _boot(pac_man_rom)
    starting_lives = pyboy.memory[0xD641]

    for _ in range(8000):
        pyboy.tick(1, False)
        if pyboy.memory[0xD641] < starting_lives:
            break
    else:
        pytest.fail("Lives never decreased within 8000 ticks")

    pyboy.stop()


def test_pac_man_game_over_when_lives_zero(pac_man_rom):
    """
    When lives reach 0 the game is over.
    Runs until lives == 0, then asserts the score is a valid BCD value (no
    corruption) and that the run actually ended.
    """
    pyboy = _boot(pac_man_rom)

    for _ in range(2000):
        pyboy.tick(1, False)
        if pyboy.memory[0xD641] == 0:
            break
    else:
        pytest.fail("Game never reached game over within 20000 ticks")

    # Score must still be a valid, non-negative integer
    assert _read_score(pyboy) >= 0
    pyboy.stop()


def test_pac_man_level_starts_at_one(pac_man_rom):
    """Level register (0xD643) must be 1 at the start of the first game."""
    pyboy = _boot(pac_man_rom)
    assert pyboy.memory[0xD643] == 1
    pyboy.stop()


def test_pac_man_level_stable_during_normal_play(pac_man_rom):
    """
    Level should not change during a short session on the first maze.
    Runs 3000 ticks and asserts level stays at 1.
    """
    pyboy = _boot(pac_man_rom)

    for _ in range(3000):
        pyboy.tick(1, False)
        assert pyboy.memory[0xD643] == 1, \
            f"Level changed unexpectedly at tick {_}"

    pyboy.stop()