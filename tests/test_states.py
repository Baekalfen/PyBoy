#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import copy
import io

import pytest

from pyboy import PyBoy
from pyboy.utils import IntIOWrapper, cython_compiled


def copy_attrs(obj, allowed_types=("int", "str", "float", "array", "dict", "list", "bool")):
    attrs = [k for k in dir(obj) if type(getattr(obj, k)).__name__ in allowed_types]
    return {k: copy.copy(getattr(obj, k)) for k in attrs}


def boot(pyboy):
    # Boot screen
    while True:
        pyboy.tick(1, False, False)
        tilemap_background = pyboy.tilemap_background
        if tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]:  # '1PLAYER' on the first screen
            break

    # Start game. Just press Start when the game allows us.
    for i in range(2):
        pyboy.button("start")
        pyboy.tick(7, False, False)


def progress(pyboy):
    for _ in range(3):
        # Do something
        pyboy.tick(10, False, False)
        pyboy.button("a")
    pyboy.tick(1, False, False)  # Flush input


ignored_attrs = [
    "_spritecache0_raw",
    "_spritecache0_state",
    "_tilecache0_raw",
    "_tilecache0_state",
    "sprites_to_render",
    "serialbuffer",
    "serialbuffer_count",
    "disable_renderer",  # Not set before calling .tick()
    "__dict__",
]


def compare_attributes(a, b):
    # Compare all attributes before and after save/load-state
    success = True
    for (module_name, attrs), (module_name2, attrs2) in zip(a.items(), b.items()):
        attrs.pop("bail", None)  # Doesn't show before .tick() is called.
        attrs2.pop("bail", None)
        assert module_name == module_name2
        assert set(attrs.keys()) ^ set(attrs2.keys()) == set(), "Expected same attributes in both sets"
        for (k, v), (k2, v2) in zip(attrs.items(), attrs2.items()):
            assert k == k2
            # assert v == v2, k

            if k in ignored_attrs:
                continue

            if v != v2:
                print(module_name, k)
                if isinstance(v, int):
                    print(hex(v), hex(v2))
                success = False
    return success


def compare_IntIOWrapper(metadata, _s1, _s2):
    success = True
    for m, s1, s2 in zip(metadata, _s1, _s2):
        # i = 0
        a = s1.buffer.getvalue()
        b = s2.buffer.getvalue()
        if a != b:
            print("failed", m)
            success = False
    return success


