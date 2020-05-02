#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
from pathlib import Path

import PIL
import pytest
from pyboy import PyBoy

from .utils import boot_rom, default_rom

if platform.python_implementation() == "PyPy":
    timeout = 15
else:
    timeout = 5

OVERWRITE_PNGS = False


@pytest.mark.skipif(not os.path.isdir("mooneye"), reason="ROM not present")
def test_blarggs():
    test_roms = [
        "mooneye/misc/boot_hwio-C.gb",
        "mooneye/misc/boot_regs-A.gb",
        "mooneye/misc/bits/unused_hwio-C.gb",
        "mooneye/misc/boot_div-A.gb",
        "mooneye/misc/boot_regs-cgb.gb",
        "mooneye/misc/boot_div-cgbABCDE.gb",
        "mooneye/misc/ppu/vblank_stat_intr-C.gb",
        "mooneye/misc/boot_div-cgb0.gb",
        "mooneye/manual-only/sprite_priority.gb",
        "mooneye/utils/bootrom_dumper.gb",
        "mooneye/utils/dump_boot_hwio.gb",
        "mooneye/acceptance/rapid_di_ei.gb",
        "mooneye/acceptance/oam_dma_start.gb",
        "mooneye/acceptance/boot_regs-dmgABC.gb",
        "mooneye/acceptance/reti_timing.gb",
        "mooneye/acceptance/call_timing.gb",
        "mooneye/acceptance/reti_intr_timing.gb",
        "mooneye/acceptance/boot_regs-mgb.gb",
        "mooneye/acceptance/ei_sequence.gb",
        "mooneye/acceptance/jp_timing.gb",
        "mooneye/acceptance/ei_timing.gb",
        "mooneye/acceptance/oam_dma_timing.gb",
        "mooneye/acceptance/call_cc_timing2.gb",
        "mooneye/acceptance/boot_div2-S.gb",
        "mooneye/acceptance/halt_ime1_timing.gb",
        "mooneye/acceptance/halt_ime1_timing2-GS.gb",
        "mooneye/acceptance/timer/tima_reload.gb",
        "mooneye/acceptance/timer/tma_write_reloading.gb",
        "mooneye/acceptance/timer/tim10.gb",
        "mooneye/acceptance/timer/tim00.gb",
        "mooneye/acceptance/timer/tim11.gb",
        "mooneye/acceptance/timer/tim01.gb",
        "mooneye/acceptance/timer/tima_write_reloading.gb",
        "mooneye/acceptance/timer/tim11_div_trigger.gb",
        "mooneye/acceptance/timer/div_write.gb",
        "mooneye/acceptance/timer/tim10_div_trigger.gb",
        "mooneye/acceptance/timer/tim00_div_trigger.gb",
        "mooneye/acceptance/timer/rapid_toggle.gb",
        "mooneye/acceptance/timer/tim01_div_trigger.gb",
        "mooneye/acceptance/boot_regs-sgb.gb",
        "mooneye/acceptance/jp_cc_timing.gb",
        "mooneye/acceptance/call_timing2.gb",
        "mooneye/acceptance/ld_hl_sp_e_timing.gb",
        "mooneye/acceptance/push_timing.gb",
        "mooneye/acceptance/boot_hwio-dmg0.gb",
        "mooneye/acceptance/rst_timing.gb",
        "mooneye/acceptance/boot_hwio-S.gb",
        "mooneye/acceptance/boot_div-dmgABCmgb.gb",
        "mooneye/acceptance/bits/mem_oam.gb",
        "mooneye/acceptance/bits/reg_f.gb",
        "mooneye/acceptance/bits/unused_hwio-GS.gb",
        "mooneye/acceptance/div_timing.gb",
        "mooneye/acceptance/ret_cc_timing.gb",
        "mooneye/acceptance/boot_regs-dmg0.gb",
        "mooneye/acceptance/interrupts/ie_push.gb",
        "mooneye/acceptance/boot_hwio-dmgABCmgb.gb",
        "mooneye/acceptance/pop_timing.gb",
        "mooneye/acceptance/ret_timing.gb",
        "mooneye/acceptance/oam_dma_restart.gb",
        "mooneye/acceptance/add_sp_e_timing.gb",
        "mooneye/acceptance/oam_dma/sources-GS.gb",
        "mooneye/acceptance/oam_dma/basic.gb",
        "mooneye/acceptance/oam_dma/reg_read.gb",
        "mooneye/acceptance/halt_ime0_nointr_timing.gb",
        "mooneye/acceptance/ppu/vblank_stat_intr-GS.gb",
        "mooneye/acceptance/ppu/intr_2_mode0_timing_sprites.gb",
        "mooneye/acceptance/ppu/stat_irq_blocking.gb",
        "mooneye/acceptance/ppu/intr_1_2_timing-GS.gb",
        "mooneye/acceptance/ppu/intr_2_mode0_timing.gb",
        "mooneye/acceptance/ppu/lcdon_write_timing-GS.gb",
        "mooneye/acceptance/ppu/hblank_ly_scx_timing-GS.gb",
        "mooneye/acceptance/ppu/intr_2_0_timing.gb",
        "mooneye/acceptance/ppu/stat_lyc_onoff.gb",
        "mooneye/acceptance/ppu/intr_2_mode3_timing.gb",
        "mooneye/acceptance/ppu/lcdon_timing-GS.gb",
        "mooneye/acceptance/ppu/intr_2_oam_ok_timing.gb",
        "mooneye/acceptance/call_cc_timing.gb",
        "mooneye/acceptance/halt_ime0_ei.gb",
        "mooneye/acceptance/intr_timing.gb",
        "mooneye/acceptance/instr/daa.gb",
        "mooneye/acceptance/if_ie_registers.gb",
        "mooneye/acceptance/di_timing-GS.gb",
        "mooneye/acceptance/serial/boot_sclk_align-dmgABCmgb.gb",
        "mooneye/acceptance/boot_regs-sgb2.gb",
        "mooneye/acceptance/boot_div-S.gb",
        "mooneye/acceptance/boot_div-dmg0.gb",
        "mooneye/emulator-only/mbc5/rom_64Mb.gb",
        "mooneye/emulator-only/mbc5/rom_1Mb.gb",
        "mooneye/emulator-only/mbc5/rom_512kb.gb",
        "mooneye/emulator-only/mbc5/rom_32Mb.gb",
        "mooneye/emulator-only/mbc5/rom_2Mb.gb",
        "mooneye/emulator-only/mbc5/rom_4Mb.gb",
        "mooneye/emulator-only/mbc5/rom_8Mb.gb",
        "mooneye/emulator-only/mbc5/rom_16Mb.gb",
        "mooneye/emulator-only/mbc2/rom_1Mb.gb",
        "mooneye/emulator-only/mbc2/ram.gb",
        "mooneye/emulator-only/mbc2/bits_unused.gb",
        "mooneye/emulator-only/mbc2/bits_ramg.gb",
        "mooneye/emulator-only/mbc2/rom_512kb.gb",
        "mooneye/emulator-only/mbc2/bits_romb.gb",
        "mooneye/emulator-only/mbc2/rom_2Mb.gb",
        "mooneye/emulator-only/mbc1/rom_1Mb.gb",
        "mooneye/emulator-only/mbc1/bits_bank2.gb",
        "mooneye/emulator-only/mbc1/bits_ramg.gb",
        "mooneye/emulator-only/mbc1/rom_512kb.gb",
        "mooneye/emulator-only/mbc1/bits_mode.gb",
        "mooneye/emulator-only/mbc1/ram_64kb.gb",
        "mooneye/emulator-only/mbc1/bits_bank1.gb",
        "mooneye/emulator-only/mbc1/rom_2Mb.gb",
        "mooneye/emulator-only/mbc1/ram_256kb.gb",
        "mooneye/emulator-only/mbc1/rom_4Mb.gb",
        "mooneye/emulator-only/mbc1/multicart_rom_8Mb.gb",
        "mooneye/emulator-only/mbc1/rom_8Mb.gb",
        "mooneye/emulator-only/mbc1/rom_16Mb.gb",
    ]

    # HACK: We load any rom and load it until the last frame in the boot rom.
    # Then we save it, so we won't need to redo it.
    pyboy = PyBoy(default_rom, window_type="dummy", bootrom=boot_rom)
    pyboy.set_emulation_speed(0)
    saved_state = io.BytesIO()
    for _ in range(59):
        pyboy.tick()
    pyboy.save_state(saved_state)
    pyboy.stop(save=False)

    for rom in test_roms:
        try:
            pyboy = PyBoy(rom, window_type="headless", bootrom=boot_rom)
        except Exception as ex:
            print(ex)
            continue
        saved_state.seek(0)
        pyboy.load_state(saved_state)

        for _ in range(20):
            pyboy.tick()

        png_path = Path(f"test_results/{rom}.png")
        image = pyboy.botsupport_manager().screen().screen_image()
        if OVERWRITE_PNGS:
            png_path.parents[0].mkdir(parents=True, exist_ok=True)
            image.save(png_path)
        else:
            old_image = PIL.Image.open(png_path)
            diff = PIL.ImageChops.difference(image, old_image)
            if diff.getbbox() and not os.environ.get("TEST_CI"):
                image.show()
                old_image.show()
                diff.show()
            assert not diff.getbbox(), f"Images are different! {rom}"

        pyboy.stop(save=False)
