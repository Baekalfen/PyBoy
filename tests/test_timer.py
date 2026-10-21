from random import Random

import pytest

from pyboy import PyBoy
from pyboy.core.timer import Timer
from pyboy.utils import MAX_CYCLES, cython_compiled


def _reference_timer_tick(timer, _cycles):
    cycles = _cycles - timer.last_cycles
    if cycles == 0:
        return False
    timer.last_cycles = _cycles

    if not timer.TAC & 0b100 and not timer.tima_reload_state:
        timer.DIV_counter = (timer.DIV_counter + cycles) & 0xFFFF
        timer.DIV = timer.DIV_counter >> 8
        timer._update_cycles_to_irq()
        return False

    ret = False
    while cycles:
        if timer.tima_reload_state:
            timer.TIMA_counter -= 1
            if timer.TIMA_counter == 0:
                if timer.tima_reload_state == 1:
                    timer.tima_reload_state = 2
                    timer.TIMA_counter = 4
                    ret = True
                else:
                    timer.tima_reload_state = 0

        counter = timer.DIV_counter
        new_counter = (counter + 1) & 0xFFFF
        timer_bit = 1 << (timer.dividers[timer.TAC & 0b11] - 1)
        if timer.TAC & 0b100 and counter & timer_bit and not new_counter & timer_bit:
            timer._increase_tima()

        timer.DIV_counter = new_counter
        timer.DIV = new_counter >> 8
        cycles -= 1

    timer._update_cycles_to_irq()
    return ret


@pytest.mark.skipif(cython_compiled, reason="This test requires access to internal timer registers")
def test_timer_tick_matches_cycle_by_cycle_reference():
    rng = Random(0x54494D41)
    fields = (
        "DIV",
        "TIMA",
        "DIV_counter",
        "TIMA_counter",
        "TMA",
        "TAC",
        "tima_reload_state",
        "_cycles_to_irq",
        "last_cycles",
    )

    def compare(initial, absolute_cycles):
        actual = Timer()
        expected = Timer()
        for field, value in initial.items():
            setattr(actual, field, value)
            setattr(expected, field, value)

        actual_result = actual.tick(absolute_cycles)
        expected_result = _reference_timer_tick(expected, absolute_cycles)
        assert actual_result == expected_result
        assert tuple(getattr(actual, field) for field in fields) == tuple(getattr(expected, field) for field in fields)

    for _ in range(1000):
        divider = rng.randrange(0x10000)
        reload_state = rng.randrange(3)
        initial = {
            "DIV": divider >> 8,
            "TIMA": rng.randrange(0x100),
            "DIV_counter": divider,
            "TIMA_counter": rng.randrange(1, 5) if reload_state else 0,
            "TMA": rng.randrange(0x100),
            "TAC": rng.randrange(8),
            "tima_reload_state": reload_state,
            "_cycles_to_irq": rng.randrange(0x10000),
            "last_cycles": rng.randrange(0x1000),
        }
        compare(initial, initial["last_cycles"] + rng.randrange(0x1001))

    for tac in (0b100, 0b101, 0b110, 0b111):
        timer = Timer()
        timer_bit = 1 << (timer.dividers[tac & 0b11] - 1)
        period = timer_bit * 2
        for remaining in range(1, 5):
            divider = ((period - remaining) & (period - 1)) | 0xFFF0
            initial = {
                "DIV": divider >> 8,
                "TIMA": 0xFF,
                "DIV_counter": divider,
                "TIMA_counter": remaining,
                "TMA": 0xFF,
                "TAC": tac,
                "tima_reload_state": 1,
                "_cycles_to_irq": MAX_CYCLES,
                "last_cycles": 0,
            }
            compare(initial, remaining + period * 2)


def test_divider_advances_with_tima_disabled(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    try:
        pyboy.memory[0xFF07] = 0
        pyboy.memory[0xFF05] = 0x5A
        pyboy.memory[0xFF04] = 0

        pyboy.tick(1, render=False)

        assert pyboy.memory[0xFF04] != 0
        assert pyboy.memory[0xFF05] == 0x5A
    finally:
        pyboy.stop(save=False)


def test_timer_interrupt_is_scheduled_after_tac_write(default_rom):
    pyboy = PyBoy(default_rom, window="null", sound_emulated=False)
    pyboy.set_emulation_speed(0)
    try:
        for offset, value in enumerate((0x3E, 0xFF, 0xE0, 0x05, 0x3E, 0x05, 0xE0, 0x07, 0x18, 0xFE)):
            pyboy.memory[0xFF80 + offset] = value
        pyboy.register_file.PC = 0xFF80
        pyboy.memory[0xFF0F] = 0

        pyboy.tick(1, render=False, sound=False)

        assert pyboy.memory[0xFF0F] & 0b0000_0100
    finally:
        pyboy.stop(save=False)
