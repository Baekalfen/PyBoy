#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
import pytest
from pyboy import PyBoy
from pyboy.plugins.game_wrapper_pandoras_blocks import GameWrapperPandorasBlocks

# https://github.com/Villadelfia/dmgtris
# https://github.com/Villadelfia/dmgtris/releases/download/1.8/PandorasBlocks.gbc


@pytest.fixture(params=[False, True])
def pandorasblocks(pandorasblocks_file, request):
    pyboy = PyBoy(pandorasblocks_file, window="null", cgb=request.param)
    try:
        yield pyboy
    finally:
        pyboy.stop(save=False)


@pytest.fixture
def started_pandorasblocks(pandorasblocks):
    pandorasblocks.game_wrapper.start_game(timer_div=0)
    return pandorasblocks


@pytest.mark.parametrize("cgb", [False, True])
def test_pandorasblocks_startup(cgb, pandorasblocks_file):
    pyboy = PyBoy(pandorasblocks_file, window="null", cgb=cgb)
    try:
        wrapper = pyboy.game_wrapper
        assert isinstance(wrapper, GameWrapperPandorasBlocks)
        wrapper.start_game(timer_div=0)
        assert pyboy.memory[0xFFFD] == 3
    finally:
        pyboy.stop(save=False)


def test_pandorasblocks_state(started_pandorasblocks):
    wrapper = started_pandorasblocks.game_wrapper
    assert wrapper.next_block() in {"I", "Z", "S", "J", "L", "O", "T"}
    assert wrapper.game_area().shape == (18, 10)
    assert wrapper.score == 0
    assert wrapper.level == 0
    assert wrapper.lines == 0


def test_pandorasblocks_blocks(started_pandorasblocks):
    wrapper = started_pandorasblocks.game_wrapper
    for block in ("I", "Z", "S", "J", "L", "O", "T"):
        wrapper.set_block(block)
        assert wrapper.next_block() == block
    with pytest.raises(KeyError):
        wrapper.set_block("invalid")


def test_pandorasblocks_reset(started_pandorasblocks):
    wrapper = started_pandorasblocks.game_wrapper
    first_block = wrapper.next_block()
    wrapper.set_block("T")
    wrapper.reset_game(timer_div=0)
    assert wrapper.next_block() == first_block


def test_pandorasblocks_cache_and_repr(started_pandorasblocks):
    wrapper = started_pandorasblocks.game_wrapper
    first_area = wrapper.game_area()
    started_pandorasblocks.tick(1, False, False)
    assert wrapper.game_area() is not first_area
    assert "Pandora's Blocks:" in repr(wrapper)


def test_pandorasblocks_game_over_modes(started_pandorasblocks):
    wrapper = started_pandorasblocks.game_wrapper
    started_pandorasblocks.memory[0xFFDB] = 24
    assert wrapper.game_over()
    started_pandorasblocks.memory[0xFFDB] = 21
    assert wrapper.game_over()
    started_pandorasblocks.memory[0xFFDB] = 0
    assert not wrapper.game_over()


def test_pandorasblocks_mappings():
    assert np.count_nonzero(GameWrapperPandorasBlocks.mapping_compressed) > 0
    assert set(GameWrapperPandorasBlocks.mapping_minimal) == {0, 1, 2}
