#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
from pathlib import Path
from zipfile import ZipFile

import PIL
import pytest

from pyboy import PyBoy

if platform.python_implementation() == "PyPy":
    timeout = 15
else:
    timeout = 5

OVERWRITE_PNGS = False

saved_state = None


@pytest.mark.parametrize(
    "clean, rom",
    [
        ####################
        # These are meant to fail on DMG:
        # (False, "misc/boot_div-A.gb"),
        # (False, "misc/boot_div-cgb0.gb"),
        # (False, "misc/boot_div-cgbABCDE.gb"),
        # (False, "misc/boot_hwio-C.gb"),
        # (False, "misc/boot_regs-A.gb"),
        # (False, "misc/boot_regs-cgb.gb"),
        # (False, "misc/ppu/vblank_stat_intr-C.gb"),
        # (False, "misc/bits/unused_hwio-C.gb"),

        # (False, "utils/bootrom_dumper.gb"),
        # (False, "utils/dump_boot_hwio.gb"),
        (False, "manual-only/sprite_priority.gb"),
        (False, "acceptance/rapid_di_ei.gb"),
        (False, "acceptance/oam_dma_start.gb"),
        (False, "acceptance/boot_regs-dmgABC.gb"),
        (False, "acceptance/reti_timing.gb"),
        (False, "acceptance/call_timing.gb"),
        (False, "acceptance/reti_intr_timing.gb"),
        (False, "acceptance/boot_regs-mgb.gb"),
        (False, "acceptance/ei_sequence.gb"),
        (False, "acceptance/jp_timing.gb"),
        (False, "acceptance/ei_timing.gb"),
        (False, "acceptance/oam_dma_timing.gb"),
        (False, "acceptance/call_cc_timing2.gb"),
        (False, "acceptance/boot_div2-S.gb"),
        (False, "acceptance/halt_ime1_timing.gb"),
        (False, "acceptance/halt_ime1_timing2-GS.gb"),
        (False, "acceptance/timer/tima_reload.gb"),
        (False, "acceptance/timer/tma_write_reloading.gb"),
        (False, "acceptance/timer/tim10.gb"),
        (False, "acceptance/timer/tim00.gb"),
        (False, "acceptance/timer/tim11.gb"),
        (False, "acceptance/timer/tim01.gb"),
        (False, "acceptance/timer/tima_write_reloading.gb"),
        (False, "acceptance/timer/tim11_div_trigger.gb"),
        (False, "acceptance/timer/div_write.gb"),
        (False, "acceptance/timer/tim10_div_trigger.gb"),
        (False, "acceptance/timer/tim00_div_trigger.gb"),
        (False, "acceptance/timer/rapid_toggle.gb"),
        (False, "acceptance/timer/tim01_div_trigger.gb"),
        (False, "acceptance/boot_regs-sgb.gb"),
        (False, "acceptance/jp_cc_timing.gb"),
        (False, "acceptance/call_timing2.gb"),
        (False, "acceptance/ld_hl_sp_e_timing.gb"),
        (False, "acceptance/push_timing.gb"),
        (False, "acceptance/boot_hwio-dmg0.gb"),
        (False, "acceptance/rst_timing.gb"),
        (False, "acceptance/boot_hwio-S.gb"),
        (False, "acceptance/boot_div-dmgABCmgb.gb"),
        (False, "acceptance/bits/mem_oam.gb"),
        (False, "acceptance/bits/reg_f.gb"),
        (False, "acceptance/bits/unused_hwio-GS.gb"),
        (False, "acceptance/div_timing.gb"),
        (False, "acceptance/ret_cc_timing.gb"),
        (False, "acceptance/boot_regs-dmg0.gb"),
        (False, "acceptance/interrupts/ie_push.gb"),
        (False, "acceptance/boot_hwio-dmgABCmgb.gb"),
        (False, "acceptance/pop_timing.gb"),
        (False, "acceptance/ret_timing.gb"),
        (False, "acceptance/oam_dma_restart.gb"),
        (False, "acceptance/add_sp_e_timing.gb"),
        (False, "acceptance/oam_dma/sources-GS.gb"),
        (False, "acceptance/oam_dma/basic.gb"),
        (False, "acceptance/oam_dma/reg_read.gb"),
        (False, "acceptance/halt_ime0_nointr_timing.gb"),
        (False, "acceptance/ppu/vblank_stat_intr-GS.gb"),
        (False, "acceptance/ppu/intr_2_mode0_timing_sprites.gb"),
        (False, "acceptance/ppu/stat_irq_blocking.gb"),
        (False, "acceptance/ppu/intr_1_2_timing-GS.gb"),
        (False, "acceptance/ppu/intr_2_mode0_timing.gb"),
        (False, "acceptance/ppu/lcdon_write_timing-GS.gb"),
        (False, "acceptance/ppu/hblank_ly_scx_timing-GS.gb"),
        (False, "acceptance/ppu/intr_2_0_timing.gb"),
        (False, "acceptance/ppu/stat_lyc_onoff.gb"),
        (False, "acceptance/ppu/intr_2_mode3_timing.gb"),
        (False, "acceptance/ppu/lcdon_timing-GS.gb"),
        (False, "acceptance/ppu/intr_2_oam_ok_timing.gb"),
        (False, "acceptance/call_cc_timing.gb"),
        (False, "acceptance/halt_ime0_ei.gb"),
        (False, "acceptance/intr_timing.gb"),
        (False, "acceptance/instr/daa.gb"),
        (False, "acceptance/if_ie_registers.gb"),
        (False, "acceptance/di_timing-GS.gb"),
        (False, "acceptance/serial/boot_sclk_align-dmgABCmgb.gb"),
        (False, "acceptance/boot_regs-sgb2.gb"),
        (False, "acceptance/boot_div-S.gb"),
        (False, "acceptance/boot_div-dmg0.gb"),
        (True, "emulator-only/mbc5/rom_64Mb.gb"),
        (True, "emulator-only/mbc5/rom_1Mb.gb"),
        (True, "emulator-only/mbc5/rom_512kb.gb"),
        (True, "emulator-only/mbc5/rom_32Mb.gb"),
        (True, "emulator-only/mbc5/rom_2Mb.gb"),
        (True, "emulator-only/mbc5/rom_4Mb.gb"),
        (True, "emulator-only/mbc5/rom_8Mb.gb"),
        (True, "emulator-only/mbc5/rom_16Mb.gb"),
        # (True, "emulator-only/mbc2/rom_1Mb.gb"),
        # (True, "emulator-only/mbc2/ram.gb"),
        # (True, "emulator-only/mbc2/bits_unused.gb"),
        # (True, "emulator-only/mbc2/bits_ramg.gb"),
        # (True, "emulator-only/mbc2/rom_512kb.gb"),
        # (True, "emulator-only/mbc2/bits_romb.gb"),
        # (True, "emulator-only/mbc2/rom_2Mb.gb"),
        (True, "emulator-only/mbc1/rom_1Mb.gb"),
        (True, "emulator-only/mbc1/bits_bank2.gb"),
        (True, "emulator-only/mbc1/bits_ramg.gb"),
        (True, "emulator-only/mbc1/rom_512kb.gb"),
        (True, "emulator-only/mbc1/bits_mode.gb"),
        (True, "emulator-only/mbc1/ram_64kb.gb"),
        (True, "emulator-only/mbc1/bits_bank1.gb"),
        (True, "emulator-only/mbc1/rom_2Mb.gb"),
        (True, "emulator-only/mbc1/ram_256kb.gb"),
        (True, "emulator-only/mbc1/rom_4Mb.gb"),
        (True, "emulator-only/mbc1/multicart_rom_8Mb.gb"),
        (True, "emulator-only/mbc1/rom_8Mb.gb"),
        (True, "emulator-only/mbc1/rom_16Mb.gb"),
    ]
)
def test_mooneye(clean, rom, mooneye_dir, default_rom):
    global saved_state

    if saved_state is None:
        # HACK: We load any rom and load it until the last frame in the boot rom.
        # Then we save it, so we won't need to redo it.
        pyboy = PyBoy(default_rom, window_type="null", cgb=False, sound_emulated=True)
        pyboy.set_emulation_speed(0)
        saved_state = io.BytesIO()
        pyboy.tick(59, True)
        pyboy.save_state(saved_state)
        pyboy.stop(save=False)

    pyboy = PyBoy(mooneye_dir + rom, window_type="null", cgb=False)
    pyboy.set_emulation_speed(0)
    saved_state.seek(0)
    if clean:
        pyboy.tick(59, True)
    else:
        pyboy.load_state(saved_state)

    pyboy.tick(180 if "div_write" in rom else 40, True)

    png_path = Path(f"tests/test_results/mooneye/{rom}.png")
    image = pyboy.screen.screen_image()
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
