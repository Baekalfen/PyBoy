#! /usr/local/bin/python2


import traceback
import time
import os.path
import os
import sys
import platform
from PyBoy.Logger import logger
from PyBoy import PyBoy
import multiprocessing as mp

timeout = 5

def test_rom(rom):
    logger.info(rom)
    pyboy = PyBoy("dummy", 1, rom, "ROMs/DMG_ROM.bin")
    # pyboy = PyBoy("SDL2", 1, rom, "ROMs/DMG_ROM.bin")
    pyboy.disableTitle()
    pyboy.setLimitEmulationSpeed(False)
    serial_output = ""
    t = time.time()
    result = None
    while not pyboy.tick():
        b = pyboy.getSerial()
        if b != "":
            serial_output += b
            # print b,
            t = time.time()

        if "Passed" in serial_output:
            result = ("Passed")
            break
        elif "Failed" in serial_output:
            result = (serial_output)
            break

        if time.time()-t > timeout:
            result = ("Timeout:\n" + serial_output)
            break
    print(serial_output)
    pyboy.stop(save=False)
    return result

if __name__ == "__main__":
    pool = mp.Pool(mp.cpu_count())

    test_roms = [
        "TestROMs/instr_timing/instr_timing.gb",
        "TestROMs/mem_timing/mem_timing.gb",
        "TestROMs/mem_timing/individual/02-write_timing.gb",
        "TestROMs/mem_timing/individual/01-read_timing.gb",
        "TestROMs/mem_timing/individual/03-modify_timing.gb",
        "TestROMs/cpu_instrs/cpu_instrs.gb",
        "TestROMs/cpu_instrs/individual/02-interrupts.gb",
        "TestROMs/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
        "TestROMs/cpu_instrs/individual/09-op r,r.gb",
        "TestROMs/cpu_instrs/individual/11-op a,(hl).gb",
        "TestROMs/cpu_instrs/individual/10-bit ops.gb",
        "TestROMs/cpu_instrs/individual/04-op r,imm.gb",
        "TestROMs/cpu_instrs/individual/01-special.gb",
        "TestROMs/cpu_instrs/individual/06-ld r,r.gb",
        "TestROMs/cpu_instrs/individual/03-op sp,hl.gb",
        "TestROMs/cpu_instrs/individual/08-misc instrs.gb",
        "TestROMs/cpu_instrs/individual/05-op rp.gb",
        # "TestROMs/cgb_sound/rom_singles/11-regs after power.gb",
        # "TestROMs/cgb_sound/rom_singles/10-wave trigger while on.gb",
        # "TestROMs/cgb_sound/rom_singles/09-wave read while on.gb",
        # "TestROMs/cgb_sound/rom_singles/02-len ctr.gb",
        # "TestROMs/cgb_sound/rom_singles/01-registers.gb",
        # "TestROMs/cgb_sound/rom_singles/07-len sweep period sync.gb",
        # "TestROMs/cgb_sound/rom_singles/04-sweep.gb",
        # "TestROMs/cgb_sound/rom_singles/08-len ctr during power.gb",
        # "TestROMs/cgb_sound/rom_singles/05-sweep details.gb",
        # "TestROMs/cgb_sound/rom_singles/03-trigger.gb",
        # "TestROMs/cgb_sound/rom_singles/06-overflow on trigger.gb",
        # "TestROMs/cgb_sound/rom_singles/12-wave.gb",
        # "TestROMs/cgb_sound/cgb_sound.gb",
        # "TestROMs/oam_bug/rom_singles/8-instr_effect.gb",
        # "TestROMs/oam_bug/rom_singles/7-timing_effect.gb",
        # "TestROMs/oam_bug/rom_singles/4-scanline_timing.gb",
        # "TestROMs/oam_bug/rom_singles/2-causes.gb",
        # "TestROMs/oam_bug/rom_singles/3-non_causes.gb",
        # "TestROMs/oam_bug/rom_singles/6-timing_no_bug.gb",
        # "TestROMs/oam_bug/rom_singles/1-lcd_sync.gb",
        # "TestROMs/oam_bug/rom_singles/5-timing_bug.gb",
        # "TestROMs/oam_bug/oam_bug.gb",
        # "TestROMs/oam_bug-2/rom_singles/8-instr_effect.gb",
        # "TestROMs/oam_bug-2/rom_singles/7-timing_effect.gb",
        # "TestROMs/oam_bug-2/rom_singles/4-scanline_timing.gb",
        # "TestROMs/oam_bug-2/rom_singles/2-causes.gb",
        # "TestROMs/oam_bug-2/rom_singles/3-non_causes.gb",
        # "TestROMs/oam_bug-2/rom_singles/6-timing_no_bug.gb",
        # "TestROMs/oam_bug-2/rom_singles/1-lcd_sync.gb",
        # "TestROMs/oam_bug-2/rom_singles/5-timing_bug.gb",
        # "TestROMs/oam_bug-2/oam_bug.gb",
        # "TestROMs/dmg_sound/rom_singles/11-regs after power.gb",
        # "TestROMs/dmg_sound/rom_singles/10-wave trigger while on.gb",
        # "TestROMs/dmg_sound/rom_singles/12-wave write while on.gb",
        # "TestROMs/dmg_sound/rom_singles/09-wave read while on.gb",
        # "TestROMs/dmg_sound/rom_singles/02-len ctr.gb",
        # "TestROMs/dmg_sound/rom_singles/01-registers.gb",
        # "TestROMs/dmg_sound/rom_singles/07-len sweep period sync.gb",
        # "TestROMs/dmg_sound/rom_singles/04-sweep.gb",
        # "TestROMs/dmg_sound/rom_singles/08-len ctr during power.gb",
        # "TestROMs/dmg_sound/rom_singles/05-sweep details.gb",
        # "TestROMs/dmg_sound/rom_singles/03-trigger.gb",
        # "TestROMs/dmg_sound/rom_singles/06-overflow on trigger.gb",
        # "TestROMs/dmg_sound/dmg_sound.gb",
        "TestROMs/mem_timing-2/rom_singles/02-write_timing.gb",
        "TestROMs/mem_timing-2/rom_singles/01-read_timing.gb",
        "TestROMs/mem_timing-2/rom_singles/03-modify_timing.gb",
        "TestROMs/mem_timing-2/mem_timing.gb",
        # "TestROMs/dmg_sound-2/rom_singles/11-regs after power.gb",
        # "TestROMs/dmg_sound-2/rom_singles/10-wave trigger while on.gb",
        # "TestROMs/dmg_sound-2/rom_singles/12-wave write while on.gb",
        # "TestROMs/dmg_sound-2/rom_singles/09-wave read while on.gb",
        # "TestROMs/dmg_sound-2/rom_singles/02-len ctr.gb",
        # "TestROMs/dmg_sound-2/rom_singles/01-registers.gb",
        # "TestROMs/dmg_sound-2/rom_singles/07-len sweep period sync.gb",
        # "TestROMs/dmg_sound-2/rom_singles/04-sweep.gb",
        # "TestROMs/dmg_sound-2/rom_singles/08-len ctr during power.gb",
        # "TestROMs/dmg_sound-2/rom_singles/05-sweep details.gb",
        # "TestROMs/dmg_sound-2/rom_singles/03-trigger.gb",
        # "TestROMs/dmg_sound-2/rom_singles/06-overflow on trigger.gb",
        # "TestROMs/dmg_sound-2/dmg_sound.gb",
    ]
    # results = []

    # results = map(test_rom, test_roms)
    results = pool.map(test_rom, test_roms)
    # for rom in test_roms:

    with open("blargg.md", "w") as f:
        f.write("# Test results for Blargg's test ROMs\n")
        f.write("|Test ROM|Result|\n")
        f.write("|---|---|\n")
        for rom, res in zip(test_roms, results):
            f.write("|%s|%s|\n" % (rom, res.replace('\n', ' ').rstrip(':')))




