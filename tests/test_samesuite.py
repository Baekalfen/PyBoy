#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
from pathlib import Path

import numpy as np
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
    "clean, gb_type, rom", [
        (True, "dmg", "interrupt/ei_delay_halt.gb"),
        (True, "dmg", "apu/div_write_trigger.gb"),
        (True, "dmg", "apu/div_write_trigger_volume_10.gb"),
        (True, "dmg", "apu/div_write_trigger_volume.gb"),
        (True, "dmg", "apu/div_write_trigger_10.gb"),
        (True, "dmg", "apu/channel_1/channel_1_freq_change_timing-cgbDE.gb"),
        (True, "dmg", "apu/channel_1/channel_1_delay.gb"),
        (True, "dmg", "apu/channel_1/channel_1_sweep.gb"),
        (True, "dmg", "apu/channel_1/channel_1_duty.gb"),
        (True, "dmg", "apu/channel_1/channel_1_nrx2_speed_change.gb"),
        (True, "dmg", "apu/channel_1/channel_1_sweep_restart.gb"),
        (True, "dmg", "apu/channel_1/channel_1_freq_change_timing-cgb0BC.gb"),
        (True, "dmg", "apu/channel_1/channel_1_align_cpu.gb"),
        (True, "dmg", "apu/channel_1/channel_1_sweep_restart_2.gb"),
        (True, "dmg", "apu/channel_1/channel_1_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "apu/channel_1/channel_1_restart.gb"),
        (True, "dmg", "apu/channel_1/channel_1_duty_delay.gb"),
        (True, "dmg", "apu/channel_1/channel_1_align.gb"),
        (True, "dmg", "apu/channel_1/channel_1_freq_change_timing-A.gb"),
        (True, "dmg", "apu/channel_1/channel_1_volume_div.gb"),
        (True, "dmg", "apu/channel_1/channel_1_volume.gb"),
        (True, "dmg", "apu/channel_1/channel_1_stop_div.gb"),
        (True, "dmg", "apu/channel_1/channel_1_restart_nrx2_glitch.gb"),
        (True, "dmg", "apu/channel_1/channel_1_stop_restart.gb"),
        (True, "dmg", "apu/channel_1/channel_1_freq_change.gb"),
        (True, "dmg", "apu/channel_1/channel_1_nrx2_glitch.gb"),
        (True, "dmg", "apu/div_trigger_volume_10.gb"),
        (True, "dmg", "apu/channel_3/channel_3_extra_length_clocking-cgbB.gb"),
        (True, "dmg", "apu/channel_3/channel_3_freq_change_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_stop_div.gb"),
        (True, "dmg", "apu/channel_3/channel_3_extra_length_clocking-cgb0.gb"),
        (True, "dmg", "apu/channel_3/channel_3_restart_during_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_and_glitch.gb"),
        (True, "dmg", "apu/channel_3/channel_3_restart_stop_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_wave_ram_locked_write.gb"),
        (True, "dmg", "apu/channel_3/channel_3_shift_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_shift_skip_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_wave_ram_sync.gb"),
        (True, "dmg", "apu/channel_3/channel_3_stop_delay.gb"),
        (True, "dmg", "apu/channel_3/channel_3_wave_ram_dac_on_rw.gb"),
        (True, "dmg", "apu/channel_3/channel_3_first_sample.gb"),
        (True, "dmg", "apu/channel_3/channel_3_restart_delay.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr_restart.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr.gb"),
        (True, "dmg", "apu/channel_4/channel_4_frequency_alignment.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr_15_7.gb"),
        (True, "dmg", "apu/channel_4/channel_4_align.gb"),
        (True, "dmg", "apu/channel_4/channel_4_equivalent_frequencies.gb"),
        (True, "dmg", "apu/channel_4/channel_4_volume_div.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr15.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr_7_15.gb"),
        (True, "dmg", "apu/channel_4/channel_4_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "apu/channel_4/channel_4_freq_change.gb"),
        (True, "dmg", "apu/channel_4/channel_4_delay.gb"),
        (True, "dmg", "apu/channel_4/channel_4_lfsr_restart_fast.gb"),
        (True, "dmg", "apu/channel_2/channel_2_align.gb"),
        (True, "dmg", "apu/channel_2/channel_2_duty_delay.gb"),
        (True, "dmg", "apu/channel_2/channel_2_duty.gb"),
        (True, "dmg", "apu/channel_2/channel_2_volume.gb"),
        (True, "dmg", "apu/channel_2/channel_2_stop_restart.gb"),
        (True, "dmg", "apu/channel_2/channel_2_align_cpu.gb"),
        (True, "dmg", "apu/channel_2/channel_2_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "apu/channel_2/channel_2_restart.gb"),
        (True, "dmg", "apu/channel_2/channel_2_stop_div.gb"),
        (True, "dmg", "apu/channel_2/channel_2_freq_change.gb"),
        (True, "dmg", "apu/channel_2/channel_2_nrx2_glitch.gb"),
        (True, "dmg", "apu/channel_2/channel_2_delay.gb"),
        (True, "dmg", "apu/channel_2/channel_2_volume_div.gb"),
        (True, "dmg", "apu/channel_2/channel_2_nrx2_speed_change.gb"),
        (True, "dmg", "apu/channel_2/channel_2_restart_nrx2_glitch.gb"),
        (True, "dmg", "sgb/command_mlt_req_1_incrementing.gb"),
        (True, "dmg", "sgb/command_mlt_req.gb"),
        (True, "cgb", "dma/gdma_addr_mask.gb"),
        (True, "cgb", "dma/hdma_mode0.gb"),
        (True, "cgb", "dma/hdma_lcd_off.gb"),
        (True, "cgb", "dma/gbc_dma_cont.gb"),
        (True, "dmg", "ppu/blocking_bgpi_increase.gb"),
    ]
)
def test_samesuite(clean, gb_type, rom, samesuite_dir, boot_cgb_rom, boot_rom, default_rom):
    global saved_state

    if saved_state is None:
        # HACK: We load any rom and load it until the last frame in the boot rom.
        # Then we save it, so we won't need to redo it.
        pyboy = PyBoy(
            default_rom,
            window="null",
            cgb=gb_type == "cgb",
            bootrom=boot_cgb_rom if gb_type == "cgb" else boot_rom,
            sound_emulated=True,
        )
        pyboy.set_emulation_speed(0)
        saved_state = io.BytesIO()
        pyboy.tick(180 if gb_type == "cgb" else 350, True)
        pyboy.save_state(saved_state)
        pyboy.stop(save=False)

    pyboy = PyBoy(
        samesuite_dir + rom,
        window="null",
        cgb=gb_type == "cgb",
        bootrom=boot_cgb_rom if gb_type == "cgb" else boot_rom,
        sound_emulated=True,
    )
    pyboy.set_emulation_speed(0)
    saved_state.seek(0)
    if clean:
        pyboy.tick(180 if gb_type == "cgb" else 350, True)
    else:
        pyboy.load_state(saved_state)

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
        # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)

        if diff.getbbox() and not os.environ.get("TEST_CI"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {rom}"

    pyboy.stop(save=False)
