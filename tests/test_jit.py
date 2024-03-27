#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_jit_tick(default_rom):
    pyboy = PyBoy(default_rom, window="null", jit=False, debug=False)
    pyboy_jit = PyBoy(default_rom, window="null", jit=True, debug=False, log_level="DEBUG")
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


# def test_jit_LY(default_rom):
#     pyboy_jit = PyBoy(default_rom, window="null", jit=True, debug=False, log_level="ERROR")

#     asm = """
# spin:
#     ld A, (LY)
#     nop
#     nop
#     nop
#     nop
#     nop
#     nop
#     nop
#     nop
#     nop
#     jp spin
# """

#     for tick in range(60 * 10):
#         pyboy_jit.tick()


def test_jit_single_step(default_rom):
    pyboy = PyBoy(default_rom, window="null", jit=False, debug=False)
    pyboy_jit = PyBoy(default_rom, window="null", jit=True, debug=False, log_level="DEBUG")
    pyboy_jit.set_emulation_speed(0)
    pyboy.set_emulation_speed(0)

    for step in range(1_000_000):
        registers_jit = pyboy_jit._single_step()
        registers = pyboy._single_step()

        if registers_jit != registers:
            print("Fixing cycles?", pyboy._cycles(), pyboy_jit._cycles(), registers, registers_jit)
            # breakpoint()
            while pyboy._cycles() < pyboy_jit._cycles():
                registers = pyboy._single_step()
            assert registers == registers_jit
            assert pyboy._cycles() == pyboy_jit._cycles()
        else:
            print("Matching cycles:", pyboy._cycles(), pyboy_jit._cycles(), registers, registers_jit)
        # breakpoint()
