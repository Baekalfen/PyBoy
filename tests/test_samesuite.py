#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json

import os
import numpy as np
import pytest

from pyboy import PyBoy

OVERWRITE_JSON = False

samesuite_json = "tests/test_results/samesuite.json"

HEX_DIGITS = "0123456789ABCDEF"
PASS_RESULT = '\x03\x05\x08\r\x15"'


def samesuite_result(pyboy):
    def decode_digit(tile, base):
        for offset in (0, 0x31):
            digit = tile - base - offset
            if 0 <= digit < len(HEX_DIGITS):
                return HEX_DIGITS[digit]
        return None

    rows = []
    for y in range(18):
        address = "".join(decode_digit(pyboy.tilemap_background[x, y], 0x11) or "" for x in range(4))
        values = []
        for x in range(4, 20, 2):
            high = decode_digit(pyboy.tilemap_background[x, y], 0x21)
            low = decode_digit(pyboy.tilemap_background[x + 1, y], 0x01)
            if high is None or low is None:
                values = []
                break
            values.append(high + low)

        if len(address) == 4 and values:
            rows.append(f"{address}: {' '.join(values)}")

    assert rows, "SameSuite result table not found"

    serial_result = pyboy._serial()
    if serial_result == PASS_RESULT:
        rows.append("Passed")
    elif serial_result:
        rows.append("Failed")
    return "\n".join(rows) + "\n"


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

    result = samesuite_result(pyboy)
    with open(samesuite_json, "r") as f:
        old_samesuite = json.load(f)

    if OVERWRITE_JSON:
        with open(samesuite_json, "w") as f:
            old_samesuite[rom] = result
            json.dump(old_samesuite, f, indent=4)
    else:
        assert result == old_samesuite[rom], f"Outputs don't match for {rom}"
        if old_samesuite[rom] != result and os.environ.get("TEST_VERBOSE_IMAGES"):
            pyboy.screen.image.show()

    pyboy.stop(save=False)
