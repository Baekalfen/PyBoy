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
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import pytest
from pyboy import PyBoy

OVERWRITE_JSON = False

blargg_json = "test_results/blargg.json"


def run_rom(rom):
    pyboy = PyBoy(rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    t = time.time()
    result = ""
    while not pyboy.tick():
        b = pyboy._serial()
        if b != "":
            result += b
            t = time.time()

        if pyboy._is_cpu_stuck():
            break

    for _ in range(10):
        pyboy.tick()
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
    "rom",
    [
        # "blargg/cgb_sound/cgb_sound.gb",
        # "blargg/cgb_sound/rom_singles/01-registers.gb",
        # "blargg/cgb_sound/rom_singles/02-len ctr.gb",
        # "blargg/cgb_sound/rom_singles/03-trigger.gb",
        # "blargg/cgb_sound/rom_singles/04-sweep.gb",
        # "blargg/cgb_sound/rom_singles/05-sweep details.gb",
        # "blargg/cgb_sound/rom_singles/06-overflow on trigger.gb",
        # "blargg/cgb_sound/rom_singles/07-len sweep period sync.gb",
        # "blargg/cgb_sound/rom_singles/08-len ctr during power.gb",
        # "blargg/cgb_sound/rom_singles/09-wave read while on.gb",
        # "blargg/cgb_sound/rom_singles/10-wave trigger while on.gb",
        # "blargg/cgb_sound/rom_singles/11-regs after power.gb",
        # "blargg/cgb_sound/rom_singles/12-wave.gb",
        "blargg/cpu_instrs/cpu_instrs.gb",
        "blargg/cpu_instrs/individual/01-special.gb",
        "blargg/cpu_instrs/individual/02-interrupts.gb",
        "blargg/cpu_instrs/individual/03-op sp,hl.gb",
        "blargg/cpu_instrs/individual/04-op r,imm.gb",
        "blargg/cpu_instrs/individual/05-op rp.gb",
        "blargg/cpu_instrs/individual/06-ld r,r.gb",
        "blargg/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
        "blargg/cpu_instrs/individual/08-misc instrs.gb",
        "blargg/cpu_instrs/individual/09-op r,r.gb",
        "blargg/cpu_instrs/individual/10-bit ops.gb",
        "blargg/cpu_instrs/individual/11-op a,(hl).gb",
        "blargg/dmg_sound/dmg_sound.gb",
        "blargg/dmg_sound/rom_singles/01-registers.gb",
        "blargg/dmg_sound/rom_singles/02-len ctr.gb",
        "blargg/dmg_sound/rom_singles/03-trigger.gb",
        "blargg/dmg_sound/rom_singles/04-sweep.gb",
        "blargg/dmg_sound/rom_singles/05-sweep details.gb",
        "blargg/dmg_sound/rom_singles/06-overflow on trigger.gb",
        "blargg/dmg_sound/rom_singles/07-len sweep period sync.gb",
        "blargg/dmg_sound/rom_singles/08-len ctr during power.gb",
        "blargg/dmg_sound/rom_singles/09-wave read while on.gb",
        "blargg/dmg_sound/rom_singles/10-wave trigger while on.gb",
        "blargg/dmg_sound/rom_singles/11-regs after power.gb",
        "blargg/dmg_sound/rom_singles/12-wave write while on.gb",
        "blargg/instr_timing/instr_timing.gb",
        "blargg/interrupt_time/interrupt_time.gb",
        "blargg/mem_timing/individual/01-read_timing.gb",
        "blargg/mem_timing/individual/02-write_timing.gb",
        "blargg/mem_timing/individual/03-modify_timing.gb",
        "blargg/mem_timing/mem_timing.gb",
        "blargg/mem_timing-2/mem_timing.gb",
        "blargg/mem_timing-2/rom_singles/01-read_timing.gb",
        "blargg/mem_timing-2/rom_singles/02-write_timing.gb",
        "blargg/mem_timing-2/rom_singles/03-modify_timing.gb",
        "blargg/oam_bug/oam_bug.gb",
        "blargg/oam_bug/rom_singles/1-lcd_sync.gb",
        "blargg/oam_bug/rom_singles/2-causes.gb",
        "blargg/oam_bug/rom_singles/3-non_causes.gb",
        "blargg/oam_bug/rom_singles/4-scanline_timing.gb",
        "blargg/oam_bug/rom_singles/5-timing_bug.gb",
        "blargg/oam_bug/rom_singles/6-timing_no_bug.gb",
        "blargg/oam_bug/rom_singles/7-timing_effect.gb",
        "blargg/oam_bug/rom_singles/8-instr_effect.gb",
    ]
)
def test_blarggs(rom):
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    blargg_dir = Path("blargg")
    if not os.path.isdir(blargg_dir):
        print(urllib.request.urlopen("https://pyboy.dk/mirror/LICENSE.blargg.txt").read())

        for name in [
            "cgb_sound",
            "cpu_instrs",
            "dmg_sound",
            "halt_bug",
            "instr_timing",
            "interrupt_time",
            "mem_timing-2",
            "mem_timing",
            "oam_bug",
        ]:
            blargg_data = io.BytesIO(urllib.request.urlopen(f"https://pyboy.dk/mirror/blargg/{name}.zip").read())
            with ZipFile(blargg_data) as _zip:
                _zip.extractall(blargg_dir)

    result = run_rom(rom)

    if os.path.isfile(blargg_json):
        with open(blargg_json, "r") as f:
            old_blargg = json.load(f)
    else:
        old_blargg = None

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
