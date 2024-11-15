#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_gameshark(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.tick(60)

    code = "010138CD"
    value = 0x01
    address = 0xCD38

    # Establish truth
    pyboy.tick()
    assert pyboy.memory[address] != value

    # Apply cheat, and validate new value
    pyboy.gameshark.add(code)
    pyboy.tick()
    assert pyboy.memory[address] == value

    # Remove cheat, and reestablish old value
    pyboy.gameshark.remove(code)
    assert pyboy.memory[address] != value

    # Add cheat, remove, but do not reestablish old value
    pyboy.gameshark.add(code)
    pyboy.tick()
    assert pyboy.memory[address] == value
    pyboy.gameshark.remove(code, False)
    assert pyboy.memory[address] == value

    pyboy.stop(save=False)


def test_gameshark_clear(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    code1 = "010138CD"
    code2 = "010138CE"
    value = 0x01
    address1 = 0xCD38
    address2 = 0xCE38

    assert pyboy.memory[address1] != value
    assert pyboy.memory[address2] != value
    pyboy.gameshark.add(code1)
    pyboy.gameshark.add(code2)
    pyboy.tick()
    assert pyboy.memory[address1] == value
    assert pyboy.memory[address2] == value

    pyboy.gameshark.clear_all()

    pyboy.tick()
    assert pyboy.memory[address1] != value
    assert pyboy.memory[address2] != value

    pyboy.stop(save=False)
