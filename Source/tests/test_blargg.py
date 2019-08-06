#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json
import time
import os.path

import sys
sys.path.append("..") # Adds higher directory to python modules path.

# from pyboy.logger import logger
from pyboy import PyBoy
import multiprocessing as mp

timeout = 5


def run_rom(rom):
    # logger.info(rom)
    pyboy = PyBoy("dummy", 1, rom, "../ROMs/DMG_ROM.bin")
    # pyboy = PyBoy("SDL2", 1, rom, "../ROMs/DMG_ROM.bin")
    pyboy.disable_title()
    pyboy.set_emulation_speed(False)
    serial_output = ""
    t = time.time()
    result = None
    while not pyboy.tick():
        b = pyboy.get_serial()
        if b != "":
            serial_output += b
            t = time.time()

        if "Passed" in serial_output:
            result = ("Passed")
            break
        elif "Failed" in serial_output:
            result = (serial_output)
            break

        if time.time() - t > timeout:
            result = ("Timeout:\n" + serial_output)
            break
    pyboy.stop(save=False)
    return result


def test_blarggs():
    test_roms = [
        "BlarggROMs/instr_timing/instr_timing.gb",
        "BlarggROMs/mem_timing/mem_timing.gb",
        "BlarggROMs/mem_timing/individual/02-write_timing.gb",
        "BlarggROMs/mem_timing/individual/01-read_timing.gb",
        "BlarggROMs/mem_timing/individual/03-modify_timing.gb",
        "BlarggROMs/cpu_instrs/cpu_instrs.gb",
        "BlarggROMs/cpu_instrs/individual/02-interrupts.gb",
        "BlarggROMs/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
        "BlarggROMs/cpu_instrs/individual/09-op r,r.gb",
        "BlarggROMs/cpu_instrs/individual/11-op a,(hl).gb",
        "BlarggROMs/cpu_instrs/individual/10-bit ops.gb",
        "BlarggROMs/cpu_instrs/individual/04-op r,imm.gb",
        "BlarggROMs/cpu_instrs/individual/01-special.gb",
        "BlarggROMs/cpu_instrs/individual/06-ld r,r.gb",
        "BlarggROMs/cpu_instrs/individual/03-op sp,hl.gb",
        "BlarggROMs/cpu_instrs/individual/08-misc instrs.gb",
        "BlarggROMs/cpu_instrs/individual/05-op rp.gb",
        # "BlarggROMs/cgb_sound/rom_singles/11-regs after power.gb",
        # "BlarggROMs/cgb_sound/rom_singles/10-wave trigger while on.gb",
        # "BlarggROMs/cgb_sound/rom_singles/09-wave read while on.gb",
        # "BlarggROMs/cgb_sound/rom_singles/02-len ctr.gb",
        # "BlarggROMs/cgb_sound/rom_singles/01-registers.gb",
        # "BlarggROMs/cgb_sound/rom_singles/07-len sweep period sync.gb",
        # "BlarggROMs/cgb_sound/rom_singles/04-sweep.gb",
        # "BlarggROMs/cgb_sound/rom_singles/08-len ctr during power.gb",
        # "BlarggROMs/cgb_sound/rom_singles/05-sweep details.gb",
        # "BlarggROMs/cgb_sound/rom_singles/03-trigger.gb",
        # "BlarggROMs/cgb_sound/rom_singles/06-overflow on trigger.gb",
        # "BlarggROMs/cgb_sound/rom_singles/12-wave.gb",
        # "BlarggROMs/cgb_sound/cgb_sound.gb",
        # "BlarggROMs/oam_bug/rom_singles/8-instr_effect.gb",
        # "BlarggROMs/oam_bug/rom_singles/7-timing_effect.gb",
        # "BlarggROMs/oam_bug/rom_singles/4-scanline_timing.gb",
        # "BlarggROMs/oam_bug/rom_singles/2-causes.gb",
        # "BlarggROMs/oam_bug/rom_singles/3-non_causes.gb",
        # "BlarggROMs/oam_bug/rom_singles/6-timing_no_bug.gb",
        # "BlarggROMs/oam_bug/rom_singles/1-lcd_sync.gb",
        # "BlarggROMs/oam_bug/rom_singles/5-timing_bug.gb",
        # "BlarggROMs/oam_bug/oam_bug.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/8-instr_effect.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/7-timing_effect.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/4-scanline_timing.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/2-causes.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/3-non_causes.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/6-timing_no_bug.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/1-lcd_sync.gb",
        # "BlarggROMs/oam_bug-2/rom_singles/5-timing_bug.gb",
        # "BlarggROMs/oam_bug-2/oam_bug.gb",
        # "BlarggROMs/dmg_sound/rom_singles/11-regs after power.gb",
        # "BlarggROMs/dmg_sound/rom_singles/10-wave trigger while on.gb",
        # "BlarggROMs/dmg_sound/rom_singles/12-wave write while on.gb",
        # "BlarggROMs/dmg_sound/rom_singles/09-wave read while on.gb",
        # "BlarggROMs/dmg_sound/rom_singles/02-len ctr.gb",
        # "BlarggROMs/dmg_sound/rom_singles/01-registers.gb",
        # "BlarggROMs/dmg_sound/rom_singles/07-len sweep period sync.gb",
        # "BlarggROMs/dmg_sound/rom_singles/04-sweep.gb",
        # "BlarggROMs/dmg_sound/rom_singles/08-len ctr during power.gb",
        # "BlarggROMs/dmg_sound/rom_singles/05-sweep details.gb",
        # "BlarggROMs/dmg_sound/rom_singles/03-trigger.gb",
        # "BlarggROMs/dmg_sound/rom_singles/06-overflow on trigger.gb",
        # "BlarggROMs/dmg_sound/dmg_sound.gb",
        "BlarggROMs/mem_timing-2/rom_singles/02-write_timing.gb",
        "BlarggROMs/mem_timing-2/rom_singles/01-read_timing.gb",
        "BlarggROMs/mem_timing-2/rom_singles/03-modify_timing.gb",
        "BlarggROMs/mem_timing-2/mem_timing.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/11-regs after power.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/10-wave trigger while on.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/12-wave write while on.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/09-wave read while on.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/02-len ctr.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/01-registers.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/07-len sweep period sync.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/04-sweep.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/08-len ctr during power.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/05-sweep details.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/03-trigger.gb",
        # "BlarggROMs/dmg_sound-2/rom_singles/06-overflow on trigger.gb",
        # "BlarggROMs/dmg_sound-2/dmg_sound.gb",
    ]

    pool = mp.Pool(mp.cpu_count())
    results = pool.map(run_rom, test_roms)

    blargg_json = "blargg.json"

    if os.path.isfile(blargg_json):
        with open(blargg_json, "r") as f:
            old_blargg = json.load(f)

            assert len(old_blargg) == len(test_roms)

            for rom in test_roms:
                assert old_blargg.get(rom)

            for rom, res in zip(test_roms, results):
                assert old_blargg[rom] == res, f"Outputs don't match for {rom}"

    with open(blargg_json, "w") as f:
        json.dump(dict(zip(test_roms, results)), f)

    with open("blargg.md", "w") as f:
        f.write("# Test results for Blargg's test ROMs\n")
        f.write("|ROM|Result|\n")
        f.write("|---|---|\n")
        for rom, res in zip(test_roms, results):
            f.write("|%s|%s|\n" % (rom, res.replace('\n', ' ').rstrip(':')))
