#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import io
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy
import json

OVERWRITE_RESULTS = False

saved_state = [None, None]

# These classifications follow the "Verified results" tables in the upstream
# Mooneye sources: https://github.com/Gekkio/mooneye-test-suite
CGB_HARDWARE_FAILURES = {
    "acceptance/bits/unused_hwio-GS.gb",
    "acceptance/boot_div-S.gb",
    "acceptance/boot_div-dmg0.gb",
    "acceptance/boot_div-dmgABCmgb.gb",
    "acceptance/boot_div2-S.gb",
    "acceptance/boot_hwio-S.gb",
    "acceptance/boot_hwio-dmg0.gb",
    "acceptance/boot_hwio-dmgABCmgb.gb",
    "acceptance/boot_regs-dmg0.gb",
    "acceptance/boot_regs-dmgABC.gb",
    "acceptance/boot_regs-mgb.gb",
    "acceptance/boot_regs-sgb.gb",
    "acceptance/boot_regs-sgb2.gb",
    "acceptance/di_timing-GS.gb",
    "acceptance/halt_ime1_timing2-GS.gb",
    "acceptance/oam_dma/sources-GS.gb",
    "acceptance/ppu/hblank_ly_scx_timing-GS.gb",
    "acceptance/ppu/intr_1_2_timing-GS.gb",
    "acceptance/ppu/lcdon_timing-GS.gb",
    "acceptance/ppu/lcdon_write_timing-GS.gb",
    "acceptance/ppu/vblank_stat_intr-GS.gb",
    "acceptance/serial/boot_sclk_align-dmgABCmgb.gb",
    "misc/boot_div-A.gb",
    "misc/boot_regs-A.gb",
}

DMG_HARDWARE_FAILURES = {
    "misc/bits/unused_hwio-C.gb",
    "misc/boot_div-A.gb",
    "misc/boot_div-cgb0.gb",
    "misc/boot_div-cgbABCDE.gb",
    "misc/boot_hwio-C.gb",
    "misc/boot_regs-A.gb",
    "misc/boot_regs-cgb.gb",
    "misc/ppu/vblank_stat_intr-C.gb",
    "acceptance/boot_div-S.gb",
    "acceptance/boot_div2-S.gb",
    "acceptance/boot_hwio-S.gb",
    "acceptance/boot_regs-mgb.gb",
    "acceptance/boot_regs-sgb.gb",
    "acceptance/boot_regs-sgb2.gb",
}


def result_has_failure(text):
    lowered = text.lower()
    return "!" in text or any(marker in lowered for marker in ("failed", "fail:", "mismatch", "not cancelled"))


MOONEYE_CASES = [
    (False, "misc/boot_div-A.gb"),
    (False, "misc/boot_div-cgb0.gb"),
    (False, "misc/boot_div-cgbABCDE.gb"),
    (False, "misc/boot_hwio-C.gb"),
    (False, "misc/boot_regs-A.gb"),
    (False, "misc/boot_regs-cgb.gb"),
    (False, "misc/ppu/vblank_stat_intr-C.gb"),
    (False, "misc/bits/unused_hwio-C.gb"),  # Should fail on 0xFF72 for DMG
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
    (True, "emulator-only/mbc2/rom_1Mb.gb"),
    (True, "emulator-only/mbc2/ram.gb"),
    (True, "emulator-only/mbc2/bits_unused.gb"),
    (True, "emulator-only/mbc2/bits_ramg.gb"),
    (True, "emulator-only/mbc2/rom_512kb.gb"),
    (True, "emulator-only/mbc2/bits_romb.gb"),
    (True, "emulator-only/mbc2/rom_2Mb.gb"),
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


@pytest.mark.parametrize("clean, rom", MOONEYE_CASES)
@pytest.mark.parametrize("cgb", [False, True], ids=["DMG", "CGB"])
def test_mooneye(clean, cgb, rom, mooneye_dir, default_rom):
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

    # LCD-on tests need extra frames before their result is written to the tilemap.
    pyboy.tick(
        180
        if "div_write" in rom
        or "lcdon_timing" in rom
        or "lcdon_write_timing" in rom
        or "mbc1" in rom
        or "sources-GS" in rom
        else 40,
        True,
    )
    if "mbc1/bits_ramg" in rom or "mbc2" in rom or "bits_" in rom:
        pyboy.tick(500)

    if rom != "manual-only/sprite_priority.gb":
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

        result_key = f"{rom} [CGB]" if cgb else rom
        if OVERWRITE_RESULTS:
            results[result_key] = {"text": text}
            with open(json_path, "w") as f:
                json.dump(results, f, indent=2)
        else:
            expected_text = results.get(result_key, results[rom])["text"]
            assert text == expected_text, "Results differ!"
            if result_has_failure(expected_text):
                if (cgb and rom in CGB_HARDWARE_FAILURES) or (not cgb and rom in DMG_HARDWARE_FAILURES):
                    pyboy.stop(save=False)
                    return
                pyboy.stop(save=False)
                pytest.xfail(f"{rom} has a recorded failure")
    else:
        result_key = f"{rom} [CGB]" if cgb else rom
        png_path = Path(f"tests/test_results/mooneye/{result_key}.png")
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
