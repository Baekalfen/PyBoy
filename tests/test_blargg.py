#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json
import os.path
# TODO: The timeout should be emulator-cycle based
import platform
import time

from pyboy import PyBoy

from . import utils

if platform.python_implementation() == "PyPy":
    timeout = 15
else:
    timeout = 5


def run_rom(args):
    rom, frame_limit = args
    # logger.info(rom)
    pyboy = PyBoy(rom, window_type="dummy", window_scale=1, bootrom_file=utils.boot_rom, disable_input=True,
                  hide_window=True)
    # pyboy = PyBoy(utils.boot_rom, window_type="SDL2", window_scale=1, bootrom_file=rom, disable_input=True,
    # hide_window=True)
    pyboy.disable_title()
    pyboy.set_emulation_speed(0)
    serial_output = ""
    t = time.time()
    result = None
    frame_count = 0
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

        if frame_limit == -1 and time.time() - t > timeout:
            result = ("Timeout:\n" + serial_output)
            break
        elif frame_count == frame_limit:
            result = ("Frame limit reached:\n" + serial_output)
            break
        frame_count += 1
    pyboy.stop(save=False)
    return result


def test_blarggs():
    test_roms = [
        ("tests/BlarggROMs/instr_timing/instr_timing.gb", 1500),
        ("tests/BlarggROMs/mem_timing/mem_timing.gb", 430),
        ("tests/BlarggROMs/mem_timing/individual/02-write_timing.gb", 500),
        ("tests/BlarggROMs/mem_timing/individual/01-read_timing.gb", 500),
        ("tests/BlarggROMs/mem_timing/individual/03-modify_timing.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/cpu_instrs.gb", 5000),
        ("tests/BlarggROMs/cpu_instrs/individual/02-interrupts.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/09-op r,r.gb", 1000),
        ("tests/BlarggROMs/cpu_instrs/individual/11-op a,(hl).gb", 1500),
        ("tests/BlarggROMs/cpu_instrs/individual/10-bit ops.gb", 1500),
        ("tests/BlarggROMs/cpu_instrs/individual/04-op r,imm.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/01-special.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/06-ld r,r.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/03-op sp,hl.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/08-misc instrs.gb", 500),
        ("tests/BlarggROMs/cpu_instrs/individual/05-op rp.gb", 1000),
        # "tests/BlarggROMs/cgb_sound/rom_singles/11-regs after power.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/10-wave trigger while on.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/09-wave read while on.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/02-len ctr.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/01-registers.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/07-len sweep period sync.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/04-sweep.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/08-len ctr during power.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/05-sweep details.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/03-trigger.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/06-overflow on trigger.gb",
        # "tests/BlarggROMs/cgb_sound/rom_singles/12-wave.gb",
        # "tests/BlarggROMs/cgb_sound/cgb_sound.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/8-instr_effect.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/7-timing_effect.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/4-scanline_timing.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/2-causes.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/3-non_causes.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/6-timing_no_bug.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/1-lcd_sync.gb",
        # "tests/BlarggROMs/oam_bug/rom_singles/5-timing_bug.gb",
        # "tests/BlarggROMs/oam_bug/oam_bug.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/8-instr_effect.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/7-timing_effect.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/4-scanline_timing.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/2-causes.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/3-non_causes.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/6-timing_no_bug.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/1-lcd_sync.gb",
        # "tests/BlarggROMs/oam_bug-2/rom_singles/5-timing_bug.gb",
        # "tests/BlarggROMs/oam_bug-2/oam_bug.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/11-regs after power.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/10-wave trigger while on.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/12-wave write while on.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/09-wave read while on.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/02-len ctr.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/01-registers.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/07-len sweep period sync.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/04-sweep.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/08-len ctr during power.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/05-sweep details.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/03-trigger.gb",
        # "tests/BlarggROMs/dmg_sound/rom_singles/06-overflow on trigger.gb",
        # "tests/BlarggROMs/dmg_sound/dmg_sound.gb",
        # ("tests/BlarggROMs/mem_timing-2/rom_singles/02-write_timing.gb", -1),
        # ("tests/BlarggROMs/mem_timing-2/rom_singles/01-read_timing.gb", -1),
        # ("tests/BlarggROMs/mem_timing-2/rom_singles/03-modify_timing.gb", -1),
        # ("tests/BlarggROMs/mem_timing-2/mem_timing.gb", -1),
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/11-regs after power.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/10-wave trigger while on.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/12-wave write while on.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/09-wave read while on.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/02-len ctr.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/01-registers.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/07-len sweep period sync.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/04-sweep.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/08-len ctr during power.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/05-sweep details.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/03-trigger.gb",
        # "tests/BlarggROMs/dmg_sound-2/rom_singles/06-overflow on trigger.gb",
        # "tests/BlarggROMs/dmg_sound-2/dmg_sound.gb",
    ]

    if os.environ.get("TEST_DOCKER"):
        results = list(map(run_rom, test_roms))
    else:
        import multiprocessing as mp
        pool = mp.Pool(mp.cpu_count())
        results = pool.map(run_rom, test_roms)

    blargg_json = "tests/blargg.json"

    if os.path.isfile(blargg_json):
        with open(blargg_json, "r") as f:
            old_blargg = json.load(f)

            assert len(old_blargg) == len(test_roms)

            for (rom, _) in test_roms:
                assert old_blargg.get(rom)

            for (rom, _), res in zip(test_roms, results):
                assert old_blargg[rom] == res, f"Outputs don't match for {rom}"

    with open(blargg_json, "w") as f:
        json.dump(dict(zip([x for x, _ in test_roms], results)), f)

    if not os.environ.get("TEST_DOCKER"):
        with open("../PyBoy.wiki/blargg.md", "w") as f:
            f.write("# Test results for Blargg's test ROMs\n")
            f.write("|ROM|Result|\n")
            f.write("|---|---|\n")
            for (rom, _), res in zip(test_roms, results):
                f.write("|%s|%s|\n" % (rom, res.replace('\n', ' ').rstrip(':')))