def get_modules(pyboy):
    modules = [
        pyboy.mb,
        pyboy.mb.cartridge,
        pyboy.mb.timer,
        pyboy.mb.interaction,
        pyboy.mb.bootrom,
        pyboy.mb.ram,
        pyboy.mb.cpu,
        pyboy.mb.lcd,
        pyboy.mb.lcd._LCDC,
        pyboy.mb.lcd._STAT,
        pyboy.mb.lcd.BGP,
        pyboy.mb.lcd.OBP0,
        pyboy.mb.lcd.OBP1,
        pyboy.mb.lcd.renderer,
        pyboy.mb.sound,
        pyboy.mb.sound.noisechannel,
        pyboy.mb.sound.sweepchannel,
        pyboy.mb.sound.tonechannel,
        pyboy.mb.sound.wavechannel,
    ]
    if pyboy.mb.hdma is not None:
        modules.append(pyboy.mb.hdma)
    return modules


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_null(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    base_line.seek(0)
    pyboy.load_state(base_line)

    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################

    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_attrs(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    progress(pyboy)  # Scrambles state
    ##############################################################
    base_line.seek(0)
    pyboy.load_state(base_line)
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################

    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_attrs_migrate_instance(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    progress(pyboy)
    base_line = io.BytesIO()
    pyboy.save_state(base_line)
    # pyboy.tick()
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    pyboy2 = PyBoy(tetris_rom, window="null")
    base_line.seek(0)
    pyboy2.load_state(base_line)
    # pyboy2.tick()
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy2)}
    ##############################################################
    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_deterministic(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    progress(pyboy)
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    base_line.seek(0)
    pyboy.load_state(base_line)

    progress(pyboy)
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################

    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_deterministic_migrated(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    progress(pyboy)
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    pyboy2 = PyBoy(tetris_rom, window="null")
    base_line.seek(0)
    pyboy2.load_state(base_line)

    progress(pyboy2)
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy2)}
    ##############################################################

    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_state_deterministic2(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    progress(pyboy)
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################
    base_line.seek(0)
    pyboy.load_state(base_line)

    progress(pyboy)
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in get_modules(pyboy)}
    ##############################################################

    assert compare_attributes(module_attrs, module_attrs2)  # class attributes


def test_state_deterministic_cython(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)
    state1 = io.BytesIO()
    state2 = io.BytesIO()

    ##############################################################
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    progress(pyboy)
    pyboy.save_state(state1)
    ##############################################################
    base_line.seek(0)
    pyboy.load_state(base_line)

    progress(pyboy)
    pyboy.save_state(state2)
    ##############################################################

    assert state1.getvalue() == state2.getvalue()


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal registers not available in Cython")
def test_submodule_states(tetris_rom):
    pyboy = PyBoy(tetris_rom, window="null")
    assert pyboy.cartridge_title == "TETRIS"
    boot(pyboy)

    modules = [
        pyboy.mb,
        pyboy.mb.cartridge,
        pyboy.mb.timer,
        pyboy.mb.interaction,
        # pyboy.mb.bootrom,  # Doesn't implement save/load state
        pyboy.mb.ram,
        pyboy.mb.cpu,
        pyboy.mb.lcd,
        # pyboy.mb.lcd._LCDC,  # Doesn't implement save/load state
        pyboy.mb.lcd._STAT,
        # pyboy.mb.lcd.BGP,  # Doesn't implement save/load state
        # pyboy.mb.lcd.OBP0,  # Doesn't implement save/load state
        # pyboy.mb.lcd.OBP1,  # Doesn't implement save/load state
        pyboy.mb.lcd.renderer,
        pyboy.mb.sound,
        pyboy.mb.sound.noisechannel,
        pyboy.mb.sound.sweepchannel,
        pyboy.mb.sound.tonechannel,
        pyboy.mb.sound.wavechannel,
    ]
    if pyboy.mb.hdma is not None:
        modules.append(pyboy.mb.hdma)

    ##############################################################
    ## Save base line
    base_line = io.BytesIO()
    pyboy.save_state(base_line)

    # Check determinism as unaccounted attributes or cycles may be offset
    progress(pyboy)

    # State of clean progress from beginning to now
    saved_state1 = io.BytesIO()
    pyboy.save_state(saved_state1)

    states1 = [IntIOWrapper(io.BytesIO()) for _ in modules]
    for m, x in zip(modules, states1):
        m.save_state(x)
        x.seek(0)
    module_attrs = {x.__class__.__name__: copy_attrs(x) for x in modules}

    ##############################################################
    ## Load base line to repeat process
    base_line.seek(0)
    pyboy.load_state(base_line)

    # Rerun to check determinism
    progress(pyboy)

    # State of rerun progress from previous state
    saved_state2 = io.BytesIO()
    pyboy.save_state(saved_state2)

    states2 = [IntIOWrapper(io.BytesIO()) for _ in modules]
    for m, x in zip(modules, states2):
        m.save_state(x)
        x.seek(0)
    module_attrs2 = {x.__class__.__name__: copy_attrs(x) for x in modules}

    ##############################################################
    ## Compare saves
    assert compare_attributes(module_attrs, module_attrs2)  # class attributes
    assert compare_IntIOWrapper(modules, states1, states2)  # class states
    assert saved_state1.getvalue() == saved_state2.getvalue()  # full state
