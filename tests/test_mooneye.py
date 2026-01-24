#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy
import json

OVERWRITE_RESULTS = False

saved_state = [None, None]


@pytest.mark.parametrize(
    "text_result, clean, cgb, rom",
    [
        (True, False, True, "misc/boot_div-A.gb"),
        (True, False, True, "misc/boot_div-cgb0.gb"),
        (True, False, True, "misc/boot_div-cgbABCDE.gb"),
        (True, False, True, "misc/boot_hwio-C.gb"),
        (True, False, True, "misc/boot_regs-A.gb"),
        (True, False, True, "misc/boot_regs-cgb.gb"),
        (True, False, True, "misc/ppu/vblank_stat_intr-C.gb"),
        (True, False, True, "misc/bits/unused_hwio-C.gb"),  # Should fail on 0xFF72 for DMG
        # (True, False, True, "utils/bootrom_dumper.gb"),
        # (True, False, True, "utils/dump_boot_hwio.gb"),
        (False, False, False, "manual-only/sprite_priority.gb"),
        (True, False, False, "acceptance/rapid_di_ei.gb"),
        (False, False, False, "acceptance/oam_dma_start.gb"),
        (True, False, False, "acceptance/boot_regs-dmgABC.gb"),
        (True, False, False, "acceptance/reti_timing.gb"),
        (True, False, False, "acceptance/call_timing.gb"),
        (True, False, False, "acceptance/reti_intr_timing.gb"),
        (True, False, False, "acceptance/boot_regs-mgb.gb"),
        (True, False, False, "acceptance/ei_sequence.gb"),
        (True, False, False, "acceptance/jp_timing.gb"),
        (True, False, False, "acceptance/ei_timing.gb"),
        (True, False, False, "acceptance/oam_dma_timing.gb"),
        (True, False, False, "acceptance/call_cc_timing2.gb"),
        (True, False, False, "acceptance/boot_div2-S.gb"),
        (True, False, False, "acceptance/halt_ime1_timing.gb"),
        (True, False, False, "acceptance/halt_ime1_timing2-GS.gb"),
        (True, False, False, "acceptance/timer/tima_reload.gb"),
        (True, False, False, "acceptance/timer/tma_write_reloading.gb"),
        (True, False, False, "acceptance/timer/tim10.gb"),
        (True, False, False, "acceptance/timer/tim00.gb"),
        (True, False, False, "acceptance/timer/tim11.gb"),
        (True, False, False, "acceptance/timer/tim01.gb"),
        (True, False, False, "acceptance/timer/tima_write_reloading.gb"),
        (True, False, False, "acceptance/timer/tim11_div_trigger.gb"),
        (True, False, False, "acceptance/timer/div_write.gb"),
        (True, False, False, "acceptance/timer/tim10_div_trigger.gb"),
        (True, False, False, "acceptance/timer/tim00_div_trigger.gb"),
        (True, False, False, "acceptance/timer/rapid_toggle.gb"),
        (True, False, False, "acceptance/timer/tim01_div_trigger.gb"),
        (True, False, False, "acceptance/boot_regs-sgb.gb"),
        (True, False, False, "acceptance/jp_cc_timing.gb"),
        (True, False, False, "acceptance/call_timing2.gb"),
        (True, False, False, "acceptance/ld_hl_sp_e_timing.gb"),
        (True, False, False, "acceptance/push_timing.gb"),
        (True, False, False, "acceptance/boot_hwio-dmg0.gb"),
        (True, False, False, "acceptance/rst_timing.gb"),
        (True, False, False, "acceptance/boot_hwio-S.gb"),
        (True, False, False, "acceptance/boot_div-dmgABCmgb.gb"),
        (True, False, False, "acceptance/bits/mem_oam.gb"),
        (True, False, False, "acceptance/bits/reg_f.gb"),
        (True, False, False, "acceptance/bits/unused_hwio-GS.gb"),
        (True, False, False, "acceptance/div_timing.gb"),
        (True, False, False, "acceptance/ret_cc_timing.gb"),
        (True, False, False, "acceptance/boot_regs-dmg0.gb"),
        (True, False, False, "acceptance/interrupts/ie_push.gb"),
        (True, False, False, "acceptance/boot_hwio-dmgABCmgb.gb"),
        (True, False, False, "acceptance/pop_timing.gb"),
        (True, False, False, "acceptance/ret_timing.gb"),
        (True, False, False, "acceptance/oam_dma_restart.gb"),
        (True, False, False, "acceptance/add_sp_e_timing.gb"),
        (True, False, False, "acceptance/oam_dma/sources-GS.gb"),
        (True, False, False, "acceptance/oam_dma/basic.gb"),
        (True, False, False, "acceptance/oam_dma/reg_read.gb"),
        (True, False, False, "acceptance/halt_ime0_nointr_timing.gb"),
        (True, False, False, "acceptance/ppu/vblank_stat_intr-GS.gb"),
        (True, False, False, "acceptance/ppu/intr_2_mode0_timing_sprites.gb"),
        (True, False, False, "acceptance/ppu/stat_irq_blocking.gb"),
        (True, False, False, "acceptance/ppu/intr_1_2_timing-GS.gb"),
        (True, False, False, "acceptance/ppu/intr_2_mode0_timing.gb"),
        (True, False, False, "acceptance/ppu/lcdon_write_timing-GS.gb"),
        (True, False, False, "acceptance/ppu/hblank_ly_scx_timing-GS.gb"),
        (True, False, False, "acceptance/ppu/intr_2_0_timing.gb"),
        (True, False, False, "acceptance/ppu/stat_lyc_onoff.gb"),
        (True, False, False, "acceptance/ppu/intr_2_mode3_timing.gb"),
        (True, False, False, "acceptance/ppu/lcdon_timing-GS.gb"),
        (True, False, False, "acceptance/ppu/intr_2_oam_ok_timing.gb"),
        (True, False, False, "acceptance/call_cc_timing.gb"),
        (True, False, False, "acceptance/halt_ime0_ei.gb"),
        (True, False, False, "acceptance/intr_timing.gb"),
        (True, False, False, "acceptance/instr/daa.gb"),
        (True, False, False, "acceptance/if_ie_registers.gb"),
        (True, False, False, "acceptance/di_timing-GS.gb"),
        (True, False, False, "acceptance/serial/boot_sclk_align-dmgABCmgb.gb"),
        (True, False, False, "acceptance/boot_regs-sgb2.gb"),
        (True, False, False, "acceptance/boot_div-S.gb"),
        (True, False, False, "acceptance/boot_div-dmg0.gb"),
        (True, True, False, "emulator-only/mbc5/rom_64Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_1Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_512kb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_32Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_2Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_4Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_8Mb.gb"),
        (True, True, False, "emulator-only/mbc5/rom_16Mb.gb"),
        (True, True, False, "emulator-only/mbc2/rom_1Mb.gb"),
        (True, True, False, "emulator-only/mbc2/ram.gb"),
        (True, True, False, "emulator-only/mbc2/bits_unused.gb"),
        (True, True, False, "emulator-only/mbc2/bits_ramg.gb"),
        (True, True, False, "emulator-only/mbc2/rom_512kb.gb"),
        (True, True, False, "emulator-only/mbc2/bits_romb.gb"),
        (True, True, False, "emulator-only/mbc2/rom_2Mb.gb"),
        (True, True, False, "emulator-only/mbc1/rom_1Mb.gb"),
        (True, True, False, "emulator-only/mbc1/bits_bank2.gb"),
        (True, True, False, "emulator-only/mbc1/bits_ramg.gb"),
        (True, True, False, "emulator-only/mbc1/rom_512kb.gb"),
        (True, True, False, "emulator-only/mbc1/bits_mode.gb"),
        (True, True, False, "emulator-only/mbc1/ram_64kb.gb"),
        (True, True, False, "emulator-only/mbc1/bits_bank1.gb"),
        (True, True, False, "emulator-only/mbc1/rom_2Mb.gb"),
        (True, True, False, "emulator-only/mbc1/ram_256kb.gb"),
        (True, True, False, "emulator-only/mbc1/rom_4Mb.gb"),
        (True, True, False, "emulator-only/mbc1/multicart_rom_8Mb.gb"),
        (True, True, False, "emulator-only/mbc1/rom_8Mb.gb"),
        (True, True, False, "emulator-only/mbc1/rom_16Mb.gb"),
    ],
)
def test_mooneye(text_result, clean, cgb, rom, mooneye_dir, default_rom):
    global saved_state

    if saved_state[cgb] is None:
        # HACK: We load any rom and load it until the last frame in the boot rom.
        # Then we save it, so we won't need to redo it.
        pyboy = PyBoy(default_rom, window="null", cgb=cgb)
        pyboy.set_emulation_speed(0)
        saved_state[cgb] = io.BytesIO()
        pyboy.tick(59, True)
        pyboy.save_state(saved_state[cgb])
        pyboy.stop(save=False)

    pyboy = PyBoy(mooneye_dir + rom, window="null", cgb=cgb)
    pyboy.set_emulation_speed(0)
    saved_state[cgb].seek(0)
    if clean:
        pyboy.tick(59, True)
    else:
        pyboy.load_state(saved_state[cgb])

    pyboy.tick(180 if "div_write" in rom or "lcdon_write_timing" in rom or "mbc1" in rom else 40, True)
    if "mbc1/bits_ramg" in rom or "mbc2" in rom:
        pyboy.tick(500)

    if text_result:
        table = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ abcdefghijklmnopqrstuvwxyz{|}~ "
        text = ""
        for y in range(18):
            for x in range(20):
                try:
                    text += table[pyboy.tilemap_background[x, y] - 32]
                except IndexError:
                    text += " "
            text = text.strip()
            text += "\n"

        json_path = Path("tests/test_results/mooneye/results.json")
        json_path.parents[0].mkdir(parents=True, exist_ok=True)
        if json_path.exists():
            with open(json_path, "r") as f:
                results = json.load(f)
        else:
            results = {}

        if OVERWRITE_RESULTS:
            results[rom] = {"text": text}
            with open(json_path, "w") as f:
                json.dump(results, f, indent=2)
        else:
            assert results[rom]["text"] == text, "Results differ!"
    else:
        png_path = Path(f"tests/test_results/mooneye/{rom}.png")
        image = pyboy.screen.image

        if OVERWRITE_RESULTS:
            png_path.parents[0].mkdir(parents=True, exist_ok=True)
            image.save(png_path)
        else:
            assert png_path.exists(), "Test result doesn't exist"
            # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
            old_image = PIL.Image.open(png_path).convert("RGB")
            diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)

            if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
                image.show()
                old_image.show()
                diff.show()
            assert not diff.getbbox(), f"Images are different! {rom}"

    pyboy.stop(save=False)
