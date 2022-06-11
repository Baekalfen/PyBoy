#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import PIL
import pytest
from pyboy import PyBoy
from tests.utils import boot_rom, boot_rom_cgb, default_rom

from .utils import url_open

if platform.python_implementation() == "PyPy":
    timeout = 15
else:
    timeout = 5

OVERWRITE_PNGS = False

saved_state = None


@pytest.mark.parametrize(
    "clean, gb_type, rom", [
        (True, "dmg", "SameSuite/interrupt/ei_delay_halt.gb"),
        (True, "dmg", "SameSuite/apu/div_write_trigger.gb"),
        (True, "dmg", "SameSuite/apu/div_write_trigger_volume_10.gb"),
        (True, "dmg", "SameSuite/apu/div_write_trigger_volume.gb"),
        (True, "dmg", "SameSuite/apu/div_write_trigger_10.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_freq_change_timing-cgbDE.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_sweep.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_duty.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_nrx2_speed_change.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_sweep_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_freq_change_timing-cgb0BC.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_align_cpu.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_sweep_restart_2.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_duty_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_align.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_freq_change_timing-A.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_volume_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_volume.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_stop_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_restart_nrx2_glitch.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_stop_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_freq_change.gb"),
        (True, "dmg", "SameSuite/apu/channel_1/channel_1_nrx2_glitch.gb"),
        (True, "dmg", "SameSuite/apu/div_trigger_volume_10.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_extra_length_clocking-cgbB.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_freq_change_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_stop_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_extra_length_clocking-cgb0.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_restart_during_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_and_glitch.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_restart_stop_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_wave_ram_locked_write.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_shift_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_shift_skip_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_wave_ram_sync.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_stop_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_wave_ram_dac_on_rw.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_first_sample.gb"),
        (True, "dmg", "SameSuite/apu/channel_3/channel_3_restart_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_frequency_alignment.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr_15_7.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_align.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_equivalent_frequencies.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_volume_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr15.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr_7_15.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_freq_change.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_4/channel_4_lfsr_restart_fast.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_align.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_duty_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_duty.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_volume.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_stop_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_align_cpu.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_extra_length_clocking-cgb0B.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_restart.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_stop_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_freq_change.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_nrx2_glitch.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_delay.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_volume_div.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_nrx2_speed_change.gb"),
        (True, "dmg", "SameSuite/apu/channel_2/channel_2_restart_nrx2_glitch.gb"),
        (True, "dmg", "SameSuite/sgb/command_mlt_req_1_incrementing.gb"),
        (True, "dmg", "SameSuite/sgb/command_mlt_req.gb"),
        (True, "cgb", "SameSuite/dma/gdma_addr_mask.gb"),
        (True, "cgb", "SameSuite/dma/hdma_mode0.gb"),
        (True, "cgb", "SameSuite/dma/hdma_lcd_off.gb"),
        (True, "cgb", "SameSuite/dma/gbc_dma_cont.gb"),
        (True, "dmg", "SameSuite/ppu/blocking_bgpi_increase.gb"),
    ]
)
def test_samesuite(clean, gb_type, rom):
    global saved_state
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    samesuite_dir = "SameSuite"
    if not os.path.isdir(samesuite_dir):
        print(url_open("https://pyboy.dk/mirror/LICENSE.SameSuite.txt"))
        samesuite_data = io.BytesIO(url_open("https://pyboy.dk/mirror/SameSuite.zip"))
        with ZipFile(samesuite_data) as _zip:
            _zip.extractall(samesuite_dir)

    if saved_state is None:
        # HACK: We load any rom and load it until the last frame in the boot rom.
        # Then we save it, so we won't need to redo it.
        pyboy = PyBoy(
            default_rom,
            window_type="headless",
            cgb=gb_type == "cgb",
            bootrom=boot_rom_cgb if gb_type == "cgb" else boot_rom
        )
        pyboy.set_emulation_speed(0)
        saved_state = io.BytesIO()
        for _ in range(180 if gb_type == "cgb" else 350):
            pyboy.tick()
        pyboy.save_state(saved_state)
        pyboy.stop(save=False)

    pyboy = PyBoy(
        rom, window_type="headless", cgb=gb_type == "cgb", bootrom=boot_rom_cgb if gb_type == "cgb" else boot_rom
    )
    pyboy.set_emulation_speed(0)
    saved_state.seek(0)
    if clean:
        for _ in range(180 if gb_type == "cgb" else 350):
            pyboy.tick()
    else:
        pyboy.load_state(saved_state)

    for _ in range(10):
        if np.all(pyboy.botsupport_manager().screen().screen_ndarray() > 240):
            for _ in range(20):
                pyboy.tick()
        else:
            break

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
