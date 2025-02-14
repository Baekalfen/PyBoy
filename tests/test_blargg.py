#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json
import os.path
from pathlib import Path

import pytest

from pyboy import PyBoy

OVERWRITE_JSON = False

blargg_json = "tests/test_results/blargg.json"


def run_rom(rom, max_frames):
    pyboy = PyBoy(str(rom), window="null", cgb="cgb" in rom)
    pyboy.set_emulation_speed(0)
    result = ""
    while pyboy.tick(1, False, False):
        b = pyboy._serial()
        if b != "":
            result += b

        if pyboy._is_cpu_stuck() or pyboy.frame_count > max_frames:
            break

    pyboy.tick(10, False, False)
    pyboy.stop(save=False)
    result += pyboy._serial()  # Getting the absolute last. Some times the tests says "Failed X tests".
    if result == "":
        n = 0
        while True:
            char = pyboy.memory[0xA004 + n]
            if char != 0:
                result += chr(char)
            n += 1

            if n > 250:
                break
    return result


@pytest.mark.parametrize(
    "test_rom, max_frames",
    [
        ("cgb_sound/cgb_sound.gb", 4_000),
        ("cgb_sound/rom_singles/01-registers.gb", 700),
        ("cgb_sound/rom_singles/02-len ctr.gb", 700),
        ("cgb_sound/rom_singles/03-trigger.gb", 700),
        ("cgb_sound/rom_singles/04-sweep.gb", 700),
        ("cgb_sound/rom_singles/05-sweep details.gb", 700),
        ("cgb_sound/rom_singles/06-overflow on trigger.gb", 700),
        ("cgb_sound/rom_singles/07-len sweep period sync.gb", 700),
        ("cgb_sound/rom_singles/08-len ctr during power.gb", 700),
        ("cgb_sound/rom_singles/09-wave read while on.gb", 700),
        ("cgb_sound/rom_singles/10-wave trigger while on.gb", 700),
        ("cgb_sound/rom_singles/11-regs after power.gb", 700),
        ("cgb_sound/rom_singles/12-wave.gb", 700),
        ("cpu_instrs/cpu_instrs.gb", 4_000),
        ("cpu_instrs/individual/01-special.gb", 700),
        ("cpu_instrs/individual/02-interrupts.gb", 700),
        ("cpu_instrs/individual/03-op sp,hl.gb", 700),
        ("cpu_instrs/individual/04-op r,imm.gb", 700),
        ("cpu_instrs/individual/05-op rp.gb", 700),
        ("cpu_instrs/individual/06-ld r,r.gb", 700),
        ("cpu_instrs/individual/07-jr,jp,call,ret,rst.gb", 700),
        ("cpu_instrs/individual/08-misc instrs.gb", 700),
        ("cpu_instrs/individual/09-op r,r.gb", 700),
        ("cpu_instrs/individual/10-bit ops.gb", 2_000),
        ("cpu_instrs/individual/11-op a,(hl).gb", 2_000),
        ("dmg_sound/dmg_sound.gb", 700),
        ("dmg_sound/rom_singles/01-registers.gb", 700),
        ("dmg_sound/rom_singles/02-len ctr.gb", 700),
        ("dmg_sound/rom_singles/03-trigger.gb", 700),
        ("dmg_sound/rom_singles/04-sweep.gb", 700),
        ("dmg_sound/rom_singles/05-sweep details.gb", 700),
        ("dmg_sound/rom_singles/06-overflow on trigger.gb", 700),
        ("dmg_sound/rom_singles/07-len sweep period sync.gb", 700),
        ("dmg_sound/rom_singles/08-len ctr during power.gb", 700),
        ("dmg_sound/rom_singles/09-wave read while on.gb", 700),
        ("dmg_sound/rom_singles/10-wave trigger while on.gb", 700),
        ("dmg_sound/rom_singles/11-regs after power.gb", 700),
        ("dmg_sound/rom_singles/12-wave write while on.gb", 700),
        ("instr_timing/instr_timing.gb", 2_000),
        ("interrupt_time/interrupt_time.gb", 700),
        ("mem_timing/individual/01-read_timing.gb", 700),
        ("mem_timing/individual/02-write_timing.gb", 700),
        ("mem_timing/individual/03-modify_timing.gb", 700),
        ("mem_timing/mem_timing.gb", 700),
        ("mem_timing-2/mem_timing.gb", 700),
        ("mem_timing-2/rom_singles/01-read_timing.gb", 700),
        ("mem_timing-2/rom_singles/02-write_timing.gb", 700),
        ("mem_timing-2/rom_singles/03-modify_timing.gb", 700),
        ("oam_bug/oam_bug.gb", 2_000),
        ("oam_bug/rom_singles/1-lcd_sync.gb", 700),
        ("oam_bug/rom_singles/2-causes.gb", 700),
        ("oam_bug/rom_singles/3-non_causes.gb", 700),
        ("oam_bug/rom_singles/4-scanline_timing.gb", 700),
        ("oam_bug/rom_singles/5-timing_bug.gb", 700),
        ("oam_bug/rom_singles/6-timing_no_bug.gb", 700),
        ("oam_bug/rom_singles/7-timing_effect.gb", 700),
        ("oam_bug/rom_singles/8-instr_effect.gb", 700),
    ],
)
def test_blarggs(test_rom, max_frames, blargg_dir):
    rom = str(blargg_dir / Path(test_rom))
    result = run_rom(rom, max_frames)

    if os.path.isfile(blargg_json):
        with open(blargg_json, "r") as f:
            old_blargg = json.load(f)
    else:
        old_blargg = None

    rom = rom.replace("\\", "/")  # Fix Windows lookup
    rom = rom.replace("test_roms/", "")
    if OVERWRITE_JSON:
        with open(blargg_json, "w") as f:
            old_blargg[rom] = result
            json.dump(old_blargg, f, indent=4)

        # TODO: Not usable atm.
        # blargg_md = "../PyBoy.wiki/blargg.md"
        # if os.path.isdir(blargg_md):
        #     with open(blargg_md, "w") as f:
        #         f.write("# Test results for Blargg's test ROMs\n")
        #         f.write("|ROM|Result|\n")
        #         f.write("|---|---|\n")
        #         for (rom, _), res in zip(test_roms, old_blargg):
        #             f.write("|%s|%s|\n" % (rom, res.replace("\n", " ").rstrip(":")))
    else:
        assert old_blargg[rom] == result, f"Outputs don't match for {rom}"
