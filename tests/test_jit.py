#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_jit_tick(default_rom):
    pyboy_jit = PyBoy(default_rom, window="null", jit=True, debug=False, log_level="DEBUG")
    pyboy = PyBoy(default_rom, window="null", jit=False, debug=False)
    pyboy_jit.set_emulation_speed(0)
    pyboy.set_emulation_speed(0)

    for tick in range(60 * 10):
        pyboy_jit.tick()
        pyboy.tick()

        fail = False
        for addr in range(0xFFFF):
            a = pyboy.memory[addr]
            b = pyboy_jit.memory[addr]
            if a != b:
                print(f"{tick=} address: 0x{addr:04x} {a}!={b}")
                fail = True
        assert pyboy._cycles() == pyboy_jit._cycles(), pyboy._cycles() - pyboy_jit._cycles()
        assert not fail
