#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import json
import os.path
import platform
import sys
import time
from pathlib import Path

import pytest

from pyboy import PyBoy

OVERWRITE_JSON = False

blargg_json = "tests/test_results/blargg.json"


def run_rom(rom):
    pyboy = PyBoy(str(rom), window_type="dummy", cgb="cgb" in rom, sound_emulated=True)
    pyboy.set_emulation_speed(0)
    t = time.time()
    result = ""
    while pyboy.tick(1, False):
        b = pyboy._serial()
        if b != "":
            result += b
            t = time.time()

        if pyboy._is_cpu_stuck():
            break

    pyboy.tick(10, False)
    pyboy.stop(save=False)
    result += pyboy._serial() # Getting the absolute last. Some times the tests says "Failed X tests".
    if result == "":
        n = 0
        while True:
            char = pyboy.get_memory_value(0xA004 + n)
            if char != 0:
                result += chr(char)
            n += 1

            if n > 250:
                break
    return result


@pytest.mark.parametrize(
    "test_rom", [
        "cgb_sound/cgb_sound.gb",
        "cgb_sound/rom_singles/01-registers.gb",
        "cgb_sound/rom_singles/02-len ctr.gb",
        "cgb_sound/rom_singles/03-trigger.gb",
        "cgb_sound/rom_singles/04-sweep.gb",
        "cgb_sound/rom_singles/05-sweep details.gb",
        "cgb_sound/rom_singles/06-overflow on trigger.gb",
        "cgb_sound/rom_singles/07-len sweep period sync.gb",
        "cgb_sound/rom_singles/08-len ctr during power.gb",
        "cgb_sound/rom_singles/09-wave read while on.gb",
        "cgb_sound/rom_singles/10-wave trigger while on.gb",
        "cgb_sound/rom_singles/11-regs after power.gb",
        "cgb_sound/rom_singles/12-wave.gb",
        "cpu_instrs/cpu_instrs.gb",
        "cpu_instrs/individual/01-special.gb",
        "cpu_instrs/individual/02-interrupts.gb",
        "cpu_instrs/individual/03-op sp,hl.gb",
        "cpu_instrs/individual/04-op r,imm.gb",
        "cpu_instrs/individual/05-op rp.gb",
        "cpu_instrs/individual/06-ld r,r.gb",
        "cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
        "cpu_instrs/individual/08-misc instrs.gb",
        "cpu_instrs/individual/09-op r,r.gb",
        "cpu_instrs/individual/10-bit ops.gb",
        "cpu_instrs/individual/11-op a,(hl).gb",
        "dmg_sound/dmg_sound.gb",
        "dmg_sound/rom_singles/01-registers.gb",
        "dmg_sound/rom_singles/02-len ctr.gb",
        "dmg_sound/rom_singles/03-trigger.gb",
        "dmg_sound/rom_singles/04-sweep.gb",
        "dmg_sound/rom_singles/05-sweep details.gb",
        "dmg_sound/rom_singles/06-overflow on trigger.gb",
        "dmg_sound/rom_singles/07-len sweep period sync.gb",
        "dmg_sound/rom_singles/08-len ctr during power.gb",
        "dmg_sound/rom_singles/09-wave read while on.gb",
        "dmg_sound/rom_singles/10-wave trigger while on.gb",
        "dmg_sound/rom_singles/11-regs after power.gb",
        "dmg_sound/rom_singles/12-wave write while on.gb",
        "instr_timing/instr_timing.gb",
        "interrupt_time/interrupt_time.gb",
        "mem_timing/individual/01-read_timing.gb",
        "mem_timing/individual/02-write_timing.gb",
        "mem_timing/individual/03-modify_timing.gb",
        "mem_timing/mem_timing.gb",
        "mem_timing-2/mem_timing.gb",
        "mem_timing-2/rom_singles/01-read_timing.gb",
        "mem_timing-2/rom_singles/02-write_timing.gb",
        "mem_timing-2/rom_singles/03-modify_timing.gb",
        "oam_bug/oam_bug.gb",
        "oam_bug/rom_singles/1-lcd_sync.gb",
        "oam_bug/rom_singles/2-causes.gb",
        "oam_bug/rom_singles/3-non_causes.gb",
        "oam_bug/rom_singles/4-scanline_timing.gb",
        "oam_bug/rom_singles/5-timing_bug.gb",
        "oam_bug/rom_singles/6-timing_no_bug.gb",
        "oam_bug/rom_singles/7-timing_effect.gb",
        "oam_bug/rom_singles/8-instr_effect.gb",
    ]
)
def test_blarggs(test_rom, blargg_dir):
    rom = str(blargg_dir / Path(test_rom))
    result = run_rom(rom)

    if os.path.isfile(blargg_json):
        with open(blargg_json, "r") as f:
            old_blargg = json.load(f)
    else:
        old_blargg = None

    rom = rom.replace("\\", "/") # Fix Windows lookup
    rom = rom.replace("test_roms/", "")
    if OVERWRITE_JSON:
        with open(blargg_json, "w") as f:
            old_blargg[rom] = result
            json.dump(old_blargg, f, indent=4)

        blargg_md = "../PyBoy.wiki/blargg.md"
        if os.path.isdir(blargg_md):
            with open(blargg_md, "w") as f:
                f.write("# Test results for Blargg's test ROMs\n")
                f.write("|ROM|Result|\n")
                f.write("|---|---|\n")
                for (rom, _), res in zip(test_roms, old_blargg):
                    f.write("|%s|%s|\n" % (rom, res.replace("\n", " ").rstrip(":")))
    else:
        assert old_blargg[rom] == result, f"Outputs don't match for {rom}"
