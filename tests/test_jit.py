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


def _registers(registers):
    A, F, B, C, D, E, HL, SP, PC, PC_1, PC_2, HL_0, HL_1 = registers
    return f"{A=:02x}, {F=:02x}, {B=:02x}, {C=:02x}, {D=:02x}, {E=:02x}, {HL=:04x}, {SP=:04x}, {PC=:04x}, {PC_1=:04x}, {PC_2=:04x}, {HL_0=:02x}, {HL_1=:02x}"


def test_jit_single_step(default_rom):
    pyboy = PyBoy(default_rom, window="null", jit=False, debug=False)
    pyboy_jit = PyBoy(default_rom, window="null", jit=True, debug=False, log_level="DEBUG")
    pyboy_jit.set_emulation_speed(0)
    pyboy.set_emulation_speed(0)

    for step in range(1_000_000):
        registers_jit = pyboy_jit._single_step()
        registers = pyboy._single_step()

        if registers_jit != registers:
            print(
                "Fixing cycles?", pyboy._cycles(), pyboy_jit._cycles(), "\n", _registers(registers), "\n",
                _registers(registers_jit)
            )
            # breakpoint()
            while pyboy._cycles() < pyboy_jit._cycles():
                registers = pyboy._single_step()
                print("Inc non-jit", "\n", _registers(registers))
            assert registers == registers_jit
            assert pyboy._cycles() == pyboy_jit._cycles()
        else:
            print(
                "Matching cycles:", pyboy._cycles(), pyboy_jit._cycles(), "\n", _registers(registers), "\n",
                _registers(registers_jit)
            )
        # breakpoint()
