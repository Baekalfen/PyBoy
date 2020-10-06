#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import PIL
from pyboy import PyBoy
from tests.utils import default_rom

if platform.python_implementation() == "PyPy":
    timeout = 15
else:
    timeout = 5

OVERWRITE_PNGS = False


def test_mooneye():
    # Has to be in here. Otherwise all test workers will import the file, and cause an error.
    mooneye_dir = "mooneye"
    if not os.path.isdir(mooneye_dir):
        print(urllib.request.urlopen("https://pyboy.dk/mirror/LICENSE.mooneye.txt").read())
        mooneye_data = io.BytesIO(urllib.request.urlopen("https://pyboy.dk/mirror/mooneye.zip").read())
        with ZipFile(mooneye_data) as _zip:
            _zip.extractall(mooneye_dir)

    test_roms = [
        ####################
        # These are meant to fail on DMG:
        # (False, "mooneye/misc/boot_div-A.gb"),
        # (False, "mooneye/misc/boot_div-cgb0.gb"),
        # (False, "mooneye/misc/boot_div-cgbABCDE.gb"),
        # (False, "mooneye/misc/boot_hwio-C.gb"),
        # (False, "mooneye/misc/boot_regs-A.gb"),
        # (False, "mooneye/misc/boot_regs-cgb.gb"),
        # (False, "mooneye/misc/ppu/vblank_stat_intr-C.gb"),
        # (False, "mooneye/misc/bits/unused_hwio-C.gb"),

        # (False, "mooneye/utils/bootrom_dumper.gb"),
        # (False, "mooneye/utils/dump_boot_hwio.gb"),
        (False, "mooneye/manual-only/sprite_priority.gb"),
        (False, "mooneye/acceptance/rapid_di_ei.gb"),
        (False, "mooneye/acceptance/oam_dma_start.gb"),
        (False, "mooneye/acceptance/boot_regs-dmgABC.gb"),
        (False, "mooneye/acceptance/reti_timing.gb"),
        (False, "mooneye/acceptance/call_timing.gb"),
        (False, "mooneye/acceptance/reti_intr_timing.gb"),
        (False, "mooneye/acceptance/boot_regs-mgb.gb"),
        (False, "mooneye/acceptance/ei_sequence.gb"),
        (False, "mooneye/acceptance/jp_timing.gb"),
        (False, "mooneye/acceptance/ei_timing.gb"),
        (False, "mooneye/acceptance/oam_dma_timing.gb"),
        (False, "mooneye/acceptance/call_cc_timing2.gb"),
        (False, "mooneye/acceptance/boot_div2-S.gb"),
        (False, "mooneye/acceptance/halt_ime1_timing.gb"),
        (False, "mooneye/acceptance/halt_ime1_timing2-GS.gb"),
        (False, "mooneye/acceptance/timer/tima_reload.gb"),
        (False, "mooneye/acceptance/timer/tma_write_reloading.gb"),
        (False, "mooneye/acceptance/timer/tim10.gb"),
        (False, "mooneye/acceptance/timer/tim00.gb"),
        (False, "mooneye/acceptance/timer/tim11.gb"),
        (False, "mooneye/acceptance/timer/tim01.gb"),
        (False, "mooneye/acceptance/timer/tima_write_reloading.gb"),
        (False, "mooneye/acceptance/timer/tim11_div_trigger.gb"),
        (False, "mooneye/acceptance/timer/div_write.gb"),
        (False, "mooneye/acceptance/timer/tim10_div_trigger.gb"),
        (False, "mooneye/acceptance/timer/tim00_div_trigger.gb"),
        (False, "mooneye/acceptance/timer/rapid_toggle.gb"),
        (False, "mooneye/acceptance/timer/tim01_div_trigger.gb"),
        (False, "mooneye/acceptance/boot_regs-sgb.gb"),
        (False, "mooneye/acceptance/jp_cc_timing.gb"),
        (False, "mooneye/acceptance/call_timing2.gb"),
        (False, "mooneye/acceptance/ld_hl_sp_e_timing.gb"),
        (False, "mooneye/acceptance/push_timing.gb"),
        (False, "mooneye/acceptance/boot_hwio-dmg0.gb"),
        (False, "mooneye/acceptance/rst_timing.gb"),
        (False, "mooneye/acceptance/boot_hwio-S.gb"),
        (False, "mooneye/acceptance/boot_div-dmgABCmgb.gb"),
        (False, "mooneye/acceptance/bits/mem_oam.gb"),
        (False, "mooneye/acceptance/bits/reg_f.gb"),
        (False, "mooneye/acceptance/bits/unused_hwio-GS.gb"),
        (False, "mooneye/acceptance/div_timing.gb"),
        (False, "mooneye/acceptance/ret_cc_timing.gb"),
        (False, "mooneye/acceptance/boot_regs-dmg0.gb"),
        (False, "mooneye/acceptance/interrupts/ie_push.gb"),
        (False, "mooneye/acceptance/boot_hwio-dmgABCmgb.gb"),
        (False, "mooneye/acceptance/pop_timing.gb"),
        (False, "mooneye/acceptance/ret_timing.gb"),
        (False, "mooneye/acceptance/oam_dma_restart.gb"),
        (False, "mooneye/acceptance/add_sp_e_timing.gb"),
        (False, "mooneye/acceptance/oam_dma/sources-GS.gb"),
        (False, "mooneye/acceptance/oam_dma/basic.gb"),
        (False, "mooneye/acceptance/oam_dma/reg_read.gb"),
        (False, "mooneye/acceptance/halt_ime0_nointr_timing.gb"),
        (False, "mooneye/acceptance/ppu/vblank_stat_intr-GS.gb"),
        (False, "mooneye/acceptance/ppu/intr_2_mode0_timing_sprites.gb"),
        (False, "mooneye/acceptance/ppu/stat_irq_blocking.gb"),
        (False, "mooneye/acceptance/ppu/intr_1_2_timing-GS.gb"),
        (False, "mooneye/acceptance/ppu/intr_2_mode0_timing.gb"),
        (False, "mooneye/acceptance/ppu/lcdon_write_timing-GS.gb"),
        (False, "mooneye/acceptance/ppu/hblank_ly_scx_timing-GS.gb"),
        (False, "mooneye/acceptance/ppu/intr_2_0_timing.gb"),
        (False, "mooneye/acceptance/ppu/stat_lyc_onoff.gb"),
        (False, "mooneye/acceptance/ppu/intr_2_mode3_timing.gb"),
        (False, "mooneye/acceptance/ppu/lcdon_timing-GS.gb"),
        (False, "mooneye/acceptance/ppu/intr_2_oam_ok_timing.gb"),
        (False, "mooneye/acceptance/call_cc_timing.gb"),
        (False, "mooneye/acceptance/halt_ime0_ei.gb"),
        (False, "mooneye/acceptance/intr_timing.gb"),
        (False, "mooneye/acceptance/instr/daa.gb"),
        (False, "mooneye/acceptance/if_ie_registers.gb"),
        (False, "mooneye/acceptance/di_timing-GS.gb"),
        (False, "mooneye/acceptance/serial/boot_sclk_align-dmgABCmgb.gb"),
        (False, "mooneye/acceptance/boot_regs-sgb2.gb"),
        (False, "mooneye/acceptance/boot_div-S.gb"),
        (False, "mooneye/acceptance/boot_div-dmg0.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_64Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_1Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_512kb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_32Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_2Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_4Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_8Mb.gb"),
        (True, "mooneye/emulator-only/mbc5/rom_16Mb.gb"),
        # (True, "mooneye/emulator-only/mbc2/rom_1Mb.gb"),
        # (True, "mooneye/emulator-only/mbc2/ram.gb"),
        # (True, "mooneye/emulator-only/mbc2/bits_unused.gb"),
        # (True, "mooneye/emulator-only/mbc2/bits_ramg.gb"),
        # (True, "mooneye/emulator-only/mbc2/rom_512kb.gb"),
        # (True, "mooneye/emulator-only/mbc2/bits_romb.gb"),
        # (True, "mooneye/emulator-only/mbc2/rom_2Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_1Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/bits_bank2.gb"),
        (True, "mooneye/emulator-only/mbc1/bits_ramg.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_512kb.gb"),
        (True, "mooneye/emulator-only/mbc1/bits_mode.gb"),
        (True, "mooneye/emulator-only/mbc1/ram_64kb.gb"),
        (True, "mooneye/emulator-only/mbc1/bits_bank1.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_2Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/ram_256kb.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_4Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/multicart_rom_8Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_8Mb.gb"),
        (True, "mooneye/emulator-only/mbc1/rom_16Mb.gb"),
    ]

    # HACK: We load any rom and load it until the last frame in the boot rom.
    # Then we save it, so we won't need to redo it.
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    saved_state = io.BytesIO()
    for _ in range(59):
        pyboy.tick()
    pyboy.save_state(saved_state)
    pyboy.stop(save=False)

    for clean, rom in test_roms:
        pyboy = PyBoy(rom, window_type="headless")
        pyboy.set_emulation_speed(0)
        saved_state.seek(0)
        if clean:
            for _ in range(59):
                pyboy.tick()
        else:
            pyboy.load_state(saved_state)

        for _ in range(40):
            pyboy.tick()

        png_path = Path(f"test_results/{rom}.png")
        image = pyboy.botsupport_manager().screen().screen_image()
        if OVERWRITE_PNGS:
            png_path.parents[0].mkdir(parents=True, exist_ok=True)
            image.save(png_path)
        else:
            old_image = PIL.Image.open(png_path)
            if "acceptance" in rom:
                # The registers are too volatile to depend on. We crop the top out, and only match the assertions.
                diff = PIL.ImageChops.difference(image.crop((0, 72, 160, 144)), old_image.crop((0, 72, 160, 144)))
            else:
                diff = PIL.ImageChops.difference(image, old_image)

            if diff.getbbox() and not os.environ.get("TEST_CI"):
                image.show()
                old_image.show()
                diff.show()
            assert not diff.getbbox(), f"Images are different! {rom}"

        pyboy.stop(save=False)
