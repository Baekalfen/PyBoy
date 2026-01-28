#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import numpy as np
import PIL
import pytest

from pyboy import PyBoy

OVERWRITE_PNGS = False


@pytest.mark.parametrize(
    "gb_type, rom",
    [
        ("dmg", "interrupt/ei_delay_halt.gb"),
        ("dmg", "apu/div_write_trigger.gb"),
        ("dmg", "apu/div_write_trigger_volume_10.gb"),
        ("dmg", "apu/div_write_trigger_volume.gb"),
        ("dmg", "apu/div_write_trigger_10.gb"),
        ("dmg", "apu/channel_1/channel_1_freq_change_timing-cgbDE.gb"),
        ("dmg", "apu/channel_1/channel_1_delay.gb"),
        ("dmg", "apu/channel_1/channel_1_sweep.gb"),
        ("dmg", "apu/channel_1/channel_1_duty.gb"),
        ("dmg", "apu/channel_1/channel_1_nrx2_speed_change.gb"),
        ("dmg", "apu/channel_1/channel_1_sweep_restart.gb"),
        ("dmg", "apu/channel_1/channel_1_freq_change_timing-cgb0BC.gb"),
        ("dmg", "apu/channel_1/channel_1_align_cpu.gb"),
        ("dmg", "apu/channel_1/channel_1_sweep_restart_2.gb"),
        ("dmg", "apu/channel_1/channel_1_extra_length_clocking-cgb0B.gb"),
        ("dmg", "apu/channel_1/channel_1_restart.gb"),
        ("dmg", "apu/channel_1/channel_1_duty_delay.gb"),
        ("dmg", "apu/channel_1/channel_1_align.gb"),
        ("dmg", "apu/channel_1/channel_1_freq_change_timing-A.gb"),
        ("dmg", "apu/channel_1/channel_1_volume_div.gb"),
        ("dmg", "apu/channel_1/channel_1_volume.gb"),
        ("dmg", "apu/channel_1/channel_1_stop_div.gb"),
        ("dmg", "apu/channel_1/channel_1_restart_nrx2_glitch.gb"),
        ("dmg", "apu/channel_1/channel_1_stop_restart.gb"),
        ("dmg", "apu/channel_1/channel_1_freq_change.gb"),
        ("dmg", "apu/channel_1/channel_1_nrx2_glitch.gb"),
        ("dmg", "apu/div_trigger_volume_10.gb"),
        ("dmg", "apu/channel_3/channel_3_extra_length_clocking-cgbB.gb"),
        ("dmg", "apu/channel_3/channel_3_freq_change_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_stop_div.gb"),
        ("dmg", "apu/channel_3/channel_3_extra_length_clocking-cgb0.gb"),
        ("dmg", "apu/channel_3/channel_3_restart_during_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_and_glitch.gb"),
        ("dmg", "apu/channel_3/channel_3_restart_stop_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_wave_ram_locked_write.gb"),
        ("dmg", "apu/channel_3/channel_3_shift_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_shift_skip_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_wave_ram_sync.gb"),
        ("dmg", "apu/channel_3/channel_3_stop_delay.gb"),
        ("dmg", "apu/channel_3/channel_3_wave_ram_dac_on_rw.gb"),
        ("dmg", "apu/channel_3/channel_3_first_sample.gb"),
        ("dmg", "apu/channel_3/channel_3_restart_delay.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr_restart.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr.gb"),
        ("dmg", "apu/channel_4/channel_4_frequency_alignment.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr_15_7.gb"),
        ("dmg", "apu/channel_4/channel_4_align.gb"),
        ("dmg", "apu/channel_4/channel_4_equivalent_frequencies.gb"),
        ("dmg", "apu/channel_4/channel_4_volume_div.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr15.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr_7_15.gb"),
        ("dmg", "apu/channel_4/channel_4_extra_length_clocking-cgb0B.gb"),
        ("dmg", "apu/channel_4/channel_4_freq_change.gb"),
        ("dmg", "apu/channel_4/channel_4_delay.gb"),
        ("dmg", "apu/channel_4/channel_4_lfsr_restart_fast.gb"),
        ("dmg", "apu/channel_2/channel_2_align.gb"),
        ("dmg", "apu/channel_2/channel_2_duty_delay.gb"),
        ("dmg", "apu/channel_2/channel_2_duty.gb"),
        ("dmg", "apu/channel_2/channel_2_volume.gb"),
        ("dmg", "apu/channel_2/channel_2_stop_restart.gb"),
        ("dmg", "apu/channel_2/channel_2_align_cpu.gb"),
        ("dmg", "apu/channel_2/channel_2_extra_length_clocking-cgb0B.gb"),
        ("dmg", "apu/channel_2/channel_2_restart.gb"),
        ("dmg", "apu/channel_2/channel_2_stop_div.gb"),
        ("dmg", "apu/channel_2/channel_2_freq_change.gb"),
        ("dmg", "apu/channel_2/channel_2_nrx2_glitch.gb"),
        ("dmg", "apu/channel_2/channel_2_delay.gb"),
        ("dmg", "apu/channel_2/channel_2_volume_div.gb"),
        ("dmg", "apu/channel_2/channel_2_nrx2_speed_change.gb"),
        ("dmg", "apu/channel_2/channel_2_restart_nrx2_glitch.gb"),
        ("cgb", "dma/gdma_addr_mask.gb"),
        ("cgb", "dma/hdma_mode0.gb"),
        ("cgb", "dma/hdma_lcd_off.gb"),
        ("cgb", "dma/gbc_dma_cont.gb"),
        ("dmg", "ppu/blocking_bgpi_increase.gb"),
    ],
)
def test_samesuite(gb_type, rom, samesuite_dir, boot_cgb_rom, boot_rom, default_rom):
    pyboy = PyBoy(
        samesuite_dir + rom,
        window="null",
        cgb=gb_type == "cgb",
        bootrom=boot_cgb_rom if gb_type == "cgb" else boot_rom,
    )
    pyboy.set_emulation_speed(0)
    pyboy.tick(180 if gb_type == "cgb" else 350, True)

    for _ in range(10):
        if np.all(pyboy.screen.ndarray[:, :, :-1] > 240):
            pyboy.tick(20, True)
        else:
            break

    png_path = Path(f"tests/test_results/SameSuite/{rom}.png")
    image = pyboy.screen.image
    if OVERWRITE_PNGS:
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
